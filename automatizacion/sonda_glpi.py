#!/usr/bin/env python3
"""
Sonda de reconocimiento contra GLPI.

NO es el script de extracción definitivo. Su único trabajo es averiguar, contra
la instancia real, cuál de las vías de extracción está disponible y dejar por
escrito qué respondió el servidor en cada intento. Con ese resultado se decide
cómo se construye el script mensual, en vez de adivinarlo.

Prueba, en este orden:

  1. API REST        ¿está habilitado /apirest.php? Es la vía limpia.
  2. Login web       ¿se puede iniciar sesión con un POST de formulario?
  3. searchOptions   ¿qué número identifica a «Entidad» y a «Fecha de apertura»
                     en esta instalación? (varían entre versiones y plugins)
  4. Exportación     ¿se puede pedir el CSV de todas las páginas?

Uso:

    export GLPI_URL=https://www.seti.co/glpi
    export GLPI_USER=...
    export GLPI_PASSWORD=...
    python3 automatizacion/sonda_glpi.py

Las credenciales se leen SOLO del entorno. Este archivo no las contiene y no
debe contenerlas nunca: lo lee cualquiera que tenga acceso al repositorio.

Solo usa la biblioteca estándar de Python 3: no hay nada que instalar, para que
pueda correr tal cual en el servidor donde acabe viviendo la tarea programada.
"""

import gzip
import http.cookiejar
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64encode
from datetime import datetime
from pathlib import Path

SALIDA = Path(__file__).parent / "salida"
UA = "Mozilla/5.0 (informe-accion-fiduciaria sonda-glpi)"
TIEMPO_LIMITE = 30


# --------------------------------------------------------------------------
# Registro: todo lo que responde el servidor queda escrito, no solo resumido.
# Si algo falla el día 1 a la 1 a. m., esto es lo que permite entenderlo.
# --------------------------------------------------------------------------

class Registro:
    def __init__(self):
        self.pasos = []

    def paso(self, titulo, ok, detalle="", evidencia=None):
        marca = "OK  " if ok else "FALLA"
        self.pasos.append({"titulo": titulo, "ok": ok, "detalle": detalle})
        print(f"  [{marca}] {titulo}")
        if detalle:
            for linea in str(detalle).strip().splitlines():
                print(f"         {linea}")
        if evidencia:
            nombre, contenido = evidencia
            ruta = SALIDA / nombre
            modo = "wb" if isinstance(contenido, bytes) else "w"
            with open(ruta, modo) as f:
                f.write(contenido)
            print(f"         → evidencia: {ruta}")

    def seccion(self, titulo):
        print(f"\n{titulo}\n{'-' * len(titulo)}")


LOG = Registro()


# --------------------------------------------------------------------------
# Cliente HTTP mínimo con cookies, equivalente a lo que hace un navegador.
# --------------------------------------------------------------------------

class Cliente:
    def __init__(self, verificar_tls=True):
        self.cookies = http.cookiejar.CookieJar()
        ctx = ssl.create_default_context()
        if not verificar_tls:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies),
            urllib.request.HTTPSHandler(context=ctx),
        )

    def pedir(self, url, datos=None, cabeceras=None, metodo=None):
        """Devuelve (codigo, cabeceras, cuerpo_bytes). No lanza en 4xx/5xx."""
        cab = {"User-Agent": UA, "Accept-Encoding": "gzip"}
        cab.update(cabeceras or {})
        cuerpo = None
        if datos is not None:
            cuerpo = (
                urllib.parse.urlencode(datos).encode()
                if isinstance(datos, dict) else datos
            )
            cab.setdefault("Content-Type", "application/x-www-form-urlencoded")
        req = urllib.request.Request(url, data=cuerpo, headers=cab, method=metodo)
        try:
            r = self.opener.open(req, timeout=TIEMPO_LIMITE)
            codigo, cabs, bruto = r.status, dict(r.headers), r.read()
        except urllib.error.HTTPError as e:
            codigo, cabs, bruto = e.code, dict(e.headers), e.read()
        if cabs.get("Content-Encoding") == "gzip":
            try:
                bruto = gzip.decompress(bruto)
            except OSError:
                pass
        return codigo, cabs, bruto

    def nombres_cookies(self):
        return sorted(c.name for c in self.cookies)


def texto(bytes_):
    return bytes_.decode("utf-8", errors="replace")


# --------------------------------------------------------------------------
# 1. Identificación de la instancia
# --------------------------------------------------------------------------

def identificar(cli, base):
    LOG.seccion("1. Identificación de la instancia")
    codigo, _, cuerpo = cli.pedir(f"{base}/index.php")
    html = texto(cuerpo)

    if codigo >= 400:
        LOG.paso("Alcanzar GLPI", False, f"HTTP {codigo}. ¿URL correcta? ¿Hay VPN de por medio?")
        return None

    version = None
    for patron in (
        r'name="generator"[^>]*content="GLPI[^0-9]*([0-9.]+)',
        r'GLPI\s+([0-9]+\.[0-9]+\.[0-9]+)',
        r'"glpi_version"\s*:\s*"([0-9.]+)"',
    ):
        m = re.search(patron, html, re.I)
        if m:
            version = m.group(1)
            break

    LOG.paso(
        "Alcanzar GLPI",
        True,
        f"HTTP {codigo} · versión detectada: {version or 'no declarada en el HTML'}",
        evidencia=("01-portada.html", html),
    )
    return version


# --------------------------------------------------------------------------
# 2. Vía A — API REST
# --------------------------------------------------------------------------

def probar_api(cli, base, usuario, clave):
    """La vía limpia. Devuelve el session_token si la API está habilitada."""
    LOG.seccion("2. Vía A · API REST (/apirest.php)")

    basico = b64encode(f"{usuario}:{clave}".encode()).decode()
    codigo, _, cuerpo = cli.pedir(
        f"{base}/apirest.php/initSession",
        cabeceras={"Authorization": f"Basic {basico}", "Content-Type": "application/json"},
    )
    cuerpo_txt = texto(cuerpo)[:1500]

    if codigo == 200:
        try:
            token = json.loads(cuerpo_txt)["session_token"]
        except (ValueError, KeyError):
            LOG.paso("initSession", False, f"HTTP 200 pero sin session_token: {cuerpo_txt[:300]}")
            return None
        LOG.paso("initSession", True, "La API REST está habilitada y acepta estas credenciales.")
        return token

    # Los mensajes de error de GLPI son específicos y dicen exactamente qué falta.
    pistas = {
        "ERROR_LOGIN_PARAMETERS_MISSING": "faltan parámetros de autenticación",
        "ERROR_GLPI_LOGIN": "credenciales rechazadas por GLPI",
        "ERROR_APP_TOKEN_PARAMETERS_MISSING": "la API exige App-Token: hay que pedirle uno al administrador",
        "ERROR_NOT_ALLOWED_IP": "la IP de esta máquina no está en la lista blanca del cliente API",
    }
    diagnostico = next(
        (v for k, v in pistas.items() if k in cuerpo_txt),
        "API no habilitada o ruta distinta",
    )
    LOG.paso(
        "initSession", False,
        f"HTTP {codigo} · {diagnostico}\nRespuesta: {cuerpo_txt[:400]}",
        evidencia=("02-apirest.txt", cuerpo_txt),
    )
    return None


def opciones_por_api(cli, base, token):
    codigo, _, cuerpo = cli.pedir(
        f"{base}/apirest.php/listSearchOptions/Ticket",
        cabeceras={"Session-Token": token, "Content-Type": "application/json"},
    )
    if codigo != 200:
        LOG.paso("listSearchOptions/Ticket", False, f"HTTP {codigo}")
        return {}
    datos = json.loads(texto(cuerpo))
    opciones = {
        k: v.get("name", "")
        for k, v in datos.items()
        if k.isdigit() and isinstance(v, dict)
    }
    LOG.paso(
        "listSearchOptions/Ticket", True,
        f"{len(opciones)} campos disponibles",
        evidencia=("03-searchoptions.json", json.dumps(datos, indent=2, ensure_ascii=False)),
    )
    _mostrar_campos_relevantes(opciones)
    return opciones


# Campos que un extractor de casos suele necesitar (ver COLUMNAS en
# extraer_glpi.py). El JSON crudo ya queda en 03-searchoptions.json; esto es
# solo una lectura rápida en consola para no tener que abrirlo y buscar a
# mano cada vez que se sondea una instancia nueva — el mismo paso que ya
# traía la sonda de Cardio Infantil (PR #5, cerrado por bifurcar el
# proyecto, pero esta parte sí era una mejora genérica).
_TERMINOS_RELEVANTES = (
    "título", "titulo", "entidad", "fecha de apertura", "estado",
    "categoría", "categoria", "prioridad", "tipo", "resolver",
    "resolución", "resolucion", "modificación", "modificacion",
)


def _mostrar_campos_relevantes(opciones):
    relevantes = {
        ident: nombre for ident, nombre in opciones.items()
        if any(t in nombre.lower() for t in _TERMINOS_RELEVANTES)
    }
    if not relevantes:
        return
    print("         Campos relevantes para un extractor de casos:")
    for ident, nombre in sorted(relevantes.items(), key=lambda kv: int(kv[0])):
        print(f"           id={ident:<5} {nombre}")


# --------------------------------------------------------------------------
# 3. Vía B — sesión web
# --------------------------------------------------------------------------

def csrf_de(html):
    """GLPI incrusta un token de un solo uso en cada formulario."""
    m = re.search(r'name="_glpi_csrf_token"\s+value="([a-f0-9]+)"', html)
    if not m:
        m = re.search(r'name="_glpi_csrf_token"[^>]*value=[\'"]([a-f0-9]+)', html)
    return m.group(1) if m else None


def iniciar_sesion_web(cli, base, usuario, clave):
    LOG.seccion("3. Vía B · Sesión web (formulario de login)")

    codigo, _, cuerpo = cli.pedir(f"{base}/index.php")
    html = texto(cuerpo)
    token = csrf_de(html)
    if not token:
        LOG.paso(
            "Leer token del formulario", False,
            "No aparece _glpi_csrf_token en la página de login. Puede que el acceso "
            "sea por SSO/SAML, en cuyo caso el login por formulario no aplica.",
            evidencia=("04-login-form.html", html),
        )
        return False
    LOG.paso("Leer token del formulario", True, f"_glpi_csrf_token = {token[:16]}…")

    codigo, cabs, cuerpo = cli.pedir(
        f"{base}/front/login.php",
        datos={
            "login_name": usuario,
            "login_password": clave,
            "_glpi_csrf_token": token,
            "submit": "Enviar",
        },
        cabeceras={"Referer": f"{base}/index.php"},
    )
    html = texto(cuerpo)

    # GLPI responde 302 al escritorio si aceptó; si no, repinta el login con error.
    fallo = re.search(r"(usuario o contraseña|incorrect|Erreur d'authentification|bad_login)", html, re.I)
    tiene_sesion = any(c.startswith("glpi_") or c.startswith("PHPSESSID") for c in cli.nombres_cookies())

    if fallo or not tiene_sesion:
        LOG.paso(
            "Autenticar", False,
            f"HTTP {codigo} · cookies: {cli.nombres_cookies()}\n"
            "Si las credenciales son correctas, sospecha de doble factor (MFA) o de SSO.",
            evidencia=("05-login-respuesta.html", html),
        )
        return False

    LOG.paso("Autenticar", True, f"HTTP {codigo} · cookies de sesión: {cli.nombres_cookies()}")
    return True


def opciones_por_ui(cli, base):
    """El desplegable de criterios del buscador lleva el ID de cada campo.
    Permite descubrir los searchOptions sin necesidad de la API."""
    codigo, _, cuerpo = cli.pedir(f"{base}/front/ticket.php")
    html = texto(cuerpo)
    opciones = dict(re.findall(r'<option[^>]*value="(\d+)"[^>]*>\s*([^<]+?)\s*</option>', html))
    if not opciones:
        LOG.paso("Descubrir campos desde el buscador", False, "No se reconoció el desplegable de criterios")
        return {}, html
    LOG.paso(
        "Descubrir campos desde el buscador", True,
        f"{len(opciones)} campos leídos del formulario de búsqueda",
        evidencia=("06-buscador.html", html),
    )
    return opciones, html


def buscar_campo(opciones, *palabras):
    """Encuentra el ID del campo cuyo nombre contiene todas las palabras."""
    for ident, nombre in opciones.items():
        limpio = nombre.lower()
        if all(p in limpio for p in palabras):
            return ident, nombre
    return None, None


# --------------------------------------------------------------------------
# 4. Exportación CSV
# --------------------------------------------------------------------------

def criterios_ticket(id_entidad=None, entidad_texto=None, id_fecha=None, desde=None, hasta=None):
    """Construye los criteria[...] de la URL de búsqueda.

    Sin argumentos reproduce el filtro que se usa hoy a mano: «Estado = Todo»,
    es decir, todos los casos de todas las entidades.
    """
    c = {
        "itemtype": "Ticket",
        "is_deleted": "0",
        "start": "0",
        "criteria[0][link]": "AND",
        "criteria[0][field]": "12",          # Estado
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": "all",
    }
    i = 1
    if id_entidad and entidad_texto:
        c[f"criteria[{i}][link]"] = "AND"
        c[f"criteria[{i}][field]"] = id_entidad
        c[f"criteria[{i}][searchtype]"] = "contains"
        c[f"criteria[{i}][value]"] = entidad_texto
        i += 1
    if id_fecha and desde:
        c[f"criteria[{i}][link]"] = "AND"
        c[f"criteria[{i}][field]"] = id_fecha
        c[f"criteria[{i}][searchtype]"] = "morethan"
        c[f"criteria[{i}][value]"] = desde
        i += 1
    if id_fecha and hasta:
        c[f"criteria[{i}][link]"] = "AND"
        c[f"criteria[{i}][field]"] = id_fecha
        c[f"criteria[{i}][searchtype]"] = "lessthan"
        c[f"criteria[{i}][value]"] = hasta
    return c


def probar_exportacion(cli, base, criterios, etiqueta):
    """display_type=3 es CSV; export_all=1 pide TODAS las páginas, no la visible."""
    parametros = dict(criterios)
    parametros.update({"display_type": "3", "export_all": "1"})
    url = f"{base}/front/report.dynamic.php?" + urllib.parse.urlencode(parametros)

    codigo, cabs, cuerpo = cli.pedir(url, cabeceras={"Referer": f"{base}/front/ticket.php"})
    tipo = cabs.get("Content-Type", "")
    disp = cabs.get("Content-Disposition", "")
    es_csv = "csv" in tipo.lower() or "csv" in disp.lower()

    if codigo != 200 or not es_csv:
        LOG.paso(
            f"Exportar CSV · {etiqueta}", False,
            f"HTTP {codigo} · Content-Type: {tipo or '(ninguno)'} · {disp or 'sin Content-Disposition'}\n"
            f"URL probada: {url[:200]}…",
            evidencia=(f"07-export-{etiqueta}.html", texto(cuerpo)[:20000]),
        )
        return None

    csv_txt = cuerpo.decode("utf-8-sig", errors="replace")
    filas = [l for l in csv_txt.splitlines() if l.strip()]
    cabecera = filas[0] if filas else ""
    LOG.paso(
        f"Exportar CSV · {etiqueta}", True,
        f"{len(filas) - 1} filas de datos · {len(cuerpo)} bytes\nColumnas: {cabecera[:300]}",
        evidencia=(f"08-export-{etiqueta}.csv", cuerpo),
    )
    return csv_txt


# --------------------------------------------------------------------------

def _asegurar_utf8_consola():
    """En Windows, la consola por defecto (cp1252) no sabe imprimir tildes ni
    flechas («→») que sí llevan los mensajes de estos scripts — sin esto, un
    print con esos caracteres revienta con UnicodeEncodeError a mitad de
    ejecución (visto en vivo: GLPI y AlertOps ya habían extraído todo bien,
    pero el traceback tumbaba el proceso con código de salida distinto de 0,
    y actualizar_informe.py reportaba «FALLÓ» aunque el insumo sí se generó).
    Se reconfigura una sola vez, aquí, porque cargar_env() es lo primero que
    llama cada script (sondas, extractores y el orquestador)."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure") and (flujo.encoding or "").lower() != "utf-8":
            flujo.reconfigure(encoding="utf-8", errors="replace")


def cargar_env():
    """Lee `.env` sin pasar por el intérprete de comandos.

    Hacerlo con `source` obliga a acordarse de entrecomillar los valores con
    espacios; si no, la shell parte la línea e intenta ejecutar el resto como
    un comando. Aquí el archivo son datos, no órdenes.

    Una variable del entorno solo gana si trae contenido. Un `source` a medias
    deja exportadas variables vacías que sobreviven en la terminal; si esas
    contaran, el archivo quedaría ignorado para siempre en esa sesión.
    """
    _asegurar_utf8_consola()
    ruta = Path(__file__).parent / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        nombre, _, valor = linea.partition("=")
        nombre, valor = nombre.strip(), valor.strip()
        if valor[:1] == valor[-1:] and valor[:1] in ("'", '"'):
            valor = valor[1:-1]
        if not os.environ.get(nombre):
            os.environ[nombre] = valor


def main():
    cargar_env()
    base = os.environ.get("GLPI_URL", "").rstrip("/")
    usuario = os.environ.get("GLPI_USER", "")
    clave = os.environ.get("GLPI_PASSWORD", "")
    entidad = os.environ.get("GLPI_ENTIDAD", "ACCION FIDUCIARIA")

    faltan = [n for n, v in (("GLPI_URL", base), ("GLPI_USER", usuario), ("GLPI_PASSWORD", clave)) if not v]
    if faltan:
        ruta = Path(__file__).parent / ".env"
        print(
            f"Faltan datos: {', '.join(faltan)}\n\n"
            f"Complétalos en {ruta} y vuelve a ejecutar:\n"
            "  python3 automatizacion/sonda_glpi.py\n\n"
            f"{'(ese archivo todavía no existe: cópialo de .env.ejemplo)' if not ruta.exists() else ''}",
            file=sys.stderr,
        )
        return 2

    SALIDA.mkdir(exist_ok=True)
    print(f"Sonda GLPI · {datetime.now():%Y-%m-%d %H:%M}")
    print(f"Destino: {base} · usuario: {usuario}")
    print(f"Evidencia en: {SALIDA}")

    cli = Cliente()
    identificar(cli, base)

    opciones = {}
    token = probar_api(cli, base, usuario, clave)
    if token:
        opciones = opciones_por_api(cli, base, token)

    hay_sesion = iniciar_sesion_web(cli, base, usuario, clave)

    if hay_sesion and not opciones:
        opciones, _ = opciones_por_ui(cli, base)

    LOG.seccion("4. Campos necesarios para filtrar en origen")
    id_entidad, nombre_entidad = buscar_campo(opciones, "entidad")
    id_fecha, nombre_fecha = buscar_campo(opciones, "fecha", "apertura")
    LOG.paso(
        "Campo «Entidad»", bool(id_entidad),
        f"searchOption {id_entidad} · «{nombre_entidad}»" if id_entidad
        else "no identificado; habrá que descargar todas las entidades y filtrar en el informe",
    )
    LOG.paso(
        "Campo «Fecha de apertura»", bool(id_fecha),
        f"searchOption {id_fecha} · «{nombre_fecha}»" if id_fecha
        else "no identificado",
    )

    if hay_sesion:
        LOG.seccion("5. Exportación")
        # Primero tal cual lo hace hoy la persona: todo, sin filtrar.
        probar_exportacion(cli, base, criterios_ticket(), "todo")
        # Después, filtrando por entidad en el propio GLPI. Si esto funciona, el
        # archivo mensual deja de contener casos de otros clientes.
        if id_entidad:
            probar_exportacion(
                cli, base,
                criterios_ticket(id_entidad=id_entidad, entidad_texto=entidad),
                "solo-entidad",
            )

    LOG.seccion("Veredicto")
    if token:
        print("  Vía A disponible: usar la API REST. Es la opción a construir.")
    elif hay_sesion:
        print("  Vía A no disponible; vía B (sesión web + exportación) sí.")
        print("  Revisa arriba si la exportación devolvió CSV y si el filtro por entidad funcionó.")
    else:
        print("  Ni A ni B. Revisa la evidencia en la carpeta de salida: lo más probable")
        print("  es MFA, SSO o que las credenciales no tengan permiso de acceso central.")
        print("  Ese es el escenario que obliga a la vía C (navegador automatizado).")

    fallos = [p["titulo"] for p in LOG.pasos if not p["ok"]]
    print(f"\n  Pasos con incidencia: {len(fallos)}/{len(LOG.pasos)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
