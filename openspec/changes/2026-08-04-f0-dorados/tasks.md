# Tareas — F0 dorados A/B

## Lista cerrada de archivos

- `openspec/changes/2026-08-04-f0-dorados/proposal.md`
- `openspec/changes/2026-08-04-f0-dorados/design.md`
- `openspec/changes/2026-08-04-f0-dorados/tasks.md`
- `openspec/changes/2026-08-04-f0-dorados/specs/exportacion/spec.md`
- `automatizacion/verificar_ab.py`
- `automatizacion/test_verificar_ab.py`
- `dorados/README.md`
- `docs/2026-08-04-f0-dorados-verificacion.md`

Ninguno coincide con los tres archivos de la PR #12, única PR abierta al
iniciar este change.

## Implementación

- [x] Reconocer el arnés existente y el formato real de `snapshotEstado()`.
- [x] Implementar creación determinista de dorados sin datos en claro.
- [x] Implementar verificación de un export contra un dorado.
- [x] Mantener compatible la comparación directa entre dos HTML.
- [x] Cubrir éxito, regresión, periodo incorrecto, export inválido y
  sobrescritura explícita con `unittest`.
- [x] Documentar los comandos ejecutados y el pendiente del export real.

## Pendiente externo

- [ ] Crear `dorados/accion-fiduciaria-2026-06.json` desde un export real y
  completo de junio de 2026. Requiere insumos reales fuera del repositorio.
