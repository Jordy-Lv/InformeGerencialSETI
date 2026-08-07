## ADDED Requirements

### Requirement: control de línea base declarado por el perfil

Un perfil SHALL poder declarar en `lineaBase.control` la comparación entre la
línea base contratada y la vigente, como datos puros y sin funciones: filas
con su etiqueta, su ambiente, su valor base y su valor actual. La diferencia
SHALL calcularla el motor, no el perfil.

#### Scenario: Bancoldex declara la ficha del entregable aprobado

- **GIVEN** `PERFIL_BANCOLDEX.lineaBase.control` con las filas del PDF
  aprobado de junio de 2026
- **WHEN** arranca el informe
- **THEN** el total base es 237, el total actual 257 y la diferencia +20,
  calculada por el motor a partir de las filas declaradas

#### Scenario: la diferencia no se declara

- **GIVEN** una fila que declara su diferencia además de base y actual
- **WHEN** se valida el perfil
- **THEN** el arranque falla con un mensaje que nombra la clave sobrante,
  en lugar de aceptar una cifra que puede contradecir a sus operandos

#### Scenario: perfil sin control de línea base

- **GIVEN** un perfil que no declara `lineaBase.control`
- **WHEN** arranca el informe
- **THEN** el perfil es válido y `c3b` no se ofrece

### Requirement: firmantes declarados por el perfil y editables

Un perfil SHALL poder declarar en `firmantes` la lista de personas que
aprueban el informe, cada una con nombre y cargo, como valor inicial
editable desde la interfaz. Un perfil SHALL NOT contener trazos de firma:
la firma es estado del cliente, no dato del perfil.

#### Scenario: Bancoldex declara sus tres firmantes

- **GIVEN** `PERFIL_BANCOLDEX.firmantes` con las tres personas del
  entregable aprobado
- **WHEN** se renderiza `c14` sin ninguna edición previa
- **THEN** aparecen los tres con el nombre y el cargo declarados

#### Scenario: la edición sobrevive al perfil

- **GIVEN** un firmante cuyo nombre se editó desde la interfaz
- **WHEN** se recarga el informe
- **THEN** prevalece el nombre editado, no el declarado en el perfil

#### Scenario: un perfil no transporta firmas

- **GIVEN** un perfil que declara un trazo de firma junto a un firmante
- **WHEN** se valida el perfil
- **THEN** el arranque falla nombrando la clave rechazada

### Requirement: columnas cualitativas declaradas por el perfil

Un perfil SHALL poder declarar en `fuentes.cualitativos.columnas` los
nombres de columna adicionales de su fuente de mitigaciones. Son datos
puros: nombres de columna que el lector existente ya sabe resolver.

#### Scenario: Bancoldex declara las cuatro columnas extra

- **GIVEN** `fuentes.cualitativos.columnas.mitigaciones` con `RESPONSABLE`,
  `FECHA ENTREGA`, `OBSERVACIONES` y `ESTADO`
- **WHEN** se carga la hoja `Mitigación` del libro mensual
- **THEN** el modelo canónico de cada registro incluye esos cuatro campos

#### Scenario: un perfil sin columnas declaradas conserva el modelo previo

- **GIVEN** un perfil que no declara `fuentes.cualitativos.columnas`
- **WHEN** se carga su libro mensual
- **THEN** cada registro conserva exactamente los campos que tenía antes de
  este cambio
