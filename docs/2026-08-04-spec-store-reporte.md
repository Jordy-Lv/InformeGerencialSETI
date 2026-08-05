# OpenSpec — store canónico del reporte

**Fecha:** 4 de agosto de 2026

## Contexto

El objeto `REPORTE` ya funciona en `main` como fuente de verdad del informe,
pero sus invariantes estaban descritos solamente por el código y sus
comentarios. El plan multicliente identifica `store-reporte` como una
capacidad que debe quedar especificada antes de continuar la migración.

Este cambio documenta el comportamiento desplegado sin modificar
`informe-accion-fiduciaria 1.html`. Su lista de archivos es disjunta de la
PR #12, que continúa reservando el perfil de Acción Fiduciaria y el HTML.

## Qué se implementó

- Un change de OpenSpec con propuesta, diseño, tareas y delta para
  `store-reporte`.
- Una spec canónica con siete requisitos `SHALL` y escenarios verificables:
  dominios y estados, publicación, semántica de cifra, notificaciones,
  cambio de periodo, rehidratación y concordancia de vistas.
- Ocho pruebas estáticas que confrontan la spec con las invariantes que ya
  existen en el HTML, sin ejecutar ni reescribir JavaScript.
- La prueba usa únicamente la librería estándar de Python.

## Verificación realizada

- Los ocho escenarios de contrato pasan:
  `python3 -m unittest automatizacion/test_specs_store_reporte.py -v`.
- La suite completa pasa con 30 pruebas:
  `python3 -m unittest discover -s automatizacion -p 'test_*.py' -v`.
- El archivo de prueba compila como Python válido:
  `python3 -m py_compile automatizacion/test_specs_store_reporte.py`.
- No hay errores de espacios ni marcadores de conflicto:
  `git diff --check`.
- El HTML no aparece entre los archivos modificados:
  `git diff --name-only` y `git status --short`.

## Archivos tocados

- `openspec/changes/2026-08-04-especificar-store-reporte/proposal.md`
- `openspec/changes/2026-08-04-especificar-store-reporte/design.md`
- `openspec/changes/2026-08-04-especificar-store-reporte/tasks.md`
- `openspec/changes/2026-08-04-especificar-store-reporte/specs/store-reporte/spec.md`
- `openspec/specs/store-reporte/spec.md`
- `automatizacion/test_specs_store_reporte.py`
- `docs/2026-08-04-spec-store-reporte.md`

## Pendiente

- Especificar `exportacion-offline` después de resolver la PR #12. Durante
  el reconocimiento se observó que el flujo de autoría puede cargar
  `insumos-af.js` como script vecino y que `exportarHTML()` conserva scripts
  con `src` al podar el clon. Antes de afirmar que todo entregable es
  autocontenido, ese caso debe resolverse y verificarse en el HTML con el
  arnés A/B.
- Ejecutar el dorado de F0 contra un export real completo de junio de 2026
  continúa pendiente por falta de esos insumos privados en el checkout.
