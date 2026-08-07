## ADDED Requirements

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
