# Cómo trabaja una IA en este proyecto

Lee primero `openspec/project.md` — las restricciones de ahí no son
negociables. Esto describe el *proceso*: cómo se propone, especifica,
implementa y verifica un cambio, y qué mecanismos existen específicamente
para que varias IAs trabajando en paralelo no se desvíen ni se pisen.

## La spec es la puerta de revisión, no el diff

Un PR que cambia comportamiento descrito en `openspec/specs/` sin su delta
correspondiente en `openspec/changes/<el-change>/specs/` **se rechaza sin
leer el código**. Esto convierte "esto no era lo acordado" de una opinión en
un hecho verificable: si el comportamiento nuevo no está en la spec, no se
implementa, sin importar cuánto sentido parezca tener en el momento.

## Estructura de un `change`

```
openspec/changes/<fecha>-<id>/
  proposal.md     # qué se propone y por qué
  design.md       # decisiones de diseño, alternativas descartadas y por qué
  tasks.md        # lista de tareas + LISTA DE ARCHIVOS QUE SE VAN A TOCAR
  specs/<capability>/spec.md   # delta: ADDED / MODIFIED / REMOVED
```

Cuando el `change` se completa y se verifica, su contenido se aplica a
`openspec/specs/<capability>/spec.md` (la verdad actual, desplegada) y el
change se archiva.

## Regla operativa: conjuntos de archivos disjuntos

El `tasks.md` de cada change lista los archivos que va a tocar. **Dos
changes abiertos al mismo tiempo no pueden listar el mismo archivo.** Con
un archivo de más de 6.500 líneas concentrando la mitad de los commits del
repo, esta es la regla que evita que dos IAs (o una IA y una persona)
trabajando en paralelo produzcan un conflicto irresoluble. En la práctica,
esto serializa las fases que tocan `informe-accion-fiduciaria 1.html` (o su
sucesor `informe.html`) una detrás de otra — y eso es correcto: esas fases
ya son secuenciales por dependencia, no paralelizables de verdad.

Antes de empezar a escribir código: confirma que ningún otro change abierto
liste los mismos archivos que el tuyo. Si los lista, coordina antes de
tocar nada — no asumas que "total, es rama aparte, no afecta a nadie". Ver
la explicación de por qué el merge sí importa aunque la rama sea
independiente en `docs/` (sesión del 4 de agosto de 2026).

## Todo requisito es `SHALL` + al menos un escenario verificable

Cada requisito en una spec se redacta como `SHALL <comportamiento>`, seguido
de al menos un `#### Scenario:` que describa una situación concreta y el
resultado esperado. La prueba de que un requisito está bien escrito es que
se pueda convertir directamente en una aserción de `REPORTE.autopruebas` o
de `pytest`. **Si no se puede convertir en aserción, no es un requisito —
es un deseo, y va a `design.md`, no a la spec.**

## No se abre una capacidad por cliente

`openspec/specs/` se organiza por **capacidad del sistema**
(`perfil-cliente`, `inventario-tarjetas`, `adaptadores-fuente`,
`store-reporte`, `exportacion`, `automatizacion-insumos`,
`reglas-de-negocio`...), nunca por cliente. Un cliente es una *instancia*
que vive en `perfiles/` y se valida con pruebas de conformidad contra las
specs existentes. Si un cliente parece necesitar una spec propia, es una
señal de que una capacidad está mal delimitada — no una razón para crear
`capabilities/cliente-<x>/`.

## Antes de escribir una línea

1. Lee `openspec/project.md`.
2. Revisa qué changes están abiertos (`openspec/changes/`) y qué archivos
   listan sus `tasks.md`, para no colisionar.
3. Si tu tarea toca comportamiento ya especificado, escribe primero el
   delta en `openspec/changes/<tu-change>/specs/`, antes de tocar código.
4. Si tu tarea toca `informe-accion-fiduciaria 1.html` (o su sucesor) de
   cualquier forma: el criterio de aceptación es 0 diferencias en
   `automatizacion/verificar_ab.py` contra `main`, salvo que el change
   documente explícitamente qué cifra visible cambia y por qué (eso solo
   aplica a fases que agregan comportamiento nuevo, nunca a Acción
   Fiduciaria — ver la restricción inviolable #2 en `project.md`).
5. Reconocimiento antes que construcción: si algo depende de una fuente
   externa (GLPI, AlertOps, Zabbix, Aranda), sondéala primero y confirma
   contra la evidencia real — no asumas que el identificador de campo o la
   categoría es igual a la de otro cliente solo porque comparten
   plataforma.

## Al terminar

- Deja un `docs/<AAAA-MM-DD>-<tema>.md` con: Contexto / Qué se implementó /
  Verificación realizada (con el comando al lado de cada afirmación — una
  afirmación sin el comando que la prueba no se distingue de una plausible)
  / Archivos tocados / Pendiente.
- El change no se archiva hasta que la verificación A/B contra `main` con
  insumos reales dé cero diferencias, cuando aplique.
- Abre PR contra `main`. La revisión la hace alguien distinto de quien
  escribió el código — GitHub ya lo impone (un autor no puede aprobar su
  propio PR), y es la razón por la que el árbol paralelo del PR #5 se
  detectó antes de llegar a `main`, no después.
