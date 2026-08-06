# Changes

Propuestas de cambio, una carpeta por change:
`<fecha>-<id>/{proposal.md, design.md, tasks.md, specs/<capability>/spec.md}`.

Ver `openspec/AGENTS.md` para la estructura completa. Para arrancar uno con
la estructura correcta: `/nuevo-change`.

## Abiertos vs. archivados

```text
openspec/changes/
  <fecha>-<id>/     ← ABIERTO. Cuenta para la regla de archivos disjuntos
  archivo/
    <fecha>-<id>/   ← CERRADO. NO cuenta para esa regla
```

**La regla de conjuntos de archivos disjuntos solo mira los changes
abiertos.** Dos changes abiertos no pueden declarar el mismo archivo en su
`tasks.md`; los archivados quedan un nivel más abajo, y así la regla vuelve a
dar el resultado correcto sin necesitar excepciones.

## Cuándo se archiva un change

Cuando su PR está fusionado en `main` **y** su criterio de aceptación está
cerrado con evidencia. Para todo lo que toca el HTML, ese criterio es una
verificación A/B con **0 diferencias** sobre exports reales.

```bash
git mv "openspec/changes/<fecha>-<id>" openspec/changes/archivo/
```

**Se mueve, no se borra** (convención fijada el 05/08/2026). El `tasks.md`
de un change archivado conserva la lista cerrada de archivos y las casillas
marcadas: es la única evidencia de qué se prometió tocar frente a qué se
tocó, y de qué se decidió *no* hacer. El `git log` no registra esa segunda
parte.

Si un change se archiva con un pendiente que no es código —F0 quedó a la
espera de `dorados/accion-fiduciaria-2026-06.json`, que exige insumos reales
de junio— se archiva con la nota explícita en su `tasks.md`.

### Antes de archivar, comprueba que ninguna prueba lea su ruta

Las pruebas de conformidad leen el delta desde la ruta del change:

```bash
grep -rn "openspec/changes" automatizacion/*.py
```

Archivar sin mirar esto **rompe la prueba** — pasó al archivar
`especificar-store-reporte`. La solución es que la prueba busque el delta en
las dos ubicaciones, como ya hace `test_specs_store_reporte.py`, no dejar el
change sin archivar.

## Estado

**Abiertos:**

- `2026-08-05-fundacion-documental` — capa de documentación de entrada
  (README, CLAUDE.md, DESIGN.md, índice de `docs/`, patrones, requisitos).
  No toca código productivo.
- `2026-08-04-f1-perfil-cliente` — **cerrado y fusionado (PR #12), pero aún
  sin archivar.** Archivarlo exige editar
  `automatizacion/test_specs_perfil_cliente.py`, que es un archivo declarado
  por F2; hacerlo ahora produciría la colisión que la regla de conjuntos
  disjuntos existe para evitar. Se archiva cuando F2 cierre.

**Archivados:**

- `2026-08-04-f0-dorados` — dorados persistentes para el A/B (PR #14).
- `2026-08-04-especificar-store-reporte` — spec del store `REPORTE` (PR #15).

**En curso fuera de `main`:** F2 (`2026-08-05-f2-contrato-perfil`), en la
rama `codex/f2-contrato-perfil`. Declara el HTML, el perfil, la spec de
`perfil-cliente` y sus pruebas.

> **Aviso mientras F1 siga abierto:** F1 y F2 declaran los mismos archivos.
> Es la única colisión conocida y está explicada arriba — no la tomes como
> precedente para abrir un tercer change sobre esos archivos.
