# Modal "Total de casos atendidos": rediseño funcional + análisis editable

**Fecha:** 22 de julio de 2026
**Rama:** `feature/casos-analisis` (pendiente de merge a `main`)
**Origen:** Cambio 2 de la hoja de ruta acordada tras la llamada de revisión del 21/07/2026 con Santiago Amaya Cely, sobre el modal de la tarjeta **"Total de casos atendidos"** (`c5`).

## Contexto

El modal repetía en una tabla inferior (`.case-register`) exactamente los mismos datos que ya mostraba el bloque superior (alertas/requerimientos/incidentes, con porcentaje y un "Estado" que siempre decía "Registrado"). Además, "Incidentes atribuibles a SETI" — la cifra que más le importa mostrar al cliente como evidencia de gestión — vivía como una píldora pequeña dentro del bloque rojo, casi invisible.

Se pidió: eliminar la redundancia, dar protagonismo real a "atribuibles a SETI" (con estado favorable/de atención, nunca solo por color), y usar el espacio liberado para un análisis narrativo automático **y editable**, con la misma arquitectura de histórico + filtro ya construida para el cambio anterior (Indicadores).

## Hallazgo crítico: qué es realmente un "incidente atribuible a SETI"

Antes de tocar el modal, analicé de dónde salía esa cifra. El parser de GLPI (`cargarGlpi`) clasificaba como "incidente" cualquier fila cuya **categoría completa** contuviera la palabra "incidente" — pero GLPI solo tiene una carpeta de primer nivel, `INCIDENTES`, que agrupa cosas muy distintas:

| Categoría (segundo nivel) | En el archivo real (46 filas) | Qué es en realidad |
|---|---|---|
| `Revision Alerta` | 31 | Ticket **autogenerado por el monitoreo** para revisar una alerta que AlertsList ya cuenta por separado. Título siempre `Alerta DataBase [cliente][host][DB]...`. No es una falla nueva. |
| `Revision Acceso` | 1 | Mismo origen (alerta autogenerada), otra etiqueta. |
| `Reportar Falla / Incidente` | 2 | **Falla real** reportada sobre el servicio administrado. |

El parser anterior contaba las 31+1 revisiones como si fueran incidentes reales. Lo confirmé contra la fuente autoritativa (fila `INCIDENTES` de la hoja `Casos` del consolidado): esa fila vale 0 en 16 de 19 meses — si las revisiones de alerta contaran como incidentes, habría decenas por mes, no 0-1.

**Corrección aplicada en `cargarGlpi`:** ahora se lee el segundo nivel de la categoría (`INCIDENTES > Revision Alerta` → `revision alerta`). Solo cuenta como *incidente atribuible* lo que no sea una revisión de alerta. Las revisiones se cuentan aparte (`revisiones`) y quedan registradas — **solo para control interno, nunca al cliente** — en `REPORTE.reconciliaciones`, con el mismo patrón ya usado para el desfase 49/61 de alertas.

En junio 2026 esta corrección **no cambia ninguna cifra publicada** (los 8 casos de Acción Fiduciaria en el archivo GLPI están fechados en mayo y son todos requerimientos), pero sí corrige un bug real que se habría manifestado en cualquier mes con revisiones de alerta del cliente. Verificado con un archivo GLPI sintético: 2 "Revision Alerta" + 1 "Reportar Falla" → `revisiones:2`, `inc:1` (correcto).

## Qué se implementó

### 1. Histórico completo de casos

`cargarCasos` ahora publica, además de los 3 meses que ya alimentaban la tabla del slide 5 (sin tocar), un histórico completo desde el inicio del contrato (`casos.datos.historico`), replicando el patrón ya usado en `cargarIndicadores`. Verificado contra el Excel real: los 19 valores de las filas ALERTAS/REQUERIMIENTOS/INCIDENTES coinciden exactamente con el store para los 10 meses desde sep-25.

### 2. Redundancia eliminada

Se borró `.case-register` (la tabla) y todo su CSS. También se limpió `.case-months`/`.case-month*` — el **sombreado rojo/rosado** del mes actual que Santiago pidió quitar — ya que la evolución mensual ahora vive en el histórico con filtro (barras), no en esas barras de progreso caseras.

### 3. KPI destacado de incidentes atribuibles a SETI

Nuevo bloque `.case-seti` con tres reglas duras:
- Nunca depende solo del color: siempre lleva ícono (✓ / !) **y** texto explícito.
- 0 → tono favorable, "Sin incidentes atribuibles a SETI".
- ≥1 → tono de atención, "N incidente(s) atribuible(s) a SETI — requiere revisión".
- Si hubo revisiones de alerta excluidas, una nota aparte lo explica ("de los N casos tipo incidente en GLPI, M correspondieron a revisión de alerta...").

### 4. `montarHistorico` extendido para reutilizarse con barras

El componente construido para Indicadores (línea, color por serie) ahora acepta `tipo:'bar'` y `colorPorPeriodo:true`. En este segundo modo el color representa **el periodo**, no el tipo de dato — exactamente lo pedido: mes reportado en azul oscuro (principal), el anterior en azul medio (secundario), el resto en azul claro (terciario). El mes reportado además lleva una etiqueta textual en el eje ("jun-26 · mes reportado"), no solo el color.

Se eligieron barras verticales (no líneas) porque la gráfica compara *totales por mes*, no series por tipo de caso — con una línea, un solo color no puede representar "el periodo" de forma consistente con lo pedido.

### 5. Análisis narrativo determinístico (`metricasCasos` + `narrarCasos`)

`metricasCasos` es la única función que calcula: total, desglose y porcentaje por tipo, variación contra el mes anterior (nunca "infinito %": si el mes anterior es 0, se reporta el delta absoluto), tendencia de los últimos 3 meses, categoría predominante o al 100 %. `narrarCasos` arma el texto por fragmentos, solo uniendo lo aplicable.

Probado contra 9 casos borde (mes anterior en 0, todos los meses en 0, un solo mes de datos, categoría al 100 %, incidentes sin atribución, con atribución, tres meses iguales, aumento grande, sin histórico) — ninguno produce `NaN`, `Infinity` ni `undefined`. Cinco de estos casos quedaron embebidos como autoprueba permanente en `REPORTE.autopruebas()`.

### 6. Análisis editable (`montarAnalisis`, reutilizable)

Componente nuevo, mismo patrón de estado-fuera-del-DOM que `rangosHistorico`. Modo lectura → botón "Editar análisis" → textarea con Guardar/Cancelar. Un badge indica "Automático" o "Editado manualmente".

**Detección de datos desactualizados:** en vez de un hash aparte, la "firma" guardada es el propio texto automático en el momento de editar (determinístico). Si al reabrir el texto automático ya no coincide con esa firma, aparece un aviso con botón "Regenerar análisis automático" que pide confirmación antes de reemplazar el texto editado — nunca lo sobrescribe en silencio.

**Persistencia:** solo en modo autoría, vía IndexedDB (clave `_analisis`, mismo mecanismo que los insumos). El HTML exportado al cliente no toca IndexedDB; el texto editado viaja embebido en `window.__ESTADO__.analisisPersonalizado` (`snapshotEstado()`).

## Verificación realizada

Con los insumos reales (`Insumos/`), navegador headless servido por HTTP local:

- **Histórico de casos:** 10 periodos (sep-25→jun-26); los 19 valores de alertas/requerimientos/incidentes coinciden con el Excel celda a celda.
- **Clasificación GLPI:** archivo sintético con 2 "Revision Alerta" + 1 "Reportar Falla" para Acción Fiduciaria → `revisiones:2`, `inc:1`, reconciliación registrada con el mensaje correcto.
- **Modal:** sin tabla redundante; KPI de atribuibles visible al abrir (probado en estado favorable, 0); barras con color por periodo y etiqueta "mes reportado"; resumen del rango (total, promedio, mejor/peor mes) correcto.
- **Análisis:** se genera solo y coincide con `narrarCasos`; edición → guardado → badge "Editado manualmente"; cambio de periodo → aviso de datos desactualizados sin perder el texto; "Regenerar" pide confirmación y luego sí reemplaza.
- **Persistencia real:** editado, recargada la página completa, restaurados los insumos guardados → el texto editado vuelve exactamente igual.
- **PDF:** `.hist-controls` y `.analisis-acciones`/`.analisis-aviso` quedan en `display:none` bajo `body.exportando-pdf` (confirmado por CSS computado); `exportarPDF()` corre sin errores en consola.
- **Exportar HTML:** el archivo generado contiene el texto editado, `window.__INFORME_CLIENTE__=true`, `window.__ESTADO__` con `analisisPersonalizado`, sin topbar/panel de carga ni librerías de solo autoría (xlsx.js). No se completó la apertura del archivo descargado en una pestaña nueva para evitar escribir en la carpeta de Descargas real del usuario sin confirmación; se verificó el contenido del blob generado en memoria en su lugar.
- **Autopruebas embebidas:** 34 verificaciones, 33 PASA. La única falla (`Portada: estado general no afirma cumplimiento`) es un defecto **preexistente**, no introducido en este cambio — confirmado comparando contra `main`: el chequeo referencia un atributo `data-k="estadoGeneral"` que no existe en ningún lugar del HTML, ni antes ni después de este cambio.
- **Sintaxis:** los 9 bloques `<script>` pasaron `node --check` después de cada edición.

## Archivos tocados

Un único archivo: [`informe-accion-fiduciaria 1.html`](../informe-accion-fiduciaria%201.html) (+486/−43 líneas). Sin cambios en dependencias ni otros archivos del repo.

## Pendiente / hallazgos fuera de este cambio

- **Autoprueba rota preexistente:** "Portada: estado general no afirma cumplimiento" referencia un `data-k="estadoGeneral"` que no existe en el HTML (confirmado también en `main`, previo a este cambio). No se corrigió por estar fuera del alcance de este cambio — queda para una intervención específica.
- El resto de ajustes de la sesión del 21/07 no cubiertos aún (motores con nombres reales, filtro de fechas en backups, disponibilidad por CI, bolsa de horas, etc.).
