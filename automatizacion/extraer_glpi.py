#!/usr/bin/env python3
"""
Extractor de la sábana de casos desde GLPI, vía API REST.

Reemplaza el trabajo manual de entrar a GLPI, filtrar, exportar y buscar el
archivo en Descargas. Produce un CSV con las mismas columnas que el informe
espera, para que `cargarGlpi()` lo lea sin cambiar una línea del HTML.

Filtra en el propio GLPI, no solo por entidad sino también por «Fecha de
apertura» (searchOption 15) acotada al mes de `--periodo`: el CSV que sale de
aquí trae solo los casos de ese mes, no el histórico completo de la entidad.

La sonda (`sonda_glpi.py`) confirmó contra la instancia real que la API REST
está habilitada, y de ahí salieron los searchOption que usa este script. No hay
ningún ID adivinado: todos vienen de `listSearchOptions/Ticket`.

Uso:

    python3 automatizacion/extraer_glpi.py                 # el mes que ya cerró (agosto -> reporta julio)
    python3 automatizacion/extraer_glpi.py --periodo 2026-06
    python3 automatizacion/extraer_glpi.py --sin-filtro-entidad
    python3 automatizacion/extraer_glpi.py --muestra        # 5 casos, para inspeccionar

Credenciales: solo desde `.env` o variables de entorno. Ver `.env.ejemplo`.
"""

import argparse
import calendar
import csv
import io
import json
import sys
from base64 import b64encode
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sonda_glpi import Cliente, cargar_env, texto  # noqa: E402
from insumos_af import adjuntar_historico, archivo_de, cargar_paquete, clasificar_caso_glpi, copiar_resguardo, escribir_paquete, fijar_periodo, mes_cerrado  # noqa: E402
import historico_casos  # noqa: E402

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


def rango_del_mes(periodo):
    """Convierte «AAAA-MM» en (desde, hasta) para acotar «Fecha de apertura»
    con searchtype morethan/lessthan, que son estrictos (no incluyen el borde):
    el día anterior al 1.º del mes, y el día siguiente al último. Así el rango
    cubre el mes completo sin adivinar cómo compara GLPI la hora."""
    anio, mes = (int(x) for x in periodo.split("-"))
    inicio = date(anio, mes, 1)
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fin = date(anio, mes, ultimo_dia)
    return (inicio - timedelta(days=1)).isoformat(), (fin + timedelta(days=1)).isoformat()


def buscar_casos(cli, base, token, entidad=None, desde=None, hasta=None, limite=None):
    """Trae los tickets página por página, filtrando en el propio GLPI por
    entidad y, si se dan, por rango de «Fecha de apertura» (searchOption 15).
    La API responde 206 mientras queden más resultados y 200 en la última."""
    criterios, i = {}, 0
    if entidad:
        criterios[f"criteria[{i}][field]"] = "80"
        criterios[f"criteria[{i}][searchtype]"] = "contains"
        criterios[f"criteria[{i}][value]"] = entidad
        i += 1
    if desde:
        criterios[f"criteria[{i}][link]"] = "AND"
        criterios[f"criteria[{i}][field]"] = "15"
        criterios[f"criteria[{i}][searchtype]"] = "morethan"
        criterios[f"criteria[{i}][value]"] = desde
        i += 1
    if hasta:
        criterios[f"criteria[{i}][link]"] = "AND"
        criterios[f"criteria[{i}][field]"] = "15"
        criterios[f"criteria[{i}][searchtype]"] = "lessthan"
        criterios[f"criteria[{i}][value]"] = hasta
        i += 1

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
        problemas.append(
            f"Cero casos devueltos para {periodo}. El filtro de fecha ya va en la consulta "
            "a GLPI, así que esto puede ser real (algunos meses no tienen casos, como ya "
            "pasó en junio de 2026) — no es automáticamente una señal de que el filtro de "
            "entidad esté mal. Si dudas, compáralo con lo que muestra GLPI a mano."
        )
        return problemas

    # El filtro de fecha ya va en la consulta a GLPI (ver rango_del_mes()); esto es una
    # red de seguridad, no el filtro principal — si aparece algo aquí, el rango enviado
    # al servidor no se comportó como se esperaba.
    idx = {n: i for i, n in enumerate(filas[0])}
    fuera_de_periodo = [
        f for f in datos
        if len(f) > idx["Fecha de apertura"] and not f[idx["Fecha de apertura"]].startswith(periodo)
    ]
    if fuera_de_periodo:
        problemas.append(
            f"{len(fuera_de_periodo)} caso(s) con fecha de apertura fuera de {periodo} pese "
            "al filtro en origen — revisa el rango de fechas que se envió a GLPI."
        )
    return problemas


def contar_requerimientos_incidentes(contenido_csv):
    """Cuenta requerimientos/incidentes del CSV ya generado (a_csv()), con la
    MISMA clasificación que `inc`/`req` en cargarGlpi() del HTML — vía
    `clasificar_caso_glpi()`, compartida con `extraer_indisponibilidades.py`.
    Ya viene filtrado por entidad y periodo (la consulta a GLPI lo garantiza),
    así que no hace falta filtrar de nuevo aquí."""
    filas = list(csv.DictReader(io.StringIO(contenido_csv), delimiter=";"))
    req = sum(1 for f in filas if clasificar_caso_glpi(f.get("Categoría"), f.get("Tipo")) == "requerimiento")
    inc = sum(1 for f in filas if clasificar_caso_glpi(f.get("Categoría"), f.get("Tipo")) == "incidente")
    return req, inc


def escribir_insumos_js(destino, periodo, csv_bytes, nombre_csv, origen, historico=None):
    """Añade la sábana de GLPI al insumo que el informe lee al abrirse.

    Comparte archivo con `extraer_alertas.py` (y los que vengan): se lee el
    paquete existente antes de escribir, así que correr este script no borra
    el `archivos.alertas` que haya dejado el otro extractor, ni al revés.

    El contenido viaja como datos —base64 y un hash— y nunca como código: el
    informe comprueba el hash antes de aceptarlo. Si alguien más puede escribir
    en la carpeta, esto es lo que impide que cuele otra cosa.

    `historico`, si se da, es el ledger completo de `historico_casos.json`
    (ya con el upsert de este mes hecho) — se adjunta como campo de nivel
    superior, no como otro `archivos.<clave>` (ver `adjuntar_historico()`).
    """
    paquete = cargar_paquete(destino)
    discrepancia = fijar_periodo(paquete, periodo)
    if discrepancia:
        print(f"Aviso: el insumo ya traía periodo {discrepancia} (de otra fuente); "
              f"se ajusta a {periodo}. Vuelve a correr esa otra extracción si no debía cambiar.",
              file=sys.stderr)
    paquete["archivos"]["glpi"] = archivo_de(csv_bytes, nombre_csv, origen)
    if historico is not None:
        adjuntar_historico(paquete, historico)
    escribir_paquete(destino, paquete)
    return paquete["archivos"]["glpi"]["sha256"]


# --------------------------------------------------------------------------

def main():
    cargar_env()

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--periodo", default=mes_cerrado(),
                   help="Mes a verificar, formato AAAA-MM (por defecto, el mes que ya cerró: "
                        "si se corre en agosto, julio)")
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

        desde, hasta = rango_del_mes(args.periodo)
        print(f"Filtro de fecha de apertura: {args.periodo} ({desde} a {hasta}, bordes exclusivos)")

        filas, total = buscar_casos(cli, base, token, entidad=filtro, desde=desde, hasta=hasta,
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
        bytes_csv = contenido.encode("utf-8-sig")
        destino.write_bytes(bytes_csv)
        resguardo = copiar_resguardo(destino, nombre, args.periodo)

        # Ledger histórico (historico_casos.json): upsert de requerimientos/
        # incidentes de este mes, independiente de la hoja «Casos» del Excel.
        # No toca el campo «alertas» del mismo periodo (eso es territorio de
        # extraer_alertas.py) ni ningún otro mes.
        req, inc = contar_requerimientos_incidentes(contenido)
        datos_historico = historico_casos.cargar()
        historico_casos.actualizar_periodo(datos_historico, args.periodo, requerimientos=req, incidentes=inc)
        historico_casos.escribir(datos_historico)

        js = SALIDA / "insumos-af.js"
        huella = escribir_insumos_js(
            js, args.periodo, bytes_csv, nombre,
            f"API REST de GLPI · {base}",
            historico=datos_historico,
        )

        problemas = verificar(contenido, args.periodo)
        print(f"\nArchivo generado: {destino}")
        print(f"  {len(filas)} casos · {len(bytes_csv)} bytes")
        print(f"Copia de resguardo: {resguardo if resguardo else '(RUTA_ONEDRIVE no configurada, se omite)'}")
        print(f"Histórico: {req} requerimiento(s), {inc} incidente(s) atribuible(s) → {historico_casos.RUTA}")
        print(f"Insumo para el informe: {js}")
        print(f"  sha256 {huella[:16]}…")
        print("  Colócalo junto al HTML para que el informe lo cargue solo.")
        if problemas:
            print("\n  Revisar antes de usarlo:")
            for x in problemas:
                print(f"    · {x}")
        else:
            print("\n  Verificación: sin observaciones.")
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
