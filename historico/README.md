# Versiones históricas

Archivo muerto. **La versión vigente es `../informe-accion-fiduciaria.html`.**

Estos archivos se conservan solo como referencia. No los edites ni los abras
para consultar el informe: contienen defectos ya corregidos que producen cifras
falsas (ver abajo).

| Archivo | Fecha | Qué es |
|---|---|---|
| `index 3.html` | 18 jul 2026 | Base más antigua del informe (111 funciones JS). |
| `informe-accion-fiduciaria.BACKUP-pre-store.html` | 19 jul 2026 | Respaldo tomado justo antes de introducir el store canónico `REPORTE` (140 funciones JS). |

## Por qué quedaron obsoletos

La versión vigente reescribió el flujo de datos sobre un store canónico
(`REPORTE`) con estados explícitos por dominio, y con ello corrigió varios
defectos que hacían que el informe publicara cifras que no venían de los
insumos:

- `DATA_CASOS` traía datos semilla hardcodeados (`alertas:[54,30,61]`) que se
  propagaban a la tarjeta, al gráfico y al PDF como si fueran del periodo.
- Un GLPI sin filas del mes daba el criterio por cumplido y habilitaba el PDF
  con un SLA ficticio.
- El modal de backups inventaba cuatro nodos de plantilla (SQL, Mysql, Oracle,
  AWS) cuando la hoja no se podía leer.
- El estado de un riesgo se deducía con una expresión regular sobre su
  descripción, lo que podía convertir un riesgo abierto en «Gestionado».
- El filtro cualitativo no exigía cliente y periodo simultáneamente, así que
  podían colarse filas de otros clientes.

Comparación completa: 1.162 líneas añadidas, 150 reescritas, 18 funciones
nuevas. Ninguna función ni ningún `id` del DOM se perdió en la migración
(`estadoRiesgoGestionado` fue reemplazada a propósito por `estadoRiesgo`).
