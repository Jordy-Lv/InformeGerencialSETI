# Automatización del Informe Mensual — Cardio Infantil

Replica, para el cliente Cardio Infantil, el patrón construido originalmente
para Acción Fiduciaria: un informe interactivo en HTML alimentado por
extractores automáticos que reemplazan la carga manual de datos.

## Estado actual

| Pieza | Estado |
|---|---|
| Sonda GLPI (`sonda_glpi.py`) | Lista para correr — pendiente confirmar credenciales y entidad real |
| Extractor GLPI (`extraer_glpi.py`) | Pendiente — depende del resultado de la sonda |
| Fuente de monitoreo SQL | Pendiente identificar la herramienta (Zabbix / SolarWinds / PRTG / otra) |
| Informe interactivo (HTML) | Pendiente — se adapta desde el de Acción Fiduciaria, con paneles propios de Cardio (matriz SQL, diagnóstico por instancia) |
| Orquestador (`actualizar_informe.py`) | Pendiente — se construye al final, cuando haya al menos una fuente automática funcionando |

## Paso 1: correr la sonda de GLPI

```bash
cd automatizacion
cp .env.ejemplo .env
# completar GLPI_URL, GLPI_APP_TOKEN y GLPI_USER_TOKEN en .env
python3 sonda_glpi.py
```

La sonda no escribe nada ni modifica producción — solo lista entidades y
categorías reales de la instancia de GLPI, para confirmar:

1. El id/nombre exacto de la entidad "Cardio Infantil".
2. Si existe una categoría equivalente a `INCIDENTES > Revisión Alerta`
   (la que en Acción Fiduciaria se excluye del conteo de incidentes
   atribuibles a SETI porque la genera el propio monitoreo, no el cliente).

Con esos dos datos confirmados se construye `extraer_glpi.py`, el
extractor real.

## Por qué este orden

Se sigue el mismo método de "reconocimiento antes que construcción" que ya
usó el equipo en Acción Fiduciaria (ver sección 11 de su documentación):
nunca se asume que los identificadores de campo (entidad, categoría, SLA)
son iguales entre clientes, aunque compartan la misma plataforma (GLPI).
