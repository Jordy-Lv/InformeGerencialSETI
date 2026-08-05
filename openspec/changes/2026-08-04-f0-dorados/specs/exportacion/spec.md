# Delta — exportación

## ADDED Requirements

### Requirement: creación de dorado por cliente y periodo

El arnés A/B SHALL crear un archivo
`dorados/<cliente>-<AAAA-MM>.json` determinista a partir de un HTML exportado
que contenga `window.__ESTADO__`.

#### Scenario: export válido crea un dorado reproducible

- **GIVEN** un HTML exportado con periodo junio de 2026
- **WHEN** se crea dos veces el dorado para `accion-fiduciaria` y `2026-06`
- **THEN** ambos contenidos JSON son idénticos byte a byte

#### Scenario: la etiqueta de periodo no coincide

- **GIVEN** un HTML exportado cuyo estado corresponde a julio de 2026
- **WHEN** se intenta crear el dorado `accion-fiduciaria-2026-06.json`
- **THEN** el comando falla sin escribir el dorado

#### Scenario: la plantilla editable no es un export

- **GIVEN** un HTML sin `window.__ESTADO__`
- **WHEN** se intenta crear un dorado
- **THEN** el comando falla sin escribir el dorado

### Requirement: el dorado no expone datos reales

El dorado SHALL almacenar solamente metadatos de identidad, conteos y
huellas SHA-256 de los componentes comparados; SHALL NOT almacenar en claro
el estado ni los textos visibles extraídos.

#### Scenario: los valores sintéticos no aparecen en el JSON

- **GIVEN** un export sintético que contiene el KPI `54 casos` y el contrato
  `CN-SINTETICO-001`
- **WHEN** se crea su dorado
- **THEN** ninguno de esos valores aparece en el archivo JSON

### Requirement: verificación exacta contra un dorado

El arnés A/B SHALL comparar un HTML exportado contra todos los componentes
del dorado y SHALL devolver éxito únicamente cuando sus huellas y conteos
coincidan.

#### Scenario: export idéntico al dorado

- **GIVEN** un dorado creado desde un export sintético
- **WHEN** se verifica el mismo export contra el dorado
- **THEN** el comando informa cero diferencias y termina con código 0

#### Scenario: una cifra visible cambia

- **GIVEN** un dorado creado con `54 casos`
- **WHEN** se verifica un export equivalente con `999 casos`
- **THEN** el comando identifica los componentes distintos y termina con
  código 1

### Requirement: reemplazo explícito de referencias

El arnés A/B SHALL rechazar la sobrescritura de un dorado existente salvo
que el operador solicite explícitamente su reemplazo.

#### Scenario: creación accidental sobre un dorado existente

- **GIVEN** un dorado que ya existe
- **WHEN** se vuelve a ejecutar la creación sin la opción de reemplazo
- **THEN** el comando falla y conserva intacto el archivo existente
