# Tarjetas faltantes del informe de Bancoldex (07/08/2026)

## Contexto

El entregable histórico de Bancoldex es
`Bancoldex/reporte-bancoldex-2026-07-02.pdf`, 11 páginas de junio de 2026. Se
auditó página por página contra el preset del informe web
(`c3, c4, c5, c7, c8, c8m`) para decidir qué tarjetas faltaban. El usuario
eligió el alcance sobre esa auditoría.

| Página del PDF | Estado previo | Decisión |
|---|---|---|
| 1. Portada | Hero | Cubierta |
| 2. Línea base del servicio | `c3`, sin la tabla base/actual | **`c3b` nueva** |
| 3. Control línea base | Sin cubrir | **`c3b`, en el modal** |
| 4. Indicadores | `c4`, 3 de 4 métricas | Fuera de alcance |
| 5–6. Casos por tipo/categoría y motor | `c5` (Aranda) | Cubiertas |
| 7. Ejecución de backups | `c7` | Cubierta |
| 8. Logros | `c8` | Cubierta |
| 9. Acciones y mejoras | `c8m`, 2 de 6 columnas | **Completada** |
| 10. Anexos | `c12` apagada | Sigue apagada |
| 11. Firmas aprobadoras | Sin cubrir | **`c14` nueva** |

Decisión explícita del usuario: **Gestión de backups conserva su tarjeta
independiente (`c7`)** y no pasa a ser una fila del cuadro de indicadores;
`c4` no se toca; `c9` y `c12` siguen apagadas.

## Qué se implementó

### `c3b` — Control de línea base

Tarjeta nueva. Resumen base/actual/diferencia por categoría en la tarjeta
colapsada; detalle por tipo de infraestructura, agrupado por ambiente, en el
modal y en la diapositiva exportable.

Las cifras se declaran en `perfiles/bancoldex.js` (`lineaBase.control`)
porque **no salen del consolidado**: su hoja `Linea Base` trae otra
estructura y suma 220/161, mientras el entregable aprobado dice 237/257. No
existe en el repositorio la fuente que produce las cifras del PDF.

`diferencia` no se declara en ninguna fila: la calcula el motor, y un perfil
que la declare **falla al arrancar** nombrando la clave.

**El id no es `c13`.** Ese ya identifica la diapositiva fija «Gracias»
(`slideCard#c13`). Se usa `c3b`, con el mismo patrón de sufijo que `c8m`.

### `c14` — Firmas aprobadoras

Tarjeta nueva con tres firmantes declarados en el perfil y editables desde la
interfaz. Cada uno firma sobre un `<canvas>` con eventos de puntero nativos
—sin librerías, sin red— y el trazo se guarda como PNG en el almacén del
cliente (`informe:bancoldex:firmas`), reutilizable entre periodos.

La diapositiva exportable lleva un `<img>` con el dataURL, no el canvas: un
`<canvas>` clonado pierde su contenido, y así la firma viaja dentro del HTML
autocontenido.

**Límite declarado:** no es una firma electrónica certificada — sin
certificado, sello de tiempo ni vinculación de identidad. Equivale a firmar
en papel y escanear, que es la práctica actual. No debe presentarse al
cliente como más que eso.

### `c8m` — Acciones y mejoras completa

Responsable, fecha de entrega, observaciones y anillo de avance. Los datos ya
se leían del archivo y se descartaban.

Las columnas van declaradas **por perfil**
(`fuentes.cualitativos.columnas.mitigaciones`) y no en el motor, porque
Acción Fiduciaria entrega este contenido en otro formato — una sola hoja con
`Cliente · Descripción · Dato / evidencia`, sin responsable, fecha ni estado.
Pintarlas siempre habría dejado cuatro columnas vacías en un informe que está
en producción.

### Podado del export (hallazgo del A/B, ver abajo)

`podarClon()` ahora elimina del entregable las tarjetas que el perfil activo
no selecciona.

## Verificación realizada

```bash
python3 -m unittest discover -s automatizacion -p 'test_*.py'
```
→ `Ran 135 tests` · `OK` (126 previas + 9 nuevas de este change).

```bash
python3 automatizacion/verificar_ab.py --autoprueba
```
→ `Autoprueba OK: el arnés distingue 'igual' de 'distinto' en los tres casos probados.`

**A/B de Acción Fiduciaria — criterio de aceptación.** Exports generados en
navegador desde `main` (`cf50713`) y desde esta rama, con los mismos insumos
reales de julio-2026 de `Accion Fiduciaria/` (consolidado, libro de logros,
más GLPI y AlertOps vía `insumos-af.js`, enlazado en ambos árboles para
igualar el estado de entrada):

```bash
python3 automatizacion/verificar_ab.py export-main.html export-rama.html
```
→ **`0 diferencias entre export-main.html y export-rama.html.`**

La primera corrida dio **16 diferencias**; ver «Hallazgos» abajo.

**Autopruebas del store**, ejecutadas en navegador (no simuladas):

- Con Acción Fiduciaria: **31 de 31 PASA**.
- Con Bancoldex y sus cuatro insumos reales de junio-2026 cargados
  (consolidado, Aranda, AlertsList y libro cualitativo; todos los criterios
  de carga en verde): **29 de 31**. Los dos fallos son **preexistentes y
  ajenos a este change** — ver «Pendiente».

**Cifras de `c3b` contra el PDF**, comprobadas con un arnés Node sobre el
perfil real:

```
Producción                       → base 109  actual 111  dif +2
Ambientes de desarrollo y prueba → base 128  actual 146  dif +18
TOTAL GENERAL: base 237 actual 257 dif +20  → COINCIDE con el PDF
```

Los ocho subtotales por categoría también coinciden (Oracle 28→27,
SQL Server 77→77, MySQL 1→3, Aplicaciones 3→4 en producción; 27→46, 97→93,
1→3, 3→4 en desarrollo y prueba).

**Firmas**, probadas de extremo a extremo en navegador: trazo sobre el
lienzo → PNG de 9,1 KB en `localStorage` → persiste tras recarga → aparece
como `<img>` embebido en la diapositiva del clon exportable, con los otros
dos firmantes en línea vacía.

**`c8m`**, con el libro real de junio cargado por el propio input del
informe: 2 registros, cada uno con responsable `SETI-BANCOLDEX`, fecha
`30/06/2026`, observaciones y anillo al `20 %`.

**Podado del export**, comprobado en ambos sentidos sobre el clon real:
- Acción Fiduciaria conserva sus 10 tarjetas y **no** contiene `tk-c3b` ni `tk-c14`.
- Bancoldex conserva sus 8 (`c3, c3b, c4, c5, c7, c8, c8m, c14`), con `s3b`
  de 19 filas y `s14` con 3 bloques de firma.

**Verificación geométrica** (la captura de pantalla no funcionó en este
entorno; se midió el layout en su lugar): sin desbordes ni solapamientos en
`c3b` ni en `c8m`, y sin scroll horizontal del documento.

## Hallazgos

Tres defectos que no se veían leyendo el código; los tres salieron de
ejecutar la verificación.

1. **El export arrastraba las tarjetas de otros clientes.** Primera corrida
   del A/B: 16 diferencias, todas de `c3b` y `c14` dentro del entregable de
   Acción Fiduciaria. El filtro por `seleccionadas` solo existía en
   `exportarPDF()`; `podarClon()` no filtraba nada. Hasta ahora no hacía
   falta, porque todas las tarjetas del DOM eran del preset de AF. Estaban
   `hidden` en pantalla — invisibles al ojo, presentes en el HTML. Corregido
   en `podarClon()`, lo que **arregla además un defecto latente**: una
   tarjeta desactivada desde el selector de composición seguía viajando en el
   entregable.

2. **La firma se guardaba en blanco.** `toDataURL()` devolvía `data:,` (6
   bytes): el buffer del canvas se dimensionaba con
   `getBoundingClientRect()`, pero `renderC14()` lo monta con el detalle
   colapsado, así que medía 0×0. Se pasó a buffer fijo de 600×200 con el CSS
   escalándolo.

3. **El avance se pintaba como «0 %».** La hoja trae `0.2` y un comentario
   del código afirmaba que `pctNum()` resolvía ambas escalas. Es falso:
   `pctNum()` solo parsea. Se aplicó el mismo umbral `1.01` que ya usa
   `actualizarTarjetasDesdeStore()`.

## Archivos tocados

- `informe-accion-fiduciaria 1.html` — entradas `c3b` y `c14` en
  `INVENTARIO_TARJETAS`; sus bloques legado en el DOM; `renderC3b`,
  `renderC14`, `totalesControlBase`, `detalleMitigacion`,
  `montarLienzoFirma`, `leerFirmas`/`guardarFirmas`/`firmantesActivos`,
  `validarClavesPerfil`; podado por preset en `podarClon()`; columnas extra
  en `extraerCualitativosPorHojasPerfil()`; CSS de `.control-base*`,
  `.firma*`, `.avance-anillo` y `.action-item__*`.
- `perfiles/bancoldex.js` — `lineaBase.control`, `firmantes`,
  `fuentes.cualitativos.columnas.mitigaciones`, `c3b` y `c14` en
  `tarjetas.seleccionadas`.
- `automatizacion/test_specs_inventario_tarjetas.py` — 9 pruebas nuevas.
- `openspec/changes/2026-08-07-tarjetas-bancoldex/` — proposal, design,
  tasks y los dos deltas.
- `openspec/specs/inventario-tarjetas/spec.md` — 4 requisitos.
- `openspec/specs/perfil-cliente/spec.md` — 3 requisitos.
- `.claude/launch.json` — configuraciones de servidor para el A/B.
- `TASKS.md`, este documento.

## Pendiente

- **Las autopruebas del store solo son válidas con Acción Fiduciaria
  activa.** Con cualquier otro perfil, dos de las 31 dan falso negativo
  porque tienen el cliente escrito a mano: `Perfil: la cabecera exportable
  adjunta el perfil resuelto al estado` compara contra la cadena
  `'accion-fiduciaria'`, e `Inventario: las diez tarjetas declaradas
  corresponden al DOM legado` exige `length===10`. **Es preexistente**, no lo
  introduce este change, y se comprobó: con AF pasan 31 de 31. Debería
  parametrizarse por `PERFIL`.
- **`.qualitative-summary` desborda 77 px** en el modal de `c8m`. Es una
  clase compartida con Acción Fiduciaria, que está en producción, y el
  contenido añadido por este change va dentro de `.action-item`, no ahí. Se
  deja con decisión del usuario y su propio A/B, mismo criterio que se aplicó
  con `c3` el 07/08.
- **Doble columna `BANCOLDEX`/`SETI` en indicadores.** La hoja `Indicador`
  trae las dos series y el motor lee solo la del cliente. Hay meses donde
  difieren (100 % / 99,7 %; 99,34 % / 100 %) y esa discrepancia hoy no se ve.
- **Origen del 237/257.** Mientras no se sepa qué proceso lo produce, `c3b`
  lleva las cifras declaradas en el perfil.
- **El PDF muestra 50 % en la primera mitigación; el archivo de junio trae
  `0.2` en las dos.** El informe refleja el archivo, que es la fuente. Vale
  confirmarlo con el equipo.
- El change **no está archivado**: no se archiva hasta estar fusionado, y
  `test_specs_adaptadores_fuente.py` todavía resuelve su delta por ruta dura
  (ver `openspec/AGENTS.md`, paso 7 de la skill `nuevo-change`).
