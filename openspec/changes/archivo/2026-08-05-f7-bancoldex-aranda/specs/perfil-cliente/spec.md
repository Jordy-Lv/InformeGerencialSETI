## ADDED Requirements

### Requirement: configuración funcional de tarjeta por perfil

El motor SHALL permitir que un perfil sobrescriba declarativamente los
dominios, fuentes y criterios de una tarjeta compartida
(`PERFIL.tarjetas.configuracion`), además de su presentación
(`PERFIL.tarjetas.presentacion`), sin incluir funciones en el archivo del
perfil.

#### Scenario: Bancoldex reutiliza c5 con Aranda

- **GIVEN** `bancoldex` configura `c5` con dominio `casos`, fuente física
  `glpi` y criterio Aranda resuelto
- **WHEN** se resuelven las tarjetas del perfil
- **THEN** `c5` usa la misma tarjeta y el mismo modal compartido, pero valida
  el export Aranda como su única fuente de casos

#### Scenario: Acción Fiduciaria conserva su configuración exacta

- **GIVEN** el perfil `accion-fiduciaria`, que no declara
  `tarjetas.configuracion`
- **WHEN** se resuelven sus tarjetas
- **THEN** cada una conserva los `dominios`/`fuentes`/`criterios` originales
  de `INVENTARIO_TARJETAS`, sin cambios

### Requirement: preset respaldado por evidencia del corte

El perfil Bancoldex SHALL seleccionar únicamente tarjetas respaldadas por el
PDF aprobado y los insumos originales del periodo, y SHALL excluir fuentes
desactualizadas o pertenecientes a otro periodo.

#### Scenario: preset final de junio de 2026

- **GIVEN** el consolidado, Aranda y libro cualitativo originales
- **WHEN** se resuelve `PERFIL_BANCOLDEX.tarjetas.seleccionadas`
- **THEN** el resultado es `c3, c4, c5, c7, c8, c8m` (se agrega `c5` sobre el
  preset previo, que no lo incluía); no incluye `c6/c11` (disponibilidad
  hasta jun-25), `c9` (TYA sep-25) ni `c12` (sin insumo exportable)

### Requirement: un libro cualitativo de alcance único acredita los dos insumos

Cuando el perfil declara
`fuentes.cualitativos.alcance === 'archivo-alcance-unico'` — un solo libro
mensual con una hoja de logros y otra de mitigaciones — cargar ese archivo
por **cualquiera** de las dos entradas del Centro de carga (Logros o
Mitigaciones) SHALL marcar **los dos** insumos como procesados.

Es la misma regla que el motor ya aplica al registro mensual de clientes de
Acción Fiduciaria, donde un archivo cargado por la entrada de Logros marca
también Mitigaciones. Ambas ramas ya publican los dos dominios; lo que
faltaba era marcar los dos insumos, de modo que el usuario tenía que cargar
el mismo archivo dos veces para que el Centro de carga lo diera por completo.

#### Scenario: Bancoldex carga su libro mensual por la entrada de Logros

- **GIVEN** un perfil con `alcance: 'archivo-alcance-unico'` y su libro
  mensual con las dos hojas
- **WHEN** el usuario lo carga en la entrada «Logros y riesgos del cliente»
- **THEN** los insumos de Logros y de Mitigaciones quedan los dos marcados
  como procesados, cada uno con el conteo de su propia hoja

#### Scenario: la entrada alterna de Mitigaciones se comporta igual

- **GIVEN** el mismo perfil y el mismo libro
- **WHEN** el usuario lo carga en la entrada «Mitigaciones y acciones
  (archivo alterno)»
- **THEN** los dos insumos quedan marcados como procesados, sin necesidad de
  volver a cargar el archivo en la otra entrada

### Requirement: un perfil no redeclara la fuente de una tarjeta para expresar que dos insumos comparten archivo

Un perfil SHALL declarar en `tarjetas.configuracion.<id>.fuentes` únicamente
las fuentes cuya **entrada de archivo** alimenta esa tarjeta. Que dos insumos
lleguen en el mismo libro se expresa con
`fuentes.cualitativos.alcance`, no reapuntando la fuente de una tarjeta a la
de otra.

`tarjeta.fuentes` sólo alimenta el mapa de extensiones admitidas por insumo:
reapuntarla deja al insumo original sin ninguna extensión válida y su entrada
de archivo rechaza cualquier archivo.

#### Scenario: la entrada de Mitigaciones de Bancoldex acepta su libro

- **GIVEN** el perfil `bancoldex`, cuyo libro mensual trae Logros y
  Mitigación en hojas separadas
- **WHEN** el usuario carga ese `.xlsx` en la entrada de Mitigaciones
- **THEN** el archivo se acepta y se interpretan las dos hojas

### Requirement: la atribución de incidentes a SETI es una regla declarada por el perfil

Un perfil SHALL declarar en `reglas.atribucionSeti` cómo se acredita que un
incidente es atribuible a SETI. El motor NO SHALL derivar esa cifra de una
aproximación cuando el perfil no declara una regla con respaldo.

Valores admitidos:

| Valor | Significado |
|---|---|
| `'log-indisponibilidades'` | La fuente de casos trae una marca explícita de atribución (el «SI» del log de indisponibilidades de GLPI). Es el default para los perfiles que no declaran la clave — preserva a Acción Fiduciaria sin cambios |
| `'sin-fuente'` | El cliente no tiene todavía una fuente que acredite la atribución. La cifra es **0** y el panel se presenta en estado favorable |

`'sin-fuente'` no es un estado de error ni un aviso: mientras no exista la
fuente que acredite la atribución, la afirmación respaldada es que **no hay
incidentes atribuibles a SETI acreditados**, no que haya una cifra
provisional. La sección se muestra igual, con su título literal.

#### Scenario: Bancoldex no acredita ningún incidente atribuible a SETI

- **GIVEN** el perfil `bancoldex`, que declara
  `reglas.atribucionSeti: 'sin-fuente'`
- **WHEN** se carga el export de Aranda del periodo con incidentes de
  categoría `Incidente`
- **THEN** el panel «Incidentes atribuibles a SETI» del modal de `c5` muestra
  `0`, en estado favorable, con el texto «Sin incidentes atribuibles a SETI»
- **AND** el conteo total de casos, el SLA y las distribuciones por tipo y
  motor no se ven afectados

#### Scenario: Acción Fiduciaria conserva su regla

- **GIVEN** un perfil que no declara `reglas.atribucionSeti`
- **WHEN** se cargan sus casos
- **THEN** la atribución se sigue resolviendo contra el log de
  indisponibilidades, exactamente como hoy

### Requirement: un perfil puede declarar modificadores de presentación de una tarjeta

Un perfil SHALL poder declarar en `tarjetas.presentacion.<id>.modificadores`
una lista de nombres de modificador BEM (`[a-z0-9-]+`) que el motor aplica al
elemento de la tarjeta como `tarjeta-kpi--<modificador>`. El motor SHALL
rechazar cualquier nombre fuera de ese patrón.

Existe para que un cliente cuyos datos no caben en la caja pensada para otro
pueda ajustar su propia presentación **sin modificar la clase compartida**,
que otros clientes ya renderizan en producción.

#### Scenario: los valores largos de Bancoldex no se desbordan en c3

- **GIVEN** el perfil `bancoldex`, cuyo valor de «Motores» es
  «Oracle · SQL Server» (más ancho que la columna)
- **WHEN** se monta la tarjeta `c3`
- **THEN** la tarjeta lleva la clase `tarjeta-kpi--valores-largos` y su texto
  se ajusta dentro de la columna, sin invadir la vecina

#### Scenario: Acción Fiduciaria no declara modificadores

- **GIVEN** un perfil sin `modificadores` en ninguna tarjeta
- **WHEN** se montan sus tarjetas
- **THEN** las clases del elemento son exactamente las de hoy

### Requirement: la presentación de una meta conserva su decimal

Al presentar una meta derivada del perfil, el motor SHALL conservar el
decimal cuando la meta lo tiene y omitirlo cuando no. NO SHALL redondear la
meta a entero.

Antes de generalizarla por perfil, la meta de backups de Acción Fiduciaria
era un literal fijo («Meta 99,3%»). Al derivarla con `metaPerfil()` el texto
pasó por `pct()`, que redondea a entero por defecto, y el informe pasó a
decir «Meta 99%»: una cifra distinta en un entregable en producción.

#### Scenario: Acción Fiduciaria conserva 99,3 %

- **GIVEN** un perfil que no declara `metas.backups` (default 99,3)
- **WHEN** se pinta la tarjeta de backups
- **THEN** el texto dice «Meta 99,3%», igual que antes de la generalización

#### Scenario: Bancoldex no gana un decimal falso

- **GIVEN** el perfil `bancoldex`, con `metas.backups: 0.95`
- **WHEN** se pinta la tarjeta de backups
- **THEN** el texto dice «Meta 95%», no «Meta 95,0%»
