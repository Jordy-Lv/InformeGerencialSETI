# F5 — Adaptadores de fuente y modelo canónico

## Contexto

Acción Fiduciaria ya resuelve el perfil y el inventario de tarjetas, pero
`cargarGlpi()` y `cargarAlertas()` todavía convierten sus filas directamente en
contadores de la interfaz. Ese acoplamiento no permite incorporar una fuente
nueva sin añadir ramas a las tarjetas y puede elegir silenciosamente una
cabecera repetida.

## Propuesta

Introducir `CasoCanonico` como frontera entre los adaptadores de GLPI y
AlertsList y los consumidores existentes. La configuración de cada origen se
declara en el perfil y el motor conserva los nombres y la firma de los
cargadores actuales. La resolución de cabecera para esos adaptadores rechazará
candidatos ambiguos con una nota verificable en lugar de seleccionar uno.

## Fuera de alcance

- Añadir un cliente nuevo o un lector de Aranda.
- Cambiar el preset, las tarjetas o el diseño visual de Acción Fiduciaria.
- Cambiar la regla contractual de AF para un archivo con columnas válidas.
