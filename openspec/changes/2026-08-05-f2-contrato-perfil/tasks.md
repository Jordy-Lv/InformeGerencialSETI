# Tareas — F2 contrato desde el perfil

## Lista cerrada de archivos

- `perfiles/accion-fiduciaria.js`
- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_perfil_cliente.py`
- `openspec/changes/2026-08-05-f2-contrato-perfil/proposal.md`
- `openspec/changes/2026-08-05-f2-contrato-perfil/design.md`
- `openspec/changes/2026-08-05-f2-contrato-perfil/tasks.md`
- `openspec/changes/2026-08-05-f2-contrato-perfil/specs/perfil-cliente/spec.md`
- `openspec/specs/perfil-cliente/spec.md`
- `docs/2026-08-05-f2-contrato-perfil.md`
- `docs/2026-08-04-plan-multicliente.md`

F1 ya fue fusionada en `main` (PR #12) y su change está completo; los otros
changes abiertos no listan estos archivos productivos. F2 es el siguiente
paso secuencial que toca el HTML.

## Implementación

- [x] Declarar y validar `contrato.inicio` como dato de perfil.
- [x] Sustituir las seis lecturas del DOM y el fallback histórico.
- [x] Mantener el nodo visual como vista hidratada desde el perfil.
- [x] Añadir escenarios de conformidad para fecha local, dato faltante y
  ausencia de lecturas del DOM.
- [x] Ejecutar la suite y comprobaciones de sintaxis.
- [x] Ejecutar A/B contra `main` desde dos exportaciones reales completas.
- [x] Documentar los comandos, resultados y pendientes reales.
