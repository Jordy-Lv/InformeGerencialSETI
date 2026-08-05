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

- Generar una exportación completa de `main` y otra de F3 con el mismo
  paquete de insumos e insumos manuales reales, y comprobar
  `automatizacion/verificar_ab.py` con resultado de `0 diferencias`.
- Solo después de ese A/B se marca F3 como completa y se inicia F4, que
  generará el HTML desde este inventario y añadirá el preset editable.
