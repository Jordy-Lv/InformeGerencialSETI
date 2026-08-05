# F7a — Adaptador Aranda y perfil Bancóldex (datos + canónico)

Rama `f7/bancoldex-aranda-perfil`, creada desde el cierre de F5 (`db3d368`).
F6 sigue abierto y reserva `informe-accion-fiduciaria 1.html`; este change
también lo lista (ver "Coordinación con F6" en `proposal.md`) porque F7a solo
añade funciones nuevas sin tocar las de GLPI/AF/Novaventa. Antes de mergear a
`main`, coordinar el orden con quien cierre F6.

## Lista cerrada de archivos

- `perfiles/base.js` (nuevo)
- `perfiles/bancoldex.js` (nuevo)
- `informe-accion-fiduciaria 1.html` (solo funciones nuevas: registro de
  perfiles `base`/`bancoldex`, `ID_PERFIL_ACTIVO`, `clasificarTipoAranda`,
  `adaptarArandaACanonico`, `cargarCasosAranda`)
- `automatizacion/test_specs_adaptadores_fuente.py`
- `automatizacion/test_specs_perfil_cliente.py`
- `openspec/changes/2026-08-05-f7-bancoldex-aranda/`
- `openspec/specs/adaptadores-fuente/spec.md`
- `openspec/specs/perfil-cliente/spec.md`
- `docs/2026-08-05-f7-bancoldex-aranda.md`
- `docs/2026-08-04-plan-multicliente.md`

## Implementación

- [x] Declarar `perfiles/base.js` y registrarlo en `PERFILES_REGISTRADOS`.
- [x] Declarar `perfiles/bancoldex.js` (extiende `base`) con la fuente `casos`
  de Aranda.
- [x] Implementar `adaptarArandaACanonico()` reutilizando `casoCanonico()` y
  el clasificador `clasificarTipoAranda()`.
- [x] Implementar la estrategia SLA `columna-cumplimiento`.
- [x] Implementar `cargarCasosAranda()`, que lee, adapta y agrega los casos
  de Aranda y devuelve el resultado (no publica en `REPORTE`: no hay dominio
  derivado todavía — ver design.md), sin modificar `cargarGlpi()`.
- [x] Agregar `ID_PERFIL_ACTIVO` (hallazgo: al cierre de F5 el perfil activo
  estaba fijo en `'accion-fiduciaria'`, sin mecanismo `?perfil=`; sin esto
  `base`/`bancoldex` quedaban inalcanzables).
- [x] Fixtures: verificación directa contra el export real de junio-2026
  (`Bancoldex/`, no versionado) en vez de un fixture sintético — ver
  `docs/2026-08-05-f7-bancoldex-aranda.md`.
- [x] Pruebas de conformidad Python (grep/regex sobre HTML y perfiles, mismo
  patrón que `test_specs_perfil_cliente.py`).
- [x] Ejecutar `python3 -m unittest discover -s automatizacion -p 'test_*.py'`
  → 68 pruebas, OK.
- [x] Cotejar los 72 casos, sus agregados por tipo/motor y el SLA 71/1 contra
  el export real de junio-2026 y `Bancoldex/reporte-bancoldex-2026-07-02.pdf`
  → coinciden exactamente (ver docs/2026-08-05-f7-bancoldex-aranda.md).
- [x] Cargar `?perfil=bancoldex` en navegador real y confirmar consola sin
  errores; ajustar `tarjetas.seleccionadas` tras encontrar que un arreglo
  vacío no es un estado soportado por `resolverTarjetasPerfil()`.
- [x] Registrar la evidencia de cierre y actualizar
  `docs/2026-08-04-plan-multicliente.md`.
- [ ] Coordinar el orden de merge con quien cierre F6 y publicar la rama
  remota (pendiente, requiere acción del equipo).

## Explícitamente fuera de esta lista (F7b, change futuro)

- Integración de `cargarCasosAranda()` con el centro de carga y una tarjeta
  visual para las cuatro categorías de Bancóldex.
- Lectores de consolidado: `Indicador` (cabecera de dos filas), `Ejecucion
  Backups`, `Linea Base`, `Disponibilidad Real` por motor.
- Decisión sobre `TYA` y la bolsa de horas.
