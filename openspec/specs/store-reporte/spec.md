# Store del reporte

## Requirements

### Requirement: dominios inicializados con estado explícito

El store `REPORTE` SHALL mantener los dominios `casos`, `alertas`, `glpi`,
`disponibilidad`, `backups`, `indicadores`, `ci`, `logros`, `mitigaciones` y
`bolsa`, e SHALL inicializar cada uno con `estado: no_cargado`, `datos: null`,
`fuente: null` y `notas: []`.

#### Scenario: sesión nueva sin insumos

- **GIVEN** una apertura de la plantilla sin estado exportado
- **WHEN** se crea `REPORTE`
- **THEN** los diez dominios existen y ninguno publica una cifra

### Requirement: publicación validada por dominio y estado

`REPORTE.publicar()` SHALL aceptar únicamente dominios registrados y los
estados `no_cargado`, `valido`, `sin_registros_confirmado`, `advertencia` e
`invalido`; SHALL rechazar cualquier otro nombre antes de mutar el dominio.

#### Scenario: publicación válida

- **GIVEN** el dominio `glpi` inicializado
- **WHEN** se publica con `estado: valido`, datos, fuente y notas
- **THEN** `REPORTE.d('glpi')` devuelve esos cuatro campos

#### Scenario: dominio desconocido

- **GIVEN** el store inicializado
- **WHEN** se intenta publicar el dominio `inventado`
- **THEN** la operación lanza `Dominio desconocido` y ningún dominio cambia

#### Scenario: estado desconocido

- **GIVEN** el dominio `glpi` inicializado
- **WHEN** se intenta publicar con `estado: supuesto`
- **THEN** la operación lanza `Estado inválido` y `glpi` conserva su valor

### Requirement: diferencia entre cifra, cero confirmado y fallo

`REPORTE.cifra(dominio)` SHALL ser verdadero solamente para `valido` y
`advertencia`; `REPORTE.resuelto(dominio)` SHALL ser verdadero para esos dos
estados y para `sin_registros_confirmado`, y SHALL ser falso para
`no_cargado` e `invalido`.

#### Scenario: tabla completa de estados

- **GIVEN** un dominio publicado sucesivamente en cada estado permitido
- **WHEN** se consultan `cifra()` y `resuelto()`
- **THEN** sus resultados coinciden con la semántica definida sin convertir
  un insumo inválido en cero ni un cero confirmado en cifra

### Requirement: notificaciones agrupadas y aisladas

El store SHALL agrupar todas las publicaciones síncronas de un mismo turno en
una sola notificación asíncrona a sus suscriptores, y SHALL continuar
notificando a los demás cuando un suscriptor lance una excepción.

#### Scenario: varias publicaciones en el mismo turno

- **GIVEN** un suscriptor que cuenta notificaciones
- **WHEN** se publican `glpi`, `alertas` y `casos` sin ceder el turno
- **THEN** el suscriptor recibe una sola notificación en la siguiente
  microtarea y observa los tres dominios actualizados

#### Scenario: un suscriptor falla

- **GIVEN** un primer suscriptor que lanza una excepción y un segundo que
  registra la llamada
- **WHEN** el store notifica un cambio
- **THEN** el error se registra y el segundo suscriptor también es invocado

### Requirement: cambio de periodo invalida los datos anteriores

Al cambiar a una firma de periodo distinta, `aplicarPeriodo()` SHALL devolver
todos los dominios a `no_cargado`, vaciar las reconciliaciones y retirar las
confirmaciones manuales de logros y mitigaciones antes de revalidar insumos.

#### Scenario: pasar de junio a julio

- **GIVEN** dominios resueltos y confirmaciones manuales para junio
- **WHEN** se aplica julio
- **THEN** ningún dominio de junio sigue publicable, no quedan
  reconciliaciones y ambas confirmaciones quedan en falso

### Requirement: rehidratación síncrona del entregable

Cuando `window.__INFORME_CLIENTE__` y `window.__ESTADO__` existan, el motor
SHALL rehidratar periodo, dominios conocidos, reconciliaciones y
`DATA_CASOS` durante la evaluación del script, antes de cualquier manejador
del evento `load`; los campos ausentes de un dominio SHALL tomar los valores
de `VACIO`.

#### Scenario: abrir un HTML exportado

- **GIVEN** un estado embebido con `glpi` resuelto y sin campo `fuente`
- **WHEN** el navegador evalúa el motor
- **THEN** `glpi` está resuelto con `fuente: null` antes de que los modales se
  rendericen después de `load`

#### Scenario: falta la marca de informe cliente

- **GIVEN** `window.__ESTADO__` sin `window.__INFORME_CLIENTE__`
- **WHEN** se evalúa el motor
- **THEN** el store conserva su estado inicial y no adopta el snapshot

### Requirement: vistas concordantes con el store

Las tarjetas, modales y gráficas SHALL derivar sus cifras publicadas del
dominio correspondiente en `REPORTE` y SHALL NOT afirmar cifras en una sesión
sin insumos.

#### Scenario: casos cargados

- **GIVEN** el dominio `casos` resuelto
- **WHEN** se renderizan la tarjeta, el modal y la gráfica de casos
- **THEN** el total y las series coinciden con `REPORTE.d('casos').datos`

#### Scenario: sesión en frío

- **GIVEN** todos los dominios en `no_cargado`
- **WHEN** se renderizan las tarjetas
- **THEN** ninguna muestra porcentajes ni un chip que afirme `Cumple`
