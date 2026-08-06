# Fundación documental — contexto legible por personas e IAs

**Fecha:** 5 de agosto de 2026
**Rama:** `docs/fundacion-documental`
**Change:** `openspec/changes/2026-08-05-fundacion-documental/`

## Contexto

Una auditoría del estado del proyecto encontró que el proceso técnico se
cumple —las tres restricciones inviolables se respetan, F1 cerró con A/B en
cero, las 40 pruebas pasan— pero que **la puerta de entrada al repositorio no
existía**. Sin `README.md` en la raíz, `openspec/project.md` se autodescribe
como «la primera pantalla que cualquiera debe leer» desde una subcarpeta
donde nadie mira primero, y `docs/` acumulaba 23 documentos sin índice ni
señal de vigencia.

Tres consecuencias medibles, no estéticas:

1. **La regla de conjuntos de archivos disjuntos daba un falso positivo.**
   Tres changes ya fusionados seguían en `openspec/changes/`, y F1 y F2
   declaraban los mismos archivos. Un agente que aplicara la regla
   literalmente se bloqueaba.
2. **`Accion Fiduciaria/` no estaba en `.gitignore`**, a diferencia de
   `Insumos*/`, `Bancoldex/` y `Novaventa/`, que sí lo están por la misma
   razón. Contenía los cuatro insumos reales del cliente y un export de
   4,3 MB con `window.__ESTADO__`.
3. **El sistema visual no estaba documentado**: 225 clases y 28 slides que
   quien tocara una tarjeta tenía que reconstruir leyendo CSS minificado.

## Qué se implementó

Ninguna línea de código productivo. El change **no toca**
`informe-accion-fiduciaria 1.html`, `perfiles/` ni `automatizacion/*.py`, por
lo que no puede alterar una cifra de Acción Fiduciaria.

### Documentos nuevos

- **`README.md`** — punto de entrada: qué es el producto, las tres
  restricciones con su motivo, una tabla «por dónde empezar según a qué
  vengas», el mapa del repositorio, el flujo de trabajo, los comandos de
  verificación, el estado real de las fases y la deuda conocida.
- **`CLAUDE.md`** — contrato operativo para agentes. Remite a `project.md` y
  `AGENTS.md` en vez de duplicarlos, y declara explícitamente que si algo lo
  contradice, gana `project.md`. Incluye una **batería de diez pruebas
  adversariales**: peticiones que deben ser rechazadas, cada una
  correspondiente a algo que ya pasó aquí (el PR #5 cerrado sin fusionar, el
  A/B parcial de F2) o que `project.md` anticipa y prohíbe.
- **`DESIGN.md`** — el sistema de diseño **extraído del código**: el lienzo
  fijo de 1280×720, los dos bloques de tokens, las tres familias
  tipográficas con su cascada de respaldo, la nomenclatura BEM con sus 17
  bloques, la anatomía de `tarjeta-kpi`, las restricciones que impone
  `html2canvas` y la hidratación de textos desde el perfil.
- **`docs/README.md`** — índice del histórico con estado por documento
  (vigente / referencia / superado), la plantilla obligatoria y desde qué
  commit aplica, y la tabla de documentos citados que ya no existen.
- **`docs/PATRONES.md`** — los siete patrones y los ocho descartados,
  extraídos de la sección 4 del plan maestro, donde estaban mezclados con el
  cronograma y eran imposibles de citar en una revisión. Añade los patrones
  de proceso.
- **`docs/requisitos-producto.md`** — 24 requisitos en seis grupos, cada uno
  marcado `[SPEC]`, `[CÓDIGO]` o `[PLAN]` según su grado de formalización, y
  con su medio de verificación. Cierra con la tabla de qué quedaría cubierto
  por cada capacidad sin escribir.
- **`.claude/skills/nuevo-change/SKILL.md`** — el flujo de OpenSpec como
  skill invocable (`/nuevo-change`), con la comprobación de colisión de
  archivos como paso obligatorio antes de crear la estructura.

### Correcciones

- **`.gitignore`** cubre `Accion Fiduciaria/`, con el motivo escrito.
- **`openspec/changes/archivo/`** creado, con la convención fijada en
  `openspec/changes/README.md`: se mueve, no se borra, porque el `tasks.md`
  es la única evidencia de qué se decidió *no* hacer. Se archivaron dos de
  los tres changes cerrados; el tercero (F1) se quedó abierto por la razón
  que se explica abajo.
- **`automatizacion/test_specs_store_reporte.py`** resuelve ahora el delta
  buscándolo tanto en `changes/` como en `changes/archivo/`, en vez de
  depender de una ruta literal.
- **`openspec/specs/README.md`** pasa a una tabla de las siete capacidades
  con qué falta en cada pendiente, señalando `reglas-de-negocio` como la más
  urgente.
- **Tres referencias rotas anotadas** con la razón real de cada una, que
  resultó ser distinta: dos documentos se **borraron a propósito** el
  29/07/2026 con autorización explícita, y el tercero
  (`2026-07-28-desarrollo-mac-despliegue-windows.md`) **no figura en esa
  tabla de borrados**: o nunca se subió, o se perdió. Ese queda marcado como
  no resuelto en `automatizacion/README.md`, con la fuente vigente
  alternativa al lado.

## Hallazgo durante la verificación: archivar un change rompía dos pruebas

Al correr la suite después de archivar, **falló**: `Ran 24 tests ... FAILED
(errors=2)`. `test_specs_perfil_cliente.py` y `test_specs_store_reporte.py`
leen el delta desde la ruta literal del change —
`openspec/changes/<change>/specs/<capacidad>/spec.md`— que al archivarse deja
de existir. Era un acoplamiento que nadie había documentado.

Se resolvió de forma distinta en cada uno, y la diferencia importa:

- **`test_specs_store_reporte.py`** — se le añadió un resolutor que busca el
  delta en `changes/` y en `changes/archivo/`. La prueba sigue comprobando
  exactamente lo mismo; solo deja de depender de dónde viva el change. Ese
  archivo no lo declara ningún otro change abierto.
- **`test_specs_perfil_cliente.py`** — **no se tocó**, y por eso **F1 se
  quedó sin archivar**. Ese archivo está declarado por el `tasks.md` de F2 y
  tiene cambios sin confirmar en la rama de F2. Editarlo aquí habría
  producido justo la colisión que la regla de conjuntos disjuntos existe para
  evitar: dos ramas modificando el mismo archivo, con conflicto garantizado
  en el merge.

F1 se archiva cuando F2 cierre, aplicando el mismo resolutor. Queda como
pendiente explícito y `openspec/changes/README.md` avisa de la colisión
mientras dure.

La consecuencia práctica es que la regla de conjuntos disjuntos **sigue dando
un falso positivo entre F1 y F2** hasta entonces. Está documentado en vez de
silenciado: un falso positivo explicado es manejable; uno inexplicado
bloquea a quien llegue.

## Verificación realizada

- **La suite completa pasa** —
  `python3 -m unittest discover -s automatizacion -p 'test_*.py'` →
  `Ran 36 tests ... OK`. Son 36 y no 40 porque las otras cuatro las añade F2
  en su propia rama, sobre `test_specs_perfil_cliente.py`.
- **Ningún archivo productivo fue tocado** —
  `git diff --stat main...HEAD -- '*.html' '*.js' 'automatizacion/*.py'` →
  salida vacía.
- **Los enlaces internos resuelven** — recorrido de los 78 enlaces relativos
  de todos los `.md` del repositorio. Los únicos destinos ausentes son
  esperados y están anotados: rutas a `Insumos/` (carpeta ignorada por
  diseño), el `.docx` cuya ausencia ya estaba registrada sin resolver desde
  el 29/07, y `2026-08-05-f2-contrato-perfil.md`, que vive en la rama de F2
  y todavía no está en `main`.
- **Este change no colisiona con F2** — sus listas cerradas son disjuntas:
  no declara ninguno de los seis archivos de F2. La colisión F1↔F2 persiste
  y está documentada arriba.
- **`Accion Fiduciaria/` queda cubierta** —
  `git check-ignore -v "Accion Fiduciaria/"` → señala la línea nueva del
  `.gitignore` (antes: código 1, sin coincidencia).
- **Sin errores de espacios** — `git diff --check` → código 0.

## Por qué este change no lleva delta de spec

`openspec/specs/` describe comportamiento del sistema, redactado como `SHALL`
+ escenario convertible en aserción. Este change no altera ninguna línea
ejecutable: forzar un delta produciría requisitos falsos del tipo «el
repositorio SHALL tener un README», que ninguna aserción verifica de forma
útil. `AGENTS.md` contempla el caso y pide que el documento de sesión lo
explique; esta sección es esa explicación.

Lo que sí es verificable —enlaces que resuelven, changes archivados, suite
verde, `.gitignore` efectivo— se comprobó con los comandos de arriba.

## Archivos tocados

Nuevos:

- `README.md`, `CLAUDE.md`, `DESIGN.md`
- `docs/README.md`, `docs/PATRONES.md`, `docs/requisitos-producto.md`
- `docs/2026-08-05-fundacion-documental.md`
- `.claude/skills/nuevo-change/SKILL.md`
- `openspec/changes/2026-08-05-fundacion-documental/{proposal,design,tasks}.md`

Modificados:

- `.gitignore`
- `openspec/specs/README.md`, `openspec/changes/README.md`
- `automatizacion/README.md` (solo la referencia no resuelta)
- `automatizacion/test_specs_store_reporte.py` (solo la resolución de la
  ruta del delta)
- `docs/2026-07-22-backups-radar-ci.md`,
  `docs/2026-07-23-analisis-por-rango-y-redondeo.md` (solo enlaces)

Movidos con `git mv`, sin editar contenido:

- `openspec/changes/2026-08-04-f0-dorados/` → `changes/archivo/`
- `openspec/changes/2026-08-04-especificar-store-reporte/` → `changes/archivo/`

## Pendiente

Este change **registra** esta deuda; no la resuelve. Cada punto necesita su
propio change:

- **Las cinco specs de capacidad que faltan.** Por orden de riesgo:
  `reglas-de-negocio` (atribución SETI, redondeo, bolsa de horas — las tres
  con errores ya corregidos en producción y sin `SHALL` que las proteja),
  `exportacion`, `adaptadores-fuente`, `inventario-tarjetas`,
  `automatizacion-insumos`.
- **`dorados/accion-fiduciaria-2026-06.json`** — criterio de cierre de F0.
  Exige insumos reales de junio de 2026.
- **Los campos declarativos del perfil.** `metas`, `celula`,
  `contrato.codigo` y `contrato.vigenciaHasta` están en
  `perfiles/accion-fiduciaria.js` y el motor no los consume: la meta 99,30 %
  sigue escrita a mano en unos ocho puntos del HTML. Cambiar el perfil no
  produce efecto **ni error**.
- **`automatizacion/instalar_tarea_programada.{ps1,bat}`** — sin seguimiento
  en la rama de F2, sin figurar en ningún `tasks.md` y sin mención en
  `automatizacion/README.md`.
- **`esAccionFiduciaria()` y `esClienteAccion()`** — ya leen del perfil, pero
  conservan el nombre de un cliente en el identificador de una función del
  motor multicliente.
- **`2026-07-28-desarrollo-mac-despliegue-windows.md`** — confirmar si se
  perdió o nunca se subió. Mismo caso que los dos `.docx` registrados el
  29/07 y todavía sin resolver.
- **Archivar `2026-08-04-f1-perfil-cliente`** cuando F2 cierre, aplicando a
  `test_specs_perfil_cliente.py` el mismo resolutor de ruta que ya tiene
  `test_specs_store_reporte.py`. Hasta entonces, F1 y F2 declaran los mismos
  archivos y la regla de conjuntos disjuntos da un falso positivo conocido.
- **F2 sigue abierto.** Su criterio de aceptación —A/B en cero con estado de
  insumos idéntico— continúa pendiente, y este change no lo altera.
