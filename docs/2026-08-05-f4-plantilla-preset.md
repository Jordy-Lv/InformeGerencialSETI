# F4 — Plantilla de tarjetas y preset persistido

**Fecha:** 5 de agosto de 2026

## Contexto

F3 dejó el inventario como fuente de verdad de las diez tarjetas de Acción
Fiduciaria, pero el panel todavía repetía a mano las envolturas de cada una.
Además, el informe no permitía adaptar temporalmente la composición sin
editar el HTML o el perfil entregado.

## Qué se implementó

- Cada descriptor ahora declara la presentación de su resumen; una plantilla
  única reconstruye las diez tarjetas del panel y conserva sus `slideCard` y
  `slide` legado como destinos de parsers y PDF.
- El botón **Tarjetas** abre un selector accesible. Muestra criterios que
  dejarían de exigirse, evita una selección vacía y deja preparada la regla de
  dependencias declarativas.
- La interfaz del selector presenta cada tarjeta como una opción editorial con
  estado, numeración, contador de selección y un resumen visible del impacto
  de la decisión; conserva foco contenido y fondo inerte mientras está abierto.
- El override se guarda por perfil como
  `informe:<perfil>:preset-tarjetas`. Un JSON vacío, repetido o desconocido se
  descarta sin impedir el inicio.
- La selección efectiva controla tarjetas visibles, criterios activos y las
  páginas exportables del PDF. El HTML exportado transporta esa selección en
  el perfil resuelto; su modal de autoría se elimina del archivo cliente.
- El store conserva los dominios completos del preset entregado, de modo que
  ocultar una tarjeta no rompe destinos de carga ni parsers.

## Verificación realizada

- Comprobación de sintaxis de los diez bloques internos con `node --check`
  → `Bloques internos válidos: 10`.
- `python3 -m unittest automatizacion/test_specs_inventario_tarjetas.py -v`
  → `Ran 9 tests ... OK`.
- `python3 -m unittest discover -s automatizacion -p 'test_*.py' -v`
  → `Ran 49 tests ... OK`.
- `git diff --check` → código 0.

## Archivos tocados

- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_inventario_tarjetas.py`
- `automatizacion/test_specs_store_reporte.py`
- `openspec/changes/2026-08-05-f4-plantilla-preset/`
- `openspec/specs/inventario-tarjetas/spec.md`
- `openspec/specs/preset-tarjetas/spec.md`
- `openspec/specs/README.md`
- `docs/2026-08-05-f4-plantilla-preset.md`
- `docs/2026-08-04-plan-multicliente.md`

## Pendiente

- Repetir la suite completa tras el ajuste estático y obtener `0` diferencias
  A/B contra `main` con el preset predeterminado y los mismos insumos reales.
- Hacer la comprobación visual manual del preset mínimo y máximo, incluido el
  PDF, porque la captura depende de las dimensiones reales del navegador.
