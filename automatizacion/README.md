# Automatización de insumos del informe (GLPI + AlertOps)

Origen: encargo de Santiago Amaya Cely en la llamada del 23/07/2026 —
*«mira cómo puedes automatizar esa parte con el GLPI… puede que haya otra forma»*.
Resultado de la investigación y guion de demo de la parte de GLPI en
[`../Automatizacion GLPI - Demo 24 julio 2026.docx`](<../Automatizacion GLPI - Demo 24 julio 2026.docx>).
El plan de cierre de GLPI (lo que falta y quién debe decidir qué) está en
[`../Automatizacion GLPI - Plan de cierre.docx`](<../Automatizacion GLPI - Plan de cierre.docx>).

La automatización de AlertOps (consolidado de alertas) se investigó después,
el 28/07/2026, siguiendo el mismo patrón: reconocimiento primero, extractor
después.

El desarrollo de todo esto vive en el Mac de Yordy, pero la tarea programada
mensual va a correr en el Windows corporativo. Qué es compatible tal cual, qué
había que adaptar (el envoltorio de la tarea programada) y cómo instalarlo
ahí, paso a paso, está en
[`../docs/2026-07-28-desarrollo-mac-despliegue-windows.md`](../docs/2026-07-28-desarrollo-mac-despliegue-windows.md).

## Qué hay aquí hoy

| Archivo | Qué es |
|---|---|
| `actualizar_informe.py` | **Punto de entrada único.** Corre las dos extracciones y deja el informe listo para abrir. Es lo que hay que programar mensualmente. |
| `tarea_mensual.sh` | Envoltorio para `cron` (Linux/macOS): log con fecha, distingue éxito/fallo. |
| `tarea_mensual.ps1` | El mismo envoltorio para el Programador de tareas de **Windows** — mismo comportamiento, PowerShell en vez de Bash. |
| `sonda_glpi.py` | Reconocimiento de GLPI. Averigua **qué vía de extracción funciona** contra la instancia real y guarda la evidencia. |
| `extraer_glpi.py` | Extrae la sábana de casos por la API REST de GLPI y aporta su parte al `insumos-af.js`. |
| `sonda_alertops.py` | Reconocimiento de AlertOps. Confirma que la api-key autentica contra la API documentada y que el esquema real coincide con lo esperado. |
| `extraer_alertas.py` | Extrae el consolidado de alertas por la API REST de AlertOps y aporta su parte al `insumos-af.js`. |
| `insumos_af.py` | Módulo compartido: lee/escribe `insumos-af.js` para que los extractores puedan aportar su archivo sin borrar el de los otros. |
| `extraer_indisponibilidades.py` | Cruza `DisponibilidadMensual.xlsx` (log de indisponibilidades, diligenciado a mano) contra los incidentes que `extraer_glpi.py` ya clasificó, para validar «atribuible a SETI» con dato real en vez de solo inferencia por categoría. **Enganchado a `actualizar_informe.py` (corre solo con el `.bat`); opcional y no bloqueante; el HTML ya usa esta reconciliación** para corregir el conteo. El archivo standalone (local + OneDrive) solo existe mientras haya algo sin registrar — se borra solo cuando ya no hace falta. |
| `historico_casos.py` | Módulo compartido: lee/escribe `salida/historico_casos.json`, el ledger acumulado de casos (alertas/requerimientos/incidentes) por mes, mes a mes por *upsert* — independiente de la hoja «Casos» del consolidado. **Construido, enganchado y consumido por el HTML** — ver sección propia más abajo. |
| `backfill_historico_casos.py` | Script de una sola vez: puebla el ledger con los meses anteriores a la automatización, leyendo la hoja «Casos» del consolidado. Ya corrido una vez (sep-25 → jun-26); no hace falta volver a correrlo salvo para poblar un cliente nuevo. |
| `requirements.txt` | Única dependencia externa de todo `automatizacion/`: `openpyxl`, para `extraer_indisponibilidades.py` y `backfill_historico_casos.py`. Los extractores mensuales (`extraer_glpi.py`, `extraer_alertas.py`) siguen sin dependencias. |
| `.env.ejemplo` | Plantilla de credenciales de las fuentes, más `RUTA_ONEDRIVE` y `RUTA_INDISPONIBILIDADES` (opcionales). Cópiala a `.env` (ignorado por git). |

## Cómo se conecta con el informe

```
                      ┌─►  salida/glpi-2026-06.csv       (original, para archivo)
extraer_glpi.py     ─┤
                      ├─►  RUTA_ONEDRIVE/Junio/glpi-2026-06.csv  (copia de resguardo;
                      │                                            la subcarpeta del mes
                      │                                            se crea sola)
                      └─►  salida/insumos-af.js  ─────►  ../insumos-af.js
extraer_alertas.py  ──────►  (mismo trío, con alertops-2026-06.csv)    (junto al HTML;
                              insumos-af.js: un solo archivo,           lo copia
                              dos claves, archivos.glpi/.alertas)       actualizar_informe.py)
                                        │
                                        └─► RUTA_ONEDRIVE/Junio/
                                              ├─ Informe Accion Fiduciaria Junio 2026.html
                                              └─ insumos-af.js
                                            (el HTML ya cargado, junto a los CSV
                                             de resguardo — mismo mecanismo,
                                             mismo mes, sin tocar nada a mano)
```

`actualizar_informe.py` orquesta los pasos que antes había que hacer a mano:
llamar a las dos APIs y, por cada una, dejar **tres copias independientes**
del mismo CSV, ninguna derivada de otra por mutación:

1. **Original**, intacto, en `salida/` (`glpi-2026-06.csv`,
   `alertops-2026-06.csv`) — para archivo y auditoría local.
2. **Copia de resguardo**, también intacta, en una subcarpeta con el nombre
   del mes (p. ej. `Julio/`) dentro de la carpeta que declares en
   `RUTA_ONEDRIVE` (`.env`) — la subcarpeta se crea sola si no existe.
   Pensada para una biblioteca de SharePoint sincronizada localmente vía
   OneDrive (el mismo mecanismo que usa «Agregar acceso directo a OneDrive»
   en la web de SharePoint): el cliente de sincronización se encarga de
   subirla, sin que el script hable con ninguna API de SharePoint. Sin
   `RUTA_ONEDRIVE` configurada, este paso se omite sin error: es opcional,
   no bloqueante.
3. **Copia convertida** (base64 + huella) dentro de `insumos-af.js`, que
   `actualizar_informe.py` copia junto al HTML para que el informe la cargue
   sola al abrirse.

Además, si `RUTA_ONEDRIVE` está configurada, `actualizar_informe.py` deja una
**cuarta copia**: el HTML del informe **ya cargado**, con su `insumos-af.js` al
lado, en la misma subcarpeta del mes donde caen los CSV de resguardo
(`RUTA_ONEDRIVE/Junio/Informe Accion Fiduciaria Junio 2026.html`). Reutiliza el
mismo `copiar_resguardo()` de los CSV — mismo mecanismo, sin código nuevo que
mantener por separado. `insumos-af.js` conserva ese nombre exacto ahí: el HTML
lo busca así sin importar cómo se llame el informe.

Al terminar, **abrir el HTML ya alcanza**: no hay que arrastrar ni copiar nada.
Y quien solo tenga acceso a la carpeta de OneDrive del cliente encuentra ahí
mismo el informe del mes con AlertsList y GLPI ya adentro, sin pasar por el
equipo donde corrió la extracción.

```bash
python3 automatizacion/actualizar_informe.py                 # el mes que ya cerró (agosto -> reporta julio)
python3 automatizacion/actualizar_informe.py --periodo 2026-06   # un mes puntual, si hace falta
python3 automatizacion/actualizar_informe.py --sin-copiar     # solo genera en salida/, no toca el HTML
python3 automatizacion/actualizar_informe.py --abrir          # además, lo abre en el navegador al terminar
```

**El periodo nunca hay que decirlo a mano.** Sin `--periodo`, los tres scripts
(este orquestador y los dos extractores) calculan solos el **mes que ya
cerró** — si hoy es agosto, julio — vía `mes_cerrado()` en `insumos_af.py`. El
mes en curso nunca se reporta: todavía no tiene sus casos/alertas completos.
`--periodo` sigue existiendo para un mes puntual (reprocesar algo atrasado,
pruebas), pero la tarea programada del primero de cada mes no necesita
pasarlo nunca.

`--abrir` es para cuando alguien lo corre a mano y quiere ver el resultado de
una vez. **No usarlo en la tarea programada**: en el servidor desatendido no
hay quien vea el navegador, y sin el flag el script no intenta abrir nada —
solo imprime la ruta del HTML para abrirlo a mano si hace falta.

Los dos extractores también pueden correrse por separado (`extraer_glpi.py`,
`extraer_alertas.py`) si solo hace falta una fuente, o para depurar una en
concreto. En cualquier orden, uno solo o los dos: cada uno lee el
`insumos-af.js` existente antes de escribir, así que no se pisan entre sí.

`insumos-af.js` se copia **junto al HTML**. Al abrirlo, el informe lo detecta y
carga lo que traiga sin que nadie arrastre nada. Si falta una fuente (por
ejemplo, GLPI falló pero AlertOps sí respondió), esa fuente sigue siendo
manual y la otra se carga igual — **ninguna fuente bloquea a la otra**, ni a
nivel del HTML ni a nivel de `actualizar_informe.py` (corre ambas extracciones
siempre, aunque una falle). Si el archivo completo no está, el centro de carga
funciona igual que siempre: **la carga manual nunca dejó de existir.**

No puede ser un `.json` leído con `fetch`: abierto desde el disco, el navegador
bloquea toda petición al sistema de archivos. Un `<script>` vecino sí carga, y
es la única puerta que queda sin montar un servidor.

Ese archivo se carga sin que nadie lo apruebe, así que el informe trata cada
fuente como origen no confiable: comprueba formato, periodo declarado y
**huella SHA-256** del contenido antes de aceptarla. Si una fuente no cuadra,
avisa y esa fuente queda en manual — la otra, si vino bien, se carga igual.

Verificado en el navegador **con datos reales de las dos APIs** (no
sintéticos — ver el detalle en cada sección de abajo): la carga automática
deja los casos y las alertas del periodo con su trazabilidad completa y ajusta
el periodo del informe al del insumo; un contenido alterado en **una sola**
fuente se rechaza por la huella sin afectar a la otra, y el informe queda en
manual solo para esa fuente.

**Pendiente de comprobar en el equipo donde se use:** si el navegador cachea
`insumos-af.js` entre aperturas. El informe le añade un sufijo variable para
evitarlo, pero en el visor de pruebas siguió sirviéndose de caché. Como defensa
de fondo, el aviso de carga **siempre muestra la fecha de extracción**: si
apareciera un insumo viejo, la fecha lo delata.

---

## GLPI

### Cómo ejecutar la sonda

```bash
cp automatizacion/.env.ejemplo automatizacion/.env
# completar GLPI_USER y GLPI_PASSWORD en ese archivo, y luego:
python3 automatizacion/sonda_glpi.py
```

### Qué prueba, y en qué orden

1. **API REST** (`/apirest.php/initSession`) — la vía limpia. Si responde, se
   construye sobre ella y no hace falta nada más.
2. **Sesión web** — login por formulario con el token `_glpi_csrf_token`, igual
   que lo haría un navegador, pero sin navegador.
3. **searchOptions** — descubre qué número identifica a «Entidad» y a «Fecha de
   apertura» *en esta instalación*. Los IDs cambian entre versiones y plugins;
   por eso se descubren en vez de escribirse a mano.
4. **Exportación CSV** — `display_type=3` con `export_all=1` (todas las páginas,
   no solo la visible). Prueba dos veces: sin filtrar, y filtrando por entidad
   dentro de GLPI.

---

## AlertOps

A diferencia de GLPI, aquí no hizo falta una sonda de descubrimiento a ciegas:
AlertOps publica un Swagger completo en
`https://api.alertops.com/swagger/v2/swagger.json`, con `GET /api/v2/alerts`
ya documentado (filtros por fecha, prioridad, política de escalamiento,
paginación por cursor). `sonda_alertops.py` solo confirma que la api-key de
*esta cuenta* autentica contra esa API y que el esquema real coincide con lo
publicado — no descubre nada que no estuviera ya en la documentación.

### Cómo ejecutar la sonda

```bash
cp automatizacion/.env.ejemplo automatizacion/.env
# completar AOPS_API_KEY en ese archivo (AlertOps → Administration →
# Subscription Settings), y luego:
python3 automatizacion/sonda_alertops.py
```

### Diferencia importante frente a GLPI: no hay filtro de entidad en la API

La cuenta de AlertOps es de **SETI completo**, no de Acción Fiduciaria. La API
no tiene un campo de entidad/cliente para filtrar en origen — a diferencia de
GLPI, donde `criteria[…][field]=80` (Entidad) sí existe. El cliente viaja como
texto libre («`Cliente: accion_fiduciaria`») dentro de `Topic`/`Message`, así
que `extraer_alertas.py` trae **todas** las alertas de la cuenta en el rango de
fechas y filtra por ese texto **antes de escribir el CSV** — con la misma
extracción por expresión regular y normalización (sin acentos, minúsculas,
guiones bajos → espacios) que ya usa `cargarAlertas()` en el navegador para el
export manual. El CSV final nunca contiene alertas de otros clientes de SETI.

### Columnas que no se generan (y por qué)

El export manual de hoy trae `ServiceName`, `InitialAssignedDate`,
`TimeToAssign` y `TimeToResolve`. La API documentada no expone esos campos, así
que el extractor **no los inventa** — los omite. `cargarAlertas()` no los
necesita para calcular nada (solo usa Alert ID, Created Date, Escalation
Policy/Response Play, y opcionalmente Topic/Message para el cliente), así que
la ausencia no afecta al informe.

### Verificado (28/07/2026, contra las cuentas reales de SETI)

- **AlertOps, en vivo:** `sonda_alertops.py` autenticó contra la cuenta real
  y confirmó el esquema. `extraer_alertas.py --periodo 2026-06` trajo 121
  alertas de toda la cuenta SETI, 53 de Acción Fiduciaria tras el filtro de
  cliente, 6 de ellas «No reconocimiento» (prioridad alta).
- **Comparado contra el export manual** (`Insumos/AlertsList.xlsx`, 61 filas):
  49 alertas coinciden por ID en ambos. De las 16 que difieren, **12** están
  fuera del mes calendario en el archivo manual (correctamente excluidas por
  el informe) y **4** son alertas del 1-2 de junio que **el export manual se
  perdió** — empezaba recién el día 9. La extracción automática resultó **más
  completa** que la manual, no solo igual de buena; las 6 de prioridad alta
  coinciden exactamente en ambas.
- **GLPI, en vivo:** `extraer_glpi.py --periodo 2026-05` trajo los mismos 8
  casos, ID por ID, que `Insumos/glpi (20).xlsx` (el manual trae espacio como
  separador de miles: `300 861` = `300861`).
- **Informe HTML real:** con `actualizar_informe.py --periodo 2026-06` y el
  `insumos-af.js` resultante copiado junto al HTML, abrir
  `informe-accion-fiduciaria 1.html` carga las dos fuentes solas (GLPI: 0
  casos en junio, confirma el hallazgo ya conocido; AlertOps: 53 alertas) sin
  errores de consola.

## Indisponibilidades (cruce de atribución a SETI)

Encargo del usuario, 28-29/07/2026: el consolidado de disponibilidad hoy
decide «incidentes atribuibles a SETI» solo por el texto de la categoría del
ticket de GLPI (`cargarGlpi()`, regla `I=/incidente|incident/` menos
revisiones de alerta) — poco confiable, porque no dice si la causa real fue de
SETI o del cliente. `DisponibilidadMensual.xlsx` (SharePoint, Célula 3,
compartido entre Acción Fiduciaria/Bancoldex/EMI) sí tiene ese dato real,
diligenciado a mano por el equipo: columna «Atribuible a SETI»
(SI/NO/EN ESTUDIO), enlazada por «NUMERO CASO GLPI».

```bash
pip install -r automatizacion/requirements.txt   # openpyxl, primera dependencia externa
# RUTA_INDISPONIBILIDADES en .env, apuntando directo al .xlsx (no a una carpeta)
```

**Enganchado a `actualizar_informe.py`** (y por lo tanto a `ejecutar.bat`/
`ejecutar.ps1`/la tarea programada): corre solo, como tercer paso, después de
GLPI y antes de copiar el insumo junto al HTML — no hace falta invocarlo
aparte. También puede correrse solo para depurar:

```bash
python3 automatizacion/extraer_indisponibilidades.py                  # el mes que ya cerró
python3 automatizacion/extraer_indisponibilidades.py --periodo 2026-07
```

Es **opcional y no bloqueante**, igual que `RUTA_ONEDRIVE`: si
`RUTA_INDISPONIBILIDADES` no está configurada (p. ej. un equipo donde esa
biblioteca de SharePoint todavía no se sincronizó), se omite con un aviso y
`actualizar_informe.py` sigue igual — no cuenta como falla ni afecta el código
de salida general (que solo depende de GLPI/AlertOps).

Requiere haber corrido antes `extraer_glpi.py` para el mismo periodo (lee
`salida/glpi-<periodo>.csv`); si no está —incluido el caso en que GLPI falló
en esa misma corrida (¡probado en vivo el 29/07/2026: se cayó la conexión a
`www.seti.co/glpi` a mitad de sesión!)—, avisa y no toca nada, sin tumbar el
resto de la corrida. Para cada incidente de GLPI del periodo busca su caso en
la hoja «Indisponibilidades» (por «NUMERO CASO GLPI», sin importar de qué mes
sea la fila) y reporta lo que dice el equipo; sin match, lo deja
`SIN_VERIFICAR` — nunca inventa una atribución.

### El HTML ya usa esta reconciliación (29/07/2026)

`cargarGlpi()` en `informe-accion-fiduciaria 1.html` lee la reconciliación
(vía `archivos.indisponibilidades` en `insumos-af.js`) y, si un ticket ya está
marcado «NO», lo excluye del conteo de «incidentes atribuibles a SETI» — el
dato real del equipo manda sobre la inferencia por categoría. «SI»,
«EN ESTUDIO» o sin match siguen contando como atribuibles (regla de siempre);
sigue pendiente decidir con negocio qué hacer específicamente con
«EN ESTUDIO». `historico_casos.json` también se corrige para el periodo
procesado, para que el número quede bien incluso después de que el mes deje
de ser el actual.

Validado en vivo el 29/07/2026: el usuario diligenció el caso real (309522,
`Atribuible a SETI: NO`) en el Excel; al volver a correr el extractor, la
tarjeta «Casos atendidos» pasó de **52 casos · 1 atribuible a SETI** a **51
casos · 0 atribuibles a SETI**, sin tocar nada en el HTML a mano.

### El archivo standalone es una ALERTA, no un registro permanente

A diferencia de `glpi-*.csv`/`alertops-*.csv` (una foto fija de lo que dijo la
fuente al extraer), `indisponibilidades-<periodo>.csv` — tanto en
`salida/` como su copia en `RUTA_ONEDRIVE` — solo existe mientras haya al
menos un incidente de GLPI **sin fila correspondiente** en el Excel
(`SIN_VERIFICAR`). Su única función es avisar «hay algo pendiente de
registrar»; una vez el equipo registra todos los casos del periodo (con
cualquier valor: SI, NO o EN ESTUDIO), el script **borra el archivo** —local y
su copia en OneDrive— porque ya no aporta nada. Vuelve a aparecer solo si
aparece un incidente nuevo sin registrar.

Esto es independiente del insumo que llega al HTML: `archivos.indisponibilidades`
en `insumos-af.js` sigue llevando la reconciliación completa mientras haya
cruce contra GLPI, exista o no el archivo standalone — así el conteo de
«atribuible a SETI» del informe no se revierte solo porque ya no quede nada
pendiente que mostrar en el archivo visible.

Detalle completo del diseño original y las preguntas abiertas en
[`../docs/2026-07-29-relevo-sesion-28-julio.md`](../docs/2026-07-29-relevo-sesion-28-julio.md)
§2 y §8.

## Histórico de casos (independiente de la hoja «Casos»)

Encargo original del usuario (capturas de WhatsApp, ver
docs/2026-07-29-relevo-sesion-28-julio.md §5.1, punto 1): *"que el HTML tenga
conocimiento de los casos anteriores... independiente de esa hoja
totalmente"*. Antes de esta sesión (29/07/2026) estaba solo diseñado, no
construido — `cargarCasos()` en el HTML reconstruía todo el histórico
(`DATA_CASOS.historico`, el que alimenta el modal de evolución de slide 5)
leyendo la hoja «Casos» del consolidado **cada vez** que se cargaba. Sin
cargar el Excel a mano, el informe no sabía nada de meses anteriores — ni
siquiera con GLPI/AlertOps ya cargados automáticamente.

**Construido, enganchado y validado el 29/07/2026:**

1. **Ledger acumulado** (`automatizacion/salida/historico_casos.json`,
   `historico_casos.py`): un JSON que crece mes a mes por *upsert* — cada
   extractor toca solo su campo del mes que le corresponde
   (`extraer_glpi.py` → requerimientos/incidentes, con la misma clasificación
   que `cargarGlpi()`, vía `clasificar_caso_glpi()` en `insumos_af.py`;
   `extraer_alertas.py` → alertas), sin pisar lo que dejó el otro ni otros
   meses. Se adjunta a `insumos-af.js` como campo `historico` de nivel
   superior (no bajo `archivos.*`, porque no es un CSV de una sola fuente).
2. **Backfill de una sola vez** (`backfill_historico_casos.py`): pobló el
   ledger con sep-25 → jun-26 leyendo la hoja «Casos» del consolidado real,
   con la misma heurística de encabezado que usa `cargarCasos()` en el HTML
   (la fila con más columnas de fecha). Nunca pisa un periodo que el ledger
   ya tenga (`solo_si_falta`), así que correrlo de nuevo por error no hace
   daño. Julio-2026 en adelante ya lo cubre la automatización en vivo.
3. **Consumo en el HTML** (`aplicarHistoricoAutomatico()`, cerca de
   `DATA_CASOS`): si `insumos-af.js` trae `historico`, sus periodos mandan
   sobre `DATA_CASOS.historico` — incluido si alguien carga o recarga el
   consolidado después (se reaplica al final de `cargarCasos()`), así el
   ledger no se revierte a la hoja del Excel. Respeta los mismos límites que
   el Excel: nunca un mes posterior al periodo seleccionado en el desplegable
   (mismo criterio que `columnasPeriodo`/`antesOIgual`), ni anterior al inicio
   de contrato.

```bash
# una sola vez, para poblar los meses anteriores a la automatización
python3 automatizacion/backfill_historico_casos.py --archivo "/ruta/Disponibilidad Consolidado Mayo.xlsx"
```

De ahí en adelante no hace falta nada manual: `extraer_glpi.py` y
`extraer_alertas.py` (ya enganchados a `actualizar_informe.py`/`ejecutar.bat`)
alimentan el ledger solos cada mes.

**Validado de la forma más exigente posible** (mismo método que el informe
autocontenido, §5.4 del relevo): se generó un HTML autocontenido con
`insumos-af.js` real (glpi + alertas + indisponibilidades + el ledger de 11
meses) incrustado, servido por HTTP local, **sin cargar el consolidado en
ningún momento**. Resultado, vía JavaScript en la propia página:

```
REPORTE.d('casos').datos.historico.periodos → 2025-09 … 2026-07 (11 meses)
REPORTE.d('casos').datos.historico.alertas → [56,59,47,66,74,70,83,54,30,61,45]
REPORTE.d('casos').datos.historico.requerimientos → [1,0,1,2,5,1,0,3,6,0,6]
REPORTE.d('casos').datos.historico.incidentes → [0,0,1,0,1,0,0,1,0,0,1]
```

Sin errores de consola. La tarjeta «Casos atendidos» del periodo mostró **52
casos · 45 alertas · 6 requerimientos · 1 atribuible a SETI** — coincide con
lo que ya reportaba GLPI/AlertOps en vivo, ahora también respaldado por el
histórico completo sin abrir el Excel.

### Bug real encontrado y corregido: el modal se quedaba pegado a un rango viejo

Al probarlo en el navegador (no en un test aislado — el usuario lo notó
abriendo el informe real), el modal de «Casos» no abría en los 3 meses que
debía (jun-26 a jul-26 en vez de may-26 a jul-26): el filtro «3M» seguía
mostrando 2 meses en vez de 3.

**Causa:** `montarHistorico()` (el componente de rango 3M/6M/12M/Todo,
compartido con Indicadores/Disponibilidad/Backups) solo recalculaba el rango
automático cuando cambiaba el **último mes** del histórico. Con el ledger
nuevo, «Casos» se publica varias veces mientras carga la página: primero con
un solo mes (el que `indiceMesActualHistorico()` crea al vuelo, antes de que
llegue el insumo), y milisegundos después ya con el ledger completo — pero el
último mes es el mismo en ambas publicaciones (el periodo del informe), así
que la condición nunca detectaba el cambio y el rango se quedaba fijo en el
primer cálculo, hecho con muy pocos meses.

**Corrección:** además de «¿cambió el último mes?», el chequeo ahora también
mira «¿cambió el TOTAL de meses?» (`cacheVieja.totalPeriodos!==periodos.length`).
Aplicado en los dos lugares del HTML con este patrón: `montarHistorico()`
(Casos/Indicadores/Disponibilidad) y el radar de Disponibilidad por CI/Backups
(mismo riesgo, mismo código duplicado).

**Validado con dos escenarios reales:**
- El HTML real de OneDrive (julio-26, 11 meses): `desde: 2026-05, hasta:
  2026-07` — 3 meses correctos.
- Simulación de agosto-26 ya cerrado (12 meses, agregando el mes con
  `historico_casos.actualizar_periodo()`): `desde: 2026-06, hasta: 2026-08` —
  la ventana móvil de 3 meses se corre sola al mes siguiente, sin tocar nada
  a mano. Confirma el comportamiento pedido: cuando cierre un mes nuevo, el
  informe se abre mostrando los últimos 3 (mes actual + 2 anteriores),
  siempre.

### El ledger viaja con el repo (29/07/2026) — y por qué eso no es lo mismo que el informe

`historico_casos.json` vivía solo dentro de `automatizacion/salida/`, ignorada
en bloque junto con los CSV crudos (que sí traen datos de otros clientes de
SETI). Al cambiar de equipo (Mac → Windows) el ledger se perdió y hubo que
rehacer el backfill a mano. Como este archivo son solo conteos mensuales ya
agregados de Acción Fiduciaria —nunca datos crudos de otro cliente—, se
excluyó de la regla general del `.gitignore`
(`!automatizacion/salida/historico_casos.json`) y se commiteó el backfill ya
corrido. De ahora en adelante un `git clone`, un `.zip` del repo o pasar el
proyecto a otra persona trae este histórico sin rehacer el backfill; la
automatización mensual lo sigue actualizando por upsert en cada corrida,
corra donde corra.

**Importante — esto no reemplaza al informe autocontenido.** Un `.zip` del
repositorio trae `historico_casos.json` (los números crudos) y la plantilla
`informe-accion-fiduciaria 1.html` **sin datos incrustados** — `insumos-af.js`
(el paquete que empareja el ledger con GLPI/AlertOps y se incrusta en el
HTML) sigue —correctamente— fuera de git, porque depende de credenciales y de
la corrida del mes. Abrir esa plantilla desde un `.zip` del repo muestra el
centro de carga manual de siempre, no el informe ya cargado. Para entregarle
a alguien (p. ej. un jefe) un informe que abra ya con todo cargado, sin
Python ni credenciales, el archivo correcto es el **HTML autocontenido** que
`actualizar_informe.py` deja en `RUTA_ONEDRIVE/<Mes>/Informe Accion
Fiduciaria <Mes> <Año>.html` — verificado copiándolo solo, sin nada más al
lado, a una carpeta vacía: carga el periodo y los 11 meses de histórico sin
errores de consola. Confirmado con un `git archive` real del `HEAD` de esta
sesión: la plantilla del repo pesa lo mismo con o sin el ledger commiteado
(`insumos-af.js` sigue sin estar ahí); el HTML autocontenido de OneDrive, en
cambio, sí lo trae todo incrustado.

### Bug de consola en Windows (29/07/2026)

`cargar_env()` —lo primero que llaman los seis scripts (sondas, extractores y
el orquestador)— imprime caracteres como «→» que la consola por defecto de
Windows (cp1252, no UTF-8) no sabe codificar. El `UnicodeEncodeError`
ocurría **después** de que GLPI/AlertOps ya habían extraído los datos
correctamente, pero el traceback tumbaba el proceso: `actualizar_informe.py`
veía un código de salida distinto de 0 y reportaba «FALLÓ» para ambas fuentes
aunque el insumo sí se había generado bien. Corregido reconfigurando la
consola a UTF-8 dentro de `cargar_env()` — un solo punto para los seis
scripts. Validado en vivo en Windows: GLPI y AlertOps ya reportan «OK».

## Credenciales

- **Cuenta de servicio de solo lectura** en ambas plataformas, no la personal
  de nadie.
- Nunca dentro de este repositorio, del HTML ni de un archivo versionado.
- En el servidor definitivo: gestor de secretos del sistema o Key Vault.

Solo se necesita Python 3, sin dependencias externas, para ambos extractores:
así pueden correr tal cual en el servidor donde acaben viviendo las tareas
programadas.

Dejan la evidencia en `automatizacion/salida/` — HTML/JSON de cada respuesta y
el CSV si logró exportarlo. **Esa carpeta está en `.gitignore`**: las
respuestas crudas de ambas plataformas traen datos de todos los clientes de
SETI, no solo de Acción Fiduciaria.

## Lo que falta

- **Cuentas de servicio de solo lectura**, en GLPI y en AlertOps. Hoy
  `automatizacion/.env` tiene credenciales **personales** en ambas — funcionan
  y ya se verificaron en vivo, pero si la automatización corre con la cuenta de
  una persona, el día que la cambie el proceso se cae en silencio, y cada
  acción queda registrada a su nombre. Cambiarlas por cuentas de servicio antes
  de dejar esto desatendido.
- ~~Depósito automático del informe en SharePoint/OneDrive del cliente~~ —
  **ya construido y validado** (28-29/07/2026, ver «El HTML ya usa esta
  reconciliación» y «El ledger viaja con el repo» más arriba):
  `actualizar_informe.py` deja el informe **autocontenido** (GLPI + AlertOps +
  histórico + indisponibilidades ya incrustados) directo en
  `RUTA_ONEDRIVE/<Mes>/`, que sincroniza solo a la biblioteca de SharePoint del
  cliente — sin depender de que nadie arrastre nada. Probado en dos equipos
  distintos (Mac y Windows). Lo que sigue pendiente es dónde corre esto
  desatendido (siguiente punto): hoy solo funciona en un equipo con sesión de
  OneDrive iniciada.
- **Dónde se ejecuta.** Necesita una máquina encendida a la 1:00 a. m.: el
  servidor de Carlos Barrera, Azure Functions u otra, por decidir. Puede ser
  la misma para las dos extracciones — es un solo comando
  (`actualizar_informe.py`).
- **Programación mensual y alerta ante fallo.** El script ya distingue qué
  fuente falló y cuál no en su código de salida y su resumen por consola;
  falta engancharlo a una tarea programada (cron / Task Scheduler) y a un
  aviso a Teams cuando el resumen no sea «OK / OK».
- **Responsable operativo** que reciba esa alerta y actúe si el proceso falla.
