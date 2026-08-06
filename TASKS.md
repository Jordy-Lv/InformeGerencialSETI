# Tareas activas

Solo lo vigente: qué está en curso, qué bloquea y el siguiente paso. Para el
histórico completo de fases fusionadas, ver [`CHANGELOG.md`](CHANGELOG.md).
Para la arquitectura objetivo (qué es cada fase y su criterio de
aceptación), ver [`docs/arquitectura-multicliente.md`](docs/arquitectura-multicliente.md).

**Regla operativa** (`openspec/AGENTS.md`): dos `changes` abiertos no pueden
declarar el mismo archivo en su `tasks.md`. Revisa `openspec/changes/`
(excluye `archivo/`) antes de tocar código.

---

## Estado por fase, según `main`

| Fase | Estado en `main` |
|---|---|
| F0 — fundación (OpenSpec, arnés A/B, dorados) | **Casi completo.** Falta correr `verificar_ab.py` contra un export real de AF con insumos de junio-2026 y crear `dorados/accion-fiduciaria-2026-06.json`. Sin esa evidencia, el criterio de F0 no cierra formalmente |
| F1 — perfil de cliente como datos puros | **Cerrado.** PR #12 fusionado (commit `404408c`), A/B con insumos reales de julio: 0 diferencias |
| F2 — contrato desacoplado del DOM | En rama `codex/f2-contrato-perfil`, sin fusionar |
| F3 — inventario de tarjetas | En rama `codex/f3-inventario-tarjetas`, sin fusionar |
| F4 — plantilla y preset de tarjetas | En rama `codex/f4-plantilla-preset`, sin fusionar |
| F5 — adaptadores y modelo canónico | En rama `codex/f5-adaptadores-canonico`, sin fusionar |
| F6 — perfil Novaventa | En rama `codex/f6-perfil-novaventa`, sin fusionar |
| F7–F11 | No iniciadas |

**Nota:** F2–F6 tienen trabajo avanzado (según quien las lleve, con suite
verde) pero su estado detallado **no está commiteado en ninguna rama** al
06/08/2026 — solo `main` es la fuente de verdad aquí. Quien retome cada
fase: actualiza esta tabla con el estado real al fusionar, y mueve la fila a
`CHANGELOG.md` cuando cierre.

---

## Siguiente paso

Fusionar F2 → F3 → F4 → F5 → F6 a `main`, en ese orden (son secuenciales
sobre `informe-accion-fiduciaria 1.html`, ver `openspec/AGENTS.md`). Antes
de cada fusión: confirmar A/B en 0 contra `main` con insumos reales.

## Bloqueos conocidos

- `dorados/accion-fiduciaria-2026-06.json` no existe — requiere insumos
  reales de junio-2026 que no están en el repo (por diseño).
- Cardio Infantil (F11) bloqueada hasta resolver 4 preguntas de sondeo —
  ver `docs/arquitectura-multicliente.md`.
