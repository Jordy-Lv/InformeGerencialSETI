# Corrección de los hallazgos de la validación de recarga de insumos — 4 de agosto de 2026

**Para:** quien continúe (Claude, en otra sesión, u otra persona).
**Qué es esto:** el registro de la sesión que corrigió los cinco puntos que
[`2026-08-04-validacion-recarga-de-insumos.md`](archivo/2026-08-04-validacion-recarga-de-insumos.md)
dejó en su lista «Qué convendría corregir» (P6, H6, P1+P2, H2+H3, P3). Léelo
antes de tocar `incrustar_insumos()`, `cargarDispoGestion()`, `cargarCasos()`,
`fijar_periodo()`/`archivo_de()`, o `reconciliar()` en
`extraer_indisponibilidades.py`.

**Rama de trabajo:** `fix/recarga-insumos-2026-08-04`.

**Alcance:** exactamente los cinco puntos de la lista de la validación
anterior — ninguno bloqueaba el uso normal descrito en la pregunta original
del usuario (recargar el consolidado con disponibilidad/backups corregidos),
así que esto es trabajo de robustez sobre casos de borde, no una corrección
urgente.

---

## 1. P6 — `incrustar_insumos()` ahora es idempotente (`automatizacion/insumos_af.py`)

**El bug.** Incrustar dos veces (correr el script sobre un HTML que ya traía
un bloque `window.__INSUMOS__`) dejaba **dos** bloques `<script>`. Cada
incrustación se inserta justo después de `<head>`, empujando el bloque
anterior hacia abajo — así que el bloque **nuevo** quedaba primero en el
documento y el **viejo** quedaba después. Como ambos `<script>` reasignan la
misma variable global y se ejecutan en orden de aparición, **el que corre al
final gana: el viejo**, pisando el nuevo en silencio. Era el hallazgo más
contraintuitivo de la validación.

**El fix.** `incrustar_insumos()` ahora busca, entre todos los `<script>` del
HTML, el que ya contiene `window.__INSUMOS__` y lo **reemplaza en su propio
lugar** en vez de insertar uno nuevo al lado. Sin bloque previo, el
comportamiento no cambia (se inserta tras `<head>`, como siempre).

**Pruebas:** `automatizacion/test_insumos_af.py::TestIncrustarInsumosIdempotente`
(nuevo) — primera incrustación inserta tras `<head>`; segunda incrustación
reemplaza (un solo bloque en el resultado, con el contenido nuevo).

---

## 2. H6 — `cargarDispoGestion()` limpia la diapositiva 6 sin la hoja «Grafica Dispo y Gestion» (HTML)

**El bug.** Con `return;` a secas ante la hoja faltante, `pintarTabla()` y la
asignación `window.ESTADO_DISPONIBILIDAD=resumen` nunca llegaban a correr.
`REPORTE.dominios.disponibilidad.datos.seti` sí quedaba en `null`
correctamente (`cargarDisponibilidad()`, que corre antes, republica
`seti:null` en cada carga, corra o no `cargarDispoGestion()`) — pero el DOM
de la diapositiva 6 (`#s6 .t-real`/`.t-seti tbody`, el medidor `[data-k="gseti"]`)
y `window.ESTADO_DISPONIBILIDAD` seguían mostrando los datos de la carga
anterior. Desincronía real entre lo que el store sabía y lo que la
diapositiva mostraba en pantalla.

**El fix.** Ante la hoja faltante, `cargarDispoGestion()` ahora:
- limpia `window.ESTADO_DISPONIBILIDAD` (`null`),
- vacía las dos tablas del DOM (`#s6 .t-real tbody`, `#s6 .t-seti tbody`),
- pone el medidor SETI en «N/A»,
- avisa en el panel de carga (`avisar('consolidado', …)`).

**Verificado en vivo** (no solo leído): servidor local (`python3 -m
http.server`), variante del consolidado sin la hoja «Grafica Dispo y
Gestion», cargada por la ruta real de archivo (`DataTransfer` + evento
`change`). Antes del fix habría quedado en 100 %/4 filas; con el fix:
`window.ESTADO_DISPONIBILIDAD` → `null`, medidor → `N/A`, 0 filas en ambas
tablas, aviso presente.

---

## 3. P1+P2 — desfase de periodo entre fuentes, visible en el paquete (`automatizacion/insumos_af.py`, `extraer_glpi.py`, `extraer_alertas.py`, `extraer_indisponibilidades.py`, HTML)

**El bug (dos hallazgos con la misma causa raíz).** `fijar_periodo()` avanza
`paquete['periodo']` cada vez que una fuente corre, pero nunca toca
`archivos.*` de las fuentes que no volvieron a correr en esa corrida. Si
`extraer_indisponibilidades.py` sale temprano (RUTA_INDISPONIBILIDADES sin
configurar, archivo inexistente, error tras reintentos) mientras GLPI/AlertOps
sí avanzan el periodo, el paquete final queda con `periodo: julio` pero
`archivos.indisponibilidades` con el cruce de junio — y nada en el HTML lo
detectaba.

**El fix — un invariante verificable, no una bitácora de eventos.** En vez de
tratar de registrar cada transición durante la corrida (frágil: varias
fuentes pueden correr en la misma invocación de `actualizar_informe.py`, y un
registro que se sobrescribe puede enmascarar un desfase detectado por una
fuente anterior), cada `archivos.<clave>` ahora guarda **su propio periodo**
(`archivo_de(…, periodo=…)`, nuevo parámetro opcional, usado por los tres
extractores). El HTML (`cargarInsumosAutomaticos()`) compara, en cada carga,
el `periodo` de cada fuente presente contra `paquete.periodo` — si no
coinciden, esa fuente quedó huérfana de una corrida anterior y se avisa. Es
un chequeo derivado del estado actual del paquete, no un histórico que haya
que limpiar: se autocorrige solo en cuanto esa fuente vuelve a correr para el
periodo vigente.

**Pruebas:**
- `automatizacion/test_insumos_af.py::TestPeriodoEnArchivoDe` — `archivo_de()`
  guarda el periodo cuando se da, no agrega la clave si no; `fijar_periodo()`
  no toca `archivos.*` existentes (documenta el comportamiento que hace
  necesario el chequeo del lado HTML).
- Verificado en vivo en el navegador: `window.__INSUMOS__` simulado con
  `periodo: 2026-07` y `archivos.indisponibilidades.periodo: 2026-06` — el
  aviso aparece señalando exactamente esa fuente y ese desfase; `archivos.glpi`
  (con periodo `2026-07`, coincidente) no se marca.

---

## 4. H2+H3 — `cargarCasos()` limpia en vez de dejar la cifra vieja (HTML)

**El bug.** Con `return null;` a secas (hoja «Casos» faltante, sin fila de
encabezado con fechas, o sin columnas de fecha reconocibles) o con
`if(A) DATA_CASOS.alertas=A.slice();` sin `else` (una fila específica —
p. ej. «Incidentes» — no diligenciada), tanto `alertasConsolidadoMes` como la
serie del gráfico de la diapositiva 5 se quedaban con el valor de la carga
**anterior**, sin ningún aviso. El número en pantalla dejaba de venir del
archivo recién cargado sin que nada lo señalara.

**El fix.**
- Hoja/encabezado/columnas de fecha faltantes: `alertasConsolidadoMes=null` y
  aviso explícito (`avisar('consolidado', …)`), en vez de conservar el valor
  anterior.
- Fila faltante (Alertas/Requerimientos/Incidentes): esa serie se deja en
  `0` para el archivo actual — mismo criterio que ya usaba el histórico de la
  misma función (`Ah||colsHistorico.map(()=>0)`) — y se avisa cuál fila
  faltó, en vez de conservar la cifra de la carga anterior.

**Verificado en vivo:** variante sin hoja «Casos» → `alertasConsolidadoMes`
pasa de `999` (carga anterior) a `null`, con aviso. Variante sin la fila
«Incidentes» → la serie de incidentes del mes en curso pasa de `555` (carga
anterior) a `0`, con aviso; Alertas/Requerimientos (filas sí presentes) se
actualizan con normalidad.

**Nota de metodología:** para aislar el efecto del consolidado, `fileGlpi` y
`fileAlertas` se vaciaron antes de cada prueba — igual que documentó la
sesión de validación, esos inputs quedan «pegados» tras el auto-cargado
inicial y `revalidar()` los reprocesa en cada carga, así el usuario solo haya
tocado el consolidado.

---

## 5. P3 — `reconciliar()` reporta duplicados de NUMERO CASO GLPI (`automatizacion/extraer_indisponibilidades.py`)

**El bug.** Dos filas del log de indisponibilidades con el mismo NUMERO CASO
GLPI pero «Atribuible a SETI» distinto se resolvían con `por_caso[digitos]=fila`
— gana la última fila leída, sin ninguna señal de que había un conflicto que
el equipo debía resolver en el Excel.

**El fix.** `reconciliar()` ahora devuelve `(reconciliadas, duplicados)`:
`duplicados` es `{digitos: [valores en orden de aparición]}` para cada caso
con más de una atribución distinta. El comportamiento de resolución **no
cambió** — no hay forma de adivinar cuál fila es la correcta sin que el
equipo lo confirme — pero `verificar()` ahora lo reporta como observación
(hasta 5 ejemplos) para que aparezca en la salida del script.

**Pruebas:** `automatizacion/test_extraer_indisponibilidades.py` (nuevo) —
sin duplicados, con duplicados de atribución distinta, sin falso positivo
cuando la atribución repetida es la misma (normalizada), y que `verificar()`
solo menciona duplicados cuando los hay.

---

## 6. Verificación general

- **Python:** `python3 -m unittest discover -s automatizacion -p 'test_*.py'`
  — 14 pruebas, todas en verde (las 4 previas de `clasificar_caso_glpi` +
  10 nuevas de esta sesión).
- **HTML:** los 9 bloques `<script>` del archivo se extrajeron y se
  verificaron con `node --check` (individualmente y concatenados) — sintaxis
  válida.
- **HTML en vivo:** servidor local + variantes del consolidado (`openpyxl`,
  mismo patrón A/B/C/D/E de la validación anterior) cargadas por la ruta real
  de archivo (`DataTransfer` + evento `change`, no simulación de la lógica en
  consola). H2, H3, H6 y P1+P2 (lado HTML) confirmados con estado
  antes/después. P6 y P3 se probaron con unittest directo sobre las
  funciones de Python, no en el navegador (no tienen contraparte JS).
- No se corrió `REPORTE.autopruebas()` (bloque «con archivos»): esta sesión
  no tocó esa suite ni sus fixtures; queda fuera de alcance.

## 7. Qué queda fuera de alcance

Los puntos de "Qué falta cubrir" de la validación original siguen sin cubrir:
sin tests automatizados de regresión para recarga/idempotencia más allá de
los añadidos aquí (que sí quedan como regresión permanente, a diferencia de
las pruebas manuales de la validación), H1 (diálogo nativo del SO) sigue sin
poder verificarse con las herramientas disponibles, H4 sigue confirmado solo
por lectura de código, y no se probó carga concurrente ni recuperación desde
IndexedDB.
