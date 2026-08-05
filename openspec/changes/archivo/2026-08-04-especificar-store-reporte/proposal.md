# Especificar el store canónico desplegado

## Contexto

El objeto `REPORTE` ya es la fuente de verdad del informe, pero sus
invariantes solo están documentados en comentarios dentro de
`informe-accion-fiduciaria 1.html`. El plan maestro y
`openspec/specs/README.md` señalan `store-reporte` como una de las primeras
capacidades que deben quedar especificadas antes de continuar la migración.

Sin una spec, una refactorización puede romper el agrupamiento de
notificaciones, confundir un cero confirmado con un insumo inválido o mover
la rehidratación al evento `load`, produciendo un informe exportado que se
pinta contra un store vacío.

## Propuesta

Documentar como requisitos verificables el comportamiento actualmente
desplegado de:

- dominios y estados permitidos;
- publicación y semántica de `cifra()`/`resuelto()`;
- notificaciones agrupadas e independientes entre suscriptores;
- reinicio al cambiar de periodo;
- rehidratación síncrona del HTML exportado;
- concordancia entre store y vistas.

El cambio no modifica el HTML ni añade comportamiento.

## Fuera de alcance

- Especificar o corregir `exportarHTML()`. El reconocimiento detectó que un
  script de insumos cargado desde un vecino puede sobrevivir al clon; esa
  capacidad queda bloqueada hasta coordinar el archivo HTML después de la
  PR #12.
- Modificar dominios, estados, reglas de negocio o criterios de exportación.
