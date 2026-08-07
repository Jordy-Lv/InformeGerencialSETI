## ADDED Requirements

### Requirement: casos normalizados por adaptador

El motor SHALL convertir las filas de GLPI y AlertsList en objetos
`CasoCanonico` antes de calcular las métricas de casos de Acción Fiduciaria.
Cada caso SHALL incluir los campos de identidad, fecha, cliente, origen, tipo,
categoría, jerarquía, SLA, motor, ambiente y atribuibilidad; los valores
desconocidos SHALL conservarse como `null`.

#### Scenario: caso GLPI con SLA excedido

- **GIVEN** una fila GLPI válida con `Tiempo para resolver excedido = Sí`
- **WHEN** el adaptador normaliza la fila
- **THEN** el caso tiene `origen = glpi-export`, tipo clasificado y
  `slaCumplido = false`

### Requirement: SLA tri-valuado conservador

Al calcular cumplimiento, el motor SHALL contar únicamente
`slaCumplido === true` como caso cumplido. Un valor `null` SHALL NOT sumarse
como cumplimiento ni convertirse a `true` o `false`.

#### Scenario: SLA ausente

- **GIVEN** dos casos, uno con SLA cumplido y uno con SLA desconocido
- **WHEN** se calcula el número de casos cumplidos
- **THEN** el resultado es uno

### Requirement: encabezado sin ambigüedad

Para un adaptador con estrategia `primera-fila-con`, el motor SHALL enumerar
todas las filas candidatas. Si hay más de una, SHALL declarar inválida la
fuente y SHALL incluir los índices candidatos en la nota; SHALL NOT elegir una
fila por orden.

#### Scenario: dos filas candidatas

- **GIVEN** una matriz con dos filas que contienen todos los campos requeridos
- **WHEN** el adaptador resuelve su encabezado
- **THEN** falla con ambos índices y el dominio queda `invalido`

### Requirement: fuentes alternativas declaradas

El perfil SHALL expresar la precedencia y ámbito de los orígenes alternativos
de alertas. El motor SHALL escoger el origen aplicable de mayor precedencia y
SHALL registrar discrepancias solo en `REPORTE.reconciliaciones`.

#### Scenario: AlertsList en el mes en curso

- **GIVEN** AlertsList y consolidado disponibles para el mismo periodo actual
- **WHEN** se resuelve el origen de alertas
- **THEN** AlertsList es el origen efectivo y cualquier diferencia queda como
  reconciliación interna
