# F6 — Perfil Novaventa

F5 quedó cerrado y publicado; ningún change activo reserva los archivos de
F6.

## Lista cerrada de archivos

- `perfiles/novaventa.js`
- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_perfil_cliente.py`
- `automatizacion/test_specs_inventario_tarjetas.py`
- `openspec/changes/2026-08-05-f6-perfil-novaventa/`
- `openspec/specs/perfil-cliente/spec.md`
- `openspec/specs/inventario-tarjetas/spec.md`
- `docs/2026-08-05-f6-perfil-novaventa.md`
- `docs/2026-08-05-registro-persistente-clientes.md`
- `docs/2026-08-04-plan-multicliente.md`

## Implementación

- [x] Declarar el perfil Novaventa y habilitar su resolución explícita.
- [x] Implementar `bloque-con-fechas` y migrar Indicadores a esa estrategia.
- [x] Declarar y cargar la fuente alternativa `Data_<mes>`.
- [x] Declarar la tabla de disponibilidad vigente de Novaventa y preservar
  `Casos` cuando un Data pertenece a otro corte.
- [x] Declarar la línea base y el preset inicial de Novaventa sin bolsa de
  horas, mitigaciones ni disponibilidad por CI duplicada.
- [x] Añadir capacidad desde la hoja homónima sin afectar la bolsa de AF.
- [x] Representar la ocupación por filesystem y orientar los dos insumos de Novaventa.
- [x] Añadir selector, registro persistente, edición y eliminación segura de
  clientes personalizados desde el HTML offline.
- [x] Asociar cada cliente a una plantilla de validación y persistir su preset
  compatible de tarjetas en la ficha del cliente.
- [x] Simplificar el alta: evitar valores mensuales heredados, agrupar la
  selección de cliente con su administrador y mover el preset al selector de
  tarjetas posterior.
- [x] Compactar visualmente el administrador, añadir divulgación progresiva y
  conservar los campos y el foco al cambiar la plantilla de insumos.
- [x] Uniformar la botonera superior en una escala compacta y retirar la ayuda
  redundante de edición.
- [x] Añadir spec, autopruebas y pruebas de conformidad.
- [ ] Validar AF, comparar las cifras de junio con el informe de referencia y
  publicar la rama remota.
