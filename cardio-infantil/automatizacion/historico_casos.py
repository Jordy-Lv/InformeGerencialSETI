"""
Ledger acumulado de casos (alertas/requerimientos/incidentes/casos_bd) por
mes, independiente de las hojas del consolidado manual (Dta junio.xlsx).

Mismo mecanismo que `historico_casos.py` de Acción Fiduciaria: un solo
archivo que crece mes a mes por *upsert* — cada extractor toca solo el
periodo y los campos que le corresponden, sin pisar lo que dejó otro.

Cardio Infantil suma un campo que Acción Fiduciaria no tiene: `casos_bd`
(la tarjeta nueva "Casos de Base de Datos", ver inventario de tarjetas).
"""

import json
from datetime import datetime
from pathlib import Path

RUTA = Path(__file__).parent / "salida" / "historico_casos.json"

CAMPOS = ("alertas", "requerimientos", "incidentes", "casos_bd")


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
    («AAAA-MM»), sin tocar otros periodos ni otros campos del mismo periodo."""
    entrada = datos["periodos"].setdefault(periodo, {})
    for campo in CAMPOS:
        if campo in campos and campos[campo] is not None:
            entrada[campo] = campos[campo]
    entrada["actualizado"] = datetime.now().astimezone().isoformat(timespec="seconds")
    return datos


def solo_si_falta(datos, periodo, **campos):
    """Variante para un futuro backfill: escribe solo si el periodo AÚN NO
    EXISTE en el ledger — nunca pisa un periodo que la automatización en vivo
    ya haya escrito. Devuelve True si escribió, False si ya existía."""
    if periodo in datos["periodos"]:
        return False
    actualizar_periodo(datos, periodo, **campos)
    return True
