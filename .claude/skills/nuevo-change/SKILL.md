---
name: nuevo-change
description: Arranca un change de OpenSpec en este repositorio con la estructura obligatoria (proposal, design, tasks y delta de spec), verificando antes que no colisione con otro change abierto. Úsala cuando vayas a empezar cualquier trabajo que toque código, specs o comportamiento del informe — antes de escribir la primera línea.
---

# Arrancar un change de OpenSpec

En este repositorio **la spec es la puerta de revisión, no el diff**. Un PR
que cambia comportamiento descrito en `openspec/specs/` sin su delta se
rechaza sin leer el código. Esta skill produce la estructura correcta y, más
importante, obliga a las comprobaciones que evitan que dos agentes en
paralelo se pisen.

## Paso 1 — Contexto obligatorio

Lee, en este orden, antes de proponer nada:

1. `openspec/project.md` — las tres restricciones inviolables.
2. `openspec/AGENTS.md` — el proceso completo.
3. `CLAUDE.md` — el perímetro operativo y las pruebas adversariales.

## Paso 2 — Comprobar colisión de archivos

**Dos changes abiertos no pueden declarar el mismo archivo.**

```bash
for t in openspec/changes/*/tasks.md; do echo "── $t"; sed -n '/Lista cerrada/,/^##/p' "$t"; done
```

Los changes en `openspec/changes/archivo/` ya están cerrados y **no cuentan**
para esta regla.

Si tu trabajo necesita un archivo que otro change abierto declara: para y
coordina. No sirve el argumento «es una rama aparte, no afecta a nadie» — el
conflicto aparece en el merge, y `informe-accion-fiduciaria 1.html` tiene
6.700 líneas.

## Paso 3 — Crear la estructura

```bash
mkdir -p "openspec/changes/$(date +%Y-%m-%d)-<id>/specs/<capacidad>"
```

```text
openspec/changes/<fecha>-<id>/
  proposal.md   Qué se propone, por qué, y qué queda FUERA de alcance
  design.md     Decisiones, alternativas descartadas con nombre, riesgos
  tasks.md      Lista CERRADA de archivos + tareas con casillas
  specs/<capacidad>/spec.md   Delta: ADDED / MODIFIED / REMOVED
```

Toma como modelo `openspec/changes/archivo/2026-08-04-f1-perfil-cliente/`:
está cerrado con A/B en cero y sirve de referencia de nivel de detalle.
Vive bajo `archivo/` porque un change cerrado se mueve ahí; los abiertos
cuelgan directamente de `openspec/changes/`.

## Paso 4 — Escribir el delta antes que el código

Cada requisito se redacta así:

```markdown
### Requirement: <nombre corto>

El motor SHALL <comportamiento>.

#### Scenario: <situación concreta>

- **GIVEN** <estado inicial>
- **WHEN** <acción>
- **THEN** <resultado esperado>
```

**La prueba de que un requisito está bien escrito es que se pueda convertir
directamente en una aserción** de `REPORTE.autopruebas` o de `pytest`. Si no
se puede, no es un requisito: es un deseo, y va a `design.md`.

Si el change no altera comportamiento especificable (documentación,
herramientas), no fuerces un delta — explica en el documento de sesión por
qué la spec no aplica.

## Paso 5 — Implementar y verificar

```bash
python3 -m unittest discover -s automatizacion -p 'test_*.py' -v
python3 automatizacion/verificar_ab.py --autoprueba
```

Si tocaste el HTML, el criterio de aceptación es **0 diferencias** contra
`main` sobre dos exports reales generados con los mismos insumos:

```bash
python3 automatizacion/verificar_ab.py export-main.html export-rama.html
```

Un A/B con diferencias «que no son de mi cambio» **no se acepta**: se iguala
el estado de entrada y se repite hasta cero.

## Paso 6 — Cerrar

No está terminado hasta que:

- [ ] `proposal.md`, `design.md` y `tasks.md` cuentan lo que *realmente* se
      implementó, no la versión anterior del plan.
- [ ] El delta está aplicado a `openspec/specs/<capacidad>/spec.md`.
- [ ] Existe `docs/<AAAA-MM-DD>-<tema>.md` con `Contexto`, `Qué se
      implementó`, `Verificación realizada`, `Archivos tocados` y
      `Pendiente` — **cada afirmación con su comando y su resultado real**.
- [ ] `docs/README.md`, el plan maestro y el `README.md` reflejan el estado
      nuevo si cambió una fase.
- [ ] PR contra `main`, revisada por alguien distinto de quien la escribió.

Una prueba no ejecutada se marca como **pendiente**, nunca como
implícitamente aprobada.

## Paso 7 — Archivar (solo cuando esté fusionado y verificado)

Antes de mover, comprueba que ninguna prueba lea la ruta del change:

```bash
grep -rn "openspec/changes" automatizacion/*.py
```

Si alguna la lee, haz que resuelva el delta en las dos ubicaciones —abierta y
archivada— como ya hace `test_specs_store_reporte.py`. Archivar sin esto
rompe la prueba.

```bash
git mv "openspec/changes/<fecha>-<id>" openspec/changes/archivo/
python3 -m unittest discover -s automatizacion -p 'test_*.py'
```

Se mueve, no se borra: el `tasks.md` es la única evidencia de qué se
prometió tocar frente a qué se tocó, y de qué se decidió *no* hacer.
