# Diseño — F5 adaptadores y canónico

`CasoCanonico` es un objeto plano con `id`, `fecha`, `cliente`, `origen`,
`tipo`, `categoria`, `jerarquia`, `slaCumplido`, `motor`, `ambiente` y
`atribuibleSeti`. Los tres últimos valores lógicos aceptan `true`, `false` o
`null`; `null` significa que la fuente no lo declara y nunca se suma a los
casos que cumplen SLA.

Los adaptadores reciben una matriz ya leída y una declaración de columnas. El
adaptador de GLPI conserva la regla de revisiones de alerta y el cruce de
indisponibilidades; AlertsList produce casos de tipo `alerta`. Después, los
cargadores existentes derivan sus métricas desde esos casos y conservan su
publicación actual en `REPORTE`.

`resolverCabecera()` enumera todas las filas que satisfacen los campos
requeridos. Para la estrategia actual `primera-fila-con`, cero candidatos
indica encabezado faltante, uno es válido y más de uno produce un error que
incluye los índices candidatos. No se modifica `filaCabecera()` porque los
lectores de consolidado usan deliberadamente sus reglas heredadas y no forman
parte de esta migración.

La declaración `origenes` admite precedencia y ámbito. Su resolución escoge
la primera fuente aplicable y registra diferencias como reconciliación interna;
AF declara el orden actual AlertsList antes del consolidado histórico, sin
alterar sus cifras.
