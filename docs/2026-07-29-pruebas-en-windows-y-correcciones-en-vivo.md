# Pruebas de la automatización en Windows y correcciones en vivo — 29 de julio de 2026

**Para:** quien continúe (Claude, en otra sesión, u otra persona).
**Qué es esto:** el registro de una sesión larga dedicada a poner a andar la
automatización de GLPI/AlertOps/Indisponibilidades en el equipo Windows del
usuario (hasta ahora solo se había probado en el Mac), y a corregir en vivo
varios bugs reales que aparecieron mientras se probaba con datos e incidentes
reales del cliente. Léelo antes de tocar `informe-accion-fiduciaria 1.html`,
`automatizacion/extraer_indisponibilidades.py` o el `.gitignore` — te ahorra
repetir el mismo diagnóstico.

**Commits de esta sesión** (en orden, todos en `origin/main`):

1. `c6dc20b` — fix del crash de consola UTF-8 en Windows.
2. `33824e0` — histórico de casos versionado en git.
3. `4039de1` — primera pasada de documentación.
4. `a96c273` — un incidente no atribuible a SETI sigue siendo un caso atendido.
5. `62ce64c` — corrección de un ejemplo del README que documentaba el bug anterior.
6. `c46d945` — cambiar de mes en el Centro de carga mensual ya no borra el histórico de otros meses.
7. `ae3fb31` — mirar un mes sin datos ya no crea una entrada fantasma en el histórico.
8. `ea78db1` — reintenta si el Excel de indisponibilidades está bloqueado.
9. `e34ad12` — un caso no se asume atribuible a SETI por defecto.

---

## 0. Contexto: de qué partía esta sesión

La sesión anterior (documentada en
[`2026-07-29-relevo-sesion-28-julio.md`](2026-07-29-relevo-sesion-28-julio.md))
había construido y validado todo esto **en el Mac de Yordy**. El usuario pidió
en esta sesión: (1) traer los cambios nuevos del repo, (2) configurarlos y
probarlos en el equipo **Windows**, y, sobre la marcha, según iban apareciendo
bugs reales al usar el sistema con datos de producción, corregirlos.

Nada de lo que sigue es hipotético: cada bug se reprodujo con datos reales
(GLPI, AlertOps, el Excel de Indisponibilidades reales del cliente) antes de
corregirse, y cada fix se verificó en el navegador contra el HTML real.

---

## 1. Configuración inicial en Windows

- Se instaló `openpyxl` (única dependencia externa, para
  `extraer_indisponibilidades.py`/`backfill_historico_casos.py`).
- `automatizacion/.env` ya existía en este equipo (credenciales reales de
  GLPI/AlertOps, `RUTA_ONEDRIVE` ya apuntando a la carpeta real del cliente).
- Se agregó `RUTA_INDISPONIBILIDADES`, apuntando a la copia sincronizada de
  `DisponibilidadMensual.xlsx` (biblioteca «Célula 3», compartida entre
  Acción Fiduciaria, Bancoldex y EMI).
- Se corrió el backfill (`backfill_historico_casos.py`) una vez en este
  equipo — el ledger vivía solo en el Mac; ver §2.

## 2. Bug: crash de consola UTF-8 en Windows (`c6dc20b`)

`cargar_env()` —lo primero que corren los seis scripts— imprime caracteres
como «→» que la consola por defecto de Windows (cp1252, no UTF-8) no sabe
codificar. El `UnicodeEncodeError` ocurría **después** de que GLPI/AlertOps ya
habían extraído los datos correctamente, pero el traceback tumbaba el
proceso: `actualizar_informe.py` reportaba «FALLÓ» para ambas fuentes aunque
el insumo sí se había generado bien. Se corrigió reconfigurando la consola a
UTF-8 dentro de `cargar_env()` — un solo punto para los seis scripts.

## 3. Portabilidad del histórico de casos (`33824e0`, `4039de1`)

`historico_casos.json` vivía solo en `automatizacion/salida/`, ignorada en
bloque junto con los CSV crudos multi-cliente. Al cambiar de Mac a Windows el
ledger se perdió y hubo que rehacer el backfill a mano. Se corrigió el
`.gitignore` (`automatizacion/salida/*` + `!automatizacion/salida/historico_casos.json`)
para versionar **solo** este archivo — son conteos mensuales ya agregados de
Acción Fiduciaria, no datos crudos de otro cliente de SETI. De ahora en
adelante, un `git clone`, un `.zip` del repo o pasarle el proyecto a otra
persona trae este histórico sin rehacer el backfill.

**Aclaración importante, documentada en el README:** esto no es lo mismo que
el HTML autocontenido. Un `.zip` del repo trae el ledger (números crudos) y la
plantilla del informe **sin datos incrustados** (`insumos-af.js` sigue fuera
de git, depende de credenciales y de la corrida del mes). Para entregarle a
alguien un informe que abra ya cargado, sin Python ni credenciales, el
archivo correcto es el HTML autocontenido que `actualizar_informe.py` deja en
`RUTA_ONEDRIVE/<Mes>/`.

## 4. Bug: "incidentes" vs "atribuible a SETI" mezclados (`a96c273`, `62ce64c`)

`cargarGlpi()` restaba del **total de casos atendidos** cualquier incidente
que el cruce con indisponibilidades marcara «no atribuible a SETI». El
usuario lo detectó en vivo: 1 incidente real de julio desapareció del total
(52 → 51) y del desglose («0 incidentes»), aunque el caso sí ocurrió y sí se
atendió. Que no sea culpa de SETI es una pregunta de responsabilidad, no de
si hubo o no un caso.

**Fix:** `DATA_CASOS.incidentes` (y por tanto el total de «casos atendidos»)
es siempre el TOTAL de incidentes reales, sin importar la atribución.
`atribuiblesSeti` es un campo aparte, calculado una sola vez en
`publicarCasos()`, que alimenta únicamente el indicador «Incidentes
atribuibles a SETI». `extraer_indisponibilidades.py` ya no sobrescribe el
total del ledger.

## 5. Bug: cambiar de mes en el Centro de carga mensual corrompía el histórico (`c46d945`, `ae3fb31`)

Dos bugs relacionados, mismo mecanismo: cambiar el desplegable de mes
reprocesa el archivo GLPI/AlertsList ya cargado (`revalidar()` →
`cargarGlpi()`/`cargarAlertas()` de nuevo) contra el periodo recién
seleccionado, aunque ese archivo sea de otro mes.

1. **La tarjeta y el modal mostraban 0** para un mes que el histórico ya
   conocía (el usuario lo vio en vivo: "Mayo 2026 — 0 casos" mientras el
   gráfico, dos párrafos abajo, mostraba 36). Fix: cuando el archivo es de
   otro mes, la cifra "actual" usa lo que el histórico ya sabía de ese mes
   en vez de 0.
2. **Solo mirar un mes sin datos reales (agosto) dejaba una entrada fantasma
   de "0 casos" para siempre** en el histórico — reproducido por el usuario.
   Se agregó `buscarIndiceMesHistorico()` (variante de solo lectura, no
   crea), reservando `indiceMesActualHistorico()` (si no existe, la crea)
   para cuando sí hay un dato real que guardar.

## 6. Bug: crash silencioso si el Excel de indisponibilidades está bloqueado (`ea78db1`)

El usuario reportó dos síntomas que resultaron ser la misma causa: cambiar
"Atribuible a SETI" no se reflejaba, y el aviso de "caso sin registrar" no
viajaba a OneDrive. Causa real: `DisponibilidadMensual.xlsx` vive en una
biblioteca de SharePoint que edita varias personas del equipo; si la
extracción corre justo cuando alguien lo tiene abierto en Excel (o OneDrive
está sincronizando), `openpyxl` revienta con `PermissionError` — un error que
**no** quedaba atrapado por `ErrorIndisponibilidades` en `main()`: tumbaba el
script entero con un traceback crudo, sin llegar nunca a la reconciliación.

**Fix:** `leer_indisponibilidades_con_reintentos()` — 4 intentos con 5s de
espera; si sigue bloqueado, falla con un mensaje claro en vez de un crash.
Verificado en vivo contra el archivo real, bloqueado por más de 30 segundos.

La lógica de "caso sin registrar → archivo standalone → viaja a OneDrive" se
confirmó correcta aparte (con un archivo sintético) — no era un bug distinto,
era la misma causa: el script nunca llegaba a correr esa parte.

### Nota operativa: tiempos de sincronización de OneDrive/SharePoint observados

Empíricos, no una garantía de Microsoft — variaron entre **10 y 100+
segundos** durante esta sesión (probado varias veces, alternando la celda
«Atribuible a SETI» entre SI/NO). Recomendación práctica: esperar 30-45s
después de guardar un cambio en el Excel antes de correr la extracción. Un
archivo **abierto** (no solo editando) bloquea mientras esté abierto — eso no
es cuestión de esperar, hay que cerrarlo.

## 7. Corrección de negocio: un caso no se asume atribuible a SETI por defecto (`e34ad12`)

El hallazgo más importante de la sesión, y el más reciente. Mientras se
probaba el fix de §6, apareció un incidente real y nuevo en GLPI (caso
311835, abierto ese mismo 29/07/2026) sin fila todavía en el Excel de
Indisponibilidades. Con la regla de hasta entonces (**«SI», «EN ESTUDIO» o
sin match cuentan como atribuibles** — la regla original de la sesión del
28-29/07, ver relevo anterior §2), el informe mostraba «2 incidentes, 1
atribuible a SETI»: un caso recién creado, que nadie había revisado
siquiera, ya aparecía "atribuible a SETI" por el solo hecho de no tener fila
registrada.

**El usuario fue explícito y tajante: no se puede atribuir un caso a SETI por
defecto.** Se preguntó también por «EN ESTUDIO» (un caso que sí está
registrado pero el equipo aún no decidió) — misma respuesta: tampoco cuenta
como atribuible hasta que se defina.

**Regla corregida (la vigente ahora):** solo cuenta como atribuible a SETI un
**«SI» explícito** en la columna «Atribuible a SETI» del Excel. «NO»,
«EN ESTUDIO», «SIN_VERIFICAR» (sin fila registrada) o cualquier caso que ni
aparezca en el log de indisponibilidades **no** cuentan como atribuibles —
quedan pendientes hasta que el equipo confirme «SI». Esto no cambia el total
de «casos atendidos» (ver §4): un caso no confirmado sigue siendo un caso
atendido, solo no es "atribuible a SETI" todavía.

Cambio de código: en `cargarGlpi()`, el filtro de exclusión pasó de
`RECONCILIACION_INDISPONIBILIDADES.get(idDeFila(r))==='no'` a
`...!=='si'`. En `extraer_indisponibilidades.py`, el mensaje de «EN ESTUDIO»
ya no dice "pendiente decidir con negocio" — la decisión ya se tomó.

**Validado en vivo, alternando el caso real (309522) varias veces:**
- Con «SI» → 1 atribuible a SETI.
- Con «NO» → 0 atribuibles a SETI.
- El caso nuevo (311835, `SIN_VERIFICAR`) nunca contó como atribuible en
  ningún escenario, mientras no se registre.
- En los tres casos, el total de «casos atendidos» se mantuvo correcto: 53
  (45 alertas + 6 requerimientos + 2 incidentes).

---

## 8. Estado actual real del periodo (julio 2026), al cierre de esta sesión

- GLPI: 8 casos (6 requerimientos, 2 incidentes: 309522 y 311835).
- AlertOps: 45 alertas de Acción Fiduciaria.
- Indisponibilidades: 309522 = NO (confirmado, no atribuible); 311835 =
  SIN_VERIFICAR (caso nuevo del 29/07, aún sin fila en el Excel).
- Total «casos atendidos»: **53**. Atribuibles a SETI: **0** (ninguno de los
  dos incidentes tiene un «SI» confirmado en este momento).
- `historico_casos.json` para 2026-07: `incidentes: 2` (ya refleja el caso
  nuevo).

## 9. Qué falta / pendiente para la próxima sesión

- **El equipo debe registrar el caso 311835** en `DisponibilidadMensual.xlsx`
  (columna `NUMERO CASO GLPI`) y diligenciar si es o no atribuible a SETI. En
  cuanto lo hagan, el número se ajusta solo en la próxima corrida.
- **VS Code abierto en este equipo bloqueó `automatizacion/salida/glpi-2026-07.csv`**
  durante parte de la sesión (probablemente una pestaña con ese archivo
  abierto) — no es un bug del código, pero vale la pena cerrar archivos de
  `salida/` en el editor antes de correr la extracción a mano.
- Sigue pendiente (sin cambios en esta sesión, ver relevo anterior §8):
  cuentas de servicio de solo lectura (hoy `.env` usa credenciales
  personales), dónde corre la tarea programada desatendida, y la
  automatización de disponibilidad Oracle con Mateo.
