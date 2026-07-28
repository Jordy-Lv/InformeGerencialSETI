# Auditoría de integridad de datos — decisiones vigentes

**Proyecto:** Informe gerencial — Acción Fiduciaria
**Auditoría original:** 19 de julio de 2026. **Corregida:** 19 de julio de 2026.

> **Nota (28/07/2026):** este documento se recortó. La versión original incluía
> quince hallazgos detallados (DATA-001 a DATA-015) con evidencia línea por
> línea de bugs que **ya fueron corregidos** en el código — el propio
> documento original lo decía: *"Los hallazgos de esta auditoría fueron
> corregidos"*. Se conserva aquí solo lo que sigue siendo relevante hoy: las
> decisiones de negocio tomadas y lo que quedó pendiente de definir. El detalle
> de cada bug ya resuelto se eliminó por no aportar nada operativo.

## Decisiones de negocio tomadas por el responsable

| Tema | Decisión aplicada |
|---|---|
| Corte de alertas | **Mes calendario.** Junio = 49. AlertsList manda para el mes en curso; el consolidado solo aporta meses previos. Si alguna vez discrepan, la diferencia se registra en `REPORTE.reconciliaciones` para control interno pero **no se muestra en el informe**: es información de auditoría y el destinatario es el cliente. No bloquea la emisión. |
| Sesión limpia | Tablero vacío. Cero cifras demo. **Sin banner de aviso**: el usuario lo consideró redundante, porque una tarjeta en «Pendiente de cargar» ya comunica que falta el insumo. |
| GLPI sin filas | «Sin registros en el periodo», nunca un porcentaje. Avisa pero no bloquea. |
| Bolsa de horas | Se configura a mano directamente en el HTML (no viene de un insumo automático); así queda por diseño. |

## Arquitectura implementada

`window.REPORTE` es el store canónico, con un estado explícito por dominio
(`no_cargado`, `valido`, `sin_registros_confirmado`, `advertencia`, `invalido`).
Tarjetas, modales, gráficos y PDF leen solo del store — ningún componente lee
de variables globales, DOM ajeno o instancias de Chart.js por separado.

## Verificación

Suite embebida: `await REPORTE.autopruebas([File,...])` desde la consola de un
navegador con el HTML abierto. Sin argumentos comprueba solo el estado en frío.

## Sigue pendiente (decisiones de negocio, a la fecha del recorte)

- Definir la fecha contractual de GLPI para SLA: apertura, solución, cierre o
  ventana de corte.
- Confirmar si mitigaciones/riesgos tendrá columna formal de estado en la
  fuente. El código ya la usa si aparece con encabezado «Estado»; si no,
  declara «No informado en la fuente» en vez de inferirlo por palabras clave.

## Pendiente de verificación manual (a la fecha del recorte)

La descarga real del PDF completo (no solo el pipeline hasta la vista previa)
no se había verificado en una ventana visible al momento de esta corrección.
