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

### Requirement: capacidad independiente de la bolsa manual

El motor SHALL publicar la ocupación de capacidad declarada en el perfil bajo
el dominio `capacidad`, sin escribir ni derivar datos en el dominio `bolsa`.

#### Scenario: hoja Capacidad de Novaventa

- **GIVEN** el perfil Novaventa declara la hoja `Capacidad` con las columnas
  Cliente y Tipo CI
- **WHEN** se carga el consolidado para junio de 2026
- **THEN** publica las ocupaciones de `/db2dta1` y `/db2dta2` en `capacidad`
  y conserva `bolsa` como dato manual independiente

### Requirement: guía de carga declarada por perfil

El motor SHALL permitir que un perfil declare ayudas para los insumos cuando
su formato tenga un destino distinto al rótulo heredado.

#### Scenario: Data de Novaventa no se carga como consolidado

- **GIVEN** el perfil Novaventa activo
- **WHEN** el consultor abre el centro de carga
- **THEN** la ayuda identifica la plantilla mensual como consolidado y
  `Data_<mes>.xlsx` como fuente alternativa de alertas

#### Scenario: Data con tabla dinámica al final

- **GIVEN** un `Data_<mes>` con un bloque de alertas seguido de filas vacías y
  una tabla dinámica de resumen
- **WHEN** se carga como fuente alternativa
- **THEN** se procesan únicamente las filas del bloque de alertas y el resumen
  no se interpreta como casos sin fecha

#### Scenario: Data fuera del corte seleccionado

- **GIVEN** un `Data_<mes>` con alertas válidas, pero ninguna del periodo del
  informe seleccionado
- **WHEN** se procesa la fuente alternativa
- **THEN** el dominio conserva la cifra certificada de la hoja `Casos`, si
  existe, registra las filas excluidas y advierte que se debe cargar el corte
  correspondiente; si no existe ese respaldo, bloquea la exportación

### Requirement: disponibilidad por tabla declarada del perfil

Un perfil SHALL poder declarar la tabla de disponibilidad que contiene su
corte vigente cuando la primera hoja homónima contenga únicamente histórico.

#### Scenario: Novaventa obtiene disponibilidad de junio de su tabla real

- **GIVEN** el perfil Novaventa y su consolidado con `Disponibilidad Real` en
  `Grafica Dispo y Gestion`
- **WHEN** se carga el corte de junio de 2026
- **THEN** el informe publica la disponibilidad y los CIs desde esa tabla, no
  desde la matriz histórica que termina en junio de 2025

### Requirement: taxonomía de indicadores declarada por perfil

El perfil SHALL declarar los alias de sus indicadores contractuales cuando el
nombre de la fuente difiera del de otro cliente.

#### Scenario: tiempos de Atención de Novaventa

- **GIVEN** el perfil Novaventa con el alias `Cumplimiento tiempos de Atención`
- **WHEN** se carga la tabla Indicadores de junio de 2026
- **THEN** el lector lo reconoce como Gestión del Servicio junto con
  Disponibilidad y Entregables, y valida tres métricas del periodo

### Requirement: registro persistente de clientes personalizados

El motor SHALL permitir registrar y resolver perfiles personalizados desde el
HTML offline, SHALL guardar únicamente datos serializables por cliente en un
registro local versionado y SHALL mantener separados los perfiles base.

#### Scenario: nuevo cliente desde plantilla

- **GIVEN** un usuario que registra un cliente con la plantilla Novaventa
- **WHEN** guarda su nombre, la plantilla y la fecha inicial contractual
- **THEN** el administrador de clientes incluye el nuevo cliente, su perfil extiende Novaventa
  y la configuración queda disponible tras recargar el HTML en el mismo
  navegador

### Requirement: alta guiada sin duplicar información mensual

El administrador SHALL pedir durante el alta únicamente la identidad, la
plantilla de lectura y el dato contractual que no puede inferirse de los
insumos mensuales; SHALL obtener indicadores, metas, disponibilidad, backups
y casos desde los insumos cargados, y no SHALL precargar datos de negocio de
la plantilla elegida como si pertenecieran al cliente nuevo.

#### Scenario: creación desde Novaventa

- **GIVEN** que el usuario crea un cliente usando la plantilla Novaventa
- **WHEN** se abre su formulario de alta
- **THEN** no aparecen como campos obligatorios el alcance, instancias, metas
  ni una matriz de tarjetas; el formulario explica que esos resultados se
  interpretan desde los archivos y dirige la personalización de tarjetas al
  selector posterior

### Requirement: validaciones derivadas de una plantilla explícita

Un cliente personalizado SHALL declarar una plantilla base para sus insumos y
el sistema SHALL limitar su preset a las tarjetas compatibles con esa
plantilla; no SHALL aceptar código, lectores ni reglas arbitrarias en el
registro local.

#### Scenario: tarjeta incompatible

- **GIVEN** un cliente que usa la plantilla Acción Fiduciaria
- **WHEN** se intenta guardar una tarjeta que la plantilla no declara
- **THEN** el sistema rechaza la configuración y conserva las fuentes y
  validaciones declaradas por la plantilla

### Requirement: administrador guiado sin pérdida de estado

El administrador SHALL identificar el cliente activo desde la barra superior,
SHALL exponer el estado abierto o cerrado de su diálogo a tecnologías de
asistencia y SHALL conservar los datos ya escritos cuando cambie la plantilla
de insumos. La explicación detallada de la plantilla SHALL estar disponible
mediante divulgación progresiva sin duplicar campos mensuales en el alta. El
control y el diálogo SHALL pertenecer solo a la sesión de autoría y no SHALL
aparecer en el HTML entregado al cliente. Los controles de la barra de autoría
SHALL compartir dimensiones compactas y no SHALL repetir una nota que explique
la acción ya nombrada por el botón **Editar datos**.

#### Scenario: cambiar la plantilla durante el alta

- **GIVEN** que el usuario ya escribió el nombre y las fechas contractuales
  de un cliente nuevo
- **WHEN** cambia el tipo de insumos entre Acción Fiduciaria y Novaventa
- **THEN** el nombre, las fechas y el foco se conservan, y solo se actualiza
  la explicación de la información que la automatización interpretará

#### Scenario: abrir y cerrar desde el control del cliente activo

- **GIVEN** el control de cliente activo en la barra de autoría
- **WHEN** el usuario abre y cierra el administrador
- **THEN** el control anuncia el estado expandido del diálogo y recupera el
  foco al cerrarlo

#### Scenario: exportar después de administrar clientes

- **GIVEN** que el administrador se creó durante la sesión de autoría
- **WHEN** se genera el HTML interactivo para el cliente
- **THEN** el exportador elimina tanto la barra de autoría como el diálogo de
  clientes antes de serializar el entregable

#### Scenario: barra de acciones uniforme

- **GIVEN** la barra de autoría visible en una pantalla de escritorio
- **WHEN** se presentan Cliente activo, Cargar informes, Editar datos,
  Tarjetas y los dos exportadores
- **THEN** todos los controles tienen el mismo ancho, alto y radio compactos,
  y no aparece una instrucción redundante junto a **Editar datos**

### Requirement: persistencia del preset en la ficha del cliente

Cuando se ajusta el selector de tarjetas para un cliente personalizado, el
motor SHALL persistir la selección tanto para la sesión como dentro de la
ficha del cliente, aislada de los demás perfiles.

#### Scenario: recarga del cliente

- **GIVEN** un cliente personalizado con una tarjeta retirada de su preset
- **WHEN** se recarga el HTML y se vuelve a seleccionar ese cliente
- **THEN** la tarjeta sigue retirada y los criterios de carga se derivan de su
  composición guardada

### Requirement: eliminación segura de clientes

El sistema SHALL permitir eliminar solo clientes personalizados, SHALL proteger
Acción Fiduciaria y Novaventa, y SHALL volver a la plantilla del cliente si se
elimina el perfil que está activo.

#### Scenario: eliminar cliente activo

- **GIVEN** un cliente personalizado activo que extiende Novaventa
- **WHEN** el usuario confirma su eliminación
- **THEN** se elimina su ficha y preset local, el administrador deja de mostrarlo y
  el informe vuelve a Novaventa sin modificar el perfil base

### Requirement: control de línea base declarado por el perfil

Un perfil SHALL poder declarar en `lineaBase.control` la comparación entre la
línea base contratada y la vigente, como datos puros y sin funciones: filas
con su etiqueta, su ambiente, su valor base y su valor actual. La diferencia
SHALL calcularla el motor, no el perfil.

#### Scenario: Bancoldex declara la ficha del entregable aprobado

- **GIVEN** `PERFIL_BANCOLDEX.lineaBase.control` con las filas del PDF
  aprobado de junio de 2026
- **WHEN** arranca el informe
- **THEN** el total base es 237, el total actual 257 y la diferencia +20,
  calculada por el motor a partir de las filas declaradas

#### Scenario: la diferencia no se declara

- **GIVEN** una fila que declara su diferencia además de base y actual
- **WHEN** se valida el perfil
- **THEN** el arranque falla con un mensaje que nombra la clave sobrante,
  en lugar de aceptar una cifra que puede contradecir a sus operandos

#### Scenario: perfil sin control de línea base

- **GIVEN** un perfil que no declara `lineaBase.control`
- **WHEN** arranca el informe
- **THEN** el perfil es válido y `c3b` no se ofrece

### Requirement: firmantes declarados por el perfil y editables

Un perfil SHALL poder declarar en `firmantes` la lista de personas que
aprueban el informe, cada una con nombre y cargo, como valor inicial
editable desde la interfaz. Un perfil SHALL NOT contener trazos de firma:
la firma es estado del cliente, no dato del perfil.

#### Scenario: Bancoldex declara sus tres firmantes

- **GIVEN** `PERFIL_BANCOLDEX.firmantes` con las tres personas del
  entregable aprobado
- **WHEN** se renderiza `c14` sin ninguna edición previa
- **THEN** aparecen los tres con el nombre y el cargo declarados

#### Scenario: la edición sobrevive al perfil

- **GIVEN** un firmante cuyo nombre se editó desde la interfaz
- **WHEN** se recarga el informe
- **THEN** prevalece el nombre editado, no el declarado en el perfil

#### Scenario: un perfil no transporta firmas

- **GIVEN** un perfil que declara un trazo de firma junto a un firmante
- **WHEN** se valida el perfil
- **THEN** el arranque falla nombrando la clave rechazada

### Requirement: columnas cualitativas declaradas por el perfil

Un perfil SHALL poder declarar en `fuentes.cualitativos.columnas` los
nombres de columna adicionales de su fuente de mitigaciones. Son datos
puros: nombres de columna que el lector existente ya sabe resolver.

#### Scenario: Bancoldex declara las cuatro columnas extra

- **GIVEN** `fuentes.cualitativos.columnas.mitigaciones` con `RESPONSABLE`,
  `FECHA ENTREGA`, `OBSERVACIONES` y `ESTADO`
- **WHEN** se carga la hoja `Mitigación` del libro mensual
- **THEN** el modelo canónico de cada registro incluye esos cuatro campos

#### Scenario: un perfil sin columnas declaradas conserva el modelo previo

- **GIVEN** un perfil que no declara `fuentes.cualitativos.columnas`
- **WHEN** se carga su libro mensual
- **THEN** cada registro conserva exactamente los campos que tenía antes de
  este cambio
