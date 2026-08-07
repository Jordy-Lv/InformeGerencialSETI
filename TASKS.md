# Tareas activas

Solo lo vigente: qué está en curso, qué bloquea y el siguiente paso. Para el
histórico completo de fases fusionadas, ver [`CHANGELOG.md`](CHANGELOG.md).
Para la arquitectura objetivo (qué es cada fase y su criterio de
aceptación), ver [`docs/arquitectura-multicliente.md`](docs/arquitectura-multicliente.md).

**Regla operativa** (`openspec/AGENTS.md`): dos `changes` abiertos no pueden
declarar el mismo archivo en su `tasks.md`. Revisa `openspec/changes/`
(excluye `archivo/`) antes de tocar código.

Última verificación de este archivo contra git: **07/08/2026 (cierre)** —
Bancoldex cerrado y A/B de AF en 0, ver «Cierre del 07/08/2026» más abajo.

**El cliente se escribe «Bancoldex», sin tilde.** Corregido en todo el
repositorio el 07/08/2026 (232 ocurrencias, 28 archivos). La regla y su
comprobación están en `openspec/changes/2026-08-05-f7-bancoldex-aranda/design.md`.
No reintroducir `Bancóldex`.

---

## Estado por fase

Verificado con `git merge-base --is-ancestor` y `git rev-list`, no por
lectura de docs. F2–F5 **sí están commiteadas** y las contiene por completo
`codex/f6-perfil-novaventa` (son secuenciales sobre el mismo HTML).

| Fase | Rama | Estado verificado |
|---|---|---|
| F0 — fundación (OpenSpec, arnés A/B, dorados) | `main` | **Abierta.** Falta `dorados/accion-fiduciaria-2026-06.json`. Sin esa evidencia F0 no cierra formalmente |
| F1 — perfil de cliente como datos puros | `main` | **Cerrada.** PR #12 (`404408c`), A/B julio-2026 en 0 |
| F2 — contrato desacoplado del DOM | `codex/f2-contrato-perfil` | Completa (7/7). Contenida en F6 |
| F3 — inventario de tarjetas | `codex/f3-inventario-tarjetas` | Completa (6/6). Contenida en F6 |
| F4 — plantilla y preset de tarjetas | `codex/f4-plantilla-preset` | Completa (10/10). Contenida en F6 |
| F5 — adaptadores y modelo canónico | `codex/f5-adaptadores-canonico` | Completa (8/8). Contenida en F6 |
| F6 — perfil Novaventa + registro de clientes | `codex/f6-perfil-novaventa` | **Cerrada el 07/08/2026.** A/B de AF en 0 con los insumos reales de julio-2026 (ver el cierre más abajo). Lista para PR |
| F7 — adaptador Aranda + perfil Bancoldex | `codex/f6-perfil-novaventa` (portado) + `codex/bancoldex-completo` (histórico) | **Casos (Aranda) y AlertsList portados a F6 el 06/08/2026** — ver [`docs/2026-08-06-aranda-alertslist-bancoldex.md`](docs/2026-08-06-aranda-alertslist-bancoldex.md). El resto de F7b (indicadores/backups/disponibilidad/lineaBase) ya existía en F6, construido por separado. `codex/bancoldex-completo` queda como referencia histórica, no se mergea |
| F8 — automatización multicliente | — | No iniciada |
| F9 — reglas compartidas JS↔Python | — | No iniciada |
| F10 — split `fuente/` (opcional) | — | No iniciada |
| F11 — Cardio Infantil | — | **Bloqueada** por 4 preguntas de sondeo |

`fix/auditoria-2026-08-02` y `codex/f0-dorados-ab` están 0 commits por
delante de `origin/main`: ya absorbidas, se pueden borrar.

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

## Siguiente paso

1. Conseguir revisión de los tres PR abiertos: **#18** (F2–F7, el grande),
   **#19** (rescate de la regla de `TASKS.md`) y **#20** (retiro de Cardio
   Infantil + higiene de `.gitignore`). Los tres dependen solo de que los
   revise alguien distinto del autor.
2. Afinar las tres tarjetas nuevas con el usuario y abrir el PR de
   `feat/tarjetas-bancoldex`, que parte de `48ab8da`. **Ojo al orden:** si
   #18 entra primero, esta rama trae los mismos hunks del fix del export y
   git los resolverá como ya aplicados o con un conflicto menor.
3. Definir con el cliente la fuente de atribución a SETI para Bancoldex. Ya
   no bloquea el entregable.
4. El hallazgo 3 (scripts externos en el export), cuando se toque la
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
- `.gitignore` cubrirá `_tmp_*/`, `.claude/launch.json` y
  `.claude/worktrees/` **cuando entre el PR #20**, no antes: hasta entonces
  `.claude/launch.json` seguirá apareciendo como no trackeado. Es esperado.
