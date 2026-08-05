# Diseño — F7a adaptador Aranda y perfil Bancóldex

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
- `tarjetas.seleccionadas: ['c9']` — hallazgo al verificar en navegador:
  `resolverTarjetasPerfil()` (motor, F3) exige al menos una tarjeta;
  `tarjetas.seleccionadas: []` no es un estado soportado y hace fallar el
  arranque (`El perfil "bancoldex" requiere tarjetas.seleccionadas.`), a
  diferencia de lo que sugiere leer el requisito de `inventario-tarjetas`
  aislado — ese requisito describe qué pasa cuando un perfil **no
  selecciona una tarjeta puntual** (como `c10` en AF), no cuando la lista
  completa está vacía. Además, casi todas las tarjetas del inventario
  compartido llevan texto de presentación **estático**, heredado de Acción
  Fiduciaria y todavía no derivado del perfil activo (c3: contrato
  «CN-21012025»; c4: metas «99,30 %/95 %/90 %»; c12: «Informe mensual
  Oracle») — mostrarlas bajo la marca Bancóldex expondría una cifra ajena
  antes de que exista un dato real. `c9` (bolsa de horas) es la única cuya
  presentación ya es genérica (`'Dato no disponible'`,
  `'Sin fuente oficial de bolsa de horas'`) y cuyo renderizador (`renderC9`)
  es un editor manual sin dependencia de GLPI ni del consolidado — la única
  tarjeta que Bancóldex puede activar hoy sin mostrar nada falso. F7b añade
  la tarjeta de casos (4 categorías) y los lectores de consolidado; esta
  lista crecerá entonces.

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

### `cargarCasosAranda()` no publica en `REPORTE` (hallazgo al implementar)

`REPORTE.publicar(dominio,…)` valida `dominio` contra `this.dominios`, que se
construye una sola vez a partir de `DOMINIOS =
[...new Set(TARJETAS_PREDETERMINADAS.flatMap(t=>t.dominios))]` (F3). Como
Bancóldex no tiene todavía una tarjeta que declare un dominio de casos propio
(ver "Fuera de alcance" en `proposal.md`), no existe ningún nombre de dominio
válido al que publicar sin editar a mano esa lista derivada — exactamente la
segunda lista fija que F3 eliminó. Por eso `cargarCasosAranda()` **devuelve**
`{estado, casos, agregados, fuente, notas}` en vez de publicar, y F7b lo
conecta a `REPORTE` cuando defina el dominio y la tarjeta. Tampoco depende de
`EXTENSIONES_INSUMO` (deriva de `TARJETAS_SELECCIONADAS.flatMap(t=>t.fuentes)`;
la única tarjeta de Bancóldex en F7a, `c9`, declara `fuentes:[]`, así que esa
lista sigue sin una entrada `aranda`): valida la extensión `.xlsx`/`.xls`
directamente, la misma que ya usa `consolidado`.

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
