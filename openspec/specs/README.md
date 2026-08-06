# Specs

Cada subcarpeta es una capacidad **del sistema**, nunca un cliente — ver
`openspec/AGENTS.md`. Un cliente es una *instancia* que vive en `perfiles/` y
se valida con pruebas de conformidad contra las specs existentes.

Aquí vive el comportamiento **vigente y desplegado**. Lo que todavía se está
proponiendo va en `openspec/changes/<change>/specs/`.

## Estado de las siete capacidades

| Capacidad | Estado |
|---|---|
| `perfil-cliente` | **Escrita.** Perfiles como datos puros, resolución por id con fallo explícito, almacenamiento compatible, textos de interfaz, transporte autocontenido en el export, equivalencia de Acción Fiduciaria e inicio contractual declarado por perfil |
| `store-reporte` | **Escrita.** El store `REPORTE`, sus cinco estados por dominio, el agrupamiento por microtarea, el cambio de periodo y la rehidratación del entregable |
| `exportacion` | Pendiente |
| `reglas-de-negocio` | Pendiente |
| `adaptadores-fuente` | Pendiente |
| `inventario-tarjetas` | Pendiente |
| `automatizacion-insumos` | Pendiente |

## Qué falta en cada pendiente

- **`exportacion`** — debe documentar que `exportarHTML()` clona el DOM vivo
  y demostrar que el resultado es un único HTML autocontenido, incluso
  cuando la sesión de autoría cargó un `insumos-af.js` vecino. Es trabajo de
  lectura y verificación del código real, no de diseño.
- **`reglas-de-negocio`** — **la más urgente.** Cubriría la atribución a SETI
  (solo un «SI» explícito cuenta), el redondeo a un decimal con el
  cumplimiento juzgado sobre el valor publicado, y la invalidación de la
  bolsa de horas al cambiar de periodo. Las tres son reglas donde **ya hubo
  errores corregidos en producción**, y hoy solo las sostiene un comentario
  en el código y un documento de sesión: nada impide que un cambio futuro
  las rompa en silencio.
- **`adaptadores-fuente`** — el modelo canónico y las estrategias de
  clasificación, detección de encabezado y origen del SLA. Bloqueante para
  incorporar Novaventa o Bancóldex sin ramas por cliente.
- **`inventario-tarjetas`** — el descriptor de tarjetas y su derivación. El
  inventario levantado está en
  `docs/archivo/2026-08-03-inventario-tarjetas-cardio-infantil.md`.
- **`automatizacion-insumos`** — el punto de entrada único, las sondas de
  reconocimiento y la regla de que los datos del cliente no se versionan.

Cada una merece su propio change: son trabajo de lectura y verificación del
código real, no de diseño. El mapa de qué requisito quedaría cubierto por
cuál está en [`docs/requisitos-producto.md`](../../docs/requisitos-producto.md).

Mientras una capacidad no tenga spec, sus reglas **no se pueden citar como
normativas en una revisión**: están implementadas, no especificadas.
