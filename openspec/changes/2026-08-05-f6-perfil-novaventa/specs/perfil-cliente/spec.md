## ADDED Requirements

### Requirement: perfil Novaventa por herencia declarada

El motor SHALL registrar `novaventa` como perfil que extiende
`accion-fiduciaria` y SHALL resolver sus sobrescrituras sin funciones propias.

#### Scenario: resolver Novaventa

- **GIVEN** los perfiles Acción Fiduciaria y Novaventa cargados
- **WHEN** el motor resuelve `novaventa`
- **THEN** conserva las fuentes compartidas y usa el filtro GLPI Novaventa

### Requirement: bloque histórico de indicadores

El lector de Indicadores SHALL usar `bloque-con-fechas` cuando así lo declare
el perfil y SHALL rechazar un bloque de metas que no tenga fechas.

#### Scenario: metas antes del histórico

- **GIVEN** la hoja Indicadores real de Novaventa con metas en las filas 2–5 y
  serie histórica desde la fila 7
- **WHEN** se carga el consolidado
- **THEN** la serie se deriva exclusivamente de la fila de cabecera histórica

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
