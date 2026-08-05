# F1 — Perfil de Acción Fiduciaria extraído

**Fecha:** 4 de agosto de 2026

## Contexto

Fase F1 del plan de plataforma multicliente: extraer el perfil de
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
9. **Definición de terminado documental**: `openspec/AGENTS.md` ahora exige que
   cada implementación mantenga sincronizados el change, la spec vigente, el
   documento de sesión, el estado del plan maestro, la lista de archivos y la
   descripción remota de la PR. Las verificaciones no ejecutadas deben quedar
   declaradas como pendientes.
10. **Segunda parte (esta sesión): ~30 literales de texto de interfaz
    eliminados**, con dos mecanismos distintos según el caso:
    - **HTML estático nunca antes conectado a JS** (`<title>`, marca del
      topbar, `CLIENTE:` de la portada): se marcan con
      `data-perfil-titulo` / `data-perfil-texto="<clave>"` y una función
      nueva, `hidratarTextosPerfil()`, los sobrescribe con
      `PERFIL.textos.*` al arrancar. El texto que ya estaba en el HTML se
      deja como resguardo visual (nunca se ve, porque la hidratación corre
      antes de pintar), no porque siga siendo la fuente de verdad.
    - **Los ~25 mensajes de validación/aviso, filtros y metadatos**
      (`avisar`, `marcar`, `bloquear`, `filtroCliente`, `pdf.setProperties`,
      nombres de archivo, el aviso de confidencialidad del export, y dos
      arreglos de datos sintéticos dentro de las propias autopruebas) ahora
      interpolan `${REPORTE.cliente}` en vez de repetir el literal.
    - **Hallazgo real en el camino**: los nombres de archivo (`pdf.save`,
      export HTML) usaban `"Accion Fiduciaria"` **sin tilde** — un primer
      intento de usar `${REPORTE.cliente}` (con tilde) ahí habría cambiado
      el nombre del entregable. Se agregó `PERFIL.textos.nombreArchivo`
      como campo separado, sin tilde, con el valor exacto que ya se
      generaba — detectado y corregido antes de seguir, no después.
    - **Deliberadamente sin tocar**: la tabla estática de logros/mitigaciones
      de ejemplo (líneas ~884-889) — sigue siendo la decisión correcta, ver
      más abajo.

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
  y quedó complementada con el A/B real descrito a continuación.
- **A/B real completo de julio de 2026:** se cargaron en Chromium los mismos
  cuatro insumos reales no versionados sobre `main` (`6ee842d`) y la rama
  (`c536853`). En ambos casos quedaron válidos los siete criterios: tres
  indicadores, disponibilidad por CI, backups, GLPI, AlertsList, 5 logros y
  7 mitigaciones; sin errores de carga. Las dos exportaciones temporales se
  compararon con
  `python3 automatizacion/verificar_ab.py /tmp/export-main-julio-2026.html /tmp/export-pr12-julio-2026.html`
  y el resultado fue `0 diferencias` con código de salida 0.
- Los insumos reales no entraron al índice de Git —
  `git status --short --ignored 'Accion Fiduciaria'` desde el directorio de
  trabajo que los contiene; la carpeta sigue fuera de la lista de archivos de
  la PR.
- Diff sin errores de espacios — `git diff --check origin/main...HEAD`.
- La definición de terminado contiene los seis puntos documentales y este
  documento conserva las cinco secciones obligatorias — comprobación estática
  con Python `pathlib` sobre `openspec/AGENTS.md` y este archivo.

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

## Pendiente

El criterio de aceptación de F1 exige **cero literales "Acción Fiduciaria"
fuera de `perfiles/accion-fiduciaria.js` y la tabla de textos**. Con el
punto 10 de arriba, ya no quedan literales pendientes de conocimiento —
`grep -n "Acci[oó]n Fiduciaria\|ACCION FIDUCIARIA\|Accion Fiduciaria"` solo
encuentra: el resguardo visual de HTML estático (hidratado al arrancar), la
tabla de ejemplo deliberadamente intacta (ver abajo), y comentarios de
código (no se renderizan, no cuentan).

- **La tabla estática de logros/mitigaciones de ejemplo (líneas ~884-889)
  sigue intacta, a propósito**: es contenido editable ya cargado (datos
  reales del período — nombres de filesystem, TS_TABLE_DEB, CHEETA — no un
  placeholder genérico), no un literal de lógica de negocio. Cambiarla
  arriesgaría el criterio de "0 cifras distintas" sin beneficio
  arquitectónico real. Si se necesita generalizar, es una decisión de
  producto (¿se resetea la tabla de ejemplo por cliente nuevo?), no una
  omisión técnica.
- **Revisión y fusión de la PR #12:** el criterio técnico de A/B real ya está
  satisfecho; todavía aplica la protección de `main` y la revisión exigida por
  GitHub antes de fusionar.
- **Dorado de F0 para junio de 2026:** esta sesión cerró F1 con datos reales de
  julio de 2026. No se crea ni se declara cerrado el dorado
  `dorados/accion-fiduciaria-2026-06.json`, porque requiere los insumos reales
  exactos de junio definidos por el plan maestro.

## Archivos tocados

- `perfiles/accion-fiduciaria.js` (nuevo)
- `informe-accion-fiduciaria 1.html` (perfil, resolverPerfil,
  fusionarProfundo global, REPORTE.cliente, los 6 filtros de cliente,
  claves de almacén y export autocontenido)
- `openspec/changes/2026-08-04-f1-perfil-cliente/` (proposal, design, tasks
  y delta de spec)
- `openspec/specs/perfil-cliente/spec.md`
- `openspec/specs/README.md`
- `openspec/AGENTS.md` (definición de terminado documental)
- `automatizacion/test_specs_perfil_cliente.py`
- `docs/2026-08-04-f1-perfil-accion-fiduciaria.md`
- `docs/2026-08-04-plan-multicliente.md` (estado de ejecución actualizado)
