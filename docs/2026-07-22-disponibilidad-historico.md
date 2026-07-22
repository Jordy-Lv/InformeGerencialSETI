# Tarjeta y modal "Disponibilidad global": meta visible + histórico por motor

**Fecha:** 22 de julio de 2026
**Rama:** `feature/disponibilidad-historico` (pendiente de merge a `main`)
**Origen:** Pedido directo del usuario (fuera de la numeración del acta del 21/07), sobre la tarjeta/modal **"Disponibilidad global"** (`c6`). A diferencia de los cambios 1 y 2, este no se planificó primero con Opus — se fue afinando en vivo, ronda a ronda, con capturas de pantalla como feedback.

## Contexto

El pedido original fue simple: *"quiero que la meta sea visible también en la tarjeta, y en el modal quiero esa misma gráfica de líneas que hemos venido haciendo, agregando los 4 motores de este cliente para ver cómo se ha comportado con el tiempo y la tendencia."* Diseño dejado a criterio propio, con corrección iterativa del usuario.

Lo que terminó pasando fue más profundo que un agregado: el modal tenía un hero de dos columnas (bloque rojo con el resultado del corte + bloque azul oscuro con el comparativo cliente/SETI/estado) heredado de antes de esta sesión. Al meter el histórico por motor debajo, ese hero — pensado para un modal sin gráfica — empezó a competir por espacio y protagonismo con la gráfica, y varias rondas de feedback fueron, en esencia, "achica esto, agranda la gráfica" hasta terminar reemplazando el hero por completo.

## Qué se implementó

### 1. Histórico por motor en el store

`cargarDispoGestion` (hoja "Grafica Dispo y Gestion") solo leía 6 meses para la tabla `#s6 .t-seti`. Se agregó, en paralelo y sin tocar esa tabla, un cálculo de histórico completo con el mismo patrón que `cargarIndicadores`/`cargarCasos`:

```js
const finicioTxt=document.querySelector('[data-k="finicio"]')?.textContent;
const inicioContrato=fecha(finicioTxt)||new Date(2025,8,1);
const colsHistorico=columnasPeriodo(rows[h],mes,anio,999).filter(x=>x.d>=inicioContrato);
resumen.tablas.seti.historico={
  periodos:colsHistorico.map(x=>({clave,etiqueta,mes,anio})),
  motores:filas.map(r=>({nombre, ci, valores:colsHistorico.map(x=>numDisp(r[x.i]))}))
};
```

Solo se calcula para la tabla SETI (`gaugeKey==='gseti'`) — es la única que el modal grafica. Contra el Excel real (`Disponibilidad Consolidado Mayo.xlsx`) esto da 10 periodos (sep-25→jun-26) y 4 motores: **SQL, Mysql, Oracle, Aws**.

### 2. `montarHistorico` extendido (dos capacidades nuevas, reutilizables)

- **`titulo`/`nota` opcionales**: agregan un encabezado (`.hist-encabezado`) dentro de la tarjeta del histórico. Indicadores y casos no lo pasan y no cambian de aspecto — solo hacía falta aquí porque el histórico de disponibilidad es una sección más dentro de un modal que ya tiene su propio título arriba.
- **Series `referencia:true`**: para la meta contractual como línea punteada plana (sin puntos, `borderDash`, `tension:0`), a diferencia de una serie de motor real. Se excluye del cálculo de `resumen` por convención del llamador (ver punto 4), no por lógica interna del componente.

### 3. Meta visible en la tarjeta colapsada

`actualizarTarjetaDisponibilidad` ahora arma el texto leyendo la meta del store (`REPORTE.d('disponibilidad').datos.meta`, no un valor fijo repetido):

```
Cliente 100,0% · SETI 100,0% · Meta 99,3%
```

### 4. Histórico de motores en el modal

`renderC6` construye 4 series de línea (una por motor, paleta `COLORES_MOTORES`) + 1 serie de referencia (meta contractual), y las monta con `montarHistorico({tipo:'line', porDefecto:3, compacto:true, alturaChart:320, titulo:'Evolución histórica por motor', ...})`. El resumen por motor (promedio del rango, mejor/peor mes, meses bajo meta) reutiliza `resumenIndicadores` tal cual, filtrando antes la serie de referencia:

```js
function resumenMotores(periodosVisibles,seriesVisibles){
  return resumenIndicadores(periodosVisibles,seriesVisibles.filter(s=>!s.referencia));
}
```

### 5. El hero de dos columnas, reemplazado por una barra de resumen única

Esto fue el resultado de la ronda de ajustes (detallada abajo), no del plan inicial. El bloque rojo/azul (`.availability-command`) desapareció por completo — todo su CSS (base + variante PDF + media query móvil) se eliminó del archivo por estar 100 % muerto, confirmado con `grep` antes de borrar. En su lugar, `.availability-summary`: una sola barra con un bloque líder oscuro (Disponibilidad SETI, resultado del corte grande) y 4 métricas secundarias en línea (Disponibilidad cliente, Meta contractual, Motores, Estado contractual), separadas por divisores finos — sin perder ningún dato de los que mostraba el hero viejo.

Detalle de diseño: `.availability-summary__stats` usa flexbox (`flex-wrap:wrap`) con `flex:1 1 140px` en cada ítem, no CSS Grid. Con grid (`repeat(auto-fit,minmax(...))`) probado primero, un número de ítems que no llena una fila completa deja hueco vacío al lado del último; con flexbox, el ítem que cae solo en la última fila se estira para llenarla. Ese fue exactamente el defecto reportado ("así se ve feo") que motivó el cambio.

### 6. Autopruebas adaptadas a la nueva estructura

Como el hero viejo desapareció, tres autopruebas que dependían de sus clases (`.availability-result strong`, `.availability-comparison b`, `.availability-comparison__ok`) se reescribieron para leer `.availability-summary` por atributo `data-metric` (`lead`/`cliente`/`meta`/`motores`/`estado`), vía un helper nuevo:

```js
const statValor=(dashId,metrica)=>{
  const el=document.querySelector(`#dashboard-${dashId} [data-metric="${metrica}"]`);
  return el?.querySelector('strong,b')?.textContent.trim()||'';
};
```

## Ronda de ajustes tras revisión visual (mismo día)

El pedido inicial se implementó como un histórico de 4 motores dentro del hero de dos columnas existente (chart en el panel azul oscuro, junto al comparativo cliente/SETI/estado). A partir de ahí, siete correcciones en vivo:

1. **"La gráfica sigue muy pequeña"** → el hero ocupaba casi toda la altura del modal con una gráfica embebida de 6 meses; se sacó la gráfica del hero y se montó como sección propia (`.hist-card`) debajo, con su propio filtro 3M/6M/12M/Todo.
2. **"Que quede en 0 scroll"** → se aplicó el mismo patrón `compacto`/`alturaChart` que casos, comprimiendo paddings del hero hasta lograr diferencia de scroll = 0 px a 1280×800.
3. **"Hazla un poco más grande"** → se subió `alturaChart` (135→170→195), aceptando ~13 px de scroll — mismo criterio que la ronda equivalente en el modal de casos.
4. **"El panel oscuro se ve con espacio muerto, reorganiza y cambia pp por %"** → el panel `.availability-trend` no repartía su contenido verticalmente (todo pegado arriba, hueco abajo). Se cambió a `display:flex;flex-direction:column;justify-content:space-between` (ambos paneles del hero, para que las cifras "Meta/Motores" y "Disponibilidad cliente/SETI/Estado" quedaran ancladas abajo en vez de flotando con un hueco). Las cajas Meta/Motores pasaron de un borde superior suelto (parecía una línea desconectada) a chips con fondo y borde propio. `pp` → `%` en el texto de la meta.
5. **"Indicadores del periodo → Indicadores del servicio"** — pedido puntual, no relacionado con disponibilidad, aplicado en la misma rama por venir en la misma sesión. Cambiado en los 4 lugares donde es texto de cara al cliente (tarjeta colapsada, barra del modal, título y kicker del modal). **No** se tocó el texto interno `'Indicadores del periodo (3 métricas)'` de `criteriosCarga()` — es un checklist de validación para quien carga los insumos, no algo que vea el cliente, y el usuario pidió el cambio "solo en esos lados" (los de las capturas).
6. **"Separemos esa tarjeta de arriba, dale protagonismo a la gráfica"** → se reemplazó el hero completo por una franja compacta reutilizando el componente `stat()` (`stats-grid`, ya usado en línea base/backups/CI) — 5 tarjetas pequeñas en vez de dos paneles grandes. `alturaChart` subió a 320. Esto liberó espacio suficiente para que la gráfica fuera claramente el elemento dominante del modal, a costa de reintroducir ~190 px de scroll.
7. **"Así se ve feo, ten más creatividad"** → el `stats-grid` con 5 ítems y `auto-fit` dejaba el quinto (Estado contractual) solo en una segunda fila, con un hueco vacío grande a su derecha. Se descartó el grid de tarjetas sueltas por la barra única `.availability-summary` descrita en el punto 5 de "Qué se implementó" — con flexbox el problema de hueco no puede repetirse estructuralmente. Esto además bajó el scroll a ~74 px (una barra es más baja que 5 tarjetas con padding propio cada una).

En cada una de estas siete vueltas se repitió el mismo ciclo: editar → servir por HTTP local → inyectar `Disponibilidad Consolidado Mayo.xlsx` real vía `fetch()`+`DataTransfer` → abrir el modal → medir `scrollHeight - clientHeight` del `.dashboard-modal__body` a 1280×800 → capturar pantalla → correr `REPORTE.autopruebas()`.

## Verificación realizada

- **Histórico por motor:** 10 periodos (sep-25→jun-26) para los 4 motores reales del cliente; Oracle muestra una caída real a 98 % en nov-25 (1 de 10 meses bajo meta), confirmando que la gráfica no aplana datos reales.
- **Meta en tarjeta:** `Cliente 100,0% · SETI 100,0% · Meta 99,3%` — confirmado en DOM tras cargar el consolidado real.
- **Filtro 3M/6M/12M/Todo:** funcionando sobre las 4 series + la de referencia; el resumen por motor recalcula correctamente al cambiar de rango.
- **Serie de referencia:** confirmado por inspección de la instancia viva de Chart.js (`chart.data.datasets`) que "Meta contractual" tiene `borderDash:[6,5]` y `pointRadius:0`, distinta de las 4 series de motor.
- **Autopruebas:** las 6 relacionadas con disponibilidad pasan (`Porcentajes: ninguna disponibilidad quedó sin normalizar`, `Disponibilidad: el corte SETI coincide con el último punto de la serie`, `Disponibilidad por CI` ×2, `Disponibilidad global: el promedio cliente sale del Excel, no de la meta`, `Disponibilidad global: el veredicto contractual se calcula`) contra los datos reales, tras adaptarlas a `.availability-summary`. Sin fallas nuevas en el resto del set (las únicas fallas presentes son de dominios sin insumo cargado en esta sesión de prueba — casos/GLPI — no relacionadas con este cambio.
- **CSS muerto:** confirmado con `grep` que ningún elemento del HTML referencia ya `.availability-command`/`.availability-result*`/`.availability-trend*`/`.availability-comparison*` antes de eliminar esas reglas (base, variante PDF y media query móvil).
- **Sintaxis:** los 9 bloques `<script>` pasaron `node --check` después de cada edición.
- **Sin probar en esta ronda:** el caso borde en que la hoja "Grafica Dispo y Gestion" no tiene dato SETI para el periodo (`setiDisponible=false`) — el código lo contempla (bloque líder muestra "—" y nota "Sin registro para {periodo}"), pero no se forzó ese escenario con datos sintéticos como sí se hizo para los casos borde de `narrarCasos` en el cambio anterior.

## Archivos tocados

Un único archivo: [`informe-accion-fiduciaria 1.html`](../informe-accion-fiduciaria%201.html). Sin cambios en dependencias ni otros archivos del repo.

## Pendiente / hallazgos fuera de este cambio

- No se probó explícitamente el escenario "SETI sin dato para el periodo" con datos sintéticos (ver arriba).
- Backups y CI (Disponibilidad por CI) siguen sin su propio histórico con filtro — mencionados como reutilización futura desde el cambio 1, todavía no abordados.
- El resto de ajustes de la sesión del 21/07 no cubiertos (bolsa de horas, motores con nombres reales en otras vistas, etc.) — ver el acta completa.
