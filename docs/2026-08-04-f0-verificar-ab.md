# F0 — Arnés de verificación A/B

**Fecha:** 4 de agosto de 2026

## Contexto

Primera pieza de F0 del plan de plataforma multicliente
(`Plan — Informe Gerencial SETI`). Ninguna fase posterior (F1 en adelante)
puede aceptarse sin "0 diferencias A/B" contra el HTML exportado real de
Acción Fiduciaria — este arnés es lo que hace esa afirmación verificable en
vez de una promesa.

## Qué se implementó

`automatizacion/verificar_ab.py`, solo librería estándar:

- `extraer_estado(html)`: saca `window.__ESTADO__` de un HTML exportado
  (mismo truco que `_PATRON` en `insumos_af.py` para `window.__INSUMOS__`).
- `extraer_texto_visible(html)`: con `html.parser`, el texto normalizado de
  `.tarjeta-kpi__valor`, `.tarjeta-kpi__meta`, `.tarjeta-kpi__chip`,
  `.dashboard-detail`, y celdas `<td>`/`<th>` de cualquier tabla.
- `comparar(html_a, html_b)`: diff estructurado campo a campo de
  `__ESTADO__` (dict/list recursivo, no solo "son distintos") + diff de
  cada lista de texto visible, elemento por elemento.
- CLI: `python3 automatizacion/verificar_ab.py a.html b.html` → 0
  diferencias = exit 0; si no, imprime cada diferencia y sale con 1.
- `--autoprueba`: no compara nada del proyecto real — construye fixtures
  sintéticos en memoria y prueba tres casos (idénticos → 0 diferencias;
  un número cambiado a propósito → se detecta en `__ESTADO__` y en el
  texto visible; un elemento de más en un lado → se detecta). Si el arnés
  mismo se rompe, esto falla con exit 1.

## Por qué el HTML exportado y no el store en frío

`exportarHTML()` clona el DOM vivo e incrusta `window.__ESTADO__` ya
resuelto en la copia — hay texto que solo existe en esa copia. Un diff del
store no vería una regresión de plantilla que no toca el store pero sí
cambia lo que el cliente lee.

## Verificación realizada

1. `python -m py_compile automatizacion/verificar_ab.py` — sin errores.
2. `python automatizacion/verificar_ab.py --autoprueba` — los 3 casos
   pasan (exit 0).
3. **Contra datos reales, fuera del repo** (nunca commiteados): abrí
   `automatizacion/salida/informe-incrustado.html` en un navegador real,
   dejé que autocargara los insumos de GLPI/AlertOps embebidos (54 casos:
   46 alertas, 6 requerimientos, 2 incidentes — julio 2026), y capturé en
   vivo el `window.__ESTADO__` real vía `snapshotEstado()` y el texto real
   de los selectores objetivo vía `querySelectorAll`. Con eso construí dos
   fixtures reales-en-estructura: uno idéntico a sí mismo (dio 0
   diferencias) y uno con `atribuiblesSeti` mutado de 0 a 1 a propósito
   —el arnés lo detectó en dos lugares independientes: el campo de
   `__ESTADO__` y el texto visible de `.tarjeta-kpi__meta`, que también
   habría cambiado. Los fixtures y el script que los construyó se borraron
   después de usarlos (datos reales de Acción Fiduciaria, no van al repo —
   ver "Fixtures — sintéticos, no reales" en el plan).
4. **No pude producir un export real desde el propio botón** de la app:
   `exportarHTML()` está bloqueado por `estadoValidacion().listo`, y el
   informe cargado solo tenía GLPI+AlertOps (disponibilidad, backups,
   logros, mitigaciones y bolsa seguían "Pendiente de cargar" / sin
   insumo). Repliqué a mano la misma lógica de `exportarHTML()`
   (`cloneNode` + `podarClon` + `snapshotEstado()` + `jsonEmbebible`) para
   capturar el estado real sin pasar por el candado de validación —
   ninguno de los números capturados es inventado, pero el archivo
   resultante no es literalmente el que produce el botón.

## Pendiente

- Producir un export real y completo (con Disponibilidad, Backups, Logros,
  Mitigaciones y Bolsa cargados) para tener un golden A/B contra `main` de
  verdad, no solo contra sí mismo. Requiere los archivos mensuales reales
  del cliente — no disponibles en este entorno con el período correcto.
- `dorados/<cliente>-<AAAA-MM>.json` (sección "Verificación" del plan) —
  este arnés compara dos HTML entre sí; falta el mecanismo de golden
  persistente por cliente/período.

## Archivos tocados

- `automatizacion/verificar_ab.py` (nuevo)
