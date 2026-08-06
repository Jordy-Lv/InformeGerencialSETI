# Validación: ¿el informe se actualiza al recargar un insumo modificado? — 4 de agosto de 2026

> **Actualización (mismo día):** los cinco puntos de la sección «Qué
> convendría corregir» (P6, H6, P1+P2, H2+H3, P3) ya se corrigieron. Ver
> [`2026-08-04-correccion-recarga-de-insumos.md`](../2026-08-04-correccion-recarga-de-insumos.md).

**Para:** quien continúe (Claude, en otra sesión, u otra persona).
**Qué es esto:** respuesta a una pregunta concreta del usuario: *"si ingreso
el mismo consolidado de disponibilidad pero cambio unos datos, ¿el HTML se
actualiza con los nuevos datos al volver a cargarlo?"*. No es una auditoría
completa del sistema — es una prueba A/B ejecutada de verdad (no solo lectura
de código) contra el HTML y el pipeline Python, con hallazgos verificados
empíricamente. **No se corrigió nada**: por decisión del usuario, esta sesión
fue solo de validación y reporte.

Relacionado: [`2026-08-02-correccion-de-la-auditoria-y-verificacion-ab.md`](../2026-08-02-correccion-de-la-auditoria-y-verificacion-ab.md)
(la sesión anterior que corrigió `HISTORICO_LEDGER`/`DATA_CASOS.labels`,
relevante para los hallazgos de casos aquí).

---

## Veredicto directo

**Sí, para lo que preguntaste: la disponibilidad y los backups del
consolidado sí se actualizan correctamente al recargarlo con datos
distintos.** Probado empíricamente: cambié disponibilidad de 100 % a 96,4 %
y backups de 100 % a 95,7 % en una copia del consolidado, lo volví a cargar
por la ruta real del usuario (el mismo input de archivo, mismo evento
`change` que dispara el navegador), y el informe reflejó ambos valores nuevos
de inmediato, sin quedar nada de la carga anterior.

Pero encontré **cuatro puntos donde una recarga puede dejar datos
silenciosamente desactualizados**, sin ningún aviso en pantalla — no en el
campo que preguntaste, sino en la hoja `Casos` (gráfico de la diapositiva 5)
y la hoja `Grafica Dispo y Gestion` (diapositiva 6). Estos sí importan si el
consolidado que recargas alguna vez llega con esas hojas incompletas o
faltantes. Ver hallazgos H2, H3, H6, P1 abajo.

---

## Metodología

Todo el material de prueba vive en el scratchpad de la sesión, no en el
repo. Pasos:

1. Serví el repo por `python3 -m http.server` (no `file://`: se necesita
   HTTP para poder hacer `fetch()` de los `.xlsx` de prueba desde la consola
   y construir objetos `File` reales).
2. Generé con `openpyxl` cuatro variantes de
   [`Insumos/Disponibilidad Consolidado Mayo.xlsx`](../../Insumos) a partir del
   original (**A**), cambiando valores del último periodo real del archivo
   (**junio-2026**, no julio: es el último mes con datos en las hojas
   `Disponibilidad`, `Backups`, `Casos` e `Inidcadores`):
   - **B** — disponibilidad 100 %→50 %, backups 100 %→40 %, Alertas 61→999,
     Requerimientos 0→777, Incidentes 0→555.
   - **C** — igual que B, sin la hoja `Casos`.
   - **D** — igual que B, sin la fila `Incidentes` en `Casos`.
   - **E** — igual que B, sin la hoja `Grafica Dispo y Gestion`.
3. En el navegador, limpié `IndexedDB`/`localStorage`, fijé el periodo del
   informe a junio-2026, y cargué cada variante **exactamente como lo hace
   un usuario**: asignando el archivo al `<input type="file">` real vía
   `DataTransfer` y disparando `input.dispatchEvent(new Event('change'))` —
   el mismo evento que escucha el listener de
   [`informe-accion-fiduciaria 1.html:4527`](../../informe-accion-fiduciaria%201.html).
   Cada carga esperó a `revalidar()` (la cola de revalidación real del
   sistema), no a un timeout arbitrario.
4. Capturé el estado completo (`REPORTE.dominios`, `DATA_CASOS`,
   `alertasConsolidadoMes`, `window.ESTADO_DISPONIBILIDAD`) antes y después
   de cada carga, y comparé campo por campo.
5. En Python, ejecuté directamente las funciones de `automatizacion/` (no
   solo las leí) contra datos sintéticos en un sandbox, sin tocar
   `automatizacion/salida/` del repo.

Nota importante sobre el primer intento: la primera corrida de la prueba A/B
dio un resultado confuso (el gráfico de casos parecía no actualizarse nunca).
La causa no era un bug del consolidado — era que la página, al arrancar,
auto-carga GLPI/AlertsList desde `insumos-af.js` y esos archivos quedan
«pegados» en sus inputs; cada `revalidar()` los reprocesa aunque el usuario
solo haya tocado el consolidado, y como esos archivos automáticos eran de
julio (no del junio que estaba probando), su lógica de «archivo de otro mes»
pisaba la cifra de alertas con el histórico. Repetí la prueba con esos dos
inputs vacíos para aislar el efecto del consolidado en sí — ver H5 abajo para
el hallazgo real que esto reveló.

---

## Hallazgos — lado navegador (HTML)

| # | Hipótesis | Veredicto | Evidencia |
|---|---|---|---|
| **Core** | Recargar el consolidado con datos nuevos actualiza disponibilidad y backups | **CONFIRMADO — funciona** | `promedioCliente`: 1 → 0,9642857…; `backups.promedio`: 100 → 95,714…; KPIs en pantalla: "100,0%"→"96,4%", "…al 100%…"→"…al 96%…" |
| **Core** | Recargar el consolidado con datos nuevos actualiza el mes actual del gráfico de Casos | **CONFIRMADO — funciona** (una vez aislado del efecto de abajo) | `DATA_CASOS.alertas[2]`: 61→999, `requerimientos[2]`: 0→777, `incidentes[2]`: 0→555 |
| H2 | `cargarCasos()` con salida temprana (`return null`) deja `alertasConsolidadoMes` del consolidado ANTERIOR | **CONFIRMADO** | Cargué C (sin hoja `Casos`) tras B (Alertas=999): `alertasConsolidadoMes` siguió en `999`, sin aviso ni error, aunque C no tiene ninguna hoja `Casos` de la que sacar ese número |
| H3 | Series de Casos se actualizan por fila (`if(A)/if(R)/if(I)`); una fila faltante deja esa serie desalineada con las etiquetas nuevas | **CONFIRMADO** | Cargué D (sin fila `Incidentes`) tras B: `DATA_CASOS.incidentes[2]` siguió en `555` (de B), sin aviso — el número mostrado no viene de D en absoluto |
| H4 | El consolidado no reemplaza logros/mitigaciones si vinieron ya de un archivo mensual autoritativo del cliente | **DELIBERADO** (código con aviso explícito, no ejecutado empíricamente por no tener un archivo mensual de prueba con el formato exacto) | [`:3898`](../../informe-accion-fiduciaria%201.html) `cualitativoAutoritativo()`; emite `avisar('logros', 'Se conservaron los logros del archivo mensual…')` |
| H5 | El histórico automático (`HISTORICO_LEDGER`) siempre pisa lo que trae el Excel, incluso para el mes actual | **DESCARTADO** (para el mes actual) — el código sí excluye el mes en curso del pisado (comentario "F2b" en `aplicarHistoricoAutomatico`, confirmado con prueba aislada). Para meses **pasados** sí manda el histórico sobre el Excel — pero eso es intencional y correcto: el histórico se corrige re-corriendo `extraer_glpi.py`/`extraer_alertas.py`, no editando el consolidado a mano | Ver metodología: sin la interferencia de GLPI/AlertOps pegados, B mostró 999/777/555 en el mes actual, no los valores del ledger |
| — | Hallazgo nuevo (no estaba en la lista original): reprocesar GLPI/AlertsList «pegados» en sus inputs (auto-cargados al arrancar) al recargar solo el consolidado puede pisar la cifra de Alertas del mes actual, si esos archivos son de otro mes | **CONFIRMADO, real** | Antes de aislar la prueba: `DATA_CASOS.alertas[2]` quedó en `53` (el histórico) en vez de `999` (el Excel recién cargado), porque `cargarAlertas()` se reprocesó también y, al no encontrar filas de junio en el AlertsList de julio, cayó a `DATA_CASOS.historico.alertas` |
| H6 | `window.ESTADO_DISPONIBILIDAD` y la tabla/medidor SETI (diapositiva 6) quedan con datos del consolidado anterior si el nuevo no trae la hoja `Grafica Dispo y Gestion` | **CONFIRMADO, con impacto visible** | Cargué E (sin esa hoja) tras B: `window.ESTADO_DISPONIBILIDAD.seti` siguió en `1` (100 %) y la tabla `#s6 .t-seti tbody` en el DOM siguió mostrando "100%" en todas las celdas — **visible en pantalla**, no solo en una variable interna. El store (`REPORTE.dominios.disponibilidad.datos.seti`) sí quedó correctamente en `null`: hay una desincronía real entre lo que el store sabe y lo que la diapositiva 6 muestra |
| H7 | El texto de "Análisis del periodo" editado a mano sobrevive a cualquier recarga, sin invalidarse automáticamente | **CONFIRMADO** (comportamiento deliberado y documentado en el código) | Inserté una entrada en `analisisPersonalizado` con una firma artificialmente vieja, recargué el consolidado, y la entrada — texto y firma vieja — sobrevivió intacta. El banner de aviso ("los datos del periodo cambiaron") no se verificó visualmente por límite de tiempo, pero la lógica que lo dispara (comparación de firmas) está confirmada en el código |
| H1 | Ningún `input.value=''` en el HTML: si el picker no dispara `change` al re-seleccionar el mismo archivo, no se reprocesa nada | **No verificable con las herramientas de esta sesión** (el diálogo nativo de "elegir archivo" queda fuera de lo que un navegador controlado por script puede abrir). Confirmado por lectura: no existe ningún `input.value=''` en todo el archivo. **Comprobación manual sugerida al usuario:** editar el `.xlsx` en disco, volver a seleccionarlo con el mismo nombre desde el mismo cuadro de diálogo, y ver si el chip de "Consolidado" se repinta. Si no, seleccionar primero otro archivo (o el mismo con otro nombre) y luego el correcto es la vía de contingencia |

---

## Hallazgos — lado Python (`automatizacion/`)

Todos ejecutados de verdad (no solo leídos) contra datos sintéticos en el scratchpad.

| # | Hipótesis | Veredicto | Evidencia |
|---|---|---|---|
| P1 | `extraer_indisponibilidades.py` tiene 3 salidas tempranas (`RUTA_INDISPONIBILIDADES` sin configurar, archivo inexistente, error tras reintentos) que ocurren **antes** de tocar `insumos-af.js` | **CONFIRMADO** | Simulé un `insumos-af.js` con `periodo: junio-2026` y `archivos.indisponibilidades` de junio. Corrí `main()` con `--archivo` apuntando a un archivo inexistente (dispara la salida `return 2`): el archivo quedó **byte a byte idéntico**. Si en el flujo real GLPI/AlertOps sí corrieron y avanzaron el periodo del paquete a julio, este paso deja `periodo: julio` con `archivos.indisponibilidades` de junio — desincronía real que el HTML no valida |
| P2 | `fijar_periodo()` cambia el periodo del paquete pero no toca `archivos.*`, dejando archivos "huérfanos" de otro mes | **CONFIRMADO** | Con un paquete de junio-2026, llamé `fijar_periodo(paquete, "2026-07")`: el periodo cambió a julio, pero `archivos.glpi` y `archivos.indisponibilidades` siguieron ahí (de junio). Solo se devuelve el periodo anterior para que el llamador imprima un aviso por stderr — nada bloquea ni limpia automáticamente |
| P3 | `reconciliar()` deduplica por `NUMERO CASO GLPI` con `por_caso[digitos]=fila`: dos filas del mismo caso con "Atribuible a SETI" distinto → gana la última, en silencio | **CONFIRMADO** | Dos filas sintéticas con el mismo caso GLPI, una `SI` y otra `NO`: el resultado tomó `NO` (la última leída), sin ningún aviso en `verificar()` |
| P4 | `copiar_resguardo(proteger=True)` conserva la copia vieja en OneDrive si el contenido cambió para el mismo mes | **DELIBERADO, confirmado como diseñado** | Corrí una v1 y luego una v2 (contenido distinto) para el mismo `glpi-2026-06.csv`: la copia en OneDrive se quedó con v1, con el aviso exacto por stderr y la vía de escape `FORZAR_ONEDRIVE=1` documentada. Consecuencia real: el HTML mostrará la cifra corregida (v2), pero el archivo de auditoría en OneDrive seguirá con la v1 vieja hasta que alguien fuerce la sobrescritura |
| P5 | `RUTAS_INSUMOS[0]='_datos/insumos-af.js'` tiene prioridad sobre la ruta plana en el HTML, y nada en Python escribe ahí | **DELIBERADO/latente — sin manifestarse hoy** | Busqué `_datos/` en todo el repo y el disco del proyecto: no existe en ningún lado ahora mismo. Es un riesgo dormido, no un problema activo: si alguna vez aparece un `_datos/insumos-af.js` residual (de un despliegue viejo o una prueba manual), ganaría silenciosamente sobre el recién generado |
| P6 | `incrustar_insumos()` (`find('<head>')` + splice) no es idempotente: aplicado dos veces deja dos bloques `window.__INSUMOS__`, y gana el viejo | **CONFIRMADO, con el resultado más contraintuitivo de esta prueba** | Incrusté un `insumos-af.js` de junio en un HTML mínimo, y luego incrusté uno de julio **sobre el resultado ya incrustado**. Quedaron 2 bloques `window.__INSUMOS__`. Cada incrustación se inserta justo después de `<head>`, empujando el bloque anterior más abajo — así que en el documento final el bloque de **julio queda primero** y el de **junio queda después**. Como los `<script>` se ejecutan en orden de aparición y cada uno reasigna la misma variable global, **el que corre al final gana: junio, el viejo**, pisando julio en silencio |
| Adicional | `historico_casos.actualizar_periodo()` (el "camino feliz" del ledger) | **CONFIRMADO — funciona correctamente** | Simulé una corrección de alertas para un mes ya existente en el ledger (53→61) y una llegada posterior de GLPI con requerimientos/incidentes del mismo mes: cada `actualizar_periodo()` solo tocó los campos dados, sin borrar los otros. Nota: no versiona el valor anterior — la única huella de una corrección es el timestamp `actualizado` (y git, si el archivo se versiona) |

---

## Qué falta cubrir (fuera del alcance de esta sesión)

- No hay ningún test automatizado (JS ni Python) que cubra re-carga o
  idempotencia — todo lo de arriba se probó a mano en esta sesión y no queda
  como regresión permanente. `REPORTE.autopruebas()` y `test_insumos_af.py`
  no tocan ninguno de estos escenarios.
- H1 no se pudo verificar con las herramientas disponibles (requiere el
  diálogo nativo del sistema operativo).
- H4 se confirmó por lectura de código, no con una carga real de un archivo
  mensual de logros/mitigaciones.
- No se hicieron pruebas de carga concurrente ni de recuperación desde
  IndexedDB (`restaurarInsumosGuardados`).

## Qué convendría corregir, en orden sugerido de impacto

1. **P6** — `incrustar_insumos()` debería ser idempotente (reemplazar un
   bloque `window.__INSUMOS__` ya incrustado, no insertar uno nuevo al lado).
   Es el más contraintuitivo: el dato viejo gana sobre el nuevo, al revés de
   lo esperable.
2. **H6** — `cargarDispoGestion()` debería limpiar/avisar explícitamente
   (no solo retornar) cuando falta la hoja `Grafica Dispo y Gestion`, para
   que la diapositiva 6 no se quede pintada con datos de la carga anterior.
3. **P1 + P2** — cuando `extraer_indisponibilidades.py` sale temprano, o
   `fijar_periodo()` detecta un periodo distinto, debería quedar registrado
   en el propio paquete (p. ej. `archivos.indisponibilidades.periodo` o un
   campo de advertencia) para que el HTML pueda detectar y avisar del
   desfase, en vez de aplicar la reconciliación vieja sin decir nada.
4. **H2 + H3** — `cargarCasos()` debería, ante una hoja/fila faltante,
   limpiar explícitamente `alertasConsolidadoMes`/la serie correspondiente
   (o al menos emitir un aviso), no dejar el valor de la carga anterior.
5. **P3** — `reconciliar()` podría avisar (no solo silenciarlo) cuando
   detecta más de una fila para el mismo `NUMERO CASO GLPI` con atribuciones
   distintas.

Ninguno de estos bloquea el uso normal descrito en la pregunta original
(recargar el consolidado con disponibilidad/backups corregidos) — son casos
de borde sobre hojas faltantes, re-incrustación repetida, o corridas
fallidas del extractor de indisponibilidades.
