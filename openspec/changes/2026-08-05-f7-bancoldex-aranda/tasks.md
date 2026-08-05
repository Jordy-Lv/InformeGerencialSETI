# F7 — Adaptador Aranda y perfil Bancóldex (F7a datos + F7b integración)

Rama de cierre `codex/bancoldex-completo`, creada desde el estado documentado
de `f7/bancoldex-aranda-perfil` (`4f822c3`).
F6 sigue abierto (en el directorio principal, sin confirmar) y reserva
`informe-accion-fiduciaria 1.html`; este change también lo lista (ver
"Coordinación con F6" en `proposal.md`) porque F7 solo añade funciones
nuevas y generalizaciones con valor por defecto idéntico al de AF, nunca
reescribiendo lógica existente de GLPI/AF/Novaventa. Antes de mergear a
`main`, coordinar el orden con quien cierre F6.

## Lista cerrada de archivos

- `perfiles/base.js` (nuevo)
- `perfiles/bancoldex.js` (nuevo)
- `informe-accion-fiduciaria 1.html` (funciones nuevas: registro de
  perfiles `base`/`bancoldex`, `ID_PERFIL_ACTIVO`, `clasificarTipoAranda`,
  `adaptarArandaACanonico`, `cargarCasosAranda`, `cargarCasosOGlpi`,
  `cargarDisponibilidadTabla`, `presentarTarjetaPerfil`; generalizaciones
  con default idéntico a AF: `definicionIndicador`/`cargarIndicadores`,
  `cargarBackups`, `actualizarTarjetaBackups`, `renderC3`,
  `actualizarTarjetasDesdeStore`/`TARJETA_PENDIENTE`)
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
- [x] Implementar `cargarCasosAranda()`, que lee, adapta, agrega y publica los
  casos de Aranda en `REPORTE.casos`, sin modificar `cargarGlpi()`.
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
- [x] **F7b** — Enrutar la entrada de archivo de casos por perfil
  (`cargarCasosOGlpi`) en los tres sitios que llamaban `cargarGlpi` directo.
- [x] **F7b** — Generalizar `cargarIndicadores()` (hoja y métricas por
  perfil, default AF intacto) y verificar contra `Indicador` real: 3
  métricas, meta y valores de junio-2026 correctos.
- [x] **F7b** — Generalizar `cargarBackups()` (hoja/columna por perfil) y
  corregir el bug real de coincidencia de columna «bd» con datos (ver
  design.md); verificado: 11 BD, 100 %.
- [x] **F7b** — `cargarDisponibilidadTabla()` para disponibilidad por motor;
  verificado que la hoja real no tiene columna para jun-26 (hallazgo, no
  bug — ver design.md).
- [x] **F7b** — `PERFIL.lineaBase` en `renderC3()` y `presentarTarjetaPerfil()`
  + `tarjetas.presentacion`, incluida la generalización de
  `TARJETA_PENDIENTE` (tercer lugar con texto de AF quemado, hallazgo al
  verificar en navegador).
- [x] **Cierre** — Fijar el preset respaldado por insumos originales:
  `c3, c4, c5, c7, c8, c8m`.
- [x] **F7b** — Verificación end-to-end en navegador con los dos archivos
  reales de junio-2026 (consolidado + Aranda): indicadores, backups y casos
  cargan correctamente; disponibilidad reporta su hallazgo real; AF sin
  cambios (mismo `CN-21012025`, misma `Meta 99,30%`, consola limpia).
- [x] Ejecutar la suite completa tras F7b → 77 pruebas, OK.
- [x] Crear una copia local y claramente etiquetada del consolidado con una
  columna simulada de junio de 2026; comprobar con ella 100 % global y 4/4
  motores, sin tratar el fixture como evidencia del servicio.
- [x] Corregir el cuarto literal de meta AF en el resumen de `c11` para leer
  la meta del dominio (`4f822c3`) y ejecutar la suite completa → 78 pruebas,
  OK.
- [x] Configurar `c5` declarativamente para Aranda y reutilizar la tarjeta,
  modal, gráfica apilada y análisis de Acción Fiduciaria.
- [x] Reemplazar los desgloses tabulares de Aranda por gráficas: dona por
  motor y barras horizontales por categoría.
- [x] Procesar un solo libro cualitativo con hojas `Logros` y `Mitigación` y
  validar que las fechas de entrega correspondan a jun-26.
- [x] Evitar que `insumos-af.js` se autocargue en Bancóldex y corrija el
  periodo del cliente con un paquete de Acción Fiduciaria.
- [x] Restaurar periodo e insumos persistidos sin una revalidación prematura;
  recargar y confirmar junio-2026, 2/2 fuentes obligatorias y exportaciones
  habilitadas.
- [x] Rehidratar las tarjetas/gráficas desde el estado embebido del HTML para
  que el entregable sea autocontenido.
- [x] Verificar visualmente en navegador el dashboard y el modal final de
  casos: 72 total, 71/72 SLA, 52 Oracle y 16 en la categoría principal.
- [x] Ejecutar suite final de 84 pruebas, validación de sintaxis JavaScript y
  `git diff --check`.
- [ ] Publicar la rama remota/PR (no solicitado; requiere decisión del
  usuario/equipo).

## Exclusiones deliberadas del preset

- Lector dinámico de la hoja `Linea Base` (hoy `PERFIL.lineaBase` es
  declaración estática verificada contra el PDF aprobado; el Excel original
  presenta totales incompatibles).
- `c6`/`c11`: el original de `Disponibilidad Real` termina en jun-25; el
  fixture de prueba no se usa como evidencia.
- `c9`: TYA corresponde a sep-25 y no acredita contrato/saldo de horas para
  jun-26.
- `c12`: no existe insumo mensual exportable en el flujo entregado.
