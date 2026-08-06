# Relevo de sesión — 28 de julio de 2026

**Para:** quien continúe (Claude, en otra sesión, u otra persona).
**Qué es esto:** el registro completo de una sesión larga con tres frentes de
trabajo que terminaron entrelazados. Léelo antes de tocar nada relacionado con
disponibilidad de bases de datos, la automatización de GLPI/AlertOps, o la
documentación del proyecto — te ahorra repetir análisis ya hechos y, más
importante, te evita repetir un error real que yo mismo cometí a mitad de
sesión (ver §3).

**Commit de cierre de esta sesión:** `27751fb` — *"Informe autocontenido en
OneDrive, levantamiento de disponibilidad BD y limpieza de docs obsoletos"*,
ya empujado a `origin/main`.

---

## 0. Cómo está organizada esta sesión

Empezó como un encargo ("audita el consolidado de disponibilidad") y terminó
tocando tres cosas distintas, en este orden:

1. **Levantamiento técnico de la automatización de disponibilidad de bases de
   datos** (Oracle, con Mateo Flórez Calonge, DBA) — §1 y §2.
2. **Corrección de errores propios** cometidos en ese levantamiento, señalados
   por el usuario — §3. Es la parte más importante para no repetir.
3. **Limpieza de documentación obsoleta** del repo — §4.
4. **Construcción real del "informe autocontenido en OneDrive"** — el grueso
   técnico de la sesión, con varias vueltas de diseño hasta llegar a la
   solución correcta — §5 a §8.
5. **Documentación y cierre** (actualización de un `.docx` existente, commit y
   push) — §9.

Si solo vas a leer una sección antes de seguir trabajando: **§5.4 (por qué se
llegó al HTML incrustado) y §8 (qué falta)**.

---

## 1. Levantamiento de disponibilidad de bases de datos (Oracle)

### 1.1 El encargo original

El usuario pidió auditar `Disponibilidad Consolidado Mayo.xlsx` (el nombre
dice «Mayo» pero el archivo trae datos hasta junio de 2026 — confirmado, no es
un hallazgo nuevo, ver §3.2) y evaluar un script de Mateo,
`oracle_disponibilidad.sh`, que calcula disponibilidad Oracle leyendo
`alert.log` y genera un HTML operativo.

**Primer intento, sin el Excel real.** El archivo no estaba disponible al
principio, así que reconstruí su contenido a partir del store serializado
(`window.__ESTADO__`) dentro de un HTML exportado que sí tenía los datos
cargados. Escribí un levantamiento completo con esa reconstrucción.

**Luego el usuario adjuntó el Excel real** (`Downloads/Junio/Disponibilidad
Consolidado Mayo.xlsx`). Auditar el archivo real —abriendo fórmulas, filas y
columnas ocultas— confirmó que la reconstrucción anterior había sido
correcta, y además reveló defectos que solo se ven abriendo el archivo:

- **8 hojas, no 7**: hay una hoja `Capacidad` (ocupación de filesystems) que el
  informe HTML no lee, y cuyos datos coinciden celda por celda con el informe
  mensual de Oracle que el equipo DBA ya produce (`Informe_Mensual_Oracle_...docx`)
  — es decir, alguien transcribe a mano un dato que ya se genera solo.
- **Columnas y filas ocultas en varias hojas.** La caída de nov-25 (98,02 %)
  está en una columna oculta de la hoja `Disponibilidad`; quien mantiene el
  archivo no la ve. Las 3 filas de la hoja `Mitigación` también están
  ocultas — el autor las dio de baja, pero el parser del informe las lee
  igual si se carga el consolidado sin el archivo cualitativo mensual.
- **Tres fórmulas de totales rotas** en la hoja `Grafica Dispo y Gestion`
  (`=AVERAGE(...)` con rangos que no llegan a junio-26, cada una con un rango
  distinto). El informe no las usa —calcula su propio promedio— así que no
  afecta al cliente, pero cualquiera que abra el Excel ve un número viejo.
- **Dos bloques de metas contradictorios** en la hoja `Inidcadores` (entregables
  80 % vs. 90 %; "tiempos de Atención" 90 % vs. "tiempos de Solución" 95 %). El
  informe acierta por casualidad de orden de filas, no por diseño.
- **El indicador "Disponibilidad de la plataforma administrada" es el mínimo
  entre los 14 CI, no el promedio** — verificado aritméticamente (nov-25:
  mínimo 98,02 % = el indicador; promedio real 99,29 % ≠ el indicador).
- **Los 9 CI no-Oracle llevan 18 meses en 100,00 % exacto**, sin una sola
  variación. El usuario confirmó después que sí se miden, pero que se está
  probando primero con los CI de Oracle (fase 1) — no es una alarma, es el
  plan.
- **Backups: 266 celdas en 100 % durante 19 meses.** El usuario confirmó que sí
  hay monitoreo real detrás y que es normal — no es una alarma tampoco.

Todo esto —y el detalle celda por celda, con fórmulas exactas— está en
[`2026-07-28-disponibilidad-bd-levantamiento.md`](2026-07-28-disponibilidad-bd-levantamiento.md).
No lo dupliques aquí; ese documento es la fuente de la verdad para ese tema.

### 1.2 El script de Mateo — evaluación

`oracle_disponibilidad.sh` está bien hecho: reconoce los tres formatos de
fecha del `alert.log`, encuentra instancias caídas vía `/etc/oratab`, distingue
caídas reales de estimadas, recorta ventanas a los bordes del período. Pero:

- Mide *N días hacia atrás*, no mes calendario — hay que corregirlo con
  `--desde`/`--hasta`.
- Solo cubre 5 de los 14 CI del cliente (los 5 que están en Oracle).
- Produce un solo número, y el Excel distingue "Disponibilidad Real" de
  "Disponibilidad SETI" — la diferencia entre ambas resultó ser un calendario
  de ventanas de mantenimiento que hoy no existe como insumo formal.

### 1.3 Recomendación entregada

**JSON estructurado, no el HTML que genera el script.** El HTML de Mateo es
válido como informe operativo para el equipo DBA (consérvese), pero como
integración es fràgil: los valores están en `<td>` sin `id`, un cambio
estético rompe la carga sin error visible, y además ya aplica la meta
contractual — duplicaría la regla de negocio que ya vive en el HTML del
informe (`cumpleMeta()`), con riesgo de que ambas diverjan sin que nadie lo
note.

El contrato técnico completo para Mateo —esquema JSON exacto, campos
obligatorios, manejo de nulos, prueba de reconciliación con datos reales
(nov-25 = 98,02 % es "la prueba clave")— está en
[`2026-07-28-contrato-tecnico-mateo.md`](2026-07-28-contrato-tecnico-mateo.md).
**Ya se le envió a Mateo** (mensaje del usuario: "ya yo le envié la
documentación que me pasaste inicialmente los dos .md a Mateo"). Él está
trabajando en su lado; nosotros seguimos en el nuestro (§5 en adelante).

### 1.4 Ideas de automatización adicionales, sin construir todavía

- **Grafana como fuente única.** Las alertas de AlertOps llegan con
  `IntegrationName: Grafana` y ya cubren Oracle y SQL Server. Si hay un
  Prometheus (u otro backend con series) detrás, una sola consulta podría
  resolver los 14 CI de una vez, sin escribir un script por motor. **Vale la
  pena preguntarlo antes de construir nada de fase 2.**
- Backups desde el catálogo RMAN (mismo contrato, mismo Mateo).
- SLA de GLPI calculado (no transcrito) para el indicador "Gestión del
  Servicio" — falta solo la definición contractual de qué fecha cuenta.

---

## 2. Documento nuevo encontrado: `DisponibilidadMensual.xlsx`

A mitad de sesión el usuario compartió otro archivo —distinto del
consolidado— que vive en SharePoint (`Célula 3`, compartido entre varios
clientes de SETI: Acción Fiduciaria, Bancoldex, EMI). Hoja `Indisponibilidades`:
un log de eventos de caída, llenado a mano por el equipo, con una columna
clave: **`Atribuible a SETI` (SI/NO/EN ESTUDIO)** y otra, `NUMERO CASO GLPI`,
**hoy vacía** (el equipo la va a llenar).

Esto es la pieza que faltaba para la pregunta abierta de "Real vs. SETI" del
levantamiento (§1.1). El usuario pidió ideas concretas para usar este archivo
en la validación de "incidentes atribuibles a SETI" que hoy el informe infiere
solo por texto de categoría de GLPI (poco confiable). Diseño propuesto (no
construido aún, ver §8):

- Un extractor nuevo (`extraer_indisponibilidades.py`, paralelo a los otros
  dos) que lea este Excel desde su ruta sincronizada de OneDrive (variable
  nueva, `RUTA_INDISPONIBILIDADES`, mismo patrón que `RUTA_ONEDRIVE`), filtre
  por cliente y período, y cruce `NUMERO CASO GLPI` contra los casos que GLPI
  ya clasificó como "incidente".
- Si el cruce encuentra el caso: la columna `Atribuible a SETI` manda sobre la
  inferencia por categoría. Si no lo encuentra (el ID aún no está puesto):
  se mantiene la regla de hoy, pero marcado como "sin verificar".
- Pendiente de decidir con negocio: qué hacer con "EN ESTUDIO".
- **Hoy, con el archivo tal como está, el cruce no encontraría nada** — las 3
  filas de Acción Fiduciaria en el archivo tienen `NUMERO CASO GLPI` vacío. El
  valor de este diseño aparece cuando el equipo empiece a llenarlo.

Esto quedó como diseño discutido y explicado en el chat, **no implementado**
en código todavía.

---

## 3. Corrección de un error propio — importante para no repetirlo

El usuario me corrigió con fuerza en un punto, y vale la pena explicarlo bien
porque es una lección de método, no solo un dato:

> *"aunque el insumo diga mayo pues viene con documentación o viene con datos
> de junio... no te guíes de toda la documentación que hay en el proyecto...
> tenías que tener más en cuenta cómo funciona el HTML actualmente."*

**Lo que pasó:** encontré que la hoja `Casos` del consolidado certifica **61**
alertas para junio, mientras que un documento viejo del proyecto
(`AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md`) decía que la cifra correcta era **49** y
que "no existe la discrepancia". Concluí —mal— que ese documento estaba
desactualizado y que había que corregirlo a 61.

**Estaba equivocado.** Repliqué la lógica real de `cargarAlertas()`/
`cargarGlpi()` del HTML contra los archivos reales de ese mes y el total que
el informe efectivamente reporta es **49** (alertas dentro del mes calendario
+ 0 requerimientos + 0 incidentes de GLPI ese mes). El **61** es otra métrica:
el total de filas de AlertsList **sin filtrar por mes** — coincide exactamente
con ese número, lo que sugiere que quien llena la celda del Excel cada mes
copia "total de filas del export", no "alertas del mes calendario". Son dos
definiciones distintas, no un documento mal escrito. La regla de negocio ya
decidida (mes calendario → 49) seguía siendo la correcta. Terminé retirando mi
propia "corrección" tanto del documento como de mis mensajes.

**La lección, en general:** una celda o un documento del proyecto pueden estar
técnicamente "bien" y aun así no ser la respuesta correcta, si no se verifica
**cómo el HTML realmente consume y reconcilia los datos en vivo** — no basta
con mirar el Excel aislado, ni con confiar en documentación vieja sin
contrastarla contra el código y, mejor todavía, contra una ejecución real.
Cuando algo no cuadre, replica la lógica del parser (`cargarCasos`,
`cargarGlpi`, `cargarAlertas`, `publicarCasos` en
`informe-accion-fiduciaria 1.html`) contra los archivos reales antes de
concluir que un dato o un documento está mal.

Dos aclaraciones más del usuario en esa misma corrección, para no
reabrirlas: la inconsistencia "Mayo" vs. datos de junio **ya estaba resuelta y
decidida**, no es un hallazgo para seguir señalando; y la bolsa de horas **se
configura a mano directamente en el HTML**, por diseño — no hay que buscarle
una fuente automática.

---

## 4. Limpieza de documentación del repositorio

A pedido del usuario ("busca candidatos de documentación vieja para
eliminar"), se auditó cada documento de `docs/` contra el estado real del
código antes de proponer nada (no repetir el error de §3 al revés: no borrar
por suposición). Se eliminó, con autorización explícita del usuario:

| Qué se borró | Por qué |
|---|---|
| `historico/` completa (`README.md`, `index 3.html`, backup pre-store) | El propio README decía "archivo muerto... no lo abras: cifras falsas". ~8 MB de HTML sin uso. |
| `docs/2026-07-22-backups-historico.md` | Documentaba la matriz de backups, reemplazada el mismo día por el radar de CI — el propio commit de reemplazo lo decía, y el código viejo ya no existe (confirmado por grep antes de borrar el doc de reemplazo). |
| `docs/2026-07-23-sesion-completa.md` | Versión larga de `2026-07-23-analisis-por-rango-y-redondeo.md` — el propio documento decía "el otro doc es la versión corta". Se conservó la corta. |
| `qa-report/report.md` y su carpeta | QA de julio con 0 hallazgos abiertos, ya resuelto. |
| `docs/AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md` | **Recortado, no borrado**: de 363 a ~40 líneas. Se conservó solo la tabla de decisiones de negocio vigentes (mes calendario, bolsa de horas manual, etc.); se eliminó el detalle bug-por-bug ya resuelto (era, de hecho, la fuente del error de §3). |

**Hallazgo aparte, sin resolver:** `automatizacion/README.md` referencia dos
archivos que no existen en el repo — `Automatizacion GLPI - Demo 24 julio
2026.docx` y `Acta - Analisis llamada Santiago Amaya Cely.docx`. No se tocó;
alguien debe confirmar si se perdieron o nunca se subieron.

---

## 5. El informe autocontenido en OneDrive — el trabajo principal de la sesión

### 5.1 El pedido original (capturas de WhatsApp)

El usuario compartió mensajes suyos (aparentemente instrucciones ya
capturadas antes, o repetidas para mí) con tres requisitos:

1. *"Se requiere que el consolidado de disponibilidad... se guarde de manera
   automática el historial de casos anteriores... evitando que Santiago deba
   seguir registrando casos manuales, y el HTML tenga conocimiento de los
   casos anteriores... independiente de esa hoja totalmente."* — histórico de
   casos que no dependa de la hoja `Casos` del Excel. **Diseñado, no
   construido** (ver §8).
2. *"Se requiere que la automatización pueda comparar los incidentes."* —
   ligado al cruce con `DisponibilidadMensual.xlsx` (§2). **Diseñado, no
   construido.**
3. *"El html debe ir en la carpeta de acción fiduciaria junto con los otros
   insumos"* y *"debe ir cargado con alert list y glpi ya cargados"* — **esto
   sí se construyó y se probó de punta a punta esta sesión.** Es el §5 en
   adelante.

### 5.2 Primera versión: copiar el HTML de autoría + `insumos-af.js` al lado

Se modificó `automatizacion/actualizar_informe.py` para que, si
`RUTA_ONEDRIVE` está configurada, además de las copias que ya dejaba (CSV
original en `salida/`, copia de resguardo del CSV en OneDrive, `insumos-af.js`
junto al HTML local), depositara también una copia del HTML de autoría +
`insumos-af.js` en `RUTA_ONEDRIVE/<Mes>/`.

**Bug real encontrado y corregido en el camino:** `actualizar_informe.py`
nunca leía `.env` por sí mismo — lo hacían `extraer_glpi.py` y
`extraer_alertas.py`, pero cada uno en su propio subproceso, así que
`RUTA_ONEDRIVE` nunca volvía al proceso padre. Se agregó `cargar_env()`
también en `actualizar_informe.py`. Sin este fix, el depósito a OneDrive
habría fallado en silencio siempre que corriera desde la tarea programada
real.

Se agregó también protección contra sobrescritura en `copiar_resguardo()`
(`insumos_af.py`): si el destino ya existe con contenido distinto, no lo pisa
— avisa y conserva el existente, salvo `FORZAR_ONEDRIVE=1`. Se probó en
aislado (carpeta temporal) con los 4 casos: primera copia, misma corrida
repetida, contenido distinto sin forzar, contenido distinto forzado. Los 4 se
comportaron como se diseñó.

### 5.3 Se encontró la carpeta real de OneDrive y se probó ahí

El usuario activó OneDrive en el Mac. Se ubicó la biblioteca real sincronizada:

```
/Users/yordypardopajaro/Library/CloudStorage/OneDrive-SETIS.A.S/ACCION FIDUCIARIA - 2026/
```

Nota importante para el futuro: **el año va en el nombre del propio acceso
directo** (`ACCION FIDUCIARIA - 2026`), no en una subcarpeta separada — así
que `RUTA_ONEDRIVE` debe apuntar ya a esa carpeta con el año incluido, y el
script solo agrega debajo el nombre del mes (sin año — decisión explícita del
usuario: *"aquí ya hay una regla que hice, debe ir el nombre del mes que se
está reportando y ya, sin tanto complique"*). Al pasar de año, alguien
actualiza esa línea de `.env` a mano.

Dentro ya había carpetas por mes (`Mayo`, `Junio`, `Abril`, `Enero_2026`,
`Febrero 2026`, `Marzo 2026` — nombres inconsistentes, heredados de antes) con
los insumos manuales reales de cada mes: el mismo `Disponibilidad Consolidado
Mayo.xlsx`, `glpi (20).xlsx`, `AlertsList.xlsx` que se auditaron en §1. Se
corrió `actualizar_informe.py --periodo 2026-07` **de verdad** contra las APIs
reales de GLPI y AlertOps (con las credenciales reales del `.env`, que
**siguen sin tocarse ni exponerse en el chat**), creando la carpeta `Julio`
por primera vez.

### 5.4 El bug que llevó al diseño final: el HTML solo venía vacío

Al abrir el HTML resultante, el usuario vio datos de **junio** en vez de
julio. Diagnóstico: la restauración automática desde IndexedDB del navegador
(datos de una sesión anterior con junio) corría antes que la carga automática
del insumo, y —lo más probable, no se pudo confirmar al 100 % porque el
usuario ya había cerrado la ventana— la pestaña nunca se recargó de verdad.

Luego el usuario planteó el problema real y más importante: **"si yo abro o
descargo netamente el HTML no me viene con los insumos... prácticamente el
HTML viene vacío."** El diseño de "HTML + `insumos-af.js` vecino" (incluso con
`insumos-af.js` escondido en una subcarpeta `_datos/`, que fue el paso
intermedio que se probó) **exige que ambos archivos viajen juntos** — si
alguien copia o descarga solo el `.html`, no hay datos.

**Solución final, implementada y probada:** los datos van **incrustados
dentro del propio HTML**, no en un archivo vecino.

- `insumos_af.py` ganó `incrustar_insumos(html_path, insumos_js_path)`: toma
  el HTML base y le inserta el contenido de `insumos-af.js` como un
  `<script>` propio, justo después de `<head>`, en una copia nueva.
- `informe-accion-fiduciaria 1.html` → `cargarInsumosAutomaticos()` ahora
  revisa primero si `window.__INSUMOS__` ya existe (por venir incrustado);
  solo si no, intenta el archivo vecino de siempre (`RUTAS_INSUMOS`, un
  arreglo con `_datos/insumos-af.js` y `insumos-af.js` como candidatos, en ese
  orden — mantiene compatibilidad con el flujo de desarrollo local en el Mac,
  que no se tocó).
- `actualizar_informe.py` ya no deposita `insumos-af.js` suelto en OneDrive
  para nada: genera el HTML incrustado (`incrustar_insumos`), lo escribe a un
  archivo temporal en `salida/`, y lo copia a la carpeta del mes.

**Verificado de la forma más exigente posible:** se copió *únicamente* el
`.html` (sin CSV, sin ningún otro archivo) a una carpeta vacía y aislada,
servida por HTTP local (`preview_start`/`preview_stop` del navegador
integrado), abierta en pestaña nueva. Resultado, vía JavaScript en la propia
página:

```
REPORTE.periodo → {mes: 6, anio: 2026, etiqueta: "jul-26"}
REPORTE.d('casos').datos → 44 alertas, 6 requerimientos, 1 incidente, 51 total
```

Esto es concluyente: si hoy es 28/07, el período por defecto sin ningún
insumo cargado habría sido **junio** (el mes anterior). Que saliera **julio**
solo es posible si el mecanismo de carga automática funcionó, con los datos
incrustados, sin nada más al lado. Sin errores de consola.

### 5.5 Protección contra sobrescritura, revisada para el nuevo diseño

Con el HTML completo (4.3 MB) como lo que se deposita, y no un
`insumos-af.js` chico, la protección original (comparar bytes) disparaba
aviso en **cada** corrida — porque el HTML lleva una marca de tiempo
incrustada que cambia siempre, aunque los datos no cambien. Se decidió, con
justificación explícita pedida y dada (ventajas/desventajas de cada opción):

- **Los CSV siguen protegidos** (`proteger=True`, por defecto): son el
  registro de auditoría; no deben pisarse en silencio.
- **El informe se exime** (`proteger=False`, parámetro nuevo en
  `copiar_resguardo()`): su función es mostrar la extracción más reciente
  disponible, no servir de registro congelado — protegerlo no cuidaría nada
  real, solo generaría fricción constante.

Probado con dos corridas reales seguidas, sin `FORZAR_ONEDRIVE`: los CSV (con
contenido idéntico) no se tocaron; el HTML se sobrescribió solo en cada
corrida (confirmado por marca de hora en disco).

---

## 6. Estructura final, verificada, de la carpeta de OneDrive

```
ACCION FIDUCIARIA - 2026/
  └── Julio/
        ├── Informe Accion Fiduciaria Julio 2026.html   (autocontenido, siempre se actualiza)
        ├── glpi-2026-07.csv                              (protegido)
        └── alertops-2026-07.csv                           (protegido)
```

Nada técnico suelto — ni `insumos-af.js`, ni ninguna subcarpeta `_datos/`
(ese enfoque intermedio se abandonó a favor de la incrustación).

---

## 7. Comandos

```bash
# uso normal — el mes cerrado se calcula solo
python3 automatizacion/actualizar_informe.py

# un período puntual
python3 automatizacion/actualizar_informe.py --periodo 2026-07

# si hiciera falta forzar que los CSV también se sobrescriban
FORZAR_ONEDRIVE=1 python3 automatizacion/actualizar_informe.py --periodo 2026-07
```

`RUTA_ONEDRIVE` y `FORZAR_ONEDRIVE` viven en `automatizacion/.env` (no
versionado). En este Mac, `RUTA_ONEDRIVE` ya quedó apuntando a la carpeta real
(`.../OneDrive-SETIS.A.S/ACCION FIDUCIARIA - 2026`) — confirmar que el mismo
acceso directo exista en el equipo donde termine corriendo la tarea
definitivamente.

---

## 8. Qué falta — para la próxima sesión

### Del informe autocontenido (§5)

- **Confirmar/crear el mismo acceso directo de OneDrive en el servidor
  definitivo** (Carlos Barrera / Azure / equipo de oficina — la decisión de
  "dónde corre la tarea" sigue pendiente, es organizativa no técnica) y
  apuntar `RUTA_ONEDRIVE` ahí. Hoy solo está probado en el Mac de desarrollo.
- La carpeta de prueba `Julio` en el OneDrive real quedó con datos parciales
  (al 28/07, mes sin cerrar) — decidir si se deja o se limpia cuando julio
  cierre de verdad.

### Del histórico de casos independiente del Excel (§5.1, punto 1)

Diseño discutido, no construido: un archivo propio
(`automatizacion/salida/historico_casos.json` o similar) que los extractores
actualicen mes a mes (upsert, nunca reescribir todo), empaquetado como una
clave nueva en `insumos-af.js`, con un parser nuevo en el HTML que reemplace
la dependencia de la hoja `Casos` del consolidado. Preguntas abiertas antes de
construirlo:
- ¿Se resguarda también en `RUTA_ONEDRIVE`, para sobrevivir el cambio de
  máquina?
- ¿Se hace un backfill de una sola vez desde el Excel (sep-25→jun-26), o se
  arranca la serie en blanco desde el primer mes que corra la automatización?

### De la validación de incidentes atribuibles a SETI (§2)

Diseño discutido, no construido: extractor nuevo
(`extraer_indisponibilidades.py`), variable `RUTA_INDISPONIBILIDADES`, cruce
por `NUMERO CASO GLPI`. Bloqueado en la práctica hasta que el equipo llene esa
columna en `DisponibilidadMensual.xlsx` (hoy vacía). Pendiente de decidir: qué
hacer con el estado "EN ESTUDIO".

### De la automatización de disponibilidad Oracle (§1)

- Mateo está trabajando con el contrato técnico ya enviado
  (§1.3). Cuando entregue el primer JSON real, la prueba de aceptación
  acordada es reproducir **98,02 %** en noviembre-25 para las 5 instancias.
- Confirmar con Santiago las dudas de negocio bloqueantes listadas en
  [`2026-07-28-disponibilidad-bd-levantamiento.md`](2026-07-28-disponibilidad-bd-levantamiento.md)
  §6 (motor de cada CI, qué distingue Real de SETI, metas contradictorias en
  `Inidcadores`, etc.).
- Preguntarle a Mateo por el Grafana/Prometheus detrás de AlertOps antes de
  construir la fase 2 (podría simplificar todo).

### Documentación

- El `automatizacion/README.md` referencia dos `.docx` que no existen en el
  repo (§4) — confirmar con el usuario si se perdieron.

---

## 9. Documentación actualizada y cierre

Se actualizó **`Automatizacion GLPI - Plan de cierre.docx`** (no se creó un
documento nuevo — ya existía, ya estaba dirigido a Santiago, y ya tenía una
fila "Pendiente" para exactamente este tema). Cambios: la fila de la tabla de
estado pasó a "Listo" con el detalle real; se agregó una sección nueva, **§9
"Informe autocontenido en OneDrive"**, con el mecanismo, la verificación
realizada y los comandos; se ajustaron el resumen ejecutivo y las secciones de
pendientes/responsables. Verificado renderizando a PDF (se instaló LibreOffice
y Poppler en el Mac para poder hacerlo) e inspeccionando visualmente las
páginas editadas — se encontró y corrigió un error propio de escape XML
(`<Mes>`/`<Año>` sin escapar rompían el documento) antes de darlo por bueno.

Todo quedó en un solo commit, **`27751fb`**, ya empujado a
`origin/main` — ver el mensaje del commit para el resumen de los tres frentes.

**Archivos nuevos de esta sesión:**
- `docs/2026-07-28-disponibilidad-bd-levantamiento.md`
- `docs/2026-07-28-contrato-tecnico-mateo.md`
- `docs/2026-07-29-relevo-sesion-28-julio.md` (este documento)

**Archivos modificados:** `automatizacion/actualizar_informe.py`,
`automatizacion/insumos_af.py`, `automatizacion/.env.ejemplo`,
`automatizacion/README.md`, `informe-accion-fiduciaria 1.html`,
`docs/AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md` (recortado),
`Automatizacion GLPI - Plan de cierre.docx`.

**Archivos eliminados:** ver tabla en §4.
