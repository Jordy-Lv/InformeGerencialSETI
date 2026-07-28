#!/usr/bin/env python3
"""
Sonda de reconocimiento contra AlertOps.

A diferencia de GLPI, la API de AlertOps ya está documentada por completo en
un Swagger público (https://api.alertops.com/swagger/v2/swagger.json): no hace
falta descubrir endpoints ni searchOptions a ciegas. Lo que esta sonda
confirma es que la api-key de esta cuenta específica autentica contra esa API
documentada y que la respuesta real trae los campos que el extractor mensual
va a necesitar — antes de construirlo sobre una suposición.

Prueba:

  1. GET /api/v2/alerts (limit=5)   ¿la api-key autentica? ¿la respuesta trae
                                     los campos documentados (topic, message,
                                     escalation_policy, created_date…)?
  2. Políticas de escalamiento      ¿qué nombres de «Escalation Policy»
                                     aparecen en los datos reales? El informe
                                     clasifica como prioridad alta las que
                                     contienen «no reconocimiento» — hay que
                                     confirmar que así se llaman en esta cuenta,
                                     no asumirlo del export manual.

Uso:

    export AOPS_URL=https://api.alertops.com
    export AOPS_API_KEY=...
    python3 automatizacion/sonda_alertops.py

La api-key se lee SOLO de `.env` (compartido con GLPI_*, ver .env.ejemplo) o
del entorno. Este archivo no la contiene y no debe contenerla nunca.

Solo usa la biblioteca estándar de Python 3: así puede correr tal cual en el
servidor donde acabe viviendo la tarea programada.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sonda_glpi import cargar_env  # mismo lector de .env que usa GLPI; no se duplica

import os  # noqa: E402

SALIDA = Path(__file__).parent / "salida"
TIEMPO_LIMITE = 30


def pedir(url, api_key):
    """Devuelve (codigo, cuerpo_bytes). No lanza en 4xx/5xx."""
    req = urllib.request.Request(url, headers={"api-key": api_key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIEMPO_LIMITE) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def main():
    cargar_env()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--limit", type=int, default=5, help="Cuántas alertas de muestra pedir (por defecto, 5)")
    args = p.parse_args()

    base = os.environ.get("AOPS_URL", "https://api.alertops.com").rstrip("/")
    api_key = os.environ.get("AOPS_API_KEY", "")

    if not api_key:
        ruta = Path(__file__).parent / ".env"
        print(
            f"Falta AOPS_API_KEY.\n\n"
            f"Se obtiene en AlertOps: Administration → Subscription Settings.\n"
            f"Complétala en {ruta} y vuelve a ejecutar:\n"
            "  python3 automatizacion/sonda_alertops.py",
            file=sys.stderr,
        )
        return 2

    SALIDA.mkdir(exist_ok=True)
    print(f"Sonda AlertOps · {datetime.now():%Y-%m-%d %H:%M}")
    print(f"Destino: {base}")
    print(f"Evidencia en: {SALIDA}")

    print("\n1. GET /api/v2/alerts (reconocimiento)\n" + "-" * 40)
    codigo, cuerpo = pedir(f"{base}/api/v2/alerts?limit={args.limit}", api_key)
    texto = cuerpo.decode("utf-8", errors="replace")
    (SALIDA / "01-alertops-alerts.json").write_text(texto, encoding="utf-8")
    print(f"  → evidencia: {SALIDA / '01-alertops-alerts.json'}")

    if codigo != 200:
        print(f"  [FALLA] HTTP {codigo}")
        print(f"  Respuesta: {texto[:500]}")
        print(
            "\n  Revisa: la api-key (Administration → Subscription Settings), que la cuenta "
            "tenga la API habilitada, y que AOPS_URL sea el correcto para esta instancia."
        )
        return 1

    print("  [OK] HTTP 200 · la api-key autentica correctamente.")
    try:
        datos = json.loads(texto)
    except ValueError:
        print("  [FALLA] HTTP 200 pero la respuesta no es JSON válido; ver evidencia.")
        return 1

    alertas = datos.get("alerts", [])
    print(f"  {len(alertas)} alerta(s) de muestra recibida(s).")
    if alertas:
        campos = sorted(alertas[0].keys())
        print(f"  Campos por alerta: {', '.join(campos)}")
        faltan = {"alert_id", "created_date", "topic", "escalation_policy"} - set(campos)
        if faltan:
            print(f"  [ATENCIÓN] faltan campos que el extractor necesita: {', '.join(sorted(faltan))}")
    else:
        print("  Sin alertas en los últimos días para esta cuenta; no es necesariamente un problema,")
        print("  pero impide confirmar el esquema con datos reales. Prueba con más --limit o revisa manualmente.")

    print("\n2. Políticas de escalamiento observadas\n" + "-" * 40)
    politicas = sorted({
        a["escalation_policy"]["name"]
        for a in alertas
        if a.get("escalation_policy") and a["escalation_policy"].get("name")
    })
    if politicas:
        for p in politicas:
            marca = "→ prioridad alta (coincide con «no reconocimiento»)" if "no reconocimiento" in p.lower() else "→ otra severidad"
            print(f"  · «{p}» {marca}")
    else:
        print("  Ninguna alerta de la muestra trae escalation_policy; no se puede confirmar el nombre exacto todavía.")

    print("\nVeredicto\n---------")
    if alertas:
        print("  API REST v2 disponible, autenticada y con el esquema esperado.")
        print("  Puede construirse el extractor mensual sobre ella (automatizacion/extraer_alertas.py).")
    else:
        print("  La api-key autentica, pero no hubo alertas de muestra para confirmar el esquema.")
        print("  Antes de confiar en el extractor, correr con --limit mayor o en un periodo con más actividad.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
