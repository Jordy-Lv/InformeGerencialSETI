# El HTML exportado salía sin interactividad (PR #18)

**Fecha:** 7 de agosto de 2026 (noche).
**Rama:** `codex/f6-perfil-novaventa` — la del PR #18.

## Contexto

Al revisar si el PR #18 estaba listo para fusionar, antes de pedirle revisión
a alguien más, apareció un defecto que ninguna de las verificaciones del
change podía ver: **el HTML exportado por esta rama se generaba y se veía
correcto, pero no respondía a ningún clic.**

Tres de los cuatro defectos son **preexistentes** —vienen de F3 y F4, ya
contenidas en esta rama— y uno de ellos rompía también el entregable de
**Acción Fiduciaria**, que está en producción. Los entregables de `main` no
están afectados: el defecto aparece al generar la tarjeta desde el inventario,
que es lo que introdujo F3.

El arnés A/B no podía delatarlo, y eso es lo importante de este hallazgo:
**compara texto visible y estado publicado, no atributos ni listeners.** Un
entregable inerte le pasa por delante con 0 diferencias.

## Qué se implementó

Los cinco cambios en `informe-accion-fiduciaria 1.html`:

1. **`resolverPerfil()` devuelve el perfil embebido tal cual.** El perfil que
   viaja en el entregable ya está resuelto —`codigoEstadoCliente()` serializa
   `perfilEfectivo()`—, pero conserva `extiende` como dato informativo, así
   que se volvía a resolver y buscaba `window.PERFIL_BASE`, que el entregable
   no lleva porque `podarClon()` elimina los `<script>` de perfiles para que
   el HTML abra solo. El `throw` rompía el arranque entero. Afectaba a los
   perfiles con herencia: **Bancoldex** y **Novaventa**.
2. **`actualizarResumen()` tolera que no exista `#loadSummary`.** El panel de
   carga es de autoría y el podado lo elimina, pero `restaurarPresetTarjetas()`
   alcanza esa función al abrir el entregable. **Rompía también a Acción
   Fiduciaria, desde F4.**
3. **La tarjeta generada recupera el `onclick` inline.** `activarModales()`
   engancha con `btn.onclick=fn`, que es una *propiedad* y no se serializa: el
   entregable se genera clonando el DOM, y un clon solo conserva atributos. El
   HTML legado sí traía el atributo; al pasar a generar la tarjeta desde el
   inventario se perdió. **Desde F3.**
4. **`pintarCI()` tolera que no exista `#tbodyCI`.** Esa tabla vive en `c11`,
   que un perfil puede no seleccionar.
5. **`podarClon()` deja de arrastrar el `#dashboardModal` de autoría**, que
   duplicaba ese `id` en el entregable. Devuelve antes su contenido a la
   tarjeta, porque `openDashboard()` *mueve* el panel al modal y exportar con
   una tarjeta abierta lo habría borrado del entregable.

## Verificación realizada

Todo lo de abajo se ejecutó en esta sesión; nada se da por bueno por analogía
con otra rama.

**Pruebas y sintaxis**

```
python3 -m unittest discover -s automatizacion -p 'test_*.py'
Ran 131 tests in 0.808s — OK          (126 antes, 5 nuevas)

node --check sobre los 9 bloques <script> inline → 9 OK, 0 con error

python3 automatizacion/verificar_ab.py --autoprueba
Autoprueba OK: el arnés distingue 'igual' de 'distinto' en los tres casos.
```

**A/B con exports reales de Acción Fiduciaria**

Dos exports generados en la misma sesión con el mismo estado de entrada —los
insumos reales de julio-2026 de `Accion Fiduciaria/`, `listo: true` en ambos—,
uno desde `main` (`cf50713`) y otro desde esta rama:

```
python3 automatizacion/verificar_ab.py export-main.html export-pr18.html
0 diferencias entre export-main.html y export-pr18.html.
```

**El entregable, abierto de verdad**

No basta con el DOM de autoría: el defecto solo se ve en el HTML exportado.
Abriendo `export-pr18.html` y haciendo clic en cada tarjeta:

| | export de la rama | export de `main` (control) |
|---|---|---|
| Tarjetas | 10 | 10 |
| Con `onclick` inline | 10 | 10 |
| Abren su panel | 9 | 9 |
| `#dashboardModal` en el DOM | 1 | 1 |
| `#loadPanel` | ausente | ausente |

La décima es `c12`, que no declara renderizador — se comporta igual en `main`,
así que no es una regresión de esta rama. Sin errores de JavaScript en ninguno
de los dos: los únicos 404 son los de `insumos-af.js`, preexistentes en `main`
y ya anotados como hallazgo abierto.

## Archivos tocados

- `informe-accion-fiduciaria 1.html` — los cinco cambios de arriba.
- `automatizacion/test_specs_inventario_tarjetas.py` — 5 pruebas nuevas
  (`TestEntregableInteractivo`).
- `openspec/specs/inventario-tarjetas/spec.md` y
  `openspec/changes/2026-08-05-f7-bancoldex-aranda/specs/inventario-tarjetas/spec.md`
  — requisito nuevo «el entregable exportado conserva la interacción», escrito
  antes que el código.
- `openspec/changes/2026-08-05-f7-bancoldex-aranda/tasks.md` — ampliación.

Se declara dentro del change de F7 y no en uno nuevo porque F7 es el único
change abierto de esta rama que declara `informe-accion-fiduciaria 1.html`, y
abrir otro lo declararía dos veces (`openspec/AGENTS.md`).

## Pendiente

- **El export sigue arrastrando `<script src="insumos-af.js">`**, que en el
  equipo del cliente da 404. Es preexistente en `main` y ya estaba anotado; no
  se corrige aquí para no ampliar el alcance de un PR que ya es grande.
- Las 5 pruebas nuevas verifican el HTML por texto, como el resto de las
  `test_specs_*`. Comprueban que el arreglo está escrito, no que el entregable
  abre — eso se verificó a mano, en el navegador, y queda registrado arriba.
