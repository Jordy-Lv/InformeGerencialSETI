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
| `insumos_af.py` | Módulo compartido: lee/escribe `insumos-af.js` para que los dos extractores puedan aportar su archivo sin borrar el del otro. |
| `.env.ejemplo` | Plantilla de credenciales de ambas fuentes, más `RUTA_ONEDRIVE` (opcional). Cópiala a `.env` (ignorado por git). |

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
- **Depósito automático del informe en SharePoint/OneDrive del cliente.**
  Distinto de `RUTA_ONEDRIVE` (que ya existe y solo resguarda los CSV
  originales para trazabilidad interna): hoy `actualizar_informe.py` deja
  `insumos-af.js` en el equipo donde corre (junto al HTML local); falta que
  el informe mismo se escriba en la biblioteca del cliente
  (`/Informes/AccionFiduciaria/2026-06/…`).
- **Dónde se ejecuta.** Necesita una máquina encendida a la 1:00 a. m.: el
  servidor de Carlos Barrera, Azure Functions u otra, por decidir. Puede ser
  la misma para las dos extracciones — es un solo comando
  (`actualizar_informe.py`).
- **Programación mensual y alerta ante fallo.** El script ya distingue qué
  fuente falló y cuál no en su código de salida y su resumen por consola;
  falta engancharlo a una tarea programada (cron / Task Scheduler) y a un
  aviso a Teams cuando el resumen no sea «OK / OK».
- **Responsable operativo** que reciba esa alerta y actúe si el proceso falla.
