# F7 — Adaptador Aranda y perfil Bancoldex (F7a datos + F7b integración)

**Reabierto el 06/08/2026, aplicado directamente sobre
`codex/f6-perfil-novaventa`** (no como merge de `codex/bancoldex-completo`).
Motivo: el usuario pidió que Bancoldex interprete AlertsList y el export de
Aranda (antes rotulado "Exportación GLPI"); `docs/2026-08-06-divergencia-bancoldex.md`
ya había identificado que esa función vive completa en `codex/bancoldex-completo`
y que las dos ramas construyeron Bancoldex sin coordinarse. En vez de mergear
las 20 diferencias del HTML (`§4` de ese documento), se hizo un **port
quirúrgico**: solo lo que F6 no tenía ya. Ver `docs/2026-08-06-<tema>.md` de
esta sesión para el detalle.

**Alcance reducido respecto al original.** Comparado contra el listado de
`codex/bancoldex-completo`, esta rama ya traía — construido de forma
independiente y verificado en su propio A/B — el equivalente de F7b para
consolidado: `definicionIndicador`/`cargarIndicadores`, `cargarBackups`
(con la misma corrección de columna «bd»), `cargarDisponibilidadTabla`
(`tabla-con-fechas`), `PERFIL.lineaBase` en `renderC3()`, `metaPerfil()` para
la aritmética de metas (`docs/2026-08-06-unidad-metas-perfil.md`), y
`presentarTarjetaPerfil()` (sin la parte de `configuracion`, añadida aquí).
**No se tocó nada de eso** — se verificó que ya es funcionalmente equivalente
antes de omitirlo. El defecto de F7 en el resumen de `c11` (§3.2 del análisis
de divergencia) tampoco aplica: `c11` no está en el preset de Bancoldex.

Lo que sí faltaba, y es el alcance real de este change:

1. El adaptador de Aranda para la tarjeta de casos (`c5`) — no existía
   ninguna versión en esta rama.
2. `fuentes.alertas` en el perfil de Bancoldex — no estaba declarado, así
   que `cargarAlertas()` hacía no-op para este cliente.
3. Un hallazgo nuevo, no cubierto por `codex/bancoldex-completo` (esa rama
   nunca declaró `fuentes.alertas` para Bancoldex, así que nunca ejercitó
   esta combinación): `publicarCasos()` y el bloque de gráfico/párrafos de
   `cargarAlertas()` sobrescriben incondicionalmente el dominio `casos` y el
   slide `s5` con el modelo AF (alertas+GLPI). Con Aranda activo eso borraba
   el dashboard de Bancoldex en cuanto se cargaba AlertsList. Se documenta
   como decisión de diseño nueva en `design.md`, sección "Interacción
   AlertsList × Aranda (hallazgo del 06/08/2026)".

## Lista cerrada de archivos

- `perfiles/bancoldex.js` (ya existente en esta rama — se edita, no se crea)
- `informe-accion-fiduciaria 1.html` (funciones nuevas: `clasificarTipoAranda`,
  `adaptarArandaACanonico`, `cargarCasosAranda`, `cargarCasosOGlpi`,
  `actualizarTarjetaCasosAranda`, `pintarCasosArandaEnSlide`; generalización
  de `presentarTarjetaPerfil` para fusionar `PERFIL.tarjetas.configuracion`;
  guard nuevo en `publicarCasos()` y en el bloque de pintado de
  `cargarAlertas()`; dispatch por modo en `actualizarTarjetaCasos()`; label
  dinámico del insumo #2 del Centro de carga; bloque `aranda-tipo-motor` en
  `renderC5()`; 3 clases CSS `.aranda-chart*`)
- `automatizacion/test_specs_adaptadores_fuente.py`
- `openspec/changes/2026-08-05-f7-bancoldex-aranda/`
- `docs/2026-08-06-aranda-alertslist-bancoldex.md` (nuevo, esta sesión)
- `docs/2026-08-07-verificacion-visual-y-nombre-bancoldex.md` (nuevo, 07/08)

**Ampliación del 07/08/2026 por el renombrado `Bancóldex` → `Bancoldex`:** la
corrección de grafía alcanza 28 archivos, la mayoría fuera de la lista de
arriba (`TASKS.md`, `README.md`, `.gitignore`, `openspec/project.md`,
`docs/**`, los `tasks.md`/`proposal.md`/`specs/` de F6). Se declara aquí
porque no hay otro change abierto que toque esos archivos y porque es una sola
sustitución textual del nombre del cliente, sin cambio de comportamiento
salvo en las cadenas visibles de `perfiles/bancoldex.js`.

`perfiles/base.js`, `ID_PERFIL_ACTIVO`, el registro de `PERFILES_REGISTRADOS`
y `cargarDisponibilidadTabla` **no** están en esta lista: ya existían en
`codex/f6-perfil-novaventa` antes de este change (construidos de forma
independiente). `docs/2026-08-04-plan-multicliente.md` tampoco se toca: no
hubo cambio de arquitectura objetivo, solo de implementación.

## Historial en `codex/bancoldex-completo` (no reaplicado literalmente)

La lista original de F7a/F7b se conserva aquí solo como referencia de lo que
ya se verificó una vez contra los insumos reales — la mayoría de estos puntos
**ya estaban resueltos de forma independiente** en `codex/f6-perfil-novaventa`
antes de este port (ver la nota de alcance reducido arriba) y no se
retocaron:

- [x] `perfiles/base.js`, registro en `PERFILES_REGISTRADOS`, `ID_PERFIL_ACTIVO`
  — ya en F6.
- [x] `definicionIndicador`/`cargarIndicadores`, `cargarBackups` (con la
  corrección de columna «bd»), `cargarDisponibilidadTabla`
  (`tabla-con-fechas`), `PERFIL.lineaBase` en `renderC3()` — ya en F6,
  verificados idénticos byte a byte contra este export.
- [x] Aritmética de `metas.backups` (fracción vs. porcentaje) — corregida en
  F6 el 06/08/2026 vía `metaPerfil()` (`docs/2026-08-06-unidad-metas-perfil.md`),
  no con la fórmula original de F7.
- [ ] El literal de meta quemado en el resumen de `c11` (§3.2 de
  `docs/2026-08-06-divergencia-bancoldex.md`) — no aplica: `c11` no está en
  el preset de Bancoldex en ninguna de las dos ramas.

## Implementación (port del 06/08/2026 sobre `codex/f6-perfil-novaventa`)

- [x] `perfiles/bancoldex.js`: agregar `fuentes.alertas` (mismo formato
  genérico de AF/Novaventa), `tarjetas.configuracion.c5` y
  `tarjetas.presentacion.c5`, y añadir `'c5'` a `tarjetas.seleccionadas`.
- [x] Generalizar `presentarTarjetaPerfil()` para fusionar también
  `PERFIL.tarjetas?.configuracion?.[id]` (hoy solo fusiona `presentacion`) —
  necesario para que `c5.dominios`/`c5.fuentes`/`c5.criterios` de Bancoldex
  se apliquen.
- [x] Portar `clasificarTipoAranda()`, `adaptarArandaACanonico()`,
  `cargarCasosAranda()`, `cargarCasosOGlpi()`, `actualizarTarjetaCasosAranda()`
  y `pintarCasosArandaEnSlide()` desde `codex/bancoldex-completo`, sin tocar
  `cargarGlpi()`.
- [x] Enrutar los 3 sitios que llaman `cargarGlpi` directo
  (`INSUMOS_PERSIST`, `procesarFuente`, la restauración de insumos) por
  `cargarCasosOGlpi`.
- [x] Dinamizar la etiqueta y el texto de ayuda del insumo #2 del Centro de
  carga: agregar `data-perfil-carga="glpiTitulo"`/`"glpiAyuda"` al
  `<label>`/`<div class="state">` de `#cardGlpi` (mismo mecanismo que ya usa
  Novaventa para consolidado/alertas) y declarar
  `textos.carga.glpiTitulo`/`glpiAyuda` en `bancoldex.js`. El literal
  «2. Exportación GLPI» embebido en el HTML sigue siendo el default para
  perfiles que no declaran esas claves.
- [x] Añadir el bloque `x.modo==='aranda-tipo-motor'` a `renderC5()` (dona por
  motor, barras por categoría, análisis narrativo) y las 3 clases CSS
  `.aranda-chart-panel`/`.aranda-chart`/`.aranda-breakdowns`.
- [x] Dispatch por modo en `actualizarTarjetaCasos()`: si
  `REPORTE.d('casos').datos?.modo==='aranda-tipo-motor'`, delega en
  `actualizarTarjetaCasosAranda()` en vez de leer `DATA_CASOS`. Necesario
  porque varios sitios (reconciliación, `cargarAlertas`) llaman
  `actualizarTarjetaCasos()` directamente sin saber qué perfil está activo.
- [x] Guard nuevo en `publicarCasos()`: `if(PERFIL.fuentes?.casos) return;` —
  ver "Interacción AlertsList × Aranda" en `design.md`.
- [x] Guard nuevo en `cargarAlertas()`: el bloque que escribe
  `DATA_CASOS.alertas`, los párrafos de `#s5` y `chartCasos` solo corre
  `if(!PERFIL.fuentes?.casos)`; el resto de la función (validar, contar,
  publicar el dominio `alertas`, marcar el insumo) sigue sin condición.
- [x] **Hallazgo en navegador** — `c5.configuracion` debe declarar
  `dominios: ['casos','alertas']` y `fuentes: ['glpi','alertas']` (no solo
  `'casos'`/`'glpi'`): sin `'alertas'` registrada, `REPORTE.publicar('alertas',...)`
  lanzaba «Dominio desconocido» y `validarArchivo('alertas',...)` rechazaba
  cualquier extensión. Ver design.md.
- [x] **Hallazgo en navegador** — guard `if(PERFIL.fuentes?.casos) return;`
  en `cargarInsumosAutomaticos()`: sin él, un `insumos-af.js` de desarrollo
  presente junto al HTML saltaba el periodo de Bancoldex a julio sin acción
  del usuario. Ver design.md.
- [x] Ejecutar `python3 -m unittest discover -s automatizacion -p 'test_*.py'`
  (95 pruebas, OK) y `automatizacion/verificar_ab.py --autoprueba` (OK).
- [x] Verificar en navegador con los insumos reales de junio-2026
  (`Bancoldex/Data consolidada junio_Bancoldex 2026.xlsx` +
  `Bancoldex/Casos  + tareas BD junio 2026.xlsx`, servidos localmente vía
  `python3 -m http.server` — la app sigue siendo `file://`, el servidor es
  solo para que este navegador de prueba ejecute JS): label dice "Exportación
  Aranda", 72 casos interpretados (33 monitoreo, 32 requerimiento, 5 tarea, 2
  incidente; SLA 71/72; 52 Oracle/19 SQL Server/1 Weblogic; dashboard y
  análisis narrativo correctos). AF sin cambios (label "GLPI" intacto,
  autocarga de `insumos-af.js` intacta, consola limpia).
- [x] Verificado también con un AlertsList sintético (2 alertas, jun-26): se
  interpreta (cuenta, publica el dominio `alertas`, marca el insumo, avisa
  por falta de columnas Topic/Message) sin alterar los 72 casos de Aranda ya
  mostrados — confirma el guard de "Interacción AlertsList × Aranda". No hay
  un CSV real de AlertsList de Bancoldex en el repo; queda pendiente
  confirmar con el primer archivo real del cliente.
- [x] Documento de sesión `docs/2026-08-06-aranda-alertslist-bancoldex.md`.

## Rediseño del modal de casos (07/08/2026, tras feedback en vivo del usuario)

Un primer intento de mejorar el modal reorganizó las mismas gráficas y,
sobre todo, **renombró "Incidentes atribuibles a SETI"** (a "Cumplimiento e
incidentes reales", luego combinándolo con un badge de SLA). El usuario
rechazó ambas cosas explícitamente. Corrección aplicada — ver
`design.md`, "Incidentes atribuibles a SETI: no se toca ese apartado", que
es ahora la referencia normativa para cualquier trabajo futuro en este
modal:

- [x] El panel `case-analysis` vuelve a tener **solo** «Incidentes
  atribuibles a SETI» (título literal, un único `.case-seti`, sin SLA ni
  badges adicionales).
- [x] El cumplimiento de SLA se movió a un panel propio con gauge circular
  (`gauge()`/`.gauge-exec`, componente ya existente en el motor y sin usar
  hasta ahora), en una grilla de 3 columnas junto a "Casos por tipo" y
  "Casos por motor".
- [x] Pruebas actualizadas (`test_modal_aranda_no_reemplaza_incidentes_por_sla`
  reescrita para verificar la estructura corregida) — 96 pruebas, OK.
- [ ] **Pendiente, explícitamente diferido por el usuario:** definir cómo se
  valida qué incidentes de Aranda son "atribuibles a SETI" (hoy usa
  `incidentesReales` — categoría `Incidente` excluyendo monitoreo — como
  cifra provisional, sin cruce de atribución real). No resolver esto sin
  evidencia real ni sin acordarlo primero con el usuario.
- [x] **Verificación visual en navegador — hecha el 07/08/2026.** Captura del
  modal con los insumos reales de junio-2026 (`Bancoldex/Casos  + tareas BD
  junio 2026.xlsx`, 72 casos): panel «Incidentes atribuibles a SETI» con
  título literal y un solo badge («2», «1 de 2 incidentes fuera del SLA»),
  panel «Cumplimiento del SLA» aparte con el gauge en 98,6 %, y la grilla de
  3 columnas con "Casos por tipo" (33/32/5/2) y "Casos por motor"
  (52 Oracle / 19 SQL Server / 1 Weblogic). Ver
  `docs/2026-08-07-verificacion-visual-y-nombre-bancoldex.md`.
- [x] **Defecto hallado en esa verificación y corregido:** el rótulo del
  gauge cruzaba el anillo de color. `padding:0 26px` en `.gauge-exec` +
  `test_gauge_exec_reserva_espacio_lateral_para_el_rotulo`. Ver design.md.
- [ ] Publicar la rama remota/PR (no solicitado; requiere decisión del
  usuario/equipo).

## Grafía del nombre del cliente (07/08/2026)

- [x] `Bancóldex` → `Bancoldex` (y `BANCÓLDEX` → `BANCOLDEX`) en los 28
  archivos del repositorio que lo mencionaban — 232 ocurrencias. Incluye las
  cadenas visibles del entregable en `perfiles/bancoldex.js` (`nombre`,
  `tituloDocumento`, `marcaTopbar`, `clienteHero`, `confidencialidad`), el
  placeholder «Ej. Bancoldex» del formulario de clientes, comentarios del
  HTML, specs, docs y pruebas. Regla y verificación en design.md, sección
  "El cliente se escribe «Bancoldex», sin tilde".
- [x] Comprobado en navegador: topbar «Informe Bancoldex», héroe «CLIENTE:
  BANCOLDEX», `<title>` «Informe Gerencial · Bancoldex», selector de cliente
  activo «Bancoldex».
- [ ] **Pendiente, fuera de este repositorio:** un cliente que el usuario
  haya creado por la UI queda guardado con el nombre que escribió en su
  `localStorage`. El renombrado no lo alcanza; hay que editarlo desde
  «Editar datos» si aparece con tilde.

## Exclusiones deliberadas del preset

- Lector dinámico de la hoja `Linea Base` (hoy `PERFIL.lineaBase` es
  declaración estática verificada contra el PDF aprobado; el Excel original
  presenta totales incompatibles).
- `c6`/`c11`: el original de `Disponibilidad Real` termina en jun-25; el
  fixture de prueba no se usa como evidencia.
- `c9`: TYA corresponde a sep-25 y no acredita contrato/saldo de horas para
  jun-26.
- `c12`: no existe insumo mensual exportable en el flujo entregado.

## Tres defectos del Centro de carga (07/08/2026, reportados por el usuario)

Detalle completo, con las mediciones y la tabla de antes/después, en
[`docs/2026-08-07-correccion-insumos-bancoldex.md`](../../../docs/2026-08-07-correccion-insumos-bancoldex.md).
Reglas normativas en `design.md`.

- [x] **El consolidado rompía el informe.** `cargarCasos()` (hoja «Casos»,
  modelo de AF) corría también para Bancoldex, cuyo consolidado sí trae esa
  hoja, y escribía sobre los `datasets` que Aranda ya había reemplazado: o
  corrompía las cifras en silencio, o lanzaba un `TypeError` que abortaba
  `cargarConsolidado()` entero y bloqueaba la exportación. Guard
  `if(PERFIL.fuentes?.casos){ alertasConsolidadoMes=null; return null; }`.
- [x] **La entrada de Mitigaciones rechazaba el libro del cliente**
  («Formato no permitido … Usa .», lista vacía). Dos capas: se retira
  `c8m: {fuentes: ['logros']}` del perfil —`tarjeta.fuentes` solo alimenta el
  mapa de extensiones— y `EXTENSIONES_INSUMO` pasa a ser la función
  `extensionesInsumo()`, porque como `const` quedaba congelado con el preset
  inicial mientras `TARJETAS_SELECCIONADAS` se reasigna después. Lo segundo
  es un defecto del motor, no de Bancoldex.
- [x] **Había que cargar el archivo cualitativo dos veces.** Las ramas
  `archivo-alcance-unico` de `cargarLogrosArchivo()` y
  `cargarMitigacionesArchivo()` marcan ahora los dos insumos, como ya hacía
  la rama del registro mensual de AF. Pedido explícito del usuario.
- [x] 11 pruebas nuevas (108 en total, OK) + `verificar_ab.py --autoprueba` OK.
- [x] Verificado en navegador con los insumos reales de junio-2026: 72 casos
  de Aranda intactos tras cargar el consolidado, las dos tarjetas
  cualitativas en verde desde cualquiera de las dos entradas, 0 errores,
  «Informe listo para exportar». AF sin cambios (`REPORTE.autopruebas()`
  31/31 PASA).

### Ampliación de la lista de archivos

- `informe-accion-fiduciaria 1.html` — guard en `cargarCasos()`;
  `EXTENSIONES_INSUMO` → `extensionesInsumo()`; respaldo de formatos en
  `validarArchivo()`; marcado doble en las dos ramas `archivo-alcance-unico`.
- `perfiles/bancoldex.js` — se retira `c8m: {fuentes: ['logros']}`.
- `automatizacion/test_specs_perfil_cliente.py` y
  `automatizacion/test_specs_adaptadores_fuente.py`.
- `docs/2026-08-07-correccion-insumos-bancoldex.md` (nuevo).

### Hallazgos abiertos de esta sesión

- [ ] **Texto desbordado en `c3`.** «Oracle · SQL Server» se monta sobre la
  columna de Vigencia: `.tarjeta-kpi__mini-val` es `white-space:nowrap` con
  `overflow:visible` y el texto excede su caja en 70 px (165 px de texto en
  95 px de columna). **No se corrigió a propósito:** es una clase compartida
  y `c3` la renderiza también Acción Fiduciaria, que está en producción —
  requiere decisión del usuario y A/B.
- [ ] **Qué cuenta como «insumo obligatorio» para Bancoldex.** El contador
  dice «1/2» con el informe ya exportable: cuenta AlertsList (que todavía no
  se confirma que aplique a este cliente) y no cuenta Aranda (que es el
  insumo #2 de la pantalla y sí es obligatorio). El bloqueo de la
  exportación no depende de este contador, así que es un problema de lo que
  se le dice al usuario, no de comportamiento. Es una definición de negocio.

### Dos defectos más, misma tarde del 07/08/2026

- [x] **Un insumo restaurado no se releía al cambiar el periodo.**
  `restaurarInsumosGuardados()` reconstruía el `File` y llamaba al cargador
  sin depositarlo en su `<input>`, y `ejecutarRevalidacion()` recorre los
  `<input>`: el export de Aranda quedaba en «0 casos de jul-26» con el
  selector en Junio. Corregido con el mismo patrón `DataTransfer` que ya usa
  `procesarFuente()`. Verificado: tras restaurar y corregir el mes, se relee
  y da 72 casos de jun-26.
- [x] **Recuento de insumos obligatorios.** Alcance definido por el usuario:
  para Bancoldex AlertsList **sí** cuenta; lo que no aplica es GLPI, al que
  reemplaza Aranda. El recuento incluye ahora la entrada de casos cuando el
  perfil declara `fuentes.casos`, e `insumoProcesado()` la resuelve contra el
  dominio `casos`. Verificado: «3/3 insumos obligatorios procesados» con
  consolidado, Aranda y AlertsList. AF conserva `consolidado`+`glpi`+`alertas`.
- [x] 17 pruebas nuevas en total (114, OK) + `verificar_ab.py --autoprueba` OK
  + `REPORTE.autopruebas()` de AF 31/31 PASA.

- [x] **Resuelto, no era un bug.** El `alertops-2026-07.csv` original no
  traía ninguna fila de Bancoldex. El usuario agregó
  `Bancoldex/AlertsList-2.csv` (202 filas) y reportó que junio-2026 seguía en
  0 — pero el archivo real no contiene una sola fila de junio (su rango es
  9/jul–7/ago/2026). Verificado: 202/212 filas SÍ se reconocen como de
  Bancoldex (el filtro funciona), y con periodo Julio da 153 alertas —
  coincide exacto con el conteo directo del CSV. No se tocó código.

## Cierre del 07/08/2026 (noche) — ver `docs/2026-08-07-cierre-bancoldex.md`

Tres decisiones del usuario y el A/B que bloqueaba la fusión.

- [x] **Atribución a SETI: Bancoldex muestra 0.** Sustituye el pendiente
  abierto más arriba («definir cómo se valida qué incidentes son atribuibles
  a SETI»): mientras no exista la fuente, el informe no afirma una atribución
  que nadie confirmó. Regla declarada en el perfil
  (`reglas: {atribucionSeti: 'sin-fuente'}`), no como caso especial del
  motor; el default preserva a AF y Novaventa sin tocarlas. El apartado
  conserva su título literal y su tarjeta única. **Sigue abierto** definir la
  fuente real de atribución, sin que bloquee el entregable.
- [x] **Desborde de `c3` corregido solo para Bancoldex** (alcance elegido por
  el usuario). Mecanismo nuevo y declarativo:
  `tarjetas.presentacion.<id>.modificadores`, validado contra
  `/^[a-z0-9-]+$/` y aplicado como `tarjeta-kpi--<modificador>`. La clase
  compartida, que AF renderiza en producción, no se toca. Medido: 165 px de
  texto en 79 px de caja antes; ajustado dentro de la caja después.
- [x] **A/B de Acción Fiduciaria: 0 diferencias.** Primera corrida: 11.
  Diez venían de estado de entrada desigual (`insumos-af.js`, ignorado por
  git, existe en el repo y no en el worktree de `main`) — se igualó y se
  repitió, sin aceptar un A/B parcial.
- [x] **Defecto real hallado por ese A/B:** `metaPerfil()` formateaba la meta
  de backups con `pct()`, que redondea a entero, y el informe de AF pasó de
  «Meta 99,3%» a «Meta 99%». Corregido con `metaTexto()`. Los otros dos usos
  de `pct(meta)` («Meta mínima de …») redondean igual en `main` y en la rama:
  no se tocan.
- [x] 12 pruebas nuevas (126 en total, OK), `verificar_ab.py --autoprueba` OK,
  `REPORTE.autopruebas()` de AF 31/31 PASA.
- [x] Delta de spec escrito antes del código
  (`specs/perfil-cliente/spec.md`): atribución declarada por el perfil,
  modificadores de presentación y presentación de la meta con su decimal.
- [x] **Bloques 7, 8–9 y 17 de la divergencia: verificados como ya resueltos**
  en esta rama. El bloque 3 (`?perfil=`) se descarta: `cambiarClienteActivo`
  cubre lo mismo. No queda nada por portar de `codex/bancoldex-completo`.

### Ampliación de la lista de archivos

- `informe-accion-fiduciaria 1.html` — `metaTexto()`; guard de
  `atribucionSeti` en `renderC5()`; modificadores en
  `montarTarjetasDesdeInventario()`; regla CSS
  `#tk-c3.tarjeta-kpi--valores-largos`.
- `perfiles/bancoldex.js` — `reglas.atribucionSeti`, `c3.modificadores`.
- `automatizacion/test_specs_perfil_cliente.py`.
- `docs/2026-08-07-cierre-bancoldex.md` (nuevo).

## Ampliación del 07/08/2026 (noche) — el entregable salía sin interactividad

Se detectó al revisar el PR #18 antes de pedirle revisión a alguien más: el
HTML exportado por esta rama se generaba y se veía correcto, pero no
respondía a ningún clic. **Tres de los cuatro defectos son preexistentes**
(desde F3 y F4) y uno de ellos rompía también el entregable de Acción
Fiduciaria, que está en producción. Se declara aquí y no en un change nuevo
porque este es el único change abierto de la rama que declara
`informe-accion-fiduciaria 1.html`, y abrir otro lo declararía dos veces.

- [x] **Delta de spec escrito primero**
  (`specs/inventario-tarjetas/spec.md`, nuevo): «el entregable exportado
  conserva la interacción», con los cuatro escenarios.
- [x] `resolverPerfil()` devuelve el perfil embebido tal cual. Ya viene
  resuelto (`codigoEstadoCliente()` serializa `perfilEfectivo()`), pero
  conserva `extiende`, así que se buscaba `window.PERFIL_BASE` — que el
  entregable no lleva, porque `podarClon()` elimina los `<script>` de
  perfiles. Rompía a los perfiles con herencia: Bancoldex y Novaventa.
- [x] `actualizarResumen()` tolera que no exista `#loadSummary`. El panel de
  carga es de autoría y el podado lo elimina, pero
  `restaurarPresetTarjetas()` alcanza esa función al abrir el entregable.
  **Este rompía también a Acción Fiduciaria, desde F4.**
- [x] La tarjeta que genera `montarTarjetasDesdeInventario()` recupera el
  `onclick` inline que traía el HTML legado. `activarModales()` engancha con
  `btn.onclick=fn`, que es una propiedad y no se serializa: un clon solo
  conserva atributos. **Desde F3.**
- [x] `pintarCI()` tolera que no exista `#tbodyCI` (vive en `c11`, que un
  perfil puede no seleccionar).
- [x] `podarClon()` deja de arrastrar el `#dashboardModal` de la sesión de
  autoría, devolviendo antes su contenido a la tarjeta —`openDashboard()`
  mueve el panel al modal, así que podarlo sin más lo borraría del
  entregable si se exporta con una tarjeta abierta.
- [x] 5 pruebas nuevas en `automatizacion/test_specs_inventario_tarjetas.py`
  (131 en total, OK). El arnés A/B no puede detectar esta clase de defecto:
  compara texto visible y estado, no atributos ni listeners.
- [x] **A/B de Acción Fiduciaria sobre esta rama: 0 diferencias.** Con dos
  exports reales generados en la misma sesión desde los insumos de
  julio-2026 (`Accion Fiduciaria/`), uno en `main` (`cf50713`) y otro en esta
  rama, ambos con el mismo estado de entrada. `verificar_ab.py --autoprueba`
  OK antes de dar el resultado por bueno.
- [x] **Verificado en el entregable, no solo en el DOM de autoría:** el HTML
  exportado de la rama abre 9 de sus 10 tarjetas, lleva un solo
  `#dashboardModal` y ninguna traza del panel de carga. El export de `main`,
  usado como control, da exactamente lo mismo (9 de 10; la décima es `c12`,
  que no declara renderizador). Sin errores de JavaScript en ninguno de los
  dos: los únicos 404 son los de `insumos-af.js`, preexistentes en `main`.

### Ampliación de la lista de archivos

- `informe-accion-fiduciaria 1.html` — guard en `resolverPerfil()`,
  `actualizarResumen()` y `pintarCI()`; `onclick` inline en la tarjeta
  generada; poda del `#dashboardModal` en `podarClon()`.
- `automatizacion/test_specs_inventario_tarjetas.py`.
- `openspec/specs/inventario-tarjetas/spec.md` y el delta del change.
- `docs/2026-08-07-export-interactivo.md` (nuevo).
