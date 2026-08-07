# Tareas activas

Solo lo vigente: qué está en curso, qué bloquea y el siguiente paso. Para el
histórico completo de fases fusionadas, ver [`CHANGELOG.md`](CHANGELOG.md).
Para la arquitectura objetivo (qué es cada fase y su criterio de
aceptación), ver [`docs/arquitectura-multicliente.md`](docs/arquitectura-multicliente.md).

> **Este archivo se actualiza siempre, no solo a veces.** Al terminar
> cualquier tarea, refleja el resultado aquí antes de cerrar la sesión. Al
> descubrir un bloqueo, una pregunta abierta o un pendiente que no estaba
> anotado, agrégalo aquí en el momento — no lo dejes para "recordarlo
> después". Un `TASKS.md` desactualizado es peor que no tenerlo: alguien
> confía en él y decide con información vieja. Detalle completo en
> `openspec/AGENTS.md` §«Al terminar», punto 4.

**Regla operativa** (`openspec/AGENTS.md`): dos `changes` abiertos no pueden
declarar el mismo archivo en su `tasks.md`. Revisa `openspec/changes/`
(excluye `archivo/`) antes de tocar código.

Última verificación de este archivo contra git: **07/08/2026 (cierre)** — PR #18,
Bancoldex cerrado y A/B de AF en 0, ver «Cierre del 07/08/2026» más abajo.

**El cliente se escribe «Bancoldex», sin tilde.** Corregido en todo el
repositorio el 07/08/2026 (232 ocurrencias, 28 archivos). La regla y su
comprobación están en `openspec/changes/2026-08-05-f7-bancoldex-aranda/design.md`.
No reintroducir `Bancóldex`.

---

## Estado por fase

Verificado con `git merge-base --is-ancestor` y `git rev-list`, no por
lectura de docs. **F2–F7 están en `main`** desde el PR #18 (`2e5a2af`,
07/08/2026); sus ramas de trabajo se borraron ya fusionadas.

| Fase | Dónde | Estado verificado |
|---|---|---|
| F0 — fundación (OpenSpec, arnés A/B, dorados) | `main` | **Abierta.** Falta `dorados/accion-fiduciaria-2026-06.json`. Sin esa evidencia F0 no cierra formalmente |
| F1 — perfil de cliente como datos puros | `main` | **Cerrada.** PR #12 (`404408c`), A/B julio-2026 en 0 |
| F2 — contrato desacoplado del DOM | `main` | **Cerrada** (7/7), vía PR #18 |
| F3 — inventario de tarjetas | `main` | **Cerrada** (6/6), vía PR #18 |
| F4 — plantilla y preset de tarjetas | `main` | **Cerrada** (10/10), vía PR #18 |
| F5 — adaptadores y modelo canónico | `main` | **Cerrada** (8/8), vía PR #18 |
| F6 — perfil Novaventa + registro de clientes | `main` | **Cerrada el 07/08/2026.** A/B de AF en 0 con los insumos reales de julio-2026 |
| F7 — adaptador Aranda + perfil Bancoldex | `main` | **Cerrada.** Casos (Aranda) y AlertsList portados el 06/08 — ver [`docs/2026-08-06-aranda-alertslist-bancoldex.md`](docs/2026-08-06-aranda-alertslist-bancoldex.md). El resto (indicadores/backups/disponibilidad/lineaBase) ya venía de F6. La línea histórica quedó en el tag `historico/bancoldex-completo`, no se mergea |
| F8 — automatización multicliente | — | No iniciada |
| F9 — reglas compartidas JS↔Python | — | No iniciada |
| F10 — split `fuente/` (opcional) | — | No iniciada |

La sección «Bloqueo principal» que sigue es **histórica**: describe la
divergencia entre las dos líneas de Bancoldex, resuelta al cerrar F7. Se
conserva porque explica por qué el HTML quedó como quedó.

---

## Bloqueo principal: dos líneas paralelas de Bancoldex

`codex/f6-perfil-novaventa` y `codex/bancoldex-completo` nacen ambas de F5
(`db3d368`) y construyeron Bancoldex por separado. La fusión da **5 archivos
en conflicto / 31 bloques** (20 de ellos en el HTML).

El análisis completo, bloque por bloque, está en
[`docs/2026-08-06-divergencia-bancoldex.md`](docs/2026-08-06-divergencia-bancoldex.md).
En resumen:

- **No son rivales, son complementarias.** F6 aporta el administrador de
  clientes por interfaz (registro persistente, `seleccionable:false`,
  capacidad, alertas alternativas); `bancoldex-completo` aporta el adaptador
  de Aranda y el renderizador de casos (c5) que F6 documenta como «no
  portado todavía» en la cabecera de `perfiles/bancoldex.js`.
- 4 de las 5 funciones que ambas ramas crean con el mismo nombre son
  **idénticas byte a byte**. El solapamiento real es mucho menor de lo que
  sugiere el conteo de conflictos.
- **Hay un defecto de cifras que decide varios conflictos.** `PERFIL.metas`
  se declara en fracción (`0.95`), y así lo lee `disponibilidad` en las dos
  ramas. Pero `backups` en `codex/f6-perfil-novaventa` lo lee como
  porcentaje:

  | Perfil | `codex/f6-perfil-novaventa` | `codex/bancoldex-completo` |
  |---|---|---|
  | AF (no declara) | Meta 99,3 % | Meta 99,3 % |
  | Bancoldex (`0.95`) | **Meta 0,95 %** ✗ | Meta 95 % ✓ |
  | Novaventa (`null`) | **Meta 0 %** ✗ | sin meta (oculta) ✓ |

  Ambos perfiles seleccionan `c7`, así que las dos cifras son visibles. AF
  no se ve afectado (no declara `backups`), y por eso su A/B pasó en 0 sin
  delatarlo.

  **Corregido el 06/08/2026 en la rama de F6**: la conversión se unificó en
  `metaPerfil()` y el delta de spec quedó escrito. Ver
  [`docs/2026-08-06-unidad-metas-perfil.md`](docs/2026-08-06-unidad-metas-perfil.md).
  El defecto simétrico de `codex/bancoldex-completo` (§3.2 del análisis)
  sigue abierto y le corresponde al change de F7.

**Actualización, misma tarde del 06/08/2026:** el punto anterior de la lista
("el adaptador de Aranda y el renderizador de casos que F6 documenta como
«no portado todavía»") ya no aplica — se portó directamente a F6, a pedido
del usuario, junto con AlertsList para Bancoldex. Ver
[`docs/2026-08-06-aranda-alertslist-bancoldex.md`](docs/2026-08-06-aranda-alertslist-bancoldex.md).
Esto reduce el área de la divergencia (ya no compite por el bloque de casos/
c5 del HTML) pero **no la cierra**: los bloques 3, 7, 8–9 y 17 (decisiones de
diseño sobre `?perfil=`, dominios del consolidado y guards de
`cargarConsolidado`) siguen sin resolver y le corresponden al change de F7.

---

## Hallazgos del end-to-end de Bancoldex (06/08/2026)

Carga completa con los insumos reales de junio-2026, hasta el HTML
exportado. Las cifras cuadran (indicadores, backups 11/11, 5 logros, 2
mitigaciones, exportación habilitada), pero el entregable sale con contenido
de Acción Fiduciaria. Detalle y evidencia en
[`docs/2026-08-06-e2e-bancoldex.md`](docs/2026-08-06-e2e-bancoldex.md).

1. ~~El preset del perfil no se aplica en una sesión limpia~~ —
   **corregido el 06/08**.
2. ~~La tabla de indicadores conserva las metas de AF~~ — **corregido el
   06/08**. Era el bloque 12 del análisis de divergencia; se comprobó contra
   el consolidado real de AF que sus rótulos y metas no cambian.
3. **El export arrastra `<script src="insumos-af.js">`** — abierto. Menor, y
   preexistente en `main`.

Además se corrigió un cuarto defecto, hallado al revisar la persistencia:
**los insumos guardados se compartían entre clientes** (el prefijo de
IndexedDB se heredaba de la plantilla, así que dos clientes sobre Novaventa
se pisaban los archivos). Ahora cada cliente tiene su almacén y el borrado
alcanza solo al cliente activo. Ver
[`docs/2026-08-06-correcciones-multicliente.md`](docs/2026-08-06-correcciones-multicliente.md).

Un quinto defecto, hallado al portar Aranda/AlertsList (mismo día, sesión
posterior): **`cargarInsumosAutomaticos()` no tenía guard por perfil** — con
`insumos-af.js` (dev local, de Acción Fiduciaria) presente junto al HTML, el
periodo de Bancoldex saltaba a julio sin acción del usuario. **Corregido.**
Ver [`docs/2026-08-06-aranda-alertslist-bancoldex.md`](docs/2026-08-06-aranda-alertslist-bancoldex.md).

## Sesión del 07/08/2026

Cerrado el pendiente de verificación visual del modal de casos (`c5`) de
Bancoldex: se abrió de verdad con los insumos reales de junio-2026 y la
estructura y las cifras son correctas («Incidentes atribuibles a SETI» con un
solo badge, panel de SLA aparte con gauge en 98,6 %, 72 casos). Mirarlo
destapó un defecto que la inspección por `innerText` no podía ver — el rótulo
del gauge cruzaba el anillo de color — corregido con `padding:0 26px` en
`.gauge-exec` y cubierto por prueba. Detalle en
[`docs/2026-08-07-verificacion-visual-y-nombre-bancoldex.md`](docs/2026-08-07-verificacion-visual-y-nombre-bancoldex.md).

**Tarde del 07/08:** el usuario reportó tres defectos del Centro de carga de
Bancoldex, los tres corregidos y verificados en navegador con los insumos
reales de junio-2026 — ver
[`docs/2026-08-07-correccion-insumos-bancoldex.md`](docs/2026-08-07-correccion-insumos-bancoldex.md):

1. `cargarCasos()` (hoja «Casos» del consolidado, modelo de AF) corría también
   para Bancoldex y pisaba los `datasets` de Aranda: o corrompía las cifras en
   silencio, o lanzaba un `TypeError` que abortaba `cargarConsolidado()`
   entero y **bloqueaba la exportación**. Guard por `PERFIL.fuentes?.casos`.
2. La entrada de Mitigaciones rechazaba el libro del propio cliente («Usa .»,
   lista vacía). Dos capas: `c8m: {fuentes: ['logros']}` en el perfil, y
   `EXTENSIONES_INSUMO` congelado al parsear. Lo segundo es del motor, no de
   Bancoldex: afecta a cualquier tarjeta agregada por la UI.
3. El libro de logros/mitigaciones había que cargarlo dos veces; ahora
   cualquiera de las dos entradas marca los dos insumos, como ya hacía AF.

4. Un insumo **restaurado** desde IndexedDB no se releía al cambiar el
   periodo: la restauración no depositaba el archivo en su `<input>` y la
   revalidación recorre los `<input>`. El export de Aranda se quedaba en «0
   casos de jul-26» con el selector en Junio.
5. El recuento de insumos obligatorios dejaba a Aranda fuera. **Alcance
   definido por el usuario: para Bancoldex AlertsList sí cuenta; lo que no
   aplica es GLPI, al que reemplaza Aranda.**

**Resuelto en la misma tarde, no era un bug:** el `alertops-2026-07.csv`
original no traía filas de Bancoldex. El usuario cargó
`Bancoldex/AlertsList-2.csv` (202 filas) y volvió a ver 0 alertas en junio —
pero ese archivo tampoco tiene ninguna fila de junio (rango real:
9/jul–7/ago/2026). El filtro sí reconoce a Bancoldex: 202/212 filas, y con
periodo Julio da 153 alertas, exacto contra el conteo directo del CSV.

**Un hallazgo quedó abierto a propósito:** el texto de `c3` («Oracle · SQL
Server») se desborda 70 px sobre la columna vecina — es una clase compartida
con AF, que está en producción, así que va con decisión del usuario y A/B.

**Sigue pendiente de F7, sin resolver:** definir con el usuario cómo se valida
qué incidentes de Aranda son «atribuibles a SETI». Hoy usa una cifra
provisional (categoría `Incidente` excluyendo monitoreo) sin ningún cruce de
atribución real. **No avanzar sin acordarlo primero.**

## Cierre del 07/08/2026 (noche): Bancoldex terminado y A/B en 0

Detalle en [`docs/2026-08-07-cierre-bancoldex.md`](docs/2026-08-07-cierre-bancoldex.md).

1. **Atribución a SETI (decisión del usuario):** Bancoldex muestra **0**
   incidentes atribuibles a SETI, con el apartado visible y en estado
   favorable, hasta que exista una fuente que acredite la atribución. Se
   declara en el perfil (`reglas: {atribucionSeti: 'sin-fuente'}`); el
   default no toca a AF ni a Novaventa. Antes se mostraba una aproximación
   (categoría `Incidente` sin monitoreo) que el informe presentaba como
   atribución confirmada.
2. **Desborde de `c3` (decisión del usuario: solo Bancoldex):** mecanismo
   nuevo `tarjetas.presentacion.<id>.modificadores` →
   `tarjeta-kpi--valores-largos`. La clase compartida con AF, que está en
   producción, no se toca.
3. **A/B de Acción Fiduciaria: 0 diferencias.** Con los insumos reales de
   julio-2026 de `Accion Fiduciaria/`. La primera corrida dio 11: diez eran
   estado de entrada desigual (`insumos-af.js`, ignorado por git, está en el
   repo y no en el worktree de `main`) y **una era un defecto real** —
   `metaPerfil()` formateaba con `pct()`, que redondea a entero, y la meta de
   backups de AF pasaba de «99,3%» a «99%». Corregido con `metaTexto()`.
4. **Los bloques 7, 8–9 y 17 de la divergencia ya estaban resueltos** en esta
   rama (verificado contra el HTML, no contra los docs). El bloque 3
   (`?perfil=`) se descarta: `cambiarClienteActivo` cubre lo mismo. **No
   queda nada por portar de `codex/bancoldex-completo`.**

## Sesión del 07/08/2026 (noche): F7 commiteada y tarjetas nuevas

Detalle en [`docs/2026-08-07-tarjetas-bancoldex.md`](docs/2026-08-07-tarjetas-bancoldex.md).

1. **F7 estaba sin commitear.** Todo el trabajo del 06 y 07 de agosto vivía
   en el árbol sin guardar: el change `2026-08-05-f7-bancoldex-aranda` sin
   trackear, +546 líneas del HTML, el perfil, 9 documentos y las pruebas. El
   PR #18 llegaba solo hasta `abfe85f`. Commiteado en `48ab8da` y **el PR #18
   ya lo contiene** (20 commits, 69 archivos, +8142/−233). Falta revisión: la
   protección de rama impide que el autor apruebe su propio PR.
2. **Tres tarjetas nuevas para Bancoldex** en `feat/tarjetas-bancoldex`,
   change `2026-08-07-tarjetas-bancoldex`: `c3b` (control de línea base),
   `c14` (firmas aprobadoras, trazadas sobre canvas en el propio informe) y
   `c8m` completada con responsable, fecha, observaciones y avance.
   **A/B de Acción Fiduciaria en 0 diferencias**; 135 pruebas en verde.
3. **El export arrastraba tarjetas de otros clientes.** Lo detectó el A/B
   (16 diferencias en la primera corrida): `podarClon()` no filtraba por
   preset, solo `exportarPDF()` lo hacía. Corregido; arregla también que una
   tarjeta desactivada desde el selector siguiera saliendo en el entregable.
4. **Las autopruebas del store solo valen con Acción Fiduciaria activa.**
   Dos de las 31 tienen el cliente escrito a mano y dan falso negativo con
   cualquier otro perfil. Preexistente, no lo introduce este change (con AF:
   31/31). Debería parametrizarse por `PERFIL`.

5. **El HTML exportado salía inerte** (reportado por el usuario tras lo
   anterior). Cuatro defectos encadenados, tres de ellos **preexistentes**:
   el perfil embebido se volvía a resolver y buscaba `window.PERFIL_BASE`
   (rompía a Bancoldex y Novaventa); `actualizarResumen()` escribía en el
   panel de carga que el entregable no lleva (**rompía también a Acción
   Fiduciaria, desde F4**); y la tarjeta generada desde el inventario perdía
   el `onclick` inline, que es lo único que sobrevive al clonado (desde F3).
   El cuarto sí lo introdujo el podado por preset: `pintarCI()` no toleraba
   una tarjeta podada. **Los entregables de esta rama estaban rotos para
   todos los perfiles**; los de `main` no. Corregido y cubierto por 5
   pruebas: el A/B no lo detecta porque compara texto y estado, no atributos
   ni listeners.

## Organización del repositorio (07/08/2026, noche)

Inventario completo de lo remoto y limpieza. Estado resultante:

**Ramas remotas — quedan 4**, todas con PR abierto: `main`,
`codex/f6-perfil-novaventa` (#18), `docs/regla-tasks-siempre` (#19),
`docs/retira-cardio-infantil` (#20) y `feat/tarjetas-bancoldex` (publicada,
sin PR todavía). Se borraron 10: cuatro ya fusionadas (#12, #14, #15, #16),
`codex/f5-adaptadores-canonico` (contenida por completo en el PR #18),
`docs/reorg-contexto` (ver abajo) y las cuatro de `cardio-infantil/`.

**Nada se borró sin respaldo.** Lo que tenía historia propia quedó en tags
anotados y publicados: `historico/cardio-infantil-*` (4) y
`historico/bancoldex-completo`, que también cubre
`f7/bancoldex-aranda-perfil` (era un subconjunto suyo). Se recuperan con
`git checkout <tag>`.

1. **Cardio Infantil se descarta** (decisión del usuario). PR #20 retira la
   fase F11, el documento de inventario y las menciones vivas. **Se conserva
   a propósito** la referencia al PR #5 como precedente: es lo que sostiene
   la prohibición de duplicar `automatizacion/` por cliente.
2. **Un commit remoto se había perdido:** `6d7785c` se empujó a
   `docs/reorg-contexto` después de que el PR #17 se fusionara, así que nunca
   llegó a `main`. Refuerza la regla de actualizar este archivo siempre.
   Rescatado en el PR #19.
3. **El PR #18 iba a entrar con los entregables rotos.** La corrección del
   export inerte vivía solo en `feat/tarjetas-bancoldex`, y tres de sus
   cuatro defectos son preexistentes — uno rompe también a Acción
   Fiduciaria. Portada en `e89577b`, con A/B en 0 sobre exports reales
   generados en la sesión y el entregable abierto de verdad (9 de 10
   tarjetas, igual que el control de `main`). Ver
   [`docs/2026-08-07-export-interactivo.md`](docs/2026-08-07-export-interactivo.md).
4. **Worktrees:** de 9 queda **1**, el principal. Los 7 de `/private/tmp` que
   había al empezar estaban consumidos, y los 4 temporales de esta sesión se
   retiraron al cerrarla (limpios y con sus ramas ya publicadas).

## El PR #18 entró a `main` (07/08/2026)

Fusionado como merge commit `2e5a2af`, sin squash: los 20 commits conservan
su historia. Verificado después del merge, no antes:

- **131 pruebas en verde** sobre `main`, y la autoprueba del arnés A/B pasa
  en sus tres casos.
- **El merge no alteró el HTML ni los perfiles**: son bit a bit los que ya
  se habían verificado en `e89577b` (`f0b64ab` para el HTML). Repetir el A/B
  ahí habría comparado un archivo consigo mismo.

Consecuencias que dejó, las tres resueltas en la misma sesión:

1. **#19 y #20 pasaron a `CONFLICTING`.** Puestos al día con `main` por
   `merge` (no `rebase`): las ramas tienen PR abierto y reescribir su
   historia obligaría a un force-push.
2. **#20 había quedado incompleto.** Su diff se calculó contra el `main`
   viejo, y #18 **reintrodujo** menciones de Cardio Infantil —incluida la
   fila de F11 en este archivo y un documento nuevo que #20 no conocía—. Se
   rehízo el retiro sobre el estado actual, no se resolvieron sus conflictos
   hunk a hunk. Detalle en la sección «Cardio Infantil» de la rama del PR.
   **Trampa detectada al portarlo:** #20 es anterior a la corrección de la
   grafía y escribía «Bancóldex» con tilde; aplicar su texto literal la
   habría reintroducido en cinco sitios.
3. **`feat/tarjetas-bancoldex` conflictaba en dos archivos**, ninguno el
   HTML: git resolvió los hunks del fix del export como ya aplicados.

## A/B de esta rama contra el `main` nuevo: 0 diferencias

El HTML de esta rama difiere del de `main`, así que la verificación anterior
—hecha contra el `main` viejo— dejó de cubrir el par. Se repitió entera con
los insumos reales de julio-2026:

- **`0 diferencias`**, código de salida 0, con el estado de entrada igualado
  a mano (`insumos-af.js` y `Accion Fiduciaria/` copiados al worktree de
  `main`, verificado por `md5`).
- **El entregable sigue vivo: 9 de 10 tarjetas abren su panel, idéntico al
  control de `main`.** La décima es `c12` («Anexos»), que declara
  `exportable:false` y no tiene panel por diseño — no es una falla.

**Aviso para quien repita esta verificación.** Medir la interacción por el
detalle inline (`#det-cX`) da un falso negativo del 100 %: una regla de CSS
lo oculta siempre (`display:none!important`) porque el contenido vive en
`.dashboard-modal`. Y ese modal **no existe hasta el primer clic** —
`podarClon()` lo elimina a propósito y `ensureModal()` lo recrea bajo
demanda—, así que buscarlo antes de hacer clic sugiere un entregable inerte
que en realidad funciona. Se comprueba tras el clic, sobre
`.dashboard-modal.is-open`.

## Cardio Infantil: descartado (07/08/2026)

Decisión del usuario. Se retiró del repositorio la fase **F11**, el documento
de inventario de tarjetas y todas las menciones de los documentos vivos
(`README.md`, este archivo, `docs/PATRONES.md`,
`docs/arquitectura-multicliente.md`, `docs/requisitos-producto.md`,
`openspec/project.md`, `automatizacion/sonda_glpi.py`).

Tres precisiones sobre el alcance, para no rehacer el trabajo ni borrar de
más:

1. **La referencia al PR #5 se conserva a propósito.** Es el precedente que
   sostiene la prohibición de duplicar `automatizacion/` por cliente
   (`openspec/project.md`). Lo que se quitó es el nombre del cliente, no la
   lección: donde decía `insumos_cardio.py` ahora dice
   `insumos_<cliente>.py`.
2. **Las actas fechadas no se reescriben.** `docs/archivo/2026-08-04-plan-multicliente.md`
   y `docs/2026-08-06-reorganizacion-contexto-documental.md` conservan su
   texto porque son el registro de lo que se decidió ese día; editarlas
   falsearía el acta. La primera lleva una nota al encabezado avisando de que
   todo lo relativo a ese cliente ya no aplica.
3. **Nada se perdió.** Las 4 ramas quedaron en tags anotados y publicados,
   `historico/cardio-infantil-*`. Se recuperan con `git checkout <tag>`.

## Siguiente paso

Los tres PR de la migración (**#18**, **#19** y **#20**) están **fusionados
a `main`** y sus ramas borradas. Queda una sola rama viva:
`feat/tarjetas-bancoldex`.

1. Afinar las tres tarjetas nuevas con el usuario y abrir el PR de
   `feat/tarjetas-bancoldex`, ya al día con `main` y con **A/B en 0** contra
   el `main` posterior a los tres merges.
2. Definir con el cliente la fuente de atribución a SETI para Bancoldex. Ya
   no bloquea el entregable.
3. El hallazgo 3 (scripts externos en el export), cuando se toque la
   exportación; no bloquea a nadie.

## Bloqueos conocidos

- `dorados/accion-fiduciaria-2026-06.json` no existe — requiere insumos
  reales de junio-2026 que no están en el repo (por diseño).

## Higiene pendiente

- `2026-08-05-fundacion-documental` va 13/19: faltan specs de `exportacion`,
  renombrar `esAccionFiduciaria()`/`esClienteAccion()` y archivar el change
  de F1.
- Un symlink a `Accion Fiduciaria` no queda cubierto por el patrón
  `Accion Fiduciaria/` del `.gitignore` (la barra final solo casa
  directorios). Sin consecuencia hoy; anotado para no redescubrirlo.

### Resuelto al cerrar la sesión del 07/08

- **Change duplicado por errata** (`2026-08-05-f6-perfil-noventa/`):
  **borrado**. No había nada que decidir — era un árbol de directorios vacío,
  sin un solo archivo, y ninguna rama del repositorio lo versiona. El correcto
  (`-novaventa`) conserva sus cinco archivos intactos.
- **`_tmp_main_ab/` (4,1 MB): borrado.** Antes de tocarlo se comprobó que su
  HTML y su perfil son **idénticos byte a byte** a los de `main`; lo único
  distinto era un symlink a `insumos-af.js`, que se retiró sin seguir el
  enlace (el archivo original sigue en el árbol). Nada irreproducible.
- **`.gitignore` ya cubre** `_tmp_*/`, `.claude/launch.json` y
  `.claude/worktrees/`: entró con el PR #20. Esos residuos dejaron de
  aparecer como no trackeados.

---

## Tareas sueltas

Lo que no es una fase completa: correcciones puntuales, deuda detectada al
pasar, seguimientos de una PR. Se agrega aquí en cuanto se detecta y se
quita en cuanto se resuelve — no espera a que alguien abra un change formal
si no lo amerita.

- Archivar los 5 changes de OpenSpec ya cerrados (F1–F5) — espera a que
  F2–F6 cierren, porque exige editar `automatizacion/test_specs_*.py` que
  el change F6 abierto también declara. Ver
  `openspec/changes/README.md` §Estado.
- `automatizacion/README.md` (579 líneas, el archivo de más *churn* del
  repo) sigue siendo el segundo mayor foco de contexto pesado sin resolver
  — quedó fuera de alcance de la reorganización documental del 06/08/2026.
  No es urgente; anotado para no perderlo de vista.

