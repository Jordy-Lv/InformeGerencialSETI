# Diseño — inventario que describe la interfaz existente

## Descriptor, perfil y comportamiento

`INVENTARIO_TARJETAS` vive en el motor y define el vocabulario cerrado: id, identidad legado DOM, dominios, fuentes, regla de criterio, renderizador y exportabilidad. `PERFIL.tarjetas.seleccionadas` es solo una lista serializable de ids y conserva el orden entregado al cliente. Las reglas de criterio y renderizadores son registros del motor nombrados por string; el perfil no contiene funciones.

Los diez ids son `c3`, `c4`, `c5`, `c6`, `c7`, `c8`, `c8m`, `c9`, `c11` y `c12`. Anexos (`c12`) participa en la conformidad DOM y el orden, pero no tiene dominio, criterio ni renderizador dinámico.

## Derivaciones sin doble camino

Los dominios se forman como unión ordenada de los descriptores seleccionados. Las extensiones se forman desde sus fuentes. Los siete criterios se obtienen de los descriptores que declaran uno y conservan sus textos y orden actuales. `renderAll()` resuelve el renderizador registrado de cada descriptor; Anexos no agrega una llamada porque su contenido es estático.

Se descarta poner funciones en el perfil: impediría serializarlo en el export y convertiría configuración de cliente en código. También se descarta generar nodos en F3: el DOM existente se valida primero y F4 será quien lo reemplace.

## Conformidad y equivalencia

Al arrancar se valida que los ids del perfil y los nombres de regla existan. `REPORTE.autopruebas` coteja tarjeta, diapositiva legado, exportabilidad y criterios contra el DOM. Las pruebas Python comprueban estáticamente las diez tarjetas y los siete criterios. El arnés A/B verifica la equivalencia del export completo.
