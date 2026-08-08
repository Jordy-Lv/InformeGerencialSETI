# Tareas — tarjetas faltantes de Bancoldex

## Lista cerrada de archivos

- `informe-accion-fiduciaria 1.html` (dos entradas nuevas en
  `INVENTARIO_TARJETAS`; bloques legado de `c3b` y `c14`; `renderC3b`,
  `renderC14`; extensión condicional de `renderC8m`; persistencia del trazo
  de firma en el almacén del cliente; clases CSS `.control-base*` y
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

### `c3b` — Control de línea base

- [x] Entrada `c3b` en `INVENTARIO_TARJETAS` con `exportable:true`,
      `dominios:[]`, `fuentes:[]` (cifras declaradas, sin insumo).
- [x] Bloque legado (tarjeta KPI + `.slideCard`) insertado tras el de `c3`.
- [x] `renderC3b()`: resumen base/actual/diferencia por categoría en la
      tarjeta; detalle por tipo de infraestructura en el modal.
- [x] Signo y color de la diferencia: negativo en rojo, positivo en verde,
      cero neutro — como el entregable aprobado.
- [x] `lineaBase.control` en `perfiles/bancoldex.js` con las cifras del PDF.
- [x] `c3b` añadida a `tarjetas.seleccionadas` de Bancoldex.

### `c14` — Firmas aprobadoras

- [x] Entrada `c14` en `INVENTARIO_TARJETAS`, bloque legado al final.
- [x] `renderC14()`: tres bloques con canvas, nombre y cargo.
- [x] Trazo con eventos de puntero, sin librerías; botones borrar y rehacer.
- [x] Persistencia del PNG en el almacén del cliente; se reutiliza al
      cambiar de periodo.
- [x] Nombre y cargo editables desde la interfaz, persistidos.
- [x] `firmantes` en `perfiles/bancoldex.js` como valor inicial.
- [x] La firma sale embebida en base64 en el HTML exportado.

### `c8m` — Acciones y mejoras completa

- [x] `fuentes.cualitativos.columnas.mitigaciones` en el perfil de Bancoldex.
- [x] `renderC8m()` pinta responsable, fecha de entrega y observaciones
      **solo** si el perfil declara esas columnas.
- [x] Anillo de avance con el `gauge()` existente, leyendo `ESTADO` como
      fracción.
- [x] Sin perfil que las declare, el marcado es byte a byte el de hoy.

## Verificación

- [x] `python3 -m unittest discover -s automatizacion -p 'test_*.py'` en verde
      (140 pruebas).
- [x] **El HTML exportado responde al clic**, comprobado abriendo el
      entregable de los dos perfiles con una sonda de `window.onerror`: AF
      9/10 tarjetas y Bancoldex 8/8, cero errores. El A/B no cubre esto.
- [x] `python3 automatizacion/verificar_ab.py --autoprueba` OK.
- [x] **A/B de Acción Fiduciaria en 0 diferencias** con los insumos reales de
      julio-2026, sobre el HTML exportado. Criterio de aceptación del change.
- [x] `await REPORTE.autopruebas()` con los insumos reales de
      Bancoldex de junio-2026 — ejecutado de verdad en el navegador, no
      simulado en consola. Con AF: **31/31 PASA**. Con Bancoldex: 29/31, los
      dos fallos preexistentes porque la suite tiene el cliente escrito a
      mano (`'accion-fiduciaria'` y `length===10`) — ver el documento de
      sesión, «Pendiente».
- [x] Verificación **visual** en navegador de `c3b` y `c14`: `innerText` no
      detecta desbordes ni solapamientos (lección del 07/08, `.gauge-exec`).
- [x] Firma trazada, guardada, recargada tras cambiar de periodo y
      comprobada en el HTML exportado.

## Cierre

- [x] `proposal.md`, `design.md` y este archivo reflejan lo implementado.
- [x] Delta aplicado a `openspec/specs/inventario-tarjetas/spec.md` y
      `openspec/specs/perfil-cliente/spec.md`.
- [x] `docs/2026-08-07-tarjetas-bancoldex.md` con `Contexto`, `Qué se
      implementó`, `Verificación realizada`, `Archivos tocados` y
      `Pendiente`, cada afirmación con su comando y su resultado real.
- [x] `TASKS.md` actualizado.

## Pendientes registrados, fuera de este change

- [ ] **Doble columna `BANCOLDEX`/`SETI` en indicadores.** La hoja
      `Indicador` trae las dos series y el motor lee solo la del cliente.
      Hay meses donde difieren (100 % / 99,7 %; 99,34 % / 100 %). Hoy esa
      discrepancia no se ve en el informe.
- [ ] **Origen del 237/257 de la línea base.** El consolidado da 220/161.
      Mientras no se sepa qué proceso produce las cifras del PDF, `c3b` las
      lleva declaradas en el perfil.
- [ ] **`Ejecución de Backups` como cuarta fila de `c4`.** Existe en la
      fuente. El usuario decidió que backups conserva su tarjeta propia
      (`c7`); no se retoma sin una decisión nueva.

## Ajuste del 07/08/2026 (tarde): sección propia para las firmas

- [x] Rótulo «04 · Aprobación del informe» delante de `c14`, con
      `data-tarjetas` para que solo lo vea el perfil que la selecciona.
- [x] `aplicarPresetTarjetas()` oculta los rótulos condicionales sin sus
      tarjetas; `podarClon()` los elimina del entregable.
- [x] Regla CSS `[hidden]{display:none}` para el rótulo: `display:flex`
      ganaba y la sección se veía igual con el atributo puesto.
- [x] `c14` pasa a formato compacto (sin `dash-grid--full`), que era lo que
      solapaba la etiqueta con el valor.
- [x] Delta aplicado a `openspec/specs/inventario-tarjetas/spec.md`.
- [x] 146 pruebas en verde y **A/B de Acción Fiduciaria en 0 diferencias**
      contra `main` (`2a9e79f`), con los insumos reales de julio-2026.
- [x] Verificado en navegador con Bancoldex: la sección aparece y la tarjeta
      ya no se solapa. Con Acción Fiduciaria el rótulo no se pinta ni viaja
      en su entregable.
