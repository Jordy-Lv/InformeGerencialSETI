# Inventario de tarjetas — Cardio Infantil

**Fecha:** 3 de agosto de 2026
**Propósito:** definir, tarjeta por tarjeta, cuáles del patrón ya construido para
Acción Fiduciaria se reutilizan tal cual para Cardio Infantil, cuáles se adaptan
y cuáles son nuevas — antes de tocar código.

**Método:** el mismo que ya usa el equipo — reconocimiento antes que
construcción. Cada fila de la tabla está respaldada por evidencia real ya
revisada: el consolidado `Dta junio.xlsx` (export de GLPI, entidad "FUNDACIÓN
CARDIOINFANTIL SO"), el PPTX `Informe Gestion Cardio_ Junio_ 2026.pptx`, y el
HTML de producción `informe-accion-fiduciaria 1.html`. Donde no hay evidencia,
la tabla dice "pendiente de sondeo" en vez de asumir.

## Tarjetas heredadas del patrón de Acción Fiduciaria

| # | Tarjeta (id) | Qué muestra en Acción Fiduciaria | Fuente en Acción Fiduciaria | Evidencia en Cardio Infantil | Fuente propuesta para Cardio | Estado |
|---|---|---|---|---|---|---|
| 1 | **Indicadores del servicio** | % disponibilidad, % gestión del servicio, % cumplimiento de entregables | Consolidado mensual + GLPI | Slides 2-3 del PPT muestran los mismos 3 % (100/100/100), pero **no están en ningún Excel que hayamos visto** | Sin confirmar | 🟡 Adaptar — estructura reutilizable, falta el dato de origen |
| 2 | **Total de casos** | Alertas + requerimientos + incidentes, incl. atribuibles a SETI | GLPI (`extraer_glpi.py`) + AlertOps (`extraer_alertas.py`) | `Dta junio.xlsx`: hoja Reque_SO (62) + hoja Alerta_SO (10), ambas ya verificadas contra las tablas dinámicas del Excel | **Solo GLPI** — Cardio no usa AlertOps, las alertas también son tickets de GLPI | 🟢 Reutilizable — con clasificación propia (ver más abajo) |
| 3 | **Disponibilidad global** | % disponibilidad por motor de BD, contra una meta | Consolidado de disponibilidad + `DisponibilidadMensual.xlsx` (atribución a SETI) | Slide 3 (100% plataforma), sin desglose por motor en el Excel revisado | Sin confirmar — candidato: Zabbix | 🔴 Pendiente de sondeo |
| 4 | **Gestión de backups** | Resultado de backups del período | Consolidado manual de backups | Slide 6 "Estado de Respaldos" es una **captura de pantalla**, no datos estructurados | Sin confirmar — depende de qué consola de backup usan | 🔴 Pendiente de sondeo |
| 5 | **Logros del servicio** | Texto cualitativo cargado a mano cada mes | Archivo cualitativo mensual | Slide 5 del PPT tiene exactamente este contenido (bloques "Tratamiento / Beneficio": permisos AD, parchado CredSSP, servidores Linux para BI, etc.) | Mismo mecanismo de carga cualitativa | 🟢 Reutilizable directamente |
| 6 | **Mitigaciones y riesgos gestionados** | Texto cualitativo, riesgos mitigados | Mismo archivo cualitativo, columna aparte | Parte del mismo contenido de slide 5 (vulnerabilidad CredSSP, depuración NAS Isilon, alarmas falsas positivas en Zabbix) | Mismo mecanismo | 🟢 Reutilizable directamente |
| 7 | **Bolsa de horas contratada** | Saldo asignado/consumido, se configura a mano en el HTML por diseño | Manual, no viene de insumo automático | No hay evidencia de este concepto en el Excel ni el PPT de Cardio | Sin confirmar si el contrato de Cardio maneja bolsa de horas | 🔴 Pendiente confirmar con el contrato |
| 8 | **Disponibilidad por sistema (radar CI)** | Radar de disponibilidad por sistema/motor contra meta | Igual que tarjeta 3, desagregado por CI | Slide 6 menciona CPU / Almacenamiento / Backups por instancia (CLDBSPROD01, SCCM, SQLLAB3) — concepto similar, **métricas distintas** (CPU/storage, no solo disponibilidad) | Sin confirmar — candidato: Zabbix | 🟡 Adaptar — mismo concepto de radar, dimensiones propias de Cardio |

**Leyenda de estado:** 🟢 reutilizable tal cual (mismo mecanismo/UI, solo cambia el insumo) · 🟡 adaptar (la estructura sirve, hay que rediseñar la fuente o las métricas) · 🔴 pendiente de sondeo (no hay fuente confirmada todavía, no se debe asumir una).

## Tarjeta nueva: Casos de Base de Datos

No existe equivalente directo en Acción Fiduciaria — Cardio Infantil separa
explícitamente los casos de BD del resto de requerimientos de sistema
operativo, con su propio flujo de trabajo (técnico asignado, solución).

- **Fuente confirmada:** `Dta junio.xlsx`, hoja "Requerimientos BD" — 10
  columnas (incluye `Asignado a - Técnico`, `Prioridad`, `Solucion -
  Solucion`, que las otras dos hojas no tienen).
- **Cifra ya verificada:** 19 casos en junio 2026 (total general de la tabla
  dinámica de esa hoja), consistente con lo que hoy se teclea a mano en la
  diapositiva 4 del PPT ("19 Casos de Base de Datos").
- **Por qué es una tarjeta propia y no una variante de "Total de casos":**
  el consolidado ya la trata como una población separada (hoja propia +
  columnas propias de gestión técnica), y el PPT actual también la reporta
  aparte.

## Regla de clasificación: por qué no se puede copiar `clasificar_caso_glpi()`

Acción Fiduciaria separa alertas de incidentes por **categoría** de ticket
(excluye `INCIDENTES > Revisión Alerta` porque la genera el propio
monitoreo). Cardio Infantil, según la evidencia del Excel, separa sus casos
por **hoja/tipo de origen** (Reque_SO / Alerta_SO / Requerimientos BD), no por
ese patrón de categoría. Esto significa que hace falta una función propia
(`clasificar_caso_cardio`), no reutilizar la de Acción Fiduciaria — se
confirma en la sonda GLPI de Cardio (`cardio-infantil/sonda_glpi.py`, sección
"categorías de tickets"), aún pendiente de correr con credenciales reales.

## Preguntas abiertas (no asumir, sondear)

1. ¿Cuál es la herramienta de monitoreo real? El texto de la diapositiva 5
   menciona **Zabbix** explícitamente ("revisión, manejo y categorización de
   alarmas en Zabbix") — es el candidato más fuerte para las tarjetas 3, 4 y
   8, pero falta confirmarlo con una sonda a su API antes de construir nada.
2. ¿De dónde salen los tres porcentajes de la tarjeta "Indicadores del
   servicio" (disponibilidad, gestión del servicio, entregables) si no están
   en `Dta junio.xlsx`? Puede ser Zabbix, puede ser un registro manual aparte.
3. ¿El contrato de Cardio Infantil incluye bolsa de horas? No hay evidencia
   ni a favor ni en contra todavía.
4. ¿Cuál es la consola de backups que usan (para la tarjeta 4)?

## Próximos pasos sugeridos

1. Correr `sonda_glpi.py` de Cardio con credenciales reales → confirmar
   entidad exacta y la ausencia/presencia de una categoría equivalente a
   "Revisión Alerta".
2. Diseñar y validar `clasificar_caso_cardio()` contra los datos reales de
   `Dta junio.xlsx` (las 3 hojas) antes de escribir el extractor.
3. Sondear Zabbix (script de reconocimiento, sin escribir nada) para resolver
   las preguntas 1 y 2 de la sección anterior.
4. Resolver las preguntas 3 y 4 con el equipo de cuenta, no por inferencia.
