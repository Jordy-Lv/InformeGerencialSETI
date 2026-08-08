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

#### Scenario: Bancoldex carga por la entrada de GLPI

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

### Requirement: etiqueta de la entrada de casos declarada por perfil

El motor SHALL mostrar la etiqueta y el texto de ayuda del insumo de casos
declarados en `PERFIL.textos.carga.glpiTitulo`/`glpiAyuda` cuando existan
(mismo mecanismo `data-perfil-carga` que ya usa el insumo de consolidado y
el de AlertsList), y SHALL conservar el literal «2. Exportación GLPI»
embebido en el HTML cuando el perfil no los declare.

#### Scenario: Bancoldex ve "Exportación Aranda"

- **GIVEN** el perfil `bancoldex`, con `textos.carga.glpiTitulo = '2.
  Exportación Aranda'`
- **WHEN** `hidratarTextosPerfil()` corre al cargar la página
- **THEN** el segundo insumo obligatorio se rotula «2. Exportación Aranda»
  con su texto de ayuda propio

#### Scenario: Acción Fiduciaria conserva el rótulo GLPI

- **GIVEN** el perfil `accion-fiduciaria`, que no declara `textos.carga.glpiTitulo`
- **WHEN** `hidratarTextosPerfil()` corre al cargar la página
- **THEN** el segundo insumo conserva el literal «2. Exportación GLPI» del
  HTML

### Requirement: casos Aranda publicados y explicados con gráficas compartidas

Cuando el perfil configura `c5` con el dominio `casos`, el cargador Aranda
SHALL publicar sus agregados en ese dominio. El modal SHALL reutilizar el
componente gráfico de casos existente y SHALL representar los desgloses por
motor y categoría como gráficas, sin tablas de Excel ni filas crudas de
tickets en el estado exportable.

#### Scenario: export real de junio de 2026

- **GIVEN** el export Aranda original con 72 casos de Bancoldex
- **WHEN** se carga y se abre `c5`
- **THEN** el modal muestra 72 casos, SLA 71/72, una barra apilada por tipo,
  una gráfica por motor y una gráfica por categoría, sin ningún elemento
  `<table>` en la rama Aranda

### Requirement: AlertsList no reemplaza el dominio de casos de un perfil con fuente propia

Cuando el perfil activo declara `fuentes.casos`, el motor SHALL interpretar
el archivo de AlertsList (validarlo, contar sus registros del periodo,
publicar el dominio `alertas` y marcar el insumo) sin sobrescribir el
dominio `casos` ni el slide compartido de casos con el modelo
alertas+GLPI de Acción Fiduciaria/Novaventa.

#### Scenario: Bancoldex carga AlertsList después de Aranda

- **GIVEN** Bancoldex con su export Aranda ya cargado (dominio `casos` en
  modo `aranda-tipo-motor`) y `fuentes.alertas` declarado
- **WHEN** se carga un AlertsList del mismo periodo
- **THEN** el dominio `alertas` publica sus propios registros y el dominio
  `casos`, la tarjeta y el slide de Aranda conservan las cifras del export
  de Aranda sin cambios

#### Scenario: Acción Fiduciaria no cambia

- **GIVEN** el perfil `accion-fiduciaria`, que no declara `fuentes.casos`
- **WHEN** se carga AlertsList
- **THEN** el dominio `casos` se recalcula con el modelo alertas+GLPI
  exactamente como antes de este change

### Requirement: un perfil con fuente propia de casos no autocarga el paquete local de otro cliente

El arranque SHALL omitir la búsqueda del `<script>` vecino de extracción
automática (p. ej. `insumos-af.js`) cuando el perfil activo declara
`fuentes.casos`.

#### Scenario: insumos-af.js presente en el equipo del consultor

- **GIVEN** un perfil con `fuentes.casos` declarado y un archivo
  `insumos-af.js` de Acción Fiduciaria presente junto al HTML (residuo de
  desarrollo local)
- **WHEN** la página carga
- **THEN** el motor no intenta leer ese script ni ajusta el periodo del
  informe con datos de otro cliente

#### Scenario: Acción Fiduciaria conserva la extracción automática

- **GIVEN** el perfil `accion-fiduciaria`, que no declara `fuentes.casos`
- **WHEN** existe `insumos-af.js` junto al HTML
- **THEN** el motor lo carga exactamente como antes de este change

### Requirement: la hoja «Casos» del consolidado no alimenta a un perfil con fuente propia de casos

`cargarCasos()` (lector de la hoja «Casos» del consolidado, modelo
alertas/requerimientos/incidentes de Acción Fiduciaria) SHALL omitirse
completo cuando el perfil activo declara `fuentes.casos`, y SHALL dejar
`alertasConsolidadoMes` en `null` para que la reconciliación con AlertsList
no compare contra una cifra de otro modelo.

Es el mismo principio ya establecido para `publicarCasos()` y para el bloque
de repintado de `cargarAlertas()`: el dueño del dominio `casos` es la fuente
declarada por el perfil, y el modelo de AF no debe escribir encima.

#### Scenario: el consolidado de Bancoldex trae hoja «Casos» y no rompe el export de Aranda

- **GIVEN** Bancoldex (declara `fuentes.casos`) con su export de Aranda ya
  cargado, cuyo gráfico del slide tiene una serie por tipo de caso
- **WHEN** se carga el consolidado, cuyo libro sí contiene una hoja «Casos»
- **THEN** las cifras y el gráfico de Aranda quedan intactos, el consolidado
  se procesa sin error y la exportación no queda bloqueada

#### Scenario: sin casos en el periodo, el consolidado sigue cargando

- **GIVEN** Bancoldex con un export de Aranda cuyo periodo no coincide con el
  seleccionado, de modo que el gráfico del slide queda sin ninguna serie
- **WHEN** se carga el consolidado
- **THEN** el consolidado se procesa con normalidad — no se produce ningún
  error de tipo al escribir sobre una serie inexistente

#### Scenario: Acción Fiduciaria conserva la hoja «Casos»

- **GIVEN** el perfil `accion-fiduciaria`, que no declara `fuentes.casos`
- **WHEN** se carga el consolidado
- **THEN** `cargarCasos()` lee la hoja «Casos» y alimenta las series y el
  histórico exactamente como antes de este change

### Requirement: las extensiones admitidas por insumo se resuelven contra la selección vigente

El motor SHALL resolver las extensiones de archivo permitidas para un insumo
leyendo las tarjetas seleccionadas **en el momento de validar**, no una vez
al cargar la página.

Un mapa calculado una sola vez queda obsoleto en cuanto el preset cambia
(restauración del preset guardado, o el usuario editando el preset en
«Tarjetas»), y el síntoma es que la entrada de archivo correspondiente
rechaza cualquier archivo con un mensaje de formatos vacío («Usa .»).

#### Scenario: el usuario agrega una tarjeta con una fuente nueva

- **GIVEN** un perfil cuyo preset inicial no incluye ninguna tarjeta que
  declare la fuente `mitigaciones`
- **WHEN** el usuario agrega en «Tarjetas» una tarjeta que sí la declara y
  carga un `.xlsx` en esa entrada
- **THEN** el archivo se acepta

#### Scenario: el mensaje de formatos nunca queda vacío

- **GIVEN** una entrada de archivo de un insumo cualquiera
- **WHEN** se rechaza un archivo por su extensión
- **THEN** el mensaje enumera al menos un formato admitido

### Requirement: un insumo restaurado se revalida al cambiar el periodo

Al restaurar los insumos guardados en el equipo, el motor SHALL depositar cada
archivo reconstruido en la entrada de archivo que le corresponde, de modo que
la revalidación por cambio de periodo lo vuelva a leer igual que a uno cargado
a mano.

La revalidación recorre las entradas de archivo. Un insumo restaurado que no
quede depositado en la suya queda congelado con el resultado del periodo con
el que se guardó, y la pantalla muestra una cifra de un mes distinto al
seleccionado sin decir que no corresponde.

#### Scenario: se restaura un insumo guardado con otro periodo y luego se corrige el mes

- **GIVEN** un insumo guardado en el equipo, leído en su momento contra un
  periodo distinto al que ahora está seleccionado
- **WHEN** el usuario restaura los informes guardados y luego cambia el mes
  del informe al que corresponde el archivo
- **THEN** ese insumo se vuelve a leer contra el periodo nuevo y su estado
  refleja las cifras del mes seleccionado

#### Scenario: el archivo restaurado queda visible en su entrada

- **GIVEN** insumos guardados en el equipo
- **WHEN** el usuario los restaura
- **THEN** cada entrada de archivo muestra el nombre del archivo restaurado,
  no «ningún archivo seleccionado»

### Requirement: el insumo de casos cuenta como obligatorio cuando el perfil declara su propia fuente

El recuento de insumos obligatorios SHALL incluir la entrada de casos cuando
el perfil declara `fuentes.casos`, y SHALL dar ese insumo por procesado
cuando el dominio `casos` queda resuelto.

Un perfil que trae sus casos por una fuente propia (Aranda) no declara
`fuentes.glpi`, pero usa la misma entrada de archivo: sin esta regla, el
insumo desaparece del recuento pese a estar en pantalla rotulado como
obligatorio y a tener un criterio de validación propio.

#### Scenario: Bancoldex con consolidado, Aranda y AlertsList

- **GIVEN** el perfil `bancoldex`, que declara `fuentes.casos` y
  `fuentes.alertas` y no declara `fuentes.glpi`
- **WHEN** se cargan el consolidado, el export de Aranda y el AlertsList del
  periodo
- **THEN** el recuento declara tres insumos obligatorios y los tres como
  procesados

#### Scenario: Acción Fiduciaria no cambia

- **GIVEN** el perfil `accion-fiduciaria`, que declara `fuentes.glpi` y
  `fuentes.alertas` y no declara `fuentes.casos`
- **WHEN** se cargan sus insumos
- **THEN** el recuento sigue siendo el de siempre: consolidado, GLPI y
  AlertsList
