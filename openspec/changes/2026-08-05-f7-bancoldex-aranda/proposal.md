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

## Alcance de este change (F7a)

Esta primera entrega deja **declarado y verificado el modelo de datos**:

1. `perfiles/base.js` — perfil base SETI, sin cliente concreto, registrado
   junto a los demás.
2. `perfiles/bancoldex.js` — extiende `base`, declara identidad, metas,
   contrato y la fuente `casos` (Aranda).
3. `adaptarArandaACanonico()` — nueva función, paralela a
   `adaptarGlpiACanonico()` (F5), que traduce las filas de Aranda a
   `CasoCanonico` reutilizando `casoCanonico()`, `resolverCabecera()` y la
   estrategia `cabecera-de-dos-filas` (nueva) para el consolidado.
4. `cargarCasosAranda()` — nuevo cargador que lee, valida y agrega los casos
   de Bancóldex por tipo, motor y SLA, y devuelve el resultado (no publica
   en `REPORTE`: no hay tarjeta ni dominio derivado todavía para Bancóldex,
   ver `design.md`), sin tocar `cargarGlpi()` ni ninguna cifra de Acción
   Fiduciaria o Novaventa.
5. Verificación de los 72 casos, sus agregados por tipo/motor y el SLA 71/1
   contra el export real y contra `Bancoldex/reporte-bancoldex-2026-07-02.pdf`.

## Fuera de alcance (queda pendiente para F7b)

- Integrar `cargarCasosAranda()` con el centro de carga (selector de
  archivo/entrada de UI) y con una tarjeta `c5`-equivalente que muestre las
  cuatro categorías de Bancóldex (hoy `renderC5()` está escrito para
  requerimiento/incidente de AF; una cifra de "Tarea" o "Incidente -
  Monitoreo" no tiene dónde pintarse todavía).
- Los tres lectores de consolidado declarados en el reconocimiento:
  `Indicador` (cabecera de dos filas, 4 métricas), `Ejecucion Backups` (por
  `BD`), `Linea Base` (con `AMBIENTE`) y `Disponibilidad Real` por motor.
- La decisión de si `TYA` puede automatizar la bolsa de horas (bloqueada:
  ningún segundo cliente lo necesita todavía, ver `openspec/project.md`).
- Cualquier cambio a Acción Fiduciaria o Novaventa.

## Coordinación con F6

`openspec/changes/2026-08-05-f6-perfil-novaventa/tasks.md` sigue abierto y
reserva `informe-accion-fiduciaria 1.html`. Este change also lo toca (solo
para añadir funciones nuevas, sin modificar las existentes de GLPI/AF). Se
desarrolla en la rama independiente `f7/bancoldex-aranda-perfil`, creada
desde el cierre de F5 (`db3d368`, `origin/codex/f5-adaptadores-canonico`), no
desde F6. **No se mergea a `main` antes de coordinar el orden con quien cierre
F6** — ver la regla de conjuntos de archivos disjuntos en `openspec/AGENTS.md`.
