"""
Empaquetado de `insumos-af.js`, compartido por los extractores.

Cada extractor (GLPI, AlertOps, los que vengan) aporta su propio archivo bajo
`archivos.<clave>`. Ninguno debe borrar lo que el otro ya dejó escrito: si hoy
se corre solo `extraer_alertas.py`, el `glpi` que dejó la corrida anterior debe
seguir ahí. Por eso se lee el paquete existente antes de escribir, en vez de
crear uno nuevo cada vez.

No puede ser un `.json` leído con fetch: abierto desde el disco, el navegador
bloquea toda petición al sistema de archivos. Un `<script>` vecino sí carga, y
es la única puerta que queda abierta sin montar un servidor. Por eso el
contenido viaja como datos —base64 y un hash— dentro de un `window.__INSUMOS__`.
"""

import hashlib
import json
import os
import re
import shutil
import sys
from base64 import b64encode
from datetime import date, datetime
from pathlib import Path

CABECERA = (
    "/* Generado por automatizacion/extraer_glpi.py y/o extraer_alertas.py. No editar a mano.\n"
    "   Lo lee el informe al abrirse; si este archivo no está, el centro de\n"
    "   carga funciona como siempre. */\n"
)

_PATRON = re.compile(r"window\.__INSUMOS__\s*=\s*(\{.*\})\s*;\s*$", re.S)


def mes_cerrado(hoy=None):
    """El mes que ya cerró, en formato AAAA-MM: si hoy es agosto, julio.

    Es el periodo por defecto de los tres scripts (los dos extractores y el
    orquestador) — nunca el mes en curso, porque un mes que todavía no termina
    no tiene sus casos/alertas completos y el informe reportaría un corte a
    medias. La tarea programada corre el primero de cada mes precisamente
    para reportar el mes que acaba de cerrar, no el que empieza.
    """
    hoy = hoy or date.today()
    anio, mes = hoy.year, hoy.month - 1
    if mes == 0:
        anio, mes = anio - 1, 12
    return f"{anio}-{mes:02d}"


def cargar_paquete(destino):
    """Lee el insumos-af.js existente, si lo hay. Un archivo ausente, corrupto
    o de otra versión no es un error: se parte de un paquete nuevo y vacío."""
    if destino.exists():
        texto = destino.read_text(encoding="utf-8")
        m = _PATRON.search(texto)
        if m:
            try:
                paquete = json.loads(m.group(1))
                if paquete.get("version") == 1 and isinstance(paquete.get("archivos"), dict):
                    return paquete
            except (ValueError, KeyError):
                pass
    return {"version": 1, "generado": None, "periodo": None, "archivos": {}}


def copiar_resguardo(origen, nombre):
    """Copia el CSV original, tal cual y sin abrirlo, a la carpeta de
    resguardo que declare RUTA_ONEDRIVE en `.env` — típicamente una carpeta
    sincronizada con OneDrive donde el cliente/jefatura archiva el corte de
    cada mes para trazabilidad. Es un tercer destino, distinto de los otros
    dos que ya existían: el propio `origen` (la copia intacta que se queda en
    `automatizacion/salida/`) y `insumos-af.js` (la copia en base64 que lee
    el informe). Ninguno de los tres se deriva de otro por mutación.

    Sin RUTA_ONEDRIVE configurada, no hace nada — es opcional. Si la carpeta
    no se puede crear o escribir (OneDrive no instalado, ruta mal escrita),
    avisa por stderr pero no interrumpe la extracción: el insumo del informe
    ya quedó bien generado antes de llegar aquí.
    """
    ruta = os.environ.get("RUTA_ONEDRIVE", "").strip()
    if not ruta:
        return None
    try:
        carpeta = Path(ruta)
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / nombre
        shutil.copyfile(origen, destino)
        return destino
    except OSError as e:
        print(f"Aviso: no se pudo copiar {nombre} a RUTA_ONEDRIVE ({ruta}): {e}", file=sys.stderr)
        return None


def archivo_de(csv_bytes, nombre, origen):
    """Construye la entrada de `archivos.<clave>` para un CSV ya generado."""
    return {
        "nombre": nombre,
        "origen": origen,
        "sha256": hashlib.sha256(csv_bytes).hexdigest(),
        "contenido": b64encode(csv_bytes).decode(),
    }


def fijar_periodo(paquete, periodo):
    """Ajusta `paquete['periodo']` al mes AAAA-MM dado.

    Devuelve el periodo anterior si ya había uno y era distinto (para que el
    llamador pueda avisar de la discrepancia), o None si no había o coincidía.
    """
    anio, mes = periodo.split("-")
    nuevo = {"mes": int(mes) - 1, "anio": int(anio)}
    anterior = paquete.get("periodo")
    paquete["periodo"] = nuevo
    if anterior and anterior != nuevo:
        return anterior
    return None


def escribir_paquete(destino, paquete):
    paquete["generado"] = datetime.now().astimezone().isoformat(timespec="seconds")
    cuerpo = json.dumps(paquete, ensure_ascii=False, indent=2)
    destino.write_text(CABECERA + f"window.__INSUMOS__ = {cuerpo};\n", encoding="utf-8")
