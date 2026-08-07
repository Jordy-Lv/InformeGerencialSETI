# Corrección del modal de casos (c5) para Bancoldex/Aranda

## Contexto

Tras portar Aranda/AlertsList a F6 (ver
[`docs/2026-08-06-aranda-alertslist-bancoldex.md`](2026-08-06-aranda-alertslist-bancoldex.md)),
el usuario pidió mejorar el diseño del modal "Total de casos atendidos" para
Bancoldex. Un primer intento reorganizó las gráficas existentes y, sobre
todo, **renombró el panel "Incidentes atribuibles a SETI"** (a "Cumplimiento
e incidentes reales", combinándolo con un badge de SLA). El usuario lo
rechazó explícitamente dos veces y pidió que la corrección quedara
documentada para que otra sesión no repita el error.

## Qué se implementó

- El panel `case-analysis` del modal vuelve a mostrar **únicamente**
  «Incidentes atribuibles a SETI» — título literal, un solo badge, nada más
  ahí — igual que en Acción Fiduciaria.
- El cumplimiento de SLA se movió a un panel propio, con un gauge circular
  (componente `.gauge-exec`/`gauge()`, ya existente en el motor desde antes
  de esta sesión pero sin ningún consumidor), dentro de una grilla de 3
  columnas junto a "Casos por tipo" y "Casos por motor".
- La regla completa, con el razonamiento y lo pendiente, quedó en
  `openspec/changes/2026-08-05-f7-bancoldex-aranda/design.md`, sección
  **"Incidentes atribuibles a SETI: no se toca ese apartado"** — es la
  referencia normativa para cualquier trabajo futuro en este modal.
- `tasks.md` del mismo change tiene el detalle de lo hecho y lo pendiente.

## Verificación realizada

- `python3 -m unittest discover -s automatizacion -p 'test_*.py'` → 96
  pruebas, OK (incluye `test_modal_aranda_no_reemplaza_incidentes_por_sla`,
  reescrita para verificar la estructura corregida).
- Inspección del DOM del modal (`innerText`) con los insumos reales de
  junio-2026: confirma título "Incidentes atribuibles a SETI" con un solo
  badge («2», «1 de 2 incidentes fuera del SLA»), panel de SLA separado con
  el gauge («98,6%», meta 100%), y las tres gráficas de desglose.
- **No se logró una captura de pantalla utilizable**: el panel de
  previsualización del navegador dejó de responder a mitad de la
  verificación visual (posible problema del panel, no se investigó a fondo
  porque el usuario pidió detener el trabajo en el informe y solo
  documentar). Pendiente para la próxima sesión.

## Pendiente

1. ~~**Verificación visual real** (captura de pantalla) del modal rediseñado
   — solo se confirmó por texto del DOM.~~ **Hecha el 07/08/2026** — ver
   [`docs/2026-08-07-verificacion-visual-y-nombre-bancoldex.md`](2026-08-07-verificacion-visual-y-nombre-bancoldex.md).
   El modal es correcto; la revisión visual destapó un defecto de CSS que la
   inspección por texto no podía ver (el rótulo del gauge cruzaba el anillo),
   ya corregido.
2. **Definir con el usuario** cómo se valida qué incidentes de Aranda son
   "atribuibles a SETI" (hoy usa una cifra provisional — categoría
   `Incidente` excluyendo `Incidente - Monitoreo` — sin ningún cruce de
   atribución real equivalente al log de indisponibilidades de GLPI). No
   avanzar en esto sin acordarlo primero.
3. Todo lo demás pendiente del change sigue igual — ver `tasks.md`.
