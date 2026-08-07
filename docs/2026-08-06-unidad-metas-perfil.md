# Unidad canónica de `PERFIL.metas`

**06/08/2026.** Corrección dentro del change abierto
`2026-08-05-f6-perfil-novaventa`. Sale del análisis de la divergencia de
Bancoldex — ver [`2026-08-06-divergencia-bancoldex.md`](2026-08-06-divergencia-bancoldex.md) §3.1.

---

## El defecto

`PERFIL.metas` se declara en **fracción de 1** (`disponibilidad: 0.9998`,
`backups: 0.95`) y así lo leía `disponibilidad`, que escala con `*100`. Pero
`backups` tenía su propia lectura, sin escalar:

```js
const metaConfigurada = PERFIL.metas?.backups;
const metaBackups = metaConfigurada===undefined ? 99.3 : Number(metaConfigurada);
```

Dos consecuencias, ambas visibles en un entregable (los dos perfiles
seleccionan `c7`):

| Perfil | Declara | Mostraba | Correcto |
|---|---|---|---|
| Acción Fiduciaria | *(omite)* | Meta 99,3 % | Meta 99,3 % ✓ |
| Bancoldex | `0.95` | **Meta 0,95 %** | Meta 95 % |
| Novaventa | `null` | **Meta 0 %** | sin meta |

Bancoldex, además, «cumplía» siempre: cualquier porcentaje de ejecución
supera una meta de 0,95.

Novaventa falla por un motivo aparte: `Number(null) === 0` y
`Number.isFinite(0) === true`, así que la rama «sin meta contractual» que F6
escribió expresamente para ese caso nunca llegaba a ejecutarse. El código
estaba escrito, comentado y muerto.

**Por qué no se detectó antes:** Acción Fiduciaria no declara `backups`, así
que cae al valor por defecto y su cifra nunca cambió. El A/B de AF pasa en 0
sin delatar nada. El defecto solo aparece en los clientes nuevos.

---

## La corrección

La causa raíz no es la aritmética, es que **la conversión estaba repetida por
clave**. Se extrajo a un único punto, `metaPerfil()`, junto a `cumpleMeta()`:

```js
function metaPerfil(clave,porDefecto,metas=PERFIL.metas){
  const declarada=metas?.[clave];
  if(declarada===null) return null;
  if(declarada===undefined) return porDefecto;
  const n=Number(declarada);
  return Number.isFinite(n)?n*100:porDefecto;
}
```

Tres casos deliberadamente distintos:

- **clave omitida** → el valor heredado de AF (retrocompatibilidad);
- **`null` explícito** → `null`, «sin meta contractual declarada»;
- **número** → escalado a porcentaje.

El `null` se compara **antes** de convertir; ese orden es el defecto que se
está corrigiendo, no un detalle de estilo.

El tercer parámetro (`metas`) existe para que la regla se pueda probar sin
mutar el `PERFIL` global, que es `const`.

Consumidores migrados (los dos que había):
`actualizarTarjetaBackups()` y `renderC7()`.

`disponibilidad` ya usaba la convención correcta y **no se tocó**: unificarla
también habría cambiado su comportamiento en los bordes (`||` captura `0`,
`null` y `NaN` por igual) sin necesidad, y ese camino sí afecta al render de
AF.

---

## Delta de spec

`openspec/changes/2026-08-05-f6-perfil-novaventa/specs/perfil-cliente/spec.md`
— nuevo requisito «unidad canónica de `PERFIL.metas`», con los tres
escenarios (fracción, `null` explícito, clave omitida). Se escribió antes del
código.

---

## Verificación ejecutada

**Pruebas de conformidad** (`automatizacion/`), 3 nuevas en
`TestUnidadDeLasMetasDelPerfil`:

```
Ran 74 tests — OK      (eran 71)
```

Se comprobó que **muerden**: reintroduciendo la lectura cruda en un solo
consumidor, `test_ningun_consumidor_reimplementa_la_conversion` falla con
`AssertionError: 2 != 1`. El archivo se restauró idéntico después.

**Autopruebas del store**, ejecutadas en el navegador sobre el archivo real
(`file://`), no simuladas en consola:

```
REPORTE.autopruebas()  →  31 pruebas, 0 fallos
  «Metas del perfil: fracción→porcentaje, con null distinto de ausente» → PASA
    ausente→99,3 · 0.95→95 · null→sin meta
```

**Contra los perfiles reales**, vía `resolverPerfil()` con la herencia
aplicada:

| Perfil | Declarado | Meta resuelta | Texto de la tarjeta |
|---|---|---|---|
| `accion-fiduciaria` | *(omitido)* | `99.3` | Meta 99,3 % |
| `novaventa` | `null` | `null` | sin meta contractual |
| `bancoldex` | `0.95` | `95` | Meta 95 % |

**Arnés A/B**: `verificar_ab.py --autoprueba` OK en los tres casos.

---

## Pendiente

**El A/B con exports reales no se ejecutó.** Requiere los insumos de
junio-2026, que por diseño no están en el repo. El riesgo para AF es bajo y
razonado —el valor de `metaBackups` para AF es `99.3` antes y después, la
misma constante— pero **eso es un argumento, no la evidencia que el contrato
exige**. Antes de fusionar F6 hay que correrlo.

El defecto simétrico de `codex/bancoldex-completo` (§3.2 del análisis: el
commit `4f822c3` cambia el resumen de c11 de AF de `"99,30%"` a `"99,3%"`)
**no se corrigió aquí** — vive en otra rama y le corresponde al change de F7.
