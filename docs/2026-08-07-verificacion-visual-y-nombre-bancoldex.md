# Verificación visual del modal de casos y grafía «Bancoldex»

Continuación directa de
[`docs/2026-08-07-correccion-modal-casos-aranda.md`](2026-08-07-correccion-modal-casos-aranda.md),
que dejó dos cosas pendientes. Esta sesión cierra la primera y atiende una
corrección nueva pedida por el usuario.

## 1. El cliente se escribe «Bancoldex», sin tilde

El usuario corrigió la grafía: **no es «Bancóldex»**. Se sustituyó
`Bancóldex` → `Bancoldex` y `BANCÓLDEX` → `BANCOLDEX` en **232 ocurrencias
repartidas en 28 archivos** del repositorio.

Lo que cambia de verdad en el entregable son las cadenas visibles de
`perfiles/bancoldex.js`:

| Clave | Antes | Ahora |
|---|---|---|
| `nombre` | `Bancóldex` | `Bancoldex` |
| `textos.tituloDocumento` | `Informe Gerencial · Bancóldex` | `Informe Gerencial · Bancoldex` |
| `textos.marcaTopbar` | `Informe Bancóldex` | `Informe Bancoldex` |
| `textos.clienteHero` | `BANCÓLDEX` | `BANCOLDEX` |
| `textos.confidencialidad` | `…preparado por SETI para Bancóldex.` | `…para Bancoldex.` |

El resto son comentarios del HTML, el placeholder «Ej. Bancoldex» del
formulario de clientes, specs, `tasks.md`, docs y comentarios de las pruebas
de Python. Se renombraron también para que una búsqueda por el nombre
encuentre todo, incluido `docs/archivo/`.

Quedaron **fuera del renombrado a propósito**: `.git/`,
`.claude/worktrees/` (copia de trabajo de otra rama) y `_tmp_main_ab/`
(residuo de una verificación A/B, ya marcado como higiene pendiente).

La regla, con su porqué y su comprobación, quedó como referencia normativa en
`openspec/changes/2026-08-05-f7-bancoldex-aranda/design.md`, sección **«El
cliente se escribe "Bancoldex", sin tilde»**. Comprobación:

```bash
grep -rn "Banc[óÓ]ldex" --include="*" . | grep -v '^./.git/' | grep -v '/worktrees/' | grep -v '_tmp_main_ab'
```

**Pendiente, fuera del alcance del repositorio:** si el usuario ya creó un
cliente por la interfaz escribiendo el nombre con tilde, ese nombre vive en
su `localStorage` y el renombrado no lo alcanza. Se corrige desde «Editar
datos».

## 2. Verificación visual del modal de casos (pendiente #1, ahora cerrado)

La sesión anterior sólo pudo confirmar el modal por `innerText` del DOM. Esta
vez se abrió de verdad, con los insumos reales de junio-2026
(`Bancoldex/Casos  + tareas BD junio 2026.xlsx`, servido por
`python3 -m http.server` sólo para que el navegador de prueba ejecute JS — la
aplicación sigue siendo `file://`).

Lo que se ve, y coincide con lo especificado:

- Panel **«Incidentes atribuibles a SETI»** con el título literal y **un solo
  badge** («2» / «1 de 2 incidentes fuera del SLA»). Sin SLA dentro, sin
  badges extra — como pidió el usuario.
- Panel **«Cumplimiento del SLA»** aparte, con el gauge circular en
  **98,6 %** («71 de 72 casos dentro del acuerdo»).
- Grilla de 3 columnas: SLA · «Casos por tipo» (33 Incidente - Monitoreo,
  32 Requerimiento, 5 Tarea, 2 Incidente) · «Casos por motor» (52 Oracle,
  19 SQL Server, 1 Weblogic).
- Cabecera roja con los 72 casos registrados y «Requerimientos por categoría»
  más abajo.

### Defecto que sólo se veía mirando

El rótulo del gauge, **«Cumplimiento SLA · meta 100%», cruzaba el anillo de
color por ambos costados**. `.gauge-exec` es un grid de 150 × 150 px con
`place-content:center` y sin padding, así que el `<span>` se estiraba a los
150 px completos. El componente existía en el motor desde antes pero nunca se
había renderizado, así que nadie lo había visto.

Corrección: `padding:0 26px` en `.gauge-exec`, que confina el texto al
círculo blanco interior (`:before` con `inset:10px`, radio 65 px). Medido en
navegador después del cambio: la esquina de texto más lejana queda a
**55,7 px** del centro — dentro del radio. Cubierto por
`test_gauge_exec_reserva_espacio_lateral_para_el_rotulo`.

No toca a Acción Fiduciaria: `gauge()` sólo se invoca desde la rama
`aranda-tipo-motor` de `renderC5()`, no hay ningún otro consumidor de
`.gauge-exec`.

**Lo que hay que llevarse de esto:** confirmar el DOM por `innerText` no
sustituye mirar la pantalla. Las cifras estaban bien desde la sesión
anterior; lo que estaba mal era invisible por texto.

## Verificación ejecutada

```
python3 -m unittest discover -s automatizacion -p 'test_*.py'
Ran 97 tests in 0.665s
OK

python3 automatizacion/verificar_ab.py --autoprueba
[OK] Fixtures idénticos -> 0 diferencias.
[OK] Cambio introducido a propósito ('54 casos' -> '999 casos') detectado: 3 diferencia(s).
[OK] Elemento extra en B detectado: 3 diferencia(s).
Autoprueba OK.
```

**El A/B contra `main` con exports reales de Acción Fiduciaria sigue sin
correrse** — es el mismo bloqueo de siempre (no hay insumos reales de AF de
junio-2026 en el repo, por diseño) y no se resolvió aquí. El argumento de que
esta sesión no puede afectar a AF es de inspección, no de A/B: el renombrado
sólo toca cadenas del perfil de Bancoldex y comentarios, y el cambio de CSS
afecta una clase sin consumidores fuera de la rama Aranda.

## Sigue pendiente

1. **Definir con el usuario cómo se valida qué incidentes de Aranda son
   «atribuibles a SETI».** Hoy usa `incidentesReales` (categoría `Incidente`
   excluyendo `Incidente - Monitoreo`) como cifra provisional, sin ningún
   cruce de atribución equivalente al log de indisponibilidades de GLPI. El
   usuario pidió explícitamente no avanzar sin acordarlo. Es el pendiente
   real de F7.
2. A/B de Acción Fiduciaria con insumos reales de junio — bloquea el cierre
   de F6 y, con él, la fusión.
3. Publicar rama/PR: decisión del usuario.
