# Automatización del Informe Mensual — Cardio Infantil

Replica, para el cliente Cardio Infantil, el patrón construido originalmente
para Acción Fiduciaria: un informe interactivo en HTML alimentado por
extractores automáticos que reemplazan la carga manual de datos. Ver
`docs/2026-08-03-inventario-tarjetas-cardio-infantil.md` para el mapeo
tarjeta por tarjeta contra la evidencia real de Cardio Infantil.

## Estado actual

| Pieza | Estado |
|---|---|
| `.env.ejemplo` | Listo — usa App-Token + User-Token desde el día uno (a diferencia de Acción Fiduciaria, que arrancó con usuario/contraseña personal y hoy lo arrastra como deuda técnica) |
| Sonda GLPI (`sonda_glpi.py`) | Lista para correr — pendiente confirmar credenciales, entidad real, y ahora también lista los `searchOptions` de `Ticket` para construir el extractor sin adivinar IDs |
| `insumos_cardio.py` | Funciones de empaquetado portadas y funcionando (paquete base64+hash, periodo, resguardo, incrustación en el HTML). **`clasificar_caso_cardio()` deliberadamente sin terminar** — levanta `NotImplementedError`, ver su docstring |
| `historico_casos.py` | Listo — ledger genérico, con un campo `casos_bd` que Acción Fiduciaria no tiene |
| Extractor GLPI (`extraer_glpi.py`) | **No creado todavía.** Depende de correr la sonda contra la instancia real y confirmar los `searchOptions` — no se van a copiar los IDs de columna de Acción Fiduciaria, pueden no coincidir |
| Fuente de monitoreo (Zabbix, a confirmar) | Pendiente sondear — ver preguntas abiertas del inventario de tarjetas |
| Informe interactivo (HTML) | Pendiente — se adapta desde el de Acción Fiduciaria una vez haya al menos una fuente real funcionando |
| Orquestador (`actualizar_informe.py`) | Pendiente — se construye al final, mismo orden que siguió Acción Fiduciaria |

## Por qué no hay `extraer_alertas.py` ni `sonda_alertops.py`

Acción Fiduciaria necesita un segundo sistema (AlertOps) porque sus alertas
no viven en GLPI. Cardio Infantil, según el consolidado manual que ya
revisamos (`Dta junio.xlsx`, hoja `Alerta_SO`), reporta sus alertas también
como tickets de GLPI — un solo extractor debería bastar. Se confirma (no se
asume) en el mismo paso de la sonda.

## Paso 1: correr la sonda de GLPI

```bash
cd automatizacion
cp .env.ejemplo .env
# completar GLPI_URL, GLPI_APP_TOKEN y GLPI_USER_TOKEN en .env
python3 sonda_glpi.py
```

La sonda no escribe nada ni modifica producción — solo imprime en consola.
Confirma, contra la instancia real:

1. El id/nombre exacto de la entidad "Cardio Infantil".
2. Si existe una categoría equivalente a `INCIDENTES > Revisión Alerta`
   (la que en Acción Fiduciaria se excluye del conteo de incidentes
   atribuibles a SETI porque la genera el propio monitoreo, no el cliente).
3. Los `searchOptions` reales de `Ticket` — la fuente de los IDs de columna
   que va a usar `extraer_glpi.py`, para no adivinar ni copiar los de otro
   cliente.

## Paso 2 (bloqueado hasta tener el resultado del paso 1)

Con los tres datos anteriores confirmados:

1. Escribir `clasificar_caso_cardio()` en `insumos_cardio.py` — hoy es un
   `NotImplementedError` a propósito.
2. Construir `extraer_glpi.py`, con los `searchOptions` reales.

## Por qué este orden

Se sigue el mismo método de "reconocimiento antes que construcción" que ya
usó el equipo en Acción Fiduciaria (ver sección 11 de su documentación):
nunca se asume que los identificadores de campo (entidad, categoría, SLA)
son iguales entre clientes, aunque compartan la misma plataforma (GLPI). Por
la misma razón, este README no incluye un extractor a medias con IDs
adivinados: un extractor que falla en silencio con datos incorrectos es peor
que no tener extractor.
