# F1 (parte 1) — Perfil de Acción Fiduciaria extraído

**Fecha:** 4 de agosto de 2026

## Contexto

Primer paso de F1 del plan de plataforma multicliente: extraer el perfil de
Acción Fiduciaria a datos, con `resolverPerfil()` + reutilización de
`fusionarProfundo`, y claves de almacén con prefijo — sin cambiar una sola
cifra del informe.

## Reconocimiento (antes de tocar código)

La arquitectura real no era la que se asumía en el plan:

- `REPORTE.cliente` estaba definido (`'Acción Fiduciaria'`) pero **nunca se
  leía** en ningún otro lugar del archivo — dato muerto.
- El filtro real de cliente estaba **duplicado 6 veces**, cada uno con su
  propia comparación normalizada, no centralizado en `REPORTE.cliente`:
  - `clienteDeFila(r).includes('accion fiduciaria')` (AlertsList)
  - `norm(r[cEnt]).includes('accion fiduciaria')` (GLPI)
  - `norm(r[cCliente]).includes('accion fiduciaria')` (tabla de disponibilidad)
  - `function esAccionFiduciaria(v)` (registro mensual de logros/mitigaciones)
  - `function esClienteAccion(v)` (variante de lo anterior, con el alias
    adicional `'accion'` a secas — usada en un segundo formato de carga)
- `fusionarProfundo` estaba **anidada dentro del módulo de gráficos**
  (la usa `montarHistorico`), no en ámbito global — no se podía reutilizar
  desde `resolverPerfil()` sin subirla primero.
- Varios textos de interfaz (`<title>`, la marca del topbar, el
  `CLIENTE:` de la portada) están escritos **directo en HTML estático**:
  ningún JS los actualiza nunca. No es que haya que "reconectarlos" a una
  fuente dinámica — nunca estuvieron conectados.

## Qué se implementó

1. **`perfiles/accion-fiduciaria.js`** (nuevo): perfil como datos puros
   (`id`, `nombre`, `celula`, `contrato`, `metas`, `aliasCliente`,
   `almacen.prefijo`, `textos`). Sin funciones.
2. **`resolverPerfil()` + `fusionarProfundo` global**: `fusionarProfundo` se
   subió de la función de gráficos a ámbito global (no dependía de
   closures externas — confirmado antes de moverla) para que
   `resolverPerfil()` la reutilice en vez de escribir un segundo merge.
   `const PERFIL = resolverPerfil('accion-fiduciaria')` se resuelve de
   forma síncrona al evaluarse el script.
3. **`REPORTE.cliente` ahora deriva de `PERFIL.nombre`** en vez de repetir
   el literal.
4. **Los 6 filtros de cliente centralizados**: los 3 sitios que comparaban
   inline ahora llaman a `esAccionFiduciaria()`; `esAccionFiduciaria()` y
   `esClienteAccion()` ahora comparan contra `PERFIL.nombre` /
   `PERFIL.aliasCliente` en vez de un literal repetido cada una.
5. **`claveAlmacen(sufijo)`** (`` `informe:${PERFIL.id}:${sufijo}` ``) y
   migración de solo lectura para las 3 claves de almacén existentes:
   - `IDB_NAME`: pasa a `PERFIL.almacen.prefijo`, que hoy vale exactamente
     `'informeAF'` — mismo valor, cero riesgo de migración real.
   - `POS_STORE_KEY` (posiciones arrastradas): nueva clave via
     `claveAlmacen('posiciones')`; si no existe, se lee la vieja
     (`'informeAF:posiciones'`) sin reescribirla. `resetPosiciones()`
     borra ambas.
   - `BOLSA_STORE_PREFIX` (bolsa de horas, una clave por periodo): mismo
     patrón — nueva vía `claveAlmacen('bolsa')+':'`, lectura con fallback
     a la vieja, borrado limpia ambas.
6. **Export autocontenido**: `codigoEstadoCliente()` adjunta el perfil resuelto
   a `window.__ESTADO__` inmediatamente después del snapshot comparable,
   `podarClon()` elimina el script vecino marcado con
   `data-perfil-cliente`, y `resolverPerfil()` toma el perfil embebido al
   abrir el entregable. El HTML exportado ya no depende de la carpeta
   `perfiles/`.
7. **Contrato OpenSpec de `perfil-cliente`**: change completo, spec
   desplegada y pruebas que fijan pureza, resolución, export autocontenido,
   compatibilidad de almacenamiento y equivalencia A/B obligatoria.
8. **Autoprueba en frío reparada**: la aserción de estado pendiente apuntaba
   a un selector de portada que no existe. Ahora comprueba los valores de las
   tarjetas, que son la vista real del estado sin insumos; no cambia el DOM ni
   ningún comportamiento visible.

## Verificación realizada

- Sintaxis del perfil válida —
  `node --check perfiles/accion-fiduciaria.js`.
- Sintaxis de todos los bloques internos del HTML válida — extracción de los
   nueve `script` sin `src` y compilación individual con `new Function` en
   Node.js.
- Ejecución real en navegador sin archivos de datos: las 29 autopruebas pasan,
  el clon exportado contiene cero scripts hacia `perfiles/`, vuelve a abrir en
  modo cliente y resuelve `PERFIL.id === 'accion-fiduciaria'` — prueba
  automatizada con Chromium/Playwright sobre el archivo local.
- OpenSpec, perfil puro, resolución, transporte autocontenido y fallbacks de
  almacenamiento conformes —
  `python3 -m unittest automatizacion.test_specs_perfil_cliente -v`.
- Suite completa de automatización sin regresiones —
  `python3 -m unittest discover -s automatizacion -p 'test_*.py' -v`.
- El arnés A/B detecta la regresión sintética deliberada y acepta el caso
  idéntico — `python3 automatizacion/verificar_ab.py --autoprueba`.
- Dos exports en frío, generados en Chromium desde `origin/main` y la rama y
  enviados en memoria a `automatizacion.verificar_ab.comparar`, producen cero
  diferencias. Esta prueba confirma la compatibilidad estructural del export,
  pero no reemplaza el A/B con insumos reales completos.
- Diff sin errores de espacios — `git diff --check origin/main...HEAD`.

La comparación A/B real no se declara como realizada: falta el par de
exportaciones completas con los mismos insumos reales.

## Un error cometido y corregido en el camino

Al insertar el `<script src="perfiles/accion-fiduciaria.js">`, el primer
intento de ubicar el punto de inserción usó como ancla un fragmento de
texto que resultó estar *dentro* del código minificado de una librería
vendor (html2canvas) — el `Edit` se aplicó ahí por error, insertando texto
en medio del minificado. Se detectó de inmediato (antes de continuar) y se
revirtió con un segundo `Edit` que restauró el texto original exacto.
Verificado con `git diff` que no quedó rastro. Se documenta aquí porque es
exactamente el tipo de error que un cambio de esta envergadura, sobre un
archivo de producción, puede introducir — y la razón por la que cada paso
de este documento se verificó por separado en vez de aplicar todos los
cambios y revisar al final.

## Pendiente (no es "F1 completo" todavía)

El criterio de aceptación de F1 exige **cero literales "Acción Fiduciaria"
fuera de `perfiles/accion-fiduciaria.js` y la tabla de textos**. Lo que
falta, sin tocar todavía:

- `<title>` (línea ~15), marca del topbar (línea ~527), `CLIENTE:` de la
  portada (`.hero2__client`, línea ~605) — HTML estático, nunca antes
  actualizado por JS; requiere una función de hidratación nueva, no solo
  mover una referencia.
- ~15 mensajes de validación/aviso (`avisar`, `marcar`, `bloquear`) que
  interpolan "Acción Fiduciaria" como texto plano en vez de
  `${REPORTE.cliente}`.
- Metadatos y nombres de archivo del PDF/HTML exportado (`pdf.save(...)`,
  `pdf.setProperties(...)`, el nombre del export HTML).
- El aviso de confidencialidad embebido en el HTML exportado.
- La tabla estática de logros/mitigaciones de ejemplo (líneas ~938-943) —
  **decisión deliberada de NO tocarla**: es contenido editable ya cargado
  (datos reales del período, no un placeholder genérico), no un literal de
  lógica de negocio. Cambiarla arriesgaría el criterio de "0 cifras
  distintas" sin beneficio arquitectónico real.
- **`automatizacion/verificar_ab.py` contra un export real de `main` no se
  corrió todavía** — sigue bloqueado por lo mismo que en F0 (el export
  real exige todos los dominios cargados; no hay archivos reales de AF a
  mano con el período correcto). La verificación de este PR es funcional
  (comportamiento idéntico probado caso por caso), no un diff A/B de
  archivo completo.
- La PR no debe fusionarse hasta que esa comparación real informe cero
  diferencias.

## Archivos tocados

- `perfiles/accion-fiduciaria.js` (nuevo)
- `informe-accion-fiduciaria 1.html` (perfil, resolverPerfil,
  fusionarProfundo global, REPORTE.cliente, los 6 filtros de cliente,
  claves de almacén y export autocontenido)
- `openspec/changes/2026-08-04-f1-perfil-cliente/` (proposal, design, tasks
  y delta de spec)
- `openspec/specs/perfil-cliente/spec.md`
- `openspec/specs/README.md`
- `automatizacion/test_specs_perfil_cliente.py`
- `docs/2026-08-04-f1-perfil-accion-fiduciaria.md`
- `docs/2026-08-04-plan-multicliente.md` (estado de ejecución actualizado)
