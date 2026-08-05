# F6 — Perfil Novaventa

## Contexto

Novaventa comparte GLPI, taxonomía y varias hojas de consolidado con Acción
Fiduciaria. Sus insumos reales añaden dos diferencias verificadas: `Data_<mes>`
es una fuente alternativa de alertas y la hoja Indicadores contiene un bloque
de metas sin fechas antes del bloque histórico.

## Propuesta

Añadir el perfil Novaventa como herencia de Acción Fiduciaria, resolverlo de
forma explícita en el informe y declarar sus fuentes y metadatos como datos.
Incorporar la estrategia `bloque-con-fechas` para escoger el bloque histórico
de indicadores y una tarjeta de capacidad alimentada desde su hoja Capacidad.

## Fuera de alcance

- Modificar cifras o comportamiento de Acción Fiduciaria.
- Implementar Bancóldex o automatización multicliente.
- Convertir la bolsa manual de AF en una regla de capacidad.
