# Inventario de tarjetas

## Requirements

### Requirement: inventario declarativo de tarjetas

El motor SHALL mantener un inventario de tarjetas con id estable, identidad legado, dominios, fuentes, exportabilidad y estrategias nombradas; SHALL resolver los ids del perfil sin funciones dentro de este.

#### Scenario: perfil de Acción Fiduciaria

- **GIVEN** el perfil `accion-fiduciaria` con sus diez ids de tarjeta
- **WHEN** el motor resuelve el inventario
- **THEN** obtiene `c3`, `c4`, `c5`, `c6`, `c7`, `c8`, `c8m`, `c9`, `c11` y `c12` en ese orden y falla ante un id desconocido

### Requirement: listas operativas derivadas

El motor SHALL derivar dominios, extensiones admitidas, criterios de carga y renderizadores desde las tarjetas resueltas, sin una segunda lista fija.

#### Scenario: criterios de Acción Fiduciaria

- **GIVEN** las diez tarjetas del perfil de Acción Fiduciaria
- **WHEN** se calcula el estado de validación
- **THEN** se obtienen los siete criterios actuales en su orden y con su texto exacto

### Requirement: conformidad descriptor con interfaz legado

El motor SHALL comprobar que cada descriptor seleccionado corresponde a su tarjeta y diapositiva legado en el DOM antes de que F4 genere esa interfaz.

#### Scenario: inventario y DOM completos

- **GIVEN** el DOM actual de Acción Fiduciaria
- **WHEN** se ejecuta `REPORTE.autopruebas()` sin insumos
- **THEN** informa que las diez tarjetas declaradas tienen sus nodos de tarjeta y diapositiva, y que los criterios declarados permanecen en siete
