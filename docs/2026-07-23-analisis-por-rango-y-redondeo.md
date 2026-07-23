# Análisis por rango en los modales + cumplimiento juzgado sobre el valor publicado

**Fecha:** 23 de julio de 2026
**Rama:** `main` (fusionado el mismo día; `feature/analisis-por-rango` se
eliminó tras el merge — ver ajustes posteriores en
[`2026-07-23-sesion-completa.md`, PARTE 7](2026-07-23-sesion-completa.md#parte-7--ajustes-posteriores-mismo-día-tarjeta-compacta-análisis-que-no-calla-variaciones-y-cierre-de-ramas))
**Origen:** Llamada de revisión del 23/07/2026 con Santiago Amaya Cely
(`transcript.docx`) y las capturas enviadas después.

## Contexto

Tres pedidos de la llamada:

1. **Análisis narrativo en los modales que aún no lo tenían.** Solo «Total de
   casos atendidos» (`c5`) tenía la tarjeta. Se pidió en Indicadores del
   servicio (`c4`), Disponibilidad global (`c6`), Gestión de backups (`c7`) y
   Disponibilidad por CI (`c11`), con una condición explícita: *«si le doy clic
   en 3 meses que me haga el análisis de esa parte, si le coloco 6 meses… si le
   coloco 12 meses…»*. Breve, general, y coherente con el periodo visible.
2. **Un cumplimiento reportado como incumplimiento por redondeo.** Corte
   **nov-25** de Disponibilidad por CI, meta 99,3 %: cinco de los 14 CI en 98 %
   → promedio 99,285714 %. La interfaz lo imprime como **99,3 %** —la meta
   exacta— pero la cápsula salía **roja** y el badge decía «Promedio bajo la
   meta». Santiago lo verificó a mano en la llamada: *«si te lo aproxima,
   deberíamos cumplir»*. Debe quedar en **naranja**.
3. **Protección del HTML que se entrega al cliente.**

Requisito transversal añadido con las capturas: **si el análisis queda sin
texto, la tarjeta no debe aparecer en el HTML exportado ni en el PDF.**

## Qué se implementó

### 1. `cumpleMeta()`: una sola regla de cumplimiento

Nueva función global junto a `pct()`. Normaliza fracción→porcentaje con el
criterio ya usado en el archivo (1 = 100 %), redondea valor y meta a **1
decimal** —la precisión con la que se publica el dato y la de la meta 99,3 %— y
compara. Reemplaza las siete comparaciones crudas que había repartidas:

| Dónde | Qué juzgaba |
|---|---|
| `montarRadarCI.estadistica()` | conteo `cumplen` y `estado` del corte (`ok`/`partial`/`bad`) |
| `montarRadarCI` · panel lateral | color de cada fila de sistema |
| `cargarConsolidado` → store `ci` | `cumplen` publicado |
| `actualizarTarjetaDisponibilidad` | chip Cumple/Revisar de `c6` |
| `actualizarTarjetaBackups` | chip de `c7` |
| Minis de indicadores | chip de `c4` |
| `renderC6` | «Estado contractual» del modal |
| `resumenIndicadores` | «Meses bajo meta» |

**Efecto verificado en nov-25:** la cápsula pasa de `is-bad` (rojo) a
`is-partial` (naranja), el badge de «Promedio bajo la meta» a «Promedio cumple ·
con brechas» y el pie de «9 sin brechas · 0 parciales · 1 bajo meta» a «9 sin
brechas · 1 parcial · 0 bajo meta». El hero **9 / 14 no cambia**: los cinco CI
en 98 % siguen sin cumplir individualmente, y así debe ser — lo que cumple es el
promedio del corte, no cada CI.

De paso se corrigió el plural «1 parciales» del pie del radar.

### 2. Análisis sensible al rango en cinco modales

`montarHistorico` y `montarRadarCI` aceptan una opción `analisis` y montan la
tarjeta como bloque hermano de la gráfica. El re-montaje ocurre dentro de
`pintar()`, pero **solo cuando cambia el rango**: el radar también repinta al
elegir un mes en la gráfica, y remontar ahí borraría un textarea abierto a media
edición.

Dos familias de generadores nuevos, con el mismo contrato que
`metricasCasos`/`narrarCasos` (cálculo puro separado de la narración,
deterministas, nunca `NaN`/`Infinity`/`undefined`, cadena vacía si no hay datos):

- **`metricasSeries` + `narrarSeries`** → `c4` (indicadores) y `c6` (motores).
  Promedio del rango, cortes bajo meta, desviación más baja y cómo cierra el
  último corte. En `c6` se descarta la serie de referencia (la meta) antes de
  calcular, igual que hace `resumenMotores`.
- **`metricasRadar` + `narrarRadar`** → `c7` (backups) y `c11` (CI). Recibe los
  `stats` que `estadistica()` ya calcula. Distingue el caso *«justo en el
  límite»* —promedio que no alcanza la meta en crudo pero sí redondeado— del
  incumplimiento real. El vocabulario (género, número, «disponibilidad» vs
  «ejecución») viene del objeto `T` de textos que ya parametrizaba el radar, así
  que backups dice «las 14 instancias» y CI «los 14 CI».

`c5` (casos) conserva su texto sobre el mes reportado y suma una frase final con
el rango visible, calculada por `metricasRangoCasos` — la misma función que
alimenta el pie de la gráfica, para que el modal no pueda contradecirse.

Ejemplo real (CI, rango «Todo»):

> Entre sep-25 y jun-26 la disponibilidad promedio de los 14 CI fue de 99,9 %,
> sobre la meta de 99,3 %. Nueve de los diez cortes cerraron sin brechas; nov-25
> quedó justo en el límite de la meta, con cinco CI por debajo (mínimo 98 %). El
> corte de jun-26 cierra con los 14 CI en 100 %.

En 3M el mismo generador produce el texto de abr-26 a jun-26.

### 3. Edición por rango

La clave de `montarAnalisis` pasa de `<id>` a `<id>:<rango>` (`ci:6M`,
`backups:TODO`, o `2025-09_2026-06` si el rango se fijó a mano). Cada rango
guarda su propia edición: al volver a 6M reaparece el texto editado, en 12M se
ve el automático.

**Migración:** los textos guardados con el formato viejo (`casos`) se adoptan
para el preset por defecto de su tarjeta (`casos:3M`), que es el rango en el que
se escribieron. Sin esto el autor vería desaparecer lo que ya había redactado.

**El rango también viaja al entregable** (`snapshotEstado` → `rangosHistorico`):
con el análisis editado por rango, si el HTML del cliente abriera siempre en el
preset por defecto mostraría el texto automático de otro rango en vez del que el
autor dejó escrito.

### 4. Sin texto, sin tarjeta

- **Modo cliente:** con el texto vacío, `montarAnalisis` no monta nada — ni
  recuadro ni título.
- **Modo autoría:** se ve un marcador con borde punteado («Sin análisis · esta
  tarjeta no se incluirá en el informe exportado ni en el PDF») para poder
  volver a escribirlo. Oculto en el PDF por
  `body.exportando-pdf .analisis-card--vacia{display:none}` y eliminado del
  clon en `podarClon`.
- Guardar en blanco cambia de significado: antes revertía al texto automático,
  ahora significa «este indicador va sin análisis». Para recuperar el automático
  está el botón **«Restaurar análisis automático»**, que solo aparece cuando hay
  algo que restaurar.

### 5. Protección del HTML exportado

Conviene decirlo tal cual: **un HTML que se entrega no se puede proteger de
verdad.** El navegador del cliente tiene que ejecutarlo, así que el código
siempre será legible con «Ver código fuente». Lo que sí se hizo es quitar lo que
explica cómo está construido y dejar clara la propiedad:

- **`despojarComentarios(js)`**: elimina los comentarios del JavaScript
  embebido conservando los avisos de licencia (`/*!`). No usa expresiones
  regulares — `//` dentro de `"http://…"`, de una plantilla o de un literal de
  regex no es un comentario. Recorre el texto con una pila de contextos léxicos,
  necesaria porque las plantillas anidan código: `` `${a?`x`:`y`}` `` es habitual
  en este archivo y una lectura «hasta el siguiente backtick» se desincroniza
  (fallo real detectado y corregido durante la implementación).
- Cada bloque se valida con `new Function(...)` antes de sustituirlo; si no
  compilara, se conserva el original. Un informe legible vale más que uno opaco.
- Se eliminan también los comentarios del HTML.
- Se antepone un aviso de confidencialidad y autoría al archivo generado.
- **No** se implementó bloqueo de clic derecho ni de teclas: no protege nada,
  molesta al lector legítimo y rompe la accesibilidad.

Resultado medido: 64 KB de comentarios fuera y el entregable baja de ~4,3 MB a
**2,9 MB** (el grueso ya venía de no incluir las librerías de solo autoría).

## Verificación realizada

Con los cuatro insumos reales de `Insumos/`, servidos por HTTP local e
inyectados con `fetch()`+`DataTransfer`:

- **Redondeo:** nov-25 en `c11` → cápsula `is-partial`, badge «Promedio cumple ·
  con brechas», pie «9 sin brechas · 1 parcial · 0 bajo meta», hero «9 / 14»
  intacto. Ningún otro corte cambió de color en `c7` ni en `c11`.
- **Análisis por rango:** los cinco modales generan texto; 3M / 6M / 12M / Todo
  producen textos distintos y coherentes con lo que muestra la gráfica. Elegir
  un mes en el radar **no** regenera el análisis (no se pierde una edición en
  curso).
- **Edición por rango:** editado en 6M → cambio a 12M (automático) → vuelta a 6M
  (reaparece lo editado). Clave guardada: `ci:6M`.
- **Migración:** una entrada antigua `casos` escrita en IndexedDB se adopta como
  `casos:3M` al recargar.
- **Tarjeta vacía:** análisis en blanco en `c7` → el clon del export no contiene
  la tarjeta (`0` nodos `.analisis-card--vacia`) y bajo `body.exportando-pdf`
  computa `display:none`, mientras la tarjeta con texto sigue en `block` y
  `.analisis-acciones` se oculta.
- **Export real:** HTML generado, guardado y **abierto**: modo cliente sin
  topbar ni panel de carga, análisis en `c4`/`c5`/`c6`/`c11` sin botones de
  edición, `c7` sin tarjeta, rango de CI en 12M (el que dejó el autor), nov-25
  naranja, cero errores de consola, y el filtro sigue recalculando el texto al
  cambiar de rango.
- **Despojo de comentarios:** los 9 bloques `<script>` del informe compilan tras
  el despojo y no queda ningún comentario superviviente (indicador de
  desincronización del lector).
- **Autopruebas:** 46/47 con los insumos cargados. La única falla —«Portada:
  estado general no afirma cumplimiento»— es **preexistente**: referencia un
  `data-k="estadoGeneral"` que no existe en el HTML, confirmado con
  `git show main` (ya documentado en `2026-07-22-casos-analisis.md`). Se
  añadieron 12 pruebas nuevas: la regla de redondeo y once casos borde de los
  generadores (rango de un corte, serie sin datos, todo en cero, sin meta, sin
  periodos, radar sin cortes, todos bajo meta, un solo sistema, promedio en el
  límite).
- **Sintaxis:** `node --check` sobre los 9 bloques después de cada edición.

## Pendiente / fuera de alcance

- **PDF:** el camino de exportación se ejecuta entero, sin errores de consola ni
  diálogos de error, y las reglas de ocultado están verificadas por CSS
  computado. No se llegó a inspeccionar el archivo final: la versión activa de
  `exportarPDF` es la que redefine el script de dashboards y no pasa por el
  `save` del prototipo de jsPDF que se interceptó para evitar escribir en la
  carpeta de Descargas del usuario.
- Falla preexistente «Portada: estado general» — sigue fuera de este cambio.
- Automatización del GLPI (RPA) y la integración con el servidor de Carlos
  Barrera: quedaron como investigación aparte en la misma llamada.

## Archivos tocados

Un único archivo de la aplicación:
[`informe-accion-fiduciaria 1.html`](../informe-accion-fiduciaria%201.html).
Sin cambios en dependencias, parsers ni store.
