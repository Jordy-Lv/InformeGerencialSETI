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

### Requirement: presentación de tarjeta sobrescribible por perfil

El motor SHALL permitir que un perfil sobrescriba la presentación (resumen
colapsado: `items`, `valor`, `meta`, `chip`) de una tarjeta que selecciona,
mediante `PERFIL.tarjetas.presentacion`, sin alterar la lógica ni los datos
de esa tarjeta para otro perfil.

#### Scenario: Bancóldex no muestra la meta de Acción Fiduciaria

- **GIVEN** el perfil `bancoldex` selecciona `c6` y declara
  `tarjetas.presentacion.c6.meta`
- **WHEN** el dominio `disponibilidad` no tiene cifra (bloqueado o pendiente)
- **THEN** la tarjeta `c6` muestra la meta declarada por Bancóldex, no la
  meta de Acción Fiduciaria

#### Scenario: Acción Fiduciaria conserva su presentación exacta

- **GIVEN** el perfil `accion-fiduciaria`, que no declara
  `tarjetas.presentacion`
- **WHEN** se resuelven sus tarjetas
- **THEN** cada una conserva el `presentacion` original de
  `INVENTARIO_TARJETAS`, sin cambios

### Requirement: ficha contractual declarada por perfil

Un perfil SHALL poder declarar `PERFIL.lineaBase` con sus propios datos
contractuales comprobados. El motor SHALL presentarlos en la tarjeta de
línea base cuando existan, y SHALL conservar la ficha heredada de Acción
Fiduciaria cuando el perfil no declare `lineaBase`.

#### Scenario: Bancóldex presenta su propia línea base

- **GIVEN** el perfil `bancoldex` con `lineaBase.estadisticas` declarado
- **WHEN** se renderiza la tarjeta de línea base
- **THEN** muestra los datos de Bancóldex y no el código de contrato de
  Acción Fiduciaria

#### Scenario: Acción Fiduciaria sin declarar lineaBase

- **GIVEN** el perfil `accion-fiduciaria`, que no declara `lineaBase`
- **WHEN** se renderiza la tarjeta de línea base
- **THEN** conserva su ficha legado exacta, incluida la lectura desde los
  campos editables del DOM
