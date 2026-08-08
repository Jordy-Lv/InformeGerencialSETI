# Delta — store del reporte

## MODIFIED Requirements

### Requirement: dominios inicializados con estado explícito

El store `REPORTE` SHALL derivar sus dominios de las tarjetas resueltas del
perfil e SHALL inicializar cada uno con `estado: no_cargado`, `datos: null`,
`fuente: null` y `notas: []`.

#### Scenario: sesión nueva de Acción Fiduciaria sin insumos

- **GIVEN** el perfil de Acción Fiduciaria y sus diez tarjetas seleccionadas
- **WHEN** se crea `REPORTE`
- **THEN** existen `casos`, `alertas`, `glpi`, `disponibilidad`, `backups`,
  `indicadores`, `ci`, `logros`, `mitigaciones` y `bolsa`, y ninguno publica
  una cifra
