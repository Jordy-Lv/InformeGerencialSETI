# Automatizar la disponibilidad de bases de datos: levantamiento y propuesta

**Fecha:** 28 de julio de 2026
**Estado:** levantamiento técnico. **No se implementó ningún cambio.**
**Objetivo:** eliminar la actualización manual del consolidado de Excel que hoy
hace el líder de cuenta.

**Insumos auditados directamente** (carpeta `Downloads/Junio/`):

| Archivo | Qué aporta |
|---|---|
| `Disponibilidad Consolidado Mayo.xlsx` | El consolidado. **8 hojas**, auditado celda por celda con fórmulas |
| `Informe_Mensual_Oracle_AcFiduciaria_Junio2026_v3_1.docx` | **Hallazgo nuevo:** el informe mensual de Oracle que el equipo DBA ya produce |
| `Consumo MENSUAL bolsa de horas.pptx` | La fuente de bolsa de horas que figuraba como «sin fuente oficial» |
| `AlertsList.xlsx`, `glpi (20).xlsx` | Ya cubiertos por la automatización existente |
| `oracle_disponibilidad.sh` | El script de Mateo Flórez Calonge (DBA) |

**Propiedades del consolidado:** creado por Adriano Carreño Arciniegas el
9/4/2025; **última modificación de Santiago Amaya Cely, 28/7/2026 01:50**. Es
decir, el archivo lo mantiene hoy el líder de cuenta.

> **Nota de trazabilidad.** Una primera versión de este documento reconstruyó el
> Excel desde el store serializado del informe exportado, porque el archivo no
> estaba disponible. Al auditar el archivo real, **todos los valores de aquella
> reconstrucción resultaron correctos**. Lo que aparece abajo marcado como
> **NUEVO** es lo que solo se ve abriendo el archivo: fórmulas, hojas que el
> informe no lee, columnas ocultas y bloques contradictorios.

---

## 1. Inventario de datos y cálculos

### 1.1 Las ocho hojas

| # | Hoja | ¿La lee el informe? | Contenido |
|---|---|---|---|
| 1 | `Disponibilidad` | Sí | 14 CI × 18 meses (ene-25 → jun-26) |
| 2 | **`Capacidad`** | **No — NUEVO** | 9 filesystems × 19 meses de % de ocupación |
| 3 | `Inidcadores` | Sí | **Dos bloques de metas que se contradicen — NUEVO** |
| 4 | `Casos` | Sí | Bloque de categorías obsoleto + serie mensual |
| 5 | `Grafica Dispo y Gestion` | Sí | Real / SETI por motor + **3 totales rotos — NUEVO** |
| 6 | `Backups` | Sí | 14 instancias × 19 meses, **todo en 100 %** |
| 7 | `Mitigación` | Sí | 3 filas de 2025, **las tres ocultas — NUEVO** |
| 8 | `Logros` | Sí | **Vacía: solo encabezados — NUEVO** |

**Ningún dato del Excel proviene de una fórmula, salvo cuatro promedios.** Las
1 000 y pico de celdas de disponibilidad, backups y capacidad están **escritas a
mano, una por una, todos los meses.** Ese es exactamente el trabajo que se
quiere eliminar.

### 1.2 NUEVO — Columnas y filas ocultas: el archivo que se ve no es el que se lee

Este es el hallazgo más importante para entender por qué el archivo acumula
errores.

| Hoja | Oculto |
|---|---|
| `Disponibilidad` | columnas **E–K y M–Q** = ene-25…jul-25 y **sep-25…ene-26** |
| `Capacidad` | columnas D, F–P, R, S |
| `Casos` | filas 4, 10, 11 y columna C |
| `Grafica Dispo y Gestion` | **fila 19** (un total) y columnas D, E |
| `Backups` | columnas C y R |
| `Mitigación` | **filas 6, 7 y 8 — las tres únicas filas de datos** |

**Quien mantiene el consolidado ve unas 6 columnas; el parser lee las 18.**

Dos consecuencias concretas:

1. **La caída de nov-25 (columna O) está oculta.** El 98,02 % que el informe
   grafica en el histórico y que motivó toda la discusión de redondeo del 23/07
   **no es visible para quien edita el archivo**. Nadie lo está revisando.
2. **Las tres mitigaciones están ocultas**, es decir, su autor las dio de baja.
   Pero SheetJS ignora el atributo de ocultamiento: si alguien carga el
   consolidado sin haber cargado antes el archivo cualitativo, **el informe
   importa tres riesgos de 2025 que el propio autor había retirado.** Esto
   confirma y agrava el hallazgo `DATA-007` de la auditoría.

### 1.3 Hoja `Disponibilidad`

- Encabezado en la **fila 4**: `Cliente` (B), `Tipo Ci` (C), `Meta` (D), y
  **18 columnas de mes en E4:V4 = 2025-01-01 → 2026-06-01**.
- Fechas reales con formato `mmm-yy` — por eso se leen bien.
- **Un solo cliente en toda la hoja:** las 14 filas son de Acción Fiduciaria. El
  filtro por cliente no descarta nada hoy.
- **La `Meta` es la cadena de texto `"99.30%"`**, no un número — en una celda
  con formato de porcentaje `0.00%`. Trampa clásica de Excel: parece número y no
  lo es. El informe la muestra tal cual y usa su propia meta `99.3` para
  calcular, así que hoy no hace daño.
- Valores: enteros `1` con formato `0%`, o decimales como `0.9802`.

**Los 14 CI y sus únicos tres eventos en 18 meses:**

| CI | feb-25 | **nov-25** | **ene-26** | Resto |
|---|---|---|---|---|
| INVERACCION | 1 | **0,9802** | 1 | 1 |
| ACBACOLG | **0,9999** | **0,9802** | 1 | 1 |
| APPACCION | 1 | **0,9802** | 1 | 1 |
| INVHISTO | 1 | **0,9802** | 1 | 1 |
| CHEETA | 1 | **0,9802** | **0,9993** | 1 |
| PWP, PSE, ACCIONAR, INTRANET, ORFEO, ACCION, CORETUTASK, LEGALBC, VLOZ | 1 | 1 | 1 | 1 |

Los cinco CI que registran caídas son exactamente los cinco de la lista
`INCLUIR` del script de Mateo. **Los otros nueve están en 100 % desde enero de
2025 sin una sola excepción en 18 meses** — 162 celdas idénticas. Vale la pena
preguntarse si se están midiendo (§6, duda 1).

### 1.4 NUEVO — Hoja `Capacidad`, que el informe no lee

Nueve filesystems de Acción Fiduciaria con su % de ocupación mensual:

| Filesystem | jun-26 |
|---|---|
| `/u02/data/inverdata03` | **0,94** |
| `u07/data/invhistdata01` | **0,92** |
| `u02/data/cheetadata01` | 0,77 |
| `u03/indices/cheetaidx01` | 0,59 |
| `u02/data/inverdata02` | 0,62 |
| `u03/indices/inveridx01` | 0,53 |
| `u07/data/invhistdata03` | 0,50 |
| `u02/data/acbakifrsdata01` | 0,47 |
| `/u02/data/inverdata01` | 0,45 |

Dos cosas:

- **Estos valores coinciden exactamente con el informe mensual de Oracle** del
  equipo DBA, que menciona «`/u02/data/inverdata03` (94 %)». Es decir, **el dato
  ya se produce por otra vía**; alguien lo transcribe al Excel.
- El encabezado tiene **la columna 2026-01 duplicada** (P4 y Q4). Es un error de
  estructura que nadie ha detectado, precisamente porque esas columnas están
  ocultas.

Hay dos filesystems por encima del 90 %. Es información de riesgo operativo que
**hoy no llega al informe del cliente**.

### 1.5 NUEVO — Hoja `Inidcadores`: dos bloques de metas contradictorios

La hoja tiene **dos tablas**, y sus metas no coinciden:

**Bloque 1 (filas 2–5) — sin columnas de mes:**

| Indicador | Meta |
|---|---|
| Disponibilidad de la plataforma administrada | 0,993 |
| Cumplimiento tiempos de **Atención** | **0,90** |
| Cumplimiento de entregables | **0,80** |

**Bloque 2 (filas 7–10) — el que usa el informe:**

| Indicador | Meta | sep-25 → jun-26 | Promedio |
|---|---|---|---|
| Disponibilidad de la plataforma administrada | 0,993 | 1 · 1 · **0,9802** · 1 · **0,9993** · 1 · 1 · 1 · 1 · 1 | `=+AVERAGE(D8:M8)` → 0,99795 |
| Cumplimiento tiempos de **Solucion** | **0,95** | 1 · 1 · **0,96** · 1 · 1 · 1 · 1 · 1 · 1 · 1 | → 0,996 |
| Cumplimiento de entregables | **0,90** | todos 1 | → 1 |

Difieren **el nombre del segundo indicador** («Atención» vs. «Solución») y **dos
de las tres metas**. Cuál es la contractual es una pregunta abierta (§6, duda 6).

**Por qué el informe acierta, y por qué es frágil:** `filaCabecera` busca la
fila con `Indicador` + `Meta` y **se queda con la última coincidencia**. Como el
bloque 2 va debajo, gana. Si alguien reordenara los bloques, el informe pasaría
a publicar metas del 90 % y 80 % **sin emitir ningún error**.

Los tres promedios de la columna N son las **únicas fórmulas correctas del
archivo**: el rango `D8:M8` cubre exactamente los 10 meses de contrato.

### 1.6 Hoja `Grafica Dispo y Gestion` — resuelto el misterio Real/SETI

Tres bloques:

**a) Filas 3–5, inventario suelto:** `SQLSERVER 216 producción / 106 pruebas`,
`MYSQL 6 / 2`. No lo lee nadie y **no cuadra** con el conteo de CI de abajo
(SQL = 21). Son cosas distintas sin etiqueta que lo diga.

**b) «Disponibilidad Real» (filas 13–17)** y **c) «Disponibilidad SETI»
(filas 21–25)**, ambas con 19 columnas: dic-24 → jun-26.

| Tabla | Motor | CI | Eventos en 19 meses |
|---|---|---|---|
| **Real** | SQL 21 · Mysql 2 · **Oracle 40** · Aws 3 | | Oracle: **nov-25 = 0,9802** y **feb-26 = 0,9732** |
| **SETI** | idénticos | | Oracle: **nov-25 = 0,9802** y **ene-26 = 0,9993** |

Ahora se puede leer la regla:

- **nov-25** aparece en las dos → fue una caída **imputable a SETI**.
- **feb-26** solo en Real (97,32 %) → una caída **no imputable a SETI**, excluida
  de la columna contractual. La lectura «SETI = Real menos lo no imputable»
  funciona.
- **ene-26 rompe la regla**: SETI = 99,93 % y Real = **100 %**. SETI no puede ser
  *peor* que la disponibilidad real.

Y hay una prueba de que el error está en la tabla Real: **el evento de ene-26 sí
existe** — está en la hoja `Disponibilidad` (CHEETA = 0,9993) y en `Inidcadores`
(0,9993). Es decir, **a la tabla «Disponibilidad Real» se le olvidó registrar la
caída de enero.** Tres hojas dicen que pasó; una dice que no.

**NUEVO — los tres totales están rotos.** Verifiqué las fórmulas y sus rangos:

| Celda | Fórmula | Rango real | Resultado | Problema |
|---|---|---|---|---|
| R19 *(fila oculta)* | `=+AVERAGE(K14:R17)` | jul-25 → **feb-26** | 0,998544 | 8 meses; le faltan 4 |
| R27 | `=+AVERAGE(K22:T25)` | jul-25 → **abr-26** | 0,999488 | 10 meses; le faltan 2 |
| R29 «total2» | `=+AVERAGE(K14:T17)` | jul-25 → **abr-26** | 0,998835 | duplica R19 con otro rango |

**Ninguno llega a jun-26**, los tres usan ventanas distintas, y ninguno empieza
donde empieza el contrato. Son fórmulas que nadie extendió al agregar columnas.

Comprobé los tres resultados a mano y coinciden con lo que Excel tiene cacheado,
así que no es un problema de recálculo: los rangos están mal escritos.

**Por suerte, el informe no los lee** — calcula su propio promedio desde la
última columna. Pero cualquiera que abra el Excel y mire ese «Total» está viendo
un número equivocado, y el informe en PowerPoint que se entregaba antes bien
pudo tomarlo de ahí.

### 1.7 Hoja `Casos`

- **Bloque superior (filas 2–20):** categorías con columnas `NOVI | DIC | ENER |
  ABR`. Obsoleto e inconsistente (filas 4, 10 y 11 ocultas). El parser lo
  ignora correctamente porque elige la fila con más celdas interpretables como
  fecha.
- **Tabla real (filas 26–29):** 19 columnas, dic-24 → jun-26.

| Serie | dic-24 → jun-26 |
|---|---|
| ALERTAS | 1 · 1 · 0 · 0 · 0 · 1 · 2 · 28 · 51 · 56 · 59 · 47 · 66 · 74 · 70 · 83 · 54 · 30 · **61** |
| REQUERIMIENTOS | 2 · 5 · 9 · 1 · 3 · 3 · 1 · 5 · 0 · 1 · 0 · 1 · 2 · 5 · 1 · 0 · 3 · 6 · **0** |
| INCIDENTES | ceros salvo nov-25, ene-26 y abr-26 = 1 |

> ### Corrección propia: U27 = 61 no es un error de la auditoría
>
> Una versión anterior de este documento afirmaba que `docs/AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md`
> estaba equivocada por decir que junio son 49 alertas. **Esa afirmación mía era
> el error.** Repliqué la lógica real de `cargarAlertas()`/`cargarGlpi()` contra
> `AlertsList.xlsx` y `glpi (20).xlsx`: el total que el informe realmente
> reporta para junio es **49** (49 alertas dentro del mes calendario + 0
> requerimientos + 0 incidentes de GLPI, sus 8 casos son todos de mayo).
>
> **El 61 de `Casos!U27` es otra métrica, no la del mes calendario**: coincide
> exactamente con el total de filas de Acción Fiduciaria que trae el archivo
> `AlertsList.xlsx` **sin filtrar por mes** (61 filas totales en el export). Todo
> indica que quien llena esa celda cada mes copia «total de filas del export»,
> no «alertas dentro del mes calendario». Son dos definiciones distintas, no una
> celda mal escrita ni un documento desactualizado. La regla de negocio ya
> decidida —mes calendario, 49— sigue siendo la correcta, y
> `AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md` no necesita corrección en este punto.

### 1.8 Hoja `Backups`

- 14 instancias, con los mismos nombres y orden que los 14 CI.
- 19 columnas: dic-24 → jun-26, más una columna `Promedio` (V).
- **Las 266 celdas valen 1.** Cero eventos en 19 meses, y el «Promedio» de cada
  fila es un `1` escrito a mano, no una fórmula.

Una tabla que solo dice 100 % durante 19 meses no aporta información: o los
respaldos nunca han fallado, o nadie está midiendo. El informe mensual de Oracle
del equipo DBA sí trae una sección «6.2 Estado de Jobs de Backup» con datos
reales por instancia, y advierte que `/mnt/BACKUP_DBO` está **al 91 % de
ocupación**. Ese contraste sugiere que la hoja `Backups` es una formalidad
(§6, duda 3).

### 1.9 Hojas `Mitigación` y `Logros`

- **`Logros` está vacía**: solo los encabezados `LINEA SERVICIO | LOGRO |
  BENEFICIO`. El consolidado nunca aporta logros; el archivo cualitativo mensual
  es la única fuente real.
- **`Mitigación`** tiene 3 filas —parches de Oracle RAC, obsolescencia de
  hardware, migración de OnBase a 19c—, todas con `RESPONSABLE: SETI`, todas
  refiriéndose a actividades **de enero y febrero de 2025**, y **las tres
  ocultas**. Ninguna columna de estado, lo que confirma `DATA-009`.

### 1.10 Cómo se calcula cada cosa, verificado

Comprobé la aritmética contra las celdas reales:

| Valor | Regla | Verificación |
|---|---|---|
| **Indicador «Disponibilidad de la plataforma»** | **el mínimo entre los CI**, no el promedio | nov-25: mínimo = 98,02 % ✓ igual al indicador. Promedio de los 14 = 99,2929 % ✗. ene-26: mínimo = 99,93 % ✓; promedio = 99,995 % ✗ |
| Fila del motor Oracle (tabla SETI) | idéntica al mínimo de sus CI | nov-25 y ene-26 coinciden exactamente |
| Medidor cliente (informe) | media simple de la última columna de los 14 CI | jun-26 → 100 % |
| Medidor SETI (informe) | media simple de los 4 motores, **sin ponderar** por sus 21/2/40/3 CI | jun-26 → 100 % |
| Promedio de backups | media de los valores con dato; `null` no cuenta | 100 % |
| Cumplimiento de meta | `cumpleMeta()`: normaliza a 0–100, **redondea ambos a 1 decimal** y compara `≥` | nov-25: 99,2929 % → «99,3 %» = meta → cumple |
| Promedios del Excel | `=+AVERAGE()` | 3 correctos en `Inidcadores`, **3 rotos** en `Grafica` |

**Regla de normalización del informe:** si `|n| ≤ 1,01` se multiplica por 100. Es
lo que permite que `1` signifique 100 %.

### 1.11 El período real: «Mayo» es un nombre obsoleto

**Confirmado sobre el archivo: contiene datos hasta junio de 2026.** Las cinco
hojas con series mensuales terminan en `2026-06-01`, y las columnas son fechas
reales con formato `mmm-yy`, no texto.

El nombre del archivo lleva desfasado al menos desde que se usó para emitir el
informe de junio. **El informe ya no confía en el nombre** (hallazgo `DATA-008`,
corregido): resuelve el período por las columnas. Esa regla debe conservarse, y
por eso el contrato con Mateo exige un campo `periodo` explícito dentro del
archivo.

---

## 2. Cómo interpreta hoy el informe el consolidado

### 2.1 Flujo actual

```
  Santiago Amaya (mensual, a mano)
        │  escribe ~1.000 celdas; ve solo ~6 columnas de las 18
        ▼
  Disponibilidad Consolidado Mayo.xlsx   (8 hojas, nombre desalineado)
        │  alguien lo arrastra al centro de carga
        ▼
  validarArchivo()  →  leerLibro()  (SheetJS, cellDates:true)
        │
   ┌────┴────┬──────────┬───────────┬─────────┬──────────┐
   ▼         ▼          ▼           ▼         ▼          ▼
 Indica-  Disponi-   DispoGes-   Backups   Casos    Logros /
 dores    bilidad    tion                            Mitigación
   │         │          │           │         │          │
   └─────────┴──────────┴───────────┴─────────┴──────────┘
                        │  REPORTE.publicar(dominio, {estado, datos, fuente})
                        ▼
        window.REPORTE — store único, un estado por dominio
        (no_cargado · valido · sin_registros_confirmado · advertencia · invalido)
                        │
   ┌────────┬───────────┼───────────┬──────────────┐
   ▼        ▼           ▼           ▼              ▼
 tarjetas modales   gráficas   slides 4/6/11   PDF / export
```

Dos cosas que hacen viable la automatización:

- **El store es el único punto de verdad.** Nada lee del DOM ni de variables
  globales. Una fuente nueva solo tiene que publicar bien en `REPORTE`.
- **La carga automática ya existe y es segura.** `cargarInsumosAutomaticos()`
  lee `insumos-af.js` como `<script>` vecino, valida versión, período y **huella
  SHA-256**, y deposita el archivo en el mismo `<input type=file>` que usaría
  una persona. Una fuente rota no bloquea a la otra.

### 2.2 Qué espera el HTML, y qué pasa si llega distinto

| Campo | Formato exigido | Si falla |
|---|---|---|
| Nombre de hoja | coincidencia normalizada, admite parcial | dominio `invalido` con mensaje |
| `Cliente` | debe **contener** `accion fiduciaria` | fila descartada **en silencio** |
| `Tipo Ci` | nombre canónico del CI | fila descartada |
| `Meta` | texto o número | `N/A` |
| Columnas de mes | **fecha real** (`Date`, serial, `d/m/aaaa`) | «sin columnas reconocibles» → `invalido` |
| Valores | número; fracción o porcentaje | `null` = sin dato |
| Nombre de indicador | debe contener `disponibilidad` / `tiempos de solucion` / `entregables` | < 3 filas → **bloquea la emisión** |
| Motor | `SQL`, `Mysql`, `Oracle`, `Aws` tal cual | fila fuera de la gráfica |

**Riesgos confirmados con el archivo real:**

1. **La ambigüedad del `1`.** Un CI con disponibilidad del **1 %** se publicaría
   como **100 %**. Hoy es teórico porque el Excel manda fracciones, pero el
   formato nuevo debe usar **escala 0–100 siempre**.
2. **`0` significa cosas distintas según la ruta.** `numDisp` (motores)
   convierte `0` en `null`; `aPctBackup` lo conserva como `0`. Una caída total
   de un motor desaparecería de la gráfica en vez de verse en rojo.
3. **Dos bloques de metas** en `Inidcadores`: el informe acierta por el orden de
   las filas, no por diseño (§1.5).
4. **Filas ocultas que el parser lee igual** (§1.2): las 3 mitigaciones dadas de
   baja pueden entrar al informe.
5. **Emparejamiento por cadena de texto.** `Disponibilidad` ↔ `Backups` se
   alinean por nombre; un `INVHIST` frente a `INVHISTO` rompería la
   correspondencia sin avisar.
6. **Filas leídas hasta la primera celda vacía** en `Grafica Dispo y Gestion`:
   una fila en blanco intercalada trunca la tabla en silencio.

---

## 3. Evaluación de la propuesta de Mateo

### 3.1 Qué hace bien el script

Es un buen trabajo y conviene decirlo primero:

- Reconoce **los tres formatos de fecha** del `alert.log` validando por
  contenido, no por una regex rígida. **Y hace falta**: el informe mensual
  confirma que CHEETA, ACBACOLG y APPACCIO corren **Oracle 10.2.0.5** (formato
  ctime) mientras INVHIST e INVERACC están en **12.2.0.1** (formato ISO).
- Descubre instancias en `ps` **y** en `/etc/oratab`, así que una base caída
  ahora —justo la que importa— no desaparece del informe.
- Cuenta las **caídas abruptas** sin `shutdown` registrado y las marca como
  `ESTIMADA` en vez de presentarlas como medición exacta.
- **Recorta las ventanas a los bordes del período** correctamente: revisé los
  cuatro casos borde y ninguno suma minutos que no debería.
- Marca `cobertura: PARCIAL` cuando el `alert.log` empieza después del inicio de
  la ventana — **declara cuándo su propio número está sobreestimado**.
- Excluye del promedio las bases `SIN_ALERT` en vez de contarlas como 0 o 100.

### 3.2 Los problemas que impiden usarlo tal cual

**(a) La ventana no es un mes calendario.** Mide *N días hacia atrás*.
`./oracle_disponibilidad.sh 30 2026-06-30` da `2026-05-31 23:59:59 →
2026-06-30 23:59:59`: 30 días, pero corrida un segundo e imposible de alinear
con meses de 28 o 31 días.

**(b) Produce un número donde el Excel tiene dos.** El `alert.log` no sabe si una
parada fue una ventana acordada. Sin una lista de exclusiones solo puede
producir la columna **Real** (§3.4).

**(c) Cubre 5 de 14 CI.** Los otros 9 no los ve. Pero —dato nuevo— esos 9 llevan
**18 meses en 100 % sin una sola excepción**, lo que sugiere que hoy tampoco se
están midiendo (§6, duda 1).

**(d) Un solo servidor.** Usa `hostname` y rutas locales. Para Oracle basta: el
informe mensual confirma que las cinco instancias residen en el servidor
**PUMA**.

**(e) Mide la instancia, no el servicio.** El propio script lo advierte: una base
arriba en `RESTRICTED` cuenta como 100 %.

**(f) Detalles menores:** falta `set -uo pipefail`; `ETIQUETA` y `ALERT_FIJO` se
recorren con división por espacios (funciona hoy, se rompe con una ruta que
tenga un espacio); el promedio general es simple entre bases.

### 3.3 ¿Sirve el HTML que genera? — No como integración

El HTML de Mateo es **un buen informe operativo para el equipo de DBA** y
recomiendo conservarlo. Como interfaz de datos no funciona:

| Criterio | Veredicto |
|---|---|
| **Compatibilidad** | El informe consume `.xlsx`/`.csv` y un `insumos-af.js` con base64 + SHA-256. No hay ruta que acepte HTML |
| **Mantenimiento** | Valores en `<td>` sin `id`, mezclados con `<b>`, `%` y clases de color. Un retoque estético rompe la carga **sin error visible**: se leería otra celda |
| **Trazabilidad** | El período solo existe como prosa. Sin versión de esquema ni identificador de corrida |
| **Validación** | No se puede validar un esquema. Quedaría en «encontré una tabla», que es la validación laxa que `DATA-006` ya obligó a corregir una vez |
| **Seguridad** | Todo el diseño actual es «el insumo transporta datos; nada de lo que traiga se ejecuta». Un HTML de terceros es lo contrario |

Y una razón de fondo: **el HTML de Mateo ya es una interpretación** — aplica la
meta 99,30, decide `CUMPLE`/`REVISAR` y promedia. Consumirlo daría **dos
implementaciones de la misma regla de negocio**, una en Bash y otra en
`cumpleMeta()`, que pueden divergir sin que nadie lo note. Es justo el patrón
que produjo los bugs 49/61 y 4/14 de la auditoría.

### 3.4 Recomendación

> ## **Formato estructurado: JSON. No HTML generado.**
>
> Mateo entrega **`disponibilidad-oracle-AAAA-MM.json`**, esquema versionado, un
> archivo por período y motor. **Y conserva su HTML** como informe operativo del
> equipo DBA — dos artefactos, dos públicos, no una disyuntiva.

Por qué JSON y no CSV, siendo que GLPI y AlertOps ya usan CSV:

1. **El dato tiene dos niveles**: una fila por instancia *más* sus ventanas de
   caída. En CSV eso obliga a dos archivos o a aplanar con columnas repetidas.
2. **Los metadatos viajan en el mismo objeto**: período, zona horaria, versión,
   servidor, cobertura del log. En CSV serían un sidecar que se puede
   desincronizar.
3. **Un solo artefacto que hashear.**
4. **Se puede validar estrictamente**, con mensajes concretos.
5. **Generar JSON desde Bash es más fácil que generar HTML**, y Mateo ya genera
   HTML. En el contrato va el emisor exacto.

Si prefiere CSV con fuerza, es **plan B aceptable** (CSV + `.meta.json`); el
informe ya trae un parser CSV robusto. Pero JSON es la recomendación.

### 3.5 Flujo propuesto

```
  Servidor PUMA (Oracle)                      Otros motores (fase 2)
  ┌──────────────────────────┐                ┌──────────────────────┐
  │ oracle_disponibilidad.sh │                │  SQL Server / MySQL  │
  │   --desde / --hasta      │                │  o Grafana (§7.1b)   │
  └───────┬──────────────────┘                └──────────┬───────────┘
          │ dos artefactos                               │
     ┌────┴─────┐                                        │
     ▼          ▼                                        ▼
  JSON        HTML  (para el DBA,              disponibilidad-<motor>-
  esquema v1        no se integra)                 AAAA-MM.json
  + sha256
     │
     ▼  carpeta sincronizada del mes
  <RUTA_INTAKE_BD>/2026-06/
     │
     ▼
  extraer_disponibilidad.py            ← NUEVO (lado informe)
    valida esquema · período · cliente · cobertura
     │
     ▼
  insumos_af.archivo_de()              ← YA EXISTE, sin cambios
     │
     ▼
  insumos-af.js  { glpi, alertas, disponibilidad }   ← tercera clave
     │
     ▼  actualizar_informe.py lo copia junto al HTML
  cargarDisponibilidadBD(file)         ← NUEVO parser
     │
     ▼
  REPORTE.publicar('disponibilidad' | 'ci')
     │
     ▼
  tarjetas · modales · gráficas · slides · PDF   ← SIN CAMBIOS
```

**Lo que hay que construir es poco**: un extractor Python gemelo de
`extraer_alertas.py`, un parser en el HTML y una clave más en `archivos`. El
store, las tarjetas, los modales, las gráficas, el PDF y toda la maquinaria de
validación y huellas **no se tocan**.

---

## 4. Qué se automatiza y qué no

| Sección | Hoja | ¿Automatizable ya? | Comentario |
|---|---|---|---|
| Disponibilidad por CI | `Disponibilidad` | **5 de 14 CI** | Los 9 restantes, pendientes de la duda 1 |
| Disponibilidad global (medidor cliente) | `Disponibilidad` | **No hasta tener los 14** | Con 5 daría un número falso |
| Real / SETI por motor | `Grafica Dispo y Gestion` | **Real sí; SETI no** | Falta el calendario de exclusiones (duda 2) |
| Indicador «Disponibilidad de la plataforma» | `Inidcadores` | **Sí, derivable** | Es el mínimo entre CI (§1.10, verificado) |
| Indicador «Gestión del Servicio» | `Inidcadores` | **Viable por otra vía** | Es SLA de GLPI; `extraer_glpi.py` ya trae los casos |
| Indicador «Entregables» | `Inidcadores` | **No** | Sin fuente de sistema |
| Backups | `Backups` | **No con este script** | Necesita RMAN. **El DBA ya lo reporta** (§7.1a) |
| **Capacidad** | `Capacidad` | **Sí, y el dato ya existe** | Está en el informe mensual de Oracle (§7.1a) |
| Casos | `Casos` | **Ya automatizado** | GLPI + AlertOps |
| Logros / Mitigaciones | `Logros`, `Mitigación` | **No** | Cualitativo. `Logros` está vacía de todos modos |
| **Bolsa de horas** | — | **Fuente encontrada** | `Consumo MENSUAL bolsa de horas.pptx` (§7.1d) |

**Lo que hay que decirle a Santiago sin adornos:** con el script tal como está,
**el consolidado no deja de actualizarse a mano**. Se automatizan 5 filas de una
hoja. Es el paso correcto, pero la automatización completa exige resolver las
dudas de §6 y una fase 2.

---

## 5. Contrato técnico para Mateo

Documento aparte, listo para enviar:
**[`2026-07-28-contrato-tecnico-mateo.md`](2026-07-28-contrato-tecnico-mateo.md)**

---

## 6. Dudas para el negocio

### Bloqueantes

1. **Los 9 CI no-Oracle llevan 18 meses en 100 % exacto. ¿Se están midiendo?**
   PWP, PSE, ACCIONAR, INTRANET, ORFEO, ACCION, CORETUTASK, LEGALBC y VLOZ no
   registran una sola variación en 162 celdas. O son extraordinariamente
   estables, o nadie los mide y se escribe 100 % por defecto. **Antes de
   automatizarlos hay que saber qué son, en qué motor y servidor viven, y quién
   los monitorea.**

2. **¿Existe un calendario formal de ventanas de mantenimiento?** Es lo que
   separa «Real» de «SETI». Sin esa lista, el `alert.log` no puede distinguir
   una parada acordada de una caída, y solo podremos generar la columna Real.

3. **Backups: 266 celdas en 100 % durante 19 meses.** Mientras tanto el informe
   mensual de Oracle reporta el filesystem de respaldos **al 91 %** y trae una
   sección de estado de jobs con datos reales. ¿La hoja `Backups` refleja algo
   medido, o es una formalidad?

4. **La caída de ene-26 falta en la tabla «Disponibilidad Real».** Tres hojas la
   registran (0,9993) y esa no. ¿Se corrige la tabla Real, o hay una razón?

5. **Los tres totales de `Grafica Dispo y Gestion` están rotos** (§1.6) y no
   llegan a jun-26. ¿Alguien los usa? Si el informe en PowerPoint los tomaba,
   se han venido reportando números equivocados.

6. **¿Cuáles son las metas contractuales?** La hoja `Inidcadores` tiene dos
   bloques que dicen cosas distintas: entregables **0,80 vs 0,90**, y
   «Cumplimiento tiempos de **Atención** 0,90» vs «de **Solución** 0,95».

### Importantes

7. **¿El indicador de disponibilidad debe ser el mínimo entre CI?** Está
   verificado que hoy lo es (nov-25 = 98,02 %, el peor CI, no el promedio de
   99,29 %). Es una regla exigente. ¿Es la contractual o un hábito?

8. **¿El mes es calendario y en qué zona horaria?** Asumo América/Bogotá y mes
   completo. Define el denominador (43 200 min en junio, 44 640 en enero).

9. **¿El medidor SETI debe ponderar por número de CI?** Hoy es promedio simple
   de 4 motores; Oracle tiene 40 CI y MySQL 2, y pesan igual.

10. **¿La disponibilidad se mide a nivel de instancia o de servicio?** Una base
    arriba en `RESTRICTED` cuenta como 100 %. ¿Es aceptable contractualmente?

11. **¿Qué pasa si un CI no tiene dato en un mes?** Hoy `null` se excluye del
    promedio. ¿Debería bloquear la emisión?

12. **Las 3 mitigaciones ocultas son de 2025.** ¿Siguen vigentes? Hoy pueden
    entrar al informe si se carga el consolidado sin el archivo cualitativo.

13. **¿La capacidad de filesystems debería llegar al informe del cliente?** Hay
    dos por encima del 90 % y el dato ya se produce.

---

## 7. Qué más se puede automatizar

### 7.1 Alta relación beneficio/esfuerzo

**a) Aprovechar el informe mensual de Oracle que el equipo DBA ya produce.**
Este es el hallazgo con más valor de toda la auditoría.
`Informe_Mensual_Oracle_AcFiduciaria_Junio2026_v3_1.docx` ya contiene, mes a
mes: ocupación de filesystems (**la hoja `Capacidad` completa** — verifiqué que
`/u02/data/inverdata03 = 94 %` coincide celda por celda), política y estado de
jobs RMAN (**la hoja `Backups`**), tablespaces, segmentos, crecimiento, usuarios
DBA y redo logs.

Es decir: **una parte del consolidado se está transcribiendo a mano desde un
informe que ya existe.** Si las consultas que lo alimentan emiten también el
JSON del contrato, se automatizan dos hojas sin trabajo nuevo de extracción.
Vale la pena preguntarle a Mateo cómo se genera ese informe hoy.

**b) Grafana como fuente única de disponibilidad.** Las alertas de AlertOps
entran con `IntegrationName: Grafana` — en junio, 49 de `Tipo: oracle` y 4 de
`Tipo: sqlserver`. **Ya existe un Grafana vigilando estos CI, y ya cubre SQL
Server.** Si tiene Prometheus detrás, una consulta tipo `avg_over_time(up[30d])`
podría resolver **los 14 CI de un golpe**, con la misma definición para todos
los motores. **Podría ser el atajo que evita toda la fase 2**; conviene
preguntarlo antes de escribir un script por tecnología.

**c) Alerta cuando la tarea mensual falla.** El gancho ya está preparado y
comentado en `automatizacion/tarea_mensual.sh:24`, esperando
`TEAMS_WEBHOOK_URL`. Sin esto, una extracción que falle el primero de mes se
descubre cuando alguien abre el informe. Quince minutos de trabajo.

**d) Bolsa de horas: la fuente existe.** Figuraba como «sin fuente oficial»
(`DATA-014`, §10.6), pero es `Consumo MENSUAL bolsa de horas.pptx`: corte
30/06/2026, 0 h consumidas, 100 contratadas, 97 disponibles. Sigue siendo
manual, pero ya sabemos qué es y quién lo produce. Nota: 0 consumidas este mes y
97 disponibles de 100 implica 3 h consumidas antes — conviene confirmar la
aritmética acumulada.

**e) SLA de GLPI calculado, no transcrito.** El indicador «Gestión del Servicio»
(96 % en nov-25) se escribe a mano. `extraer_glpi.py` ya trae la sábana de casos
con sus fechas. Falta la definición contractual de cuál fecha cuenta
(`DATA-014`).

### 7.2 Vale la pena, con más trabajo

**f) Validador del consolidado mientras siga existiendo.** Un script que abra el
Excel y avise de: fórmulas cuyo rango no llega al último mes, columnas de fecha
duplicadas, bloques de metas contradictorios, filas ocultas con datos y series
sin una sola variación en N meses. Los cinco defectos que encontré hoy los habría
detectado solo, y ninguno era visible a simple vista. Es la red de seguridad más
barata mientras el Excel siga en el camino crítico.

**g) Depósito automático del informe en SharePoint.** Ya identificado en
`automatizacion/README.md`. El mecanismo —carpeta sincronizada por OneDrive— ya
está resuelto y probado con `RUTA_ONEDRIVE`.

**h) Generación del PDF sin intervención.** El pipeline existe pero necesita
ventana visible. Con Playwright headless entraría en la tarea mensual. Ojo: la
auditoría dejó anotado que **la descarga real del PDF nunca se verificó
completa**; conviene cerrar eso primero.

**i) `REPORTE.autopruebas()` en la tarea mensual.** Ya existe y corre 47 pruebas.
Ejecutarlas con Node y fallar la tarea si alguna cae convertiría la suite en una
red de seguridad real en vez de una herramienta de consola.

### 7.3 Estructural

**j) Retirar el Excel del camino crítico.** El objetivo final no es «un script
que llena el Excel», sino que **cada dominio tenga su fuente de sistema**:
disponibilidad de la BD, backups del catálogo, capacidad del filesystem, casos de
GLPI, alertas de AlertOps, cualitativo de quien lo escribe. Cuando estén, el
consolidado deja de ser un insumo.

**k) Un histórico inmutable.** Hoy la historia vive en columnas de Excel: si
alguien edita una celda de nov-25, la historia cambia retroactivamente y nadie se
entera — y con esa columna **oculta**, menos aún. Un archivo por período,
versionado y con su huella, hace la serie auditable. La estructura de carpetas
por mes ya existe.

**l) Estandarizar el contrato de insumos.** El esquema que se defina para
disponibilidad sirve tal cual para backups, capacidad y SLA. Definirlo una vez
evita negociar un formato distinto con cada proveedor de datos.

---

## 8. Resumen

- **El Excel «Mayo» contiene junio de 2026.** Confirmado sobre el archivo: las
  cinco series mensuales terminan en `2026-06-01`.
- **8 hojas, no 7.** Hay una `Capacidad` que el informe no lee y cuyos datos ya
  existen en el informe mensual del equipo DBA.
- **Casi nada del Excel es una fórmula.** Unas 1 000 celdas escritas a mano cada
  mes. Ese es el trabajo a eliminar.
- **Cinco defectos que nadie había visto**, todos verificados: tres totales con
  rangos rotos que no llegan a jun-26; dos bloques de metas contradictorios; una
  columna de fecha duplicada; la caída de ene-26 ausente de la tabla «Real»; y
  columnas y filas ocultas que hacen que **quien mantiene el archivo no vea la
  caída de nov-25 ni las mitigaciones que el informe sí puede importar**.
- **El HTML generado no sirve como integración.** Recomiendo **JSON
  estructurado** con esquema versionado, huella y metadatos — y que Mateo
  conserve su HTML para el equipo DBA.
- **El script de Mateo está bien hecho pero cubre 5 de 14 CI.** Necesita ventana
  calendario explícita.
- **La infraestructura de carga ya está lista.** Añadir disponibilidad es una
  clave más en `archivos`, un extractor y un parser.
- **El mejor hallazgo:** parte del consolidado se transcribe a mano desde un
  informe mensual que el equipo DBA **ya produce**. Y existe un Grafana que ya
  cubre Oracle y SQL Server, que podría resolver los 14 CI de una sola vez.
