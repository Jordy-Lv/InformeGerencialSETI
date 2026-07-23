# Sesión del 23 de julio de 2026 — contexto completo, hallazgos y cambios

**Rama:** `main` · **Commit:** `965726f` (ya fusionado; `feature/analisis-por-rango`
y las demás ramas `feature/*` se eliminaron el 23/07 tras confirmar que `main`
las contenía por completo — ver [PARTE 7](#parte-7--ajustes-posteriores-mismo-día-tarjeta-compacta-análisis-que-no-calla-variaciones-y-cierre-de-ramas))
**Archivo intervenido:** `informe-accion-fiduciaria 1.html` (+502 / −57 líneas en `11eee35`,
más +28 / −15 líneas adicionales en `965726f`)
**Documento técnico resumido:** [`2026-07-23-analisis-por-rango-y-redondeo.md`](2026-07-23-analisis-por-rango-y-redondeo.md)

Este documento recoge **todo**: el material de entrada, lo que se encontró al
estudiar el código, las decisiones que se tomaron y por qué, cada cambio
aplicado y la verificación de cada uno. El otro doc es la versión corta.

---

# PARTE 1 · El material de entrada

## 1.1 La llamada (`transcript.docx`)

Transcripción de ~23 minutos entre **Santiago Amaya Cely** y **Yordy Pardo
Pajaro**, revisando en pantalla el informe ya construido. 289 intervenciones.
Cronología de lo relevante:

| Momento | Qué se dijo |
|---|---|
| 00:00:03 | *«Lo único es que revisemos si el análisis lo podemos hacer con… por código, un análisis general, de ahí que claro que lo pueda editar»* — el análisis debe generarse solo, pero ser editable por si saca información irrelevante. |
| 00:00:32 | *«Agreguemos en la parte de abajito un espacio para colocar el análisis de la gráfica… si yo le doy clic en 3 meses que me haga el análisis de esa parte, si lo coloco 6 meses que me haga el análisis de esa parte y si le coloco 12 meses que me haga el análisis de esa parte.»* — **el análisis debe seguir al rango**. |
| 00:00:57 | Pasan a Gestión de backups: meta **99,3 %**, una sola meta. Yordy explica por qué eligió la gráfica de cápsulas: permite manejar 14 bases de datos y ver el valor exacto de cada mes. |
| 00:02:26 | Santiago confirma el comportamiento: *«cada vez que yo le doy clic a ese cosito verde, él me arroja una tabla donde yo veo el detalle de todas las disponibilidades»*. |
| 00:03:06 | Yordy aclara que el mes bajo del ejemplo no es de backups sino de **Disponibilidad por CI**, que usa la misma gráfica. |
| 00:04:07 | Yordy, viendo el corte de noviembre: *«Aquí debería estar en naranja. Bueno, aquí sí me equivoqué, pero sí, sí cumplió.»* |
| 00:05:10 – 00:06:07 | Santiago rehace el promedio a mano: **14 bases de datos, 5 de ellas en 98 %** → le da **99,2**, no 99,3. *«Revísate cómo hace ese promedio porque no sé por qué te está dando 99,3… sin embargo, el sistema te está diciendo que no estás cumpliendo.»* |
| 00:07:01 – 00:07:45 | Con el cálculo en pantalla (99,29): *«De hecho, ahí te lo está aproximando porque a mí me da 99,285714… El sistema lo que hizo fue aproximarte los 99,3. Yo creo que entonces estaría bien. Pero si te lo aproxima, deberíamos cumplir.»* Yordy: *«Sí, es una buena observación para corregir.»* |
| 00:08:07 | *«¿Y lo mismo, análisis, dónde están los análisis?»* → Yordy: *«que se despliegue aquí también»*. |
| 00:08:51 | *«El análisis en esas 2 tarjetas, ¿no?»* → *«Sí, en estos 2, análisis.»* |
| 00:09:02 | Logros y mitigaciones **se dejan como están** hasta que Santiago defina cómo llenarlas. |
| 00:09:22 – 00:10:00 | Bolsa de horas: tarjetas con horas contratadas, consumo del mes y disponibles, recalculando en vivo. |
| 00:10:02 | *«Me gusta para nosotros que estamos haciendo el informe. Yo lo dejaría así.»* — **bolsa de horas aprobada sin cambios**. |
| 00:10:09 | *«¿Cómo se lo vamos a mostrar al cliente? El cliente no puede entrar y ver esto, editar bolsa de horas.»* |
| 00:10:40 – 00:11:13 | Yordy demuestra el HTML exportado: sin barra superior, sin edición de bolsa, sin «editar análisis». |
| 00:11:14 | *«Muy re bien, te adelantaste y muy bien. Eso está muy chévere… solamente hay que hacerle esos cambios y ya acabamos con esta vaina.»* |
| 00:12:21 | *«¿Cuando yo le exporto ese código queda protegido, algo así, pa' que no me lo copien o qué?»* → Yordy: *«Pues no lo he validado como tal… ¿qué posibilidad hay de encriptar la parte de por debajo del código? Ya voy a revisar eso también.»* |
| 00:13:38 – 00:18:13 | Plan a futuro con Carlos Barrera: automatizar logros/mitigaciones y backups vía API o script; un **RPA** que entre a GLPI con usuario y contraseña, descargue el CSV de casos, lo deje en una ruta de SharePoint y Power Automate lo lleve al informe, el 1.º de cada mes a la 1:00 a. m. |
| 00:18:41 | *«Necesito que le dejes la documentación… cómo fue que se construyó todo, y lo guardes allá en esa carpeta.»* |
| 00:19:19 – 00:21:07 | Encargo de investigar cómo automatizar el GLPI (servidor propio vs. Power Automate). |
| 00:22:11 – 00:22:26 | Reunión el **3 de agosto a las 8:30 a. m.** para hacer el informe de acción juntos, en vivo, corrigiendo sobre la marcha. |

## 1.2 Las capturas enviadas

Seis capturas de los modales, ya con los datos de junio 2026 cargados:

1. **Indicadores del servicio** — 12M, tres series (disponibilidad de la
   plataforma 99,8 %, gestión del servicio 99,6 %, cumplimiento de entregables
   100 %), con la caída de nov-25 (98 % y 96 %). **Sin tarjeta de análisis.**
2. **Total de casos atendidos** — 3M, 49 casos, 0 atribuibles a SETI, **con** su
   tarjeta «Análisis del periodo» y el botón «Editar análisis».
3. **Disponibilidad global** — SETI 100 %, cliente 100 %, meta 99,3 %, 4
   motores, «Cumple». **Sin análisis.**
4. **Gestión de backups** — 14/14, promedio 100 %, 10 cortes, todos verdes.
   **Sin análisis.**
5. **Disponibilidad por CI (jun-26)** — 14/14, todos en 100 %; en la gráfica se
   ve **nov-25 en rojo** y el pie dice «9 sin brechas · 0 parciales · **1 bajo
   meta**».
6. **Disponibilidad por CI con nov-25 seleccionado** — el caso del bug:
   **«9 / 14»**, **promedio del corte 99,3 %**, «5 CI empatados · menor
   resultado 98 %», badge rojo **«Promedio bajo la meta»**, y en el panel
   lateral los cinco CI en 98 % (INVERACCION, ACBACOLG, APPACCION, INVHISTO,
   CHEETA) y nueve en 100 %.

La captura 6 es la prueba del defecto: **el propio modal imprime 99,3 %, que es
la meta, y a la vez declara incumplimiento.**

## 1.3 Instrucción textual junto a las capturas

> «aquí en este modal, debe habilitarse un espacio para un análisis en la parte
> de abajo, así como en casos atendidos, así se ve bien, entonces ese análisis
> cambia respecto al mes, debe ser un análisis genérico bien hecho, un análisis
> general, no debe ser ese que está en la imagen, pero debe ser un análisis
> breve y que concuerde con el periodo analizado, acá en el modal de
> disponibilidad global también debe haber un cuadro de análisis, igual que en
> gestión de backups y también en disponibilidad CI, recuerda que si no hay nada
> de texto en el análisis, no se coloca la tarjeta al exportar como HTML o PDF,
> no se debe mostrar esa tarjeta (donde contiene el texto) si no hay texto, y
> mira ahí te muestro en el modal de DISPONIBILIDAD POR CI QUE LA META ES 99,3,
> y pues ahí en ese periodo de nov aunque estuvimos en el límite, redondeando
> cumplimos por ende se debe ver anaranjado, así que fixea eso por favor»

De aquí salen cuatro requisitos:

- Análisis en **Indicadores** (la captura señalada), **Disponibilidad global**,
  **Backups** y **CI**.
- Texto **breve, general**, coherente con el periodo, y **no** una copia del
  estilo enumerativo del de casos.
- **Sin texto → sin tarjeta** en HTML exportado y en PDF.
- nov-25 debe verse **anaranjado**, no rojo.

## 1.4 Decisiones consultadas antes de implementar

| Pregunta | Respuesta |
|---|---|
| ¿En qué modales va el análisis? | Inicialmente **«solo backups y CI»**… **ampliado después** por las capturas a Indicadores, Disponibilidad global, Backups y CI. Se implementó el alcance ampliado, que es la instrucción más reciente. |
| Si edito el texto en un rango y cambio de rango, ¿qué pasa? | **Una edición por rango** (`ci:6M`, `backups:TODO`…). Al volver a ese rango reaparece lo editado; en los demás se ve el automático. |
| ¿Cómo corregir el redondeo? | *«Se debe redondear, el sistema debe tener en cuenta el valor redondeado… entonces debe verse en color anaranjado.»* |
| ¿Protección del export y RPA del GLPI? | **Incluir la protección del export**. El RPA queda fuera. |

El matiz del **naranja** importa: no se pedía que nov-25 pasara a verde. En ese
corte el promedio cumple **pero cinco CI siguen por debajo**, y el componente ya
tenía definido ese estado intermedio (`partial` = «Promedio cumple · con
brechas»). El arreglo lo lleva de `bad` a `partial`, no a `ok`.

---

# PARTE 2 · Lo que se encontró al estudiar el código

## 2.1 Forma del proyecto

Un único HTML monolítico y offline de 4,3 MB / 5.402 líneas, con las librerías
(xlsx, Chart.js, jsPDF, html2canvas, fuentes e imágenes en base64) embebidas.
Nueve bloques `<script>` inline. El informe se usa en dos modos:

- **Autoría**: se cargan los Excel del mes, se editan textos, se exporta.
- **Cliente** (`window.__INFORME_CLIENTE__`): el HTML exportado, solo lectura,
  que se hidrata desde `window.__ESTADO__` y no abre IndexedDB.

Los datos viven en un store propio (`REPORTE`) con dominios (`casos`,
`disponibilidad`, `ci`, `backups`, `indicadores`, `logros`, `mitigaciones`), y
cada modal se repinta cuando el store notifica (`REPORTE.suscribir(renderAll)`).
Como `renderAll()` reconstruye el `innerHTML`, **todo estado de interfaz vive
fuera del DOM** (`rangosHistorico`, `analisisPersonalizado`,
`seleccionDisponibilidadCI`).

## 2.2 Piezas relevantes localizadas

| Pieza | Dónde estaba | Papel |
|---|---|---|
| `pct(v,dec)` | 1700 | Formateo global de porcentajes. |
| `pct` local del dashboard | 4055 | `maximumFractionDigits:1` → **imprime 99,285714 como «99,3»**. Origen visual del desfase. |
| `montarHistorico` | 4172 | Gráfica + filtro 3M/6M/12M/Todo + `resumen`. La usan `c4`, `c5`, `c6`. Su `pintar()` es el punto de re-render por rango. |
| `montarAnalisis` | 4341 | Tarjeta de análisis editable ya existente: edición, badge, aviso por firma, solo lectura en cliente, persistencia IndexedDB. |
| `metricasCasos` / `narrarCasos` | 4440 / 4488 | Patrón del proyecto: cálculo puro separado de la narración, sin NaN/Infinity, con autopruebas. |
| `montarRadarCI` | 4936 | Gráfica de cápsulas, **compartida** por `c7` (backups) y `c11` (CI) mediante `opts.id` y `opts.textos`. |
| `snapshotEstado` | 3651 | Lo que viaja al HTML del cliente. |
| `podarClon` | 3686 | Poda del clon al exportar. |
| Autopruebas | 1854+ | 30+ verificaciones embebidas, ejecutables con `await REPORTE.autopruebas(archivos)`. |

## 2.3 El defecto, localizado con precisión

En `montarRadarCI.estadistica()`:

```js
const cumplen = valores.filter(v => v >= meta).length;
…
estado: !valores.length ? 'empty'
      : promedio < meta ? 'bad'
      : cumplen === valores.length ? 'ok' : 'partial'
```

Compara el **valor crudo** (99,285714) contra la meta (99,3) mientras la vista
imprime **99,3 %**. De ahí el rojo y el «Promedio bajo la meta» de la captura 6.

La misma comparación cruda estaba repetida en otros seis lugares, cada uno con
su propia normalización fracción→porcentaje copiada a mano:

1. Fila del panel lateral del radar (5015)
2. `cumplen` publicado en el store de CI (2591)
3. Chip de la tarjeta de Disponibilidad global (3026)
4. Chip de la tarjeta de Backups (3131)
5. Minis de la tarjeta de Indicadores (3102)
6. «Estado contractual» de `renderC6` (4635)

Más dos **autopruebas** que replicaban la fórmula vieja (2049 y 2082) — habrían
seguido dando por buena la conducta incorrecta.

## 2.4 Lo que ya existía y se reutilizó (no se reinventó)

- `montarAnalisis` completo: edición, aviso de datos desactualizados por firma,
  modo cliente, persistencia IndexedDB (`_analisis`), export vía
  `snapshotEstado`.
- `rangosHistorico` + `PRESETS_HISTORICO` + `indicesDeRango` para el filtro.
- El objeto `T` de textos de `montarRadarCI`, que ya distinguía «CI» de
  «instancia» — se le añadieron claves de género y número en vez de crear un
  segundo mecanismo.
- `resumenCasos`, refactorizado para compartir cálculo con el análisis.

---

# PARTE 3 · Los cambios aplicados

## Cambio 1 — `cumpleMeta()`: una sola regla de cumplimiento

**Nuevo** en la línea 1715, junto a `pct()`:

```js
function cumpleMeta(valor,meta,dec=1){
  const aPorcentaje=v=>{ … Math.abs(n)<=1.01 ? n*100 : n … };
  const v=aPorcentaje(valor), m=aPorcentaje(meta);
  if(v===null||m===null) return false;
  const f=10**dec;
  return Math.round(v*f)/f >= Math.round(m*f)/f;
}
```

Redondea a **1 decimal** —la precisión con la que se publica el dato y la de la
meta 99,3 %— y compara. Sustituye las **siete** comparaciones crudas de §2.3 y
las **dos autopruebas** que las replicaban. También se corrigió el plural «1
parciales» del pie del radar.

**Efecto medido en nov-25** (datos reales, leídos del DOM):

| | Antes | Después |
|---|---|---|
| Promedio del corte | 99,29285714285713 | *(igual, no se toca el dato)* |
| Clase de la cápsula | `is-bad` (rojo) | **`is-partial` (naranja)** |
| Badge del panel | «Promedio bajo la meta» | **«Promedio cumple · con brechas»** |
| Pie del radar | 9 sin brechas · 0 parciales · 1 bajo meta | **9 sin brechas · 1 parcial · 0 bajo meta** |
| Hero | 9 / 14 | **9 / 14 (sin cambio, y así debe ser)** |

El hero no cambia porque los cinco CI en 98 % **no** cumplen individualmente. Lo
que cumple es el promedio del corte.

## Cambio 2 — Análisis sensible al rango en cinco modales

### 2.a Enganche en los dos componentes de gráfica

`montarHistorico` y `montarRadarCI` aceptan una opción `analisis` y montan la
tarjeta como **bloque hermano** de la gráfica (`montarHostAnalisis`, 4613), de
modo que pueda desaparecer entera sin dejar hueco dentro del recuadro.

El re-montaje lo gobierna `crearRefrescoAnalisis` (4626), que **solo remonta
cuando cambia la clave de rango**:

```js
function crearRefrescoAnalisis(host,{id,titulo,generar}){
  let claveActual=null;
  return (clave,ctx)=>{
    if(clave===claveActual && host.dataset.montado==='1') return;
    claveActual=clave; host.dataset.montado='1';
    montarAnalisis(host,{id:`${id}:${clave}`,titulo,generar:()=>generar(ctx)});
  };
}
```

Esto no es un detalle cosmético: el radar **también repinta al elegir un mes en
la gráfica**, y remontar ahí borraría un textarea abierto a media edición.

`claveDeRango` (4804) devuelve el preset (`3M`/`6M`/`12M`/`TODO`) o
`desde_hasta` si el rango se fijó a mano con los selectores.

### 2.b Generadores nuevos

Mismo contrato que `metricasCasos`/`narrarCasos`: **deterministas, cálculo puro
separado de la narración, jamás NaN/Infinity/undefined, y cadena vacía cuando no
hay datos** (una cadena vacía significa «sin tarjeta»).

| Función | Línea | Para |
|---|---|---|
| `metricasSeries` | 4807 | `c4` indicadores, `c6` motores |
| `narrarSeries` | 4841 | idem |
| `metricasRadar` | 4875 | `c7` backups, `c11` CI |
| `narrarRadar` | 4895 | idem |
| `metricasRangoCasos` | 4943 | `c5` casos (y el pie de su gráfica) |

Auxiliares: `NUM_PALABRA`/`enPalabras` (números en letras hasta doce) y `plural`.

**`metricasSeries`** calcula por serie: promedio del rango, cortes bajo meta
(con `cumpleMeta`), la desviación más baja con su mes, y el último valor; y de
forma global: promedio general, total de cortes bajo meta, el peor de todas las
series, cuántas cierran en meta y si el cierre es uniforme. En `c6` se descarta
antes la serie de referencia (la línea de meta), igual que hace `resumenMotores`.

**`metricasRadar`** parte de los `stats` que `estadistica()` ya calcula y añade:
promedio del rango, cuántos cortes `ok`/`partial`/`bad`, el peor corte, el
último, y una bandera clave:

```js
peorEnLimite: peor.estado==='partial' && peor.promedio<meta && cumpleMeta(peor.promedio,meta)
```

que distingue *«justo en el límite»* del incumplimiento real — exactamente el
caso de nov-25.

**Vocabulario:** `narrarRadar` toma género y número del objeto `T` que ya
parametrizaba el radar, ampliado con `unidadSingular`, `unidadPlural`, `art`,
`artSingular` y `medidaMin`. Por eso backups dice «las 14 instancias» y CI «los
14 CI», sin duplicar el generador.

### 2.c Textos que produce (reales, con los insumos de junio 2026)

| Modal | Rango | Texto generado |
|---|---|---|
| **CI** | Todo | *Entre sep-25 y jun-26 la disponibilidad promedio de los 14 CI fue de 99,9 %, sobre la meta de 99,3 %. Nueve de los diez cortes cerraron sin brechas; nov-25 quedó justo en el límite de la meta, con cinco CI por debajo (mínimo 98 %). El corte de jun-26 cierra con los 14 CI en 100 %.* |
| **CI** | 3M | *Entre abr-26 y jun-26 la disponibilidad promedio de los 14 CI fue de 100 %, sobre la meta de 99,3 %. Tres cortes cerraron con todos los CI en meta. El corte de jun-26 cierra con los 14 CI en 100 %.* |
| **Backups** | Todo | *Entre sep-25 y jun-26 la ejecución promedio de las 14 instancias fue de 100 %, sobre la meta de 99,3 %. Diez cortes cerraron con todas las instancias en meta. El corte de jun-26 cierra con las 14 instancias en 100 %.* |
| **Disponibilidad global** | Todo | *Entre sep-25 y jun-26 los cuatro motores monitoreados promediaron 99,9 %, sobre la meta de 99,3 %. La única desviación fue Oracle en nov-25, con 98 %. El corte de jun-26 cierra con los cuatro en 100 %.* |
| **Indicadores** | 3M | *Entre abr-26 y jun-26 los tres indicadores contractuales promediaron 100 %. Ningún corte del rango quedó por debajo de la meta. El corte de jun-26 cierra con los tres en 100 %.* |

En Indicadores no se nombra la meta porque **cada indicador tiene la suya** y no
hay una común: el generador prefiere callar antes que inventar una cifra.

### 2.d `c5` (casos) sensible al rango

`narrarCasos` recibe un tercer parámetro opcional `rango` y añade una frase
final:

> En el rango visible (abr-26 a jun-26) se atendieron 142 casos, un promedio de
> 47,3 al mes, con abr-26 como el mes más alto (58).

Las cifras salen de `metricasRangoCasos`, **la misma función que alimenta el pie
de la gráfica**, para que el modal no pueda contradecirse a sí mismo.

## Cambio 3 — Edición por rango, con migración

La clave de `montarAnalisis` pasa de `<id>` a `<id>:<rango>`. `snapshotEstado`
exporta el Map completo, así que las claves compuestas viajan sin tocar nada.

**Migración** (`PRESET_POR_DEFECTO` + `adoptarAnalisis`, 4512): un texto guardado
con el formato viejo (`casos`) se adopta para el preset por defecto de su
tarjeta (`casos:3M`) — que es el rango en el que se escribió. Sin esto, un
análisis ya redactado desaparecería sin explicación.

**El rango viaja al entregable**: `snapshotEstado` incluye ahora
`rangosHistorico`, y el arranque en modo cliente lo rehidrata. Con el análisis
editado por rango, si el HTML del cliente abriera siempre en el preset por
defecto mostraría el texto automático de **otro** rango en lugar del que el
autor dejó escrito.

## Cambio 4 — Sin texto, sin tarjeta

- **Modo cliente:** con el texto final vacío, `montarAnalisis` no monta nada —
  ni recuadro, ni título, ni clase.
- **Modo autoría:** marcador con borde punteado (`.analisis-card--vacia`) y el
  aviso «Sin análisis · esta tarjeta no se incluirá en el informe exportado ni
  en el PDF», con el botón para escribirlo.
- **PDF:** `body.exportando-pdf .analisis-card--vacia{display:none!important}`,
  la misma mecánica que ya ocultaba `.hist-controls`.
- **Export:** `podarClon` elimina del clon los nodos `.analisis-card--vacia`.

**Cambio de semántica documentado:** guardar en blanco antes revertía al texto
automático; ahora significa «este indicador va sin análisis» y se guarda como
`{texto:'', personalizado:true}`. Para recuperar el automático se añadió el botón
**«Restaurar análisis automático»**, visible solo cuando hay algo que restaurar.

## Cambio 5 — Protección del HTML exportado

Lo primero, dicho sin adornos y así consta en la documentación entregable:
**un HTML que se entrega no se puede proteger de verdad.** El navegador del
cliente tiene que ejecutarlo, luego el código siempre será legible con «Ver
código fuente». Lo que sí se puede es quitar lo que explica *cómo está
construido* y dejar clara la propiedad.

**`despojarComentarios(js)`** (3757): elimina los comentarios del JavaScript
embebido conservando los avisos de licencia (`/*!`). No usa expresiones
regulares —`//` dentro de `"http://…"`, de una plantilla o de un literal de
regex no es un comentario—: recorre el texto con una **pila de contextos
léxicos**.

> **Fallo real detectado durante la implementación.** La primera versión leía
> las plantillas «hasta el siguiente backtick». Con `` `${a?`x`:`y`}` `` —
> habitual en este archivo— el cierre se detecta en el lugar equivocado y a
> partir de ahí **todo queda desfasado**: el código seguía compilando, pero
> regiones enteras conservaban sus comentarios, señal de que el lector estaba
> interpretando código como si fuera texto. Se detectó instrumentando el
> recorrido y midiendo comentarios supervivientes; se corrigió con la pila
> (`tpl` / `interp` con conteo de llaves). Ahorro antes del arreglo: 29 KB. Después: **64 KB**.

Red de seguridad: cada bloque se valida con `new Function(...)` antes de
sustituirlo; si no compilara, **se conserva el original**. Un informe legible
vale más que uno opaco.

También se eliminan los comentarios del HTML y se antepone al archivo generado
un **aviso de confidencialidad y autoría**.

**No** se implementó bloqueo de clic derecho ni de teclas: no protege nada,
molesta al lector legítimo y rompe la accesibilidad.

**Resultado:** 64 KB de comentarios fuera; el entregable pasa de ~4,3 MB a
**2,9 MB** (2.904.733 bytes), con el grueso del ahorro viniendo de no incluir
las librerías de solo autoría.

## Cambio 6 — Autopruebas

- Reapuntadas a `cumpleMeta` las dos que replicaban la fórmula vieja.
- **12 nuevas**, movidas al tramo que corre siempre (son funciones puras, no
  necesitan insumos):
  - La regla de redondeo: 99,2857 → cumple; 99,3 → cumple; 1 (fracción) →
    cumple; 99,24, 98 y `null` → no cumplen.
  - Diez casos borde de los generadores: rango de un solo corte, serie sin
    datos, todo en cero, sin meta declarada, sin periodos, radar sin cortes con
    dato, radar de un solo corte, todos bajo meta, un solo sistema, y el
    promedio justo en el límite.
  - Una prueba específica de la regla de negocio: *un promedio que redondea a la
    meta no se narra como incumplimiento* (el texto debe decir «límite» y no
    «bajo meta»).

---

# PARTE 4 · Verificación

Método: servidor HTTP local (`python3 -m http.server 8777`), los cuatro insumos
reales de `Insumos/` inyectados con `fetch()` + `DataTransfer` sobre los `<input
type=file>`, y comprobaciones leídas del DOM vivo.

| Qué | Resultado |
|---|---|
| **Redondeo, nov-25** | Cápsula `is-partial`, badge «Promedio cumple · con brechas», pie «9 sin brechas · 1 parcial · 0 bajo meta», hero «9 / 14» intacto. Confirmado además con captura de pantalla. |
| **Ningún efecto colateral** | Los otros nueve cortes de `c11` y los diez de `c7` conservan su color. |
| **Análisis en los cinco modales** | `c4`, `c5`, `c6`, `c7`, `c11` generan texto; ver §2.c. |
| **Sensibilidad al rango** | 3M / 6M / 12M / Todo producen textos distintos y coherentes con lo que muestra la gráfica. |
| **No se pierde la edición** | Elegir un mes en el radar **no** regenera el análisis. |
| **Edición por rango** | Editado en 6M → 12M muestra el automático → volver a 6M recupera lo editado. Clave guardada: `ci:6M`. |
| **Migración de claves** | Una entrada antigua `casos` escrita en IndexedDB se adopta como `casos:3M` al recargar. |
| **Tarjeta vacía · PDF** | Bajo `body.exportando-pdf`: `.analisis-card--vacia` → `display:none`; tarjeta con texto → `block`; `.analisis-acciones` → `none`; controles del radar → `none`. |
| **Tarjeta vacía · export** | Clon del export con 0 nodos `.analisis-card--vacia`; el modal afectado sale sin tarjeta. |
| **Export real, abierto y ejecutado** | Modo cliente sin topbar ni panel de carga; análisis en `c4`/`c5`/`c6`/`c11` **sin botones de edición**; `c7` sin tarjeta (se dejó en blanco a propósito); rango de CI en 12M, el que dejó el autor; nov-25 naranja; **cero errores de consola**; el filtro sigue recalculando el texto al cambiar de rango. |
| **Despojo de comentarios** | Los 9 bloques `<script>` compilan tras el despojo y **no queda ningún comentario superviviente**. |
| **Autopruebas** | **46 de 47** con los insumos cargados. |
| **Sintaxis** | `node --check` sobre los 9 bloques después de cada edición. |

**La única prueba que falla** —«Portada: estado general no afirma
cumplimiento»— es **preexistente**: referencia un `data-k="estadoGeneral"` que
no existe en el HTML. Confirmado con `git show main:… | grep -c` → aparece 1 vez
solo en la prueba, nunca en el marcado. Ya estaba documentada en
`2026-07-22-casos-analisis.md`.

## Cómo repetir la verificación

```bash
python3 -m http.server 8777
```

Abrir `http://localhost:8777/informe-accion-fiduciaria%201.html`, cargar los
cuatro archivos de `Insumos/` y, en la consola:

```js
await REPORTE.autopruebas([/* los cuatro File */])
```

---

# PARTE 5 · Lo que queda fuera

- **PDF sin inspección del archivo final.** El camino de exportación se ejecuta
  entero, sin errores de consola ni diálogos de error, y las reglas de ocultado
  están verificadas por CSS computado. No se llegó a abrir el PDF resultante: la
  versión activa de `exportarPDF` es la que **redefine** el script de dashboards
  y no pasa por el `save` del prototipo de jsPDF que se interceptó para evitar
  escribir en la carpeta de Descargas. Se comprobó que **no** quedó ningún
  archivo en `~/Downloads`.
- **Autoprueba rota preexistente** «Portada: estado general» — sigue fuera de
  alcance, como en las dos intervenciones anteriores.
- **Logros y mitigaciones**: sin tocar, por decisión de Santiago en la llamada
  (00:09:02).
- **Bolsa de horas**: sin tocar, aprobada tal cual (00:10:02).
- **Automatización del GLPI (RPA)**, integración con el servidor de Carlos
  Barrera, Power Automate y SharePoint: investigación aparte encargada en la
  misma llamada (00:19:19).

# PARTE 6 · Para la reunión del 3 de agosto

Lo que conviene enseñar y confirmar con Santiago:

1. **nov-25 en Disponibilidad por CI**: ahora naranja, con el badge «Promedio
   cumple · con brechas» — y explicar por qué el hero sigue en 9/14.
2. **Los análisis**, cambiando el rango delante de él para que vea que el texto
   sigue al filtro.
3. **La tarjeta vacía**: borrar un análisis y exportar, para que compruebe que no
   aparece en el entregable.
4. **La conversación sobre la protección del código**: qué se hizo, y por qué no
   existe una protección real de un HTML que se entrega.

---

# PARTE 7 · Ajustes posteriores (mismo día): tarjeta compacta, análisis que no calla variaciones, y cierre de ramas

Ronda corta, en una conversación aparte el mismo 23/07, ya con `11eee35`/`a179e84`
mergeados en la cabeza de `feature/analisis-por-rango`. Dos pedidos puntuales del
usuario sobre lo ya construido, más el cierre de todo el árbol de ramas. Commit:
`965726f`.

## 7.1 — Modal de Disponibilidad global sin scroll

**Pedido:** que el modal se vea completo (incluida la tarjeta de análisis) sin
que el usuario tenga que hacer scroll, tocando **solo** la tarjeta resumen de
arriba (`.availability-summary`) — «no tienes permiso a modificar más nada».

**Medición antes de tocar nada** (servidor HTTP local, insumo real
`Disponibilidad Consolidado Mayo.xlsx` inyectado por `fetch`+`DataTransfer`,
viewport 1280×800, `scrollHeight - clientHeight` del `.dashboard-modal__body`):

| Pieza | Alto |
|---|---|
| Scroll total | **245 px** |
| `.availability-summary` (con margen) | 156 px |
| `.hist-chart` (gráfica) | 320 px |
| `.hist-resumen` | 82 px |
| `.analisis-host.analisis-card` | 125 px |

**El problema, cuantificado antes de escribir una sola línea:** aun
**eliminando por completo** la tarjeta resumen (156 px) sobraban 89 px de
scroll. Reducirla «solo un poco» —la instrucción original— ahorra en la
práctica ~40–55 px sin dejarla ilegible: muy lejos de los 245 px necesarios.
Tocar únicamente lo autorizado no alcanzaba el objetivo declarado (0 scroll).

Se expuso la cuenta al usuario en vez de forzar un recorte que no iba a
funcionar, con `AskUserQuestion`. Primera pregunta — alcance: ¿solo la tarjeta
(sin llegar a 0), tarjeta + un poco de la gráfica, o solo reportar números y
decidir después? Eligió **tarjeta + gráfica**. Con ese permiso ampliado se
probaron en vivo, con overrides de CSS inyectados en el DOM (sin tocar aún el
archivo), varias combinaciones tarjeta/`alturaChart`, midiendo el scroll
resultante en cada una:

| Tarjeta | Gráfica | Scroll resultante |
|---|---|---|
| 142→104 px | 320→220 px | 103 px |
| 142→88 px | 320→190 px | 55 px |
| 142→88 px | 320→160 px | 25 px |
| 142→88 px | 320→134 px | **0 px** |

0 px exige recortar la gráfica un 58 % (320→134 px), justo lo opuesto a
«darle protagonismo a la gráfica», la decisión de diseño explícita de la
ronda del 22/07 (`2026-07-22-disponibilidad-historico.md`, punto 6–7 de la
sección «Ronda de ajustes»). Segunda pregunta al usuario, ya con captura del
resultado a 134 px: ¿0 scroll con la gráfica muy reducida, 190 px (el mismo
tamaño ya validado en el modal de casos) con ~55 px de scroll residual, o
220 px con ~103 px? Eligió **190 px / 55 px residual** — prioriza que la
gráfica siga siendo legible sobre el 0 px exacto; el scroll que queda apenas
roza el botón «Editar análisis», el análisis en sí queda completo.

**Cambios aplicados** en `informe-accion-fiduciaria 1.html`:

- CSS `.availability-summary` y sus descendientes (antes en torno a la línea
  4035): `min-height` 142→88 px, `margin-bottom` 14→8 px; paddings de
  `__lead` y `__stat` de `22px …`→`10px …`; número principal (`__lead
  strong`) 38→24 px; valores secundarios (`__stat b`) 27→18 px; etiquetas
  11–12 px sin cambio salvo el `min-height` fijo de 29 px en `__stat span`
  (reservaba espacio para etiquetas de dos líneas), eliminado para que la
  celda se ajuste a su contenido real.
- Llamada a `montarHistorico` para `#hist-host-disponibilidad` (renderC6):
  `alturaChart:320` → `alturaChart:190` — el mismo valor que ya usa el
  histórico de casos (`c5`), no uno nuevo inventado para este modal.

No se tocó `.hist-resumen`, `.analisis-card` ni ningún otro modal — el
`alturaChart:190` de casos es una llamada distinta (`#hist-host-casos`), así
que bajar el de disponibilidad no le afecta.

**Verificación:** con el consolidado real cargado y el modal reabierto desde
cero (no sobre los overrides de prueba), `scrollHeight - clientHeight` dio
**55 px** — coincide exactamente con lo probado en vivo. Captura de pantalla
confirma «Análisis del periodo» completo y legible. Sin errores de consola.
Los 9 bloques `<script>` pasan `node --check`.

## 7.2 — El análisis no debe callar una variación solo porque cumple meta

**Pedido**, con captura del modal «Indicadores del servicio» en 6M: el
tooltip de la gráfica muestra que en ene-26 la disponibilidad de la
plataforma administrada fue 99,9 % (meta 99,3 %), pero el texto generado
decía «Ningún corte del rango quedó por debajo de la meta» — sin mencionar
esa variación. El usuario la identificó verbalmente como «Oracle», aunque en
este modal (a diferencia de Disponibilidad global) las series son los tres
indicadores contractuales, no los motores; el fondo del pedido —que una
desviación real no desaparezca del análisis solo por cumplir la meta— aplica
igual.

**Causa, localizada en `metricasSeries`/`narrarSeries` (línea 4807):** la
función solo registra un valor como «desviación» cuando **incumple la
meta** (`bajoMeta`, vía `cumpleMeta`). 99,9 % ≥ 99,3 % cumple, así que nunca
entraba en `peorGlobal` y la rama `totalBajoMeta===0` imprimía el texto
genérico sin mirar si hubo variación real dentro del rango. Es la misma
función que alimenta **Disponibilidad global** (`c6`) además de
**Indicadores del servicio** (`c4`) — ambas comparten `montarHistorico` con
series de línea — así que el arreglo beneficia a los dos modales por igual,
sin tocar el radar de cápsulas (Backups/CI), que ya tenía su propio manejo
de «cumple pero con brechas» vía `peorEnLimite`.

**Cambio aplicado:**

- `metricasSeries`: cada valor de cada serie ahora también se compara contra
  el mínimo de su propia serie (`minimo`, sin filtrar por meta). A nivel
  global se calcula `minimoGlobal` (el punto más bajo de todo el rango,
  entre todas las series) y `hayVariacion` (hay más de un valor y la
  diferencia entre el máximo y el mínimo observados supera 0,001 — para no
  disparar el aviso por ruido de punto flotante cuando en realidad todo es
  el mismo número).
- `narrarSeries`: cuando `totalBajoMeta===0` (nadie incumple), si además
  `hayVariacion` y hay más de un corte visible, la frase pasa de «Ningún
  corte del rango quedó por debajo de la meta.» a «Ningún corte del rango
  quedó por debajo de la meta; el valor más bajo fue **{serie}** en
  **{mes}**, con **{valor}%**.». Con un solo corte visible, o sin variación
  real (todo en el mismo valor, p. ej. 100 % siempre), el texto no cambia.

**Texto real generado** tras el cambio, con el consolidado cargado, modal
Indicadores del servicio, rango 6M (ene-26→jun-26):

> Entre ene-26 y jun-26 los tres indicadores contractuales promediaron 100%.
> Ningún corte del rango quedó por debajo de la meta; el valor más bajo fue
> Disponibilidad de la plataforma administrada en ene-26, con 99,9%. El
> corte de jun-26 cierra con los tres en 100%.

**Verificación:** `REPORTE.autopruebas()` con los cuatro insumos reales
cargados — **42 de 42** pasan, sin fallas nuevas ni regresiones en los casos
borde ya cubiertos (rango de un solo corte, serie sin datos, todo en cero,
sin meta declarada, sin periodos). `node --check` sobre los 9 bloques
`<script>`, sin errores.

## 7.3 — Commit, fusión a `main` y cierre de todas las ramas `feature/*`

El usuario pidió consolidar todo en `main` y borrar el resto del árbol de
ramas. Antes de borrar nada se verificó, para cada rama, que no tuviera
ningún commit propio fuera del historial ya alcanzable desde
`feature/analisis-por-rango` (`git log feature/analisis-por-rango..<rama>`
vacío en las cuatro) y que `main` fuera ancestro directo de
`feature/analisis-por-rango` (fast-forward limpio, sin merge commit).

1. `git add` explícito (sin `-A`) de los archivos pendientes: el consolidado
   de disponibilidad (5 bytes de diferencia, metadata de guardado), el
   traslado de `Logros_Clientes_Junio_2026_1 (1).xlsx` de la raíz a
   `Insumos/` (mismo hash de git antes y después — confirmado con
   `git hash-object`/`git rev-parse`, así que git lo registró como rename,
   no como borrado+alta), el HTML con los cambios de 7.1/7.2, y
   `transcript.docx` (nuevo, la transcripción de la llamada del §1.1).
2. Commit `965726f` en `feature/analisis-por-rango`.
3. `git checkout main && git merge --ff-only feature/analisis-por-rango` —
   fast-forward, sin commit de merge.
4. `git branch -d` (con minúscula, no `-D`: solo borra si ya está fusionado,
   así que un commit no alcanzable habría abortado el borrado en vez de
   perderse) sobre `feature/analisis-por-rango`, `feature/casos-analisis`,
   `feature/disponibilidad-historico`, `feature/indicadores-historico` y
   `feature/tarjeta-ci-sistemas`.

**Estado final:** una sola rama, `main`, en `965726f`, árbol de trabajo
limpio. Sin remoto configurado en este repositorio, así que no hubo nada que
sincronizar ni ramas remotas que limpiar.
