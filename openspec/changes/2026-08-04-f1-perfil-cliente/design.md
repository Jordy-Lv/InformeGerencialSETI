# Diseño — perfil de cliente

## Perfil como dato puro

Cada perfil publica un objeto serializable, sin funciones. El registro del
motor conserva las funciones que resuelven nombres; el archivo de perfil solo
contiene datos que una persona de cuenta puede revisar.

`fusionarProfundo()` se reutiliza para resolver una futura cadena `extiende`:
objetos se fusionan recursivamente y arreglos se reemplazan. No se introduce un
segundo algoritmo de merge.

## Dos formas de carga para dos momentos distintos

En modo autoría, el HTML carga el perfil vecino marcado con
`data-perfil-cliente`. Esto mantiene el perfil editable y revisable como dato.

En el export, `codigoEstadoCliente()` serializa primero el snapshot canónico y
adjunta inmediatamente el perfil ya resuelto a `window.__ESTADO__.perfil`.
`podarClon()` elimina el script vecino. Como `exportarHTML()` inyecta esa
cabecera antes de los scripts de aplicación, `resolverPerfil()` toma primero el
perfil embebido. Así, el archivo entregado no depende de su ubicación ni de una
red.

El perfil se adjunta después de cerrar la asignación JSON canónica, en la misma
cabecera y antes de arrancar el motor. Esta separación es deliberada:
`verificar_ab.py` continúa comparando exactamente el estado histórico de
`main`, mientras el navegador sí observa el perfil dentro de
`window.__ESTADO__`. Incluir el campo dentro de `snapshotEstado()` produciría
una diferencia estructural inevitable y haría imposible cumplir el criterio A/B
de F1 aun cuando cifras y textos fueran idénticos.

Se descartó copiar el contenido textual del archivo vecino dentro del clon:
duplicaría dos representaciones del perfil. El objeto resuelto dentro del
estado es la fuente que ya viaja con el resto de los datos del entregable.

## Textos de interfaz derivados del perfil

`hidratarTextosPerfil()` resuelve el título, la marca y el cliente de portada
desde `PERFIL.textos` al evaluar el motor. Los mensajes de carga, filtros,
propiedades PDF, nombres de archivo y aviso de confidencialidad consumen el
mismo perfil. `nombreArchivo` permanece separado de `nombre` porque el nombre
histórico del entregable no lleva tilde y cambiarlo violaría la equivalencia.

## Compatibilidad del almacenamiento

Las escrituras nuevas de posiciones y bolsa usan `claveAlmacen()`. Las
lecturas consultan primero la clave nueva y luego la histórica; borrar limpia
ambas. La migración no reescribe silenciosamente datos históricos.

## Verificación

Las autopruebas comprueban que la cabecera adjunta el perfil al estado y que la
poda retira la dependencia externa. Una prueba Python estática fija además el
contrato OpenSpec, la pureza del perfil y los fallbacks de almacenamiento.

La equivalencia visible se cerró con dos exportaciones completas de julio de
2026 producidas desde `main` y la rama con los mismos insumos reales no
versionados. `automatizacion/verificar_ab.py` informó cero diferencias.
