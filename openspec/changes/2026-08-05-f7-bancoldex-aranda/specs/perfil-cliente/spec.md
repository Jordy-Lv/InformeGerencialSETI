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

### Requirement: configuración funcional de tarjeta por perfil

El motor SHALL permitir que un perfil sobrescriba declarativamente los
dominios, fuentes y criterios de una tarjeta compartida, además de su
presentación, sin incluir funciones en el archivo del perfil.

#### Scenario: Bancóldex reutiliza c5 con Aranda

- **GIVEN** `bancoldex` configura `c5` con dominio `casos`, fuente física
  `glpi` y criterio Aranda resuelto
- **WHEN** se resuelven las tarjetas del perfil
- **THEN** `c5` usa la misma tarjeta y el mismo modal compartido, pero valida
  el export Aranda como su única fuente de casos

### Requirement: preset respaldado por evidencia del corte

El perfil Bancóldex SHALL seleccionar únicamente tarjetas respaldadas por el
PDF aprobado y los insumos originales del periodo, y SHALL excluir fuentes
desactualizadas o pertenecientes a otro periodo.

#### Scenario: preset final de junio de 2026

- **GIVEN** el consolidado, Aranda y libro cualitativo originales
- **WHEN** se resuelve `PERFIL_BANCOLDEX.tarjetas.seleccionadas`
- **THEN** el resultado es `c3, c4, c5, c7, c8, c8m`; no incluye `c6/c11`
  (disponibilidad hasta jun-25), `c9` (TYA sep-25) ni `c12` (sin insumo
  exportable)

### Requirement: salida Bancóldex autocontenida

El HTML de cliente SHALL rehidratar desde su estado embebido el periodo, los
agregados de casos, indicadores, backups, logros y mitigaciones antes de
pintar tarjetas y gráficas, sin depender de IndexedDB ni de los libros fuente.

#### Scenario: apertura del HTML exportado sin Excel

- **GIVEN** un informe Bancóldex exportado después de cargar las tres fuentes
  obligatorias
- **WHEN** el cliente abre el HTML sin servidor ni archivos Excel vecinos
- **THEN** observa junio de 2026 y las mismas cifras y gráficas aprobadas en
  autoría
