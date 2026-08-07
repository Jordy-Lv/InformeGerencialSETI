# Cierre de Bancoldex: atribución a SETI, desborde de c3 y el A/B de AF

**07/08/2026 (tarde-noche), rama `codex/f6-perfil-novaventa`.** Tres
decisiones del usuario, tomadas sobre el análisis de lo que faltaba para dar
Bancoldex por terminado, y la verificación A/B que bloqueaba la fusión.

---

## 1. Punto de partida: qué faltaba de verdad

Revisado contra el código, no contra los documentos: la construcción de
Bancoldex ya estaba completa (114 pruebas OK, e2e con los insumos reales de
junio-2026 cuadrando). Lo pendiente eran decisiones, no implementación.

Los «bloques de divergencia sin resolver» que `TASKS.md` arrastraba desde el
06/08 (3, 7, 8–9 y 17 de
[`2026-08-06-divergencia-bancoldex.md`](2026-08-06-divergencia-bancoldex.md))
se comprobaron uno por uno contra el HTML de esta rama:

| Bloque | Estado real |
|---|---|
| 7 — `insumoProcesado('consolidado')` | Resuelto con el enfoque de F6 (dominios derivados de `TARJETAS_SELECCIONADAS`) |
| 8–9 — contador de insumos obligatorios | Resuelto el 07/08 vía `PERFIL.fuentes` |
| 17 — guards de `cargarConsolidado` | Resuelto: `requiereDisponibilidad`/`requiereBackups` + el guard de `cargarCasos()` |
| 3 — resolución de `?perfil=` | **Descartado**: `cambiarClienteActivo` cubre lo mismo. No se porta |

`codex/bancoldex-completo` no aporta nada más que se vaya a portar.

## 2. Incidentes atribuibles a SETI: 0, por decisión

**Decisión del usuario:** Bancoldex no muestra ningún incidente atribuible a
SETI. El apartado se conserva —mismo título literal, ver
`design.md`— con la cifra en 0 y en estado favorable.

El motivo es de fondo: Aranda no trae el equivalente del log de
indisponibilidades de GLPI, donde un «SI» explícito confirma la atribución.
La cifra que estaba activa (categoría `Incidente` excluyendo monitoreo) era
una aproximación que el informe presentaba al cliente como atribución
confirmada. Con dos incidentes en junio-2026, el entregable afirmaba «2
atribuibles a SETI» sin que nadie lo hubiera verificado.

Se declara como regla del perfil, no como caso especial del motor:

```js
reglas: {atribucionSeti: 'sin-fuente'},
```

`'log-indisponibilidades'` es el default implícito de quien no declara la
clave, así que Acción Fiduciaria y Novaventa no cambian.

**Queda abierto** definir la fuente real de atribución para Bancoldex. La
diferencia con antes es que ahora el informe no afirma nada sin respaldo
mientras tanto.

## 3. Desborde de «Oracle · SQL Server» en c3

Medido en navegador a 1000 px de ancho: el texto ocupa **165 px en una caja
de 79 px** y se monta sobre la columna de Vigencia. La causa es
`#tk-c3 .tarjeta-kpi__mini-val{white-space:nowrap}`, dimensionada para los
valores cortos de Acción Fiduciaria («9», «66», «CN-21012025»).

**Decisión del usuario: corregir solo para Bancoldex.** AF está en
producción y comparte esa clase. Se añadió un mecanismo declarativo: un
perfil puede pedir modificadores BEM para su tarjeta.

```js
c3: {modificadores: ['valores-largos'], items: [...]}
```

El motor los valida contra `/^[a-z0-9-]+$/` y los aplica como
`tarjeta-kpi--<modificador>`. La regla CSS nueva tiene mayor especificidad
(`#tk-c3.tarjeta-kpi--valores-largos`) y no alcanza a ninguna tarjeta que no
lo declare.

Medición después del cambio, mismo ancho: el texto se ajusta en 3 líneas
dentro de su caja (25 px de holgura). A 1512 px —el ancho de trabajo real—
todos los valores caben en una línea (139 px de texto en 171 px de caja) y
ningún otro valor se parte.

## 4. El A/B de Acción Fiduciaria: primero 11 diferencias, luego 0

Es la tarea que bloqueaba la fusión de F6 desde el 05/08. Se corrió con los
insumos reales de `Accion Fiduciaria/` (consolidado, GLPI y AlertOps de
julio-2026, libro de logros), exportando el HTML desde `main` y desde la rama
con el mismo estado de entrada.

### Primera corrida: 11 diferencias, 10 de ellas por estado desigual

Nueve diferencias (histórico de jun-26 en 61 vs 53, notas del dominio
`casos`/`glpi`, `reconciliaciones` 0 vs 1) venían de una sola causa: el
repositorio tiene `insumos-af.js` en la raíz —insumo de desarrollo local,
ignorado por git— y el worktree de `main` no. Con él presente se autocarga el
ledger histórico y la reconciliación de indisponibilidades; sin él, no. El
código de las dos versiones en ese punto es idéntico.

**No se aceptó el A/B parcial:** se igualó el estado de entrada (el mismo
`insumos-af.js` en ambos, `localStorage`/IndexedDB limpios en los dos
orígenes) y se repitió.

### La diferencia número 11 sí era un defecto real

```
.tarjeta-kpi__meta[2]:  A='Ejecución de backup en julio · Meta 99,3%'
                        B='Ejecución de backup en julio · Meta 99%'
```

En `main` esa meta es un literal fijo. Al generalizarla en F6 con
`metaPerfil()`, el texto pasó a formatearse con `pct()`, **que redondea a
entero por defecto**: el informe de Acción Fiduciaria empezaba a decir «Meta
99%» donde el contrato dice 99,3 %. Una cifra de un entregable en
producción, cambiada sin que nadie lo pidiera.

Corregido con `metaTexto()`, que conserva el decimal solo cuando existe
(99,3 → «99,3%»; 95 → «95%», sin el «95,0%» que habría dejado `pct(m,1)`).

Los otros dos usos de `pct(meta)` —«Meta mínima de …» en los modales de
backups y de CI— redondean igual en `main` y en la rama: **no se tocaron**,
porque cambiarlos introduciría una diferencia A/B nueva y no es el alcance de
este change.

### Segunda corrida

```
python3 automatizacion/verificar_ab.py export-main.html export-rama.html
0 diferencias entre export-main.html y export-rama.html.
```

## 5. Verificación

```
python3 -m unittest discover -s automatizacion -p 'test_*.py'
Ran 126 tests — OK          (114 antes; 12 nuevas)

python3 automatizacion/verificar_ab.py --autoprueba
Autoprueba OK (los 3 casos)

verificar_ab.py export-main.html export-rama.html
0 diferencias
```

En navegador, con los insumos reales de junio-2026:

- **Bancoldex** — modal de `c5`: «Incidentes atribuibles a SETI» con **0** y
  panel verde («Sin incidentes atribuibles a SETI»); 72 casos, SLA 98,6 %,
  distribuciones por tipo (33/32/5/2) y motor (52/19/1) intactas.
- **Bancoldex** — `c3` con la clase `tarjeta-kpi--valores-largos` y sin
  invasión de la columna vecina, verificado por medición y por captura.
- **Acción Fiduciaria** — `c3` sin la clase, `font-size:19px` y
  `white-space:nowrap` intactos; `REPORTE.autopruebas()` **31/31 PASA**; sin
  errores de JS en consola (los dos 404 son `insumos-af.js` en su ruta
  alterna, preexistentes).

### Nota sobre el arnés de verificación

El navegador de prueba no deja el archivo exportado en disco, así que el A/B
se hizo con un servidor estático de verificación
(`scratchpad/servidor_ab.py`) que acepta un `POST /_guardar/<nombre>` con el
HTML capturado del `Blob` de `exportarHTML()`. **No es parte del producto:**
el informe se sigue abriendo con doble clic desde `file://` y no hace ninguna
llamada de red. El servidor solo existe mientras corre la verificación.

## 6. Qué queda abierto

- **Definir la fuente de atribución a SETI para Bancoldex.** Ya no bloquea el
  entregable (el informe no afirma nada sin respaldo), pero sigue pendiente.
- **El export arrastra `insumos-af.js`** (hallazgo 3 del e2e del 06/08).
  Menor y preexistente en `main`.
- **Publicar la rama y abrir el PR** de `codex/f6-perfil-novaventa` → `main`,
  que lleva F2–F7. El A/B que lo bloqueaba ya está en 0.
