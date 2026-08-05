# Diseño — spec base de `store-reporte`

## Fuente de verdad observada

La spec se deriva del código desplegado en `main` (`bb71e09`) y no propone
una arquitectura nueva. Los puntos reconocidos son:

- declaración de `ESTADOS`, `DOMINIOS`, `VACIO` y `REPORTE`;
- rehidratación contigua a la creación del store, durante la evaluación del
  script;
- `aplicarPeriodo()`;
- consumidores y aserciones existentes de `REPORTE.autopruebas`.

## Verificación sin tocar el monolito

Mientras la PR #12 mantiene reservado el HTML, una prueba Python de librería
estándar lee el archivo como fuente y fija las invariantes estructurales que
esta spec documenta. No ejecuta ni reescribe JavaScript. Los escenarios
siguen redactados para poder migrarse después a aserciones de
`REPORTE.autopruebas`.

Se descarta añadir ahora las aserciones dentro del HTML: violaría los
conjuntos de archivos disjuntos y obligaría a resolver el conflicto de F1 en
esta tarea documental.

## Aplicación de la spec

Como el comportamiento ya está desplegado y este change no tiene una fase de
código posterior, el mismo PR añade la spec actual en
`openspec/specs/store-reporte/spec.md` y conserva este delta como puerta de
revisión. No se archiva el change porque el repositorio todavía no ha fijado
una convención de archivo.
