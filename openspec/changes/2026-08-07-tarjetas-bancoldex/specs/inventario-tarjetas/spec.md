## ADDED Requirements

### Requirement: tarjeta de control de línea base

El inventario SHALL incluir una tarjeta `c13` que presente la comparación
entre la línea base contratada y la vigente, con la diferencia por
categoría, a partir de cifras declaradas por el perfil y sin requerir
ningún insumo cargado.

#### Scenario: Bancoldex declara su control de línea base

- **GIVEN** el perfil `bancoldex` con `lineaBase.control` declarado y `c13`
  en `tarjetas.seleccionadas`
- **WHEN** se renderiza el informe sin haber cargado ningún insumo
- **THEN** `c13` muestra el total base, el total actual y la diferencia, sin
  quedar en estado «Pendiente de cargar»

#### Scenario: el detalle vive en el modal

- **GIVEN** `c13` renderizada con su ficha declarada
- **WHEN** se abre la tarjeta
- **THEN** el modal lista cada tipo de infraestructura con su base, su valor
  actual y su diferencia, agrupados por ambiente

#### Scenario: un perfil que no la declara no la muestra

- **GIVEN** un perfil sin `lineaBase.control` y sin `c13` en
  `tarjetas.seleccionadas`
- **WHEN** se resuelven las tarjetas del perfil
- **THEN** `c13` no aparece en el informe ni en el HTML exportado

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
