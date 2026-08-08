# Diseño — F7 adaptador Aranda y perfil Bancoldex

## Addendum del 06/08/2026 — port quirúrgico sobre `codex/f6-perfil-novaventa`

Todo lo que sigue en este archivo describe el trabajo original en
`codex/bancoldex-completo`, que no se remergea literalmente — ver la nota de
alcance en `tasks.md`. Esta sección documenta las decisiones **nuevas** del
port, que F7 nunca enfrentó porque nunca declaró `fuentes.alertas` para
Bancoldex.

### Interacción AlertsList × Aranda (hallazgo del 06/08/2026)

`publicarCasos()` y el tramo final de `cargarAlertas()` (escritura de
`DATA_CASOS.alertas`, los párrafos de `#s5 .parrafos` y `chartCasos`) están
escritos para el modelo AF/Novaventa: un caso "atendido" es
`alertas + requerimientos + incidentes`, con GLPI y AlertsList como las dos
fuentes obligatorias del mismo dominio `casos`. Ambas funciones corren
**incondicionalmente** al final de `cargarAlertas()`, sin importar qué
perfil esté activo.

Al declarar `fuentes.alertas` para Bancoldex (necesario para que el usuario
pueda cargar su AlertsList), esa combinación se vuelve alcanzable por primera
vez: Bancoldex ya tenía su propio dominio `casos` (`modo:'aranda-tipo-motor'`,
publicado por `cargarCasosAranda()`), y cargar un AlertsList después lo
sobrescribía con el objeto `{estado:'no_cargado', notas:['Requiere AlertsList
y GLPI...']}` de `publicarCasos()` (Bancoldex nunca publica en el dominio
`glpi`, así que `REPORTE.resuelto('glpi')` es `false` y esa función cae
siempre en la rama temprana) — y el chart/párrafos del slide `s5`, que
`pintarCasosArandaEnSlide()` ya había pintado, se sobrescribían con prosa y
series de "alertas" sin relación con Aranda.

**Resolución:** dos guards mínimos, ambos con el mismo predicado
(`PERFIL.fuentes?.casos`, ya usado en `cargarCasosOGlpi()` y en el guard de
`insumos-af.js`) para no introducir un tercer criterio:

1. `publicarCasos()` retorna de inmediato si `PERFIL.fuentes?.casos` — el
   dominio `casos` de un perfil con fuente propia de casos no lo gestiona
   esta función.
2. El bloque de `cargarAlertas()` que pinta `DATA_CASOS`/`#s5`/`chartCasos`
   solo corre si `!PERFIL.fuentes?.casos`. Lo que queda sin condición:
   validar el archivo, contar alertas del periodo, publicar el dominio
   `alertas` (`REPORTE.publicar('alertas',...)`) y marcar el insumo como
   cargado — es decir, AlertsList **sí se interpreta** para Bancoldex
   (cuenta, queda validado, dispara avisos si hay 0 registros), solo que no
   intenta dibujar el slide legado de AF.

Con `PERFIL.fuentes?.alertas` sin declarar (AF/Novaventa), ambos guards son
no-op: la condición siempre evalúa igual que antes de este cambio, 0 diff.

### `c5.configuracion` debe declarar `alertas` aunque no alimente su cifra (hallazgo en navegador)

Al probar end-to-end con los tres insumos reales de junio-2026 más un
AlertsList sintético, dos fallos aparecieron que ningún test estático había
cubierto porque dependen de qué tarjetas están *seleccionadas*, no solo de
qué código existe:

1. `REPORTE.publicar('alertas',...)` lanzaba `"Dominio desconocido: alertas"`.
   `REPORTE.dominios` se inicializa desde `DOMINIOS`, la unión de
   `tarjeta.dominios` de las tarjetas seleccionadas. Al declarar
   `c5.configuracion.dominios: ['casos']` (sin `'alertas'`), ningún dominio
   registrado para Bancoldex se llamaba `alertas`.
2. `validarArchivo('alertas',file)` rechazaba cualquier extensión con
   `"Formato no permitido: «archivo». Usa ."` (lista vacía). Igual que arriba:
   `EXTENSIONES_INSUMO` solo registra una fuente si algún `tarjeta.fuentes`
   seleccionado la declara; `c5.configuracion.fuentes: ['glpi']` (sin
   `'alertas'`) dejaba a esa fuente sin extensiones permitidas.

**Resolución:** `c5.configuracion` declara `dominios: ['casos','alertas']` y
`fuentes: ['glpi','alertas']` — Aranda sigue siendo la única fuente que
alimenta la *cifra* de `c5` (los guards de la sección anterior lo garantizan),
pero `'alertas'` debe seguir registrada como dominio/fuente válida porque dos
mecanismos genéricos del motor la refieren por nombre exacto:
`actualizarVisibilidad()` (`c5:!!CARGA.glpi&&!!CARGA.alertas`, que decide si
la diapositiva `s5` se muestra en el entregable) y `EXTENSIONES_INSUMO`. Esto
también confirma, con evidencia real, que el diseño original de exigir
AlertsList además de Aranda para Bancoldex es intencional y correcto: son dos
insumos obligatorios independientes, igual que para AF/Novaventa.

### `cargarInsumosAutomaticos()` no debe autocargar el paquete de otro cliente (hallazgo en navegador)

Al abrir Bancoldex en un equipo con `insumos-af.js` presente junto al HTML
(archivo de desarrollo local, gitignored, con datos reales de Acción
Fiduciaria), el periodo del informe saltó de junio a julio de 2026 sin que el
usuario cargara nada — `cargarInsumosAutomaticos()` no tenía guard alguno por
perfil y cargaba ese `<script>` vecino sin importar cuál estuviera activo.
Mismo predicado que ya usan `cargarCasosOGlpi()` y el guard de `publicarCasos()`:
`if(PERFIL.fuentes?.casos) return;` al inicio de la función. AF/Novaventa (sin
`fuentes.casos`) conservan la extracción automática exactamente como antes.

### Incidentes atribuibles a SETI: no se toca ese apartado (lineamiento del usuario, 06–07/08/2026)

**Regla para cualquier sesión futura que toque el modal de `c5` (dashboard
"Detalle del indicador" → "Total de casos atendidos") de Bancoldex/Aranda:**
el panel `case-analysis` (columna derecha del `case-command`) debe
reproducir **exactamente** el de Acción Fiduciaria:

- Título literal `Incidentes atribuibles a SETI` — no renombrarlo (se
  intentó `"Cumplimiento e incidentes reales"` y `"Incidentes reales"`; el
  usuario lo rechazó las dos veces).
- **Un solo** `.case-seti` dentro de ese panel. Nada más ahí — ni un segundo
  badge de SLA, ni una fila `.case-analysis__badges`, ni una nota adicional.
  El usuario fue explícito: *"ahí no debe haber más nada que eso"*.
- El cumplimiento de SLA (`x.sla`) **no vive en este panel**. Tiene su
  propio panel en la grilla de desgloses, con gauge circular — ver más abajo.

**Por qué "Incidentes atribuibles a SETI" y no otra cosa:** es el mismo
concepto que ya usa el `renderC5()` no-Aranda (rama `metricasCasos(x)` /
`m.atribuiblesSeti`), y el usuario quiere que Bancoldex se lea igual que
Acción Fiduciaria en ese punto, no una variante con nombre propio.

**Qué cifra usar ahí (pendiente, deliberadamente sin resolver):** AF calcula
`atribuiblesSeti` cruzando los incidentes de GLPI contra el log de
indisponibilidades (`RECONCILIACION_INDISPONIBILIDADES`, un «SI» explícito
por caso). Aranda no tiene un mecanismo equivalente todavía. Como cifra
provisional se usa `incidentesReales` (`cargarCasosAranda()`: casos con
`categoria` exactamente `'Incidente'`, excluyendo `'Incidente - Monitoreo'`
— el mismo principio de no contar ruido de monitoreo automático como falla,
pero **sin** cruce de atribución real). **El usuario pidió explícitamente
revisar en otra sesión cómo validar qué incidentes de Aranda son
"atribuibles a SETI"** (¿existe un log de indisponibilidades para Bancoldex?
¿lo es el CAUSA/RAZON del export? ¿algo del ESTADO/GRUPO_ESPECIALISTA?) —
no inventar esa validación sin evidencia real, y no dar por cerrado este
punto hasta que se defina con el usuario.

**Dónde vive el SLA en su lugar:** panel propio `"Cumplimiento del SLA"` en
la grilla de desgloses (`dash-layout--tres`, junto a "Casos por tipo" y
"Casos por motor"), con un gauge circular (`gauge(label,value,meta)` —
componente `.gauge-exec`/`.gauge-row` que ya existía en el motor,
**sin ningún consumidor hasta esta sesión**: se usó tal cual en vez de un
badge de texto, siguiendo el pedido de "gráficas más cheveres, no solo
reordenar lo mismo"). `meta` se pasa en `100` (cumplimiento pleno) porque
Bancoldex no declara una meta contractual de SLA de casos distinta.

**Feedback general de esta iteración, para no repetirlo:** la primera
versión del rediseño (commit anterior a esta corrección) solo reorganizó
los mismos tipos de gráfica (bar/donut) sin aportar una visualización
distinta, y encima reinterpretó "incidentes atribuibles a SETI" como un
concepto nuevo ("incidentes reales") en vez de dejarlo intacto. Las dos
cosas se rechazaron. Antes de tocar este modal otra vez: (1) no renombrar
ni reinterpretar paneles que ya existen en el motor para otro perfil sin
pedirlo explícitamente, (2) buscar componentes de visualización ya
construidos y sin usar (como `gauge-exec`) antes de reciclar el mismo tipo
de gráfica.

### El cliente se escribe «Bancoldex», sin tilde (lineamiento del usuario, 07/08/2026)

**Regla:** en este repositorio el nombre del cliente es `Bancoldex` —
nunca `Bancóldex`. Aplica a las cadenas visibles del entregable
(`perfiles/bancoldex.js`: `nombre`, `textos.tituloDocumento`,
`textos.marcaTopbar`, `textos.clienteHero`, `textos.confidencialidad`) y
también a comentarios, specs, `tasks.md` y documentos de sesión, para que
una búsqueda por el nombre encuentre todo.

El usuario lo corrigió explícitamente. La grafía oficial de la entidad
lleva tilde, así que la ortografía «correcta» aquí es una trampa: quien
escriba el nombre por primera vez tenderá a acentuarlo. Por eso queda
escrito como regla y no como detalle de estilo. Si alguna sesión futura
reintroduce la tilde, corregirla en el mismo commit.

Verificación: `grep -rn "Banc[óÓ]ldex" --include="*" .` (excluyendo `.git/`,
`.claude/worktrees/` y `_tmp_main_ab/`) sólo debe devolver los sitios que
**enuncian la regla** — esta sección, `TASKS.md`, el `tasks.md` de este
change y `docs/2026-08-07-verificacion-visual-y-nombre-bancoldex.md`. Una
ocurrencia en cualquier otro archivo es una regresión.

### El rótulo del gauge no puede cruzar el anillo (hallazgo de la verificación visual, 07/08/2026)

`.gauge-exec` es un grid de 150 × 150 px con `place-content:center` y sin
padding: el `<span>` del rótulo se estiraba a los 150 px completos, así que
«Cumplimiento SLA · meta 100%» quedaba pisando el anillo de color por los
dos costados. El componente existía en el motor desde antes pero **nunca se
había renderizado**, así que el defecto no se había visto nunca — sólo salió
al mirar el modal, no al inspeccionar el DOM.

Corrección: `padding:0 26px` en `.gauge-exec`. Confina el texto al círculo
blanco interior que dibuja el `:before` (`inset:10px`, radio 65 px). Medido
en navegador tras el cambio: la esquina de texto más lejana queda a 55,7 px
del centro. Cubierto por
`test_gauge_exec_reserva_espacio_lateral_para_el_rotulo`.

Es un cambio de una regla CSS sin ningún otro consumidor (`gauge()` sólo se
invoca desde la rama `aranda-tipo-motor` de `renderC5()`), así que no altera
la salida de Acción Fiduciaria.

**Moraleja operativa:** confirmar el DOM por `innerText` no sustituye mirar
la pantalla. Las cifras estaban bien desde la sesión anterior; lo que estaba
mal era invisible por texto.

### `actualizarTarjetaCasos()` — dispatch por modo, no por perfil

Varios sitios llaman `actualizarTarjetaCasos()` directamente sin conocer el
perfil activo (reconciliación de indisponibilidades, autopruebas,
`cargarAlertas`). En vez de parchar cada sitio, la función misma revisa
`REPORTE.d('casos').datos?.modo` y delega en `actualizarTarjetaCasosAranda()`
cuando corresponde — igual patrón que ya usa `actualizarTarjetasDesdeStore()`
en `codex/bancoldex-completo`, aplicado en un solo lugar en vez de repetirlo
en cada llamador.

## F7b — lectores de consolidado (hallazgos al verificar contra los archivos reales)

### Bug real: coincidencia de columna «BD» con datos, no con la cabecera

`cargarBackups()` generalizado usaba `filaCabecera()` para ubicar la fila
con la columna declarada (`'bd'` para Bancoldex). `filaCabecera()` hace
`c===a||c.includes(a)` y **se queda con la última fila que matchea**, no la
primera. La instancia real `BCOEXCCBD27` normaliza a `bcoexccbd27`, que
`.includes('bd')` — así que la "cabecera" resuelta era la primera fila de
datos, no la fila 0 real. Se corrigió a una búsqueda de coincidencia
**exacta** (`norm(c)===nombreColBackups`) en vez de reusar `filaCabecera()`
para este lector. Verificado contra `Bancoldex/Data consolidada
junio_Bancoldex 2026.xlsx`: 11 BD, promedio 100 %, coincide con la hoja
real.

### Hallazgo real: `Disponibilidad Real` sin corte vigente

La hoja existe y su tabla («DISPONIBILIDAD REAL», filas por motor: MY SQL,
ORACLE, SQLSERVER, WEB LOGIC) se resuelve correctamente con
`cargarDisponibilidadTabla()`, pero sus columnas de fecha en el archivo de
junio-2026 solo llegan hasta **jun-25** — un año de rezago en el propio
archivo del cliente, no un error de lectura. El motor bloquea el
consolidado con `"La tabla «Disponibilidad Real» no tiene una columna para
jun-26."`, comportamiento correcto (la restricción inviolable #2 exige no
inventar cifras). **Queda como hallazgo para reportar a Bancoldex/SETI**,
no como pendiente de este change.

### Cuarto lugar con texto de AF quemado: resumen de `c11`

Al probar con un consolidado completo (insumo real + una columna de prueba
de junio-2026 con disponibilidad 100 %, ver docs de sesión), el resumen
colapsado de `c11` seguía diciendo *"4 de 4 cumplen la meta de 99,30%"* —
un literal dentro de `actualizarTarjetasDesdeStore()`, distinto de
`presentarTarjetaPerfil()` (que ya cubre el texto por defecto de la
tarjeta) y de `TARJETA_PENDIENTE` (que cubre el estado sin cifra). Se
corrigió a leer `ci.datos.meta` (que `cargarDisponibilidadTabla()` ya
publica desde `PERFIL.metas.disponibilidad`), con el mismo valor 99,3 %
como default cuando el dominio no lo declara — AF sin cambios.

### Precisión de la meta en el modal `c6` (soporte fuera del preset final)

La prueba controlada con una copia del consolidado que agrega junio de 2026
mostró que `c6` redondea la meta 99,98 % a 100 % mediante `pct(meta)`. Esto
vuelve visualmente indistinguibles la meta contractual y un cumplimiento
perfecto. El árbol de trabajo contiene una solución local: usar dos decimales
cuando la estrategia declarada es `tabla-con-fechas` y conservar el formato
existente en los demás perfiles.

La decisión semántica es independiente del formato: Bancoldex debe seguir
mostrando SETI `Sin dato` y sin histórico SETI, porque la fuente solo respalda
`Disponibilidad Real` por motor. No se copiará esa serie a SETI para llenar el
modal. El formato a dos decimales se conserva como soporte para la estrategia
`tabla-con-fechas`, pero `c6`/`c11` se excluyen del preset final: el único
libro original termina en jun-25 y el fixture con jun-26 no es evidencia. Por
ello esta ruta no bloquea ni aporta cifras al informe Bancoldex entregable.

### Tercer lugar con texto de AF quemado: `TARJETA_PENDIENTE`

Además del `presentacion.items` de `INVENTARIO_TARJETAS` (ya cubierto por
`presentarTarjetaPerfil()`), `actualizarTarjetasDesdeStore()` usa un mapa
aparte, `TARJETA_PENDIENTE`, para repintar una tarjeta cuando su dominio
sigue sin cifra — con el texto de meta de AF quemado ("Meta 99,30%..."). Se
verificó en navegador: con `disponibilidad` bloqueada (hallazgo anterior),
la tarjeta `c6` de Bancoldex mostraba la meta de AF. Se generalizó
`TARJETA_PENDIENTE` para consultar el mismo
`PERFIL.tarjetas.presentacion[id]` antes de usar su valor por defecto.

### Por qué `PERFIL.lineaBase` no lee la hoja «Linea Base»

El reconocimiento identificó que `Linea Base` trae `AMBIENTE` y dos columnas
`CANTIDAD` (contrato vs. corte). No se escribió un lector para esa hoja en
F7b: `PERFIL.lineaBase` (usado por `renderC3()`, heredado de la rama F6)
es una declaración **estática** del perfil, verificada a mano contra la
página «Control línea base» del PDF de referencia (Total General 237→257),
igual que ya lo es para AF y Novaventa. Ningún perfil, incluido Bancoldex,
tiene hoy un lector dinámico de esa hoja — construirlo sin un segundo
cliente que lo justifique violaría la regla de `project.md`.

## `perfiles/base.js`

Hasta ahora `PERFILES_REGISTRADOS` solo resuelve `accion-fiduciaria` (raíz) y
`novaventa` (hereda de AF). El plan maestro reserva `base` para un cliente
que no comparte lo suficiente con ningún perfil existente. `base` no
representa a ningún cliente: no tiene `aliasCliente` de negocio, sus metas y
tarjetas quedan vacías/mínimas, y cualquier perfil que lo use debe declarar
todo lo propio. Se registra igual que los demás, con `extiende: null`, para
que `resolverPerfil('base')` funcione y la cadena de Bancoldex
(`bancoldex → base`) no sea un caso especial en `resolverPerfil()`.

## Selección de perfil activo por `?perfil=` (hallazgo, no planeado)

Al verificar en navegador se encontró que en el cierre de F5
`const PERFIL = resolverPerfil('accion-fiduciaria');` estaba **fijo** — no
existía el mecanismo `ID_PERFIL_ACTIVO` que lee `?perfil=` de la URL (ese
mecanismo se agregó después, en la rama F6, que este change no incluye por
partir del cierre de F5). Sin él, `base`/`bancoldex` quedan registrados pero
inalcanzables: no hay forma de cargar el motor con otro perfil que no sea
Acción Fiduciaria. Se agrega la misma resolución `PERFIL_EMBEBIDO?.id ||
new URLSearchParams(location.search).get('perfil') || 'accion-fiduciaria'`
que ya usa (independientemente) la rama F6, así que ambas ramas convergerán
al mismo texto en este punto al mezclarse — un conflicto de mezcla trivial,
no una divergencia de comportamiento. Sin `?perfil=` ni perfil embebido, el
resultado es exactamente `'accion-fiduciaria'`: mismo comportamiento que
antes para Acción Fiduciaria.

## `perfiles/bancoldex.js`

Extiende `base`. Declara (datos, sin funciones):

- `contrato`, `metas.disponibilidad = 0.9998` (evidencia del reconocimiento).
- `fuentes.casos` (ver abajo) — **no** `fuentes.glpi`: Bancoldex no tiene GLPI.
- `almacen.prefijo = 'informeBancoldex'`.
- `textos` con las mismas claves que ya usan AF/Novaventa.
- `tarjetas.seleccionadas: ['c3','c4','c5','c7','c8','c8m']`. Es el preset
  de cierre respaldado por el PDF aprobado y los tres libros originales del
  corte. `c6`/`c11` quedan fuera por disponibilidad desactualizada; `c9` por
  un TYA de otro periodo sin contrato/saldo; `c12` por no existir insumo
  mensual exportable. Ninguna tarjeta vacía se usa como relleno.

## Fuente `casos` (Aranda)

```js
casos: {
  lector: 'tabular-xlsx',
  adaptador: 'aranda-export',
  // Alias ya normalizados (minúsculas, espacio en vez de guion bajo): ver
  // "Alias de columna: normalizados, no literales" más abajo.
  cabecera: {estrategia: 'primera-fila-con', campos: [['numero del caso'], ['fecha registro']]},
  columnas: {
    id: ['numero del caso'], tipoCaso: ['tipo de caso'], jerarquia: ['jerarquia'],
    cumplimiento: ['indicardor de cumplimiento'], // typo real de la fuente, no se corrige
    fecha: ['fecha registro'], motor: ['motor'],
  },
  filtroCliente: {estrategia: 'archivo-alcance-unico'},
  jerarquia: {separador: '.'},
  sla: {estrategia: 'columna-cumplimiento', verdaderos: ['cumple'], falsos: ['no cumple']},
}
```

### Alias de columna: normalizados, no literales (hallazgo al verificar)

`col()`/`candidatosCabecera()` comparan `norm(celda)` contra el alias **tal
cual está escrito en el perfil** — el alias mismo no pasa por `norm()`. La
primera versión de este perfil declaró `['numero_del_caso']` (calcado del
nombre de columna real, con guion bajo) y `resolverCabecera()` no encontró
ninguna fila candidata: `norm('NUMERO_DEL_CASO')` da `'numero del caso'`
(guion bajo → espacio), que nunca es igual ni contiene
`'numero_del_caso'`. Los alias de AF/Novaventa ya siguen esta convención
(`'fecha de apertura'`, `'tiempo para resolver excedido'`) porque sus
columnas reales ya usan espacios; Aranda es la primera fuente con guiones
bajos, así que es la primera vez que el detalle importa. Se corrigió a
`['numero del caso']`, `['tipo de caso']`, `['fecha registro']` y se
verificó con el arnés Node de este change (ver "Verificación de F7a")
contra el export real: encabezado resuelto en la fila 0, 72 filas
adaptadas.

### `cargarCasosAranda()` publica en el dominio compartido `casos`

El cierre configura `c5` declarativamente con `dominios: ['casos']`; por eso
`DOMINIOS` incorpora el destino sin agregar una segunda lista fija.
`cargarCasosAranda()` publica un objeto `modo: 'aranda-tipo-motor'` con
agregados por tipo, motor, categoría de requerimiento y SLA. El store no
persiste ni exporta identificadores o filas crudas de tickets: el entregable
solo recibe los agregados necesarios para explicar las gráficas.

`renderC5()` conserva la tarjeta, el modal y el componente
`montarHistorico()` de Acción Fiduciaria. La adaptación Bancoldex agrega una
dona por motor, barras horizontales por categoría y un análisis narrativo;
no presenta tablas de Excel. Con un único corte real no se inventan meses
históricos: la barra apilada muestra solo jun-26.

### Por qué `adaptador: 'aranda-export'` y no una nueva `PERFIL.fuentes.glpi`

`cargarGlpi()` (línea ~3330) es una función de ~150 líneas ya cargada de
reglas propias de AF/Novaventa: cruce con
`RECONCILIACION_INDISPONIBILIDADES`, exclusión de "revisiones de alerta",
escritura directa en `#s4 tbody`, y los arreglos `DATA_CASOS.requerimientos` /
`.incidentes` (dos series, no cuatro). Generalizarla para Bancoldex — 4 tipos,
sin revisiones de alerta, sin indisponibilidades — sería reintroducir ramas
por cliente dentro de una función que hoy es literal-AF, exactamente lo que
`project.md` prohíbe ("ningún archivo `informe-<cliente>.html` con lógica
propia" aplicado a una función en vez de un archivo). Se prefiere una función
nueva, paralela, que comparte los mismos primitivos de F5
(`casoCanonico()`, `resolverCabecera()`, `col()`) sin tocar la existente. La
integración con la interfaz (qué botón, qué tarjeta) es F7b porque necesita
su propio diseño visual, no una reutilización forzada de `#s4`.

### Decisión de alcance de cliente: archivo de alcance único

El reconocimiento descartó filtrar por `Proyecto` (siempre "Mesa de Servicios
TI.", cero casos) y por `COMPANIA` (pierde 8 de 72 filas reales que el PDF sí
cuenta). Se declara `filtroCliente.estrategia = 'archivo-alcance-unico'`: el
adaptador acepta todas las filas del archivo tal como Aranda lo entrega,
porque el export ya es específico de Bancoldex — la identidad del cliente la
garantiza el perfil seleccionado en el centro de carga, no una columna. Un
archivo que mezclara clientes no tiene hoy una señal fiable para separarlos
(ver "Pendiente pequeño" abajo); por eso esta estrategia se implementa como
paso-a-través explícito y documentado, no como filtro adivinado.

### Clasificador `aranda-por-tipo-de-caso`

A diferencia de `clasificarTipoGlpi()` (que infiere de categoría con regex),
Aranda declara el tipo directamente en `TIPO_DE_CASO`. El canónico solo
admite `requerimiento|incidente|alerta|cambio|caso_bd|otro`
(`TIPOS_CASO_CANONICO`, línea 2153); la hoja `Junio` trae
`Incidente - Monitoreo`, `Requerimiento`, `Tarea`, `Incidente`. Mapeo:

| `TIPO_DE_CASO` | `CasoCanonico.tipo` |
|---|---|
| `Requerimiento` | `requerimiento` |
| `Incidente`, `Incidente - Monitoreo` | `incidente` |
| `Tarea` | `otro` |
| cualquier otro valor | `otro` (se registra en notas, no falla) |

`Incidente` e `Incidente - Monitoreo` colapsan al mismo tipo canónico porque
el canónico no distingue monitoreo — esa distinción es visual (F7b) y se
recupera de `categoria`/`jerarquia`, que conservan el texto original de
`TIPO_DE_CASO`. No se agrega un séptimo valor a `TIPOS_CASO_CANONICO` sin un
segundo cliente que lo necesite (regla dura de `project.md`).

### SLA `columna-cumplimiento`

```
'Cumple' → true, 'No cumple' → false, vacío o cualquier otro valor → null
```

Paralela a `columna-excedido` (que invierte un booleano de "excedido"),
`columna-cumplimiento` lee directamente un booleano de "cumplido". Ambas
estrategias son casos de la misma regla dura ya vigente en
`metricasSlaCanonico()`: solo `true` cuenta. Con los 72 casos reales, 71
`Cumple` + 1 `No cumple` + 0 vacíos coincide con la tabla de SLA del
reconocimiento.

### `cabecera-de-dos-filas` (declarada, no implementada en F7a)

El `Indicador` de Bancoldex tiene meses en la fila 2 y `BANCOLDEX|SETI` en la
fila 3. `resolverCabecera()` (línea 2146) solo soporta `primera-fila-con` y
lanza si se le pide otra estrategia — comportamiento correcto y ya probado.
F7a **no** implementa esta estrategia todavía: no hay lector de consolidado
que la use hasta F7b. Queda declarada aquí para que F7b no tenga que
rediseñarla, y su ausencia de código no bloquea F7a porque nada la invoca
todavía.

## Cierre end-to-end

### Consolidado selectivo

El cargador ejecuta únicamente los lectores cuyos dominios pertenecen al
preset activo. Para Bancoldex procesa `indicadores` y `backups`, pero no
invoca la tabla `Disponibilidad Real` desactualizada. Así un dominio excluido
no bloquea evidencia válida de otro dominio del mismo libro.

### Un libro cualitativo, dos dominios

La fuente `cualitativos` declara una sola entrada y las hojas exactas
`Logros`/`Mitigación`. El lector publica ambos dominios y exige que todas las
fechas de entrega de mitigaciones pertenezcan al periodo seleccionado. Esta
decisión evita pedir dos archivos artificiales y conserva la validación del
corte.

### Restauración y periodo

En el arranque, `aplicarPeriodo({revalidarInsumos:false})` fija el periodo sin
revalidar antes de que IndexedDB restaure los archivos. Después cada insumo se
procesa por su ruta normal. Además, el paquete automático `insumos-af.js` se
omite cuando el perfil declara una fuente propia de casos; de otro modo los
insumos de Acción Fiduciaria podían reemplazar junio de Bancoldex por julio.

### Salida autocontenida

El estado exportable rehidrata indicadores, casos Aranda, backups, logros y
mitigaciones antes de pintar tarjetas y gráficas. El perfil y los agregados
viajan embebidos; no se requieren Excel, IndexedDB ni un servidor en la
entrega al cliente.

## Gap preexistente: diapositivas «constantes» no dependen de la selección

Verificando en navegador con `?perfil=bancoldex` se confirmó que `c3` (línea
base) y `c9` (bolsa) son diapositivas «constantes»: `actualizarVisibilidad()`
solo alterna `display` para `c4,c5,c6,c7,c8,c8m,c11` (según si su dominio
tiene datos); `c3`/`c9`/`c12` quedan siempre visibles, y `renderAll()` solo
ejecuta el renderizador de una tarjeta si está en `TARJETAS_SELECCIONADAS`.
Como Bancoldex no selecciona `c3`, `renderC3()` nunca corre y la diapositiva
conserva su marcado estático original — incluido `text('[data-k="contrato"]')
||'21012025'`, un campo editable por el consultor en el DOM (no derivado de
`PERFIL.contrato`, a diferencia de `contrato.inicio` que F2 sí migró). Esto
**no es un defecto de F7a**: es una brecha preexistente de la migración
multicliente — ninguna fase anterior extrajo el código de contrato/
instancias/bases de datos de `c3` a datos del perfil, así que cualquier
cliente nuevo hereda el mismo texto de Acción Fiduciaria hasta que el
consultor lo edite a mano en el Centro de carga, igual que ya debe hacer con
otros campos hoy. Seleccionar solo `c9` para Bancoldex evita agregar
diapositivas *nuevas* con contenido incorrecto (p. ej. `c5` diría «Requiere
AlertsList y GLPI del periodo», falso para Bancoldex) sin pretender resolver
esta brecha ya existente, que queda anotada como pendiente para cuando se
extraiga `c3` a datos del perfil (ningún change lo ha hecho todavía para
ningún cliente, incluida Novaventa).

## Verificación de F7a

Con fixtures sintéticos (mismos nombres de columna y los mismos dos valores
de SLA que la fuente real, contenido inventado) más una comparación puntual
contra el export real de `Bancoldex/Casos  + tareas BD junio 2026.xlsx`
(nunca versionado): 72 casos, agregados por tipo y por motor, y SLA 71/1
coinciden con `Bancoldex/reporte-bancoldex-2026-07-02.pdf`. Acción Fiduciaria
y Novaventa no tienen ninguna línea de código modificada por este change —
solo funciones nuevas — así que no se requiere `verificar_ab.py` para F7a
(no hay superficie de regresión); se documenta igual como evidencia de que
la suite existente sigue en verde.

## Pendiente pequeño registrado

Si en el futuro aparece un export de Aranda con más de un cliente mezclado,
`archivo-alcance-unico` no lo detecta y el resultado sería incorrecto en
silencio. No se resuelve aquí porque no hay evidencia real de ese caso
(regla de "dos clientes con evidencia real" de `project.md`); si ocurre, la
fuente `casos` deberá declarar `filtroCliente.estrategia` con una columna y
regla nuevas, verificadas contra esa evidencia.

### `tarjeta.fuentes` solo alimenta el mapa de extensiones (hallazgo del 07/08/2026)

`tarjeta.fuentes` tiene **un único consumidor en todo el motor**: el mapa de
extensiones de archivo admitidas por insumo. No controla visibilidad, ni
criterios, ni qué cargador corre.

Consecuencia práctica, y trampa real en la que ya se cayó: reapuntar la
fuente de una tarjeta para expresar «estos dos insumos vienen en el mismo
archivo» no expresa nada — solo deja al insumo original sin ninguna extensión
válida, y su entrada de archivo pasa a rechazar todo con la lista vacía
(«Formato no permitido: …. Usa .»).

`perfiles/bancoldex.js` llegó a declarar `c8m: {fuentes: ['logros']}` con esa
intención. Se retiró el 07/08/2026. Que el libro sea uno solo se declara con
`fuentes.cualitativos.alcance: 'archivo-alcance-unico'`, que es lo que leen
`cargarLogrosArchivo()` y `cargarMitigacionesArchivo()`.

**Regla:** un perfil declara en `tarjetas.configuracion.<id>.fuentes`
únicamente las fuentes cuya **entrada de archivo** alimenta esa tarjeta.

Nota sobre `c5`: ahí sí es correcto declarar `fuentes: ['glpi','alertas']`,
porque las dos entradas de archivo alimentan esa tarjeta. No es el mismo
caso.

### Las extensiones admitidas se resuelven al validar, no al parsear (hallazgo del 07/08/2026)

`EXTENSIONES_INSUMO` era un `const` calculado una sola vez al parsear la
página. `TARJETAS_SELECCIONADAS` se reasigna después —`restaurarPresetTarjetas()`
y la UI de «Tarjetas»—, así que el mapa quedaba obsoleto para el resto de la
sesión. Comprobado en vivo: quitar `c5` del preset no cambia ninguna clave.

Es un defecto del motor, no de Bancoldex: cualquier tarjeta agregada por la
interfaz cuya fuente no estuviera en el preset inicial habría producido el
mismo mensaje sin formatos.

Corregido convirtiéndolo en la función `extensionesInsumo()`, resuelta en
cada validación — el mismo criterio que `dominiosActivos()`, que siempre se
calculó dentro de la función. `validarArchivo()` además respalda contra
`EXTENSIONES_POR_FUENTE`: una entrada que se le ofrece al usuario nunca debe
rechazar con una lista de formatos vacía.

**Al agregar una constante derivada de `TARJETAS_SELECCIONADAS`, hacerla
función.** El preset cambia en tiempo de ejecución.

### El consolidado no alimenta a un perfil con fuente propia de casos (hallazgo del 07/08/2026)

`cargarCasos()` (hoja «Casos» del consolidado) implementa el modelo
alertas/requerimientos/incidentes de AF. Corría también para Bancoldex, cuyo
consolidado sí trae esa hoja, y escribía sobre `chartCasos.data.datasets[0..2]`
— que para entonces `pintarCasosArandaEnSlide()` ya había reemplazado por una
serie por tipo de caso.

Con 3 series o más corrompía en silencio las cifras de Aranda; con el gráfico
vacío (periodo sin casos) lanzaba un `TypeError` que abortaba el `try` de
`cargarConsolidado()` entero y bloqueaba la exportación.

Corregido con el mismo guard que ya usan `publicarCasos()` y el bloque de
repintado de `cargarAlertas()`:
`if(PERFIL.fuentes?.casos){ alertasConsolidadoMes=null; return null; }`.

**El patrón, ya en tres sitios y vale como regla:** todo lo que escriba sobre
el dominio `casos`, sobre el slide `s5` o sobre `chartCasos` con el modelo de
AF debe preguntar antes si el perfil declara `fuentes.casos`. Si aparece un
cuarto sitio, lleva el mismo guard.

### Un libro cualitativo de alcance único acredita los dos insumos (07/08/2026)

Las ramas `archivo-alcance-unico` de `cargarLogrosArchivo()` y
`cargarMitigacionesArchivo()` publicaban los dos dominios pero marcaban un
solo insumo — el de la entrada usada —, así que el usuario tenía que cargar
el mismo archivo dos veces para que el Centro de carga lo diera por completo.
La rama del registro mensual de clientes de AF ya marcaba los dos desde
antes; esto la iguala. Pedido explícito del usuario el 07/08/2026.

### Las tres vías de carga deben dejar el archivo en su `<input>` (hallazgo del 07/08/2026)

Un insumo puede llegar por tres caminos: carga manual, extracción automática
(`procesarFuente()`) y restauración desde IndexedDB
(`restaurarInsumosGuardados()`). `ejecutarRevalidacion()` —lo que corre al
cambiar el periodo— recorre los `<input>`, así que **cualquier vía que no
deposite el archivo en el suyo produce un insumo que no se revalida jamás**:
se queda congelado con el resultado del mes con el que se cargó y la pantalla
muestra una cifra de otro periodo sin decir que no corresponde.

`procesarFuente()` ya lo hacía bien y su comentario lo explica. La
restauración era la única que no. Corregido con el mismo patrón
`DataTransfer`.

**Regla:** si se agrega una cuarta vía de carga, deposita el archivo en su
`<input>` — o cambia `ejecutarRevalidacion()` para que no dependa de ellos.
Hoy depende, y hay una prueba que lo fija para que el arreglo no quede por
inercia si eso cambia.

### Alcance de insumos obligatorios de Bancoldex (definido por el usuario, 07/08/2026)

**Para Bancoldex, AlertsList sí es obligatorio. Lo que no aplica es GLPI, al
que reemplaza Aranda.** Queda escrito porque el comentario anterior del código
afirmaba lo contrario («Bancoldex … no los usa aún»).

La entrada física `glpi` la comparten dos fuentes declarables: `glpi`
(AF/Novaventa) y `casos` (Bancoldex). El recuento de obligatorios cuenta la
entrada si el perfil declara **cualquiera** de las dos, y `insumoProcesado()`
resuelve contra el dominio `casos` para los perfiles con fuente propia —
Aranda publica ahí y nunca en el dominio `glpi`.
