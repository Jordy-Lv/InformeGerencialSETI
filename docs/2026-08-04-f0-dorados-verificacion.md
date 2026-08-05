# F0 — Dorados persistentes para la verificación A/B

**Fecha:** 4 de agosto de 2026

## Contexto

El arnés `automatizacion/verificar_ab.py` ya comparaba dos HTML exportados y
tenía una autoprueba sintética, pero F0 conservaba dos pendientes: ejecutar
la verificación con un export real completo de junio de 2026 y crear el
mecanismo `dorados/<cliente>-<AAAA-MM>.json` definido por el plan maestro.

Este incremento resuelve el mecanismo sin tocar el informe ni colisionar con
la PR #12. El export real continúa pendiente porque sus insumos privados no
están disponibles en el checkout.

## Qué se implementó

- Creación de dorados deterministas desde un HTML producido por
  `exportarHTML()` mediante `--crear-dorado`, `--cliente` y `--periodo`.
- Validación del periodo contra `window.__ESTADO__.periodo`, respetando que
  el mes del estado es base cero.
- Formato JSON sin valores reales en claro: solo identidad, conteos y huellas
  SHA-256 del estado y de cada lista de textos visibles.
- Verificación de un export mediante `--contra-dorado`, con códigos de salida
  `0` para igualdad, `1` para diferencias y `2` para entradas inválidas.
- Protección contra sobrescrituras accidentales; reemplazar un dorado exige
  `--reemplazar-dorado`.
- Ocho pruebas nuevas de creación, privacidad, determinismo, periodo,
  export inválido, regresión numérica, sobrescritura y compatibilidad del CLI.
- Change de OpenSpec con requisitos `SHALL` y escenarios convertidos en
  aserciones de `unittest`.

## Verificación realizada

- Los dos archivos Python compilan sin errores —
  `python3 -m py_compile automatizacion/verificar_ab.py automatizacion/test_verificar_ab.py`.
- Las 22 pruebas de `automatizacion/` pasan, incluidas las 8 nuevas —
  `python3 -m unittest discover -s automatizacion -p 'test_*.py' -v`.
- El arnés conserva su autoprueba histórica: igualdad, cifra mutada y elemento
  extra se distinguen correctamente —
  `python3 automatizacion/verificar_ab.py --autoprueba`.
- El diff no contiene errores de espacios ni marcadores inválidos —
  `git diff --check`.
- Al iniciar el trabajo, la única PR abierta era la #12 y sus tres archivos
  no coinciden con la lista cerrada de este change —
  `gh pr list --repo Jordy-Lv/InformeGerencialSETI --state open --limit 100 --json number,title,files`.

## Archivos tocados

- `automatizacion/verificar_ab.py`
- `automatizacion/test_verificar_ab.py`
- `dorados/README.md`
- `openspec/changes/2026-08-04-f0-dorados/proposal.md`
- `openspec/changes/2026-08-04-f0-dorados/design.md`
- `openspec/changes/2026-08-04-f0-dorados/tasks.md`
- `openspec/changes/2026-08-04-f0-dorados/specs/exportacion/spec.md`
- `docs/2026-08-04-f0-dorados-verificacion.md`

## Pendiente

- Generar `dorados/accion-fiduciaria-2026-06.json` desde un export real y
  completo de junio de 2026 y versionar únicamente ese JSON de huellas.
- Ejecutar el export actual contra esa referencia. Hasta entonces F0 sigue
  «casi completo»: el mecanismo queda probado, pero no la evidencia real.
- No se tocó ni se validó A/B el HTML porque este incremento no lo modifica.
