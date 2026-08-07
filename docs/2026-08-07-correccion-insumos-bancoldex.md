# Cinco defectos del Centro de carga de Bancoldex

Reportados por el usuario el 07/08/2026 con una captura del Centro de carga:
el consolidado marcado en rojo con un error de JavaScript, la entrada de
Mitigaciones rechazando el libro del propio cliente, y la necesidad de cargar
el mismo archivo cualitativo dos veces.

Al verificarlos aparecieron dos más, reportados por el usuario en la misma
sesión: un insumo restaurado que no se releía al cambiar el periodo, y el
recuento de insumos obligatorios. Los cinco son independientes entre sí, y los
cinco están corregidos y verificados en navegador con los insumos reales de
junio-2026.

---

## 1. El consolidado rompía el informe cuando el perfil trae sus casos de Aranda

**Síntoma.** `undefined is not an object (evaluating
'chartCasos.data.datasets[0].data=[...DATA_CASOS.alertas]')` en la tarjeta del
consolidado y en «Errores que impiden exportar». El informe quedaba
bloqueado.

**Causa.** `cargarCasos()` —el lector de la hoja «Casos» del consolidado, que
implementa el modelo alertas/requerimientos/incidentes de Acción Fiduciaria—
se ejecutaba también para Bancoldex, cuyo consolidado **sí trae** esa hoja.
Para entonces `pintarCasosArandaEnSlide()` ya había reemplazado
`chartCasos.data.datasets` por una serie **por tipo de caso**. La escritura
sobre `datasets[0..2]` tenía dos desenlaces:

- con 3 series o más (el caso normal: 4 tipos de caso), **corrompía en
  silencio** las cifras de Aranda del gráfico del slide;
- con el gráfico vacío —cuando el periodo seleccionado no tiene casos, que es
  justo lo que muestra la captura del usuario: «0 casos de jul-26 (72 en el
  archivo)»— lanzaba un `TypeError`.

Ese `TypeError` no se quedaba en el gráfico: abortaba el `try` de
`cargarConsolidado()` **entero**, así que los indicadores y los backups que ya
se habían leído bien nunca se registraban, y la exportación quedaba
bloqueada.

**Corrección.** Guard al principio de `cargarCasos()`:

```js
if(PERFIL.fuentes?.casos){ alertasConsolidadoMes=null; return null; }
```

Es el mismo principio ya establecido para `publicarCasos()` y para el bloque
de repintado de `cargarAlertas()`: el dueño del dominio `casos` es la fuente
que declara el perfil, y el modelo de AF no escribe encima.
`alertasConsolidadoMes` se limpia por la misma razón que en `sinHojaCasos()`:
la reconciliación con AlertsList compara contra la cifra certificada de *ese*
modelo, y para un perfil Aranda no existe.

Acción Fiduciaria no se ve afectada: no declara `fuentes.casos`, así que sigue
leyendo la hoja «Casos» igual que antes.

## 2. La entrada de Mitigaciones rechazaba el libro del propio cliente

**Síntoma.** `Formato no permitido: «Logros_Mitigacion_TYA Bencoldex_junio.xlsx». Usa .`
— con la lista de formatos vacía, sobre un `.xlsx` perfectamente válido.

**Causa, en dos capas.**

*La inmediata:* `perfiles/bancoldex.js` declaraba `c8m: {fuentes: ['logros']}`,
con el comentario «El mismo libro mensual trae Logros y Mitigación en hojas
separadas». La intención era correcta pero el mecanismo no:
`tarjeta.fuentes` alimenta **exclusivamente** el mapa de extensiones
admitidas por insumo (es su único consumidor en todo el motor). Reapuntarla a
`logros` dejó a `mitigaciones` sin ninguna extensión válida. Que el libro sea
uno solo ya lo expresa `fuentes.cualitativos.alcance: 'archivo-alcance-unico'`,
que es lo que de verdad leen los dos cargadores.

*La de fondo:* `EXTENSIONES_INSUMO` era un `const` calculado **una sola vez al
parsear** la página, a partir del preset inicial. `TARJETAS_SELECCIONADAS` se
reasigna después —al restaurar el preset guardado y cada vez que el usuario
edita el preset en «Tarjetas»—, así que el mapa quedaba obsoleto. Comprobado
en vivo: quitar `c5` del preset no cambia una sola clave del mapa.

Cualquier tarjeta agregada por la interfaz cuya fuente no estuviera en el
preset inicial habría producido el mismo «Usa .» — no es un problema de
Bancoldex, es del motor.

**Corrección.**

- Se retira `c8m: {fuentes: ['logros']}` del perfil (queda la fuente del
  inventario), con el porqué escrito en su lugar para que no vuelva.
- `EXTENSIONES_INSUMO` pasa a ser la función `extensionesInsumo()`, resuelta
  en cada validación — mismo criterio que `dominiosActivos()`, que siempre se
  calculó dentro de la función.
- `validarArchivo()` respalda contra `EXTENSIONES_POR_FUENTE`: si ninguna
  tarjeta seleccionada declara esa fuente, el criterio correcto es no ofrecer
  la entrada de archivo; ofrecerla **y además** rechazar todo con una lista
  vacía es el peor de los dos mundos, porque el mensaje no le dice al usuario
  qué cargar.

## 3. Había que cargar el archivo cualitativo dos veces

**Lo que pidió el usuario:** cargar el libro de logros y mitigaciones en
cualquiera de las dos entradas y que, si el sistema detecta los dos
contenidos, marque los dos apartados en verde.

**Estado real antes del cambio.** El motor ya lo hacía para el registro
mensual de clientes de Acción Fiduciaria: `cargarLogrosArchivo()` marcaba
`logros` **y** `mitigaciones`. Pero la rama `archivo-alcance-unico` —la de
Bancoldex— publicaba los dos dominios y marcaba **un solo** insumo: el de la
entrada por la que se había entrado. Simétricamente en
`cargarMitigacionesArchivo()`. Resultado: la otra tarjeta se quedaba en rojo
y el usuario tenía que volver a cargar el mismo archivo.

**Corrección.** Las dos ramas `archivo-alcance-unico` marcan ahora los dos
insumos, y cada mensaje reporta el conteo de su propia hoja en vez de repetir
«N logro(s) y M mitigación(es)» en las dos tarjetas.

## 4. Un insumo restaurado no se releía al cambiar el periodo

**Síntoma.** El export de Aranda mostrando «0 casos de jul-26 (72 en el
archivo)» con el selector marcando **Junio 2026**, su entrada de archivo en
«ningún archivo seleccionado», y «Falta completar: Aranda: casos, motores y
SLA del periodo».

**Causa.** `restaurarInsumosGuardados()` reconstruye el `File` desde IndexedDB
y llama al cargador directamente, pero **nunca lo deposita en el `<input>`**.
`ejecutarRevalidacion()` —lo que corre al cambiar el periodo— recorre
justamente los `<input>`. Un insumo restaurado quedaba entonces congelado con
el resultado del mes con el que se guardó, y ningún cambio de periodo lo
alcanzaba.

`procesarFuente()` (la extracción automática) ya hacía lo correcto desde
antes, y su comentario lo dice explícitamente: deposita el archivo en el input
«a partir de ahí es indistinguible de uno arrastrado a mano: se revalida al
cambiar el periodo». La restauración era la única de las tres vías de carga
que no seguía esa regla.

**Corrección.** La restauración deposita cada archivo en su entrada, con el
mismo patrón `DataTransfer` de `procesarFuente()`. Efecto lateral bienvenido:
la entrada deja de decir «ningún archivo seleccionado» después de restaurar.

Reproducido y verificado en navegador:

| | Antes | Ahora |
|---|---|---|
| Tras restaurar (guardado en julio) | input vacío, «0 casos de jul-26» | input con el archivo, «0 casos de jul-26» |
| Tras corregir el mes a Junio | **sigue en «0 casos de jul-26»**, dominio `casos` en `null` | «72 casos de jun-26», dominio `casos` con 72 |

## 5. Qué cuenta como insumo obligatorio para Bancoldex

**Definido por el usuario el 07/08/2026:** para Bancoldex **AlertsList sí
cuenta**; lo que no aplica es **GLPI**, al que reemplaza Aranda.

El recuento armaba la lista como `['consolidado', glpi si el perfil declara
fuentes.glpi, alertas si declara fuentes.alertas]`. Bancoldex no declara
`fuentes.glpi` —trae sus casos por `fuentes.casos`— así que Aranda quedaba
fuera del recuento pese a estar rotulado como obligatorio en pantalla y a
tener su propio criterio de validación. De ahí el «1/2» con el informe ya
exportable.

Corregido en dos puntos:

- El recuento incluye la entrada de casos cuando el perfil declara
  `fuentes.casos`. La entrada física `glpi` la comparten las dos fuentes
  declarables, así que la clave del insumo no cambia.
- `insumoProcesado('glpi')` resuelve contra el dominio `casos` para esos
  perfiles: Aranda publica ahí, nunca en el dominio `glpi`, así que el insumo
  jamás se daba por procesado.

Verificado con los tres insumos cargados: **«3/3 insumos obligatorios
procesados»** e «Informe listo para exportar». Acción Fiduciaria conserva su
lista de siempre (`consolidado`, `glpi`, `alertas`), porque declara
`fuentes.glpi` y no declara `fuentes.casos`.

---

## Verificación

Pruebas estáticas y arnés:

```
python3 -m unittest discover -s automatizacion -p 'test_*.py'
Ran 114 tests in 0.663s
OK

python3 automatizacion/verificar_ab.py --autoprueba
Autoprueba OK
```

Las 17 pruebas nuevas cubren los cinco defectos: el guard de `cargarCasos()` y
su posición antes de la escritura al gráfico, que `extensionesInsumo()` sea
función y se invoque en cada validación, que el mensaje nunca quede sin
formatos, que el perfil no reapunte la fuente de `c8m`, que las dos ramas de
alcance único marquen los dos insumos, que la restauración deposite cada
archivo en su entrada antes de cargarlo, y que el recuento de obligatorios
incluya la fuente propia de casos.

En navegador, con los insumos reales de junio-2026 y el perfil `bancoldex`:

| Escenario | Antes | Ahora |
|---|---|---|
| Periodo jul-26 (Aranda sin casos) + consolidado | `TypeError`, export bloqueado | Se procesa; los errores que quedan son los reales y explicados («La hoja Indicadores no contiene una columna para jul-26») |
| Periodo jun-26: Aranda + consolidado | Cifras de Aranda corrompidas por el consolidado | 72 casos intactos, 4 series (`REQUERIMIENTO=32`, `INCIDENTE - MONITOREO=33`, `INCIDENTE=2`, `TAREA=5`), 0 errores |
| Libro cualitativo en la entrada de Mitigaciones | «Formato no permitido … Usa .» | Aceptado; las dos tarjetas en verde (5 logros / 2 mitigaciones) |
| El mismo libro en la entrada de Logros | Solo Logros en verde | Las dos en verde |
| Estado final | «0/2 insumos», errores | «Informe listo para exportar» |

Acción Fiduciaria, sin cambios: `REPORTE.autopruebas()` da **31/31 PASA**, el
perfil no declara `fuentes.casos` (así que `cargarCasos()` sigue corriendo) y
`extensionesInsumo()` devuelve las cinco claves de siempre.

**El A/B contra `main` con exports reales de AF sigue pendiente**, por el
bloqueo de siempre (no hay insumos reales de AF de junio en el repo). El
argumento de no afectación para AF es de inspección y de autopruebas, no de
A/B.

---

## Hallazgo nuevo, NO corregido: texto desbordado en la tarjeta de línea base

Al verificar el informe se ve que, en la tarjeta `c3` de Bancoldex, el valor
**«Oracle · SQL Server» se monta encima de la columna de Vigencia**.

No es una ilusión de la captura: `.tarjeta-kpi__mini-val` tiene
`white-space:nowrap` con `overflow:visible`, así que el texto se sale de su
columna. Medido en navegador:

| Valor | Ancho de la caja | Ancho del texto | Desborde |
|---|---|---|---|
| `Oracle · SQL Server` | 95 px | 165 px | **+70 px** |
| `CN-2024112` | 95 px | 99 px | +5 px |
| `Hasta 14/11/2026` | 172 px | 139 px | — |

**No se corrigió, a propósito:** `.tarjeta-kpi__mini-val` es una clase
compartida y `c3` la renderizan todos los clientes, incluido Acción
Fiduciaria, que está en producción. Cualquier arreglo (truncar con elipsis,
permitir dos líneas, o repartir el ancho de las columnas según su contenido)
cambia una tarjeta de un informe que ya se entrega, y eso va con decisión del
usuario y A/B, no de corrido dentro de otra corrección.

## Resuelto: el AlertsList real sí reconoce a Bancoldex — el archivo anterior simplemente no traía sus alertas

La preocupación quedó abierta con `alertops-2026-07.csv` (46 alertas, ninguna
de Bancoldex). El 07/08/2026, tarde, el usuario agregó
`Bancoldex/AlertsList-2.csv` (202 filas) y reportó que el informe seguía
mostrando 0 alertas para junio-2026 — parecía el mismo problema.

**No lo es.** Verificado con el archivo real: **202 de sus 212 filas se
identifican correctamente como de Bancoldex** (el filtro
`norm(valor).includes(norm(PERFIL.nombre))` sobre Topic/Message funciona
bien). Lo que pasa es que el archivo **no contiene una sola fila de
junio-2026** — su rango real es del 9 de julio al 7 de agosto de 2026.

Confirmado cargándolo con distintos periodos:

| Periodo seleccionado | Alertas de Bancoldex encontradas |
|---|---|
| Junio 2026 | 0 (correcto: el archivo no tiene ese mes) |
| Julio 2026 | 153 — coincide exacto con el conteo directo del CSV |

El motor está leyendo bien. El archivo es de otro corte. No se tocó código:
no había nada que corregir.

Ojo: no bloquea la exportación (un dominio con 0 registros se da por
resuelto), así que el informe puede emitirse con la cifra equivocada. Por eso
queda anotado como lo siguiente a mirar.
