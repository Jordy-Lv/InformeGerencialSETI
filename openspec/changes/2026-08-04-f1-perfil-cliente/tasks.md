# Tareas — F1 perfil de cliente

## Lista cerrada de archivos

- `perfiles/accion-fiduciaria.js`
- `informe-accion-fiduciaria 1.html`
- `openspec/changes/2026-08-04-f1-perfil-cliente/proposal.md`
- `openspec/changes/2026-08-04-f1-perfil-cliente/design.md`
- `openspec/changes/2026-08-04-f1-perfil-cliente/tasks.md`
- `openspec/changes/2026-08-04-f1-perfil-cliente/specs/perfil-cliente/spec.md`
- `openspec/specs/perfil-cliente/spec.md`
- `openspec/specs/README.md`
- `openspec/AGENTS.md`
- `automatizacion/test_specs_perfil_cliente.py`
- `docs/2026-08-04-f1-perfil-accion-fiduciaria.md`
- `docs/2026-08-04-plan-multicliente.md`

La PR #12 era la única PR abierta al revisar los conjuntos de archivos. Los
changes ya fusionados no reservan ninguno de los archivos nuevos de esta lista.

## Implementación

- [x] Extraer el perfil de Acción Fiduciaria como datos puros.
- [x] Resolver el perfil por id reutilizando `fusionarProfundo()`.
- [x] Aplicar el perfil a filtros, store y claves de almacenamiento del alcance.
- [x] Combinar la migración de claves de bolsa con la herencia entre periodos.
- [x] Transportar el perfil resuelto dentro del estado exportado.
- [x] Eliminar del export la dependencia al archivo vecino del perfil.
- [x] Hidratar desde el perfil los textos de interfaz y metadatos de exportación.
- [x] Agregar requisitos `SHALL`, escenarios y pruebas de conformidad.
- [x] Ejecutar A/B con dos exportaciones reales completas y obtener 0 diferencias.

## Evidencia de cierre

El 4 de agosto de 2026 se generaron dos exportaciones de Acción Fiduciaria para
julio de 2026, una desde `main` (`6ee842d`) y otra desde esta rama (`c536853`),
con exactamente los mismos cuatro insumos reales no versionados. Los siete
criterios quedaron válidos y `automatizacion/verificar_ab.py` informó
`0 diferencias`. Los archivos reales y las exportaciones temporales permanecen
fuera del repositorio.
