# Indicadores del servicio: renombrado + modal histórico reutilizable

**Fecha:** 22 de julio de 2026
**Rama:** `feature/indicadores-historico` → merge a `main`
**Commits:** `c2c6d64` (estado base) · `acb96cf` (implementación)
**Origen:** Cambio 1 de la hoja de ruta acordada tras la llamada de revisión del 21/07/2026 con Santiago Amaya Cely (ver [`Acta - Analisis llamada Santiago Amaya Cely.docx`](../Acta%20-%20Analisis%20llamada%20Santiago%20Amaya%20Cely.docx)).

## Contexto

El 21/07/2026 Santiago (líder de cuenta) revisó el informe HTML sección por
sección y aprobó la estructura general como reemplazo definitivo del formato
anterior en diapositivas. De esa revisión salió una lista de ajustes
puntuales, con entrega en dos días y nueva revisión el jueves 23. El primero
de esos ajustes — y el único abordado en este cambio — fue sobre la tarjeta
**Indicadores del periodo**:

1. Renombrar el indicador **"Tiempos de solución"** a **"Gestión del
   Servicio"** en todo el informe.
2. El modal de esa tarjeta no aportaba nada nuevo: repetía el mismo
   resultado, meta y margen del mes que ya se veía en la tarjeta colapsada.
   Se pidió rediseñarlo para mostrar la **evolución histórica** del
   indicador, con un filtro de rango (desde el inicio del contrato hasta el
   mes del informe, nunca después) que por defecto muestre los últimos 3
   meses.

El usuario pidió explícitamente que la solución **no fuera un parche
puntual**: debía quedar diseñada para reutilizarse tal cual en los demás
indicadores con evolución mensual (disponibilidad, backups, CI), que son
pendientes futuros de la misma acta.

## Qué se implementó

### 1. Renombrado (presentación, no la fuente)

El texto que llega en el Excel del cliente (`Cumplimiento tiempos de
Solucion`) **no cambió** — sigue siendo lo que el parser reconoce. Se separó
nombre-de-fuente de nombre-de-presentación con un único mapa:

```js
const ETIQUETA_INDICADOR=[
  {patron:'disponibilidad',      rotulo:'Disponibilidad de la plataforma administrada'},
  {patron:'tiempos de solucion', rotulo:'Gestión del Servicio'},
  {patron:'entregables',         rotulo:'Cumplimiento de entregables'}
];
function rotuloIndicador(nombreFuente){ /* norm() + find + fallback al nombre crudo */ }
```

`cargarIndicadores` publica en el store `nombre` (rótulo) y `nombreFuente`
(texto original, trazabilidad). Cualquier vista que lea `nombre` del store
—tarjeta, tabla del slide 4, modal— recibe el nombre correcto sin duplicar
el mapa. Los dos textos estáticos del HTML (`tarjeta-kpi__mini-etq` y la
celda de la tabla del slide `#s4`) se editaron a mano porque no dependen del
store.

**No se tocó** el título de la sección ("Indicadores del periodo"/"del
servicio") — eso corresponde a un punto distinto del acta (#12, renombrar la
*sección*, no el indicador) que no formaba parte de este pedido. Queda
pendiente de confirmación explícita antes de tocarlo.

### 2. Histórico completo en el store

`cargarIndicadores` seguía leyendo solo 3 columnas (`columnasPeriodo(...,3)`)
porque la tabla del slide 4 y `DATA_CASOS.labels` solo esperan tres meses.
Se añadió un segundo cálculo, en paralelo, sin tocar el primero:

- `colsHistorico`: todas las columnas del Excel desde el **inicio del
  contrato** (leído de `[data-k="finicio"]`, con respaldo `2025-09-01`)
  hasta el **mes del informe**, nunca después.
- Se publica `datos.historico = {periodos, filas}` dentro del mismo dominio
  `indicadores` del store `REPORTE`, con `valores` y `meta` ya normalizados
  a escala porcentual (0–100).

La identidad de cada fila (nombre/meta) se resuelve una sola vez
(`filasBase`) y alimenta tanto el `filas` legado (3 meses) como
`historico.filas` (rango completo), para no llamar `rotuloIndicador()` ni
leer la meta dos veces.

Como `historico` viaja dentro de `datos`, y `snapshotEstado()` ya serializa
`datos` completo sin cambios, **el HTML exportado al cliente incluye el
histórico y su filtro funcionando**, sin tocar el pipeline de exportación.

### 3. Componente reutilizable: `montarHistorico`

Vive dentro del mismo IIFE `#dashboards-detalle` que ya tenía `chart()`,
`head()`, `pct()`, `esc()` — para no duplicarlos ni colgarlos de `window`
(la causa raíz de bugs anteriores documentada en
[`Insumos/AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md`](../Insumos/AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md)).

```js
montarHistorico(contenedor, {
  id,          // clave de estado — separa el rango de cada indicador
  periodos,    // [{clave, etiqueta, mes, anio}] ya recortado por el store
  series,      // [{nombre, meta, valores, color}]
  porDefecto,  // nº de meses iniciales (3)
  resumen      // (periodosVisibles, seriesVisibles) => HTML del resumen
})
```

Puntos de diseño:

- **Estado fuera del DOM.** El rango elegido vive en un `Map` del módulo
  (`rangosHistorico`), indexado por `id`. `renderAll()` reconstruye por
  completo el `innerHTML` de cada tarjeta en cada apertura de modal y en
  cada notificación del store; sin este `Map` el filtro se olvidaría cada
  vez que otro dominio publica. Mover el filtro **no** llama a
  `renderAll()`: solo repinta su propio host (gráfica + resumen), así los
  controles no pierden foco.
- **`chart()` se extendió** con un quinto parámetro `opts`, fusionado sobre
  las opciones base con un helper de merge profundo (`fusionarProfundo`).
  Las llamadas existentes (una sola, en `renderC6`) siguen funcionando
  igual — `opts` es opcional. El histórico lo usa para una **escala Y
  dinámica** (`min(valores) − holgura` … `max(valores) + holgura`, tope
  100,5) en vez del `min:95/max:101` fijo que ya usaba `chart()` para otros
  IDs "percentage", que habría cortado un valor por debajo de 95.
- **Tipo de gráfica: línea con marcadores**, no barras. Justificación: las
  series son casi planas cerca del 100 %; con 10+ meses de contrato, barras
  agrupadas por indicador saturan el ancho, mientras la línea escala sin
  degradarse. Consistente con `dash-chart-dispo`, que ya usa el mismo
  patrón.
- **Sin líneas de meta en la gráfica**: con tres indicadores hay tres metas
  distintas (99,3 / 95 / 90 %); pintarlas todas sería ruido. La meta vive en
  el tooltip (`Gestión del Servicio: 96% · meta 95%`) y en el resumen.
- **Presets `3M · 6M · 12M · Todo` + Desde/Hasta**: el `<select>` solo
  contiene las opciones de `periodos`, que el store ya recortó al rango
  válido — estructuralmente no es posible seleccionar un mes fuera de
  contrato o posterior al periodo del informe.

CSS nuevo con prefijo `.hist-*`, autocontenido (el componente pone su propia
tarjeta — quien lo monta solo pasa un `<div>` vacío) y con
`body.exportando-pdf .hist-controls{display:none}` para que el PDF capture
el rango activo sin un control interactivo inerte.

### 4. `renderC4` reescrito

De un bloque que repetía resultado/meta/margen (`signal-stage`,
`contract-metrics`, `variance-board` — CSS que quedó sin uso, no se borró
por el riesgo de tocar una línea CSS minificada compartida con
`.backup-command`) a: cabecera existente → `montarHistorico` con las tres
series (Disponibilidad, Gestión del Servicio, Entregables; colores azul
`#1F77B4` / naranja `#ED7D31` / verde `#2E7D32`, la misma terna que
`chartCasos`) → resumen por indicador (`resumenIndicadores`): promedio del
rango, mejor/peor mes, meses bajo meta.

## Bug encontrado y corregido durante la verificación

Al probar con el Excel real (`Insumos/Disponibilidad Consolidado
Mayo.xlsx`), "Meses bajo meta" daba **0** en todos los indicadores incluso
con noviembre-25 claramente por debajo de meta en disponibilidad
(98,02 % vs. meta 99,3 %). Causa: `historico.filas[].meta` se publicaba con
el valor crudo del Excel (`0.993`), mientras que `valores` sí se normalizaba
a porcentaje (`99.3`) — comparar `98.02 < 0.993` nunca es cierto. Se corrigió
normalizando `meta` con el mismo helper que normaliza `valores`
(`aPctHistorico`), sin tocar `datos.filas[].meta` (legado, que otros
consumidores como `actualizarTarjetasDesdeStore` ya normalizan por su
cuenta). Verificado de nuevo con datos reales tras el fix.

## Verificación realizada

Todo con el navegador integrado, sirviendo el proyecto por HTTP local
(`python3 -m http.server`) para poder inyectar el Excel real vía `fetch()` +
`DataTransfer` sobre el input real (mismo camino que un usuario cargando el
archivo a mano):

- **Parser:** `historico.periodos` con 10 entradas (sep-25→jun-26);
  nov-25 = 98,02 % / 96 % / 100 %, coincide con el Excel.
- **Sin regresión:** tabla del slide 4 sigue con 3 columnas;
  `DATA_CASOS.labels` sigue con 3 posiciones (el gráfico de casos no se
  tocó).
- **Modal:** arranca en 3M (abr–jun-26) sin tocar nada; 12M y Todo muestran
  la caída de nov-25; Desde/Hasta no puede salirse del rango sep-25→jun-26;
  el resumen recalcula correctamente al cambiar el rango (confirmado el fix
  del bug de meta).
- **Renombrado:** "Gestión del Servicio" visible en tarjeta, tabla del
  slide 4, leyenda de la gráfica y resumen; el parser sigue reconociendo el
  texto original del Excel.
- **Autopruebas embebidas** (`REPORTE.autopruebas()`): todas en verde,
  incluida una nueva — el último punto de cada serie histórica coincide con
  lo que muestra la tarjeta colapsada.
- **PDF:** `.hist-controls` pasa a `display:none` bajo
  `body.exportando-pdf`.
- **Export HTML:** `REPORTE.d('indicadores').datos.historico` — la misma
  referencia que `snapshotEstado()` serializa hacia el entregable — se
  confirmó completa y con la meta ya normalizada.
- **Sintaxis:** los 9 bloques `<script>` del archivo se extrajeron y
  pasaron `node --check` después de cada edición.
- Sin errores en consola en ninguna prueba.

## Archivos tocados

Un único archivo: [`informe-accion-fiduciaria 1.html`](../informe-accion-fiduciaria%201.html)
(+261/−33 líneas). Nada de infraestructura, dependencias ni otros archivos
del repo.

## Pendiente (fuera de este cambio)

- Renombrar la sección "Indicadores del periodo" → "Indicadores del
  servicio/contrato" (punto #12 del acta) — no pedido en este ciclo.
- Aplicar `montarHistorico` a disponibilidad, backups y CI, tal como quedó
  diseñado para reutilizarse.
- El resto de ajustes de la sesión del 21/07 (colores del gráfico de casos,
  tarjeta de motores, bolsa de horas, etc. — ver el acta completa).
