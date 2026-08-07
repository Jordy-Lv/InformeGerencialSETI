# Prueba end-to-end de Bancoldex con insumos reales

**06/08/2026.** Rama `codex/f6-perfil-novaventa`. Carga completa de los
insumos reales de junio-2026, hasta el HTML exportado.

**Resultado: la carga funciona y las cifras cuadran, pero el entregable sale
con contenido de Acción Fiduciaria.** Tres hallazgos, dos de ellos bloqueantes.

---

## 1. Montaje

Los insumos viven en `Bancoldex/` (ignorado por git, verificado: 0 archivos
trackeados). Fuente de verdad independiente: lectura con `openpyxl`, contra la
que se contrastó todo lo que muestra el motor.

El panel del navegador descarta la *query string* en `file://`, así que
`?perfil=bancoldex` no llegaba al motor. Se trabajó sobre una copia idéntica
salvo **una línea añadida** —un `history.replaceState` previo al primer
`<script>`, que fija la query sin tocar el motor—, verificada con `difflib`:
1 línea de diferencia. La copia se eliminó al terminar; `localStorage` quedó
limpio.

Insumos cargados por el input real (`File` + `DataTransfer` + evento
`change`), no llamando a funciones internas:

- `Data consolidada junio_Bancoldex 2026.xlsx` → `fileConsolidado`
- `Logros_Mitigacion_TYA Bencoldex_junio.xlsx` → `fileLogros`

`Casos + tareas BD junio 2026.xlsx` no se cargó: `c5` no está en el preset de
esta rama (el adaptador de Aranda vive en `codex/bancoldex-completo`).

---

## 2. Lo que funciona

Periodo jun-26, perfil `bancoldex` resuelto con 5 tarjetas y 4 dominios.
**Cero errores, cero avisos.** `estadoValidacion().listo === true`.

| Dato | Excel (openpyxl) | Informe | |
|---|---|---|---|
| Indicadores del periodo | 3 filas | 3 | ✓ |
| Disponibilidad jun-26 | `1` / meta `0.9998` | 100 % · Meta 99,98 % | ✓ |
| Gestión del servicio | `1` / meta `0.97` | 100 % · Meta 97 % | ✓ |
| Entregables | `1` / meta `0.99` | 100 % · Meta 99 % | ✓ |
| Backups jun-26 | 11 BD, todas `1` | 100 % · 11/11 | ✓ |
| Meta de backups | `0.95` | **Meta 95 %** | ✓ |
| Logros | 5 filas | 5 logros | ✓ |
| Mitigaciones | 2 filas | 2 registros | ✓ |

La corrección de `metaPerfil()` se confirma end-to-end en sus **dos** rutas:
la tarjeta resumen («Ejecución de backup en junio · Meta 95 %») y el detalle
(«Meta mínima de 95 % · jun-26», «Meta 95 %» en el histórico). Antes de la
corrección ambas habrían dicho «Meta 0,95 %».

La exportación produce `Informe Bancoldex Junio 2026.html` (2,99 MB), con
`__INFORME_CLIENTE__ = true`, el perfil embebido como `bancoldex` y sin el
`<script data-perfil-cliente>` externo.

---

## 3. Hallazgo 1 — el preset del perfil no se aplica en una sesión limpia
### Bloqueante

`aplicarPresetTarjetas()` es lo único que hace `tarjeta.hidden = !activas.has(id)`.
En el arranque solo se llama desde `restaurarPresetTarjetas()`:

```js
function restaurarPresetTarjetas(){
  const guardado=resolverPresetGuardado();      // lee localStorage
  if(guardado) aplicarPresetTarjetas(...);      // ← si no hay nada, no hace nada
}
```

Con `localStorage` vacío —un consultor abriendo el archivo por primera vez—
`resolverPresetGuardado()` devuelve `null` y **el preset declarado en
`PERFIL.tarjetas.seleccionadas` nunca llega al DOM**. Las tarjetas que el
perfil no seleccionó quedan visibles, con el contenido estático de Acción
Fiduciaria, y viajan al export:

| Tarjeta | Texto que sale en el informe de Bancoldex |
|---|---|
| c5 | «CASOS ATENDIDOS · Requiere AlertsList y GLPI del periodo» (Bancoldex usa Aranda) |
| c6 | «DISPONIBILIDAD GLOBAL · **Meta 99,30 %** · requiere el consolidado» |
| c9 | «BOLSA DE HORAS · Dato no disponible» (Bancoldex no tiene bolsa) |
| c11 | «DISPONIBILIDAD POR CI · **Meta 99,30 % por CI**» |
| c12 | «Anexos · **Informe_mensual_Oracle_Accion_Fiduciaria_Junio_2026**» |

La última filtra el nombre de un entregable de otro cliente.

Comprobación de la causa: con `localStorage` vacío las cinco tarjetas tienen
`hidden === false`; tras llamar a mano a
`aplicarPresetTarjetas(PERFIL.tarjetas.seleccionadas)` las cinco pasan a
`hidden === true` y el export vuelve a contener solo `c3, c4, c7, c8, c8m`.

**Por qué no se había visto:** Acción Fiduciaria selecciona las diez
tarjetas, así que ocultar cero es indistinguible de no aplicar el preset. El
mismo patrón que el defecto de las metas: solo se manifiesta en un cliente
que no sea AF. Por lógica afecta también a Novaventa (selecciona 8 de 11),
aunque **no se comprobó** en esta sesión.

---

## 4. Hallazgo 2 — la tabla de indicadores conserva las metas de AF
### Bloqueante

La tarjeta resumen `c4` muestra las metas correctas, porque las escribe
`PERFIL.tarjetas.presentacion`. La **tabla de detalle** no: sus celdas de
rótulo y meta son literales del HTML de AF y nadie las sobreescribe.

| Indicador | Meta mostrada | Meta real (Excel) |
|---|---|---|
| Disponibilidad de la plataforma administrada | **99,30 %** | 99,98 % |
| Gestión del Servicio | **95 %** | 97 % |
| Cumplimiento de entregables | **90 %** | 99 % |

Las tres son exactamente `PERFIL_ACCION_FIDUCIARIA.metas` (`0.9930`, `0.95`,
`0.90`). Los rótulos también son de AF: el Excel de Bancoldex dice
«Cumplimiento tiempos de Atención», el informe dice «Gestión del Servicio».

Esto viaja al HTML exportado (una ocurrencia de `99,30%` en el texto visible
tras descartar nodos ocultos).

**Ya está resuelto en la otra rama.** Es el bloque 12 del análisis de
divergencia: `codex/bancoldex-completo` escribe `cells[0]` y `cells[1]` desde
el Excel; F6 no. La prueba end-to-end confirma que ese bloque debe resolverse
a favor de `bancoldex-completo`, con el A/B de AF como condición —porque en
`main` esas celdas son estáticas y AF depende de que sigan diciendo lo mismo.

---

## 5. Hallazgo 3 — el export arrastra dos `<script src>` externos
### Menor, y preexistente

El HTML exportado conserva en el `<head>`:

```html
<script src="_datos/insumos-af.js?v=…"></script>
<script src="insumos-af.js?v=…"></script>
```

Vienen de `RUTAS_INSUMOS` (precarga de insumos de AF). **No es de F6**: están
igual en `origin/main`. Dos observaciones: un entregable autocontenido no
debería referenciar archivos externos, y el nombre es específico de AF, lo
que no tiene sentido en un informe de Bancoldex. La autoprueba «el entregable
no conserva la dependencia externa» solo poda `script[data-perfil-cliente]`,
así que no los cubre.

---

## 6. Estado y siguiente paso

Nada de esto se corrigió en esta sesión: los dos hallazgos bloqueantes tocan
el motor y merecen su propio delta de spec. El HTML de producción quedó con
los cambios de `metaPerfil()` y nada más; la copia de prueba y `localStorage`
se limpiaron.

Orden sugerido:

1. Hallazgo 1 dentro del change de F6 —es un defecto de F6, y `c12` filtrando
   un nombre de archivo de otro cliente no debería llegar a `main`.
2. Hallazgo 2 en el change de F7, junto con el resto del bloque 12, con el
   A/B de AF como condición de cierre.
3. Hallazgo 3 aparte, cuando se toque la exportación; no bloquea a Bancoldex.
