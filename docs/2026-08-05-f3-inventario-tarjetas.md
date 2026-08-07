# F3 — Inventario declarativo de tarjetas

**Fecha:** 5 de agosto de 2026

## Contexto

Las diez tarjetas del informe de Acción Fiduciaria estaban presentes en el
HTML, pero su información operativa se repartía entre listas independientes
de dominios, extensiones admitidas, criterios de carga y llamadas a los
renderizadores. Esa duplicación impedía comprobar que una configuración
describiera exactamente la interfaz que F4 deberá generar.

## Qué se implementó

- `PERFIL.tarjetas.seleccionadas` declara el orden de las diez tarjetas:
  `c3`, `c4`, `c5`, `c6`, `c7`, `c8`, `c8m`, `c9`, `c11` y `c12`.
- `INVENTARIO_TARJETAS` registra para cada una su nodo de tarjeta y
  diapositiva legado, dominios, fuentes, exportabilidad, criterios y, cuando
  aplica, el renderizador nombrado.
- La resolución del perfil rechaza listas vacías, ids repetidos y tarjetas
  desconocidas. El perfil continúa siendo un objeto de datos puros.
- `DOMINIOS`, `EXTENSIONES_INSUMO`, `criteriosCarga()` y `renderAll()` se
  derivan del inventario; los siete criterios preservan sus textos y orden.
- `REPORTE.autopruebas()` verifica que las diez tarjetas declaradas tienen
  tarjeta y diapositiva en el DOM legado, y que se resuelven siete criterios.
- Se añadió la capacidad `inventario-tarjetas` con delta OpenSpec y pruebas
  de conformidad estática. La prueba existente del store deja de exigir una
  segunda lista literal de dominios.

## Verificación realizada

- `python3 -m unittest automatizacion/test_specs_inventario_tarjetas.py automatizacion/test_specs_store_reporte.py -v` → `Ran 15 tests ... OK`.
- `python3 -m unittest discover -s automatizacion -p 'test_*.py' -v` → `Ran 47 tests ... OK`.
- La comprobación de sintaxis de los nueve bloques internos del HTML con
  `node --check` → `Bloques internos válidos: 9`.
- `git diff --check` → código 0.
- Se intentó abrir el HTML local para validación interactiva en el navegador
  integrado, pero la política del entorno bloquea rutas `file://`. No se usó
  una alternativa que eludiera esa restricción.
- `python3 automatizacion/verificar_ab.py '/Users/yordypardopajaro/Downloads/Otros/export-main-f3.html' '/Users/yordypardopajaro/Downloads/Otros/export-f3.html'`
  → `0 diferencias entre export-main-f3.html y export-f3.html.` Ambas
  exportaciones se produjeron el 5 de agosto de 2026 con los mismos insumos
  reales completos; `export-f3.html` contiene `INVENTARIO_TARJETAS` y la
  exportación de `main` no, como corresponde a cada versión.

## Archivos tocados

- `perfiles/accion-fiduciaria.js`
- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_inventario_tarjetas.py`
- `automatizacion/test_specs_store_reporte.py`
- `openspec/changes/2026-08-05-f3-inventario-tarjetas/`
- `openspec/specs/inventario-tarjetas/spec.md`
- `openspec/specs/store-reporte/spec.md`
- `openspec/specs/README.md`
- `docs/2026-08-05-f3-inventario-tarjetas.md`
- `docs/2026-08-04-plan-multicliente.md`

## Pendiente

- F3 está cerrada. La siguiente fase, F4, reemplazará el HTML legado de las
  tarjetas por la plantilla única del inventario y añadirá el preset editable.
