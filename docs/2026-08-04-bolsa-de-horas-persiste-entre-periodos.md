# Bolsa de horas: la tarjeta persiste entre periodos sin editar — 4 de agosto de 2026

**Para:** quien continúe (Claude, en otra sesión, u otra persona).
**Qué es esto:** corrección de un bug reportado por el usuario en la tarjeta
«Control bolsa de horas» (diapositiva 9/c9). Léelo antes de tocar
`restaurarBolsaGuardada()`, `firmaBolsa()` o el `localStorage` de bolsa de
horas (`informeAF:bolsa:<AAAA-MM>`) en `informe-accion-fiduciaria 1.html`.

**Rama:** `fix/bolsa-horas-carry-forward-2026-08-04`, desde `main` (sin
relación con `fix/recarga-insumos-2026-08-04`, que sigue en su propio PR
aparte).

**Incluye dos cambios relacionados, mismo PR:** el carry-forward entre
periodos (§1-2) y, agregado después por feedback del usuario probando el fix
en vivo, un botón «Guardar» explícito (§3) — sin él, la única forma de sacar
la tarjeta de «Dato no disponible» la primera vez era tocar un campo y
reescribir el mismo valor, algo nada intuitivo.

---

## 1. El bug (carry-forward)

La bolsa de horas no tiene insumo automático — el consultor la diligencia a
mano en el editor de la tarjeta, y se guarda en `localStorage` bajo una clave
**por periodo** (`informeAF:bolsa:2026-06`, `informeAF:bolsa:2026-07`, …).

Al cambiar de mes en el desplegable, `aplicarPeriodo()` limpia todos los
dominios de `REPORTE` (`DOMINIOS.forEach(d=>REPORTE.limpiar(d))`), incluido
`bolsa`. `restaurarBolsaGuardada()` debía repoblarlo leyendo la clave del mes
nuevo — pero si el consultor **no había editado ese mes todavía** (lo normal:
un cliente sin novedades en su bolsa de horas mes a mes), no existía esa
clave, la función retornaba sin hacer nada, y la tarjeta caía al estado
«sin dato»: mensaje "Dato no disponible: registra manualmente…", el editor
se abría con valores por defecto (100/0/97), y la tarjeta KPI del dashboard
mostraba «Sin datos» — aunque el consultor ya la había diligenciado
correctamente el mes anterior y nada había cambiado.

## 2. El fix (carry-forward)

`restaurarBolsaGuardada()` (línea ~6033 de
`informe-accion-fiduciaria 1.html`) ahora, si no hay una clave exacta para el
periodo activo, busca la **más reciente anterior o igual** a ese periodo
entre todas las claves `informeAF:bolsa:*` guardadas (comparación de strings
`AAAA-MM`, que ordena igual alfabética que cronológicamente) y la usa como
si fuera la del mes actual — sin persistirla bajo la clave nueva
(`persistir:false`, ya existía ese parámetro). Con eso:

- La tarjeta se mantiene **constante** —mismos números, misma «Fecha de
  corte» del último registro real— hasta que alguien la edite de nuevo, en
  vez de mostrar «Dato no disponible» solo porque nadie tocó ese mes en
  particular.
- Al editar un mes concreto, se guarda como registro propio (clave de ese
  mes) sin tocar el registro del que se heredó — cada mes editado sigue
  siendo una fuente independiente; el «heredado» nunca se vuelve permanente
  sin que alguien lo confirme escribiendo algo.
- Un periodo **anterior a cualquier registro existente** (nunca se ha
  diligenciado la bolsa para ningún mes hasta ese punto) sigue mostrando
  «Dato no disponible», correctamente: no hay nada de qué heredar.

No se tocó el modelo de datos (`normalizarBolsa`), la validación
(`validarBolsa`) ni el guardado (`publicarBolsa`) — solo la resolución de
"¿qué muestro si este periodo no tiene su propio registro?".

## 3. Botón «Guardar» explícito (feedback en vivo del usuario)

Probando el fix de carry-forward en el navegador, el usuario notó algo que la
implementación original no resolvía: **la primera vez** que se abre el editor
para un periodo sin ningún registro (ni propio ni heredado — el caso base,
antes de que exista cualquier dato), los campos muestran valores por defecto
razonables (100/0/97, de `normalizarBolsa()`), pero esos valores no cuentan
como «guardados» hasta que el usuario dispara un evento `input` en el
formulario — es decir, hasta que toca un campo y escribe algo, **aunque sea
el mismo número que ya estaba ahí**. No había ninguna pista visual de que
hiciera falta hacer eso, ni un botón que dijera «confirmar esto».

**El fix:** se agregó un botón «Guardar» junto a «Borrar datos»
(`.bolsa-form__save`, en `editorBolsa()`) que lee los valores actuales del
formulario (los que estén, por defecto o editados), valida y publica de
inmediato — sin depender de ningún evento `input` previo. Un solo clic saca
la tarjeta de «Dato no disponible» y la deja con esos valores confirmados,
igual que si el usuario los hubiera escrito a mano. Si los datos no pasan
`validarBolsa()` (p. ej. un campo vacío), no guarda nada y muestra el mismo
panel de errores que ya usaba el autoguardado.

No reemplaza el autoguardado por `input` (`actualizarYGuardarBolsa()`, que
sigue igual para ediciones posteriores) — es un atajo adicional para el caso
en que no hay nada que «editar» de verdad, solo confirmar.

## 4. Alcance declarado por el usuario

> "esta grafica por lo menos para este cliente (este proyecto se va a
> extender para hacer multicliente) se mantenga con la ultima modificacion"

El fix es genérico (no hardcodea nada del cliente actual) y sigue siendo
correcto en un escenario multicliente futuro siempre que la bolsa de horas
de cada cliente use su propio prefijo de `localStorage` — hoy
`BOLSA_STORE_PREFIX='informeAF:bolsa:'` es un único namespace compartido por
todo el archivo HTML (coherente con que hoy el HTML es de un solo cliente).
Si el proyecto pasa a multicliente en el mismo documento o dominio de
`localStorage`, `BOLSA_STORE_PREFIX` necesitará incluir un identificador de
cliente — **no se tocó aquí** porque está fuera del alcance pedido y no hay
todavía un mecanismo de identidad de cliente en el HTML al que enlazarlo.

## 5. Verificado en vivo

Servidor local (`python3 -m http.server`), sin insumos automáticos de por
medio (la bolsa de horas es 100 % manual):

**Carry-forward (§1-2):**

1. Periodo → junio-2026. `hayCifra('bolsa')` en `false` (limpio).
2. `window.guardarBolsaHoras({contratadas:100, consumidasMes:3,
   disponibles:97, …})` → guardado bajo `informeAF:bolsa:2026-06`.
3. Periodo → julio-2026 (sin editar nada). Resultado:
   `REPORTE.cifra('bolsa')` → `true`, `REPORTE.d('bolsa').datos` con los
   valores de junio intactos, tarjeta KPI «3 h consumidas · 97 h disponibles
   de 100 contratadas · Actualizada» (antes: «Dato no disponible · Sin
   datos»), modal de detalle sin el mensaje de «Dato no disponible», «Fecha
   de corte · 30/06/2026» visible (señala que es una cifra heredada, no
   nueva). `localStorage` solo con la clave de junio — julio no quedó
   escrito solo por mirarlo.
4. Edité julio (`consumidasMes:10, disponibles:87`) → quedó guardado bajo su
   propia clave `informeAF:bolsa:2026-07`; la de junio no cambió.
5. Periodo → marzo-2026 (anterior a cualquier registro). `hayCifra('bolsa')`
   → `false`, como se espera: no hay nada de qué heredar.

**Botón «Guardar» (§3), en el navegador real (no solo por consola), sobre la
misma sesión anterior:**

6. Periodo → marzo-2026 (`hayCifra('bolsa')` en `false`, sin heredar de
   nada anterior). Abrí el editor con clic real y hallé el botón morado
   «Guardar» junto a «Borrar datos», con los valores por defecto (100/0/97)
   ya visibles. Clic en «Guardar» **sin tocar ningún campo** → la tarjeta
   pasó de «Dato no disponible» a la tarjeta completa (Consumo del mes,
   Bolsa contratada, Saldo disponible, medidor, resumen narrativo), la
   tarjeta KPI del dashboard pasó de «Sin datos» a «Actualizada», y quedó
   guardado en `localStorage['informeAF:bolsa:2026-03']` con esos mismos
   valores.
7. Periodo → febrero-2026 (otro caso base, sin heredar). Vacié el campo
   «Horas contratadas» y hice clic en «Guardar»: no se publicó nada
   (`hayCifra('bolsa')` siguió en `false`), el formulario mostró
   `has-error` con el mensaje «Ingresa una cantidad válida de horas
   contratadas mayor que cero.», y no quedó nada escrito en `localStorage`
   para ese periodo.

Sintaxis de los 9 bloques `<script>` del HTML verificada con `node --check`
tras cada cambio.
