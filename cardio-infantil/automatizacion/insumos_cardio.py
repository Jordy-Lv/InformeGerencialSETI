"""
Empaquetado de `insumos-cardio.js`, compartido por los extractores de Cardio
Infantil. Es el equivalente de `insumos_af.py` en Acción Fiduciaria — mismo
mecanismo, adaptado a este cliente. Las funciones de empaquetado (paquete
base64 + hash, periodo, ledger histórico) son genéricas y se portaron tal
cual; lo único que NO se porta es `clasificar_caso_glpi()`, ver más abajo.

Cada extractor (GLPI, y los que vengan) aporta su propio archivo bajo
`archivos.<clave>`. Ninguno debe borrar lo que otro ya dejó escrito: por eso
se lee el paquete existente antes de escribir, en vez de crear uno nuevo cada
vez.

No puede ser un `.json` leído con fetch: abierto desde el disco, el navegador
bloquea toda petición al sistema de archivos. Un `<script>` vecino sí carga, y
es la única puerta que queda abierta sin montar un servidor. Por eso el
contenido viaja como datos —base64 y un hash— dentro de un
`window.__INSUMOS_CARDIO__` (nombre propio, para no colisionar si algún día
el mismo navegador tuviera abierto también el informe de Acción Fiduciaria).
"""

import hashlib
import json
import os
import re
import shutil
import sys
import time
from base64 import b64encode
from datetime import date, datetime
from pathlib import Path

CABECERA = (
    "/* Generado por automatizacion/*.py de Cardio Infantil. No editar a mano.\n"
    "   Lo lee el informe al abrirse; si este archivo no está, el centro de\n"
    "   carga funciona como siempre. */\n"
)

_PATRON = re.compile(r"window\.__INSUMOS_CARDIO__\s*=\s*(\{.*\})\s*;\s*$", re.S)


def clasificar_caso_cardio(categoria, tipo, hoja_origen=None):
    """Clasifica un caso de Cardio Infantil en 'alerta' | 'requerimiento' |
    'incidente' | 'caso_bd' | 'otro'.

    DELIBERADAMENTE SIN TERMINAR. No se puede escribir la regla real todavía:
    el consolidado manual (Dta junio.xlsx) separa los casos por HOJA de
    origen (Reque_SO / Alerta_SO / Requerimientos BD), no por categoría de
    ticket como hace `clasificar_caso_glpi()` en Acción Fiduciaria — así que
    copiar esa función no sirve aquí (ver inventario de tarjetas,
    docs/2026-08-03-inventario-tarjetas-cardio-infantil.md).

    Para escribir la regla real hace falta primero:
      1. Correr sonda_glpi.py contra la instancia real de Cardio Infantil.
      2. Confirmar si, al traer los tickets por API (no por export manual),
         existe alguna forma de reproducir esa misma separación en 3 grupos
         (¿un campo de categoría raíz distinto por grupo? ¿tres filtros de
         búsqueda distintos, uno por grupo?) — o si hay que pedirle al
         equipo de Cardio Infantil el criterio real que usan al exportar.

    Levanta NotImplementedError a propósito: es preferible que
    extraer_glpi.py falle ruidosamente a que clasifique casos con una regla
    inventada y nadie lo note hasta que las cifras del informe no cuadren.
    """
    raise NotImplementedError(
        "clasificar_caso_cardio() todavía no está definida — depende de correr "
        "sonda_glpi.py contra el GLPI real de Cardio Infantil y confirmar cómo "
        "reproducir la separación Reque_SO / Alerta_SO / Requerimientos BD por "
        "API. Ver docs/2026-08-03-inventario-tarjetas-cardio-infantil.md."
    )


def mes_cerrado(hoy=None):
    """El mes que ya cerró, en formato AAAA-MM: si hoy es agosto, julio.

    Idéntica a la de Acción Fiduciaria (`insumos_af.py`): nunca se reporta el
    mes en curso porque todavía no tiene sus casos completos.
    """
    hoy = hoy or date.today()
    anio, mes = hoy.year, hoy.month - 1
    if mes == 0:
        anio, mes = anio - 1, 12
    return f"{anio}-{mes:02d}"


def cargar_paquete(destino):
    """Lee el insumos-cardio.js existente, si lo hay. Un archivo ausente,
    corrupto o de otra versión no es un error: se parte de un paquete nuevo y
    vacío."""
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


MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _mismo_contenido(a, b):
    """True si dos archivos tienen exactamente los mismos bytes."""
    return (hashlib.sha256(Path(a).read_bytes()).digest()
            == hashlib.sha256(Path(b).read_bytes()).digest())


def copiar_resguardo(origen, nombre, periodo, proteger=True):
    """Copia el CSV original a la carpeta del mes dentro de RUTA_ONEDRIVE
    (`.env`). Idéntica en comportamiento a la de Acción Fiduciaria: sin
    RUTA_ONEDRIVE configurada, no hace nada (es opcional); con `proteger=True`
    (por defecto) no sobrescribe un archivo ya existente con contenido
    distinto, salvo `FORZAR_ONEDRIVE=1`."""
    ruta = os.environ.get("RUTA_ONEDRIVE", "").strip()
    if not ruta:
        return None
    try:
        _anio, mes = periodo.split("-")
        nombre_mes = MESES_ES[int(mes) - 1].capitalize()
        carpeta = Path(ruta) / nombre_mes
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / nombre
        destino.parent.mkdir(parents=True, exist_ok=True)
        forzar = os.environ.get("FORZAR_ONEDRIVE", "").strip() not in ("", "0")
        if proteger and destino.exists() and not forzar:
            if _mismo_contenido(origen, destino):
                return destino
            print(f"Aviso: {destino} ya existe con contenido distinto; se conservó "
                  f"el existente sin sobrescribir (define FORZAR_ONEDRIVE=1 para "
                  f"forzarlo).", file=sys.stderr)
            return destino
        shutil.copyfile(origen, destino)
        return destino
    except OSError as e:
        print(f"Aviso: no se pudo copiar {nombre} a RUTA_ONEDRIVE ({ruta}): {e}", file=sys.stderr)
        return None


def eliminar_resguardo(nombre, periodo):
    """Borra la copia de resguardo en RUTA_ONEDRIVE si existe. Sin
    RUTA_ONEDRIVE configurada, o si el archivo no existe, no hace nada."""
    ruta = os.environ.get("RUTA_ONEDRIVE", "").strip()
    if not ruta:
        return None
    try:
        _anio, mes = periodo.split("-")
        nombre_mes = MESES_ES[int(mes) - 1].capitalize()
        destino = Path(ruta) / nombre_mes / nombre
        if destino.exists():
            destino.unlink()
            return destino
        return None
    except OSError as e:
        print(f"Aviso: no se pudo borrar {nombre} de RUTA_ONEDRIVE ({ruta}): {e}", file=sys.stderr)
        return None


def incrustar_insumos(html_path, insumos_js_path):
    """Devuelve el HTML como texto, con el contenido de `insumos-cardio.js`
    incrustado como un `<script>` propio justo después de `<head>` — mismo
    mecanismo que `incrustar_insumos()` de Acción Fiduciaria."""
    html = Path(html_path).read_text(encoding="utf-8")
    insumos_js = Path(insumos_js_path).read_text(encoding="utf-8")
    marcador = "<head>"
    i = html.find(marcador)
    if i < 0:
        raise ValueError(f"{html_path} no tiene una etiqueta <head> donde incrustar los insumos.")
    i += len(marcador)
    bloque = f"\n<script>\n{insumos_js}</script>\n"
    return html[:i] + bloque + html[i:]


def adjuntar_historico(paquete, historico):
    """Añade el ledger acumulado (historico_casos.json) al paquete, como
    campo de nivel superior `historico`."""
    paquete["historico"] = historico


def archivo_de(csv_bytes, nombre, origen):
    """Construye la entrada de `archivos.<clave>` para un CSV ya generado."""
    return {
        "nombre": nombre,
        "origen": origen,
        "sha256": hashlib.sha256(csv_bytes).hexdigest(),
        "contenido": b64encode(csv_bytes).decode(),
    }


def fijar_periodo(paquete, periodo):
    """Ajusta `paquete['periodo']` al mes AAAA-MM dado. Devuelve el periodo
    anterior si ya había uno y era distinto, o None si no había o coincidía."""
    anio, mes = periodo.split("-")
    nuevo = {"mes": int(mes) - 1, "anio": int(anio)}
    anterior = paquete.get("periodo")
    paquete["periodo"] = nuevo
    if anterior and anterior != nuevo:
        return anterior
    return None


class ArchivoBloqueado(OSError):
    """El destino existe y no se pudo escribir tras varios reintentos —
    típicamente porque OneDrive/el propio navegador lo tienen abierto con
    lock exclusivo en Windows. Se distingue de un OSError genérico para que
    quien llama pueda dar un mensaje claro ("cierra el archivo e intenta de
    nuevo") en vez de "no se pudo hablar con GLPI", que sería engañoso: la
    extracción sí funcionó, lo que falló fue el guardado en disco."""


def escribir_con_reintentos(destino, bytes_datos, intentos=5, espera=0.4):
    """Escribe `bytes_datos` en `destino`, reintentando ante PermissionError
    — común en Windows cuando OneDrive está sincronizando el archivo o el
    informe HTML lo tiene abierto. Nota: no existía en insumos_af.py pese a
    que extraer_glpi.py de Acción Fiduciaria la importa de ahí — ese es un
    import roto en el código base actual (confirmado, no está en ningún
    archivo del proyecto ni en la rama fix/recarga-insumos-2026-08-04). Se
    implementa aquí, completa, para que Cardio Infantil no herede el mismo
    problema."""
    ultimo_error = None
    for intento in range(intentos):
        try:
            destino.write_bytes(bytes_datos)
            return
        except PermissionError as e:
            ultimo_error = e
            if intento < intentos - 1:
                time.sleep(espera)
    raise ArchivoBloqueado(
        f"No se pudo escribir {destino} tras {intentos} intentos — "
        f"¿está abierto en otro programa? ({ultimo_error})"
    )


def escribir_paquete(destino, paquete):
    paquete["generado"] = datetime.now().astimezone().isoformat(timespec="seconds")
    cuerpo = json.dumps(paquete, ensure_ascii=False, indent=2)
    contenido = (CABECERA + f"window.__INSUMOS_CARDIO__ = {cuerpo};\n").encode("utf-8")
    escribir_con_reintentos(destino, contenido)
