# F2 — Inicio contractual desde el perfil

**Fecha:** 5 de agosto de 2026

## Contexto

F1 dejó el perfil de Acción Fiduciaria como fuente de sus datos, pero seis
recorridos del pipeline todavía usaban el texto editable
`[data-k="finicio"]`. Cuando ese nodo no era legible, cada recorrido usaba
silenciosamente `new Date(2025,8,1)`. Eso no es aceptable para un perfil
nuevo: una fecha plausible e incorrecta recorta el histórico sin avisar.

## Qué se implementó

- `PERFIL.contrato.inicio` declara `2025-09-01`, el mismo día que el texto
  visible vigente `01/09/2025`.
- `inicioContrato()` valida formato ISO, día calendario real y construye la
  fecha en hora local. Al faltar o ser inválido, el motor falla antes de
  `load` con un mensaje que nombra `contrato.inicio`; no queda fallback.
- `INICIO_CONTRATO` sustituye las seis lecturas del DOM y la comprobación de
  autoprueba de backups. El nodo visual permanece, pero
  `hidratarContratoPerfil()` lo escribe desde el perfil.
- El delta OpenSpec y la spec vigente añaden los requisitos verificables de
  fuente, validación y ausencia de lecturas del DOM. Las pruebas de
  conformidad cubren el perfil, el pipeline y la hidratación.

## Verificación realizada

- Se revisó el inventario de entradas y salidas relevantes del proyecto: los
  insumos manuales de Acción Fiduciaria están en `Accion Fiduciaria/`, los
  paquetes y cortes automáticos en `automatizacion/salida/`, y el perfil en
  `perfiles/`. En particular, el CSV de indisponibilidades de julio está en
  `automatizacion/salida/indisponibilidades-2026-07.csv`; no se volvió a
  tratar como un insumo inexistente.
- Los diez escenarios de perfil y contrato pasan —
  `python3 -m unittest automatizacion/test_specs_perfil_cliente.py -v` →
  `Ran 10 tests ... OK`.
- La suite completa conserva las cuarenta pruebas —
  `python3 -m unittest discover -s automatizacion -p 'test_*.py' -v` →
  `Ran 40 tests ... OK`.
- Los nueve bloques JavaScript internos compilan y el perfil es sintácticamente
  válido — `node --input-type=module ...` y
  `node --check perfiles/accion-fiduciaria.js` → `Bloques internos válidos: 9`.
- La lógica de fecha se evaluó en tiempo de ejecución: conserva el 1 de
  septiembre de 2025 y rechaza ausencia, 30 de febrero y formato no ISO —
  `node --input-type=module ...` → `Contrato válido y tres casos inválidos
  verificados en tiempo de ejecución.`
- El arnés A/B continúa distinguiendo igualdad, una cifra modificada y un
  elemento extra — `python3 automatizacion/verificar_ab.py --autoprueba` →
  `Autoprueba OK`.
- El primer cotejo fue descartado: no usaba el paquete completo de salida en
  ambos lados. El inventario posterior confirmó que el insumo auxiliar sí
  existe en el proyecto: `automatizacion/salida/indisponibilidades-2026-07.csv`.
- El A/B de cierre se generó desde una copia temporal de `main` (`404408c`) y
  otra de esta rama, ambas con el mismo paquete real
  `automatizacion/salida/insumos-af.js`
  (`d6b086a09a19230e018cda6dab58e7ec406433ae`). Ese paquete incorpora GLPI,
  AlertsList y `indisponibilidades-2026-07.csv`; los cuatro insumos manuales
  reales de `Accion Fiduciaria/` se restauraron en ambos informes.
- En la carga de ambas versiones, julio de 2026 reportó 54 casos (6
  requerimientos y 2 incidentes), 46 alertas, 0 atribuibles a SETI y el aviso
  de los 2 incidentes sin confirmar en el log de indisponibilidades.
- Las exportaciones comparadas quedaron fuera del repositorio en
  `/tmp/export-main-f2-julio-2026-controlado.html` y
  `/tmp/export-f2-julio-2026-controlado-v2.html`. El comando
  `python3 automatizacion/verificar_ab.py /tmp/export-main-f2-julio-2026-controlado.html /tmp/export-f2-julio-2026-controlado-v2.html`
  devolvió `0 diferencias`.
- La exportación F2 resultante contiene `inicioContrato()` e
  `INICIO_CONTRATO`. Las copias y exportaciones fueron temporales; no se
  modificó OneDrive de producción.
- No hay errores de espacios — `git diff --check` → código 0.

## Archivos tocados

- `perfiles/accion-fiduciaria.js`
- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_perfil_cliente.py`
- `openspec/changes/2026-08-05-f2-contrato-perfil/` (propuesta, diseño,
  tareas y delta)
- `openspec/specs/perfil-cliente/spec.md`
- `docs/2026-08-05-f2-contrato-perfil.md`
- `docs/2026-08-04-plan-multicliente.md`

## Pendiente

- Abrir la revisión y fusión de F2 contra `main`; no quedan tareas técnicas
  ni cambios visibles pendientes dentro de esta fase.
