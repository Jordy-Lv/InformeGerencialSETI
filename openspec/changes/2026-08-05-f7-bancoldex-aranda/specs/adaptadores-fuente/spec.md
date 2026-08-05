## ADDED Requirements

### Requirement: casos de Aranda normalizados por adaptador

El motor SHALL convertir las filas del export manual de Aranda en objetos
`CasoCanonico` mediante un adaptador propio, sin usar ni modificar
`adaptarGlpiACanonico()`. El tipo SHALL derivarse de `TIPO_DE_CASO` y la
jerarquía SHALL separarse con `.`, no con `>`.

#### Scenario: caso Aranda con tipo Incidente - Monitoreo

- **GIVEN** una fila Aranda válida con `TIPO_DE_CASO = Incidente - Monitoreo`
  y `JERARQUIA = Base De Datos.Intermitencia`
- **WHEN** el adaptador normaliza la fila
- **THEN** el caso tiene `origen = aranda-export`, `tipo = incidente` y
  `jerarquia = ['Base De Datos', 'Intermitencia']`

### Requirement: SLA de Aranda por columna de cumplimiento

El motor SHALL ofrecer la estrategia `columna-cumplimiento` para fuentes que
declaran el cumplimiento directamente (no como excedido). `'Cumple'` SHALL
producir `true`, `'No cumple'` SHALL producir `false`, y cualquier otro valor
o celda vacía SHALL producir `null`.

#### Scenario: SLA vacío en Aranda

- **GIVEN** una fila Aranda con `INDICARDOR DE CUMPLIMIENTO` vacío
- **WHEN** el adaptador resuelve el SLA de esa fila
- **THEN** `slaCumplido` es `null` y `metricasSlaCanonico()` no la cuenta como
  cumplida ni como incumplida

### Requirement: identidad de cliente por archivo de alcance único

Un perfil SHALL poder declarar `filtroCliente.estrategia =
'archivo-alcance-unico'` cuando su fuente se entrega ya delimitada a ese
cliente. En ese caso el motor SHALL aceptar todas las filas sin aplicar un
filtro de columna.

#### Scenario: filas sin columna de compañía

- **GIVEN** un export Aranda donde 8 de 72 filas no tienen `COMPANIA`
- **WHEN** el perfil declara `archivo-alcance-unico`
- **THEN** las 72 filas se conservan como casos del cliente
