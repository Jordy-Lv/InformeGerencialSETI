# Divergencia de Bancoldex: análisis de la fusión F6 ↔ F7

**06/08/2026.** Investigación previa a fusionar. No se modificó código: todo
lo de aquí sale de inspeccionar las dos ramas y de un merge de prueba en un
worktree desechable, ya eliminado.

---

## 1. El problema

`codex/f6-perfil-novaventa` y `codex/bancoldex-completo` nacen ambas de la
punta de F5 (`db3d368`) y construyeron soporte de Bancoldex por separado,
sin coordinarse.

```
db3d368 (F5) ─┬─ F6 …… registro de clientes por interfaz + Novaventa + Bancoldex parcial
              └─ F7 …… adaptador Aranda + Bancoldex completo (c5, casos)
```

Merge de prueba (`git merge --no-commit`): **5 archivos, 31 bloques.**

| Archivo | Bloques |
|---|---|
| `informe-accion-fiduciaria 1.html` | 20 |
| `automatizacion/test_specs_perfil_cliente.py` | 5 |
| `perfiles/bancoldex.js` | 4 |
| `perfiles/base.js` | 1 |
| `docs/archivo/2026-08-04-plan-multicliente.md` | 1 |

---

## 2. Hallazgo principal: son complementarias, no rivales

El conteo de conflictos exagera el problema. Al abrirlos:

**Los perfiles casi no divergen.** `perfiles/base.js` difiere en 5 líneas
(F6 añade `seleccionable:false`, que F7 no tiene). `perfiles/bancoldex.js`
difiere sobre todo en comentarios y en que **F6 quitó `c5` a propósito**. Su
propia cabecera lo dice:

> …su renderizador (dona por motor, barras por categoría) y el clasificador
> de las cuatro categorías de Aranda […] viven en el motor de
> `codex/bancoldex-completo` y todavía no se portaron a esta rama…

Es decir, el autor de F6 sabía que le faltaba lo de F7 y lo documentó.

**4 de las 5 funciones que ambas ramas crean con el mismo nombre son
idénticas byte a byte**: `cargarDisponibilidadTabla`, `definicionIndicador`,
`extraerCualitativosPorHojasPerfil`, `rotuloIndicador`. Solo diverge
`presentarTarjetaPerfil`, y ahí F7 es superconjunto estricto de F6 (aplica
`configuracion` además de `presentacion` — justo lo que `c5` necesita).

**El resto son funciones disjuntas.** Cada rama aporta lo suyo:

| Aporta F6 (`codex/f6-perfil-novaventa`) | Aporta F7 (`codex/bancoldex-completo`) |
|---|---|
| Administrador de clientes por interfaz (`abrirGestionClientes`, `guardarClienteFormulario`, `leerRegistroClientes`, `eliminarCliente`…) | `adaptarArandaACanonico`, `clasificarTipoAranda` |
| `IDS_PERFILES_SELECCIONABLES` + `seleccionable:false` | `cargarCasosAranda`, `cargarCasosOGlpi` |
| `cargarCapacidad` (tarjeta c10) | `actualizarTarjetaCasosAranda`, `pintarCasosArandaEnSlide` |
| `cargarAlertasDataAlternativa` | `hidratarCentroCargaPerfil`, `hidratarLineaBasePerfil` |
| Perfil Novaventa completo | `fuenteActiva`, `dominiosDeFuente`, `aplicarPeriodo` |

---

## 3. Dos defectos de cifras que la fusión debe resolver

Ninguno de los dos afecta a Acción Fiduciaria en `main` hoy. Los dos serían
visibles en un entregable.

### 3.1 `PERFIL.metas.backups` — unidades inconsistentes en F6

Las metas se declaran en **fracción** (`disponibilidad: 0.9998`,
`backups: 0.95`) y así las leen los dos lados para `disponibilidad`
(`Number(...)*100`). Pero F6 lee `backups` como si fuera porcentaje:

```js
// codex/f6-perfil-novaventa
const metaBackups = metaConfigurada===undefined ? 99.3 : Number(metaConfigurada);
// codex/bancoldex-completo
const metaBackups = metaDeclarada===null ? null
                  : (metaDeclarada===undefined ? 99.3 : Number(metaDeclarada)*100);
```

Ejecutando la aritmética de cada rama sobre los tres perfiles reales:

| Perfil | F6 | F7 |
|---|---|---|
| AF (no declara `backups`) | Meta 99,3 % | Meta 99,3 % |
| Bancoldex (`0.95`) | **Meta 0,95 %** ✗ | Meta 95 % ✓ |
| Novaventa (`null`) | **Meta 0 %** ✗ | sin meta (oculta) ✓ |

Novaventa falla porque `Number(null) === 0` y `Number.isFinite(0) === true`,
así que la rama «sin meta» que F6 escribió expresamente para Novaventa nunca
se ejecuta. Ambos perfiles seleccionan `c7`, así que las dos cifras se ven.
Además, con meta 0,95 % cualquier ejecución de backups «cumple».

AF no declara `backups`, y por eso su A/B pasó en 0 sin delatar nada.

**Resolución:** estructura de F6 (aporta la rama «sin meta» que Novaventa
necesita, ausente en F7) + aritmética de F7 (`===null` explícito y `*100`).
Aplica en los dos sitios: `actualizarTarjetaBackups()` y el radar de c7.

### 3.2 F7 cambia un texto de AF y su A/B nunca se corrió

El commit `4f822c3` («corregir cuarto literal de meta AF en el resumen de
c11») reemplaza en `actualizarTarjetasDesdeStore()`:

```js
- if(m) m.textContent=`${ok} de ${n} cumplen la meta de 99,30%`;
+ if(m) m.textContent=`${ok} de ${n} cumplen la meta de ${pct(ci.datos.meta??99.3, ci.datos.meta!=null?2:1)}`;
```

Su mensaje afirma «AF sin cambios». No es exacto: para AF `ci.datos.meta` es
`null`, así que el formateo cae a **1 decimal**, y `pct(99.3, 1)` produce
`"99,3%"` — no `"99,30%"`. `c11` es `exportable:true` y AF la selecciona, así
que el texto llega al entregable.

Esto encaja con lo que la propia rama documenta en
`docs/2026-08-05-f7-bancoldex-aranda.md`:

> **No ejecutado — pendiente:** cotejo A/B (`automatizacion/verificar_ab.py`)
> con exportaciones reales de `main`.

El contrato del repo (`CLAUDE.md` §6) no admite cerrar así. La corrección es
de una línea: usar 2 decimales también en el caso por defecto.

---

## 4. Resolución propuesta, bloque por bloque (HTML)

`A` = `codex/f6-perfil-novaventa`, `B` = `codex/bancoldex-completo`.

| # | Qué es | Resolución |
|---|---|---|
| 1 | Comentario `F7`/`F7a` + `<script>` de novaventa | Unión (mantener el script de A) |
| 2 | Mapa de perfiles | Unión: entrada `novaventa` de A + guard de embebido por id de B |
| 3 | Resolución de `?perfil=` (solo B) | **Decisión**: A cubre lo mismo con `cambiarClienteActivo`. Conservar uno, no los dos |
| 4 | `presentarTarjetaPerfil` | **B** (superconjunto; `c5` lo necesita) |
| 5 | Comentario de inventario (solo A) | A |
| 6 | `actualizarResumen` | Unión: `guardarPresetClienteActivo` de A + guard `!__INFORME_CLIENTE__` de B |
| 7 | `insumoProcesado('consolidado')` | **Decisión de diseño**: A deriva dominios de `TARJETAS_SELECCIONADAS`; B de `dominiosDeFuente()` |
| 8–9 | Contador de insumos obligatorios | **Decisión**: misma idea, dos implementaciones (`PERFIL.fuentes` vs `fuenteActiva()`) |
| 10 | Comentario de taxonomía | B (más explícito) |
| 11 | Nombres de hoja de indicadores | Equivalentes (ambos pasan por `norm()`) |
| 12 | Render de indicadores | B es superconjunto, **pero escribe `cells[0]`/`cells[1]` que en `main` son estáticos** → verificar con A/B de AF antes de aceptar |
| 13 | `cargarCapacidad` (solo A) | A |
| 14 | Renombre `declaracion`→`declaracionDispo` | Trivial |
| 15 | `actualizarTarjetaBackups` | **A estructura + B aritmética** (ver §3.1) |
| 16 | Comentario de logros/mitigación (solo A) | A |
| 17 | Guards de `cargarConsolidado` | Unión — **el bloque más delicado**: A aporta `capacidad`, B aporta `requiereIndicadores` y los guards de `PERFIL.fuentes.casos/cualitativos` |
| 18 | Detalles del consolidado | Unión (misma lógica que 17) |
| 19 | `lineaBase` | Equivalentes, solo comentario |
| 20 | Radar de backups | **A estructura + B aritmética** (ver §3.1) |

De 20 bloques: **12 son mecánicos** (unión o comentario), **4 tienen un lado
correcto demostrable**, y **4 requieren decisión de diseño** (3, 7, 8–9, 17).

---

## 5. Recomendación

Fusionar **B dentro de A**, no al revés: A está al día con `origin/main`
(0 commits atrás) y lleva F2–F6; B está 6 atrás y solo aporta F7.

Orden sugerido:

1. Cerrar y fusionar F6 primero (`codex/f6-perfil-novaventa` → `main`), con
   su A/B de AF pendiente. Deja una base estable y reduce el problema a una
   sola divergencia.
2. Abrir un change para F7 sobre esa base, con los §3.1 y §3.2 corregidos y
   declarados como delta de spec.
3. Exigir el A/B de AF que F7 nunca corrió, **antes** de fusionar.

Las cuatro decisiones de diseño (bloques 3, 7, 8–9, 17) conviene resolverlas
explícitamente en el `design.md` de ese change, no dentro del `git merge`.

---

## 6. Verificado en esta sesión

```
python3 -m unittest discover -s automatizacion -p 'test_*.py'
Ran 71 tests — OK

python3 automatizacion/verificar_ab.py --autoprueba
Autoprueba OK (los 3 casos)
```

Ambos defectos de §3 se comprobaron ejecutando en Node la aritmética copiada
literalmente de cada rama, no por lectura. **No se ejecutó** el A/B con
exports reales: requiere insumos que no están en el repo.
