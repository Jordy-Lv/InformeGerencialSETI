# Tareas — tarjetas faltantes de Bancoldex

## Lista cerrada de archivos

- `informe-accion-fiduciaria 1.html` (dos entradas nuevas en
  `INVENTARIO_TARJETAS`; bloques legado de `c13` y `c14`; `renderC13`,
  `renderC14`; extensión condicional de `renderC8m`; persistencia del trazo
  de firma en el almacén del cliente; clases CSS `.linea-base-control*` y
  `.firma*`)
- `perfiles/bancoldex.js` (`lineaBase.control`, `firmantes`,
  `fuentes.cualitativos.columnas.mitigaciones`, `tarjetas.seleccionadas`)
- `automatizacion/test_specs_inventario_tarjetas.py`
- `automatizacion/test_specs_perfil_cliente.py`
- `openspec/changes/2026-08-07-tarjetas-bancoldex/`
- `openspec/specs/inventario-tarjetas/spec.md`
- `openspec/specs/perfil-cliente/spec.md`
- `docs/2026-08-07-tarjetas-bancoldex.md`
- `TASKS.md`

**Colisión declarada.** `informe-accion-fiduciaria 1.html` y
`perfiles/bancoldex.js` los declara también
`2026-08-05-f7-bancoldex-aranda`, que sigue abierto. El motivo por el que se
continúa —y las dos alternativas descartadas con su comprobación— está en
`design.md`, «Decisión 0». Este change parte de `48ab8da`, que ya contiene
F7 completo.

## Implementación

### `c13` — Control de línea base

- [ ] Entrada `c13` en `INVENTARIO_TARJETAS` con `exportable:true`,
      `dominios:[]`, `fuentes:[]` (cifras declaradas, sin insumo).
- [ ] Bloque legado (tarjeta KPI + `.slideCard`) insertado tras el de `c3`.
- [ ] `renderC13()`: resumen base/actual/diferencia por categoría en la
      tarjeta; detalle por tipo de infraestructura en el modal.
- [ ] Signo y color de la diferencia: negativo en rojo, positivo en verde,
      cero neutro — como el entregable aprobado.
- [ ] `lineaBase.control` en `perfiles/bancoldex.js` con las cifras del PDF.
- [ ] `c13` añadida a `tarjetas.seleccionadas` de Bancoldex.

### `c14` — Firmas aprobadoras

- [ ] Entrada `c14` en `INVENTARIO_TARJETAS`, bloque legado al final.
- [ ] `renderC14()`: tres bloques con canvas, nombre y cargo.
- [ ] Trazo con eventos de puntero, sin librerías; botones borrar y rehacer.
- [ ] Persistencia del PNG en el almacén del cliente; se reutiliza al
      cambiar de periodo.
- [ ] Nombre y cargo editables desde la interfaz, persistidos.
- [ ] `firmantes` en `perfiles/bancoldex.js` como valor inicial.
- [ ] La firma sale embebida en base64 en el HTML exportado.

### `c8m` — Acciones y mejoras completa

- [ ] `fuentes.cualitativos.columnas.mitigaciones` en el perfil de Bancoldex.
- [ ] `renderC8m()` pinta responsable, fecha de entrega y observaciones
      **solo** si el perfil declara esas columnas.
- [ ] Anillo de avance con el `gauge()` existente, leyendo `ESTADO` como
      fracción.
- [ ] Sin perfil que las declare, el marcado es byte a byte el de hoy.

## Verificación

- [ ] `python3 -m unittest discover -s automatizacion -p 'test_*.py'` en verde.
- [ ] `python3 automatizacion/verificar_ab.py --autoprueba` OK.
- [ ] **A/B de Acción Fiduciaria en 0 diferencias** con los insumos reales de
      julio-2026, sobre el HTML exportado. Criterio de aceptación del change.
- [ ] `await REPORTE.autopruebas(archivos)` con los insumos reales de
      Bancoldex de junio-2026 — ejecutado de verdad en el navegador, no
      simulado en consola.
- [ ] Verificación **visual** en navegador de `c13` y `c14`: `innerText` no
      detecta desbordes ni solapamientos (lección del 07/08, `.gauge-exec`).
- [ ] Firma trazada, guardada, recargada tras cambiar de periodo y
      comprobada en el HTML exportado.

## Cierre

- [ ] `proposal.md`, `design.md` y este archivo reflejan lo implementado.
- [ ] Delta aplicado a `openspec/specs/inventario-tarjetas/spec.md` y
      `openspec/specs/perfil-cliente/spec.md`.
- [ ] `docs/2026-08-07-tarjetas-bancoldex.md` con `Contexto`, `Qué se
      implementó`, `Verificación realizada`, `Archivos tocados` y
      `Pendiente`, cada afirmación con su comando y su resultado real.
- [ ] `TASKS.md` actualizado.

## Pendientes registrados, fuera de este change

- [ ] **Doble columna `BANCOLDEX`/`SETI` en indicadores.** La hoja
      `Indicador` trae las dos series y el motor lee solo la del cliente.
      Hay meses donde difieren (100 % / 99,7 %; 99,34 % / 100 %). Hoy esa
      discrepancia no se ve en el informe.
- [ ] **Origen del 237/257 de la línea base.** El consolidado da 220/161.
      Mientras no se sepa qué proceso produce las cifras del PDF, `c13` las
      lleva declaradas en el perfil.
- [ ] **`Ejecución de Backups` como cuarta fila de `c4`.** Existe en la
      fuente. El usuario decidió que backups conserva su tarjeta propia
      (`c7`); no se retoma sin una decisión nueva.
