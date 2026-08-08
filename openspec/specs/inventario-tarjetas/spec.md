# Inventario de tarjetas

## Requirements

### Requirement: inventario declarativo de tarjetas

El motor SHALL mantener un inventario de tarjetas con id estable, identidad
legado, presentación, dominios, fuentes, exportabilidad, dependencias y
estrategias nombradas; SHALL resolver los ids del perfil sin funciones dentro
de este.

#### Scenario: perfil de Acción Fiduciaria

- **GIVEN** el perfil `accion-fiduciaria` con sus diez ids de tarjeta
- **WHEN** el motor resuelve el inventario
- **THEN** obtiene `c3`, `c4`, `c5`, `c6`, `c7`, `c8`, `c8m`, `c9`, `c11` y `c12` en ese orden y falla ante un id desconocido

#### Scenario: descriptor listo para plantilla

- **GIVEN** una tarjeta seleccionada de Acción Fiduciaria
- **WHEN** el motor genera el panel
- **THEN** su descriptor aporta toda la identidad visual del resumen y conserva
  los ids legado de su tarjeta y diapositiva

### Requirement: listas operativas derivadas

El motor SHALL derivar dominios, extensiones admitidas, criterios de carga y renderizadores desde las tarjetas resueltas, sin una segunda lista fija.

#### Scenario: criterios de Acción Fiduciaria

- **GIVEN** las diez tarjetas del perfil de Acción Fiduciaria
- **WHEN** se calcula el estado de validación
- **THEN** se obtienen los siete criterios actuales en su orden y con su texto exacto

### Requirement: conformidad descriptor con interfaz legado

El motor SHALL comprobar que cada descriptor seleccionado corresponde a su
tarjeta y diapositiva legado en el DOM; SHALL generar el contenedor de tarjeta
desde su descriptor sin reemplazar la diapositiva que usan los parsers y PDF.

#### Scenario: inventario y DOM completos

- **GIVEN** el DOM actual de Acción Fiduciaria
- **WHEN** se ejecuta `REPORTE.autopruebas()` sin insumos
- **THEN** informa que las diez tarjetas declaradas tienen sus nodos de tarjeta y diapositiva, y que los criterios declarados permanecen en siete

#### Scenario: plantilla sobre nodos legado

- **GIVEN** el inventario predeterminado de Acción Fiduciaria
- **WHEN** inicia el informe
- **THEN** las diez tarjetas del panel se marcan como generadas desde el
  inventario y sus diez diapositivas legado conservan el mismo id

### Requirement: tarjeta de capacidad declarada por perfil

El inventario SHALL ofrecer la tarjeta `c10` para el dominio `capacidad` y
solo la SHALL activar un perfil que la declare en su selección de tarjetas.

#### Scenario: Novaventa activa capacidad

- **GIVEN** el perfil Novaventa selecciona `c10`
- **WHEN** se resuelve su inventario
- **THEN** la tarjeta presenta la ocupación máxima y una gráfica horizontal
  por filesystem, sobre una escala explícita de 0 a 100 %

#### Scenario: Acción Fiduciaria conserva su panel

- **GIVEN** el perfil Acción Fiduciaria no selecciona `c10`
- **WHEN** se resuelve su inventario y se exporta el informe
- **THEN** no se crea una cifra automática de bolsa ni cambia su panel visible

### Requirement: preset y ficha de línea base propios del perfil

El motor SHALL resolver la presentación declarada por el perfil sobre el
inventario común, sin transferir cifras contractuales entre clientes.

#### Scenario: preset inicial de Novaventa

- **GIVEN** el perfil Novaventa y la referencia de junio de 2026
- **WHEN** se inicia el informe sin un preset local guardado
- **THEN** muestra línea base, indicadores, casos, disponibilidad, backups,
  logros, capacidad y anexos; no muestra la bolsa de horas, mitigaciones ni
  el duplicado de disponibilidad por CI

#### Scenario: línea base de Novaventa

- **GIVEN** el perfil Novaventa
- **WHEN** se abre la tarjeta Línea base
- **THEN** muestra Administración remota de Bases de datos, 48 BD SQL Server,
  7 BD DB2 y vigencia de 21/07/2025 a 20/07/2026, sin el contrato ni las
  cifras de Acción Fiduciaria

### Requirement: tarjeta de control de línea base

El inventario SHALL incluir una tarjeta `c3b` que presente la comparación
entre la línea base contratada y la vigente, con la diferencia por
categoría, a partir de cifras declaradas por el perfil y sin requerir
ningún insumo cargado.

#### Scenario: Bancoldex declara su control de línea base

- **GIVEN** el perfil `bancoldex` con `lineaBase.control` declarado y `c3b`
  en `tarjetas.seleccionadas`
- **WHEN** se renderiza el informe sin haber cargado ningún insumo
- **THEN** `c3b` muestra el total base, el total actual y la diferencia, sin
  quedar en estado «Pendiente de cargar»

#### Scenario: el detalle vive en el modal

- **GIVEN** `c3b` renderizada con su ficha declarada
- **WHEN** se abre la tarjeta
- **THEN** el modal lista cada tipo de infraestructura con su base, su valor
  actual y su diferencia, agrupados por ambiente

#### Scenario: un perfil que no la declara no la muestra

- **GIVEN** un perfil sin `lineaBase.control` y sin `c3b` en
  `tarjetas.seleccionadas`
- **WHEN** se resuelven las tarjetas del perfil
- **THEN** `c3b` no aparece en el informe ni en el HTML exportado

### Requirement: tarjeta de firmas aprobadoras

El inventario SHALL incluir una tarjeta `c14` que presente los firmantes
declarados por el perfil y permita registrar la firma de cada uno trazándola
sobre un lienzo en el propio informe, sin dependencias externas ni llamadas
de red.

#### Scenario: se traza y se conserva una firma

- **GIVEN** `c14` seleccionada y un firmante sin firma registrada
- **WHEN** se traza la firma sobre su lienzo
- **THEN** el trazo se guarda en el almacén del cliente activo y sigue
  visible tras recargar el informe

#### Scenario: la firma sobrevive al cambio de periodo

- **GIVEN** un firmante con firma registrada en un periodo
- **WHEN** se cambia el periodo del informe
- **THEN** la firma se conserva, sin exigir volver a trazarla

#### Scenario: la firma no se comparte entre clientes

- **GIVEN** dos clientes distintos con `c14` seleccionada
- **WHEN** se registra una firma en el primero y se activa el segundo
- **THEN** el segundo no muestra la firma del primero

#### Scenario: un firmante sin firma no bloquea el informe

- **GIVEN** un firmante declarado sin trazo registrado
- **WHEN** se exporta el informe
- **THEN** su bloque sale con la línea de firma vacía, su nombre y su cargo

#### Scenario: la firma viaja en el export

- **GIVEN** una firma registrada
- **WHEN** se genera el HTML exportado
- **THEN** el trazo va embebido como imagen en base64, sin referencias a
  archivos externos

### Requirement: sección propia para las firmas, condicionada al perfil

El informe SHALL agrupar la tarjeta de firmas bajo su propio rótulo de
sección, «04 · Aprobación del informe», al mismo nivel que «Marco
contractual», «Operación del período» y «Seguimiento del servicio».

Un rótulo de sección MAY declarar de qué tarjetas depende. Cuando lo hace,
SHALL mostrarse solo si el perfil activo selecciona al menos una de ellas, y
SHALL desaparecer del HTML exportado cuando el podado se lleva todas.

La dependencia se declara como dato en el marcado (una lista de
identificadores), no como comportamiento: el motor aplica la misma regla a
cualquier sección que la use.

#### Scenario: Bancoldex ve la sección de aprobación

- **GIVEN** el perfil `bancoldex`, que selecciona `c14`
- **WHEN** se renderiza el informe
- **THEN** el rótulo «04 · Aprobación del informe» encabeza la tarjeta de
  firmas

#### Scenario: un perfil que no firma no ve la sección

- **GIVEN** el perfil `accion-fiduciaria`, que no selecciona `c14`
- **WHEN** se renderiza el informe
- **THEN** el rótulo no aparece, y el informe conserva sus tres secciones
  sin ninguna cabecera vacía

#### Scenario: el rótulo no viaja en un entregable sin sus tarjetas

- **GIVEN** un perfil que no selecciona ninguna tarjeta de la sección
- **WHEN** se genera el HTML exportado
- **THEN** el rótulo se elimina del entregable, no viaja oculto

### Requirement: la tarjeta de firmas usa el formato compacto

La tarjeta `c14` SHALL presentarse con el formato compacto de una sola
columna, no con el de ancho completo reservado a las tarjetas de varios
campos (`dash-grid--full`).

#### Scenario: el resumen no se solapa

- **GIVEN** `c14` renderizada en su sección
- **WHEN** se observa su resumen colapsado
- **THEN** la etiqueta, el valor y la nota se apilan sin solaparse, como en
  las demás tarjetas de un solo dato

### Requirement: el entregable solo contiene las tarjetas seleccionadas

El HTML exportado SHALL contener únicamente las tarjetas que el perfil
activo selecciona. Una tarjeta del inventario que el perfil no selecciona
SHALL quedar fuera del entregable, no solo oculta.

#### Scenario: una tarjeta de otro cliente no viaja en el entregable

- **GIVEN** el perfil `accion-fiduciaria`, que no selecciona `c3b` ni `c14`
- **WHEN** se exporta el informe a HTML
- **THEN** el entregable no contiene sus nodos, y el A/B contra `main` da
  cero diferencias

#### Scenario: la tarjeta seleccionada sí viaja

- **GIVEN** el perfil `bancoldex`, que sí selecciona `c3b` y `c14`
- **WHEN** se exporta el informe a HTML
- **THEN** el entregable conserva ambas tarjetas con su diapositiva

#### Scenario: una tarjeta desactivada desde la interfaz

- **GIVEN** una tarjeta del preset desactivada en el selector de composición
- **WHEN** se exporta el informe a HTML
- **THEN** tampoco viaja en el entregable

## MODIFIED Requirements

### Requirement: detalle de mitigaciones según las columnas del perfil

La tarjeta `c8m` SHALL pintar responsable, fecha de entrega, observaciones y
avance **únicamente** cuando el perfil activo declare esas columnas en su
fuente cualitativa. Un perfil que no las declare SHALL renderizar el mismo
marcado que antes de este cambio.

#### Scenario: Bancoldex muestra el cuadro completo

- **GIVEN** el perfil `bancoldex`, cuya hoja `Mitigación` trae `RESPONSABLE`,
  `FECHA ENTREGA`, `OBSERVACIONES` y `ESTADO`, declaradas en el perfil
- **WHEN** se carga el libro mensual y se renderiza `c8m`
- **THEN** cada registro muestra hallazgo, mitigación, responsable, fecha de
  entrega, observaciones y el avance como porcentaje

#### Scenario: Acción Fiduciaria no cambia

- **GIVEN** el perfil `accion-fiduciaria`, cuyo libro trae una sola hoja con
  `Cliente · Descripción · Dato / evidencia` y que no declara columnas de
  mitigación
- **WHEN** se carga su libro mensual y se renderiza `c8m`
- **THEN** el marcado resultante es idéntico al anterior a este cambio, sin
  columnas vacías ni encabezados nuevos

#### Scenario: columna declarada que la fuente no trae

- **GIVEN** un perfil que declara una columna ausente en el archivo del mes
- **WHEN** se renderiza `c8m`
- **THEN** esa columna se omite en lugar de pintarse vacía, y el resto del
  registro se muestra con normalidad

### Requirement: el entregable exportado conserva la interacción

El HTML exportado SHALL permitir abrir cada tarjeta seleccionada y ver su
panel de detalle, sin depender de estado que no sobreviva al clonado del
DOM (listeners, propiedades de nodo) ni de nodos que el propio podado
elimina.

#### Scenario: cada tarjeta del entregable abre su panel

- **GIVEN** un informe exportado de cualquier perfil
- **WHEN** se hace clic en el resumen de una tarjeta seleccionada
- **THEN** se abre su panel con el contenido del periodo, sin errores en
  consola

#### Scenario: un perfil que hereda abre su entregable

- **GIVEN** un perfil con `extiende` declarado, como `bancoldex` o
  `novaventa`
- **WHEN** se abre su HTML exportado, sin los archivos de `perfiles/`
- **THEN** el informe arranca con el perfil ya resuelto que viaja en el
  estado, sin intentar cargar el perfil padre

#### Scenario: los scripts de autoría no abortan el entregable

- **GIVEN** un entregable del que el podado eliminó el panel de carga
  (`#loadPanel`, y con él `#loadSummary`)
- **WHEN** se abre y la cadena `restaurarPresetTarjetas()` →
  `aplicarPresetTarjetas()` → `actualizarResumen()` alcanza esa función
- **THEN** la función devuelve sin escribir, en vez de lanzar un `TypeError`
  que aborte el script y deje el informe inerte

#### Scenario: exportar con una tarjeta abierta

- **GIVEN** una tarjeta abierta en su modal en el momento de exportar
- **WHEN** se genera el HTML
- **THEN** el entregable conserva ese panel en su tarjeta y no lleva el
  modal de la sesión de autoría

## MODIFIED Requirements
