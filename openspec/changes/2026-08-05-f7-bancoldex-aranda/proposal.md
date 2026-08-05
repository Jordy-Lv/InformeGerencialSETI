# F7 — Adaptador Aranda (carga manual) + perfil Bancóldex

## Contexto

Bancóldex no comparte instancia GLPI con Acción Fiduciaria ni Novaventa: sus
casos llegan en un export manual de Aranda (`Casos + tareas BD <mes>.xlsx`,
hoja `Junio`, 72 filas) y su consolidado (`Data consolidada
junio_Bancoldex.xlsx`) tiene una forma distinta en cada hoja compartida con
Acción Fiduciaria — ver `docs/2026-08-05-reconocimiento-bancoldex.md` para el
reconocimiento completo con evidencia real. Bancóldex también difiere lo
bastante como para no poder heredar de `accion-fiduciaria` (la regla del 30 %
de `docs/2026-08-04-plan-multicliente.md` lo prohíbe): fuente de casos,
esquema de columnas, separador de jerarquía, origen del SLA, 4 indicadores en
vez de 3, `Linea Base` con `AMBIENTE`, backups por `BD`, y disponibilidad por
motor son todos distintos.

Hoy no existe ningún perfil que extienda `base` — solo `accion-fiduciaria`
(`extiende: null`) y `novaventa` (`extiende: accion-fiduciaria`) están
registrados en `PERFILES_REGISTRADOS`. Bancóldex es el primer cliente que
ejercita esa rama del diseño.

## Alcance de F7a (modelo de datos)

1. `perfiles/base.js` — perfil base SETI, sin cliente concreto, registrado
   junto a los demás.
2. `perfiles/bancoldex.js` — extiende `base`, declara identidad, metas,
   contrato y la fuente `casos` (Aranda).
3. `adaptarArandaACanonico()` — nueva función, paralela a
   `adaptarGlpiACanonico()` (F5), que traduce las filas de Aranda a
   `CasoCanonico` reutilizando `casoCanonico()` y `resolverCabecera()`.
4. `cargarCasosAranda()` — nuevo cargador que lee, valida y agrega los casos
   de Bancóldex por tipo, motor y SLA, sin tocar `cargarGlpi()` ni ninguna
   cifra de Acción Fiduciaria o Novaventa.
5. Verificación de los 72 casos, sus agregados por tipo/motor y el SLA 71/1
   contra el export real y contra `Bancoldex/reporte-bancoldex-2026-07-02.pdf`.

## Alcance de F7b (integración real, misma rama)

Con Bancóldex como prioridad confirmada por el usuario, se completó en la
misma rama, la misma sesión:

6. `cargarCasosOGlpi()` — despacho por perfil en la entrada de archivo que
   hoy recibe GLPI (`fuentes.casos` → Aranda; sin declarar → `cargarGlpi()`
   intacto), conectado en los tres sitios que antes llamaban `cargarGlpi`
   directo (`INSUMOS_PERSIST`, `procesarFuente`, `ejecutarRevalidacion`).
7. `definicionIndicador()` — generaliza `cargarIndicadores()` para leer el
   nombre de hoja y la taxonomía de métricas desde
   `PERFIL.fuentes.consolidado.indicadores` (con el arreglo `ETIQUETA_INDICADOR`
   de AF como valor por defecto, sin cambiar su resultado).
8. `cargarBackups()` generalizado para leer hoja/columna desde
   `PERFIL.fuentes.consolidado.backups` (por defecto `'Backups'`/`'instancias'`,
   igual que antes).
9. `cargarDisponibilidadTabla()` — nueva función para la estrategia
   `tabla-con-fechas` (disponibilidad por motor/sistema), con
   `cargarDisponibilidad()` despachando a ella solo cuando el perfil la
   declara.
10. `PERFIL.lineaBase` — `renderC3()` presenta la ficha contractual real del
    perfil cuando la declara; AF (sin declararla) conserva su ficha legado
    exacta. Cierra el "gap preexistente" identificado durante F7a.
11. `presentarTarjetaPerfil()` / `PERFIL.tarjetas.presentacion` — un perfil
    puede sobrescribir la presentación (resumen colapsado) de una tarjeta
    que selecciona, sin tocar su lógica ni el inventario compartido.
12. Selección ampliada de Bancóldex: `c3, c4, c6, c7, c8, c8m, c9, c11, c12`
    (`c5` casos y `c10` capacidad quedan fuera — ver `design.md`).
13. Todo verificado end-to-end en navegador real, cargando los dos archivos
    reales de Bancóldex de junio-2026 sin errores de consola.

## Fuera de alcance (queda pendiente)

- Tarjeta visual de casos (`c5`-equivalente) con las cuatro categorías de
  Bancóldex: `renderC5()`/sus criterios (`glpi`+`alertas`) siguen escritos
  para AF/Novaventa. El adaptador ya lee y valida el archivo; falta dónde
  pintarlo.
- `Linea Base` como lector de hoja: `PERFIL.lineaBase` es hoy una
  declaración estática (verificada contra el PDF), no un parser de la hoja
  homónima del consolidado — ningún perfil la lee dinámicamente todavía.
- La decisión de si `TYA` puede automatizar la bolsa de horas (bloqueada:
  ningún segundo cliente lo necesita todavía, ver `openspec/project.md`).
- Cualquier cambio a Acción Fiduciaria o Novaventa.

## Coordinación con F6

`openspec/changes/2026-08-05-f6-perfil-novaventa/tasks.md` sigue abierto y
reserva `informe-accion-fiduciaria 1.html`. Este change también lo toca
(solo con funciones nuevas y generalizaciones con valor por defecto
idéntico al de AF, nunca reescribiendo lógica existente de GLPI/AF/
Novaventa). Se desarrolla en la rama independiente
`f7/bancoldex-aranda-perfil`, creada desde el cierre de F5 (`db3d368`,
`origin/codex/f5-adaptadores-canonico`), no desde F6.

**F6 creció durante esta misma sesión** mucho más allá de "perfil
Novaventa": Codex agregó un administrador de clientes por interfaz
(`docs/2026-08-05-registro-persistente-clientes.md`, directorio principal,
sin confirmar al momento de escribir esto) que permite crear clientes
personalizados eligiendo una "plantilla de validación" existente. Ese
mismo documento deja registrado como pendiente "crear y verificar la
plantilla de validación de Bancóldex" — es decir, F6 y F7 convergen en la
misma necesidad. Se intentó empezar a registrar `perfiles/base.js` y
`bancoldex.js` directamente en el directorio principal (los dos archivos
quedaron ahí, ver `docs/2026-08-05-f7-bancoldex-aranda.md`), pero el editor
detectó que Codex modificaba `informe-accion-fiduciaria 1.html`
**activamente y en simultáneo**; el usuario, consultado, prefirió que el
resto de F7 (registro en `PERFILES_REGISTRADOS`, lectores de consolidado,
tarjeta de casos) se completara aquí, en la rama aislada, para no arriesgar
el trabajo de Codex ni el propio. **No se mergea a `main` antes de
coordinar el orden con quien cierre F6** — ver la regla de conjuntos de
archivos disjuntos en `openspec/AGENTS.md`. Cuando F6 cierre, integrar
`bancoldex` como tercera plantilla de su registro de clientes es trabajo
directo: el perfil ya existe, verificado, con el mismo contrato de datos
(`PERFIL.lineaBase`, `metas`, `tarjetas.presentacion`) que F6 ya usa para
Novaventa.
