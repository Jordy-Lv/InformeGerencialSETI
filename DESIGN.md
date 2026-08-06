# Sistema de diseño del informe

Este documento **describe lo que ya existe** en
`informe-accion-fiduciaria 1.html`. No propone una paleta nueva ni una escala
tipográfica nueva, y no debe usarse para «mejorar» el aspecto por cuenta
propia: cualquier retoque estético es una diferencia visible en el informe de
un cliente en producción, y la restricción #2 lo prohíbe sin un change que lo
justifique.

Cuando encuentres una inconsistencia real, está señalada abajo como deuda.
Documentarla es correcto; resolverla de oficio, no.

---

## 1. El lienzo

El informe es una secuencia de **28 slides de tamaño fijo**, pensadas para
proyectarse y para exportarse a PDF sin reflujo.

```css
--W: 1280px;   /* ancho de slide  */
--H: 720px;    /* alto de slide   */

.slide {
  position: relative;
  width: var(--W); height: var(--H);
  background: #fff; overflow: hidden;
  border-radius: 10px;
  box-shadow: 0 8px 30px rgba(20,30,50,.14);
  font-size: 16px;
}
```

**16:9 exacto y `overflow:hidden`.** No hay diseño responsive y no debe
haberlo: el contenido que se desborda se corta, no se adapta. Si un bloque no
cabe, se reduce el contenido o se reparte en otra slide — nunca se cambia
`--H`.

Todas las medidas parten de `font-size: 16px` en la slide. Es la referencia
para cualquier `em` que escribas dentro.

---

## 2. Color

Dos bloques `:root`. El primero es la marca original; el segundo se añadió al
introducir las tarjetas.

### Marca

| Token | Valor | Uso |
|---|---|---|
| `--rojo` | `#E0352B` | Color de marca SETI. Acentos, títulos, barras |
| `--rojo-tabla` | `#FF0000` | Rojo puro, solo en tablas heredadas |
| `--verde` | `#00B050` | Cumplimiento, estado correcto |
| `--tinta` | `#3d3d3d` | Texto principal. **No `#000`** |
| `--gris` | `#7a7a7a` | Texto secundario, etiquetas, notas |

### Estados y superficies

| Token | Valor | Uso |
|---|---|---|
| `--rojo-suave` / `--rojo-suave-2` | `#FDECEA` / `#FFF5F4` | Fondo de estado en fallo |
| `--verde-suave` | `#F1FAF4` | Fondo de estado correcto |
| `--verde-tinta` | `#176B3A` | Texto sobre `--verde-suave` (contraste) |
| `--ambar` / `--ambar-suave` | `#B0780B` / `#FFF9EB` | Advertencia, valor límite |
| `--azul-marino` | `#1F3864` | Encabezados de sección y hero |

**La semántica del color es información, no decoración.** Verde, ámbar y rojo
significan cumple / al límite / incumple frente a una meta contractual. No
uses `--verde` porque «queda mejor»: alguien va a leer un estado que no es.

Todo estado cromático se acompaña de texto o icono. La lectura no puede
depender solo del color.

> **Deuda:** `--rojo` y `--rojo-tabla` conviven sin regla escrita de cuándo
> aplica cada uno; el segundo solo sobrevive en tablas antiguas. Y los dos
> bloques `:root` deberían ser uno. Ambas cosas se arreglan en el change que
> toque esa zona del CSS, no antes.

---

## 3. Tipografía

| Token | Familia | Dónde |
|---|---|---|
| `--titulo` | `'Handel Gothic BT', 'Questrial', 'Century Gothic', sans-serif` | Títulos de portada y de sección |
| `--sans` | `Arial, 'Helvetica Neue', Helvetica, sans-serif` | Todo el cuerpo |
| `--tabla` | `'Aptos Narrow', Arial, sans-serif` | Tablas densas |

**Solo fuentes del sistema, con cascada de respaldo.** No se cargan fuentes
web: no hay red (restricción #1), y una `@font-face` remota rompería el
informe en el equipo del cliente. `Handel Gothic BT` es la fuente corporativa
y puede no estar instalada — por eso la cascada llega hasta `Century Gothic`
y `sans-serif`.

Corolario: **el texto puede medir distinto en cada máquina.** Es la razón de
`overflow: hidden` en la slide y de que ningún bloque se ajuste al píxel.

---

## 4. Nomenclatura: BEM, sin excepciones

225 clases, 17 bloques, en `bloque__elemento--modificador`:

```text
availability-summary   bolsa-form      case-seti        case-total
ci-overview            ci-radar        ci-range-bar     ci-range-panel
dashboard-modal        hero2           hist-stat        hours-capacity
hours-command          hours-ledger    hours-narrative  stat-card
tarjeta-kpi
```

```css
.tarjeta-kpi            /* bloque      */
.tarjeta-kpi__valor     /* elemento    */
.tarjeta-kpi__chip--ok  /* modificador */
```

Reglas de la casa:

- **Un guion bajo doble de profundidad, nunca dos.** No existe
  `.bloque__elemento__subelemento`; si te hace falta, el elemento es en
  realidad un bloque nuevo.
- **Sin selectores anidados por etiqueta** (`.tarjeta-kpi div span`). El
  clonado del DOM en `exportarHTML()` y la captura de `html2canvas` dependen
  de que el estilo viaje con la clase.
- **Sin utilidades sueltas** tipo `.mt-4`. Este proyecto no tiene Tailwind ni
  lo tendrá; el espaciado vive en el componente.
- Nombres en español o en el término técnico establecido (`hero2`,
  `stat-card`), coherentes con el bloque vecino.

---

## 5. El componente central: `tarjeta-kpi`

Es el patrón que más se repite y el que hay que imitar al añadir uno nuevo.

```text
.tarjeta-kpi
├── __icono
├── __etiqueta        Qué se mide
├── __valor           La cifra grande
├── __meta            "Meta 99,30% · requiere el consolidado"
├── __chip            Estado: --ok | --warn | --err
│   └── __chip-punto
├── __barra           Progreso frente a la meta
├── __resumen         Texto de apoyo (--multi para varias cifras)
├── __mini            Dato secundario en fila
│   ├── __mini-etq   ├── __mini-val   └── __mini-meta
├── __flecha          Tendencia contra el periodo anterior
└── __detalle         Panel desplegable
    └── __detalle-inner
```

```css
--tarjeta-radio: 16px;
--tarjeta-sombra:       0 4px 18px rgba(20,30,50,.08);
--tarjeta-sombra-hover: 0 10px 30px rgba(20,30,50,.14);
```

### Los tres estados que toda tarjeta debe distinguir

Esto no es estética: lo impone la spec de `store-reporte`, que separa **cifra
real**, **cero confirmado** y **fallo de carga**.

| Estado | Se ve así | Significa |
|---|---|---|
| Con dato | Cifra + chip `--ok`/`--warn`/`--err` | El insumo cargó y se calculó |
| Pendiente | «Pendiente de cargar» + `__meta` diciendo qué falta | Nadie ha cargado ese insumo |
| Cero confirmado | `0` con nota explícita | Hay dato y el valor es cero |

**Un cero nunca puede parecerse a un «no cargado».** Confundirlos es
reportarle a un cliente que no hubo incidentes cuando en realidad nadie subió
el archivo.

---

## 6. Restricciones que impone la exportación

`jsPDF` y `html2canvas` están **embebidos y minificados dentro del HTML** —
no son un `<script src>`. Eso mantiene el entregable autocontenido y limita
lo que el CSS puede hacer:

- **Sin Shadow DOM ni Web Components.** `html2canvas` no los captura y
  `exportarHTML()` clona el DOM vivo. Está descartado con nombre en
  [`docs/PATRONES.md`](docs/PATRONES.md).
- **El orden del DOM es el orden visual.** No reordenes con `order` de
  flexbox ni con posicionamiento absoluto: lo capturado es el DOM.
- **Nada crítico en `:hover`, `::before` con contenido, o animación.** Lo que
  solo existe al interactuar no llega al PDF.
- **Sin `position: fixed`** dentro de una slide.
- Los elementos con clase `.ed` son **editables en vivo** por quien arma el
  informe. Su contenido es dato del mes, no plantilla: no lo trates como
  texto fijo.

Al exportar, el estado resuelto viaja dentro de `window.__ESTADO__` y el
documento no puede quedar con un `script src` hacia `perfiles/`. Está
especificado en
[`openspec/specs/perfil-cliente/spec.md`](openspec/specs/perfil-cliente/spec.md).

---

## 7. Los textos del cliente salen del perfil

Ningún nombre de cliente se escribe a mano en el motor. Se hidrata desde
`PERFIL.textos` mediante atributos:

```html
<title data-perfil-titulo>…</title>
<span data-perfil-texto="marcaTopbar">…</span>
<div data-perfil-texto-plantilla="… identifica {cliente} y separa …">…</div>
```

El texto que dejas escrito en el HTML es solo **resguardo visual** para el
instante anterior a que corra el script; se sobrescribe de inmediato. Si
añades un texto que nombra al cliente, va con su atributo y su clave en
`perfiles/<cliente>.js`.

> **Deuda conocida:** las metas (99,30 %, 95 %, 90 %) y los datos de contrato
> (`CN-21012025`, vigencia) **siguen escritos a mano** en el HTML, aunque el
> perfil ya los declara. Cambiar el perfil no los mueve. No lo repliques en
> componentes nuevos: lee del perfil.

---

## 8. Checklist antes de dar por buena una pieza de interfaz

- [ ] ¿Cabe en 1280×720 sin desbordar, con la fuente de respaldo?
- [ ] ¿La clase sigue BEM y cuelga de un bloque existente o de uno nuevo bien
      delimitado?
- [ ] ¿Usa tokens en vez de valores literales de color?
- [ ] ¿Distingue dato, pendiente y cero confirmado?
- [ ] ¿El estado se entiende sin depender del color?
- [ ] ¿Sobrevive a `html2canvas` — sin hover, sin Shadow DOM, sin `order`?
- [ ] ¿Los textos del cliente salen del perfil?
- [ ] ¿Sigue dando **0 diferencias** en `verificar_ab.py` contra `main`?
