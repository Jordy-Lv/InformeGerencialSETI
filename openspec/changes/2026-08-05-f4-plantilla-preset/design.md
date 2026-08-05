# Diseño — F4 plantilla y preset

## Límites de la migración

La tarjeta de panel y su detalle se generan con una única plantilla desde el
descriptor. La diapositiva interna se conserva con su `id` legado (`s3`,
`s4`, …): los parsers y `html2canvas` la escriben y capturan directamente.
Esta separación evita que el refactor rompa destinos de escritura que aún no
están descritos como datos.

La selección resuelta es una lista ordenada de ids válidos del inventario. El
valor por defecto permanece en `PERFIL.tarjetas.seleccionadas`; el override
del consultor vive bajo `informe:<perfil>:preset-tarjetas` en `localStorage`.
Un valor corrupto, repetido o con ids desconocidos se ignora y no impide
abrir el informe.

## Interfaz y exportación

El selector reutiliza el modal existente para no abrir un segundo sistema de
diálogos. Cada opción muestra su nombre y los criterios que desaparecerían;
una dependencia no satisfecha queda deshabilitada con su motivo. La primera
versión de Acción Fiduciaria no declara dependencias, pero la validación se
implementa desde el descriptor para no esconder esa regla futura.

La exportación serializa el perfil resuelto, incluida la selección efectiva.
El PDF itera únicamente las diapositivas asociadas a tarjetas exportables y
seleccionadas, más su portada fija. Con el preset por defecto, la secuencia y
el contenido son exactamente los actuales.

## Alternativas descartadas

- Eliminar o recrear las diapositivas desde JavaScript: rompería los parsers
  que aún escriben selectores de legado y elevaría innecesariamente el riesgo
  de la captura PDF.
- Guardar el preset dentro del perfil fuente: un cambio temporal del
  consultor no debe modificar la configuración entregada.
- Crear componentes web: Shadow DOM no es compatible con el clonado ni con
  la captura que produce el PDF.
