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
import unicodedata
from base64 import b64encode
from datetime import date, datetime
from pathlib import Path

# Clasificación de un caso de GLPI en requerimiento/incidente/revisión, EXACTAMENTE
# igual que cargarGlpi() en el HTML (informe-accion-fiduciaria 1.html): un ticket
# cuenta como «incidente» si su Categoría (o Tipo, si no hay Categoría) matchea
# R_INCIDENTE, salvo que CUALQUIER nivel de la categoría tras el primero (tras
# ">") sea una revisión de alerta autogenerada por el monitoreo — esas no son
# fallas nuevas. Regla corregida el 02/08/2026 (F3): con categorías de tres
# niveles («INCIDENTES > Revision Alerta > Jobs Fallidos») tomar solo el
# último nivel no matcheaba «Revision Alerta» y el ticket se contaba como
# incidente real; había que revisar todos los niveles después del primero,
# no solo uno.
# Compartida entre extraer_glpi.py (cuenta req/inc del mes para historico_casos.json)
# y extraer_indisponibilidades.py (identifica qué IDs de GLPI son «incidente» para
# cruzarlos contra el log de indisponibilidades): una sola definición, no dos.
R_REQUERIMIENTO = re.compile(r"requerim|request|solicitud", re.I)
R_INCIDENTE = re.compile(r"incidente|incident", re.I)
R_REVISION = re.compile(r"^revision", re.I)


def _norm(v):
    s = unicodedata.normalize("NFD", str(v or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()


def clasificar_caso_glpi(categoria, tipo):
    """'requerimiento' | 'incidente' | 'revision' | 'otro', a partir de la
    Categoría (o Tipo si no hay Categoría) de un caso ya extraído de GLPI."""
    clas_texto = categoria or tipo or ""
    n = _norm(clas_texto)
    if R_REQUERIMIENTO.search(n):
        return "requerimiento"
    if R_INCIDENTE.search(n):
        niveles = categoria.split(">")[1:] if categoria else []
        es_revision = any(R_REVISION.search(_norm(p)) for p in niveles)
        return "revision" if es_revision else "incidente"
    return "otro"


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


MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _mismo_contenido(a, b):
    """True si dos archivos tienen exactamente los mismos bytes."""
    return (hashlib.sha256(Path(a).read_bytes()).digest()
            == hashlib.sha256(Path(b).read_bytes()).digest())


def copiar_resguardo(origen, nombre, periodo, proteger=True):
    """Copia el CSV original, tal cual y sin abrirlo, a la carpeta del mes
    dentro de RUTA_ONEDRIVE (`.env`) — típicamente la carpeta sincronizada
    con la biblioteca de SharePoint donde se archiva el corte de cada mes
    para trazabilidad. Es un tercer destino, distinto de los otros dos que ya
    existían: el propio `origen` (la copia intacta que se queda en
    `automatizacion/salida/`) y `insumos-af.js` (la copia en base64 que lee
    el informe). Ninguno de los tres se deriva de otro por mutación.

    La subcarpeta se llama solo el mes en español, capitalizado (p. ej.
    «Julio»), igual que ya se nombran a mano la mayoría de los meses en esa
    biblioteca — se crea si no existe. Sin RUTA_ONEDRIVE configurada, no hace
    nada: es opcional. Si la carpeta no se puede crear o escribir (OneDrive
    no instalado o sin sincronizar, ruta mal escrita), avisa por stderr pero
    no interrumpe la extracción: el insumo del informe ya quedó bien
    generado antes de llegar aquí.

    Con `proteger=True` (por defecto — para los CSV originales, que son
    registro de auditoría): si en esa carpeta ya hay un archivo con ese
    nombre y su contenido es distinto del que se va a escribir, **no lo
    sobrescribe** — avisa por stderr y conserva el que ya estaba. Evita que
    una corrida repetida del mismo mes borre en silencio una versión que ya
    quedó ahí. Si el contenido es idéntico, no hace nada. Para forzar la
    sobrescritura de todas formas, definir `FORZAR_ONEDRIVE=1`.

    Con `proteger=False` (para el informe HTML): siempre sobrescribe. Ese
    archivo no es un registro de auditoría — es una vista de la extracción
    más reciente disponible, así que congelarlo en la primera corrida del mes
    no protegería nada real, solo generaría una advertencia constante y sin
    valor en cada corrida siguiente (su contenido cambia siempre, aunque los
    datos no, por la marca de tiempo que lleva incrustada).
    """
    ruta = os.environ.get("RUTA_ONEDRIVE", "").strip()
    if not ruta:
        return None
    try:
        _anio, mes = periodo.split("-")
        nombre_mes = MESES_ES[int(mes) - 1].capitalize()
        carpeta = Path(ruta) / nombre_mes
        carpeta.mkdir(parents=True, exist_ok=True)
        destino = carpeta / nombre
        # `nombre` puede traer una subcarpeta (p. ej. "_datos/insumos-af.js"),
        # para dejar un archivo técnico un nivel más adentro que los insumos
        # de negocio. Se crea también si hace falta.
        destino.parent.mkdir(parents=True, exist_ok=True)
        forzar = os.environ.get("FORZAR_ONEDRIVE", "").strip() not in ("", "0")
        if proteger and destino.exists() and not forzar:
            if _mismo_contenido(origen, destino):
                return destino  # ya estaba igual: nada que hacer
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
    """Borra la copia de resguardo en RUTA_ONEDRIVE si existe — contraparte de
    copiar_resguardo(), para archivos cuya sola EXISTENCIA es la señal (como
    el log de indisponibilidades pendientes de extraer_indisponibilidades.py):
    una vez deja de haber algo que reportar, el archivo no debe quedarse ahí
    con contenido obsoleto. Sin RUTA_ONEDRIVE configurada, o si el archivo no
    existe, no hace nada."""
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
    """Devuelve el HTML como texto, con el contenido de `insumos-af.js`
    incrustado como un `<script>` propio justo después de `<head>`.

    El archivo resultante es autocontenido: no depende de ningún vecino para
    auto-cargar los datos del mes. Sigue funcionando igual si alguien lo
    copia, lo descarga suelto o lo mueve fuera de la carpeta donde vive hoy
    `insumos-af.js` — a diferencia del truco de `<script src="...">`, que
    exige que ambos archivos viajen juntos. `cargarInsumosAutomaticos()` ya
    revisa primero si `window.__INSUMOS__` existe antes de intentar buscar un
    archivo vecino, así que este bloque basta para que arranque solo.
    """
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
    """Añade el ledger acumulado (historico_casos.json, vía historico_casos.py)
    al paquete, como campo de nivel superior `historico` — no bajo `archivos`,
    porque no es un CSV de una sola fuente: ya es el JSON combinado de todos
    los meses/fuentes. A diferencia de `archivos.<clave>` no lleva huella
    propia: viaja igual de confiable (o no) que `paquete.periodo`, que el
    informe ya acepta sin verificar por separado."""
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
