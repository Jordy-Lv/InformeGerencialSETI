# Capacidad — perfil de cliente

## Requirements

### Requirement: perfil como datos puros

El sistema SHALL representar cada perfil de cliente como un objeto serializable
sin funciones y SHALL identificarlo mediante un `id` estable.

#### Scenario: perfil de Acción Fiduciaria conforme

- **GIVEN** el archivo `perfiles/accion-fiduciaria.js`
- **WHEN** se inspecciona el objeto publicado
- **THEN** su id es `accion-fiduciaria` y no contiene funciones

### Requirement: resolución explícita del perfil

El motor SHALL resolver el perfil activo mediante un registro por id, SHALL
reutilizar `fusionarProfundo()` para la herencia y SHALL fallar explícitamente
cuando el id no esté registrado o sus datos no estén disponibles.

#### Scenario: id registrado

- **GIVEN** el perfil `accion-fiduciaria` cargado
- **WHEN** el motor llama `resolverPerfil('accion-fiduciaria')`
- **THEN** obtiene el objeto con ese mismo id

#### Scenario: id desconocido

- **GIVEN** un id que no figura en el registro
- **WHEN** se intenta resolverlo
- **THEN** el motor lanza un error que incluye el id y los perfiles registrados

### Requirement: entregable autocontenido

El exportador SHALL incluir el perfil resuelto dentro de `window.__ESTADO__` y
SHALL eliminar del HTML entregado toda dependencia al archivo de perfil vecino.

#### Scenario: export abierto fuera del proyecto

- **GIVEN** una sesión de autoría que cargó `perfiles/accion-fiduciaria.js`
- **WHEN** se genera el HTML interactivo
- **THEN** el estado contiene `perfil.id = accion-fiduciaria` y el documento
  exportado no contiene un `script src` hacia `perfiles/`

### Requirement: almacenamiento compatible por perfil

El motor SHALL construir las claves nuevas de posiciones y bolsa con el id del
perfil y SHALL conservar la lectura de las claves históricas de Acción
Fiduciaria cuando la clave nueva no exista.

#### Scenario: existe una posición con clave nueva

- **GIVEN** valores bajo las claves nueva e histórica de posiciones
- **WHEN** se restaura la posición
- **THEN** se usa el valor de la clave nueva

#### Scenario: solo existe una bolsa histórica

- **GIVEN** que no existe bolsa bajo la clave nueva y sí bajo
  `informeAF:bolsa:<periodo>`
- **WHEN** se restaura la bolsa del periodo
- **THEN** se recupera el valor histórico sin reescribirlo

### Requirement: textos de interfaz derivados del perfil

El motor SHALL obtener del perfil activo los textos de presentación y los
metadatos de exportación que identifican al cliente.

#### Scenario: hidratación de Acción Fiduciaria

- **GIVEN** el perfil `accion-fiduciaria` resuelto
- **WHEN** se evalúa el motor en modo autoría
- **THEN** el título, la marca y el cliente de portada se hidratan desde
  `PERFIL.textos`, y los nombres de los entregables conservan el valor
  histórico configurado en `PERFIL.textos.nombreArchivo`

### Requirement: equivalencia de Acción Fiduciaria

La migración del perfil SHALL conservar todas las cifras, textos y
comportamientos visibles del export de Acción Fiduciaria respecto de `main`.

#### Scenario: comparación con insumos reales idénticos

- **GIVEN** exportaciones completas de `main` y de la rama producidas con los
  mismos insumos y periodo
- **WHEN** se ejecuta `automatizacion/verificar_ab.py`
- **THEN** el comando informa cero diferencias y termina con código 0
