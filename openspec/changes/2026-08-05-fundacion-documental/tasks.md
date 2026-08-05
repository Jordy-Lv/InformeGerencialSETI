# Tareas — fundación documental

## Lista cerrada de archivos

Documentos nuevos:

- `README.md`
- `CLAUDE.md`
- `DESIGN.md`
- `docs/README.md`
- `docs/PATRONES.md`
- `docs/requisitos-producto.md`
- `docs/2026-08-05-fundacion-documental.md`
- `.claude/skills/nuevo-change/SKILL.md`
- `openspec/changes/2026-08-05-fundacion-documental/{proposal,design,tasks}.md`

Documentos modificados:

- `.gitignore`
- `openspec/specs/README.md`
- `openspec/changes/README.md`
- `automatizacion/README.md` (solo la referencia rota de la línea 18)
- `automatizacion/test_specs_store_reporte.py` (solo la resolución de la
  ruta del delta, tras descubrir que archivar el change rompía la prueba)
- `docs/2026-07-22-backups-radar-ci.md`,
  `docs/2026-07-23-analisis-por-rango-y-redondeo.md`,
  `docs/2026-07-29-relevo-sesion-28-julio.md` (solo enlaces rotos)

Movimientos (sin editar contenido):

- `openspec/changes/2026-08-04-f0-dorados/` → `openspec/changes/archivo/`
- `openspec/changes/2026-08-04-especificar-store-reporte/` → `openspec/changes/archivo/`

**Ningún archivo de esta lista aparece en el `tasks.md` de F2**, el único
change abierto que toca código. F2 declara `perfiles/accion-fiduciaria.js`,
`informe-accion-fiduciaria 1.html`, `automatizacion/test_specs_perfil_cliente.py`,
`openspec/specs/perfil-cliente/spec.md`, `docs/2026-08-05-f2-contrato-perfil.md`
y `docs/2026-08-04-plan-multicliente.md`. Los conjuntos son disjuntos: este
change no toca ninguno de esos seis.

### Por qué F1 no se archiva todavía

Se intentó, y **rompió `automatizacion/test_specs_perfil_cliente.py`**: esa
prueba lee el delta desde la ruta literal del change, que al archivarse deja
de existir. Arreglarla exige editar ese archivo — y ese archivo está
declarado por F2.

Archivar F1 aquí habría producido exactamente la colisión que la regla de
conjuntos disjuntos existe para evitar. F1 se queda abierto y se archiva
cuando F2 cierre, en el mismo change que libere ese test. La deuda queda
registrada abajo.

## Implementación

- [x] Redactar `README.md` como punto de entrada con ruta de lectura.
- [x] Redactar `CLAUDE.md` con el contrato operativo y las pruebas
      adversariales, remitiendo a `project.md`/`AGENTS.md` sin duplicarlos.
- [x] Extraer el sistema de diseño real del HTML a `DESIGN.md`.
- [x] Indexar `docs/` con estado por documento y vigencia de la plantilla.
- [x] Extraer los siete patrones y los descartados a `docs/PATRONES.md`.
- [x] Redactar `docs/requisitos-producto.md` con requisitos trazables.
- [x] Cubrir `Accion Fiduciaria/` en `.gitignore`.
- [x] Fijar la convención de archivado y mover los changes cerrados que
      podían moverse sin invadir el conjunto de archivos de F2 (dos de tres).
- [x] Hacer que `test_specs_store_reporte.py` resuelva el delta esté el
      change abierto o archivado, en vez de depender de una ruta literal.
- [x] Reparar las cuatro referencias a documentos no conservados.
- [x] Publicar la skill `nuevo-change`.
- [x] Verificar que todo enlace interno resuelve y que la suite sigue verde.
- [x] Documentar comandos, resultados y pendientes reales.

## Pendientes que este change deja registrados, no resueltos

- [ ] Specs de `exportacion`, `inventario-tarjetas`, `adaptadores-fuente`,
      `automatizacion-insumos` y `reglas-de-negocio`.
- [ ] `dorados/accion-fiduciaria-2026-06.json` (criterio de cierre de F0).
- [ ] Consumo real de `PERFIL.metas`, `PERFIL.celula` y
      `PERFIL.contrato.codigo` por el motor.
- [ ] Trazabilidad de `automatizacion/instalar_tarea_programada.{ps1,bat}`.
- [ ] Archivar `2026-08-04-f1-perfil-cliente` cuando F2 cierre, aplicando a
      `test_specs_perfil_cliente.py` el mismo resolutor de ruta que ya tiene
      `test_specs_store_reporte.py`.
- [ ] Renombrar `esAccionFiduciaria()` y `esClienteAccion()` a nombres de
      motor multicliente.
