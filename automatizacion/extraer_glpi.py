#!/usr/bin/env python3
"""
Extractor de la sábana de casos desde GLPI, vía API REST.

Reemplaza el trabajo manual de entrar a GLPI, filtrar, exportar y buscar el
archivo en Descargas. Produce un CSV con las mismas columnas que el informe
espera, para que `cargarGlpi()` lo lea sin cambiar una línea del HTML.

La sonda (`sonda_glpi.py`) confirmó contra la instancia real que la API REST
está habilitada, y de ahí salieron los searchOption que usa este script. No hay
ningún ID adivinado: todos vienen de `listSearchOptions/Ticket`.

Uso:

    python3 automatizacion/extraer_glpi.py                 # mes en curso
    python3 automatizacion/extraer_glpi.py --periodo 2026-06
    python3 automatizacion/extraer_glpi.py --sin-filtro-entidad
    python3 automatizacion/extraer_glpi.py --muestra        # 5 casos, para inspeccionar

Credenciales: solo desde `.env` o variables de entorno. Ver `.env.ejemplo`.
"""

import argparse
import csv
import io
import json
import sys
from base64 import b64encode
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sonda_glpi import Cliente, cargar_env, texto  # noqa: E402

import os  # noqa: E402

SALIDA = Path(__file__).parent / "salida"

# searchOptions verificados contra www.seti.co/glpi el 23/07/2026.
# El orden es el de la exportación manual, para que el archivo automático se
# pueda comparar columna a columna con el que se venía bajando a mano.
COLUMNAS = [
    ("2",  "ID"),
    ("1",  "Título"),
    ("80", "Entidad"),
    ("15", "Fecha de apertura"),
    ("12", "Estado"),
    ("19", "Última modificación"),
    ("7",  "Categoría"),
    ("3",  "Prioridad"),
    ("30", "SLA - SLA Tiempo en resolver"),
    ("82", "Tiempo para resolver excedido"),
    ("14", "Tipo"),
    ("17", "Fecha de resolución"),
]

# Las cuatro que `cargarGlpi()` exige; sin ellas el informe rechaza el archivo.
OBLIGATORIAS = {"Entidad", "Fecha de apertura", "Categoría", "Tiempo para resolver excedido"}

POR_PAGINA = 200


class ErrorGlpi(Exception):
    pass


# --------------------------------------------------------------------------

def abrir_sesion(cli, base, usuario, clave):
    basico = b64encode(f"{usuario}:{clave}".encode()).decode()
    codigo, _, cuerpo = cli.pedir(
        f"{base}/apirest.php/initSession",
        cabeceras={"Authorization": f"Basic {basico}", "Content-Type": "application/json"},
    )
    if codigo != 200:
        raise ErrorGlpi(f"initSession devolvió HTTP {codigo}: {texto(cuerpo)[:300]}")
    return json.loads(texto(cuerpo))["session_token"]


def cerrar_sesion(cli, base, token):
    """GLPI mantiene la sesión abierta hasta que expira. Cerrarla es higiene:
    evita acumular sesiones muertas en el servidor con cada ejecución."""
    try:
        cli.pedir(f"{base}/apirest.php/killSession", cabeceras={"Session-Token": token})
    except OSError:
        pass


def buscar_casos(cli, base, token, entidad=None, limite=None):
    """Trae los tickets página por página. La API responde 206 mientras queden
    más resultados y 200 en la última."""
    criterios = {}
    if entidad:
        criterios.update({
            "criteria[0][field]": "80",
            "criteria[0][searchtype]": "contains",
            "criteria[0][value]": entidad,
        })

    fijos = {f"forcedisplay[{i}]": ident for i, (ident, _) in enumerate(COLUMNAS)}
    fijos.update(criterios)
    fijos["sort"] = "15"
    fijos["order"] = "DESC"

    filas, inicio, total = [], 0, None
    while True:
        fin = inicio + (limite or POR_PAGINA) - 1
        consulta = dict(fijos, **{"range": f"{inicio}-{fin}"})
        url = f"{base}/apirest.php/search/Ticket?" + _urlencode(consulta)
        codigo, cabs, cuerpo = cli.pedir(
            url, cabeceras={"Session-Token": token, "Content-Type": "application/json"}
        )
        if codigo not in (200, 206):
            raise ErrorGlpi(f"search/Ticket devolvió HTTP {codigo}: {texto(cuerpo)[:400]}")

        datos = json.loads(texto(cuerpo))
        total = datos.get("totalcount", 0)
        lote = datos.get("data") or []
        if isinstance(lote, dict):          # según versión llega indexado por id
            lote = list(lote.values())
        filas.extend(lote)

        if limite or not lote or len(filas) >= total:
            break
        inicio += POR_PAGINA

    return filas, total


def _urlencode(d):
    from urllib.parse import urlencode
    return urlencode(d)


# --------------------------------------------------------------------------

def limpiar(valor):
    """La API devuelve booleanos como 0/1 y campos multivalor como listas.
    El informe tolera ambos, pero el archivo debe poder compararse a ojo con la
    exportación manual, así que se deja igual de legible."""
    if valor is None or valor == "":
        return ""
    if isinstance(valor, list):
        return " | ".join(str(limpiar(v)) for v in valor if v not in (None, ""))
    if isinstance(valor, dict):
        return limpiar(valor.get("name") or valor.get("completename") or "")
    return str(valor).replace("\r", " ").replace("\n", " ").strip()


def como_si_no(valor):
    """«Tiempo para resolver excedido» llega como 0/1 por la API y como Sí/No
    en la exportación manual. El informe acepta ambos («1» está en su lista de
    valores verdaderos), pero se normaliza para que el archivo sea legible por
    una persona que lo abra en Excel."""
    s = str(valor).strip().lower()
    if s in ("1", "true", "sí", "si", "yes"):
        return "Sí"
    if s in ("0", "false", "no", ""):
        return "No"
    return str(valor)


def a_csv(filas):
    salida = io.StringIO()
    escritor = csv.writer(salida, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    escritor.writerow([nombre for _, nombre in COLUMNAS])
    for fila in filas:
        registro = []
        for ident, nombre in COLUMNAS:
            valor = limpiar(fila.get(ident, fila.get(int(ident) if ident.isdigit() else ident, "")))
            if nombre == "Tiempo para resolver excedido":
                valor = como_si_no(valor)
            registro.append(valor)
        escritor.writerow(registro)
    return salida.getvalue()


def verificar(csv_texto, periodo):
    """Comprobaciones que deben pasar antes de dar el archivo por bueno.
    Un extractor que falla en silencio es peor que no tener extractor."""
    filas = list(csv.reader(io.StringIO(csv_texto), delimiter=";"))
    if not filas:
        return ["El archivo salió vacío: ni siquiera tiene encabezado."]

    problemas = []
    cabecera = set(filas[0])
    faltan = OBLIGATORIAS - cabecera
    if faltan:
        problemas.append(f"Faltan columnas que el informe exige: {', '.join(sorted(faltan))}")

    datos = filas[1:]
    if not datos:
        problemas.append("Cero casos devueltos. Revisa el filtro de entidad.")
        return problemas

    idx = {n: i for i, n in enumerate(filas[0])}
    del_periodo = [
        f for f in datos
        if len(f) > idx["Fecha de apertura"] and f[idx["Fecha de apertura"]].startswith(periodo)
    ]
    if not del_periodo:
        problemas.append(
            f"Ningún caso con fecha de apertura en {periodo}. El informe lo reportará "
            "como «sin registros en el periodo» — comprueba que sea correcto."
        )
    return problemas


# --------------------------------------------------------------------------

def main():
    cargar_env()
    hoy = date.today()

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--periodo", default=f"{hoy.year}-{hoy.month:02d}",
                   help="Mes a verificar, formato AAAA-MM (por defecto, el actual)")
    p.add_argument("--sin-filtro-entidad", action="store_true",
                   help="Descarga todas las entidades, como la exportación manual de hoy")
    p.add_argument("--muestra", action="store_true",
                   help="Trae solo 5 casos e imprime el JSON crudo, para inspeccionar formatos")
    args = p.parse_args()

    base = os.environ.get("GLPI_URL", "").rstrip("/")
    usuario = os.environ.get("GLPI_USER", "")
    clave = os.environ.get("GLPI_PASSWORD", "")
    entidad = os.environ.get("GLPI_ENTIDAD", "ACCION FIDUCIARIA")

    if not (base and usuario and clave):
        print("Faltan credenciales. Complétalas en automatizacion/.env", file=sys.stderr)
        return 2

    SALIDA.mkdir(exist_ok=True)
    cli = Cliente()
    token = None
    try:
        token = abrir_sesion(cli, base, usuario, clave)
        print(f"Sesión abierta en {base}")

        filtro = None if args.sin_filtro_entidad else entidad
        print(f"Filtro de entidad: {filtro or '(ninguno — todas las entidades)'}")

        filas, total = buscar_casos(cli, base, token, entidad=filtro,
                                    limite=5 if args.muestra else None)
        print(f"GLPI reporta {total} casos; se recibieron {len(filas)}.")

        if args.muestra:
            ruta = SALIDA / "muestra-cruda.json"
            ruta.write_text(json.dumps(filas, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\nJSON crudo de {len(filas)} casos → {ruta}")
            print("\nMapeo a columnas del informe:\n")
            print(a_csv(filas))
            return 0

        contenido = a_csv(filas)
        nombre = f"glpi-{args.periodo}.csv"
        destino = SALIDA / nombre
        destino.write_text(contenido, encoding="utf-8-sig")

        problemas = verificar(contenido, args.periodo)
        print(f"\nArchivo generado: {destino}")
        print(f"  {len(filas)} casos · {destino.stat().st_size} bytes")
        if problemas:
            print("\n  Revisar antes de usarlo:")
            for x in problemas:
                print(f"    · {x}")
        else:
            print("  Verificación: sin observaciones.")
        return 0

    except ErrorGlpi as e:
        print(f"\nGLPI rechazó la petición:\n  {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"\nNo se pudo hablar con {base}:\n  {e}", file=sys.stderr)
        return 1
    finally:
        if token:
            cerrar_sesion(cli, base, token)


if __name__ == "__main__":
    sys.exit(main())
