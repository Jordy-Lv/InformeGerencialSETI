# Aranda + AlertsList para Bancoldex, portado a F6

## Contexto

El usuario pidió, sobre `codex/f6-perfil-novaventa`, que Bancoldex pudiera
interpretar AlertsList y que el insumo #2 del Centro de carga (rotulado
«Exportación GLPI») dijera «Exportación Aranda» e interpretara ese formato.

Antes de tocar código se verificó contra `TASKS.md` y
`docs/2026-08-06-divergencia-bancoldex.md`: esta funcionalidad ya existía,
completa y probada con los insumos reales de junio-2026, en la rama
`codex/bancoldex-completo` (change `2026-08-05-f7-bancoldex-aranda`), que
diverge de F6 en 20 bloques del HTML. Para no crear una tercera versión de
la misma capacidad, el usuario eligió portar quirúrgicamente solo lo que
faltaba, en vez de mergear las dos ramas completas o reescribir desde cero.

## Qué se implementó

Reabierto el change `2026-08-05-f7-bancoldex-aranda` sobre esta rama, con
alcance reducido: el reconocimiento previo mostró que F6 ya tenía,
construido de forma independiente, el equivalente de F7b para indicadores,
backups, disponibilidad por tabla y línea base — no se tocó nada de eso.

1. **`perfiles/bancoldex.js`**: `fuentes.alertas` (formato genérico
   Alert ID/Created Date/Escalation Policy), `tarjetas.configuracion.c5`
   (dominios `casos`+`alertas`, fuente física `glpi`+`alertas`, criterio
   propio de Aranda), `tarjetas.presentacion.c5`, `'c5'` en
   `tarjetas.seleccionadas`, y `textos.carga.glpiTitulo`/`glpiAyuda` para el
   rótulo dinámico.
2. **Motor (`informe-accion-fiduciaria 1.html`)**:
   - `clasificarTipoAranda()`, `adaptarArandaACanonico()`,
     `cargarCasosAranda()`, `cargarCasosOGlpi()`,
     `actualizarTarjetaCasosAranda()`, `pintarCasosArandaEnSlide()` —
     portadas desde `codex/bancoldex-completo` sin tocar `cargarGlpi()`.
   - Los 3 sitios que llamaban `cargarGlpi` directo ahora llaman
     `cargarCasosOGlpi`.
   - `presentarTarjetaPerfil()` generalizada para fusionar también
     `PERFIL.tarjetas.configuracion` (antes solo `presentacion`).
   - Bloque `x.modo==='aranda-tipo-motor'` en `renderC5()` (dona por motor,
     barras por categoría, análisis narrativo) + 3 clases CSS.
   - `data-perfil-carga="glpiTitulo"`/`"glpiAyuda"` en el insumo #2, mismo
     mecanismo que ya usa Novaventa.
   - **Decisión nueva, no cubierta por F7** (esa rama nunca declaró
     `fuentes.alertas` para Bancoldex): `publicarCasos()` y el bloque de
     `cargarAlertas()` que pinta `DATA_CASOS`/`#s5`/`chartCasos` ahora se
     condicionan a `!PERFIL.fuentes?.casos`, para que AlertsList no
     sobrescriba el dominio `casos` de un perfil con fuente propia.
     `actualizarTarjetaCasos()` despacha por el modo publicado.
   - **Hallazgo en navegador**: `c5.configuracion` debe declarar
     `'alertas'` en `dominios` y `fuentes` aunque no alimente la cifra de
     `c5` — dos mecanismos genéricos (`actualizarVisibilidad()`,
     `EXTENSIONES_INSUMO`) la refieren por nombre exacto.
   - **Hallazgo en navegador**: `cargarInsumosAutomaticos()` no tenía guard
     por perfil; con `insumos-af.js` (de Acción Fiduciaria) presente junto
     al HTML, el periodo de Bancoldex saltaba de junio a julio sin acción
     del usuario. Se agregó `if(PERFIL.fuentes?.casos) return;`.
3. **`automatizacion/test_specs_adaptadores_fuente.py`**: clase
   `TestAdaptadorAranda` (13 pruebas) que cubre el adaptador, el
   enrutamiento, la configuración declarativa de tarjeta, el modal, los dos
   guards de la interacción AlertsList × Aranda, y los dos hallazgos de
   navegador.
4. **OpenSpec**: change `2026-08-05-f7-bancoldex-aranda` reabierto con
   `tasks.md`/`design.md`/`proposal.md` actualizados al alcance real, y los
   deltas de `adaptadores-fuente`/`perfil-cliente` recortados a lo que esta
   sesión efectivamente implementó (no al alcance completo de la rama
   `codex/bancoldex-completo`).

## Verificación realizada

```
python3 -m unittest discover -s automatizacion -p 'test_*.py'
→ 95 pruebas, OK

python3 automatizacion/verificar_ab.py --autoprueba
→ Autoprueba OK (los 3 casos)

node --check <script principal extraído>
→ sin errores de sintaxis

git diff --check -- "informe-accion-fiduciaria 1.html" perfiles/bancoldex.js
→ sin errores de espacio en blanco
```

**Navegador real** (Chrome vía el panel de previsualización), sirviendo el
directorio del repo con `python3 -m http.server` únicamente para que el
navegador de prueba ejecute JavaScript sobre `http://` — el entregable
sigue siendo un archivo `file://` sin servidor, eso no cambia:

- Bancoldex, junio 2026, con los insumos reales
  `Bancoldex/Data consolidada junio_Bancoldex 2026.xlsx` y
  `Bancoldex/Casos  + tareas BD junio 2026.xlsx` (ambos gitignored, no
  versionados):
  - Insumo #2 rotulado «2. Exportación Aranda» con su ayuda propia.
  - 72 casos interpretados: 33 Incidente-Monitoreo, 32 Requerimiento, 5
    Tarea, 2 Incidente. SLA 71/72 (98,61 %). Motores: 52 Oracle, 19 SQL
    Server, 1 Weblogic. Categoría principal de requerimientos: Ejecución de
    Scripts (16). Cifras idénticas a las que
    `docs/2026-08-05-f7-bancoldex-aranda.md` (rama `bancoldex-completo`)
    había verificado contra el mismo archivo.
  - Tarjeta c5, dashboard (dona + barras + análisis narrativo) y export de
    slide (`#s5`) renderizan correctamente.
  - Indicadores (3, 100 %) y backups (100 %) sin cambios — confirma que la
    generalización independiente de F6 para esos lectores sigue intacta.
- AlertsList sintético (2 alertas, jun-26, sin columnas Topic/Message): se
  interpreta (cuenta 2, publica el dominio `alertas` con estado
  `advertencia`, marca el insumo, avisa por la columna faltante) **sin
  alterar** los 72 casos de Aranda ya mostrados — confirma el guard de
  "Interacción AlertsList × Aranda". No existe un CSV real de AlertsList de
  Bancoldex en este equipo; queda pendiente confirmar con el primero real.
- Acción Fiduciaria (perfil por defecto, sin `?perfil=`): label «2.
  Exportación GLPI» intacto, autocarga de `insumos-af.js` intacta (8 casos
  reales del dev fixture local), consola sin errores nuevos.

## Archivos tocados

- `perfiles/bancoldex.js`
- `informe-accion-fiduciaria 1.html`
- `automatizacion/test_specs_adaptadores_fuente.py`
- `openspec/changes/2026-08-05-f7-bancoldex-aranda/` (proposal.md, design.md,
  tasks.md, specs/adaptadores-fuente/spec.md, specs/perfil-cliente/spec.md)
- `docs/2026-08-06-aranda-alertslist-bancoldex.md` (este documento)

## Pendiente

- Confirmar el parseo de AlertsList con un archivo real de Bancoldex (hoy
  solo se probó con un CSV sintético) en cuanto el cliente entregue uno.
- Aplicar el delta de este change a `openspec/specs/` y archivarlo cuando
  se decida el momento de cierre (coordinado con el resto de F6/F7, ver
  `TASKS.md`).
- La divergencia completa entre `codex/f6-perfil-novaventa` y
  `codex/bancoldex-completo` (20 bloques del HTML) sigue sin resolverse;
  este port no la cierra, solo evita profundizarla en el área de casos de
  Bancoldex. `codex/bancoldex-completo` queda como referencia histórica.
- No se ejecutó el A/B real de Acción Fiduciaria contra `main` (bloqueado
  por falta de insumos reales de junio, ver `TASKS.md`); el A/B sintético
  (`--autoprueba`) y la inspección manual de los guards (todos
  condicionados a `PERFIL.fuentes?.casos`, que AF nunca declara) son la
  evidencia disponible de que AF no cambia.
