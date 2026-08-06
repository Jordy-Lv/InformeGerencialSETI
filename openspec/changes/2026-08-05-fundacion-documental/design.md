# Diseño — la capa de contexto

## Por qué este change no lleva delta de spec

`openspec/specs/` describe **comportamiento del sistema**, redactado como
`SHALL` + escenario convertible en aserción. Este change no altera ninguna
línea ejecutable: no hay comportamiento nuevo que especificar y forzar un
delta produciría requisitos falsos del tipo «el repositorio SHALL tener un
README», que ninguna aserción puede verificar de forma útil.

`AGENTS.md` ya contempla el caso: cuando un cambio no altera comportamiento
especificable, el documento de sesión explica por qué la spec no aplica. Eso
se hace en `docs/2026-08-05-fundacion-documental.md`.

Lo que sí es verificable —que los enlaces internos resuelvan, que no queden
changes fusionados sin archivar— se comprueba con comandos concretos, y esos
comandos quedan escritos en el documento de sesión.

## Tres documentos en la raíz, no uno

La tentación es un único `README.md` gigante. Se descarta porque los tres
documentos tienen **lectores distintos y ciclos de vida distintos**:

| Documento | Lector | Cambia cuando |
|---|---|---|
| `README.md` | Quien llega por primera vez | Cambia el estado de una fase |
| `CLAUDE.md` | Un agente antes de escribir código | Se endurece o relaja una regla |
| `DESIGN.md` | Quien toca el HTML o una tarjeta | Se añade un componente o token |

Mezclarlos garantiza que el archivo se desactualice: un cambio de fase
obligaría a releer las reglas de diseño para encontrar dónde editar. Además,
`CLAUDE.md` se carga automáticamente en el contexto de un agente; meterle el
sistema de diseño completo gasta contexto en cada sesión, incluidas las que
solo tocan Python.

## `CLAUDE.md` remite, no duplica

`openspec/project.md` y `openspec/AGENTS.md` son la fuente de verdad del
proceso y de las restricciones. `CLAUDE.md` **no las reescribe**: enuncia lo
irrenunciable en forma corta y enlaza al documento que manda. Duplicar el
texto crearía dos verdades que divergen al primer ajuste, exactamente el
defecto que este proyecto ya documentó en el perfil (`metas` declaradas en
`perfiles/` que el motor no consume).

## Pruebas adversariales como parte del contrato

Una regla escrita solo se sostiene si alguien intentó romperla. Por eso
`CLAUDE.md` incluye una batería de peticiones que **deben ser rechazadas**,
con la respuesta correcta al lado: «migremos a Vite», «copiemos
`automatizacion/` para el cliente nuevo», «el A/B da 9 diferencias pero
ninguna es del cambio, mergeemos».

No son ejemplos decorativos: cada una corresponde a algo que ya pasó en este
repositorio (el PR #5 cerrado sin fusionar, el A/B parcial de F2) o a una
propuesta que `project.md` anticipa y prohíbe. Sirven para dos cosas:
verificar que un agente nuevo entendió el contrato, y detectar cuándo una
regla está redactada de forma tan ambigua que se puede obedecer y violar a
la vez.

## Archivado: mover, no borrar

`changes/README.md` dejaba abierta la convención entre mover a
`changes/archivo/` o eliminar. Se elige **mover**, y se fija por escrito:

- El `tasks.md` de un change archivado conserva la lista cerrada de archivos
  y las casillas marcadas. Es la única evidencia de qué se prometió tocar
  frente a qué se tocó; borrarla deja el `git log` como único registro, y el
  `git log` no dice qué se decidió *no* hacer.
- La regla de conjuntos disjuntos solo mira `openspec/changes/*/tasks.md`.
  Con los archivados un nivel más abajo, la regla vuelve a dar el resultado
  correcto sin necesitar excepciones.

Un change se archiva cuando su PR está fusionado en `main` **y** su
criterio de aceptación está cerrado con evidencia. F0 se archiva con una
nota explícita: su pendiente (`dorados/accion-fiduciaria-2026-06.json`) no
es código, es un artefacto que exige insumos reales de junio.

## El sistema de diseño se documenta desde el código

`DESIGN.md` no propone una paleta ni una escala tipográfica nuevas. Recoge
lo que ya existe: los dos bloques de `:root`, las 225 clases en
`bloque__elemento--modificador`, el lienzo fijo de 1280×720 y las 28 slides.

La razón es la restricción #2: cualquier cosa que este documento «mejore»
por su cuenta terminaría siendo una cifra o un píxel distinto en el informe
de un cliente real. El documento describe, y donde hay una inconsistencia
real —dos bloques `:root` separados, `--rojo` y `--rojo-tabla` conviviendo—
la señala como deuda en vez de resolverla de oficio.

## Alternativas descartadas

- **Un `docs/adr/` con decisiones numeradas.** Formato más estándar, pero
  este repositorio ya narra sus decisiones en documentos de sesión fechados
  y con comandos ejecutados. Introducir un segundo formato obligaría a
  decidir, en cada cambio, en cuál de los dos escribir.
- **Generar el índice de `docs/` con un script.** El valor del índice no es
  la lista de archivos —eso lo da `ls`— sino la columna de estado, que exige
  criterio humano sobre qué documento quedó superado por cuál.
- **Mover el contenido de `project.md` a la raíz.** Rompería todos los
  enlaces existentes y la referencia de `AGENTS.md`, a cambio de nada que no
  resuelva un enlace desde el `README`.
