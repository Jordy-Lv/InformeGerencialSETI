## ADDED Requirements

### Requirement: perfil base sin cliente concreto

El sistema SHALL registrar un perfil `base` con `extiende: null` que no
representa a ningún cliente, para que perfiles sin evidencia de parentesco
suficiente con un cliente existente puedan extenderlo directamente.

#### Scenario: Bancóldex extiende base

- **GIVEN** el perfil `bancoldex` con `extiende: 'base'`
- **WHEN** el motor llama `resolverPerfil('bancoldex')`
- **THEN** el resultado incluye los valores de `base` fusionados con los
  propios de `bancoldex`, y no depende de ningún dato de `accion-fiduciaria`
  ni de `novaventa`
