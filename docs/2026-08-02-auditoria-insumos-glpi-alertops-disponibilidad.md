# Auditoría de insumos → HTML (GLPI · AlertOps · Consolidado de disponibilidad)

**Fecha:** 2 de agosto de 2026
**Alcance:** verificar que `informe-accion-fiduciaria 1.html` lea, interprete y
presente correctamente los tres insumos (GLPI, AlertsList/AlertOps y el
Consolidado de disponibilidad), más el cruce de indisponibilidades.
**Método:** ejecución real de los extractores contra las APIs de producción,
lectura del Excel real de indisponibilidades, y ejecución del HTML en el
navegador con esos insumos, comparando entrada → transformación → pantalla.
**Estado del repo al terminar:** intacto (`git status` limpio). Todas las
corridas se hicieron sobre una copia en un directorio temporal.

---

## 0. Efecto secundario de la auditoría (para trazabilidad)

La primera corrida de `extraer_alertas.py` escribió en el OneDrive real.
`cargar_env()` (`automatizacion/sonda_glpi.py:421`) ignora una variable de
entorno **vacía** —comportamiento intencional y documentado—, así que el
intento de neutralizar `RUTA_ONEDRIVE=""` desde el entorno no tuvo efecto y
ganó el valor del `.env`.

Resultado: se **creó** `ACCION FIDUCIARIA - 2026/Julio/` con
`alertops-2026-07.csv` (46 alertas). **No se sobrescribió nada** — esa carpeta
no existía; el corte del 29/07 vive en `Julio 2/`. Las corridas siguientes ya
apuntaron a un OneDrive falso en el directorio temporal.

Lección aplicable: para redirigir `RUTA_ONEDRIVE` en pruebas hay que darle un
valor **no vacío** (una ruta desechable), no una cadena vacía.

---

## 1. Ejecución de los scripts (resultado real)

| Comando | Resultado |
|---|---|
| `sonda_alertops.py` | **OK** · HTTP 200, la api-key autentica. 0 alertas de muestra (los últimos días no tuvieron actividad) → no confirmó el esquema con datos |
| `extraer_alertas.py` (jul-2026) | **OK** · 152 alertas de toda la cuenta SETI → **46** de Acción Fiduciaria (3 «No reconocimiento») |
| `extraer_glpi.py` (jul-2026) | **OK** · GLPI reporta 8 casos, se recibieron 8 → 6 requerimientos, 2 incidentes (309522, 311835) |
| `extraer_indisponibilidades.py` (jul-2026) | **OK con observación** · 3 filas de Acción Fiduciaria en todo el log, **0 en 2026-07**, ambos incidentes quedan `SIN_VERIFICAR` |
| `py_compile automatizacion/*.py` | compilan OK |
| `REPORTE.autopruebas()` en el navegador | **17/17 PASA** |
| lint / typecheck / build / tests | **no existen** (sin `package.json`, sin pytest, sin linter instalado) |

Credenciales: `.env` completo y funcional para GLPI y AlertOps. Nada bloqueó la
ejecución; no hizo falta documentar ningún impedimento de acceso.

Comparado con el corte del 29/07/2026: AlertOps 45 → **46** (una alerta más
entre el 29 y el 31 de julio); GLPI idéntico, 8 casos.

---

## 2. Hallazgos confirmados

### F1 · **Crítica** · bug confirmado · integración (GLPI ↔ indisponibilidades)

**«Incidentes atribuibles a SETI» vuelve a asumirse por defecto cuando la
reconciliación no está disponible.**

**Ubicación:** `informe-accion-fiduciaria 1.html:2784-2786`, `:3416-3417`, `:3449`

**Descripción.** El cálculo es
`atribuiblesSeti = incidentes − excluidosIndisp`. Si
`RECONCILIACION_INDISPONIBILIDADES` es `null`, `excluidosIndisp` vale `0` y
**todos** los incidentes cuentan como atribuibles — exactamente la regla que se
corrigió el 29/07/2026.

**Evidencia (mismo archivo GLPI, mismo periodo, en vivo en el navegador):**

```
con reconciliación : "46 alertas · 6 requerimientos · 2 incidentes · 0 atribuibles a SETI"
sin reconciliación : "46 alertas · 6 requerimientos · 2 incidentes · 2 atribuibles a SETI"  ← chip en rojo
```

Y con el desplegable en abr-26 (el archivo GLPI cargado es de julio →
`archivoDeOtroMes`), sin haber leído ni una sola fila de abril:

```
"58 casos | 54 alertas · 3 requerimientos · 1 incidente · 1 atribuible a SETI"
```

Ese `1` sale del ledger histórico, no de ninguna evidencia de atribución.

**Condición de reproducción — tres situaciones reales:**

1. Carga **manual** de GLPI/AlertsList, sin `insumos-af.js` al lado.
2. `RUTA_INDISPONIBILIDADES` sin configurar — documentado hoy como «opcional y
   no bloqueante».
3. Solo **cambiar el mes** en el desplegable del Centro de carga.

**Corrección mínima recomendada.** Que `atribuiblesSeti` sea `null`
(→ «sin confirmar») cuando no hubo cruce, en vez de `nI`:

```js
atribuiblesSeti: RECONCILIACION_INDISPONIBILIDADES
  ? Math.max(0, nI - excluidosIndisp)
  : null
```

y que tarjeta, chip y modal muestren «pendiente de confirmar» en ese caso.

**Prueba automatizada recomendada.** En `REPORTE.autopruebas()`: cargar GLPI con
`RECONCILIACION_INDISPONIBILIDADES = null` y afirmar que ninguna vista muestra
un número de atribuibles mayor que 0.

---

### F2a · **Alta** · bug confirmado · integración

**La barra del mes reportado queda sin etiqueta en el eje X del gráfico de la
diapositiva 5.**

**Ubicación:** `informe-accion-fiduciaria 1.html:2345` (`aplicarPeriodo`),
`:3173-3183` (`cargarCasos`), `:3816-3826` (`pintarGraficos`)

**Descripción.** `pintarGraficos()` pasa `labels: DATA_CASOS.labels` **por
referencia**. `aplicarPeriodo()` y `cargarCasos()` la reemplazan por una copia
(`[...DATA_CASOS.labels]`), rompiendo esa referencia; a partir de ahí
`indiceMesActual()` empuja el mes nuevo a `DATA_CASOS.labels` y el gráfico
nunca se entera.

**Evidencia — HTML autocontenido de OneDrive (sin consolidado), estado limpio:**

```
chartCasos.data.labels        → []          ← 0 etiquetas
chartCasos.data.datasets[0]   → [46]        ← 1 barra dibujada
eje X ticks                   → []
tarjeta                       → "54 casos"
```

**Con el consolidado cargado (flujo real de la interfaz, vía evento `change`):**

```
etiquetas eje X : ["abr-26","may-26","jun-26"]     ← 3
datos alertas   : [54, 30, 61, 46]                 ← 4 barras dibujadas
barra 4 (jul-26, el mes del informe) → sin etiqueta
```

El cliente ve un grupo de barras huérfano justo donde debería decir «jul-26».

**Corrección mínima recomendada.** En `indiceMesActual()`, tras el `push`,
sincronizar `chartCasos.data.labels = [...DATA_CASOS.labels]`; o no romper
nunca la referencia (mutar el arreglo con `splice` en vez de reasignarlo).

**Prueba automatizada recomendada.** Afirmar
`chartCasos.data.labels.length === chartCasos.data.datasets[0].data.length` y
que la última etiqueta sea `etiquetaPeriodo(mes, anio)`.

---

### F2b · **Alta** · bug confirmado · integración

**El mismo informe muestra dos cifras distintas para junio-26.**

**Ubicación:** `informe-accion-fiduciaria 1.html:1765-1799`
(`aplicarHistoricoAutomatico` solo toca `DATA_CASOS.historico`)

**Descripción.** El ledger corrige jun-26 a **53** alertas (commit `391675d`),
pero la serie del gráfico (`DATA_CASOS.alertas`) se llena desde la hoja «Casos»
del Excel, que dice **61**, y nunca se reconcilia con el ledger.

**Evidencia en la misma página:**

```
gráfico diapositiva 5 · jun-26 → 61 alertas
modal «Casos»                  → "Frente a jun-26 (53 casos), el total aumentó un 2 %."
```

**Corrección mínima recomendada.** Que `aplicarHistoricoAutomatico()` también
reescriba `DATA_CASOS.alertas` / `.requerimientos` / `.incidentes` para los
meses que el ledger cubra y que estén presentes en `DATA_CASOS.labels`.

---

### F3 · **Alta** · bug confirmado · GLPI

**Las categorías de tres niveles `INCIDENTES > Revision Alerta > X` NO se
excluyen como revisión de alerta.**

**Ubicación:**
- `automatizacion/insumos_af.py:55` — `categoria.split(">")[-1]`
- `informe-accion-fiduciaria 1.html:2769` — `s.split('>').pop()`

**Descripción.** Ambos toman el **último** nivel, no el **segundo** (que es lo
que declara el comentario del propio código). Con tres niveles, el último es
«Jobs Fallidos» / «Bloqueos» / «Espacios», que no matchea `^revision`.

**Evidencia — muestreo real de GLPI, julio-2026, todas las entidades
(1 660 tickets):**

```
1262  'INCIDENTES > Revision Alerta'                                → revision  OK
   6  'INCIDENTES > Revision Alerta > Alto numero de sesiones...'   → incidente MAL
   5  'INCIDENTES > Revision Alerta > Jobs Fallidos'                → incidente MAL
   3  'INCIDENTES > Revision Alerta > Bloqueos'                     → incidente MAL
   1  'INCIDENTES > Revision Alerta > Espacios'                     → incidente MAL
   1  'INCIDENTES > Revision Alerta > Atraso replica'               → incidente MAL
```

17 tickets mal clasificados en un solo mes. Acción Fiduciaria no tuvo ninguno
en julio (sus 2 incidentes son `INCIDENTES > Reportar Falla / Incidente`), pero
la categoría está viva en esta instancia de GLPI: no es hipotética.

**Impacto.** Infla «incidentes», infla «casos atendidos» y crea candidatos
falsos a «atribuible a SETI».

**Corrección mínima recomendada (en los dos sitios).** Evaluar `^revision`
sobre **cualquier** nivel posterior al primero, no solo el último. En Python:

```python
any(R_REVISION.search(_norm(p)) for p in categoria.split(">")[1:])
```

**Prueba automatizada recomendada.** Tabla de casos con las seis categorías
reales de arriba, afirmando `clasificar_caso_glpi(...) == 'revision'` para las
seis, y su equivalente en JS.

---

### F4 · **Media** · bug de dato confirmado · indisponibilidades

**La columna «NUMERO CASO GLPI» está completamente vacía en el Excel compartido
hoy.**

**Ubicación:** `Echo_Nexus - Célula 3/DisponibilidadMensual.xlsx`, hoja
`Indisponibilidades` (fuera del repo; ruta en `RUTA_INDISPONIBILIDADES`).

**Evidencia:**

```
fila 2 (encabezado): Cliente | NUMERO CASO GLPI | Servicio | Ambiente | Objeto | Atribuible a SETI | ...
fila 4: Accion Fiduciaria | (vacío) | BASE DE DATOS | Producción | CHEETA  | NO | ... 2026-01-20
fila 5: Accion Fiduciaria | (vacío) | BASE DE DATOS | Producción | CHEETA  | NO | ... 2026-02-27
fila 6: Accion Fiduciaria | (vacío) | REDES         | ...       | VPN S2S | NO | ... 2026-03-16
```

Las 3 únicas filas de Acción Fiduciaria del log están sin número de caso. **El
cruce no puede emparejar nunca**, y el caso 309522 que se diligenció el 29/07
(`Atribuible a SETI: NO`) ya no aparece en la hoja.

**Impacto.** El indicador «atribuible a SETI» es estructuralmente 0 e
`indisponibilidades-2026-07.csv` seguirá existiendo como alerta permanente de
«hay algo pendiente por registrar».

El código se comporta bien (`SIN_VERIFICAR`, sin inventar atribución), pero
**el insumo no está aportando información**. Es un asunto operativo, no de
código.

**Corrección mínima recomendada.** Que `extraer_indisponibilidades.py` avise
explícitamente cuando **ninguna** fila del cliente tenga `NUMERO CASO GLPI`
diligenciado — hoy ese caso es indistinguible de «hay casos nuevos sin
registrar».

---

## 3. Hipótesis y riesgos que requieren validación con datos reales

Todo lo de esta sección **no** está confirmado: es riesgo latente identificado
por lectura del código más pruebas de borde.

### F5 · **Media** · riesgo probable · AlertOps

`created_date` llega **sin marcador de zona horaria**
(`"2026-07-31T05:15:55"`, sin `Z` ni offset). `fecha()` en el HTML lo interpreta
como hora **local de Colombia**.

Si AlertOps entrega UTC, toda alerta creada entre 00:00 y 05:00 UTC se asigna al
día anterior en Colombia, y las de fin/principio de mes cruzan de mes.

No se pudo resolver con datos: el 1 y 2 de agosto de 2026 (fin de semana) la
cuenta no tuvo **ninguna** alerta, así que no hubo forma de comparar el
`created_date` más reciente contra el reloj.

Sí se verificó que los bordes del rango son **inclusivos en ambos extremos**
(`createdFrom=2026-07-31&createdTo=2026-07-31` → 5 alertas del día 31), así que
no hay truncamiento del mes.

**Cómo validar.** Disparar una alerta de prueba a una hora conocida y comparar
`created_date` con el reloj local; o confirmar la configuración de zona horaria
de la cuenta en AlertOps.

### F6 · **Media** · riesgo probable · GLPI

`col(head, ['id'])` (`informe-accion-fiduciaria 1.html:1845`, uso en `:2752`)
empareja por **inclusión**. Verificado en vivo:

```
col(['Numero','Entidad','Fecha de apertura'], ['id'])  →  1   ← engancha «Entidad»
```

Con el CSV automático no ocurre (`ID` es la columna 0). Con una exportación
manual sin columna `ID`, `idDeFila()` devolvería `""` y el cruce de
indisponibilidades fallaría en silencio para todos los casos.

**Corrección.** Exigir coincidencia exacta para alias cortos como `id`.

### F7 · **Media** · riesgo probable · GLPI

Divergencia JS ↔ Python en categorías ambiguas. En `cargarGlpi()`
(`:2772-2773`) `req` e `inc` se calculan con filtros **independientes**: una
categoría que matchee `R` e `I` a la vez se cuenta **dos veces**.
`clasificar_caso_glpi()` (Python) devuelve una sola clase (requerimiento gana).
Resultado: el total en vivo divergiría del ledger.

**Verificado que hoy no ocurre:** 0 de 1 660 tickets de julio-2026 caen en una
categoría ambigua. Es riesgo latente ante una categoría nueva del estilo
`INCIDENTES > Solicitud de servicio`.

### F8 · **Baja** · riesgo probable · zona horaria

`fecha('2026-07-01')` (fecha sin hora) devuelve
`Tue Jun 30 2026 19:00:00 GMT-0500`, y `esPeriodo('2026-07-01', 6, 2026)` es
`false`. Los CSV actuales siempre traen hora, pero una exportación manual con
fechas sin hora perdería el día 1 de cada mes.

### F9 · **Baja** · mejora · operación

El corte de julio quedó repartido: los CSV y el HTML del 29/07 están en
`ACCION FIDUCIARIA - 2026/Julio 2/`, y la corrida de hoy creó `.../Julio/`.
`copiar_resguardo()` siempre construye `<Mes>`, así que una carpeta renombrada
por OneDrive parte el archivo del mes en dos ubicaciones.

### F10 · **Baja** · mejora · documentación

`automatizacion/actualizar_informe.py:19-20` y `:104-106` afirman que «el HTML
todavía no lee lo que aporta [indisponibilidades] a `insumos-af.js` (pendiente
de integrar)». Es falso desde el 29/07/2026 — el README y
`cargarInsumosAutomaticos()` (`:2564-2575`) lo contradicen.

### F11 · **Baja** · mejora · QA

No hay lint, typecheck, build ni tests fuera de `REPORTE.autopruebas()`. Las 17
pruebas pasan y **ninguna** habría detectado F1, F2a ni F2b: comparan
`chartCasos.data.datasets[N].data` contra el store, pero nunca `data.labels`, y
nunca ejercitan el caso «sin reconciliación».

---

## 4. Diagrama del flujo, de cada insumo al HTML

```
GLPI REST API ──► extraer_glpi.py ──┬─► salida/glpi-AAAA-MM.csv (utf-8-sig, ';')
 (criteria 80=Entidad,              ├─► RUTA_ONEDRIVE/<Mes>/            [F9]
  15=Fecha apertura,                ├─► historico_casos.json  (req/inc) [F3]
  morethan/lessthan)                └─► insumos-af.js · archivos.glpi (b64+sha256)

AlertOps /api/v2/alerts ─► extraer_alertas.py ─┬─► salida/alertops-AAAA-MM.csv
 (createdFrom/To inclusivos,   filtro regex    ├─► historico_casos.json (alertas)
  paginación por cursor)       "Cliente: xxx"  └─► insumos-af.js · archivos.alertas
                                                                        [F5 tz]
DisponibilidadMensual.xlsx ─► extraer_indisponibilidades.py ─► insumos-af.js
 (hoja Indisponibilidades,      cruce por NUMERO CASO GLPI    · archivos.indisponibilidades
  SharePoint Célula 3)          ↑ columna vacía hoy [F4]

                      ┌─────────────────────────────────────────┐
insumos-af.js  ──────►│  cargarInsumosAutomaticos()  (sha256)   │
(o <script> incrustado)│   ├─ parsearReconciliacionIndisp.      │──[F1]
                      │   ├─ cargarGlpi()   ──► REPORTE 'glpi'  │──[F3][F6][F7]
                      │   ├─ cargarAlertas()──► REPORTE 'alertas'│
                      │   └─ aplicarHistoricoAutomatico(ledger) │──[F2b]
                      └───────────────┬────────────────────────┘
Consolidado .xlsx ──► cargarConsolidado() ──► Indicadores / Disponibilidad /
 (manual, arrastrado)   └─ cargarCasos() ──► DATA_CASOS + chartCasos  [F2a][F2b]
                                              │
                                    publicarCasos() ──► tarjeta c5 · modal · slide 5
```

---

## 5. Campos esperados por el código vs. disponibles en cada fuente

### GLPI (`glpi-2026-07.csv`, 8 filas)

| Campo esperado | ¿Existe? | Observación |
|---|---|---|
| `Entidad` (obligatoria) | Sí | `Entidad Raíz > Colombia > ACCION FIDUCIARIA` |
| `Fecha de apertura` (obligatoria) | Sí | `2026-07-10 15:03:21` — con hora, evita F8 |
| `Categoría` (obligatoria) | Sí | 2 niveles hoy; 3 niveles rompen la exclusión → **F3** |
| `Tiempo para resolver excedido` (obligatoria) | Sí | normalizado a `Sí`/`No` |
| `ID` (cruce indisponibilidades) | Sí | col 0; sin ella engancharía «Entidad» → **F6** |
| `Tipo` (respaldo de Categoría) | Sí | `1`=incidente, `2`=requerimiento (numérico, no textual) |
| `Título`, `Estado`, `Prioridad`, `SLA`, `Última modificación`, `Fecha de resolución` | Sí | no usados en cálculos |

Sin duplicados, sin celdas vacías. Encabezado en fila 0, `utf-8-sig`,
separador `;`.

### AlertOps (`alertops-2026-07.csv`, 46 filas)

| Campo esperado | ¿Existe? | Observación |
|---|---|---|
| `Created Date` (obligatoria) | Sí | ISO sin zona horaria → **F5** |
| `Escalation Policy/Response Play` (obligatoria) | Sí | `Severidad P3-P4` (42), `No reconocimiento` (3) |
| `Alert ID` | Sí | sin duplicados |
| `Topic` / `Message` (filtro de cliente) | Sí | `Cliente: accion_fiduciaria` |
| `ServiceName`, `InitialAssignedDate`, `TimeToAssign`, `TimeToResolve` | **No** | la API no los expone — omitidos a propósito; el HTML no los usa |

### Consolidado (`Insumos/Disponibilidad Consolidado Mayo.xlsx`)

| Hoja | Encabezado | Cobertura | Estado con periodo jul-26 |
|---|---|---|---|
| `Disponibilidad` | fila 3, `Cliente/Tipo Ci/Meta` + meses | 2025-01 → **2026-06** | **invalido** — falta columna jul-26 |
| `Inidcadores` (grafía heredada) | fila 6 | 2025-09 → **2026-06** | `sin_registros_confirmado` |
| `Casos` | fila 25, `CATEGORIA` + meses | 2024-12 → **2026-06** | jun-26 = 61 alertas (ledger dice 53) → **F2b** |
| `Backups` | fila 4, `INSTANCIAS` + meses | hasta 2026-06 | **invalido** |
| `Mitigación` / `Logros` | fila 4 / fila 3 | 3 filas / vacía | ok / vacío |

**El consolidado está desactualizado un mes.** El HTML lo maneja
correctamente: bloquea disponibilidad, backups y CI, y no deja emitir el PDF.
Es el comportamiento deseado, pero significa que el informe de julio no puede
cerrarse hasta que alguien actualice ese Excel.

### Indisponibilidades (`DisponibilidadMensual.xlsx`)

| Columna | ¿Existe? | Datos reales |
|---|---|---|
| `Cliente` (obligatoria) | Sí | 3 filas de Acción Fiduciaria + Bancoldex + EMI |
| `Atribuible a SETI` (obligatoria) | Sí | las 3 de Acción Fiduciaria = `NO` |
| `NUMERO CASO GLPI` (obligatoria, clave del cruce) | Columna sí | **100 % vacía** → **F4** |
| `Servicio`, `Objeto`, `Tipo de Evento`, `Fecha / Hora inicio`, `Motivo` | Sí | |

---

## 6. Entrada → transformación → HTML (datos reales, jul-26)

| Dato | Fuente | Transformación | HTML | ¿Coincide? |
|---|---|---|---|---|
| Alertas | 152 de la cuenta SETI | filtro `Cliente: accion_fiduciaria` → 46 | tarjeta «46 alertas» | Sí |
| Prioridad alta | 3 con `No reconocimiento` | — | «6,52 % (3)» | Sí |
| Casos GLPI | 8 tickets | 6 req + 2 inc | «6 requerimientos · 2 incidentes» | Sí |
| Casos atendidos | 46+6+2 | — | «54 casos» | Sí |
| Atribuibles a SETI | 0 filas con «SI» | `SIN_VERIFICAR` ×2 | «0 atribuibles» *(solo con reconciliación cargada)* | **F1** |
| SLA | 0 vencidos de 8 | 8/8 | 100 % | Sí |
| Histórico (11 meses) | ledger | el ledger manda | modal correcto | Sí |
| Serie del gráfico s5 | ledger + Excel | **sin reconciliar** | jun-26 = 61 vs 53 | **F2b** |
| Etiqueta del mes en el gráfico | — | referencia rota | barra sin etiqueta | **F2a** |

---

## 7. Prioridad para el informe que se entrega al cliente

1. **F1** — el informe puede afirmar «N incidentes atribuibles a SETI» sin
   ninguna evidencia. Es la única que produce una afirmación **falsa y
   perjudicial** sobre SETI frente al cliente.
2. **F2b** — dos cifras contradictorias de junio en la misma página; cualquier
   lector atento lo nota.
3. **F2a** — el mes reportado aparece como una barra sin nombre en la gráfica
   principal.
4. **F3** — infla incidentes en cuanto GLPI use una categoría de 3 niveles para
   este cliente.
5. **F4** — el cruce que da valor al indicador está inerte por falta de
   diligenciamiento.
6. **F5–F8** — latentes, no visibles hoy.

**Nota operativa aparte:** el consolidado del repo llega hasta jun-26. Para
emitir julio hay que actualizarlo; hasta entonces el informe (correctamente)
bloquea disponibilidad, backups y CI.

---

## 8. Comandos ejecutados

```bash
python3 automatizacion/sonda_alertops.py                      # OK, HTTP 200
python3 automatizacion/extraer_alertas.py                     # 152 → 46 AF
python3 automatizacion/extraer_glpi.py                        # 8 casos
python3 automatizacion/extraer_indisponibilidades.py          # 2 SIN_VERIFICAR
python3 automatizacion/extraer_alertas.py --muestra --periodo 2026-07
python3 -m py_compile automatizacion/*.py                     # OK
python3 -m http.server 8791                                   # informe + insumos reales
# en el navegador: REPORTE.autopruebas()                      # 17/17 PASA
# + sondeos ad hoc de bordes de fecha en AlertOps y de categorías GLPI (1 660 tickets)
```

Todos corrieron sobre una copia del proyecto en un directorio temporal; desde
la segunda corrida en adelante, con `RUTA_ONEDRIVE` redirigida a una carpeta
desechable (ver §0).
