# Delta — Inventario de tarjetas

## MODIFIED Requirements

### Requirement: inventario declarativo de tarjetas

El motor SHALL mantener un inventario de tarjetas con id estable, identidad
legado, presentación, dominios, fuentes, exportabilidad, dependencias y
estrategias nombradas; SHALL resolver los ids del perfil sin funciones dentro
de este.

#### Scenario: descriptor listo para plantilla

- **GIVEN** una tarjeta seleccionada de Acción Fiduciaria
- **WHEN** el motor genera el panel
- **THEN** su descriptor aporta toda la identidad visual del resumen y conserva
  los ids legado de su tarjeta y diapositiva
