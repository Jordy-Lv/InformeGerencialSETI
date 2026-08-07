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
- [x] Unificar la unidad de `PERFIL.metas` en `metaPerfil()`: fracción de 1,
  con `null` explícito distinto de clave omitida. Antes, `metas.backups` se
  leía como porcentaje mientras `metas.disponibilidad` se leía como fracción
  — Bancoldex (`0.95`) mostraba «Meta 0,95 %» y Novaventa (`null`) «Meta 0 %».
- [x] Aplicar el preset del perfil en cada arranque, no solo cuando hay uno
  guardado. Sin esto, un cliente abierto en un equipo limpio conservaba
  visibles las tarjetas que su perfil no selecciona —con el contenido de AF
  dentro, incluido el nombre de su anexo— y viajaban al HTML exportado.
- [x] Rotular la tabla de indicadores desde el consolidado del cliente. Antes
  las dos primeras celdas eran literales de AF: Bancoldex mostraba
  «Meta 99,30 %» en vez de 99,98 %. Verificado que AF no cambia.
- [x] Dimensionar el almacén de insumos por cliente: el prefijo declarado ya
  no se hereda de la plantilla. Dos clientes sobre Novaventa compartían base
  de datos y se pisaban los insumos. El borrado manual alcanza solo al
  cliente activo y la interfaz lo nombra.
- [ ] Validar AF, comparar las cifras de junio con el informe de referencia y
  publicar la rama remota. **Bloqueada:** requiere los insumos reales de
  junio-2026, que por diseño no están en el repo.
