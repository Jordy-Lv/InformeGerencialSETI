# Inventario de tarjetas

**Fecha:** 3 de agosto de 2026 (recuperado a `docs/` el 4 de agosto de 2026, tras cerrarse sin mergear el PR #1 original).

**Qué es esto:** el primer insumo de diseño para volver el informe multicliente
por *configuración*, no por copia. No es un anexo del cliente Cardio Infantil
— es el ejercicio que, repetido por cada tarjeta del informe, debería producir
la especificación del contrato de tarjeta (id, dominios que consume, tipo de
gráfico, validaciones, qué muestra en cada uno de los 5 estados de
`REPORTE`) y, a partir de ahí, el perfil de cliente como dato. Cardio
Infantil es el caso de prueba: el cliente que no comparte AlertOps, que
separa sus casos por hoja de origen en vez de por categoría de ticket, y que
por eso obliga a que el diseño del contrato sea genuinamente general y no una
generalización a posteriori de lo que ya hacía Acción Fiduciaria.

**Método:** reconocimiento antes que construcción — el mismo que ya usa el
equipo para GLPI y AlertOps. Cada fila de la tabla está respaldada por
evidencia real ya revisada: el consolidado `Dta junio.xlsx` de Cardio
Infantil (export de GLPI, entidad "FUNDACIÓN CARDIOINFANTIL SO"), su PPTX
`Informe Gestion Cardio_ Junio_ 2026.pptx`, y el HTML de producción
`informe-accion-fiduciaria 1.html`. Donde no hay evidencia, la tabla dice
"pendiente de sondeo" en vez de asumir.

## Tarjetas de Acción Fiduciaria, vistas desde un segundo cliente

| # | Tarjeta (id) | Qué muestra en Acción Fiduciaria | Fuente en Acción Fiduciaria | Evidencia en Cardio Infantil | Fuente propuesta para Cardio | ¿Es la misma regla de negocio, o solo cambia un identificador? |
|---|---|---|---|---|---|---|
| 1 | **Indicadores del servicio** | % disponibilidad, % gestión del servicio, % cumplimiento de entregables | Consolidado mensual + GLPI | Slides 2-3 del PPT muestran los mismos 3 % (100/100/100), pero **no están en ningún Excel que hayamos visto** | Sin confirmar | Estructura igual, fuente distinta — pendiente de sondeo, no de diseño |
| 2 | **Total de casos** | Alertas + requerimientos + incidentes, incl. atribuibles a SETI | GLPI (`extraer_glpi.py`) + AlertOps (`extraer_alertas.py`) | `Dta junio.xlsx`: hoja Reque_SO (62) + hoja Alerta_SO (10), ambas ya verificadas contra las tablas dinámicas del Excel | **Solo GLPI** — Cardio no usa AlertOps, las alertas también son tickets de GLPI | Identificador (fuente de alertas) — configuración, no código nuevo |
| 3 | **Disponibilidad global** | % disponibilidad por motor de BD, contra una meta | Consolidado de disponibilidad + `DisponibilidadMensual.xlsx` (atribución a SETI) | Slide 3 (100% plataforma), sin desglose por motor en el Excel revisado | Sin confirmar — candidato: Zabbix | Pendiente de sondeo |
| 4 | **Gestión de backups** | Resultado de backups del período | Consolidado manual de backups | Slide 6 "Estado de Respaldos" es una **captura de pantalla**, no datos estructurados | Sin confirmar — depende de qué consola de backup usan | Pendiente de sondeo |
| 5 | **Logros del servicio** | Texto cualitativo cargado a mano cada mes | Archivo cualitativo mensual | Slide 5 del PPT tiene exactamente este contenido (bloques "Tratamiento / Beneficio": permisos AD, parchado CredSSP, servidores Linux para BI, etc.) | Mismo mecanismo de carga cualitativa | Misma regla exacta — cero cambios |
| 6 | **Mitigaciones y riesgos gestionados** | Texto cualitativo, riesgos mitigados | Mismo archivo cualitativo, columna aparte | Parte del mismo contenido de slide 5 (vulnerabilidad CredSSP, depuración NAS Isilon, alarmas falsas positivas en Zabbix) | Mismo mecanismo | Misma regla exacta — cero cambios |
| 7 | **Bolsa de horas contratada** | Saldo asignado/consumido, se configura a mano en el HTML por diseño | Manual, no viene de insumo automático | No hay evidencia de este concepto en el Excel ni el PPT de Cardio | Sin confirmar si el contrato de Cardio maneja bolsa de horas | Pendiente confirmar con el contrato |
| 8 | **Disponibilidad por sistema (radar CI)** | Radar de disponibilidad por sistema/motor contra meta | Igual que tarjeta 3, desagregado por CI | Slide 6 menciona CPU / Almacenamiento / Backups por instancia (CLDBSPROD01, SCCM, SQLLAB3) — concepto similar, **métricas distintas** (CPU/storage, no solo disponibilidad) | Sin confirmar — candidato: Zabbix | Regla parcialmente distinta: mismo concepto de radar, dimensiones propias de Cardio |

## Tarjeta que no tiene equivalente en Acción Fiduciaria

**Casos de Base de Datos** — no es una variante de "Total de casos": Cardio
Infantil separa explícitamente los casos de BD del resto de requerimientos
de sistema operativo, con su propio flujo de trabajo (técnico asignado,
solución registrada).

- **Fuente confirmada:** `Dta junio.xlsx`, hoja "Requerimientos BD" — 10
  columnas (incluye `Asignado a - Técnico`, `Prioridad`, `Solucion -
  Solucion`, que las otras dos hojas no tienen).
- **Cifra ya verificada:** 19 casos en junio 2026 (total general de la tabla
  dinámica de esa hoja) y, por separado, verificado extremo a extremo con el
  parser real contra el archivo real (ver PR #6, cerrado por bifurcar el
  proyecto pero con esta cifra confirmada dos veces por caminos distintos):
  62 requerimientos, 10 alertas, 19 casos de BD.
- **Por qué es una tarjeta propia y no una variante:** el consolidado ya la
  trata como una población separada (hoja propia + columnas propias de
  gestión técnica), y el PPT actual también la reporta aparte. Esta es la
  prueba de que la regla de negocio es genuinamente distinta, no solo un
  identificador — el criterio que separa "esto va al núcleo" de "esto va al
  perfil del cliente".

## Por qué `clasificar_caso_glpi()` no basta como está

Acción Fiduciaria separa alertas de incidentes por **categoría** de ticket
(excluye `INCIDENTES > Revisión Alerta` porque la genera el propio
monitoreo). Cardio Infantil, según la evidencia del Excel, separa sus casos
por **hoja/tipo de origen** (Reque_SO / Alerta_SO / Requerimientos BD) — un
patrón distinto. Esta es, con la tarjeta de Casos de BD, la segunda señal
concreta de que el contrato de tarjeta necesita una noción explícita de
"regla de clasificación del perfil", no una función fija compartida. Se
confirma (no se asume) en la sonda GLPI de Cardio
(`cardio-infantil/sonda_glpi.py` — pendiente de reincorporar cuando exista
el sistema de perfil), aún pendiente de correr con credenciales reales.

## Preguntas abiertas (no asumir, sondear)

1. ¿Cuál es la herramienta de monitoreo real de Cardio Infantil? El texto de
   la diapositiva 5 menciona **Zabbix** explícitamente ("revisión, manejo y
   categorización de alarmas en Zabbix") — candidato más fuerte para las
   tarjetas de disponibilidad, backups y el radar por sistema, pero falta
   confirmarlo con una sonda a su API antes de construir nada.
2. ¿De dónde salen los tres % de "Indicadores del servicio" de Cardio si no
   están en `Dta junio.xlsx`? Puede ser Zabbix, puede ser un registro manual
   aparte.
3. ¿El contrato de Cardio Infantil incluye bolsa de horas?
4. ¿Cuál es la consola de backups que usa Cardio Infantil hoy?

## Próximos pasos (orden propuesto en el review del PR #5)

1. Este documento (recuperado).
2. Especificación del contrato de tarjeta: id, dominios que consume, tipo de
   gráfico permitido, validaciones que exige para pintarse, qué muestra
   cuando su dominio está en cada uno de los 5 estados de `REPORTE`.
3. Perfil de cliente como dato: nombre, entidad GLPI, fuentes disponibles,
   tarjetas activas y su orden, criterios de validación aplicables —
   `criteriosCarga()` y `DOMINIOS` en `informe-accion-fiduciaria 1.html`
   pasan a derivarse de ahí en vez de estar fijos.
4. Migrar las 10 tarjetas actuales de Acción Fiduciaria al inventario, sin
   cambiar una sola cifra — el informe de julio tiene que salir byte por
   byte igual. Criterio de aceptación de este paso.
5. Cardio Infantil entra como el segundo perfil. Si necesita tocar el motor
   para funcionar, el diseño del contrato todavía no está bien.
6. Recién ahí: modal de selección de tarjetas y presets por cliente.
