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
