# Modal "Gestión de backups": la matriz cede su lugar al radar de "Disponibilidad por CI"

**Fecha:** 22 de julio de 2026
**Rama:** `feature/disponibilidad-historico` (pendiente de merge a `main`)
**Origen:** Pedido directo del usuario sobre el modal **"Gestión de backups"** (`c7`): *"reemplazar esta primera gráfica de gestión de backups por la de disponibilidad CI, así totalmente igualita"*. Decisión de negocio tomada en la misma sesión: la línea de meta será **99,3 %**, el mismo SLA contractual que usa CI, para que la gráfica quede idéntica.

## Contexto

El modal de backups estrenaba (mismo día, en `2026-07-22-backups-historico.md` — documento **eliminado a propósito** el 29/07/2026 porque describía la matriz que este mismo cambio reemplazó; ver la tabla de borrados en [`2026-07-29-relevo-sesion-28-julio.md`](archivo/2026-07-29-relevo-sesion-28-julio.md)) un hero verde de una fila + una **matriz de celdas** instancia × mes (✓/×/%). El de **Disponibilidad por CI** (`c11`) ya usaba el diseño que el cliente prefiere: hero azul de 4 estadísticas + **gráfica de cápsulas** de promedio mensual con línea de meta punteada + panel lateral con el valor exacto por sistema. El pedido fue unificar: dejar backups **igual** que CI.

Ese doc de la matriz queda como registro histórico del diseño anterior; esta intervención lo reemplaza.

## Qué se implementó

Sin duplicar código: se reutiliza el componente de CI (`montarRadarCI`) y todo su CSS (`.ci-*`). Los datos de backups ya tenían la forma exacta que el componente espera (`historico.instancias` con `valores[]` alineados a `historico.periodos[]`), así que no se tocó el parser `cargarBackups` ni el store.

### 1. `montarRadarCI` parametrizado (reutilizable)

Se le añadió un tercer parámetro `opts={}`, todo con defaults iguales al comportamiento de hoy (CI no cambia):

- `id` (`'ci'` por defecto) — separa el estado del filtro (`rangosHistorico`, `seleccionDisponibilidadCI`) por llamador. Abrir backups ya no mueve el rango de CI y viceversa (verificado).
- Un objeto de textos `T` (kicker, subtítulo del panel, rótulo del panel lateral, textos del stat "peor", palabra de la medida) que backups sobrescribe con la variante "instancia"/"ejecución". El interior (estadística, escala, cápsulas, panel lateral, footer, actualización del `.ci-overview`) no cambió.

### 2. `renderC7` reescrito

De `backup-command--matrix` + `backup-hero` + `montarMatrizBackups` a la misma estructura `ci-command` + `ci-overview` (4 stats) + `.ci-radar` que `renderC11`, alimentada desde `dom('backups').datos.historico` y con `meta=99,3`. El modal ya no crea ningún canvas (el radar es HTML/CSS puro), lo que además simplifica el PDF.

### 3. Autopruebas adaptadas

Las dos pruebas de backups que leían la matriz vieja se reapuntaron al nuevo DOM, modeladas sobre las de CI:

- "Backups: el detalle lista todas las instancias de la hoja" → cuenta `#dashboard-c7 .ci-month-row` (14/14).
- "Backups: cada instancia coincide con el Excel" → coteja `.ci-month-row[data-valor]` del periodo seleccionado contra `historico.instancias`.

### 4. Limpieza de código muerto

Eliminados por quedar sin uso (confirmado con `grep`): JS `montarMatrizBackups`, `estadoBackup`, `seleccionBackups`; y el CSS de la matriz (`.backup-command`, `.backup-hero*`, `.backup-history*`, `.backup-matrix*`, `.backup-nodes*`, `.backup-grid`, `.backup-node*`, `.backup-ribbon`, `.backup-legend`, y las reglas `body.exportando-pdf .backup-*`). Se **conservó** la línea minificada `3980` (`.backup-command` histórico) porque comparte declaración con reglas vivas `.signal-*`/`.metric-constellation` fuera de alcance —mismo criterio ya aplicado antes con el CSS de `renderC4`— y las reglas `#dashboard-c7 .dashboard-*` de las media queries, que siguen vigentes.

## Verificación realizada

Con los cuatro insumos reales de `Insumos/`, navegador servido por HTTP local, inyectando los Excel vía `fetch()`+`DataTransfer`:

- **Paridad visual:** el modal de backups reproduce el de CI — hero 4 stats (14/14, promedio 100 %, "Resultado uniforme · Todas las instancias", 10 meses), 10 cápsulas por mes con la línea de meta **99,3 %** punteada, panel lateral "Valor exacto por instancia" con las 14 instancias, filtro 3M/6M/12M/Todo + Desde/Hasta.
- **Interacción:** click en una cápsula cambia el mes del panel lateral; 3M reduce a 3 cortes.
- **Estados de filtro independientes:** backups en 3M y CI en Todo no se cruzan; backups recuerda su rango al reabrir (ids `'backups'` vs `'ci'`).
- **CI sin regresión:** conserva todos sus textos por defecto y sus 10 cápsulas / 14 filas.
- **Autopruebas:** 34/35 PASA. La única falla —"Portada: estado general no afirma cumplimiento"— es **preexistente** (referencia `data-k="estadoGeneral"` inexistente en el HTML, ya en `main`), sin relación con este cambio. Las 4 pruebas de backups pasan.
- **PDF:** el radar de backups usa las clases `hist-controls`/`ci-radar__controls`, cubiertas por las reglas `body.exportando-pdf …{display:none}` que ocultan el filtro en el PDF; mismo camino de exportación que CI (con PDF ya verificado). No se ejecutó la descarga real para no escribir en Descargas sin confirmación.
- **Sintaxis:** los 9 bloques `<script>` pasan `node --check`; el bloque de estilos editado quedó con las llaves balanceadas.

## Archivos tocados

Un único archivo: [`informe-accion-fiduciaria 1.html`](../informe-accion-fiduciaria%201.html). Sin cambios en dependencias, parser ni store.

## Pendiente / fuera de alcance

- No se ejecutó la descarga real del PDF (solo se verificó el camino de export y las reglas de ocultado).
- Falla preexistente "Portada: estado general" — fuera de este cambio.
- La diapositiva estática `s7` y la tarjeta colapsada `c7` no se tocaron (solo el modal).
