# Diseño — tarjetas faltantes de Bancoldex

## Decisión 0 — colisión de archivos con F7, declarada y no eludida

`CLAUDE.md` §3 y `openspec/AGENTS.md` prohíben que dos changes abiertos
declaren el mismo archivo. Este change declara
`informe-accion-fiduciaria 1.html` y `perfiles/bancoldex.js`, que
`2026-08-05-f7-bancoldex-aranda` también declara y que sigue abierto. **Se
declara la colisión aquí en vez de eludirla en silencio.**

Se verificaron las tres salidas posibles antes de decidir:

1. **Archivar F7 para liberar los archivos.** Descartada, y comprobado
   empíricamente: `test_specs_adaptadores_fuente.py:18` resuelve el delta con
   una ruta dura a `changes/2026-08-05-f7-bancoldex-aranda/`, así que mover
   el change impide importar el módulo y se pierden 32 pruebas (126 → 94).
   Además el paso 7 de la skill `nuevo-change` solo permite archivar cuando
   el change está **fusionado**, y F7 no lo está.
2. **Esperar el merge del PR #18.** Descartada: el PR está `BLOCKED` y la
   protección de rama de `main` impide que el autor apruebe su propio PR
   (`openspec/project.md`, «Flujo de trabajo»). Esperar bloquea el trabajo
   por tiempo indefinido y por una causa ajena al código.
3. **Declarar la colisión y continuar.** Elegida.

El riesgo que la regla previene es la **divergencia paralela** — el caso
`codex/f6-perfil-novaventa` contra `codex/bancoldex-completo`, 31 bloques en
conflicto, documentado en `docs/2026-08-06-divergencia-bancoldex.md`. Aquí no
aplica: este change nace de la rama que **ya contiene F7 completo y
commiteado** (`48ab8da`, en el PR #18), F7 está congelado y nadie trabaja en
paralelo sobre él. Es trabajo secuencial, no paralelo.

Es además el patrón ya establecido en el repositorio: F2, F3, F4, F6 y F7
declaran todas `informe-accion-fiduciaria 1.html` y todas siguen abiertas,
cada una justificándolo por lo mismo. `2026-08-05-f3-inventario-tarjetas`
lo dice literalmente: «F2 quedó registrado en el commit `38530c5` […] F3 es
el siguiente cambio secuencial sobre el HTML».

## Decisión 1b — los identificadores son `c3b` y `c14`, no `c13`/`c14`

El proposal hablaba de `c13`. **`c13` ya está ocupado**: identifica la
diapositiva fija «Gracias» (`slideCard#c13`, con su `s13`). Reutilizarlo
habría hecho que `document.getElementById('c13')` devolviera el nodo
equivocado.

Se usa `c3b`, con el mismo patrón de sufijo que ya emplea `c8m`: acompaña a
`c3` y se monta justo detrás. Para las firmas, `c14`/`s14` estaban libres.
Cubierto por prueba (`test_c13_no_se_reutiliza_para_una_tarjeta`).

## Decisión 1 — las tarjetas nuevas necesitan nodo legado en el DOM

`montarTarjetasDesdeInventario()` recorre `INVENTARIO_TARJETAS`, busca
`document.getElementById(t.legado.tarjeta)` y **retorna si no existe**. No
hay ningún mecanismo para una tarjeta sin nodo previo: `TARJETA_PENDIENTE`
es solo un mapa de textos de estado vacío, y el selector de preset de la
interfaz activa y desactiva tarjetas del inventario, no crea nuevas.

Por lo tanto `c13` y `c14` requieren su bloque HTML legado (tarjeta KPI +
`.slideCard`) escrito en el motor, igual que las doce actuales. Se descartó
generalizar el montaje para crear nodos desde el inventario: es un mecanismo
nuevo que hoy necesita un solo cliente, y el corolario duro de
`openspec/project.md` pide dos clientes con evidencia real antes de aceptar
uno.

**Orden en el informe:** lo fija la posición del nodo en el DOM, no el orden
de `tarjetas.seleccionadas` (que solo filtra). `c13` se inserta a
continuación de `c3`, y `c14` al final, como en el PDF.

## Decisión 2 — `c8m` se extiende por perfil, nunca globalmente

Comprobado contra los dos libros reales:

| | Acción Fiduciaria | Bancoldex |
|---|---|---|
| Hojas | una (`Logros Julio 2026`) | dos (`Logros`, `Mitigación`) |
| Separación | filas-título dentro de la hoja | por hoja |
| Columnas de mitigación | `Cliente · Descripción · Dato / evidencia` | `HALLAZGO · MITIGACIÓN · RESPONSABLE · FECHA ENTREGA · OBSERVACIONES · ESTADO` |

`renderC8m()` pinta `r[0]` y `r[1]` precisamente porque es el mínimo común
denominador. Extenderlo sin condición dejaría cuatro columnas vacías en el
informe de AF y rompería la restricción inviolable #2.

Las columnas adicionales se declaran como **dato** en el perfil, bajo
`fuentes.cualitativos.columnas.mitigaciones`, con los nombres de columna de
la fuente. Un perfil que no las declara —AF, Novaventa— renderiza
exactamente el marcado de hoy, sin ninguna rama nueva en su camino de
ejecución. El `ESTADO` viene como fracción (`0.2`) y se pinta con el mismo
`gauge()` que ya existe en el motor; no se introduce un componente nuevo.

Cumple el principio rector: cambiar esos nombres solo cambia qué celdas se
leen, no cómo se decide algo. Es dato.

## Decisión 3 — firma trazada en el informe, no imagen importada

El usuario pidió poder firmar ahí mismo. Se implementa con `<canvas>` y
eventos de puntero nativos: sin librerías, sin red, coherente con la
restricción inviolable #1.

- **Persistencia:** PNG por `toDataURL()` en el almacén del cliente
  (`PERFIL.almacen.prefijo`), con el mismo mecanismo por cliente que ya usa
  la bolsa de horas (`c9`) y que se corrigió el 06/08 para no compartir
  datos entre clientes.
- **Reutilización entre periodos:** decisión del usuario. Cada persona firma
  una vez y su trazo persiste, con botón de rehacer.
- **Peso:** un trazo típico ronda 10 KB por firma; tres firmas quedan muy por
  debajo de lo que el propio PDF pesa (4,9 MB).
- **Firmantes:** nombre y cargo se declaran en `perfiles/bancoldex.js` como
  valor inicial y son editables desde la interfaz, que persiste la edición.
  Una rotación de personal no exige tocar código.

**Alternativa descartada:** extraer las firmas manuscritas del PDF y
embeberlas. Fija en el artefacto la firma de tres personas concretas,
obliga a editar código en cada rotación y transporta una firma real de
alguien a un archivo que se copia y se reenvía.

**Límite declarado, no oculto:** una firma trazada en un `<canvas>` no es una
firma electrónica certificada — no lleva certificado, sello de tiempo ni
vinculación de identidad, y cualquiera con el HTML abierto puede trazarla.
Es equivalente a la práctica actual (firmar en papel y escanear), y no debe
presentarse ante el cliente como algo más que eso.

## Decisión 4 — `c13` y `c14` son tarjetas opcionales, no dimensiones nuevas

El corolario duro de `openspec/project.md` exige dos clientes con evidencia
real antes de aceptar un mecanismo nuevo. Hoy solo Bancoldex necesita estas
dos tarjetas. No se considera que lo violen: el inventario ya contiene
tarjetas que no todos los perfiles seleccionan (`c9`, `c10`, `c12`), y una
entrada más del inventario que otros perfiles simplemente no listan no es
una dimensión de primera clase ni una estrategia registrada.

El canvas de firma **sí** es un tipo de componente nuevo, y se señala
explícitamente: se acepta porque es una tarjeta opcional del inventario que
ningún otro perfil selecciona, no una capacidad transversal del motor.

## Hallazgos de la implementación (07/08/2026)

Tres defectos que ninguna inspección de código habría dado por sí sola; los
tres salieron de ejecutar la verificación de verdad.

### 1. El export arrastraba las tarjetas de otros clientes — lo detectó el A/B

La primera corrida del A/B dio **16 diferencias**, todas de `c3b` y `c14`
apareciendo dentro del entregable de Acción Fiduciaria. `podarClon()` no
filtraba por preset: el filtro por `seleccionadas` solo existía en
`exportarPDF()`. Hasta ahora no hacía falta, porque todas las tarjetas del
DOM pertenecían al preset de AF.

Se añade el podado por `TARJETAS_SELECCIONADAS` en `podarClon()`. **Corrige
además un defecto latente**: una tarjeta desactivada desde el selector de
composición seguía viajando en el HTML exportado. Tras el arreglo, A/B en 0.

Es el riesgo que la tabla de abajo anticipaba como «el riesgo del change», y
se confirmó. La inspección del DOM en pantalla no lo veía: las tarjetas
estaban `hidden`, que es exactamente lo que engaña al ojo y no al arnés.

### 2. La firma se guardaba en blanco

`toDataURL()` devolvía `data:,` (6 bytes). El buffer del `<canvas>` se
dimensionaba desde `getBoundingClientRect()`, pero `renderC14()` monta el
lienzo con el detalle de la tarjeta colapsado (`display:none`), así que el
rect medía 0×0. Se pasa a un buffer fijo de 600×200 y el CSS lo escala; las
coordenadas del puntero se convierten a coordenadas de buffer. Verificado:
PNG real de 9,1 KB, coherente con los ~10 KB estimados arriba.

### 3. El avance se pintaba como «0 %»

La hoja trae `0.2` y el comentario del código afirmaba que `pctNum()`
resolvía ambas escalas. **Es falso**: `pctNum()` solo parsea, no reescala.
Se aplica el mismo umbral `1.01` que ya usa
`actualizarTarjetasDesdeStore()` con los indicadores.

De paso se separó el rótulo del nombre de columna: el perfil declara
`avance: 'Avance'` como rótulo y la columna se localiza por alias
(`estado`, `avance`, …), para que el rótulo del informe no quede atado al
encabezado del archivo del cliente.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Los nodos nuevos en el DOM alteran el export de Acción Fiduciaria | El export ya filtra por `seleccionadas` y `exportable`. Es **el** riesgo del change y lo decide el A/B con insumos reales, no la inspección |
| `c8m` extendida cambia el informe de AF | Las columnas van por perfil; AF no declara ninguna. Cubierto por A/B y por prueba de conformidad |
| Una firma guardada se reutiliza en un mes que esa persona no aprobó | Aceptado por decisión del usuario. El botón de rehacer permite retirarla |
| Las cifras de `c13` divergen del consolidado real | Ya divergen (220/161 contra 237/257). Queda escrito en la tarjeta que la fuente es el entregable aprobado, no el consolidado |
