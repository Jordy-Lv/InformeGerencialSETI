# Delta — perfil de cliente

## ADDED Requirements

### Requirement: inicio contractual declarado por perfil

El motor SHALL obtener el límite inicial de los históricos desde
`PERFIL.contrato.inicio`, expresado como fecha calendario ISO `AAAA-MM-DD`, y
SHALL usarlo sin leer `[data-k="finicio"]`.

#### Scenario: inicio de Acción Fiduciaria

- **GIVEN** el perfil `accion-fiduciaria` con `contrato.inicio = 2025-09-01`
- **WHEN** el pipeline limita los históricos contractuales
- **THEN** cada recorrido usa el 1 de septiembre de 2025 como límite inferior
  y no consulta el nodo visual de inicio

### Requirement: contrato incompleto falla explícitamente

El motor SHALL validar `PERFIL.contrato.inicio` al arrancar y SHALL fallar con
un mensaje que identifique ese campo cuando falte, tenga formato inválido o
no represente un día calendario válido.

#### Scenario: perfil sin inicio contractual

- **GIVEN** un perfil resuelto sin `contrato.inicio`
- **WHEN** el motor inicia
- **THEN** el arranque se detiene con un error que menciona `contrato.inicio`
  y no sustituye una fecha por defecto

### Requirement: equivalencia contractual de Acción Fiduciaria

La migración SHALL conservar las cifras, textos y comportamiento visibles del
export de Acción Fiduciaria respecto de `main`.

#### Scenario: comparación con los mismos insumos

- **GIVEN** exportaciones completas de `main` y de la rama producidas con los
  mismos insumos y periodo
- **WHEN** se ejecuta `automatizacion/verificar_ab.py`
- **THEN** el comando informa cero diferencias y termina con código 0
