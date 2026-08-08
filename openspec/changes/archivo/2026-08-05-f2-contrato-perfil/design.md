# Diseño — inicio contractual desde el perfil

## Fecha ISO validada localmente

`PERFIL.contrato.inicio` usa `AAAA-MM-DD`. No se entrega directamente a
`new Date(texto)`: esa forma interpreta una fecha ISO sin hora en UTC y puede
convertir septiembre en agosto en una zona horaria occidental. El motor la
reconoce por componentes y construye `new Date(anio, mes - 1, dia)`, que es
una fecha de calendario local. También comprueba el redondeo de JavaScript
para rechazar días inexistentes.

La validación ocurre al resolver el perfil, antes del primer evento `load`.
Un perfil sin el dato o con un formato/fecha inválidos detiene el arranque con
un mensaje que identifica `contrato.inicio`; no existe fallback.

## Fuente de verdad y vista

`INICIO_CONTRATO` conserva la fecha validada durante la sesión. Los seis
recorridos que limitan históricos, y la autoprueba de backups, lo consumen
directamente. El elemento `data-k="finicio"` se conserva por compatibilidad
visual y de edición del documento, pero se hidrata desde el perfil y no es
leído por el pipeline.

Se descartó usar `fecha(PERFIL.contrato.inicio)`: la función genérica debe
seguir aceptando fechas de Excel y texto libre existentes, mientras que el
contrato necesita semántica explícita de fecha calendario y un error claro.

## Equivalencia

El valor trasladado (`2025-09-01`) es el mismo día que el texto vigente
`01/09/2025` y que el fallback histórico. Por ello, los límites de cada serie
se mantienen. La comprobación A/B se ejecutará sobre exportaciones producidas
con los mismos insumos reales disponibles, además de las pruebas de contrato.
