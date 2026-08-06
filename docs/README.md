# Histórico de sesiones

Cada archivo narra una sesión de trabajo: qué se hizo, con qué comandos se
verificó y qué quedó pendiente. **El orden cronológico no equivale a
vigencia** — un documento de julio puede seguir mandando y uno del 4 de
agosto puede estar superado por el del 5. Por eso esta tabla lleva estado.

## Cómo leer la columna «Estado»

| Estado | Significa |
|---|---|
| **Vigente** | Describe cómo funciona el sistema hoy. Si vas a tocar esa zona, léelo |
| **Referencia** | Levantamiento, contrato con un tercero o inventario. No caduca, pero no manda sobre el código |
| **Superado** | Lo que cuenta ya fue corregido o reemplazado. Se conserva por el razonamiento, no por la conclusión |

## Empieza por aquí

| Documento | Para qué |
|---|---|
| [Plan maestro multicliente](2026-08-04-plan-multicliente.md) | El documento más importante del repositorio: arquitectura objetivo, las once fases con criterio de aceptación, riesgos y estado de ejecución |
| [Patrones de diseño](PATRONES.md) | Los siete patrones adoptados y los descartados, con el motivo de cada uno |
| [Requisitos del producto](requisitos-producto.md) | Qué debe hacer el informe y con qué se verifica cada requisito |

---

## Agosto de 2026 — migración multicliente

| Fecha | Documento | Estado | Tema |
|---|---|---|---|
| 05 | `2026-08-05-f2-contrato-perfil.md` — todavía en la rama `codex/f2-contrato-perfil`, no en `main` | En curso | `PERFIL.contrato.inicio` sustituye seis lecturas del DOM. **A/B en cero pendiente** |
| 05 | [Fundación documental](2026-08-05-fundacion-documental.md) | Vigente | Esta capa de documentación: README, CLAUDE.md, DESIGN.md, índice y archivado de changes |
| 04 | [Plan maestro multicliente](2026-08-04-plan-multicliente.md) | Vigente | Arquitectura objetivo, fases F0–F11, riesgos, estado de ejecución |
| 04 | [F1 — perfil de Acción Fiduciaria](2026-08-04-f1-perfil-accion-fiduciaria.md) | Vigente | Perfil como datos puros, `resolverPerfil()`, claves de almacén. Cerrado con A/B en cero |
| 04 | [F0 — dorados para el A/B](2026-08-04-f0-dorados-verificacion.md) | Vigente | Huellas SHA-256 versionables sin exponer cifras del cliente |
| 04 | [F0 — arnés de verificación A/B](2026-08-04-f0-verificar-ab.md) | Vigente | `verificar_ab.py`, el instrumento que respalda la restricción #2 |
| 04 | [F0 — fundación de OpenSpec](2026-08-04-f0-openspec-fundacion.md) | Vigente | Origen de `project.md` y `AGENTS.md` |
| 04 | [Spec del store `REPORTE`](2026-08-04-spec-store-reporte.md) | Vigente | Los cinco estados por dominio y la rehidratación del entregable |
| 04 | [Bolsa de horas entre periodos](2026-08-04-bolsa-de-horas-persiste-entre-periodos.md) | Vigente | Corrección: la tarjeta persistía sin editar al cambiar de periodo |
| 04 | [Corrección de recarga de insumos](2026-08-04-correccion-recarga-de-insumos.md) | Vigente | Arreglo de los hallazgos de la validación del mismo día |
| 04 | [Validación de recarga de insumos](2026-08-04-validacion-recarga-de-insumos.md) | Superado | El diagnóstico; la corrección está en el documento anterior |
| 03 | [Inventario de tarjetas](2026-08-03-inventario-tarjetas-cardio-infantil.md) | Referencia | Inventario completo de tarjetas y el razonamiento del PR #5 cerrado sin fusionar |
| 02 | [Corrección de la auditoría + A/B](2026-08-02-correccion-de-la-auditoria-y-verificacion-ab.md) | Vigente | Correcciones aplicadas y verificación A/B de la auditoría |
| 02 | [Auditoría de insumos → HTML](2026-08-02-auditoria-insumos-glpi-alertops-disponibilidad.md) | Superado | El diagnóstico; las correcciones están en el documento anterior |

## Julio de 2026 — automatización e insumos

| Fecha | Documento | Estado | Tema |
|---|---|---|---|
| 29 | [Pruebas en Windows y correcciones en vivo](2026-07-29-pruebas-en-windows-y-correcciones-en-vivo.md) | Vigente | Despliegue real en Windows. **Aquí se corrigió la regla de atribución SETI: solo un «SI» explícito cuenta** |
| 29 | [Relevo de sesión del 28 de julio](2026-07-29-relevo-sesion-28-julio.md) | Referencia | Traspaso de contexto entre sesiones |
| 28 | [Levantamiento de disponibilidad de BD](2026-07-28-disponibilidad-bd-levantamiento.md) | Referencia | Propuesta para automatizar la disponibilidad de bases de datos |
| 28 | [Contrato técnico de extracción](2026-07-28-contrato-tecnico-mateo.md) | Referencia | Contrato con el tercero que provee la extracción de disponibilidad |
| 23 | [Análisis por rango y redondeo](2026-07-23-analisis-por-rango-y-redondeo.md) | Vigente | El cumplimiento se juzga sobre el valor publicado, con un decimal |
| 22 | [Backups adoptan el radar de CI](2026-07-22-backups-radar-ci.md) | Vigente | Unificación visual del modal de backups con el de Disponibilidad por CI |
| 22 | [Bolsa de horas editable](2026-07-22-bolsa-horas-manual.md) | Vigente | Origen de la bolsa de horas manual |
| 22 | [Modal de casos atendidos](2026-07-22-casos-analisis.md) | Vigente | Rediseño funcional y análisis editable |
| 22 | [Disponibilidad global](2026-07-22-disponibilidad-historico.md) | Vigente | Meta visible e histórico por motor |
| 22 | [Indicadores del servicio](2026-07-22-indicadores-historico.md) | Vigente | Modal histórico reutilizable |

## Sin fecha en el nombre

| Documento | Estado | Tema |
|---|---|---|
| [Auditoría de integridad de datos](AUDITORIA_DATOS_Y_RELEVO_CLAUDE.md) | Vigente | Decisiones de integridad que siguen aplicando |

---

## La plantilla obligatoria y desde cuándo aplica

Desde el commit `c278818` («Formaliza la actualización documental por
cambio», 4 de agosto de 2026), todo documento de sesión **debe** tener estas
cinco secciones, y así lo exige `openspec/AGENTS.md`:

```markdown
## Contexto              Qué problema había y por qué se abordó ahora
## Qué se implementó     El cambio real, no la intención
## Verificación realizada  Cada afirmación con su comando y su resultado
## Archivos tocados      Incluye documentación y pruebas, no solo código
## Pendiente             Lo que quedó abierto, dicho sin adornos
```

Los documentos anteriores a esa fecha **no la siguen**, y es correcto: son
histórico, no se reescriben. No los tomes como ejemplo de formato — sí de
nivel de detalle.

La regla que sostiene todo esto: **una prueba no ejecutada se marca como
pendiente, nunca como implícitamente aprobada.** El documento de F2 del 5 de
agosto es el mejor ejemplo: reporta su propio A/B fallido con las
diferencias que encontró, en vez de presentarlo como cerrado.

## Documentos citados que ya no existen

Aparecen citados en documentos antiguos. Cada referencia quedó anotada en el
texto para que nadie los busque en vano, **pero no faltan por la misma
razón**:

| Documento | Por qué no está |
|---|---|
| `2026-07-22-backups-historico.md` | **Borrado a propósito** el 29/07/2026, con autorización: describía la matriz de backups que el radar de CI reemplazó el mismo día |
| `2026-07-23-sesion-completa.md` | **Borrado a propósito** el 29/07/2026: era la versión larga de `2026-07-23-analisis-por-rango-y-redondeo.md`, y se conservó la corta |
| `2026-07-28-desarrollo-mac-despliegue-windows.md` | **Sin resolver.** No figura en la tabla de borrados autorizados: o nunca se subió, o se perdió. Lo citaba `automatizacion/README.md` como la guía de despliegue en Windows |

Las dos primeras bajas están justificadas en la tabla de borrados del
[relevo del 29 de julio](2026-07-29-relevo-sesion-28-julio.md), que también
deja registrado —y sigue sin resolver— que `automatizacion/README.md`
referencia dos `.docx` que tampoco existen en el repositorio.
