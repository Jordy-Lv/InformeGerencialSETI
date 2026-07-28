#!/bin/bash
# Tarea programada mensual — corre GLPI + AlertOps y deja el informe listo.
#
# Uso en crontab, el primero de cada mes a la 1:00 a. m.:
#   0 1 1 * * /ruta/al/proyecto/automatizacion/tarea_mensual.sh
#
# No lleva --abrir: en un servidor sin pantalla no hay quien vea el navegador.
# No necesita --periodo: actualizar_informe.py calcula solo el mes que cerró.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

mkdir -p automatizacion/salida
LOG="automatizacion/salida/tarea_mensual.log"
FECHA=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== $FECHA ===" >> "$LOG"
python3 automatizacion/actualizar_informe.py >> "$LOG" 2>&1
CODIGO=$?

if [ $CODIGO -ne 0 ]; then
  echo "FALLÓ (código $CODIGO) — $FECHA" >> "$LOG"
  # Alerta ante fallo: descomentar cuando exista el webhook de Teams y quede
  # definido TEAMS_WEBHOOK_URL (en este mismo archivo o en el entorno del cron).
  # curl -s -X POST -H 'Content-Type: application/json' \
  #   -d "{\"text\":\"Automatización GLPI/AlertOps falló el ${FECHA} (código ${CODIGO}). Revisar ${LOG} en el servidor.\"}" \
  #   "$TEAMS_WEBHOOK_URL"
else
  echo "OK — $FECHA" >> "$LOG"
fi

exit $CODIGO
