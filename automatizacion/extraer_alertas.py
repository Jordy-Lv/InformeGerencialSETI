#!/usr/bin/env python3
"""
Extractor del consolidado de alertas desde AlertOps, vía su API REST v2.

Reemplaza el trabajo manual de entrar a AlertOps, exportar el reporte y
arrastrar el archivo al informe. Produce un CSV con las mismas columnas que
`cargarAlertas()` espera, para que el informe lo lea sin cambiar una línea
del HTML.

`sonda_alertops.py` confirmó que la API está documentada en un Swagger público
(https://api.alertops.com/swagger/v2/swagger.json) y que la api-key de esta
cuenta autentica contra ella. De ahí sale el contrato que usa este script —
no hay ningún campo adivinado.

Columnas del export manual que NO se generan aquí porque la API documentada
no las expone (ServiceName, InitialAssignedDate, TimeToAssign, TimeToResolve):
se omiten en vez de inventarlas. `cargarAlertas()` no las necesita para
calcular nada, así que su ausencia no afecta al informe.

Filtro de cliente: a diferencia de GLPI, la API de AlertOps no tiene un campo
de entidad/cliente — la cuenta es de SETI completo. El cliente viaja como
texto «Cliente: xxx» dentro de Topic/Message, igual que lo lee hoy
`cargarAlertas()` en el navegador. Este script aplica la misma extracción
(regex + normalización) para no escribir en el CSV alertas de otros clientes
de SETI.

Uso:

    python3 automatizacion/extraer_alertas.py                 # el mes que ya cerró (agosto -> reporta julio)
    python3 automatizacion/extraer_alertas.py --periodo 2026-06
    python3 automatizacion/extraer_alertas.py --muestra        # 5 alertas, para inspeccionar

Credenciales: solo desde `.env` o variables de entorno. Ver `.env.ejemplo`.
"""

import argparse
import calendar
import csv
import io
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sonda_glpi import cargar_env  # mismo lector de .env que usa GLPI
from insumos_af import archivo_de, cargar_paquete, escribir_paquete, fijar_periodo, mes_cerrado  # noqa: E402

import os  # noqa: E402

SALIDA = Path(__file__).parent / "salida"
TIEMPO_LIMITE = 30
POR_PAGINA = 100
MAX_PAGINAS = 500  # ~50.000 alertas; si se alcanza, algo va mal y hay que revisar a mano

# Columnas que produce este extractor, en el orden del export manual (hasta
# donde la API documentada tiene equivalente — ver docstring de arriba).
COLUMNAS = [
    "Alert ID", "Created Date", "Created By", "Priority", "IntegrationName",
    "Escalation Policy/Response Play", "Topic", "Message", "Source",
    "SourceName", "SourceID", "Status", "Owner", "Resolution Date",
    "Within SLA", "Resolution",
]

OBLIGATORIAS = {"Created Date", "Escalation Policy/Response Play"}

RE_CLIENTE = re.compile(r"cliente:\s*([a-z0-9_\-]+)", re.I)


class ErrorAlertOps(Exception):
    pass


# --------------------------------------------------------------------------

def norm(v):
    """Misma normalización que `norm()` en el informe: sin acentos, minúsculas,
    todo separador colapsado a un espacio. Necesaria para que «accion_fiduciaria»
    (con guion bajo, como llega en el texto) case con «accion fiduciaria»."""
    s = unicodedata.normalize("NFD", str(v or ""))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()


def cliente_de(alerta):
    txt = f"{alerta.get('topic') or ''} {alerta.get('description') or ''}"
    m = RE_CLIENTE.search(txt)
    return norm(m.group(1)) if m else ""


def pedir(url, api_key):
    req = urllib.request.Request(url, headers={"api-key": api_key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIEMPO_LIMITE) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def buscar_alertas(base, api_key, desde, hasta):
    """Trae todas las alertas del rango, paginando por cursor (`metadata.next`)."""
    alertas, cursor, pagina = [], None, 0
    while True:
        parametros = {"limit": POR_PAGINA, "createdFrom": desde, "createdTo": hasta}
        if cursor:
            parametros["next"] = cursor
        url = f"{base}/api/v2/alerts?" + urllib.parse.urlencode(parametros)
        codigo, cuerpo = pedir(url, api_key)
        if codigo != 200:
            raise ErrorAlertOps(f"GET /api/v2/alerts devolvió HTTP {codigo}: {cuerpo.decode('utf-8', 'replace')[:400]}")
        datos = json.loads(cuerpo.decode("utf-8", "replace"))
        lote = datos.get("alerts") or []
        alertas.extend(lote)
        cursor = (datos.get("metadata") or {}).get("next")
        pagina += 1
        if not cursor or not lote:
            break
        if pagina >= MAX_PAGINAS:
            print(f"Aviso: se alcanzó el tope de {MAX_PAGINAS} páginas sin agotar el cursor; "
                  "revisa el rango de fechas o el límite manualmente.", file=sys.stderr)
            break
    return alertas


# --------------------------------------------------------------------------

def limpiar(v):
    if v is None:
        return ""
    return str(v).replace("\r", " ").replace("\n", " ").strip()


def nombre_owner(owner):
    if not isinstance(owner, dict):
        return ""
    if owner.get("user_name"):
        return limpiar(owner["user_name"])
    return limpiar(f"{owner.get('first_name', '')} {owner.get('last_name', '')}".strip())


def nombre_integracion(integracion):
    if isinstance(integracion, dict):
        return limpiar(integracion.get("name", ""))
    return ""


def nombre_politica(politica):
    if isinstance(politica, dict):
        return limpiar(politica.get("name", ""))
    return ""


def fila_de(a):
    return [
        limpiar(a.get("alert_id")),
        limpiar(a.get("created_date")),
        limpiar(a.get("sender")),
        limpiar(a.get("priority")),
        nombre_integracion(a.get("integration")),
        nombre_politica(a.get("escalation_policy")),
        limpiar(a.get("topic")),
        limpiar(a.get("description")),
        limpiar(a.get("source")),
        limpiar(a.get("source_name")),
        limpiar(a.get("source_id")),
        limpiar(a.get("status")),
        nombre_owner(a.get("owner")),
        limpiar(a.get("closed_date")),
        limpiar(a.get("within_sla")),
        limpiar(a.get("resolution")),
    ]


def a_csv(alertas):
    salida = io.StringIO()
    escritor = csv.writer(salida, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    escritor.writerow(COLUMNAS)
    for a in alertas:
        escritor.writerow(fila_de(a))
    return salida.getvalue()


def verificar(csv_texto, periodo):
    """Comprobaciones que deben pasar antes de dar el archivo por bueno."""
    filas = list(csv.reader(io.StringIO(csv_texto), delimiter=";"))
    if not filas:
        return ["El archivo salió vacío: ni siquiera tiene encabezado."]

    problemas = []
    faltan = OBLIGATORIAS - set(filas[0])
    if faltan:
        problemas.append(f"Faltan columnas que el informe exige: {', '.join(sorted(faltan))}")

    datos = filas[1:]
    if not datos:
        problemas.append("Cero alertas de Acción Fiduciaria en el periodo. Revisa el filtro de cliente.")
        return problemas

    idx = filas[0].index("Created Date")
    del_periodo = [f for f in datos if len(f) > idx and f[idx].startswith(periodo)]
    if not del_periodo:
        problemas.append(
            f"Ninguna alerta con fecha en {periodo}. El informe lo reportará "
            "como «sin registros en el periodo» — comprueba que sea correcto."
        )
    return problemas


# --------------------------------------------------------------------------

def main():
    cargar_env()

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--periodo", default=mes_cerrado(),
                   help="Mes a extraer, formato AAAA-MM (por defecto, el mes que ya cerró: "
                        "si se corre en agosto, julio)")
    p.add_argument("--muestra", action="store_true",
                   help="Trae solo 5 alertas e imprime el JSON crudo, para inspeccionar formatos")
    args = p.parse_args()

    base = os.environ.get("AOPS_URL", "https://api.alertops.com").rstrip("/")
    api_key = os.environ.get("AOPS_API_KEY", "")
    filtro_cliente = norm(os.environ.get("AOPS_CLIENTE", "ACCION FIDUCIARIA"))

    if not api_key:
        print("Falta AOPS_API_KEY. Complétala en automatizacion/.env "
              "(Administration → Subscription Settings en AlertOps).", file=sys.stderr)
        return 2

    anio, mes = args.periodo.split("-")
    desde = f"{anio}-{mes}-01"
    ultimo_dia = calendar.monthrange(int(anio), int(mes))[1]
    hasta = f"{anio}-{mes}-{ultimo_dia:02d}"

    SALIDA.mkdir(exist_ok=True)
    try:
        print(f"Consultando AlertOps: {base} · periodo {desde} a {hasta}")
        if args.muestra:
            codigo, cuerpo = pedir(
                f"{base}/api/v2/alerts?" + urllib.parse.urlencode({"limit": 5, "createdFrom": desde, "createdTo": hasta}),
                api_key,
            )
            if codigo != 200:
                raise ErrorAlertOps(f"GET /api/v2/alerts devolvió HTTP {codigo}: {cuerpo.decode('utf-8','replace')[:400]}")
            datos = json.loads(cuerpo.decode("utf-8", "replace"))
            alertas = datos.get("alerts") or []
            ruta = SALIDA / "muestra-alertops-cruda.json"
            ruta.write_text(json.dumps(alertas, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\nJSON crudo de {len(alertas)} alerta(s) → {ruta}")
            print("\nMapeo a columnas del informe:\n")
            print(a_csv(alertas))
            return 0

        todas = buscar_alertas(base, api_key, desde, hasta)
        print(f"AlertOps devolvió {len(todas)} alerta(s) de toda la cuenta en el periodo.")

        # Coincidencia por inclusión en ambos sentidos: tolera que el texto traiga
        # "accion_fiduciaria" o variantes más largas ("accion fiduciaria celula3").
        def es_del_cliente(a):
            c = cliente_de(a)
            return bool(c) and (filtro_cliente in c or c in filtro_cliente)

        cliente = [a for a in todas if es_del_cliente(a)]
        print(f"Filtro de cliente «{filtro_cliente}»: {len(cliente)} de {len(todas)} alertas.")

        contenido = a_csv(cliente)
        nombre = f"alertops-{args.periodo}.csv"
        destino = SALIDA / nombre
        bytes_csv = contenido.encode("utf-8-sig")
        destino.write_bytes(bytes_csv)

        js = SALIDA / "insumos-af.js"
        paquete = cargar_paquete(js)
        discrepancia = fijar_periodo(paquete, args.periodo)
        if discrepancia:
            print(f"Aviso: el insumo ya traía periodo {discrepancia} (de otra fuente); "
                  f"se ajusta a {args.periodo}. Vuelve a correr esa otra extracción si no debía cambiar.",
                  file=sys.stderr)
        paquete["archivos"]["alertas"] = archivo_de(bytes_csv, nombre, f"API REST de AlertOps · {base}")
        escribir_paquete(js, paquete)

        problemas = verificar(contenido, args.periodo)
        print(f"\nArchivo generado: {destino}")
        print(f"  {len(cliente)} alertas · {len(bytes_csv)} bytes")
        print(f"Insumo para el informe: {js}")
        print(f"  sha256 {paquete['archivos']['alertas']['sha256'][:16]}…")
        print("  Colócalo junto al HTML para que el informe lo cargue solo (mismo archivo que GLPI).")
        if problemas:
            print("\n  Revisar antes de usarlo:")
            for x in problemas:
                print(f"    · {x}")
        else:
            print("\n  Verificación: sin observaciones.")
        return 0

    except ErrorAlertOps as e:
        print(f"\nAlertOps rechazó la petición:\n  {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"\nNo se pudo hablar con {base}:\n  {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
