# Diseño — F7 adaptador Aranda y perfil Bancóldex

## F7b — lectores de consolidado (hallazgos al verificar contra los archivos reales)

### Bug real: coincidencia de columna «BD» con datos, no con la cabecera

`cargarBackups()` generalizado usaba `filaCabecera()` para ubicar la fila
con la columna declarada (`'bd'` para Bancóldex). `filaCabecera()` hace
`c===a||c.includes(a)` y **se queda con la última fila que matchea**, no la
primera. La instancia real `BCOEXCCBD27` normaliza a `bcoexccbd27`, que
`.includes('bd')` — así que la "cabecera" resuelta era la primera fila de
datos, no la fila 0 real. Se corrigió a una búsqueda de coincidencia
**exacta** (`norm(c)===nombreColBackups`) en vez de reusar `filaCabecera()`
para este lector. Verificado contra `Bancoldex/Data consolidada
junio_Bancoldex 2026.xlsx`: 11 BD, promedio 100 %, coincide con la hoja
real.

### Hallazgo real: `Disponibilidad Real` sin corte vigente

La hoja existe y su tabla («DISPONIBILIDAD REAL», filas por motor: MY SQL,
ORACLE, SQLSERVER, WEB LOGIC) se resuelve correctamente con
`cargarDisponibilidadTabla()`, pero sus columnas de fecha en el archivo de
junio-2026 solo llegan hasta **jun-25** — un año de rezago en el propio
archivo del cliente, no un error de lectura. El motor bloquea el
consolidado con `"La tabla «Disponibilidad Real» no tiene una columna para
jun-26."`, comportamiento correcto (la restricción inviolable #2 exige no
inventar cifras). **Queda como hallazgo para reportar a Bancóldex/SETI**,
no como pendiente de este change.

### Cuarto lugar con texto de AF quemado: resumen de `c11`

Al probar con un consolidado completo (insumo real + una columna de prueba
de junio-2026 con disponibilidad 100 %, ver docs de sesión), el resumen
colapsado de `c11` seguía diciendo *"4 de 4 cumplen la meta de 99,30%"* —
un literal dentro de `actualizarTarjetasDesdeStore()`, distinto de
`presentarTarjetaPerfil()` (que ya cubre el texto por defecto de la
tarjeta) y de `TARJETA_PENDIENTE` (que cubre el estado sin cifra). Se
corrigió a leer `ci.datos.meta` (que `cargarDisponibilidadTabla()` ya
publica desde `PERFIL.metas.disponibilidad`), con el mismo valor 99,3 %
como default cuando el dominio no lo declara — AF sin cambios.

### Precisión de la meta en el modal `c6` (soporte fuera del preset final)

La prueba controlada con una copia del consolidado que agrega junio de 2026
mostró que `c6` redondea la meta 99,98 % a 100 % mediante `pct(meta)`. Esto
vuelve visualmente indistinguibles la meta contractual y un cumplimiento
perfecto. El árbol de trabajo contiene una solución local: usar dos decimales
cuando la estrategia declarada es `tabla-con-fechas` y conservar el formato
existente en los demás perfiles.

La decisión semántica es independiente del formato: Bancóldex debe seguir
mostrando SETI `Sin dato` y sin histórico SETI, porque la fuente solo respalda
`Disponibilidad Real` por motor. No se copiará esa serie a SETI para llenar el
modal. El formato a dos decimales se conserva como soporte para la estrategia
`tabla-con-fechas`, pero `c6`/`c11` se excluyen del preset final: el único
libro original termina en jun-25 y el fixture con jun-26 no es evidencia. Por
ello esta ruta no bloquea ni aporta cifras al informe Bancóldex entregable.

### Tercer lugar con texto de AF quemado: `TARJETA_PENDIENTE`

Además del `presentacion.items` de `INVENTARIO_TARJETAS` (ya cubierto por
`presentarTarjetaPerfil()`), `actualizarTarjetasDesdeStore()` usa un mapa
aparte, `TARJETA_PENDIENTE`, para repintar una tarjeta cuando su dominio
sigue sin cifra — con el texto de meta de AF quemado ("Meta 99,30%..."). Se
verificó en navegador: con `disponibilidad` bloqueada (hallazgo anterior),
la tarjeta `c6` de Bancóldex mostraba la meta de AF. Se generalizó
`TARJETA_PENDIENTE` para consultar el mismo
`PERFIL.tarjetas.presentacion[id]` antes de usar su valor por defecto.

### Por qué `PERFIL.lineaBase` no lee la hoja «Linea Base»

El reconocimiento identificó que `Linea Base` trae `AMBIENTE` y dos columnas
`CANTIDAD` (contrato vs. corte). No se escribió un lector para esa hoja en
F7b: `PERFIL.lineaBase` (usado por `renderC3()`, heredado de la rama F6)
es una declaración **estática** del perfil, verificada a mano contra la
página «Control línea base» del PDF de referencia (Total General 237→257),
igual que ya lo es para AF y Novaventa. Ningún perfil, incluido Bancóldex,
tiene hoy un lector dinámico de esa hoja — construirlo sin un segundo
cliente que lo justifique violaría la regla de `project.md`.

## `perfiles/base.js`

Hasta ahora `PERFILES_REGISTRADOS` solo resuelve `accion-fiduciaria` (raíz) y
`novaventa` (hereda de AF). El plan maestro reserva `base` para un cliente
que no comparte lo suficiente con ningún perfil existente. `base` no
representa a ningún cliente: no tiene `aliasCliente` de negocio, sus metas y
tarjetas quedan vacías/mínimas, y cualquier perfil que lo use debe declarar
todo lo propio. Se registra igual que los demás, con `extiende: null`, para
que `resolverPerfil('base')` funcione y la cadena de Bancóldex
(`bancoldex → base`) no sea un caso especial en `resolverPerfil()`.

## Selección de perfil activo por `?perfil=` (hallazgo, no planeado)

Al verificar en navegador se encontró que en el cierre de F5
`const PERFIL = resolverPerfil('accion-fiduciaria');` estaba **fijo** — no
existía el mecanismo `ID_PERFIL_ACTIVO` que lee `?perfil=` de la URL (ese
mecanismo se agregó después, en la rama F6, que este change no incluye por
partir del cierre de F5). Sin él, `base`/`bancoldex` quedan registrados pero
inalcanzables: no hay forma de cargar el motor con otro perfil que no sea
Acción Fiduciaria. Se agrega la misma resolución `PERFIL_EMBEBIDO?.id ||
new URLSearchParams(location.search).get('perfil') || 'accion-fiduciaria'`
que ya usa (independientemente) la rama F6, así que ambas ramas convergerán
al mismo texto en este punto al mezclarse — un conflicto de mezcla trivial,
no una divergencia de comportamiento. Sin `?perfil=` ni perfil embebido, el
resultado es exactamente `'accion-fiduciaria'`: mismo comportamiento que
antes para Acción Fiduciaria.

## `perfiles/bancoldex.js`

Extiende `base`. Declara (datos, sin funciones):

- `contrato`, `metas.disponibilidad = 0.9998` (evidencia del reconocimiento).
- `fuentes.casos` (ver abajo) — **no** `fuentes.glpi`: Bancóldex no tiene GLPI.
- `almacen.prefijo = 'informeBancoldex'`.
- `textos` con las mismas claves que ya usan AF/Novaventa.
- `tarjetas.seleccionadas: ['c3','c4','c5','c7','c8','c8m']`. Es el preset
  de cierre respaldado por el PDF aprobado y los tres libros originales del
  corte. `c6`/`c11` quedan fuera por disponibilidad desactualizada; `c9` por
  un TYA de otro periodo sin contrato/saldo; `c12` por no existir insumo
  mensual exportable. Ninguna tarjeta vacía se usa como relleno.

## Fuente `casos` (Aranda)

```js
casos: {
  lector: 'tabular-xlsx',
  adaptador: 'aranda-export',
  // Alias ya normalizados (minúsculas, espacio en vez de guion bajo): ver
  // "Alias de columna: normalizados, no literales" más abajo.
  cabecera: {estrategia: 'primera-fila-con', campos: [['numero del caso'], ['fecha registro']]},
  columnas: {
    id: ['numero del caso'], tipoCaso: ['tipo de caso'], jerarquia: ['jerarquia'],
    cumplimiento: ['indicardor de cumplimiento'], // typo real de la fuente, no se corrige
    fecha: ['fecha registro'], motor: ['motor'],
  },
  filtroCliente: {estrategia: 'archivo-alcance-unico'},
  jerarquia: {separador: '.'},
  sla: {estrategia: 'columna-cumplimiento', verdaderos: ['cumple'], falsos: ['no cumple']},
}
```

### Alias de columna: normalizados, no literales (hallazgo al verificar)

`col()`/`candidatosCabecera()` comparan `norm(celda)` contra el alias **tal
cual está escrito en el perfil** — el alias mismo no pasa por `norm()`. La
primera versión de este perfil declaró `['numero_del_caso']` (calcado del
nombre de columna real, con guion bajo) y `resolverCabecera()` no encontró
ninguna fila candidata: `norm('NUMERO_DEL_CASO')` da `'numero del caso'`
(guion bajo → espacio), que nunca es igual ni contiene
`'numero_del_caso'`. Los alias de AF/Novaventa ya siguen esta convención
(`'fecha de apertura'`, `'tiempo para resolver excedido'`) porque sus
columnas reales ya usan espacios; Aranda es la primera fuente con guiones
bajos, así que es la primera vez que el detalle importa. Se corrigió a
`['numero del caso']`, `['tipo de caso']`, `['fecha registro']` y se
verificó con el arnés Node de este change (ver "Verificación de F7a")
contra el export real: encabezado resuelto en la fila 0, 72 filas
adaptadas.

### `cargarCasosAranda()` publica en el dominio compartido `casos`

El cierre configura `c5` declarativamente con `dominios: ['casos']`; por eso
`DOMINIOS` incorpora el destino sin agregar una segunda lista fija.
`cargarCasosAranda()` publica un objeto `modo: 'aranda-tipo-motor'` con
agregados por tipo, motor, categoría de requerimiento y SLA. El store no
persiste ni exporta identificadores o filas crudas de tickets: el entregable
solo recibe los agregados necesarios para explicar las gráficas.

`renderC5()` conserva la tarjeta, el modal y el componente
`montarHistorico()` de Acción Fiduciaria. La adaptación Bancóldex agrega una
dona por motor, barras horizontales por categoría y un análisis narrativo;
no presenta tablas de Excel. Con un único corte real no se inventan meses
históricos: la barra apilada muestra solo jun-26.

### Por qué `adaptador: 'aranda-export'` y no una nueva `PERFIL.fuentes.glpi`

`cargarGlpi()` (línea ~3330) es una función de ~150 líneas ya cargada de
reglas propias de AF/Novaventa: cruce con
`RECONCILIACION_INDISPONIBILIDADES`, exclusión de "revisiones de alerta",
escritura directa en `#s4 tbody`, y los arreglos `DATA_CASOS.requerimientos` /
`.incidentes` (dos series, no cuatro). Generalizarla para Bancóldex — 4 tipos,
sin revisiones de alerta, sin indisponibilidades — sería reintroducir ramas
por cliente dentro de una función que hoy es literal-AF, exactamente lo que
`project.md` prohíbe ("ningún archivo `informe-<cliente>.html` con lógica
propia" aplicado a una función en vez de un archivo). Se prefiere una función
nueva, paralela, que comparte los mismos primitivos de F5
(`casoCanonico()`, `resolverCabecera()`, `col()`) sin tocar la existente. La
integración con la interfaz (qué botón, qué tarjeta) es F7b porque necesita
su propio diseño visual, no una reutilización forzada de `#s4`.

### Decisión de alcance de cliente: archivo de alcance único

El reconocimiento descartó filtrar por `Proyecto` (siempre "Mesa de Servicios
TI.", cero casos) y por `COMPANIA` (pierde 8 de 72 filas reales que el PDF sí
cuenta). Se declara `filtroCliente.estrategia = 'archivo-alcance-unico'`: el
adaptador acepta todas las filas del archivo tal como Aranda lo entrega,
porque el export ya es específico de Bancóldex — la identidad del cliente la
garantiza el perfil seleccionado en el centro de carga, no una columna. Un
archivo que mezclara clientes no tiene hoy una señal fiable para separarlos
(ver "Pendiente pequeño" abajo); por eso esta estrategia se implementa como
paso-a-través explícito y documentado, no como filtro adivinado.

### Clasificador `aranda-por-tipo-de-caso`

A diferencia de `clasificarTipoGlpi()` (que infiere de categoría con regex),
Aranda declara el tipo directamente en `TIPO_DE_CASO`. El canónico solo
admite `requerimiento|incidente|alerta|cambio|caso_bd|otro`
(`TIPOS_CASO_CANONICO`, línea 2153); la hoja `Junio` trae
`Incidente - Monitoreo`, `Requerimiento`, `Tarea`, `Incidente`. Mapeo:

| `TIPO_DE_CASO` | `CasoCanonico.tipo` |
|---|---|
| `Requerimiento` | `requerimiento` |
| `Incidente`, `Incidente - Monitoreo` | `incidente` |
| `Tarea` | `otro` |
| cualquier otro valor | `otro` (se registra en notas, no falla) |

`Incidente` e `Incidente - Monitoreo` colapsan al mismo tipo canónico porque
el canónico no distingue monitoreo — esa distinción es visual (F7b) y se
recupera de `categoria`/`jerarquia`, que conservan el texto original de
`TIPO_DE_CASO`. No se agrega un séptimo valor a `TIPOS_CASO_CANONICO` sin un
segundo cliente que lo necesite (regla dura de `project.md`).

### SLA `columna-cumplimiento`

```
'Cumple' → true, 'No cumple' → false, vacío o cualquier otro valor → null
```

Paralela a `columna-excedido` (que invierte un booleano de "excedido"),
`columna-cumplimiento` lee directamente un booleano de "cumplido". Ambas
estrategias son casos de la misma regla dura ya vigente en
`metricasSlaCanonico()`: solo `true` cuenta. Con los 72 casos reales, 71
`Cumple` + 1 `No cumple` + 0 vacíos coincide con la tabla de SLA del
reconocimiento.

### `cabecera-de-dos-filas` (declarada, no implementada en F7a)

El `Indicador` de Bancóldex tiene meses en la fila 2 y `BANCOLDEX|SETI` en la
fila 3. `resolverCabecera()` (línea 2146) solo soporta `primera-fila-con` y
lanza si se le pide otra estrategia — comportamiento correcto y ya probado.
F7a **no** implementa esta estrategia todavía: no hay lector de consolidado
que la use hasta F7b. Queda declarada aquí para que F7b no tenga que
rediseñarla, y su ausencia de código no bloquea F7a porque nada la invoca
todavía.

## Cierre end-to-end

### Consolidado selectivo

El cargador ejecuta únicamente los lectores cuyos dominios pertenecen al
preset activo. Para Bancóldex procesa `indicadores` y `backups`, pero no
invoca la tabla `Disponibilidad Real` desactualizada. Así un dominio excluido
no bloquea evidencia válida de otro dominio del mismo libro.

### Un libro cualitativo, dos dominios

La fuente `cualitativos` declara una sola entrada y las hojas exactas
`Logros`/`Mitigación`. El lector publica ambos dominios y exige que todas las
fechas de entrega de mitigaciones pertenezcan al periodo seleccionado. Esta
decisión evita pedir dos archivos artificiales y conserva la validación del
corte.

### Restauración y periodo

En el arranque, `aplicarPeriodo({revalidarInsumos:false})` fija el periodo sin
revalidar antes de que IndexedDB restaure los archivos. Después cada insumo se
procesa por su ruta normal. Además, el paquete automático `insumos-af.js` se
omite cuando el perfil declara una fuente propia de casos; de otro modo los
insumos de Acción Fiduciaria podían reemplazar junio de Bancóldex por julio.

### Salida autocontenida

El estado exportable rehidrata indicadores, casos Aranda, backups, logros y
mitigaciones antes de pintar tarjetas y gráficas. El perfil y los agregados
viajan embebidos; no se requieren Excel, IndexedDB ni un servidor en la
entrega al cliente.

## Gap preexistente: diapositivas «constantes» no dependen de la selección

Verificando en navegador con `?perfil=bancoldex` se confirmó que `c3` (línea
base) y `c9` (bolsa) son diapositivas «constantes»: `actualizarVisibilidad()`
solo alterna `display` para `c4,c5,c6,c7,c8,c8m,c11` (según si su dominio
tiene datos); `c3`/`c9`/`c12` quedan siempre visibles, y `renderAll()` solo
ejecuta el renderizador de una tarjeta si está en `TARJETAS_SELECCIONADAS`.
Como Bancóldex no selecciona `c3`, `renderC3()` nunca corre y la diapositiva
conserva su marcado estático original — incluido `text('[data-k="contrato"]')
||'21012025'`, un campo editable por el consultor en el DOM (no derivado de
`PERFIL.contrato`, a diferencia de `contrato.inicio` que F2 sí migró). Esto
**no es un defecto de F7a**: es una brecha preexistente de la migración
multicliente — ninguna fase anterior extrajo el código de contrato/
instancias/bases de datos de `c3` a datos del perfil, así que cualquier
cliente nuevo hereda el mismo texto de Acción Fiduciaria hasta que el
consultor lo edite a mano en el Centro de carga, igual que ya debe hacer con
otros campos hoy. Seleccionar solo `c9` para Bancóldex evita agregar
diapositivas *nuevas* con contenido incorrecto (p. ej. `c5` diría «Requiere
AlertsList y GLPI del periodo», falso para Bancóldex) sin pretender resolver
esta brecha ya existente, que queda anotada como pendiente para cuando se
extraiga `c3` a datos del perfil (ningún change lo ha hecho todavía para
ningún cliente, incluida Novaventa).

## Verificación de F7a

Con fixtures sintéticos (mismos nombres de columna y los mismos dos valores
de SLA que la fuente real, contenido inventado) más una comparación puntual
contra el export real de `Bancoldex/Casos  + tareas BD junio 2026.xlsx`
(nunca versionado): 72 casos, agregados por tipo y por motor, y SLA 71/1
coinciden con `Bancoldex/reporte-bancoldex-2026-07-02.pdf`. Acción Fiduciaria
y Novaventa no tienen ninguna línea de código modificada por este change —
solo funciones nuevas — así que no se requiere `verificar_ab.py` para F7a
(no hay superficie de regresión); se documenta igual como evidencia de que
la suite existente sigue en verde.

## Pendiente pequeño registrado

Si en el futuro aparece un export de Aranda con más de un cliente mezclado,
`archivo-alcance-unico` no lo detecta y el resultado sería incorrecto en
silencio. No se resuelve aquí porque no hay evidencia real de ese caso
(regla de "dos clientes con evidencia real" de `project.md`); si ocurre, la
fuente `casos` deberá declarar `filtroCliente.estrategia` con una columna y
regla nuevas, verificadas contra esa evidencia.
