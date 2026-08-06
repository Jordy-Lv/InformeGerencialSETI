# Reorganización del contexto documental para reducir consumo de tokens

## Contexto

El repositorio mantenía su contexto de trabajo (goals, decisiones, estado de
fases) en 76 archivos `.md`, ~434 KB (≈110k tokens si se cargaban todos).
Cada sesión nueva compensaba la falta de un punto de entrada liviano en
`main` pegando o abriendo mucho más de lo necesario — sobre todo
`docs/2026-08-04-plan-multicliente.md` (622 líneas), que mezclaba
arquitectura estable con una tabla de estado que cambiaba cada sesión. Este
change parte de la PR #16 (`docs/fundacion-documental`, sin fusionar al
06/08/2026), que ya traía `README.md`, `CLAUDE.md`, `docs/README.md` con
columna de estado, `docs/PATRONES.md` y la convención
`openspec/changes/archivo/`, y completa lo que le faltaba.

## Qué se implementó

1. **Corrección puntual del plan maestro (previa a partirlo):** la tabla
   `Estado de ejecución` decía que F1 estaba "pendiente revisión y fusión"
   cuando ya está fusionada en `main` (PR #12, commit `404408c`) — corregido
   con evidencia de `git log`. F2–F11 se dejó explícito que viven en ramas
   sin fusionar en vez del genérico "Pendientes".
2. **Se partió el plan maestro en tres documentos de vida distinta:**
   - `docs/arquitectura-multicliente.md` (nuevo) — la parte estable:
     contexto, decisiones tomadas, arquitectura objetivo, estructura de
     OpenSpec, fases con criterio de aceptación, archivos críticos,
     verificación, riesgos, preguntas abiertas. Se omitió la sección 4
     "Patrones" del original porque ya está íntegra en `docs/PATRONES.md`
     (PR #16); se enlaza en su lugar.
   - `TASKS.md` (nuevo, raíz) — solo lo activo: estado por fase según lo que
     **`main` puede verificar** (F0 casi completo, F1 cerrado, F2–F6 en
     ramas sin fusionar), siguiente paso y bloqueos conocidos.
   - `CHANGELOG.md` (nuevo, raíz) — entradas de 3–5 líneas fechadas,
     sembrado retroactivamente con F0 y F1 (lo único verificable en `main`
     al momento de escribir). Se documentó explícitamente que F2–F6 no se
     siembran todavía, para no registrar como hecho algo que aún puede
     cambiar.
   - El documento original se movió a
     `docs/archivo/2026-08-04-plan-multicliente.md` con una nota de
     redirección arriba; se conserva completo por su valor histórico.
3. **Se archivaron 6 documentos** marcados «Superado» o «Referencia» en
   `docs/README.md` (2 555 líneas en total) a `docs/archivo/`:
   `2026-08-04-validacion-recarga-de-insumos.md`,
   `2026-08-03-inventario-tarjetas-cardio-infantil.md`,
   `2026-08-02-auditoria-insumos-glpi-alertops-disponibilidad.md`,
   `2026-07-29-relevo-sesion-28-julio.md`,
   `2026-07-28-disponibilidad-bd-levantamiento.md`,
   `2026-07-28-contrato-tecnico-mateo.md`. Todos con `git mv` (historial
   preservado), ninguno borrado.
4. **Se corrigieron los enlaces** que apuntaban a las rutas viejas de los 7
   archivos movidos, en `docs/README.md`, `openspec/project.md`,
   `openspec/specs/README.md`, `docs/requisitos-producto.md`,
   `automatizacion/README.md` y varios docs de sesión vigentes que se
   citaban entre sí. Los enlaces dentro de documentos ya archivados
   (histórico) **no se tocaron** — es la convención que el propio
   `docs/README.md` ya establece: no se reescribe el histórico.
5. **`openspec/AGENTS.md`:** se añadió la sección «Qué leer según la tarea»
   (la tabla de carga bajo demanda) y se sustituyó el punto 4 de «Al
   terminar» — antes pedía actualizar la tabla del plan maestro; ahora pide
   actualizar `TASKS.md` y, si la fase cierra, sumar una entrada a
   `CHANGELOG.md`.
6. **`CLAUDE.md`:** de 148 a 122 líneas. Se eliminó la sección "Dato o
   código" (duplicada en `project.md` y `PATRONES.md`) y se redujo "Cómo se
   cierra una tarea" de un checklist de 6 puntos a un párrafo que enlaza a
   `AGENTS.md`. Se conservaron íntegras las tablas de "Prohibido" y "Pruebas
   adversariales" — son las de mayor valor operativo y no están duplicadas
   en ningún otro archivo.

## Verificación realizada

```bash
python3 -m unittest discover -s automatizacion -p 'test_*.py' -v
```
Resultado: **36 pruebas, OK** — ningún archivo de código ni de spec vigente
se tocó en este change, así que la suite no debía verse afectada; se
confirma que no lo fue.

```bash
grep -rn "docs/2026-\|(2026-07-\|(2026-08-" --include="*.md" .
```
Usado para localizar y corregir manualmente cada enlace relativo hacia los
7 archivos movidos (ver punto 4 arriba). Verificación final por archivo
movido con `grep` dirigido a cada nombre de archivo, confirmando cero
referencias activas sin actualizar fuera de `docs/archivo/`.

## Archivos tocados

**Nuevos:** `TASKS.md`, `CHANGELOG.md`, `docs/arquitectura-multicliente.md`,
este documento.

**Movidos (`git mv`, sin editar contenido salvo lo indicado):**
`docs/2026-08-04-plan-multicliente.md` (+ nota de redirección),
`docs/2026-08-04-validacion-recarga-de-insumos.md`,
`docs/2026-08-03-inventario-tarjetas-cardio-infantil.md`,
`docs/2026-08-02-auditoria-insumos-glpi-alertops-disponibilidad.md`,
`docs/2026-07-29-relevo-sesion-28-julio.md`,
`docs/2026-07-28-disponibilidad-bd-levantamiento.md`,
`docs/2026-07-28-contrato-tecnico-mateo.md` → todos a `docs/archivo/`.

**Editados (solo enlaces o las secciones descritas arriba):** `README.md`,
`CLAUDE.md`, `docs/README.md`, `docs/PATRONES.md`, `docs/requisitos-producto.md`,
`docs/2026-07-22-backups-radar-ci.md`,
`docs/2026-07-23-analisis-por-rango-y-redondeo.md`,
`docs/2026-07-29-pruebas-en-windows-y-correcciones-en-vivo.md`,
`docs/2026-08-02-correccion-de-la-auditoria-y-verificacion-ab.md`,
`docs/2026-08-04-correccion-recarga-de-insumos.md`, `automatizacion/README.md`,
`openspec/AGENTS.md`, `openspec/project.md`, `openspec/specs/README.md`.

## Pendiente

- **Paso 1 del plan (archivar los 5 changes de OpenSpec ya cerrados: F1–F5)
  queda explícitamente fuera de este change.** Requiere editar
  `automatizacion/test_specs_perfil_cliente.py`,
  `test_specs_inventario_tarjetas.py` y `test_specs_adaptadores_fuente.py`
  para que descubran el delta por `glob` en vez de una ruta literal — y esos
  mismos archivos están declarados por el change F6, abierto en la rama
  `codex/f6-perfil-novaventa`. Se ejecuta cuando F2–F6 cierren, siguiendo la
  misma lógica que `openspec/changes/README.md` ya documenta para F1
  (bloqueado por F2 desde antes de este change).
- Este trabajo se hizo en un worktree aislado (`docs/reorg-contexto`, base
  `origin/docs/fundacion-documental`) para no tocar el árbol de trabajo de
  F6, que tenía cambios sin commitear. **Falta fusionar la PR #16 a `main`
  primero**, y esta rama contra la PR #16 (o directamente contra `main`
  tras esa fusión) — coordinado con el usuario antes de cualquier merge.
- `TASKS.md` documenta que F2–F6 tienen trabajo avanzado según quien las
  lleve, pero esa información **no está commiteada en ninguna rama**
  accesible desde aquí; queda anotado como aviso explícito en `TASKS.md`
  para que quien fusione cada fase actualice la tabla con el estado real.
- No se tocó `automatizacion/README.md` más allá de las tres referencias
  rotas — sigue siendo el segundo mayor foco de inflado de contexto
  (579 líneas, el archivo de más *churn* del repo) y queda fuera de alcance
  de este change.
