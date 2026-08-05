# Tareas — F4 plantilla de tarjetas y preset

## Lista cerrada de archivos

- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_inventario_tarjetas.py`
- `automatizacion/test_specs_store_reporte.py`
- `openspec/changes/2026-08-05-f4-plantilla-preset/`
- `openspec/specs/inventario-tarjetas/spec.md`
- `openspec/specs/preset-tarjetas/spec.md`
- `openspec/specs/README.md`
- `docs/2026-08-05-f4-plantilla-preset.md`
- `docs/2026-08-04-plan-multicliente.md`

F3 está cerrada con su evidencia A/B y es el cambio secuencial anterior que
reservaba el HTML y el perfil. Los changes con tareas incompletas no reservan
estos archivos productivos.

## Implementación

- [x] Extender el descriptor con la presentación necesaria para la plantilla.
- [x] Generar las tarjetas del panel desde los descriptores sin mover las
  diapositivas legado.
- [x] Añadir el modal de preset, dependencias y resumen de criterios.
- [x] Persistir y restaurar una selección válida por perfil.
- [x] Exportar la selección efectiva y derivar de ella las páginas del PDF.
- [x] Añadir autopruebas y pruebas estáticas para presets mínimo, máximo y
  restauración del predeterminado.
- [x] Ejecutar suite y comprobaciones de sintaxis.
- [x] Ejecutar A/B real contra `main` con el preset predeterminado.
- [ ] Comprobar visualmente el PDF con preset mínimo y máximo.
- [x] Actualizar las specs vigentes y el documento de sesión.

## Evidencia parcial de cierre

El 5 de agosto de 2026, `export-main-f3.html` (desde `main` `404408c`) y
`export-f4.html` (F4) se compararon con
`python3 automatizacion/verificar_ab.py` y dieron `0 diferencias`. Un parser
HTML confirmó además que `#presetTarjetasModal` no quedó en el DOM del
entregable. Falta solamente la comprobación visual de las dos composiciones
extremas del PDF.
