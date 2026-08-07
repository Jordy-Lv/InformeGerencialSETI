# Preset de tarjetas

## Requirements

### Requirement: selección local de tarjetas

El motor SHALL resolver el preset local válido sobre la selección por defecto
del perfil y SHALL conservar el orden definido por el inventario.

#### Scenario: deseleccionar bolsa de horas

- **GIVEN** el preset predeterminado de Acción Fiduciaria
- **WHEN** el consultor deselecciona `c9` y confirma el selector
- **THEN** desaparecen su tarjeta y su página exportable, sin alterar las
  cifras de las tarjetas restantes

#### Scenario: preset almacenado inválido

- **GIVEN** un valor local que contiene un id desconocido o repetido
- **WHEN** se abre el informe
- **THEN** el motor lo descarta y usa el preset predeterminado del perfil

### Requirement: exportación con selección resuelta

El exportado SHALL transportar la selección efectiva dentro del perfil
resuelto y SHALL incluir en el PDF únicamente las páginas exportables de esa
selección, además de las páginas fijas del informe.

#### Scenario: restaurar el predeterminado

- **GIVEN** un preset local que excluyó una tarjeta
- **WHEN** el consultor restaura el predeterminado
- **THEN** el HTML y el PDF vuelven a incluir la tarjeta, y la exportación de
  Acción Fiduciaria con el preset predeterminado conserva equivalencia A/B
