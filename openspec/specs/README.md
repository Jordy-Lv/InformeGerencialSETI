# Specs

Cada subcarpeta es una capacidad del sistema (`perfil-cliente/`,
`inventario-tarjetas/`, `adaptadores-fuente/`, `store-reporte/`,
`exportacion/`, `automatizacion-insumos/`, `reglas-de-negocio/`...), nunca
un cliente — ver `openspec/AGENTS.md`.

**Estado:** `store-reporte/spec.md` documenta el store `REPORTE`, sus cinco
estados por dominio, el agrupamiento por microtarea, el cambio de periodo y
la rehidratación del entregable. `exportacion/spec.md` continúa pendiente:
debe documentar que `exportarHTML()` clona el DOM vivo y demostrar que el
resultado es un único HTML autocontenido, incluso cuando la sesión de autoría
cargó un `insumos-af.js` vecino. Es trabajo de lectura y verificación del
código real, no de diseño, y queda reservado para su propio `change` después
de liberar el HTML ocupado por la PR #12.
