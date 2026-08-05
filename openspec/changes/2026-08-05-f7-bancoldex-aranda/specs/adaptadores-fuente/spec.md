## ADDED Requirements

### Requirement: casos de Aranda normalizados por adaptador

El motor SHALL convertir las filas del export manual de Aranda en objetos
`CasoCanonico` mediante un adaptador propio, sin usar ni modificar
`adaptarGlpiACanonico()`. El tipo SHALL derivarse de `TIPO_DE_CASO` y la
jerarquía SHALL separarse con `.`, no con `>`.

#### Scenario: caso Aranda con tipo Incidente - Monitoreo

- **GIVEN** una fila Aranda válida con `TIPO_DE_CASO = Incidente - Monitoreo`
  y `JERARQUIA = Base De Datos.Intermitencia`
- **WHEN** el adaptador normaliza la fila
- **THEN** el caso tiene `origen = aranda-export`, `tipo = incidente` y
  `jerarquia = ['Base De Datos', 'Intermitencia']`

### Requirement: SLA de Aranda por columna de cumplimiento

El motor SHALL ofrecer la estrategia `columna-cumplimiento` para fuentes que
declaran el cumplimiento directamente (no como excedido). `'Cumple'` SHALL
producir `true`, `'No cumple'` SHALL producir `false`, y cualquier otro valor
o celda vacía SHALL producir `null`.

#### Scenario: SLA vacío en Aranda

- **GIVEN** una fila Aranda con `INDICARDOR DE CUMPLIMIENTO` vacío
- **WHEN** el adaptador resuelve el SLA de esa fila
- **THEN** `slaCumplido` es `null` y `metricasSlaCanonico()` no la cuenta como
  cumplida ni como incumplida

### Requirement: identidad de cliente por archivo de alcance único

Un perfil SHALL poder declarar `filtroCliente.estrategia =
'archivo-alcance-unico'` cuando su fuente se entrega ya delimitada a ese
cliente. En ese caso el motor SHALL aceptar todas las filas sin aplicar un
filtro de columna.

#### Scenario: filas sin columna de compañía

- **GIVEN** un export Aranda donde 8 de 72 filas no tienen `COMPANIA`
- **WHEN** el perfil declara `archivo-alcance-unico`
- **THEN** las 72 filas se conservan como casos del cliente

### Requirement: entrada de casos enrutada por perfil

El motor SHALL despachar el archivo de la entrada de casos al adaptador de
Aranda cuando el perfil declara `fuentes.casos`, y a `cargarGlpi()` en caso
contrario, sin modificar `cargarGlpi()`.

#### Scenario: Bancóldex carga por la entrada de GLPI

- **GIVEN** el perfil `bancoldex`, que declara `fuentes.casos` y no
  `fuentes.glpi`
- **WHEN** se carga un archivo por la entrada que Acción Fiduciaria usa para
  GLPI
- **THEN** el motor lo procesa con el adaptador de Aranda

#### Scenario: Acción Fiduciaria no cambia

- **GIVEN** el perfil `accion-fiduciaria`, que declara `fuentes.glpi` y no
  `fuentes.casos`
- **WHEN** se carga un archivo GLPI
- **THEN** el motor llama `cargarGlpi()` exactamente como antes

### Requirement: lectores de indicadores, backups y disponibilidad configurables por perfil

El motor SHALL leer el nombre de hoja de `Indicadores`/`Backups` y la
taxonomía de métricas de indicadores desde `PERFIL.fuentes.consolidado`
cuando estén declarados, y SHALL conservar sus valores por defecto de
Acción Fiduciaria cuando no lo estén. El motor SHALL ofrecer la estrategia
`tabla-con-fechas` para disponibilidad por motor/sistema cuando el perfil
la declara.

#### Scenario: Bancóldex lee su hoja Indicador de dos filas

- **GIVEN** el perfil `bancoldex`, con `fuentes.consolidado.indicadores.hojas
  = ['Indicador']` y sus tres métricas con alias propios
- **WHEN** se carga el consolidado de junio de 2026
- **THEN** el dominio `indicadores` publica los tres valores del mes con sus
  metas declaradas (99,98 %, 97 %, 99 %)

#### Scenario: Bancóldex lee backups por BD

- **GIVEN** el perfil `bancoldex`, con `fuentes.consolidado.backups = {hoja:
  'Ejecucion Backups', columna: 'bd'}`
- **WHEN** se carga el consolidado de junio de 2026
- **THEN** el dominio `backups` publica 11 instancias con 100 % de ejecución,
  sin que una coincidencia parcial del nombre de columna con un valor de
  fila (p. ej. `BCOEXCCBD27`) elija una fila de datos como cabecera

#### Scenario: Acción Fiduciaria conserva sus lectores exactos

- **GIVEN** el perfil `accion-fiduciaria`, que no declara
  `fuentes.consolidado.indicadores` ni `.backups`
- **WHEN** se carga su consolidado
- **THEN** el motor sigue leyendo las hojas `Indicadores`/`Inidcadores` y
  `Backups`/`Instancias` exactamente como antes de este change

### Requirement: casos Aranda publicados y explicados con gráficas compartidas

Cuando el perfil configura `c5` con el dominio `casos`, el cargador Aranda
SHALL publicar sus agregados en ese dominio. El modal SHALL reutilizar el
componente gráfico de casos existente y SHALL representar los desgloses por
motor y categoría como gráficas, sin tablas de Excel ni filas crudas de
tickets en el estado exportable.

#### Scenario: export real de junio de 2026

- **GIVEN** el export Aranda original con 72 casos de Bancóldex
- **WHEN** se carga y se abre `c5`
- **THEN** el modal muestra 72 casos, SLA 71/72, una barra apilada por tipo,
  una gráfica por motor y una gráfica por categoría, sin ningún elemento
  `<table>` en la rama Aranda

### Requirement: consolidado procesado por dominios seleccionados

El cargador del consolidado SHALL ejecutar únicamente los lectores requeridos
por los dominios del preset activo, de forma que una hoja excluida y sin corte
vigente no bloquee dominios válidos del mismo archivo.

#### Scenario: disponibilidad desactualizada fuera del preset Bancóldex

- **GIVEN** el consolidado original donde `Disponibilidad Real` termina en
  jun-25 y el preset de jun-26 solo requiere indicadores y backups
- **WHEN** se carga el consolidado
- **THEN** se publican tres indicadores y 11 backups, y no se exige una
  columna jun-26 a la hoja de disponibilidad excluida

### Requirement: libro cualitativo de alcance único

Un perfil SHALL poder declarar un solo archivo cualitativo con hojas exactas
para logros y mitigaciones. El lector SHALL publicar ambos dominios y SHALL
rechazar mitigaciones cuya fecha de entrega no pertenezca al periodo activo.

#### Scenario: libro cualitativo Bancóldex de junio de 2026

- **GIVEN** un libro con hojas `Logros` y `Mitigación`, cinco logros y dos
  mitigaciones con fecha de entrega 30/06/2026
- **WHEN** se carga para junio de 2026
- **THEN** los dominios publican 5 y 2 registros respectivamente desde la
  misma entrada de archivo

### Requirement: perfil con fuente propia no autocarga insumos ajenos

El arranque SHALL omitir el paquete automático de Acción Fiduciaria cuando el
perfil activo declara una fuente propia de casos, y SHALL restaurar el periodo
antes de revalidar sus insumos persistidos.

#### Scenario: Bancóldex persiste junio mientras existe insumos-af.js de julio

- **GIVEN** Bancóldex guardado en junio de 2026 y un paquete local de Acción
  Fiduciaria de julio de 2026
- **WHEN** la página se recarga
- **THEN** conserva junio, restaura sus archivos Bancóldex y no procesa el
  paquete ajeno
