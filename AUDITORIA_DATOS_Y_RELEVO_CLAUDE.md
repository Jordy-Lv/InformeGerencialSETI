# Auditoría de integridad de datos y relevo técnico

**Proyecto:** Informe gerencial — Acción Fiduciaria  
**Fecha de auditoría:** 19 de julio de 2026  
**Estado:** el diseño visual fue aprobado por el usuario. La siguiente intervención debe priorizar la veracidad, trazabilidad y validación de los datos; no rediseñar la portada, las tarjetas ni los modales salvo que sea indispensable para indicar un estado de datos.

---

## ESTADO DE LA CORRECCIÓN — 19 de julio de 2026

Los hallazgos de esta auditoría **fueron corregidos**. Lo que sigue documenta qué se
hizo; el resto del documento se conserva como registro de la auditoría original.

### Decisiones de negocio tomadas por el responsable

| Tema | Decisión aplicada |
|---|---|
| Corte de alertas (§3.2) | **Mes calendario.** Junio = 49. AlertsList manda para el mes en curso; el consolidado solo aporta meses previos. Si alguna vez discrepan, la diferencia se registra en `REPORTE.reconciliaciones` para control interno pero **no se muestra en el informe**: es información de auditoría y el destinatario es el cliente. No bloquea la emisión. |

> **Corrección a la §3.2 de esta auditoría.** El relevo afirmaba que la hoja «Casos»
> del consolidado certifica **61** alertas para junio y que eso contradecía las 49 de
> AlertsList. **Es falso.** La hoja `Casos` tiene una segunda tabla a partir de la
> fila 26 con columnas de fecha reales, y la celda **U27 (jun-26) vale 49**, igual que
> AlertsList. Las dos fuentes coinciden; no existe la discrepancia descrita.
> El 61 son las filas totales de Acción Fiduciaria en AlertsList (49 de junio + 12 de
> julio), no una cifra certificada del consolidado. Verificado leyendo el archivo con
> openpyxl el 20 de julio de 2026.
| Sesión limpia (DATA-001) | Tablero vacío. Cero cifras demo. **Sin banner de aviso**: el usuario lo consideró redundante, porque una tarjeta en «Pendiente de cargar» ya comunica que falta el insumo. |
| GLPI sin filas (DATA-004) | «Sin registros en el periodo», nunca un porcentaje. Avisa pero no bloquea. |
| Bolsa de horas | Tarjeta conservada mostrando «Dato no disponible — sin fuente». |

### Arquitectura implementada

Se creó `window.REPORTE`, store canónico con un estado explícito por dominio
(`no_cargado`, `valido`, `sin_registros_confirmado`, `advertencia`, `invalido`).
Los parsers existentes se conservaron —su lógica era correcta— y ahora publican al
store en vez de escribir a variables léxicas, instancias de Chart.js y DOM a la vez.
Tarjetas, modales, gráficos y PDF leen solo del store.

**Causa raíz de los bugs 49/61 y 4/14:** el bloque `#dashboards-detalle` es un
`<script>` aparte que leía `window.DATA_CASOS` y `window.chartBackups`; ambas son
declaraciones léxicas (`const`/`let`), que no se cuelgan de `window`. Los renderers
caían siempre al dato de ejemplo. Se eliminaron todos los fallbacks.

**Fallo adicional encontrado durante la corrección:** el repintado de los modales
dependía de `requestAnimationFrame`, que el navegador no dispara en una pestaña en
segundo plano. Si el usuario cargaba los Excel con la pestaña de fondo, los modales
conservaban el contenido anterior. Ahora el store notifica de forma directa.

### Estado por hallazgo

| ID | Estado |
|---|---|
| DATA-001 valores semilla | Corregido. HTML sin cifras semilla, banner de plantilla, portada ya no afirma «Cumple» sin datos. |
| DATA-002 casos 49 vs 61 | Corregido. Tarjeta, modal, gráfico y PDF leen `REPORTE.casos`. |
| DATA-003 backups 4 vs 14 | Corregido. Se publican las 14 instancias con sus nombres reales. |
| DATA-004 GLPI SLA 100 % | Corregido. Denominador cero produce `null`, no 1. |
| DATA-005 reconciliación | Corregido **en el modelo, no en la interfaz**. La diferencia 49/61 se detecta y se registra en `REPORTE.reconciliaciones` con ambas cifras y la regla aplicada. No se imprime: el informe va al cliente y una discrepancia entre fuentes internas de SETI no es información suya. Consultable desde consola. Una autoprueba verifica que no se filtre al informe. |
| DATA-006 validación laxa | Corregido. `estadoValidacion()` exige estado resuelto en el store. |
| DATA-007 contaminación | Corregido. El cualitativo es autoritativo; el consolidado no lo pisa. |
| DATA-008 periodo por nombre | Corregido. Se avisa siempre y se registra la base del periodo en la procedencia. |
| DATA-009 estado inferido | Corregido. Se eliminó la inferencia por regex; se usa columna real o «No informado en la fuente». |
| DATA-010 fallbacks favorables | Corregido en C4, C5, C7, C8, C9 y C11. |
| DATA-011 trazabilidad | Corregido **en el modelo, no en la interfaz**. Cada dominio guarda su procedencia completa (archivo, hoja, fila de encabezado, filas leídas/cliente/periodo/excluidas, regla de corte, campo de fecha, fecha de importación) en `REPORTE.d('<dominio>').fuente`. El bloque visual «Fuente y validación» se retiró de los modales por decisión del usuario: lo consideró ruido. La evidencia sigue disponible desde consola y para el auditor que la necesite. |
| DATA-012 datos duplicados | Corregido por el store canónico. |
| DATA-013 re-render frágil | Corregido. Suscripción al store en vez de envolver `actualizarResumen`. |
| DATA-014 fecha GLPI | **Pendiente de definición contractual** (§10.4). Sigue usando fecha de apertura, ahora declarada en la trazabilidad. |
| DATA-015 insumos restaurados | Corregido. Aviso explícito al restaurar desde IndexedDB. |

### Verificación

Suite embebida: `await REPORTE.autopruebas([File,...])` desde la consola. Sin
argumentos comprueba solo el estado en frío. **22/22 pruebas pasan** contra los cuatro
Excel auditados. Cubre los casos de la §7 más portada, gráfico, normalización de
porcentajes y trazabilidad.

Un bug se detectó precisamente al revisar el render del PDF: el modal de
disponibilidad imprimía «1 %» porque el consolidado guarda las disponibilidades como
fracción (1 = 100 %) y ese valor no se normalizaba. Corregido, con una prueba que
ahora caza cualquier porcentaje sospechosamente bajo.

### Pendiente de verificación manual

**La descarga real del PDF no pudo completarse en el entorno de pruebas.** El pipeline
se ejecutó y se verificó página por página hasta la de disponibilidad (portada, línea
base, indicadores, casos y disponibilidad renderizaron con las cifras del store), pero
`html2canvas` avanza al ritmo de los repintados y la pestaña de prueba estaba en
segundo plano. **Debe probarse la descarga completa en una ventana visible.**

### Sigue pendiente (decisiones de negocio)

- Definir la fecha contractual de GLPI (§10.4): apertura, solución, cierre o SLA.
- Conseguir la fuente oficial de bolsa de horas (§10.6).
- Confirmar si mitigaciones/riesgos tendrá columna formal de estado (§10.5). El código
  ya la usa si aparece con encabezado «Estado».

---

## 1. Encargo para quien continúe

El frontend está terminado y fue aprobado. El usuario detectó cifras contradictorias y posibles falsos positivos después de cargar los Excel mensuales. El objetivo es convertir el flujo en un informe confiable, no seguir embelleciendo la interfaz.

Regla principal: **ninguna métrica, chip “Cumple”, interpretación, gráfico o PDF debe afirmar un valor si no existe una fuente válida, correspondiente a Acción Fiduciaria y al período seleccionado.**

Archivo de trabajo:

- `informe-accion-fiduciaria.html` — HTML autocontenido y offline; contiene SheetJS, Chart.js, html2canvas y jsPDF embebidos.

Insumos auditados, conservados en la carpeta del proyecto:

- `Disponibilidad Consolidado Mayo.xlsx`
- `AlertsList.xlsx`
- `glpi (20).xlsx`
- `Logros_Clientes_Junio_2026_1 (1).xlsx`

## 2. Resultado ejecutivo

La carga de los cuatro archivos completa el checklist y habilita el PDF, pero el informe **no es todavía confiable como documento de datos**. Hay tres causas principales:

1. La plantilla presenta valores de junio como si fueran datos cargados aun con una sesión limpia.
2. Los detalles tipo modal usan varios fallbacks estáticos, por lo que pueden contradecir la tarjeta principal y el Excel.
3. La validación actual confirma que un archivo fue leído, no que tenga datos suficientes, coherentes, del cliente y del período.

El caso reproducido más importante es el de atenciones: con los mismos cuatro archivos, la tarjeta muestra **49 casos** y el modal muestra **61**. El valor 49 se deriva de AlertsList filtrado a junio; 61 procede de una serie de ejemplo/fallback del consolidado inicial, no del resultado de la carga.

## 3. Evidencia contrastada de las fuentes

### 3.1 Valores encontrados en los Excel

| Dominio | Fuente y hoja | Hecho verificable | Resultado que debería conservarse como dato fuente |
|---|---|---|---|
| Alertas | `AlertsList.xlsx` / `AlertsList (2)` | Hay 61 alertas de Acción Fiduciaria: 49 fechadas en junio de 2026 y 12 entre el 1 y el 7 de julio. | **49** si el informe de junio es calendario; **61** solo si el negocio define un corte junio–7 de julio. |
| Casos históricos | `Disponibilidad Consolidado Mayo.xlsx` / `Casos` | La fila histórica para junio dice Alertas 61, Requerimientos 0, Incidentes 0. | Dato conflictivo que requiere reconciliación; no debe mezclarse silenciosamente con el detalle de AlertsList. |
| GLPI | `glpi (20).xlsx` / `glpi (20)` | Ocho filas de Acción Fiduciaria, todas con fecha de apertura en mayo de 2026; ninguna de junio. | Junio: **sin registros**, no “SLA 100%”. |
| Disponibilidad por CI | `Disponibilidad Consolidado Mayo.xlsx` / `Disponibilidad` | Hay 14 CI de Acción Fiduciaria; cada uno está en 100% para jun-26; meta 99,30%. | 14/14 CI y promedio 100%. |
| Backups | `Disponibilidad Consolidado Mayo.xlsx` / `Backups` | Hay 14 instancias y todas están en 100% para junio. | 14/14 y 100%, con los nombres reales de las 14 instancias. |
| Indicadores | `Disponibilidad Consolidado Mayo.xlsx` / `Inidcadores` | Disponibilidad, tiempos de solución y entregables: 100% para junio. | 3 métricas; sus metas se deben conservar por fila. |
| Logros | `Logros_Clientes_Junio_2026_1 (1).xlsx` / `Logros Junio 2026` | Una fila de Acción Fiduciaria bajo “LOGROS DEL MES”. | 1 logro: verificación de estabilidad de cuentas privilegiadas. |
| Mitigaciones y riesgos | mismo archivo, misma hoja | Cinco filas de Acción Fiduciaria bajo “MITIGACIONES Y RIESGOS GESTIONADOS”. Dos describen riesgos abiertos o pendientes. | 5 registros, conservando texto/evidencia y condición explícita de cada uno. |

### 3.2 Decisión funcional pendiente: 49 o 61 alertas

No se debe “corregir” a 61 sin una decisión de negocio. Los dos números tienen una fuente:

- **49**: fechas de apertura estrictamente entre el 1 y el 30 de junio; es lo que hoy aplica el código al filtrar `Created Date`.
- **61**: total de filas de Acción Fiduciaria en el archivo y también valor de la serie histórica del consolidado; incluye 12 alertas de julio.

Se debe confirmar con el responsable del reporte cuál es la regla oficial:

1. mes calendario;
2. ventana operativa de cierre (definir fecha inicial y final); o
3. cifra certificada del consolidado, con una regla de reconciliación frente al detalle crudo.

Hasta decidirlo, el sistema debe marcar la discrepancia como bloqueante para la emisión, no elegir un número por conveniencia.

## 4. Pruebas realizadas

### Prueba A — sesión limpia, sin insumos

Al abrir el HTML sin cargar archivos, el tablero expone como hechos: 61 casos, 99,8% de disponibilidad, seis logros, catorce sistemas y 100% de backups. El botón PDF permanece deshabilitado, pero las tarjetas y sus detalles pueden comunicar esas cifras como reales.

**Resultado:** falso positivo confirmado. Debe existir un estado “Sin datos cargados” o “Plantilla / ejemplo”, no cifras operativas sin fuente.

### Prueba B — carga de los cuatro insumos de junio de 2026

Se cargaron el consolidado, GLPI, AlertsList y el archivo cualitativo. El centro de carga muestra 3/3 insumos obligatorios y habilita el PDF. El resumen de estado reporta:

- Consolidado: tres indicadores, disponibilidad 100%, backups 100%.
- AlertsList: 49 alertas del período; seis de prioridad alta; 12 fuera de junio excluidas.
- GLPI: cero casos de junio y ocho registros de Acción Fiduciaria en otros meses; sin embargo informa SLA 100%.
- Logros: uno.
- Mitigaciones: cinco.

### Prueba C — inconsistencia tarjeta/modal de casos

Después de la carga, la tarjeta “Casos atendidos” muestra 49 (49 alertas, 0 requerimientos, 0 incidentes). Al abrir su modal, el modal muestra 61, con evolución 58/36/61 y desglose de 61 alertas.

Se comprobó en tiempo de ejecución que:

- el estado real `DATA_CASOS` contiene `[54, 30, 49]` para alertas;
- `window.DATA_CASOS` no existe;
- el renderer del modal lee `window.DATA_CASOS || fallback`, por lo que toma la serie estática `[54, 30, 61]`.

**Resultado:** bug crítico confirmado y reproducible.

### Prueba D — detalle de backups

Tras cargar el consolidado, el modal de backups presenta “4/4 instancias verificadas” y cuatro nodos fijos: SQL, Mysql, Oracle y AWS. La hoja `Backups` del consolidado contiene catorce instancias de Acción Fiduciaria. El renderer usa `window.chartBackups`, que tampoco existe como propiedad global, y vuelve a la lista fija de cuatro nodos.

**Resultado:** bug crítico confirmado y reproducible. La cifra agregada 100% coincide por casualidad; el detalle y la cobertura son falsos.

## 5. Hallazgos priorizados

### P0 — bloquear emisión o marcar explícitamente “sin dato”

#### DATA-001 — Valores semilla presentados como información real

- **Evidencia:** una sesión limpia muestra 61 casos, 99,8%, seis logros, cuatro backups/100% y catorce sistemas, sin insumos.
- **Riesgo:** un usuario puede abrir, capturar o interpretar un modal sin haber cargado el mes y obtener un informe aparente.
- **Corrección esperada:** introducir estados por dominio: `no_cargado`, `valido`, `sin_registros_confirmado`, `advertencia`, `invalido`. Antes de `valido`, no mostrar KPI, gráfico, “Cumple” ni interpretación; usar “Pendiente de cargar” o “Dato no disponible”.

#### DATA-002 — Casos: tarjeta y modal no provienen del mismo estado

- **Evidencia:** tarjeta 49 frente a modal 61 con los mismos archivos (Prueba C).
- **Causa técnica:** `renderC5()` consulta `window.DATA_CASOS`, pero `DATA_CASOS` se declara como constante léxica, no como `window.DATA_CASOS`; por ello toma el fallback.
- **Corrección esperada:** un único store normalizado; todos los renderizadores deben recibir el mismo objeto de datos. Eliminar fallbacks numéricos para datos operativos.
- **Prueba de aceptación:** cargar el set auditado; tarjeta, modal, gráfico y PDF de casos deben mostrar la misma cifra y la misma serie. Cambiar el período o el archivo debe volver a comprobarlo.

#### DATA-003 — Backups: detalle de cuatro nodos ficticios frente a catorce reales

- **Evidencia:** modal 4/4 con SQL/Mysql/Oracle/AWS; Excel 14 instancias (Prueba D).
- **Causa técnica:** `renderC7()` busca `window.chartBackups`; la instancia real no está en ese namespace y se activa el fallback fijo.
- **Corrección esperada:** renderizar los 14 nombres y valores desde el store normalizado de backups; si no hay registros, no inventar cuatro nodos ni 100%.
- **Prueba de aceptación:** el conteo, cada nombre, el porcentaje promedio y el PDF deben coincidir con la hoja `Backups`.

#### DATA-004 — GLPI sin filas de junio se comunica como SLA 100%

- **Evidencia:** el archivo contiene ocho filas de Acción Fiduciaria en mayo y cero en junio. El sistema calcula `cliente.length ? ... : 1`, por lo que guarda cumplimiento 1 y en el centro de carga indica `SLA 100,00%`.
- **Riesgo:** ausencia de muestra convertida en cumplimiento perfecto.
- **Corrección esperada:** en denominador cero, emitir `Sin datos`, `No aplicable confirmado` o bloquear hasta una confirmación explícita; nunca 100%. El chip general no puede depender de ese valor.
- **Prueba de aceptación:** un GLPI sin registros de la entidad/período no habilita el PDF sin una decisión de ausencia confirmada y debe conservar su trazabilidad.

#### DATA-005 — Reconciliación de alertas sin regla de corte

- **Evidencia:** Consolidado/Casos dice 61 en junio; detalle de AlertsList tiene 49 en junio + 12 en julio.
- **Riesgo:** informes diferentes para el mismo mes según el componente que se consulte.
- **Corrección esperada:** exigir una política declarada de período y fuente maestra. Al detectar diferencia entre el consolidado y AlertsList, mostrar ambas cifras, la regla aplicada y bloquear la emisión hasta aceptar la excepción.

### P1 — corregir antes de uso mensual recurrente

#### DATA-006 — Validación acepta un archivo aunque sus datos no son suficientes

`estadoValidacion()` considera suficiente que existan objetos `CARGA.glpi` y `CARGA.alertas`; no requiere filas de la entidad/período ni que el resultado tenga una semántica aprobada. Así, el PDF se habilita con GLPI vacío y SLA ficticio.

**Acción:** validar esquema, cliente, período, cobertura mínima y consistencia interfuentes, no solo que la lectura no haya fallado.

#### DATA-007 — El consolidado puede contaminar logros y mitigaciones del archivo mensual

`cargarConsolidado()` reinicia logros y mitigaciones e importa las hojas genéricas `Logros` y `Mitigación`. El consolidado auditado trae tres mitigaciones históricas, sin una prueba robusta de que sean las de Acción Fiduciaria/junio. Si el usuario vuelve a seleccionar el consolidado después del archivo cualitativo, puede sobrescribir los cinco registros correctos.

**Acción:** definir prioridad de fuente por dominio. El archivo mensual cualitativo debe ser autoritativo cuando está presente; el consolidado no debe resetearlo. Guardar origen, fecha de carga y hash por dominio.

#### DATA-008 — Período del archivo cualitativo se valida por el nombre

El archivo se acepta como junio 2026 porque su nombre contiene “Junio” y “2026”; el contenido no tiene una columna explícita de período por registro.

**Acción:** requerir período dentro del archivo, metadato confirmado por el usuario o un aviso bloqueante con confirmación explícita. Un nombre de archivo no es evidencia suficiente.

#### DATA-009 — Estado de mitigación inferido mediante palabras clave

El código clasifica textos como “Gestionado” o “En seguimiento” mediante expresiones regulares de la descripción/evidencia. En los cinco registros auditados hay riesgos abiertos, pendientes y acciones preventivas; una inferencia puede cambiar el significado sin dato estructurado.

**Acción:** no producir una clasificación ejecutiva no presente en la fuente. Mostrar el texto original o incorporar una columna de estado validada por el responsable.

#### DATA-010 — “Cumple” y narrativas se calculan con datos ausentes o fallbacks

Ejemplos auditados:

- `renderC4()` reemplaza valor/meta faltantes por 100%.
- `renderC7()` reemplaza ausencia por cuatro nodos a 100%.
- `renderC8()` reemplaza cero logros por seis en el dato destacado.
- `renderC11()` reemplaza cero filas por catorce sistemas.
- el control de bolsa muestra 0 consumidas / 100 disponibles sin insumo de bolsa.

**Acción:** sustituir `||` numéricos/arrays de ejemplo en dominios operativos por estados nulos explícitos. La UI puede conservar su diseño, pero deberá mostrar “Sin dato” y no una cifra favorable.

#### DATA-011 — No existe trazabilidad visible por cifra

El usuario no puede identificar desde qué archivo, hoja, fila, fecha de corte y regla sale un KPI. La tarjeta de mitigaciones fue intencionalmente simplificada; esa simplificación debe coexistir con un detalle de auditoría, no eliminar la evidencia.

**Acción:** para cada dominio guardar y exponer, al menos en un detalle de “Fuente y validación”: archivo, hoja, rango/filas, período aplicado, filtro de cliente, fecha de importación, conteo total/excluido y advertencias. Mantener la tarjeta resumida como el usuario pidió.

### P2 — deuda técnica y calidad del flujo

#### DATA-012 — Los datos viven en DOM, variables y gráficos a la vez

El resumen de la tarjeta se actualiza desde `DATA_CASOS`; los modales consultan DOM, globals o fallbacks; los gráficos mantienen su propia copia. Esto permite divergencias como 49/61 y 14/4.

**Acción:** crear un modelo canónico inmutable por importación y hacer que resumen, modal, gráfico, narrativa y PDF se rendericen exclusivamente desde él.

#### DATA-013 — Las actualizaciones internas no re-renderizan de forma fiable los detalles

El intento de envolver `window.actualizarResumen` no alcanza las llamadas léxicas a `actualizarResumen()` dentro del script original. Aunque se corrigiera el namespace, el redibujado debe ser un evento explícito del store, no un efecto lateral.

#### DATA-014 — Fecha usada para GLPI puede no ser la definición contractual

Se filtra por “Fecha de apertura”. Para SLA mensual podría requerirse fecha de resolución, cierre o ventana de corte. También se clasifica requerimiento/incidente con regex sobre Categoría/Tipo.

**Acción:** confirmar definición contractual y mapear categorías permitidas; documentar filas no clasificadas y no descartarlas silenciosamente.

#### DATA-015 — Restauración local puede mantener insumos de un corte anterior

Los archivos se persisten en IndexedDB en el navegador. Aunque es útil, la interfaz debe señalar claramente fecha de importación, período y que se restauraron insumos locales. De lo contrario, un usuario puede emitir con archivos anteriores creyendo que acaba de cargar información nueva.

## 6. Arquitectura recomendada para la corrección

No aplicar arreglos puntuales por tarjeta. Implementar estas capas:

1. **Importadores puros por fuente.** Cada uno devuelve filas normalizadas y metadatos, sin tocar el DOM.
2. **Store canónico del informe.** Ejemplo conceptual: `report = { periodo, cliente, fuentes, indicadores, disponibilidad, backups, casos, logros, mitigaciones, validacion }`. Las cifras no se guardan duplicadas en Chart.js o nodos HTML.
3. **Motor de validación y reconciliación.** Debe generar errores bloqueantes, avisos y decisiones pendientes. Debe distinguir “cero registros reales”, “sin fuente”, “fuente inválida” y “ausencia confirmada”.
4. **Render único.** Tarjetas, modales, texto interpretativo y PDF consumen el mismo `report`. Ningún componente puede usar arreglos de ejemplo cuando existe un reporte activo.
5. **Provenance por métrica.** El modelo debe conservar origen por dato: archivo, hoja, campos, filtro, período y registros excluidos.
6. **Exportación protegida.** El PDF solo se habilita si no hay contradicciones críticas, la cobertura está validada y las excepciones cuentan con confirmación visible.

## 7. Matriz mínima de pruebas automatizadas

Crear fixtures a partir de los cuatro archivos auditados y ejecutar, como mínimo:

| Caso | Aserción |
|---|---|
| Sesión sin insumos | No hay cifras operativas ni “Cumple”; PDF bloqueado. |
| Set auditado, junio calendario | Alertas 49 en tarjeta, modal, gráfico, texto y PDF; ninguna vista muestra 61. |
| Set auditado, ventana junio–julio aprobada | Alertas 61 de manera consistente y se muestra el rango de corte. |
| Backups auditados | 14/14, catorce nombres reales y 100%; ningún nodo fijo de plantilla. |
| GLPI auditado | Estado “Sin registros de junio”, nunca SLA 100%; PDF bloqueado o ausencia confirmada. |
| Archivo cualitativo auditado | 1 logro y 5 mitigaciones de Acción Fiduciaria; no se incluyen HOMI, Novaventa, EMI ni La Riviera. |
| Orden de carga inverso | Cargar cualitativo y luego consolidado no reemplaza los datos cualitativos correctos. |
| Archivo de otro período | Se rechaza o requiere confirmación explícita y se marca en el reporte. |
| Conflicto Consolidado vs AlertsList | La discrepancia se muestra y bloquea hasta seleccionar una regla de fuente/corte. |
| PDF | Las métricas de cada página son idénticas al store canónico y a la tarjeta correspondiente. |

## 8. Contexto de UX que se debe preservar

- El usuario aprobó la portada con collage y pidió conservarla siempre.
- Aprobó la estructura de tarjetas y los modales; no desea volver a tarjetas expandibles de estilo Excel.
- Pidió lenguaje serio y evitar frases promocionales/genéricas.
- La tarjeta debe decir exactamente **“Mitigaciones y riesgos gestionados”**.
- La marca debe decir **SETI**, no CETI.
- El usuario pidió que las tarjetas cualitativas sean concisas: total y contenido real, sin etiquetas genéricas como “responsable no informado”. La evidencia puede vivir en el modal/auditoría.
- El HTML debe seguir trabajando offline.

## 9. Historial técnico relevante

Durante esta sesión se hicieron ajustes visuales y de flujo, entre ellos:

- portadas, tarjetas y modales rediseñados;
- importación de logros/mitigaciones desde el archivo mensual y filtrado por Acción Fiduciaria;
- corrección del nombre SETI;
- corrección previa de un fallo de PDF por acceso a `window.MESES` (se cambió a `MESES` en el scope correcto);
- prueba interna del pipeline de PDF con `save` simulado. La descarga final real debe volver a probarse después del refactor de datos.

Esos cambios no sustituyen las correcciones de datos descritas arriba.

## 10. Definiciones que debe confirmar el negocio antes de cerrar

1. ¿El informe mensual de junio se mide por junio calendario o por una ventana de corte que incluye julio? Indicar fechas exactas.
2. Cuando Consolidado y AlertsList difieren, ¿cuál es la fuente de verdad y quién aprueba una excepción?
3. ¿Cómo se debe reportar un mes con cero filas GLPI: sin actividad, sin datos, no aplicable o pendiente de certificación?
4. ¿Qué fecha define el período de GLPI: apertura, solución, cierre o SLA?
5. ¿Se requiere una columna formal de estado para mitigaciones/riesgos, en vez de inferirla del texto?
6. ¿Cuál es la fuente oficial de bolsa de horas? Hasta tenerla, no comunicar “0 h consumidas” como hecho.

## 11. Criterio de cierre para Claude

No declarar el flujo listo solo porque el PDF se genera. Se considerará listo cuando:

- una misma métrica coincida en tarjeta, modal, gráfico, narrativa y PDF;
- ninguna cifra favorable nazca de un fallback, plantilla o denominador cero;
- toda cifra sea rastreable a una fuente y período;
- los conflictos entre fuentes sean explícitos y requieran resolución;
- los tests de la sección 7 pasen;
- el diseño aprobado permanezca visualmente intacto salvo los estados de validación necesarios.
