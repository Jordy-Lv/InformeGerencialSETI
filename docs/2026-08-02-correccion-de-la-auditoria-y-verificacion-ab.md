# Corrección de la auditoría del 02/08 y verificación A/B — 2 de agosto de 2026

**Para:** quien continúe (Claude, en otra sesión, u otra persona).
**Qué es esto:** el registro de la sesión que corrigió los hallazgos
confirmados de
[`2026-08-02-auditoria-insumos-glpi-alertops-disponibilidad.md`](2026-08-02-auditoria-insumos-glpi-alertops-disponibilidad.md)
(F1, F2a, F2b, F3, F4, F10), más una verificación A/B independiente hecha por
el usuario contra `main` con insumos reales, que encontró tres cosas más
sobre el propio trabajo de esta sesión — dos bugs reales y un comentario
desactualizado, también corregidos. Léelo antes de tocar `atribuiblesSeti`,
el gráfico de la diapositiva 5 (`chartCasos`/`DATA_CASOS.labels`), la
clasificación de categorías GLPI, o `extraer_indisponibilidades.py`.

**Commits de esta sesión** (en orden, todos en `origin/main` tras el merge):

1. `1019cb9` — se versiona el documento de la auditoría (primer commit de la rama).
2. `d08bad1` — Fase 1 (F1): `atribuiblesSeti` deja de derivarse por resta.
3. `01fd654` — Fase 2 (F2a+F2b): el gráfico de la diapositiva 5 deja de desincronizarse.
4. `c2884d6` — Fase 3 (F3): categorías GLPI de tres niveles se excluyen como revisión.
5. `98fc059` — Fase 4 (F4+F10): aviso de columna de cruce vacía + comentarios desactualizados.
6. `4d0ad43` — corrige los tres hallazgos de la verificación A/B posterior.

Merge a `main`: fast-forward (`391675d..4d0ad43`), publicado con `git push`.
Rama de trabajo: `fix/auditoria-2026-08-02` (sigue existiendo localmente,
candidata a limpieza — el merge fue ff, no hay historial que perder al
borrarla).

---

## 0. Contexto y decisión de producto

La auditoría de la misma fecha encontró cinco defectos que afectan lo que el
cliente ve, el más grave (F1) capaz de **afirmar algo falso y perjudicial
contra SETI**: con el log de indisponibilidades sin cargar, el informe podía
mostrar «N incidentes atribuibles a SETI» sin ninguna evidencia real detrás.

Antes de tocar código se acordó con el usuario el alcance (F1–F4+F10, dejando
F5–F9+F11 como latentes, documentados sin tocar — ver §5) y una decisión de
producto explícita para F1:

> Un incidente solo cuenta como atribuible a SETI cuando existe un `SI`
> explícito en `DisponibilidadMensual.xlsx` para ese número de caso. Sin
> número de caso, sin coincidencia, sin log cargado o con `NO`/`EN ESTUDIO` →
> **0 atribuibles, chip verde, presentación normal**. No se muestra «pendiente
> de confirmar»: SETI se presume inocente hasta que el consultor lo marque.

Trabajo por fases, una sesión de Sonnet por fase, un commit por fase, en rama
aparte — plan completo guardado en
`/Users/yordypardopajaro/.claude/plans/vamos-a-planificar-como-lucky-grove.md`.

---

## 1. Fase 1 — F1: `atribuiblesSeti` nunca se deriva por resta (`d08bad1`)

**El bug.** `atribuiblesSeti` se calculaba en tres sitios como
`incidentes − excluidosIndisp`. Sin log cargado, `excluidosIndisp` valía `0`
y la resta convertía **todos** los incidentes en atribuibles.

**El fix.** `atribuiblesSeti` se cuenta una sola vez en `cargarGlpi()`,
directamente sobre los `SI` explícitos del log, y se propaga tal cual a
`CARGA.glpi`, `REPORTE` (dominios `glpi`/`casos`), la tarjeta y el modal —
`publicarCasos()`, `actualizarTarjetaCasos()` y `reconciliarIndisponibilidadesGlpi()`
ya no lo derivan por resta. `narrarCasos()` dice «no se identificaron
atribuibles» siempre que `atribuiblesSeti===0`, no solo cuando
`incidentes===0` (antes, con incidentes>0 sin confirmar, no decía nada).

**Verificado:** los tres escenarios reales de la auditoría (GLPI manual sin
`insumos-af.js`, `RUTA_INDISPONIBILIDADES` sin configurar, solo cambiar el
mes en el desplegable) dan 0 atribuibles con chip verde. 3 autopruebas nuevas
en `REPORTE.autopruebas()`.

---

## 2. Fase 2 — F2a+F2b: el gráfico de la diapositiva 5 (`01fd654`)

**F2a — la barra del mes reportado sin etiqueta.** `pintarGraficos()` pasa
`DATA_CASOS.labels` a Chart.js **por referencia**; `cargarIndicadores()` y
`cargarCasos()` la reasignaban (`DATA_CASOS.labels=cols.map(...)`),
desconectando el gráfico. El `push` del mes en curso
(`indiceMesActual()`, llamado desde `cargarGlpi()`/`cargarAlertas()`) nunca
llegaba entonces al eje.

**Fix:** `fijarLabelsCasos()`, única puerta que muta `DATA_CASOS.labels` en
sitio con `splice` (nunca reasigna) y sincroniza el eje explícitamente;
`indiceMesActual()` sincroniza también tras su `push`, por robustez.

**F2b — junio-26 con dos cifras (61 vs 53).** El ledger acumulado solo
reescribía `DATA_CASOS.historico`; la serie corta del gráfico
(`DATA_CASOS.alertas/requerimientos/incidentes`) se quedaba con lo que trajo
la hoja «Casos» del Excel. Fix: `aplicarHistoricoAutomatico()` propaga el
ledger también a la serie corta, para los meses anteriores al periodo
activo — el mes en curso se deja intacto porque lo escriben GLPI/AlertOps en
vivo.

**Nota de proceso:** las 3 autopruebas nuevas de esta fase viven en el bloque
"con el set auditado" de `REPORTE.autopruebas()` (requiere pasarle
`File[]`), y en esta sesión **no llegaron a ejecutarse** — no había fixtures
de GLPI/AlertsList en el repo, así que la lógica se verificó simulándola a
mano en la consola del navegador, no corriendo las aserciones escritas. La
verificación A/B (§4) sí las corrió con insumos reales y confirmó que pasan.
Lección guardada en memoria (`feedback_verificar_autopruebas_reales`): al
añadir pruebas a ese bloque sin fixtures disponibles, decirlo explícitamente
como limitación en vez de reportarlo como «probado».

---

## 3. Fase 3 — F3: categorías GLPI de tres niveles (`c2884d6`)

**El bug.** Tanto `clasificar_caso_glpi()` (Python,
`automatizacion/insumos_af.py`) como `cargarGlpi()` (HTML) tomaban solo el
**último** nivel de la categoría (`split(">")[-1]` / `.pop()`) para detectar
revisiones de alerta, aunque el comentario decía «segundo nivel». Con
categorías de tres niveles («INCIDENTES > Revision Alerta > Jobs Fallidos»),
el último nivel no matchea `^revision` — 17 tickets mal clasificados en un
mes, en el muestreo real de la auditoría.

**Fix, espejado en ambos lados:** revisar **todos** los niveles después del
primero, no solo uno.

- `insumos_af.py`: `any(R_REVISION.search(_norm(p)) for p in categoria.split(">")[1:])`.
- HTML: `esRevisionCategoria()` reemplaza a `nivel2Categoria()`; se subió de
  scope local (dentro de `cargarGlpi()`) a nivel de módulo y se expone en
  `window`, para poder probarla directamente desde `REPORTE.autopruebas()`
  sin duplicar la lógica.

**`automatizacion/test_insumos_af.py`** (nuevo, unittest de stdlib, sin
dependencias nuevas — decisión del usuario): las seis categorías reales del
muestreo de 1 660 tickets, más casos borde. Misma tabla replicada como
prueba pura en `REPORTE.autopruebas()`, para que JS y Python no puedan
divergir en silencio.

---

## 4. Fase 4 — F4+F10 (`98fc059`)

**F4.** `extraer_indisponibilidades.py` no distinguía «hay casos nuevos por
registrar este mes» (normal) de «nadie diligenció NUNCA la columna NUMERO
CASO GLPI» (falla estructural: el cruce no puede emparejar en ningún
periodo). `main()` ahora calcula la señal sobre **todas** las filas del
cliente en el log (no solo las del periodo), la imprime y `verificar()` la
suma como problema propio. Aviso operativo: el código de salida no cambia.

**F10.** Dos comentarios de `actualizar_informe.py`, escritos el 29/07/2026,
decían que el HTML «todavía no lee» lo que aporta indisponibilidades a
`insumos-af.js`. Eso se integró ese mismo día — el HTML sí lo lee, vía
`cargarInsumosAutomaticos()` (`informe-accion-fiduciaria 1.html:2622`).
Corregidos ambos comentarios.

---

## 5. Verificación A/B del usuario (sesión aparte, mismo día)

El usuario montó `main` (antes) y la rama (después) en paralelo, dos
servidores locales, mismos insumos reales (`insumos-af.js`,
`glpi-2026-07.csv`, AlertsList reconstruido del paquete, el consolidado del
repo), y reprodujo cada hallazgo en A/B:

| Hallazgo | `main` (antes) | Rama (después) |
|---|---|---|
| F1 — sin reconciliación | tarjeta: 1 atribuible a SETI, chip rojo | 0 atribuibles, chip verde |
| F2a — etiquetas del gráfico | labels=3 vs datos=4 → barra jul-26 huérfana | labels=4, última etiqueta jul-26 |
| F2b — jun-26 | gráfico 61 vs modal 53 | gráfico 53 = modal 53 |
| F3 — `esRevisionCategoria` | no existía (lógica local, solo el último nivel) | 8/8 categorías del muestreo bien clasificadas, JS y Python alineados |

42 autopruebas en la rama (`main`: 35), con 1 falla — la misma en ambas
ramas: `Backups: el detalle lista todas las instancias de la hoja`
(`modal=0 hoja=undefined`), causada por el consolidado desactualizado a
jun-26 — no relacionada con estos cambios, sin tocar. Python: `py_compile`
OK y 4/4 tests pasan.

Detalle del test de F2b: con el `insumos-af.js` versionado en el repo, el
test es vacuo porque ese fixture ya trae jun-26=61 igual que el Excel; el
usuario tuvo que forzar el ledger a 53 (el valor de `historico_casos.json`)
para que el escenario discriminara — ahí sí, `main` falla y la rama pasa.

F4 y F10 verificados aparte: la señal de columna vacía distingue
correctamente los tres casos (todas vacías → `True`; una diligenciada →
`False`; sin filas → `False`), el mensaje sale y el código de salida sigue
en 0. La referencia `informe-accion-fiduciaria 1.html:2622` de los
comentarios corregidos apunta exacto a `cargarInsumosAutomaticos()`.

### Tres hallazgos adicionales, corregidos en `4d0ad43`

1. **`reconciliarIndisponibilidadesGlpi()` mentía sin log cargado**
   (`:3518`). El guard `RECONCILIACION_INDISPONIBILIDADES&&` que blindó
   `avisar()` en F1 no llegó a esta función: sin log, `excluidos` pasa a
   ser TODOS los incidentes reales, y el registro de control interno
   (`REPORTE.reconciliaciones`, no visible al cliente — solo trazabilidad)
   afirmaba que el equipo había marcado «NO»/«EN ESTUDIO» — falso cuando el
   log ni siquiera se cargó. Mismo error de fondo que F1, un nivel más
   abajo. Fix: la función no publica nada sin reconciliación cargada.
   Autoprueba nueva.

2. **La nota `notaSinReconciliacion` (F1) no se mostraba en ningún lado** —
   vivía en `REPORTE.d('glpi').notas`, que nada renderiza en el HTML. Se le
   preguntó al usuario el alcance del fix: eligió **«solo al consultor»**
   (no tocar la narrativa que lee el cliente final). Se agregó a
   `CARGA.detalles.glpi` — el resumen del panel de carga, visible sin pasar
   por `avisar()`/warn — diferenciando el texto con/sin reconciliación
   igual que ya se hizo en el aviso de `cargarGlpi()`.

3. **Cosmético:** el comentario de `fijarLabelsCasos()` decía que «la
   referencia nunca cambia» justo antes de una línea que reasigna
   `chartCasos.data.labels` — cierto solo para `DATA_CASOS.labels` (la
   fuente), no para la del gráfico. Comentario corregido.

22 autopruebas pasan tras esto (antes 21, +1 por el hallazgo #1).

---

## 6. Merge y push a `main`

`main` no había avanzado desde que se creó la rama (`fix/auditoria-2026-08-02..main`
vacío) ni divergido de `origin/main`, así que el merge fue fast-forward
directo, sin PR ni commit de merge:

```bash
git checkout main
git merge --ff-only fix/auditoria-2026-08-02   # 391675d..4d0ad43
git push origin main
```

`main` local y `origin/main` (GitHub) quedaron en `4d0ad43`.

---

## 7. Estado al cierre de esta sesión

**Resuelto y en producción:** F1, F2a, F2b, F3, F4, F10, más los dos bugs
reales y el comentario que salieron de la verificación A/B.

**Sigue pendiente** (documentado en la auditoría, §3 de ese doc, sin tocar
en esta ronda — ninguno se confirmó con los insumos actuales, a diferencia
de F1–F4 que sí tenían evidencia en vivo):

| # | Severidad | Qué es | Por qué sigue pendiente |
|---|---|---|---|
| F5 | Media | `created_date` de AlertOps sin marcador de zona horaria; si la fuente entrega UTC, alertas de madrugada se asignarían al día/mes anterior en Colombia. | No confirmable con datos: el 1–2/08/2026 la cuenta no tuvo alertas para comparar contra el reloj. Requiere disparar una alerta de prueba a hora conocida, o confirmar la config de zona horaria de la cuenta AlertOps — no es algo resoluble solo desde el código. |
| F6 | Media | `col(head,['id'])` empareja por inclusión de texto, no exacto; una exportación manual de GLPI sin columna `ID` podría enganchar mal con «Entidad» y el cruce de indisponibilidades fallaría en silencio. | No ocurre con el flujo automático actual (`ID` es la columna 0 del CSV). Riesgo preventivo, no correctivo. |
| F7 | Media | `req`/`inc` en `cargarGlpi()` (JS) se calculan con filtros independientes; una categoría que matchee ambos patrones a la vez se contaría dos veces. Python (`clasificar_caso_glpi()`) no tiene ese problema. | Verificado que hoy 0 de 1 660 tickets caen en categoría ambigua. Riesgo latente ante una categoría GLPI nueva. |
| F8 | Baja | Fechas sin hora (`fecha('2026-07-01')`) se interpretan con offset y caen al día anterior — perdería el día 1 de cada mes. | Los CSV actuales (flujo automático) siempre traen hora. Solo afectaría una exportación manual con fechas truncadas. |
| F9 | Baja | El corte de julio quedó repartido entre `Julio/` y `Julio 2/` en OneDrive (`copiar_resguardo()` siempre usa `<Mes>` a secas). | Operativo (organización de carpetas en OneDrive), no un bug de código. |
| F11 | Baja | No hay lint, typecheck ni build para el proyecto en general. | Parcialmente atendido de rebote: `automatizacion/test_insumos_af.py` (nuevo, F3) y varias aserciones nuevas en `REPORTE.autopruebas()` — pero no es un framework de QA general para todo el repo. |

**Nota operativa aparte, sin cambios:** el consolidado del repo llega hasta
jun-26. Para emitir julio hace falta actualizarlo; hasta entonces el
informe (correctamente) bloquea disponibilidad, backups y CI.

**Rama `fix/auditoria-2026-08-02`:** sigue existiendo localmente tras el
merge fast-forward. Puede borrarse sin perder nada (todo su historial ya
está en `main`), pero no es urgente.
