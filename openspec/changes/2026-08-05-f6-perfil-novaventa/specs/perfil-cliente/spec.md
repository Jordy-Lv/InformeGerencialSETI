## ADDED Requirements

### Requirement: perfil Novaventa por herencia declarada

El motor SHALL registrar `novaventa` como perfil que extiende
`accion-fiduciaria` y SHALL resolver sus sobrescrituras sin funciones propias.

#### Scenario: resolver Novaventa

- **GIVEN** los perfiles Acción Fiduciaria y Novaventa cargados
- **WHEN** el motor resuelve `novaventa`
- **THEN** conserva las fuentes compartidas y usa el filtro GLPI Novaventa

### Requirement: bloque histórico de indicadores

El lector de Indicadores SHALL usar `bloque-con-fechas` cuando así lo declare
el perfil y SHALL rechazar un bloque de metas que no tenga fechas.

#### Scenario: metas antes del histórico

- **GIVEN** la hoja Indicadores real de Novaventa con metas en las filas 2–5 y
  serie histórica desde la fila 7
- **WHEN** se carga el consolidado
- **THEN** la serie se deriva exclusivamente de la fila de cabecera histórica
