# Informe QA: Informe Acción Fiduciaria

| Campo | Valor |
|---|---|
| **Fecha** | 2026-07-20 |
| **URL probada** | http://127.0.0.1:4173/informe-accion-fiduciaria.html |
| **Sesiones** | informe-qa, informe-whitebox, informe-pdf, project-legacy, qa-fixes y legacy-fixed |
| **Alcance** | Flujo completo, carga, edición, visualización, exportación, responsive, accesibilidad y análisis de implementación |

## Estado tras la remediación

| Estado | Cantidad |
|---|---:|
| Resueltos | 9 |
| Regresiones visuales detectadas y resueltas | 1 |
| Abiertos | 0 |

| Hallazgo | Estado | Corrección y comprobación |
|---|---|---|
| ISSUE-001 | Resuelto | “Revisar informe” mantiene abierto el centro de carga, enfoca una alerta y enumera lo pendiente; solo cierra cuando los siete criterios están resueltos. |
| ISSUE-002 | Resuelto | Las tarjetas declaran `aria-haspopup="dialog"` y `aria-controls="dashboardModal"`; ya no exponen un `aria-expanded` contradictorio. |
| ISSUE-003 | Resuelto | Ambos diálogos mueven/capturan el foco, vuelven inerte el fondo, cierran con Escape y restauran el foco al invocador. |
| ISSUE-004 | Resuelto | La interfaz usa “Indicadores” y el cargador admite tanto el nombre correcto como el histórico “Inidcadores”. |
| ISSUE-005 | Resuelto | La rejilla móvil pasa a una columna y permite saltos de línea; la vigencia y los títulos completos se leen a 390 × 844 px. [Evidencia](resolved/mobile-390-fixed.png). |
| ISSUE-006 | Resuelto | Se valida extensión y archivo no vacío antes de leerlo; un `.txt` no cuenta como procesado ni se guarda en IndexedDB. |
| ISSUE-007 | Resuelto | Las tablas cualitativas genéricas requieren cliente y periodo verificables y filtran ambos simultáneamente; un registro mensual exige que el nombre identifique el corte. |
| ISSUE-008 | Resuelto | `index (1).html` muestra una alternativa accesible y redirige al informe vigente sin solicitar dependencias ausentes. |
| ISSUE-009 | Resuelto | El PDF conserva la captura visual e incorpora una capa lógica de texto, idioma y metadatos. `pdftotext` recupera el contenido de las 10 páginas. No se declara conformidad PDF/UA ni etiquetado estructural. |

La regresión final con los cuatro archivos reales pasa **22/22 autopruebas**. El PDF corregido está en [output/pdf/Informe Accion Fiduciaria Junio 2026.pdf](../output/pdf/Informe%20Accion%20Fiduciaria%20Junio%202026.pdf): 10 páginas, 2,8 MB, formato 16:9, sin recortes ni solapamientos y con texto buscable/extraíble.

### Corrección posterior: gráfico deformado en el PDF

Se reprodujo que, al exportar desde una ventana menor de 760 px, los media queries móviles apilaban el panel de disponibilidad dentro del lienzo PDF. Además, Chart.js conservaba un bitmap de 470 px y el navegador lo estiraba hasta 638 px, deformando y desenfocando ejes, meses y leyenda.

La exportación ahora fija la composición ejecutiva de escritorio independientemente del viewport y vuelve a dibujar el gráfico en 638 × 236 px con buffer 2× (1276 × 472). Las exportaciones realizadas desde ventanas de 700 px y 1440 px producen una página 5 idéntica píxel por píxel. También se comprobó que las 22 autopruebas siguen pasando después de exportar.

![Disponibilidad global corregida en el PDF](resolved/disponibilidad-pdf-corregida.png)

## Resumen inicial de hallazgos

| Severidad | Cantidad |
|---|---:|
| Crítica | 0 |
| Alta | 1 |
| Media | 6 |
| Baja | 2 |
| **Total** | **9** |

## Dictamen inicial, antes de las correcciones

El flujo principal funciona con los cuatro archivos reales del proyecto y genera un informe coherente de junio de 2026. Las 19 autopruebas de integridad que pueden ejecutarse con los insumos cargados pasan, la restauración desde IndexedDB funciona y el PDF final se genera con 10 páginas visualmente correctas.

En ese momento, el producto no debía considerarse libre de defectos ni listo para un uso desatendido. Los nueve hallazgos descritos a continuación quedan conservados como registro histórico; su estado vigente es “Resuelto”, según la matriz de remediación anterior.

## Qué hace el proyecto y por qué existe

Es un informe gerencial interactivo que reemplaza la lectura lineal de una presentación de PowerPoint. Su objetivo es mostrar primero un resumen ejecutivo y permitir abrir el detalle que explica de dónde sale cada cifra. La transcripción de la reunión confirma ese propósito: conservar el contenido del informe anterior, pero hacerlo más resumido, intuitivo, trazable e interactivo, con opción de editar y exportar a PDF.

El archivo operativo actual es `informe-accion-fiduciaria.html`. Es una aplicación autocontenida de aproximadamente 4,1 MB: incluye estilos, lógica y bibliotecas de gráficos, lectura de Excel y generación de PDF dentro del mismo HTML. No usa servidor de negocio ni envía los archivos a internet; durante la prueba solo solicitó el propio HTML y el favicon local.

## Flujo funcional entendido

1. Al abrir, selecciona por defecto el mes calendario anterior y muestra la línea base contractual.
2. El usuario carga consolidado, GLPI, AlertsList y contenido cualitativo; también puede confirmar explícitamente que no hubo logros o mitigaciones.
3. Los analizadores normalizan fechas y porcentajes, filtran el período y, cuando la fuente lo permite, el cliente Acción Fiduciaria.
4. Un almacén central (`REPORTE`) publica los dominios casos, alertas, GLPI, disponibilidad, backups, indicadores, CI, logros, mitigaciones y bolsa de horas.
5. Las tarjetas resumen esos dominios; al activarlas se abre un detalle con la evidencia y las series históricas.
6. Los archivos se guardan localmente en IndexedDB para restaurarlos tras recargar. Las posiciones editadas se guardan en `localStorage`.
7. La exportación crea una portada y nueve paneles de detalle, rasteriza cada página, añade su capa lógica de texto y las ensambla en un PDF 16:9.

## Fuentes reales y resultado de junio de 2026

| Fuente | Uso observado | Resultado |
|---|---|---|
| `Disponibilidad Consolidado Mayo.xlsx` | Indicadores, disponibilidad global/por CI, backups e histórico de casos | 100% de disponibilidad; 14/14 CI cumplen; backups 100% |
| `glpi (20).xlsx` | Requerimientos, incidentes y SLA del cliente/período | 0 filas de Acción Fiduciaria en junio; no inventa SLA |
| `AlertsList.xlsx` | Alertas de junio y clasificación de prioridad | 49 alertas de junio; coincide con el consolidado |
| `Logros_Clientes_Junio_2026_1 (1).xlsx` | Logros, mitigaciones y riesgos del cliente | 1 logro y 5 mitigaciones de Acción Fiduciaria |

## Pruebas ejecutadas

| Área | Cobertura | Resultado |
|---|---|---|
| Carga válida | Cuatro archivos reales y revalidación completa | Pasa |
| Integridad | 22 autopruebas contra tarjeta, store, modal y Excel | 22/22 pasan |
| Período | Junio→julio, exclusión de filas fuera del mes y GLPI sin registros | Pasa también para tablas cualitativas genéricas |
| Persistencia | Recarga del navegador y “Restaurar últimos informes” | Pasa |
| Casos negativos | Cero archivos, `.txt` como consolidado, fuentes sin columnas opcionales | Pasa: informa, bloquea y no persiste entradas inválidas |
| Interacción | Edición, teclado, apertura/cierre de tarjetas y diálogos | Pasa visual y semánticamente; foco contenido y restaurado |
| Responsive | Escritorio y móvil 390 × 844 px | Pasa, sin overflow ni recorte de datos críticos |
| Exportación | PDF real con los cuatro insumos, 10 páginas, 2,8 MB | Genera y conserva las cifras; diseño visual aprobado |
| PDF visual | Renderizado de las 10 páginas y revisión de tablas, gráficos y textos | Sin páginas vacías, cortes ni solapamientos |
| PDF accesible | Idioma, metadatos y extracción de texto | Pasa el objetivo del hallazgo mediante capa lógica de texto; no es PDF/UA etiquetado |
| Red/privacidad | Recursos solicitados por el navegador | Sin llamadas externas; procesamiento local |
| Prototipo antiguo | Apertura de `index (1).html` y verificación de dependencias | Pasa: redirige al informe vigente y no produce errores |

Medición local orientativa: el HTML transfirió 4.143.102 bytes y disparó `DOMContentLoaded` a 134 ms y `load` a 152 ms en el servidor local. No se presenta como una prueba de rendimiento de producción.

## Inventario y estado de las variantes

- `informe-accion-fiduciaria.html`: versión activa y única que completa todo el flujo.
- `informe-accion-fiduciaria.BACKUP-pre-store.html`, `informe-accion-fiduciaria-propuesta.html` e `index 3.html`: copias históricas completas, no módulos requeridos por la versión activa.
- `index (1).html`: entrada histórica de compatibilidad que redirige al informe activo y conserva un enlace manual como alternativa.
- `AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md`: relevo/auditoría previa; varias conclusiones siguen vigentes, pero la prueba negativa encontró una brecha no cubierta por sus autopruebas cualitativas.
- Los cuatro `.xlsx`: insumos mensuales reales.
- `Llamada con Santiago Amaya Cely.docx`: transcripción que define el objetivo funcional del rediseño.
- `~$Disponibilidad Consolidado Mayo.xlsx`: archivo temporal de bloqueo de Excel; no participa en la aplicación y conviene retirarlo del paquete de entrega cuando Excel esté cerrado.

## Causas técnicas iniciales

| Hallazgo | Causa confirmada en el HTML activo |
|---|---|
| ISSUE-001 | El botón “Revisar informe” ejecuta directamente `cerrarCarga()`; no consulta `estadoValidacion()` ni el resumen de faltantes. |
| ISSUE-007 | El fallback de `extraerMitigaciones()` convierte todas las filas reconocibles y `registrarContenido()` admite contenido sin cliente/período verificable como advertencia. |
| ISSUE-006 | El atributo `accept` del selector no se complementa con una validación real de extensión/MIME; después de analizar, `ejecutarRevalidacion()` guarda el archivo aunque el dominio quede inválido. El contador solo comprueba que exista un objeto cargado. |
| ISSUE-003 | `abrirCarga()` y `cerrarCarga()` solo cambian una clase CSS: no mueven/restauran el foco, no aplican `inert` al fondo y no implementan un ciclo de tabulación. El modal de detalle comparte la misma debilidad. |
| ISSUE-002 | `activarModales()` reemplaza el comportamiento expansible por `openDashboard()`, pero restablece `aria-expanded` a `false` y no actualiza la relación accesible cuando abre el diálogo. |
| ISSUE-005 | Las tarjetas móviles conservan una rejilla mínima de dos columnas y valores con `white-space: nowrap`, lo que prioriza la altura fija sobre el texto completo. |
| ISSUE-009 | `exportarPDF()` captura cada panel con `html2canvas` y lo agrega a jsPDF como PNG; no inserta texto ni estructura etiquetada. |

## Hallazgos

### ISSUE-001: “Revisar informe” acepta 0 de 3 insumos obligatorios sin advertencia

| Campo | Valor |
|---|---|
| **Severidad** | Media |
| **Categoría** | Funcional / UX |
| **URL** | http://127.0.0.1:4173/informe-accion-fiduciaria.html |
| **Video de reproducción** | [videos/issue-001-repro.webm](videos/issue-001-repro.webm) |

**Descripción**

El centro de carga llama “obligatorios” al consolidado, GLPI y AlertsList, y muestra “0/3 insumos obligatorios procesados”. Aun así, el botón “Revisar informe” cierra el diálogo sin validar, explicar qué falta ni mostrar un estado de error. El informe queda con todos los datos operativos en “Sin datos” y el PDF continúa deshabilitado. Se esperaba impedir el avance o, si el avance parcial es deliberado, comunicar claramente qué puede revisarse y por qué la exportación sigue bloqueada.

**Pasos de reproducción**

1. Abrir “Cargar informes” sin seleccionar archivos.
   ![Paso 1](screenshots/issue-001-step-1.png)
2. Pulsar “Revisar informe”.
3. **Resultado:** el diálogo se cierra sin advertencia y se muestra el informe vacío.
   ![Resultado](screenshots/issue-001-result.png)

---

### ISSUE-007: Mitigaciones de otro cliente y otro período contaminan el informe

| Campo | Valor |
|---|---|
| **Severidad** | Alta |
| **Categoría** | Funcional / Integridad de datos |
| **URL** | http://127.0.0.1:4173/informe-accion-fiduciaria.html |
| **Video de reproducción** | [videos/issue-007-repro-v2.webm](videos/issue-007-repro-v2.webm) |

**Descripción**

El fixture contiene dos filas en “Mitigación”: una de Acción Fiduciaria para junio de 2026 y otra de “Otra Entidad”. El sistema importa las dos como si fueran de Acción Fiduciaria. Además, al cambiar el período a julio, mantiene ambas mitigaciones mientras descarta correctamente los indicadores de junio. Esto puede publicar información de otro cliente y de otro mes en un informe gerencial. Se esperaba filtrar por cliente y período o bloquear la importación cuando no pueda verificarlos.

**Pasos de reproducción**

1. Abrir el centro de carga en junio de 2026.
   ![Paso 1](screenshots/issue-007-v2-step-1.png)
2. Cargar el consolidado de QA. El sistema muestra “2 registros” de mitigación aunque solo una fila pertenece al cliente.
   ![Paso 2](screenshots/issue-007-v2-step-2.png)
3. Cambiar el período a julio de 2026.
4. **Resultado:** los indicadores de junio se limpian, pero las dos mitigaciones continúan en el informe de julio.
   ![Resultado](screenshots/issue-007-v2-result.png)

**Contenido del fixture**

![Una fila de Acción Fiduciaria y otra de Otra Entidad](screenshots/issue-007-fixture.png)

---

### ISSUE-006: Un archivo de texto inválido cuenta como consolidado “procesado” y se guarda

| Campo | Valor |
|---|---|
| **Severidad** | Media |
| **Categoría** | Funcional / Validación |
| **URL** | http://127.0.0.1:4173/informe-accion-fiduciaria.html |
| **Video de reproducción** | [videos/issue-006-repro-v2.webm](videos/issue-006-repro-v2.webm) |

**Descripción**

El campo de consolidado acepta un archivo `.txt` que no es una hoja de cálculo. Aunque el sistema detecta que faltan todas las métricas y muestra errores que impiden exportar, incrementa el contador a “1/3 insumos obligatorios procesados” y persiste “Consolidado · Junio 2026” en los informes guardados. Se esperaba rechazar el tipo/formato antes de marcarlo como procesado y no persistir un insumo inválido.

**Pasos de reproducción**

1. Abrir el centro de carga sin archivos seleccionados.
   ![Paso 1](screenshots/issue-006-step-1-v2.png)
2. Seleccionar `archivo-invalido.txt` como “Consolidado de disponibilidad”.
3. **Resultado:** aparece “1/3 insumos obligatorios procesados” y el consolidado queda guardado a pesar de los errores de estructura y contenido.
   ![Resultado](screenshots/issue-006-result-v2.png)

---

### ISSUE-005: Datos clave quedan recortados en móvil

| Campo | Valor |
|---|---|
| **Severidad** | Media |
| **Categoría** | Visual / Responsive |
| **URL** | http://127.0.0.1:4173/informe-accion-fiduciaria.html |
| **Video de reproducción** | N/A |

**Descripción**

En un viewport móvil de 390 × 844 px no existe desplazamiento horizontal global, pero el contenido se recorta dentro de las tarjetas. La fecha de vigencia contractual aparece como “Hasta 31/08/20…” y el título “MITIGACIONES Y RIESGOS GESTIONADOS” invade la zona del control de expansión y queda truncado. Se esperaba que los datos críticos se ajustaran a varias líneas o que la tarjeta reorganizara sus columnas sin perder información.

**Evidencia**

![Informe a 390 px con fecha y títulos recortados](screenshots/mobile-390.png)

---

### ISSUE-004: Nombre de hoja “Inidcadores” mal escrito

| Campo | Valor |
|---|---|
| **Severidad** | Baja |
| **Categoría** | Contenido / UX |
| **URL** | http://127.0.0.1:4173/informe-accion-fiduciaria.html |
| **Video de reproducción** | N/A |

**Descripción**

La ayuda del primer archivo indica que el consolidado requiere las hojas “Inidcadores, Disponibilidad y Backups”. “Inidcadores” debería ser “Indicadores”. En un flujo basado en nombres exactos de hojas, el error puede inducir al usuario a renombrar incorrectamente su archivo o a interpretar mal un rechazo.

**Evidencia**

![Texto mal escrito en el centro de carga](screenshots/load-modal.png)

---

### ISSUE-003: El diálogo no captura el foco y permite operar el informe detrás

| Campo | Valor |
|---|---|
| **Severidad** | Media |
| **Categoría** | Accesibilidad / Funcional |
| **URL** | http://127.0.0.1:4173/informe-accion-fiduciaria.html |
| **Video de reproducción** | [videos/issue-003-repro.webm](videos/issue-003-repro.webm) |

**Descripción**

Al abrir “Centro de carga mensual”, el foco permanece en el botón “Cargar informes”. La primera pulsación de Tab lleva a “Editar datos”, que está visualmente detrás del diálogo. Al pulsar Enter, el informe entra en modo de edición mientras el diálogo continúa abierto. El fondo tampoco queda fuera del árbol de accesibilidad y la tabulación recorre todas las tarjetas. Se esperaba mover el foco al diálogo, limitarlo a sus controles, marcar el resto como inerte y devolver el foco al botón invocador al cerrar.

**Pasos de reproducción**

1. Abrir “Cargar informes”.
   ![Paso 1](screenshots/issue-003-step-1.png)
2. Pulsar Tab una vez; el foco se desplaza a “Editar datos” detrás del diálogo.
   ![Paso 2](screenshots/issue-003-step-2.png)
3. Pulsar Enter.
4. **Resultado:** el botón de fondo cambia a “Listo” y el contenido entra en edición sin cerrar el diálogo.
   ![Resultado](screenshots/issue-003-result.png)

---

### ISSUE-002: La tarjeta abre un diálogo, pero conserva semántica de “colapsada”

| Campo | Valor |
|---|---|
| **Severidad** | Media |
| **Categoría** | Funcional / UX / Accesibilidad |
| **URL** | http://127.0.0.1:4173/informe-accion-fiduciaria.html |
| **Video de reproducción** | N/A |

**Descripción**

Las tarjetas sí abren correctamente un diálogo visual de detalle. Sin embargo, el botón “Línea base” conserva `aria-expanded="false"` mientras el diálogo está abierto y el foco permanece en la tarjeta detrás del modal. Además, `aria-controls` describe el detalle embebido, no el diálogo que finalmente recibe el contenido. Un lector de pantalla recibe un estado distinto del visible. Se esperaba usar semántica de apertura de diálogo (`aria-haspopup="dialog"`), mover el foco al modal y anunciar su estado de forma consistente.

**Pasos de reproducción**

1. Abrir el informe y localizar la tarjeta “Línea base”.
   ![Paso 1](screenshots/issue-002-step-1.png)
2. Pulsar la tarjeta.
3. **Resultado:** el diálogo se abre, pero el botón sigue exponiendo `aria-expanded="false"` y conserva el foco.
   ![Resultado](screenshots/issue-002-semantics.png)

---

### ISSUE-009: El PDF exportado es una imagen sin texto accesible

| Campo | Valor |
|---|---|
| **Severidad** | Media |
| **Categoría** | Accesibilidad / Exportación |
| **Artefacto corregido** | [Informe Accion Fiduciaria Junio 2026.pdf](../output/pdf/Informe%20Accion%20Fiduciaria%20Junio%202026.pdf) |
| **Video de reproducción** | N/A |

**Descripción**

El PDF de 10 páginas se ve correctamente, pero cada página se inserta como una imagen PNG. `pdfinfo` reporta `Tagged: no` y la extracción de texto devuelve únicamente separadores de página. Por lo tanto, el contenido no es seleccionable ni buscable y no puede recorrerse adecuadamente con lector de pantalla. Se esperaba conservar una capa de texto o producir un PDF etiquetado accesible.

---

### ISSUE-008: El prototipo `index (1).html` abre una página vacía

| Campo | Valor |
|---|---|
| **Severidad** | Baja |
| **Categoría** | Estructura del proyecto / Mantenibilidad |
| **URL** | http://127.0.0.1:4173/index%20(1).html |
| **Video de reproducción** | N/A |

**Descripción**

El archivo solo contiene el contenedor `#app` y referencia `styles.css` y `app.js`, pero ambos recursos faltan y responden HTTP 404. Si se entrega o abre por error, el usuario ve una página completamente vacía. Se esperaba eliminar/archivar el prototipo o incluir una indicación que dirija al HTML vigente.

**Evidencia**

![Página vacía del prototipo](screenshots/issue-008-orphan-index.png)

---
