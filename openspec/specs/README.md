# Specs

Cada subcarpeta es una capacidad del sistema (`perfil-cliente/`,
`inventario-tarjetas/`, `adaptadores-fuente/`, `store-reporte/`,
`exportacion/`, `automatizacion-insumos/`, `reglas-de-negocio/`...), nunca
un cliente — ver `openspec/AGENTS.md`.

**Estado:** vacío todavía. `store-reporte/spec.md` y `exportacion/spec.md`
deberían ser lo primero en escribirse — documentan comportamiento que **ya
existe** en `informe-accion-fiduciaria 1.html` (el store `REPORTE`, sus 5
estados por dominio, el coalescing por microtask, que `exportarHTML()`
clona el DOM vivo) y que hoy solo vive en comentarios dentro del archivo.
Es trabajo de lectura cuidadosa del código real, no de diseño — se deja
pendiente como su propio `change`, no se improvisa aquí.
