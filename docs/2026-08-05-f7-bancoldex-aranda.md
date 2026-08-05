# F7 — Adaptador Aranda y perfil Bancóldex (F7a datos + F7b integración real)

**Rama de cierre:** `codex/bancoldex-completo`, creada desde el relevo
documentado de `f7/bancoldex-aranda-perfil` (`4f822c3`), en un worktree
aislado (`/private/tmp/f7-bancoldex-aranda`) para no interferir con el
trabajo en curso de F6 (Novaventa, `codex/f6-perfil-novaventa`, con
cambios sin confirmar al momento de abrir esta rama).

**Estado final:** Bancóldex queda funcional para junio de 2026 con el preset
`c3, c4, c5, c7, c8, c8m`, tres fuentes originales, restauración persistente,
salida autocontenida y visualización ejecutiva de casos. Las secciones F7a,
F7b y «Relevo final de Claude» se conservan como historial; sus pendientes
quedan resueltos o descartados explícitamente en «Cierre Codex» al final.

Este documento cubre dos sesiones seguidas el 05/08/2026: F7a (modelo de
datos) y F7b (integración real con los archivos de Bancóldex, priorizada
explícitamente por el usuario). La sección "F7b" es la más reciente.

## Contexto

El plan maestro (`docs/2026-08-04-plan-multicliente.md`) reserva F7 para el
adaptador de Aranda (carga manual) y el perfil Bancóldex. Ya existía un
reconocimiento completo (`docs/2026-08-05-reconocimiento-bancoldex.md`) con
evidencia real de los cuatro insumos de Bancóldex (`Bancoldex/`, ignorados
por git) y del PDF de referencia de junio de 2026. Esta sesión retoma ese
reconocimiento para implementar el modelo de datos y, después, completar la
integración visual y funcional del perfil.

`openspec/changes/2026-08-05-f6-perfil-novaventa/tasks.md` seguía abierto y
reserva `informe-accion-fiduciaria 1.html`; esta rama también lo toca (solo
con funciones nuevas, sin modificar las de GLPI/AF/Novaventa) porque
declarar un segundo/tercer perfil exige registrarlo en el motor. Queda
registrado explícitamente: **coordinar el orden de merge con quien cierre
F6** antes de llevar esta rama a `main`.

## Qué se implementó

1. **`perfiles/base.js`** — perfil raíz sin cliente concreto (`extiende:
   null`), para que Bancóldex pueda extenderlo sin superar el 30% de
   sobrescritura que exigiría heredar de un perfil de cliente
   (`docs/2026-08-04-plan-multicliente.md`).
2. **`perfiles/bancoldex.js`** — extiende `base`; declara `contrato` (código
   `CN-2024112`, inicio 14/11/2024, fin 14/11/2026) y las cuatro metas de
   indicadores (disponibilidad 99,98%, cumplimiento de atención 97%,
   entregables 99%, ejecución de backups 95%) leídas directamente del PDF de
   referencia (`Bancoldex/reporte-bancoldex-2026-07-02.pdf`, páginas «Línea
   base del servicio» e «Indicadores»), no inventadas. Declara
   `fuentes.casos` (Aranda) y `tarjetas.seleccionadas: ['c9']` (ver más
   abajo).
3. **Adaptador de Aranda** (`clasificarTipoAranda`,
   `adaptarArandaACanonico`, `cargarCasosAranda`) — funciones nuevas,
   paralelas a `adaptarGlpiACanonico`/`cargarGlpi` de F5, sin modificarlas.
   Clasifica por `TIPO_DE_CASO` (no por categoría como GLPI), separa
   jerarquía por `.` (no `>`), y resuelve el SLA con la estrategia nueva
   `columna-cumplimiento` (`Cumple`→true, `No cumple`→false, cualquier otro
   valor→null).
4. **Registro de perfiles y selección por URL** — `base`/`bancoldex` se
   suman a `PERFILES_REGISTRADOS`. Se encontró que al cierre de F5
   `resolverPerfil('accion-fiduciaria')` estaba fijo (sin mecanismo
   `?perfil=`); sin corregirlo, un segundo perfil registrado quedaba
   inalcanzable. Se agregó `ID_PERFIL_ACTIVO` (la misma resolución que ya
   trae, de forma independiente, la rama F6 — convergerán en un conflicto de
   mezcla trivial, no de comportamiento). Sin `?perfil=` el resultado sigue
   siendo `'accion-fiduciaria'`: mismo comportamiento que antes.
5. **Decisión de alcance de cliente** — Aranda declara
   `filtroCliente.estrategia: 'archivo-alcance-unico'`: acepta todas las
   filas del export porque ya se entrega delimitado a Bancóldex (el
   reconocimiento descartó filtrar por `Proyecto` o `COMPANIA`, ver
   `design.md`).

## Decisiones registradas durante la implementación (no estaban en el plan previo)

- **`tarjetas.seleccionadas: ['c9']`, no vacío.** `resolverTarjetasPerfil()`
  exige al menos una tarjeta; un arreglo vacío hace fallar el arranque. De
  las tarjetas del inventario compartido, `c9` (bolsa de horas) es la única
  cuyo texto de presentación ya es genérico y cuyo renderizador no depende
  de GLPI ni del consolidado — las demás mostrarían texto o cifras de
  Acción Fiduciaria bajo la marca Bancóldex.
- **Gap preexistente registrado, no resuelto aquí:** `c3` (línea base) y
  `c9` son diapositivas «constantes» — `actualizarVisibilidad()` no las
  oculta nunca, y como Bancóldex no selecciona `c3`, su renderizador nunca
  corre y la diapositiva conserva el marcado estático original de Acción
  Fiduciaria (contrato «CN-21012025», etc.), leído de un campo editable del
  DOM (`[data-k="contrato"]`), no del perfil. Esto no es un defecto de F7a:
  ninguna fase anterior extrajo ese campo a datos del perfil, así que
  cualquier cliente nuevo (incluida Novaventa) hereda el mismo texto hasta
  que el consultor lo edite a mano. Ver `design.md` del change, sección
  "Gap preexistente".
- **`cargarCasosAranda()` no publica en `REPORTE`.** Los dominios de
  `REPORTE` se derivan de `TARJETAS_PREDETERMINADAS` (F3); como Bancóldex no
  tiene todavía una tarjeta de casos con sus cuatro categorías, no hay un
  nombre de dominio válido al que publicar sin editar a mano esa lista
  derivada. La función devuelve `{estado, casos, agregados, fuente, notas}`;
  F7b la conecta a `REPORTE` cuando exista esa tarjeta.
- **Alias de columna deben ir ya normalizados.** `col()`/`resolverCabecera()`
  comparan `norm(celda)` contra el alias tal cual está escrito — el alias no
  se normaliza. La primera versión de este perfil usaba
  `['numero_del_caso']` (calcado del nombre real de columna, con guion
  bajo) y no encontraba ninguna fila candidata, porque `norm()` convierte
  guion bajo en espacio. Se corrigió a `['numero del caso']` y se verificó
  contra el export real.

## Verificación realizada

- **Sintaxis:** `node --check` sobre los nueve bloques `<script>` inline
  concatenados (`node v24.18.0`) → sin errores. `node --check` sobre
  `perfiles/base.js`, `perfiles/bancoldex.js`, `perfiles/accion-fiduciaria.js`
  → sin errores.
- **Suite Python:** `python3 -m unittest discover -s automatizacion -p
  'test_*.py'` → `Ran 68 tests ... OK` (66 preexistentes + 2 nuevas clases
  de conformidad para F7a, ninguna prueba existente se eliminó; se
  actualizaron 2 aserciones textuales de `test_specs_perfil_cliente.py` que
  dependían del texto exacto, anterior a este cambio, de la línea de
  registro de `accion-fiduciaria`).
- **Adaptador contra el export real (Node, con el SheetJS embebido en el
  propio HTML, extraído a un módulo temporal — no se instaló ninguna
  dependencia nueva):** `adaptarArandaACanonico()` sobre
  `Bancoldex/Casos  + tareas BD junio 2026.xlsx` (hoja `Junio`, 72 filas,
  insumo real no versionado) produjo:
  - 72 casos adaptados, encabezado resuelto sin ambigüedad en la fila 0.
  - Por `TIPO_DE_CASO`: Incidente - Monitoreo 33, Requerimiento 32, Tarea 5,
    Incidente 2 — coincide exactamente con la página «Total de casos
    atendidos» del PDF de referencia y con el reconocimiento previo.
  - Por tipo canónico: `incidente` 35 (33+2, colapso correcto de monitoreo),
    `requerimiento` 32, `otro` 5.
  - Por motor: Oracle 52, SQL Server 19, WebLogic 1 — coincide con el
    reconocimiento previo.
  - SLA: 71 cumplidos, 1 no cumple, 0 nulos, cumplimiento 98,61% —
    coincide con la tabla de SLA del PDF y del reconocimiento.
  - Jerarquía separada correctamente por `.` (ejemplo verificado: `Base De
    Datos.Ejecucion de Scrips` → `['Base De Datos', 'Ejecucion de
    Scrips']`).
  - 0 casos sin fecha válida, 0 casos fuera de junio de 2026.
- **Carga real en navegador (Chrome vía herramienta de Browser, servidor
  estático local temporal solo para esta verificación — el producto sigue
  siendo `file://`, esto no cambia el entregable):**
  - `informe-accion-fiduciaria 1.html` sin `?perfil=` → título "Informe
    Gerencial · Acción Fiduciaria", `REPORTE.cliente` = "Acción Fiduciaria",
    consola sin errores de ejecución (solo un 404 preexistente y no
    relacionado de `insumos-af.js`, un script de prellenado opcional para
    autoría). **Confirma que F7a no altera el comportamiento por defecto de
    Acción Fiduciaria.**
  - `?perfil=bancoldex` → título "Informe Gerencial · Bancóldex",
    `document.querySelector('[data-perfil-texto="clienteHero"]')` =
    "BANCÓLDEX", consola sin errores de ejecución. Se detectó y corrigió en
    el camino que `tarjetas.seleccionadas: []` hacía fallar el arranque
    (ver arriba).
  - `resolverPerfil('bancoldex')`, invocado directamente en la página
    cargada, produce el objeto fusionado completo (`base` + `bancoldex`)
    con todos los campos esperados.
- **No ejecutado — pendiente:** cotejo A/B (`automatizacion/verificar_ab.py`)
  con exportaciones reales de `main`. No se considera necesario para
  cerrar F7a porque ningún código existente de GLPI/AF/Novaventa se
  modificó (solo funciones nuevas y una fusión de perfil embebido
  behavior-preserving para AF, verificada arriba en navegador); si el
  equipo prefiere el cotejo formal de todas formas, sigue pendiente.
  Tampoco se ejecutó el cotejo completo contra el PDF para los dominios de
  consolidado (indicadores, disponibilidad, backups, línea base): esos
  lectores son F7b.

## Archivos tocados

- `perfiles/base.js` (nuevo)
- `perfiles/bancoldex.js` (nuevo)
- `informe-accion-fiduciaria 1.html` (funciones nuevas: registro de
  perfiles `base`/`bancoldex`, `ID_PERFIL_ACTIVO`, `clasificarTipoAranda`,
  `adaptarArandaACanonico`, `cargarCasosAranda`; sin modificar
  `cargarGlpi`/`adaptarGlpiACanonico`/`adaptarAlertasACanonico`)
- `automatizacion/test_specs_adaptadores_fuente.py`
- `automatizacion/test_specs_perfil_cliente.py`
- `openspec/changes/2026-08-05-f7-bancoldex-aranda/` (proposal, design,
  tasks, deltas de spec de `adaptadores-fuente` y `perfil-cliente`)
- `docs/2026-08-05-f7-bancoldex-aranda.md` (este documento)
- `docs/2026-08-04-plan-multicliente.md` (tabla de estado de ejecución)

No se tocó ningún archivo productivo de `main` fuera de los listados; no se
aplicó el delta a `openspec/specs/` todavía (el change sigue abierto: falta
F7b y la coordinación de merge con F6).

## F7b — Integración real (misma fecha, sesión siguiente)

### Contexto de esta sesión

El usuario pidió explícitamente continuar con Bancóldex como prioridad
máxima y, en el camino, mostró una captura del directorio principal: un
cliente "Bancóldex" creado a través de un **administrador de clientes por
interfaz** que Codex agregó a F6 (no en el plan original de F6 —
`docs/2026-08-05-registro-persistente-clientes.md`), fallando al cargar el
consolidado con "Formato no permitido". El diagnóstico: ese cliente usaba
la plantilla de Acción Fiduciaria o Novaventa (las únicas dos que existían
entonces), que exige GLPI y hojas de consolidado con la forma de AF —
Bancóldex no tiene ninguna de las dos. Se intentó agregar `perfiles/base.js`
y `perfiles/bancoldex.js` directamente en el directorio principal para que
esa herramienta pudiera ofrecer "Bancóldex" como plantilla real; el editor
detectó que Codex modificaba `informe-accion-fiduciaria 1.html`
**activamente y en simultáneo** (diff comparado antes/después del propio
guardado). Ante esa evidencia, se preguntó al usuario cómo proceder; eligió
que el resto de F7 se completara en esta rama aislada, dejando los dos
archivos de perfil ya agregados al directorio principal tal cual, para que
el equipo los reconcilie cuando F6 cierre.

### Qué se implementó

1. **`cargarCasosOGlpi()`** — la misma entrada de archivo que hoy recibe
   GLPI despacha al adaptador de Aranda cuando el perfil declara
   `fuentes.casos`; conectada en los tres sitios que llamaban `cargarGlpi`
   directo (persistencia de insumos, restauración automática, revalidación
   al cambiar de periodo). `cargarGlpi()` no se tocó.
2. **`cargarIndicadores()` generalizado** — hoja y taxonomía de métricas
   (`definicionIndicador()`) declaradas por el perfil; sin declarar, AF
   conserva `ETIQUETA_INDICADOR` y el nombre de hoja de siempre.
3. **`cargarBackups()` generalizado** — hoja/columna declaradas por el
   perfil; sin declarar, AF conserva `'Backups'`/`'instancias'`.
4. **`cargarDisponibilidadTabla()`** — nueva, para disponibilidad por
   motor/sistema (estrategia `tabla-con-fechas`); `cargarDisponibilidad()`
   despacha a ella solo si el perfil la declara.
5. **`PERFIL.lineaBase` en `renderC3()`** — cierra el "gap preexistente" de
   F7a: un perfil con `lineaBase` declarada presenta su propia ficha
   contractual; AF, sin declararla, conserva la suya exacta.
6. **`presentarTarjetaPerfil()` / `PERFIL.tarjetas.presentacion`** — un
   perfil puede sobrescribir el resumen colapsado de una tarjeta que
   selecciona (usado por `c3`, `c4`, `c6`, `c7`, `c11`, `c12` de Bancóldex).
7. **`actualizarTarjetaBackups()` con meta configurable** — `PERFIL.metas.backups`
   nulo/no declarado se distingue de un valor real (95 % para Bancóldex).
8. **`perfiles/bancoldex.js` ampliado** — `tarjetas.seleccionadas: ['c3',
   'c4', 'c6', 'c7', 'c8', 'c8m', 'c9', 'c11', 'c12']` (sin `c5`: sus
   criterios exigen `glpi`+`alertas`, que Bancóldex no tiene; sin `c10`:
   Bancóldex no declara capacidad).

### Dos bugs reales encontrados y corregidos al verificar contra los archivos

- **Columna «BD» coincidía con un valor de fila, no con la cabecera.**
  `filaCabecera()` hace `c.includes(alias)` y se queda con la **última**
  fila que matchea. La instancia real `BCOEXCCBD27` contiene "bd" como
  subcadena, así que la cabecera resuelta era esa fila de datos, no la fila
  0. Se corrigió el lector de backups a una coincidencia exacta. Ver
  `design.md` para el detalle completo.
- **`TARJETA_PENDIENTE` era un tercer lugar con texto de AF quemado.**
  Además del `presentacion` del inventario (ya cubierto por
  `presentarTarjetaPerfil`), `actualizarTarjetasDesdeStore()` usa un mapa
  aparte para repintar una tarjeta sin cifra — con la meta de AF fija. Se
  generalizó para consultar `PERFIL.tarjetas.presentacion` también ahí.
  Verificado en navegador: antes del fix, `c6` de Bancóldex bloqueada
  mostraba "Meta 99,30%"; después, "Meta 99,98%".

### Hallazgo real (no un bug): `Disponibilidad Real` sin corte vigente

La hoja `Disponibilidad Real` existe, con su tabla por motor (MY SQL,
ORACLE, SQLSERVER, WEB LOGIC), y `cargarDisponibilidadTabla()` la resuelve
correctamente — pero sus columnas de fecha en el archivo real de
junio-2026 **solo llegan hasta jun-25**. El motor bloquea el consolidado
con un mensaje explícito, comportamiento correcto y esperado (no se
inventan cifras). **Esto es información para reportar al equipo de
Bancóldex/SETI**, no un pendiente de ingeniería.

### Verificación realizada (F7b)

- `node --check` sobre el HTML completo y sobre `perfiles/bancoldex.js` →
  sin errores, en cada iteración de esta sesión.
- `python3 -m unittest discover -s automatizacion -p 'test_*.py'` → **77
  pruebas, OK** (68 de F7a + 9 nuevas de F7b; se actualizó 1 aserción de
  F7a que dependía de la selección `['c9']` anterior).
- **Carga real en navegador con ambos archivos reales de junio-2026**
  (`Bancoldex/Data consolidada junio_Bancoldex 2026.xlsx` y `Bancoldex/Casos
  + tareas BD junio 2026.xlsx`, inyectados vía `fetch()`+`DataTransfer` al
  input real, mismo camino que usaría una persona):
  - Con el periodo del informe en junio de 2026: **indicadores** publica
    los 3 valores esperados (100 %/100 %/100 %, metas 99,98 %/97 %/99 %);
    **backups** publica 11 instancias al 100 %; **casos** (por la entrada
    de GLPI) publica 72 casos con los mismos agregados por tipo, motor y
    SLA que F7a ya había verificado por separado.
  - **disponibilidad** queda bloqueada con el hallazgo real de arriba — es
    el único error restante al cargar el consolidado completo.
  - Acción Fiduciaria, recargada en la misma sesión sin `?perfil=`: mismo
    título, `CN-21012025` en `c3`, `Meta 99,30%` en `c6`, consola sin
    errores nuevos. **F7b no altera a AF.**

### Archivos tocados (F7b, adicionales a F7a)

- `informe-accion-fiduciaria 1.html` (generalizaciones listadas arriba,
  todas con el mismo valor por defecto que AF ya tenía)
- `perfiles/bancoldex.js` (ampliado)
- `automatizacion/test_specs_adaptadores_fuente.py`,
  `automatizacion/test_specs_perfil_cliente.py` (pruebas nuevas)
- `openspec/changes/2026-08-05-f7-bancoldex-aranda/` (proposal, design,
  tasks y ambos deltas de spec, ampliados)
- Además, en el **directorio principal** (fuera de esta rama, sin
  confirmar por el usuario todavía): `perfiles/base.js`,
  `perfiles/bancoldex.js` y 4 líneas de `<script>` en
  `informe-accion-fiduciaria 1.html` — agregados antes de detectar la
  edición concurrente de Codex, dejados tal cual por decisión del usuario.

## Relevo final de Claude — disponibilidad (sesión interrumpida)

Esta sección separa la evidencia ya cerrada del experimento local y del
ajuste que quedó sin validar cuando Claude agotó sus tokens.

### Prueba controlada sin alterar el insumo real

Se creó una copia local, ignorada por Git, del consolidado:

- Original: `Bancoldex/Data consolidada junio_Bancoldex 2026.xlsx`.
- Fixture: `Bancoldex/Data consolidada junio_Bancoldex 2026
  (prueba-disponibilidad-jun26).xlsx`.

El original conserva la tabla `Disponibilidad Real` hasta junio de 2025. La
copia agrega una columna para junio de 2026 con 100 % en los cuatro motores
(`MY SQL`, `ORACLE`, `SQLSERVER`, `WEB LOGIC`). La revisión directa de ambos
libros confirma que la nueva fecha está insertada antes de `PROMEDIO` solo en
el fixture. La copia sirve para recorrer el flujo de la interfaz; **no es
evidencia del servicio ni corrige el archivo entregado por el cliente**.

Con esa copia, el lector publicó disponibilidad global 100,0 %, meta 99,98 %
y cuatro de cuatro motores en cumplimiento. La prueba descubrió un cuarto
literal de Acción Fiduciaria en el resumen colapsado de `c11`, que todavía
decía 99,30 %. Ese defecto sí quedó corregido y confirmado en el commit
`4f822c3`: el resumen ahora lee `ci.datos.meta` y conserva 99,3 % como valor
por defecto para Acción Fiduciaria.

### Interpretación correcta del modal `c6`

- `Disponibilidad SETI: sin dato` es deliberado para Bancóldex: el insumo no
  entrega una serie SETI independiente. Copiar `Disponibilidad Real` a SETI
  inventaría una equivalencia que la fuente no demuestra.
- El histórico SETI del modal queda vacío por la misma razón:
  `cargarDisponibilidadTabla()` no publica `tablas.seti.historico`. El
  histórico respaldado por la fuente es el detalle por motor de `c11`.
- La meta contractual 99,98 % aparecía como 100 % en `c6` por usar
  `pct(meta)` sin decimales. Esto es un problema de presentación, no de
  cálculo ni de lectura del Excel.

### Cambio local pendiente, no confirmado

El árbol de trabajo conserva un único cambio de código sin commit en
`informe-accion-fiduciaria 1.html`: para perfiles cuya disponibilidad usa la
estrategia `tabla-con-fechas`, el modal formatea la meta con dos decimales;
los demás perfiles mantienen el formato anterior. La intención es mostrar
99,98 % para Bancóldex sin cambiar el 99 % que hoy muestra Acción
Fiduciaria.

Claude alcanzó a iniciar la comprobación en navegador, pero encontró estado
persistido de pruebas anteriores en IndexedDB. Ese estado se restauraba al
recargar e impedía atribuir el resultado al fixture actual. La sesión terminó
antes de limpiar IndexedDB y repetir la prueba; por tanto, el cambio **no debe
considerarse validado ni listo para commit**.

### Secuencia exacta para retomar

1. Limpiar IndexedDB y cualquier estado persistido de la aplicación de
   prueba; recargar `?perfil=bancoldex` desde un estado vacío.
2. Seleccionar junio de 2026 y cargar el fixture etiquetado arriba.
3. Verificar en `c6` meta 99,98 %, disponibilidad cliente 100 % y SETI
   `Sin dato`; no fabricar histórico SETI.
4. Verificar en `c11` cuatro de cuatro motores y meta 99,98 %.
5. Recargar Acción Fiduciaria y comprobar que `c6` conserva su presentación
   anterior (meta 99 %) y que el resumen de `c11` conserva su meta real.
6. Agregar una prueba de regresión para la precisión por estrategia, ejecutar
   la suite completa y la validación sintáctica; solo entonces confirmar el
   cambio pendiente.
7. Mantener separado el fixture y reportar como hallazgo de fuente que el
   consolidado real no contiene junio de 2026 en `Disponibilidad Real`.

## Cierre Codex — Bancóldex terminado

### Insumos originales aceptados

1. `Data consolidada junio_Bancoldex 2026.xlsx`: tres indicadores al 100 %
   con metas 99,98 %/97 %/99 %, y 11 backups al 100 % con meta 95 %.
2. `Casos + tareas BD junio 2026.xlsx`: 72 casos; tipos 33/32/5/2; motores
   Oracle 52, SQL Server 19 y WebLogic 1; SLA 71/72 (98,61 %).
3. `Logros_Mitigacion_TYA Bencoldex_junio.xlsx`: 5 logros y 2 mitigaciones;
   todas las mitigaciones tienen fecha de entrega 30/06/2026.

La carga del consolidado es selectiva: el preset requiere indicadores y
backups, por lo que la tabla `Disponibilidad Real` (que termina en jun-25) no
bloquea esas dos fuentes válidas. El fixture que agrega jun-26 solo documenta
la capacidad del lector; nunca se usa como evidencia del informe.

### Presentación final

- `c3`: contrato `CN-2024112`, 257 activos y vigencia hasta 14/11/2026,
  respaldados por el PDF aprobado. La hoja Excel de línea base no reemplaza
  esa evidencia porque sus totales 220/161 contradicen 237/257 del PDF.
- `c4`: indicadores del servicio con las metas contractuales de Bancóldex.
- `c5`: reutiliza la tarjeta, el modal y la gráfica apilada de Acción
  Fiduciaria. Se añadieron una dona por motor, barras por categoría, SLA y
  análisis narrativo. No contiene tablas de Excel ni exporta filas/IDs de
  tickets.
- `c7`: 11 bases de datos, ejecución de backups 100 %, meta 95 %.
- `c8`/`c8m`: el mismo libro mensual alimenta Logros y Mitigación.

No se seleccionan `c6/c11` (disponibilidad original desactualizada), `c9`
(TYA de sep-25 sin horas contratadas/saldo para jun-26) ni `c12` (sin insumo
mensual exportable). Son exclusiones basadas en evidencia, no pendientes del
entregable.

### Errores de integración corregidos

- El paquete automático `insumos-af.js` ya no se procesa para perfiles con
  fuente propia de casos; no puede cambiar junio Bancóldex por julio de Acción
  Fiduciaria.
- El periodo se fija sin revalidación antes de restaurar IndexedDB. Tras una
  recarga, junio-2026 y los tres archivos reaparecen por la misma ruta de
  validación manual.
- El HTML de cliente rehidrata casos Aranda, indicadores, backups y
  cualitativos desde el estado embebido; la entrega no depende de los Excel,
  IndexedDB ni de un servidor.

### Evidencia final

- Navegador real: dashboard de seis tarjetas, periodo junio-2026, centro de
  carga 2/2 fuentes obligatorias y exportaciones habilitadas.
- Modal de casos: 72 total, 98,61 % SLA, gráficas por tipo/motor/categoría y
  análisis automático con cifras consistentes.
- Recarga completa: periodo e insumos restaurados sin contaminación del
  paquete AF.
- Suite: 84 pruebas correctas.
- Sintaxis: perfiles y bloques JavaScript internos válidos.
- Formato: `git diff --check` sin errores.

Lo único no ejecutado por decisión de alcance es publicar la rama o abrir un
PR; requiere una instrucción separada del equipo.
