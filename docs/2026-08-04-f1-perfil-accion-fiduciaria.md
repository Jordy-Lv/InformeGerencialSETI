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

## Verificación realizada

- Consola sin errores al cargar el archivo completo (con todos los cambios
  aplicados).
- `PERFIL` resuelve con los 4 campos esperados; `REPORTE.cliente ===
  PERFIL.nombre === 'Acción Fiduciaria'`; `fusionarProfundo` es función
  global; `claveAlmacen('posiciones') === 'informe:accion-fiduciaria:posiciones'`.
- `IDB_NAME === 'informeAF'` (idéntico al valor anterior — verificado, no
  asumido).
- Escritura real de bolsa de horas (`window.guardarBolsaHoras(...)`) cayó
  en la clave nueva (`informe:accion-fiduciaria:bolsa:2026-07`), confirmado
  leyendo `localStorage` directamente; se limpió después de la prueba.
- **`esAccionFiduciaria()` y `esClienteAccion()` probadas con 11 casos**
  (mayúsculas, tildes, el alias `"accion"` a secas, cadena vacía, `null`,
  `undefined`, entidad ajena, texto con jerarquía `>`): el resultado de
  cada caso coincide exactamente con lo que la lógica original hardcodeada
  habría dado. No es "no truena" — es comportamiento verificado
  idéntico.

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

## Archivos tocados

- `perfiles/accion-fiduciaria.js` (nuevo)
- `informe-accion-fiduciaria 1.html` (perfil, resolverPerfil,
  fusionarProfundo global, REPORTE.cliente, los 6 filtros de cliente,
  claves de almacén)
