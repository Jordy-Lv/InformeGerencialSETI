"""
Ledger acumulado de casos (alertas/requerimientos/incidentes) por mes,
independiente de la hoja «Casos» del consolidado.

Encargo original del usuario (capturas de WhatsApp, ver
docs/2026-07-29-relevo-sesion-28-julio.md §5.1): "que el HTML tenga
conocimiento de los casos anteriores... independiente de esa hoja
totalmente" — para que Santiago deje de tener que mantener esa hoja a mano
solo para que el informe sepa su propio histórico.

Vive en `automatizacion/salida/historico_casos.json`, un solo archivo que
crece mes a mes por *upsert*: cada extractor (`extraer_glpi.py`,
`extraer_alertas.py`) toca solo el periodo y los campos que le corresponden,
sin tocar los demás — igual que `insumos_af.py` con `insumos-af.js`. El
backfill inicial (`backfill_historico_casos.py`) puebla los meses anteriores
a que existiera esta automatización, leyendo la hoja «Casos» una sola vez,
con la misma regla de "nunca pisar un periodo que el ledger ya tenga".
"""

import json
from datetime import datetime
from pathlib import Path

RUTA = Path(__file__).parent / "salida" / "historico_casos.json"

CAMPOS = ("alertas", "requerimientos", "incidentes")


def cargar(ruta=RUTA):
    """Lee el ledger existente, si lo hay. Ausente, corrupto o de otra
    versión no es un error: se parte de uno nuevo y vacío."""
    if ruta.exists():
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            if datos.get("version") == 1 and isinstance(datos.get("periodos"), dict):
                return datos
        except (ValueError, OSError):
            pass
    return {"version": 1, "periodos": {}}


def escribir(datos, ruta=RUTA):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cuerpo = json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True)
    ruta.write_text(cuerpo, encoding="utf-8")


def actualizar_periodo(datos, periodo, **campos):
    """Upsert: toca solo los campos dados (de CAMPOS) del periodo indicado
    («AAAA-MM»), sin tocar otros periodos ni otros campos del mismo periodo
    — así `extraer_glpi.py` puede escribir requerimientos/incidentes de un
    mes sin borrar las alertas que ya dejó `extraer_alertas.py` para ese
    mismo mes, o viceversa, sin importar el orden en que corran."""
    entrada = datos["periodos"].setdefault(periodo, {})
    for campo in CAMPOS:
        if campo in campos and campos[campo] is not None:
            entrada[campo] = campos[campo]
    entrada["actualizado"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return datos


def solo_si_falta(datos, periodo, **campos):
    """Variante para el backfill: escribe solo si el periodo AÚN NO EXISTE en
    el ledger — nunca pisa un periodo que la automatización en vivo ya haya
    escrito. Devuelve True si escribió, False si ya existía (se omitió)."""
    if periodo in datos["periodos"]:
        return False
    actualizar_periodo(datos, periodo, **campos)
    return True
