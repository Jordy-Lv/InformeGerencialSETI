# F0 — Fundación de OpenSpec

**Fecha:** 4 de agosto de 2026

## Contexto

Segunda pieza de F0 del plan de plataforma multicliente. Sin
`openspec/project.md` y `openspec/AGENTS.md`, no hay dónde anclar las
restricciones inviolables ni el proceso de `changes`/`specs` que el plan
exige para que varias IAs trabajando en paralelo no se desvíen.

## Qué se implementó

- `openspec/project.md`: las tres restricciones inviolables (HTML
  `file://`, Acción Fiduciaria no cambia una cifra, Python stdlib+openpyxl),
  el principio dato-vs-código con su prueba práctica y el corolario de "dos
  clientes con evidencia real" antes de cualquier mecanismo nuevo, la
  prohibición explícita de árboles de código por cliente (citando el PR #5
  como precedente ya vivido), y una tabla de dónde vive cada cosa.
- `openspec/AGENTS.md`: cómo se estructura un `change`, la regla de
  conjuntos de archivos disjuntos entre changes abiertos, el requisito
  `SHALL` + escenario verificable, la prohibición de una capacidad por
  cliente, y una lista de verificación de "antes de escribir una línea" /
  "al terminar".
- `openspec/specs/README.md` y `openspec/changes/README.md`: placeholders
  que explican el propósito de cada carpeta — **no** se escribieron specs
  de capacidades reales todavía (ver Pendiente).

## Verificación realizada

Ninguna ejecutable: son documentos de proceso, no código. La verificación
real es que alguien más los lea y confirme que reflejan el plan acordado
antes de que se usen para juzgar un PR — por eso este PR necesita revisión
como cualquier otro, no se auto-certifica.

## Pendiente

- **`openspec/specs/store-reporte/spec.md` y `exportacion/spec.md`**: son
  las specs de mayor prioridad después de esta fundación, porque
  documentan comportamiento que **ya existe** en
  `informe-accion-fiduciaria 1.html` y que hoy solo vive en comentarios.
  Requiere lectura cuidadosa del archivo real (el store `REPORTE`, sus 5
  estados por dominio, el coalescing por microtask, `exportarHTML()`
  clonando el DOM vivo) — se deja como su propio `change`, no se
  improvisó aquí para no escribir una spec superficial o incorrecta.
- El resto de las capacidades del inventario (`perfil-cliente`,
  `inventario-tarjetas`, `adaptadores-fuente`, `automatizacion-insumos`,
  `reglas-de-negocio`) esperan a que exista al menos un change real que
  las ejercite (F1 en adelante).
- Falta decidir la convención de archivado de un `change` completado
  (¿se mueve a `changes/archivo/`? ¿se borra?) — anotado en
  `openspec/changes/README.md`, sin resolver.

## Archivos tocados

- `openspec/project.md` (nuevo)
- `openspec/AGENTS.md` (nuevo)
- `openspec/specs/README.md` (nuevo)
- `openspec/changes/README.md` (nuevo)
