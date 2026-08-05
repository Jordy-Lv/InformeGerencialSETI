#!/usr/bin/env python3
"""
Arnés de verificación A/B (F0 del plan de plataforma multicliente).

Compara dos HTML **exportados** del informe (uno de `main`, uno de la rama
que se está migrando) y confirma que producen exactamente el mismo
contenido visible para el cliente. Es el criterio de aceptación de cada fase
de la migración: "0 diferencias A/B" contra los mismos insumos.

Por qué sobre el HTML exportado y no sobre `window.REPORTE` en frío:
`exportarHTML()` clona el DOM vivo e incrusta el estado ya resuelto
(`window.__ESTADO__`) en la copia — hay texto que solo existe ahí (ver
`jsonEmbebible(snapshotEstado())` en `informe-accion-fiduciaria 1.html`). Un
diff del store no vería una regresión de plantilla que no toca el store pero
sí cambia lo que el cliente lee.

Compara dos cosas, independientes entre sí:
  1. `window.__ESTADO__` — estructurado, campo a campo (mismo truco que
     `insumos_af.py` usa con `_PATRON` para `window.__INSUMOS__`).
  2. El texto visible normalizado de los selectores que de verdad importan:
     `.tarjeta-kpi__valor`, `.tarjeta-kpi__meta`, `.tarjeta-kpi__chip`,
     `.dashboard-detail`, y cualquier celda `<td>`/`<th>` de tabla.

Solo biblioteca estándar (`html.parser`, `re`, `json`) — misma restricción
que el resto de `automatizacion/`.

Uso:
    python3 automatizacion/verificar_ab.py informe-main.html informe-rama.html
    python3 automatizacion/verificar_ab.py --autoprueba
    python3 automatizacion/verificar_ab.py --crear-dorado informe-exportado.html \
        --cliente accion-fiduciaria --periodo 2026-06
    python3 automatizacion/verificar_ab.py informe-exportado.html \
        --contra-dorado dorados/accion-fiduciaria-2026-06.json

`--autoprueba` no compara nada del proyecto: construye dos fixtures
sintéticos en memoria, uno idéntico (debe dar 0 diferencias) y uno con un
solo número visible cambiado a propósito (debe detectarlo). Un arnés que
nunca ha fallado no ha demostrado nada — esto es la prueba de que si falla,
lo dice.
"""

import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

_PATRON_ESTADO = re.compile(r"window\.__ESTADO__\s*=\s*(\{.*?\})\s*;", re.S)
_PATRON_CLIENTE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_PATRON_PERIODO = re.compile(r"^(\d{4})-(\d{2})$")

ESQUEMA_DORADO = 1

CLASES_OBJETIVO = (
    "tarjeta-kpi__valor",
    "tarjeta-kpi__meta",
    "tarjeta-kpi__chip",
    "dashboard-detail",
)


def extraer_estado(html_texto):
    """`None` si el HTML no trae `window.__ESTADO__` (no es un export válido,
    o es la plantilla editable sin exportar) — se distingue de "es un dict
    vacío", que sí sería un estado real."""
    m = _PATRON_ESTADO.search(html_texto)
    if not m:
        return None
    return json.loads(m.group(1))


def _normalizar(texto):
    return re.sub(r"\s+", " ", texto).strip()


class _ExtractorTexto(HTMLParser):
    """Recorre el HTML una sola vez y junta, por selector objetivo, el texto
    normalizado de cada elemento que lo tenga — en el orden del documento.
    Las celdas de tabla (`td`/`th`) van aparte, bajo la clave `tabla`,
    porque no se identifican por clase CSS sino por tag.

    HTML mal balanceado (una etiqueta que nunca cierra) es responsabilidad
    de quien genera el archivo, no de este parser: se cierra lo que quede
    abierto al terminar, sin intentar adivinar la intención.
    """

    def __init__(self, clases):
        super().__init__(convert_charrefs=True)
        self.clases = set(clases)
        self.resultado = {c: [] for c in clases}
        self.resultado["tabla"] = []
        self._pila = []  # [(tag, objetivo_o_None, [fragmentos_de_texto])]

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        clases_tag = set((d.get("class") or "").split())
        interseccion = clases_tag & self.clases
        objetivo = next(iter(interseccion)) if interseccion else None
        if objetivo is None and tag in ("td", "th"):
            objetivo = "tabla"
        self._pila.append([tag, objetivo, []])

    handle_startendtag = handle_starttag  # <br/> etc.: no aporta texto, pero no debe romper la pila

    def handle_data(self, data):
        if self._pila:
            self._pila[-1][2].append(data)

    def handle_endtag(self, tag):
        for i in range(len(self._pila) - 1, -1, -1):
            if self._pila[i][0] == tag:
                _, objetivo, fragmentos = self._pila.pop(i)
                texto_crudo = "".join(fragmentos)
                if objetivo:
                    texto = _normalizar(texto_crudo)
                    if texto:
                        self.resultado[objetivo].append(texto)
                if self._pila:  # el texto interno también pertenece al padre
                    self._pila[-1][2].append(texto_crudo)
                return
        # Etiqueta de cierre sin apertura correspondiente en la pila: se ignora.

    def cerrar(self):
        """Vacía lo que haya quedado abierto (HTML mal formado) sin perder
        el texto que ya se recolectó en las etiquetas que sí cerraron bien."""
        while self._pila:
            tag, objetivo, fragmentos = self._pila.pop()
            if objetivo:
                texto = _normalizar("".join(fragmentos))
                if texto:
                    self.resultado[objetivo].append(texto)


def extraer_texto_visible(html_texto):
    parser = _ExtractorTexto(CLASES_OBJETIVO)
    parser.feed(html_texto)
    parser.cerrar()
    return parser.resultado


def _diferencias_estructuradas(a, b, ruta=""):
    """Recorre dos estructuras (dict/list/valor) en paralelo y devuelve una
    lista de (ruta, valor_a, valor_b) para cada punto donde difieren — para
    que el reporte diga QUÉ campo cambió, no solo que `__ESTADO__` difiere."""
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for clave in sorted(set(a) | set(b)):
            if clave not in a:
                diffs.append((f"{ruta}.{clave}", "(ausente)", b[clave]))
            elif clave not in b:
                diffs.append((f"{ruta}.{clave}", a[clave], "(ausente)"))
            else:
                diffs.extend(_diferencias_estructuradas(a[clave], b[clave], f"{ruta}.{clave}"))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append((f"{ruta} (longitud)", len(a), len(b)))
        for i, (va, vb) in enumerate(zip(a, b)):
            diffs.extend(_diferencias_estructuradas(va, vb, f"{ruta}[{i}]"))
    elif a != b:
        diffs.append((ruta or "(raíz)", a, b))
    return diffs


def comparar(html_a, html_b):
    """Devuelve una lista de diferencias legibles (strings). Lista vacía =
    los dos HTML producen el mismo contenido visible para el cliente."""
    reporte = []

    estado_a, estado_b = extraer_estado(html_a), extraer_estado(html_b)
    if (estado_a is None) != (estado_b is None):
        reporte.append(
            f"__ESTADO__: uno de los dos archivos no lo trae "
            f"(¿alguno no es un export real, sino la plantilla editable?) "
            f"— A={'sí' if estado_a is not None else 'no'}, B={'sí' if estado_b is not None else 'no'}"
        )
    elif estado_a is not None:
        for ruta, va, vb in _diferencias_estructuradas(estado_a, estado_b, "__ESTADO__"):
            reporte.append(f"{ruta}: A={va!r}  B={vb!r}")

    visible_a, visible_b = extraer_texto_visible(html_a), extraer_texto_visible(html_b)
    for clave in sorted(set(visible_a) | set(visible_b)):
        la, lb = visible_a.get(clave, []), visible_b.get(clave, [])
        if la != lb:
            reporte.append(f".{clave}: {len(la)} elemento(s) en A, {len(lb)} en B")
            for i, (va, vb) in enumerate(zip(la, lb)):
                if va != vb:
                    reporte.append(f"  [{i}] A={va!r}  B={vb!r}")
            if len(la) != len(lb):
                extra = la[len(lb):] if len(la) > len(lb) else lb[len(la):]
                lado = "A" if len(la) > len(lb) else "B"
                reporte.append(f"  elementos extra solo en {lado}: {extra!r}")

    return reporte


# --------------------------------------------------------------------------
# Dorados persistentes: guardan huellas, nunca los datos reales en claro.
# --------------------------------------------------------------------------

class ErrorDorado(ValueError):
    """El export o el archivo dorado no cumple su contrato verificable."""


def _json_canonico(valor):
    return json.dumps(
        valor,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256(valor):
    return hashlib.sha256(_json_canonico(valor).encode("utf-8")).hexdigest()


def _contar_hojas(valor):
    if isinstance(valor, dict):
        return sum(_contar_hojas(v) for v in valor.values())
    if isinstance(valor, list):
        return sum(_contar_hojas(v) for v in valor)
    return 1


def _validar_periodo(periodo):
    m = _PATRON_PERIODO.fullmatch(periodo or "")
    if not m or not 1 <= int(m.group(2)) <= 12:
        raise ErrorDorado("Periodo inválido: usa AAAA-MM con un mes entre 01 y 12.")
    return int(m.group(1)), int(m.group(2))


def _validar_identidad(cliente, periodo):
    if not _PATRON_CLIENTE.fullmatch(cliente or ""):
        raise ErrorDorado(
            "Cliente inválido: usa un id en minúsculas separado por guiones "
            "(por ejemplo, accion-fiduciaria)."
        )
    return _validar_periodo(periodo)


def _snapshot_para_dorado(html_texto, periodo):
    estado = extraer_estado(html_texto)
    if estado is None:
        raise ErrorDorado(
            "El HTML no trae window.__ESTADO__: debe ser un export real, no la plantilla editable."
        )

    anio, mes_uno = _validar_periodo(periodo)
    periodo_estado = estado.get("periodo") if isinstance(estado, dict) else None
    if not isinstance(periodo_estado, dict):
        raise ErrorDorado("window.__ESTADO__.periodo no es un objeto válido.")
    if periodo_estado.get("anio") != anio or periodo_estado.get("mes") != mes_uno - 1:
        detectado = f"{periodo_estado.get('anio')}-{periodo_estado.get('mes')} (mes base cero)"
        raise ErrorDorado(
            f"El periodo declarado {periodo} no coincide con __ESTADO__.periodo: {detectado}."
        )

    return estado, extraer_texto_visible(html_texto)


def crear_dorado(html_texto, cliente, periodo):
    """Crea una referencia determinista sin guardar estado ni textos en claro."""
    _validar_identidad(cliente, periodo)
    estado, visible = _snapshot_para_dorado(html_texto, periodo)

    componentes = {
        "__ESTADO__": {
            "elementos": _contar_hojas(estado),
            "sha256": _sha256(estado),
        }
    }
    for clave in sorted(visible):
        textos = visible[clave]
        componentes[f".{clave}"] = {
            "elementos": len(textos),
            "sha256": _sha256(textos),
        }

    snapshot = {"estado": estado, "texto_visible": visible}
    return {
        "esquema": ESQUEMA_DORADO,
        "cliente": cliente,
        "periodo": periodo,
        "huella_total": _sha256(snapshot),
        "componentes": componentes,
    }


def texto_dorado(dorado):
    """Representación estable: el mismo export produce los mismos bytes."""
    return json.dumps(dorado, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _nombre_dorado(cliente, periodo):
    return f"{cliente}-{periodo}.json"


def guardar_dorado(ruta, dorado, reemplazar=False):
    ruta = Path(ruta)
    esperado = _nombre_dorado(dorado["cliente"], dorado["periodo"])
    if ruta.name != esperado:
        raise ErrorDorado(f"El dorado debe llamarse {esperado}, no {ruta.name}.")
    if ruta.exists() and not reemplazar:
        raise ErrorDorado(
            f"El dorado ya existe: {ruta}. Usa --reemplazar-dorado solo si el cambio es intencional."
        )
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto_dorado(dorado), encoding="utf-8")


def cargar_dorado(ruta):
    ruta = Path(ruta)
    try:
        dorado = json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ErrorDorado(f"No existe el dorado: {ruta}") from exc
    except json.JSONDecodeError as exc:
        raise ErrorDorado(f"El dorado no contiene JSON válido: {ruta}: {exc}") from exc

    if not isinstance(dorado, dict) or dorado.get("esquema") != ESQUEMA_DORADO:
        raise ErrorDorado(
            f"Esquema de dorado no soportado: se esperaba {ESQUEMA_DORADO}."
        )
    cliente, periodo = dorado.get("cliente"), dorado.get("periodo")
    _validar_identidad(cliente, periodo)
    esperado = _nombre_dorado(cliente, periodo)
    if ruta.name != esperado:
        raise ErrorDorado(f"El dorado debe llamarse {esperado}, no {ruta.name}.")
    if not isinstance(dorado.get("componentes"), dict) or not dorado.get("huella_total"):
        raise ErrorDorado("El dorado no trae huella_total y componentes válidos.")
    return dorado


def comparar_con_dorado(html_texto, dorado):
    actual = crear_dorado(html_texto, dorado["cliente"], dorado["periodo"])
    reporte = []
    esperados, actuales = dorado["componentes"], actual["componentes"]
    for nombre in sorted(set(esperados) | set(actuales)):
        if nombre not in esperados:
            reporte.append(f"{nombre}: componente extra en el export actual")
        elif nombre not in actuales:
            reporte.append(f"{nombre}: componente ausente en el export actual")
        elif esperados[nombre] != actuales[nombre]:
            ee = esperados[nombre].get("elementos")
            ea = actuales[nombre].get("elementos")
            reporte.append(
                f"{nombre}: difiere (elementos esperados={ee}, actuales={ea}; huella SHA-256 distinta)"
            )
    if not reporte and dorado["huella_total"] != actual["huella_total"]:
        reporte.append("huella_total: difiere aunque las huellas de componentes coinciden")
    return reporte


# --------------------------------------------------------------------------
# Autoprueba: demuestra que el arnés SÍ detecta un cambio real, no solo que
# nunca reporta diferencias. Ver docstring del módulo.
# --------------------------------------------------------------------------

def _fixture(valor_casos="54 casos", nota_extra="", mes=6, anio=2026):
    estado = {
        "periodo": {"mes": mes, "anio": anio, "etiqueta": "periodo-sintetico"},
        "dominios": {
            "casos": {"estado": "valido", "datos": {"total": 54 if valor_casos == "54 casos" else 999}},
        },
    }
    return f"""<!DOCTYPE html>
<html><head>
<script id="estado-cliente">window.__INFORME_CLIENTE__=true;window.__ESTADO__={json.dumps(estado)};</script>
</head><body>
<div class="tarjeta-kpi"><span class="tarjeta-kpi__valor">{valor_casos}</span>
<span class="tarjeta-kpi__meta">46 alertas · 6 requerimientos{nota_extra}</span>
<span class="tarjeta-kpi__chip">Vigente</span></div>
<table><tr><td>CN-SINTETICO-001</td><th>Vigencia</th></tr></table>
<div class="dashboard-detail">Ficha contractual detalle</div>
</body></html>"""


def autoprueba():
    fallos = []

    # 1. Dos fixtures idénticos -> 0 diferencias.
    a, b = _fixture(), _fixture()
    diffs = comparar(a, b)
    if diffs:
        fallos.append(f"FALSO POSITIVO: fixtures idénticos deberían dar 0 diferencias, dieron {len(diffs)}:\n  " + "\n  ".join(diffs))
    else:
        print("[OK] Fixtures idénticos -> 0 diferencias.")

    # 2. Un número visible cambiado (KPI y __ESTADO__ a la vez) -> se detecta.
    a, b = _fixture(), _fixture(valor_casos="999 casos")
    diffs = comparar(a, b)
    # El reporte separa "qué selector cambió" de "cuál es el valor nuevo" en
    # líneas distintas (una lista + su detalle) — hay que mirar el reporte
    # completo unido, no cada línea por separado.
    reporte_completo = "\n".join(diffs)
    detecto_kpi = "tarjeta-kpi__valor" in reporte_completo and "999 casos" in reporte_completo
    detecto_estado = "__ESTADO__" in reporte_completo and "B=999" in reporte_completo
    if not diffs:
        fallos.append("FALSO NEGATIVO: cambié '54 casos' -> '999 casos' y el arnés reportó 0 diferencias.")
    elif not (detecto_kpi and detecto_estado):
        fallos.append(
            f"El arnés detectó ALGO pero no lo que se esperaba (KPI visible + __ESTADO__.total). "
            f"detecto_kpi={detecto_kpi} detecto_estado={detecto_estado}\nDiferencias reportadas:\n  " + "\n  ".join(diffs)
        )
    else:
        print(f"[OK] Cambio introducido a propósito ('54 casos' -> '999 casos') detectado: {len(diffs)} diferencia(s) reportada(s).")

    # 3. Un elemento de más en un lado (no solo valores distintos, también
    #    conteo distinto) -> se detecta.
    a = _fixture()
    b = a.replace(
        '<div class="tarjeta-kpi">',
        '<div class="tarjeta-kpi"><span class="tarjeta-kpi__valor">EXTRA</span><div class="tarjeta-kpi">',
        1,
    )
    diffs = comparar(a, b)
    if not diffs:
        fallos.append("FALSO NEGATIVO: agregué una tarjeta de más en B y el arnés reportó 0 diferencias.")
    else:
        print(f"[OK] Elemento extra en B detectado: {len(diffs)} diferencia(s) reportada(s).")

    if fallos:
        print("\nAUTOPRUEBA FALLIDA:\n")
        for f in fallos:
            print(f"  - {f}\n")
        return False
    print("\nAutoprueba OK: el arnés distingue 'igual' de 'distinto' en los tres casos probados.")
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo_a", nargs="?", help="HTML exportado de referencia (típicamente, de main)")
    p.add_argument("archivo_b", nargs="?", help="HTML exportado a verificar (típicamente, de la rama)")
    modo = p.add_mutually_exclusive_group()
    modo.add_argument("--autoprueba", action="store_true", help="No compara nada del proyecto: prueba el arnés contra fixtures sintéticos")
    modo.add_argument("--crear-dorado", metavar="HTML", help="Crea un dorado desde un HTML exportado")
    modo.add_argument("--contra-dorado", metavar="JSON", help="Compara archivo_a contra un dorado existente")
    p.add_argument("--cliente", help="Id del cliente para --crear-dorado (por ejemplo, accion-fiduciaria)")
    p.add_argument("--periodo", help="Periodo AAAA-MM para --crear-dorado")
    p.add_argument("--salida", help="Ruta de salida de --crear-dorado; por defecto dorados/<cliente>-<periodo>.json")
    p.add_argument("--reemplazar-dorado", action="store_true", help="Permite reemplazar explícitamente un dorado existente")
    args = p.parse_args(argv)

    if args.autoprueba:
        return 0 if autoprueba() else 1

    if args.crear_dorado:
        if args.archivo_a or args.archivo_b:
            p.error("--crear-dorado recibe el HTML en la propia opción, sin archivos posicionales.")
        if not args.cliente or not args.periodo:
            p.error("--crear-dorado requiere --cliente y --periodo.")
        ruta_html = Path(args.crear_dorado)
        if not ruta_html.exists():
            print(f"No existe: {ruta_html}", file=sys.stderr)
            return 2
        salida = Path(args.salida) if args.salida else Path("dorados") / _nombre_dorado(args.cliente, args.periodo)
        try:
            dorado = crear_dorado(ruta_html.read_text(encoding="utf-8"), args.cliente, args.periodo)
            guardar_dorado(salida, dorado, reemplazar=args.reemplazar_dorado)
        except (ErrorDorado, UnicodeDecodeError) as exc:
            print(f"No se pudo crear el dorado: {exc}", file=sys.stderr)
            return 2
        print(f"Dorado creado: {salida}.")
        return 0

    if args.contra_dorado:
        if not args.archivo_a or args.archivo_b:
            p.error("--contra-dorado requiere exactamente un HTML posicional.")
        ruta_html = Path(args.archivo_a)
        if not ruta_html.exists():
            print(f"No existe: {ruta_html}", file=sys.stderr)
            return 2
        try:
            dorado = cargar_dorado(args.contra_dorado)
            diffs = comparar_con_dorado(ruta_html.read_text(encoding="utf-8"), dorado)
        except (ErrorDorado, UnicodeDecodeError) as exc:
            print(f"No se pudo verificar el dorado: {exc}", file=sys.stderr)
            return 2
        if not diffs:
            print(f"0 diferencias contra {Path(args.contra_dorado).name}.")
            return 0
        print(f"{len(diffs)} diferencia(s) contra {Path(args.contra_dorado).name}:\n")
        for d in diffs:
            print(f"  {d}")
        return 1

    if args.cliente or args.periodo or args.salida or args.reemplazar_dorado:
        p.error("--cliente, --periodo, --salida y --reemplazar-dorado solo aplican a --crear-dorado.")

    if not args.archivo_a or not args.archivo_b:
        p.print_usage(sys.stderr)
        print("Faltan los dos archivos a comparar (o usa --autoprueba).", file=sys.stderr)
        return 2

    ruta_a, ruta_b = Path(args.archivo_a), Path(args.archivo_b)
    for ruta in (ruta_a, ruta_b):
        if not ruta.exists():
            print(f"No existe: {ruta}", file=sys.stderr)
            return 2

    html_a = ruta_a.read_text(encoding="utf-8")
    html_b = ruta_b.read_text(encoding="utf-8")

    diffs = comparar(html_a, html_b)
    if not diffs:
        print(f"0 diferencias entre {ruta_a.name} y {ruta_b.name}.")
        return 0

    print(f"{len(diffs)} diferencia(s) entre {ruta_a.name} (A) y {ruta_b.name} (B):\n")
    for d in diffs:
        print(f"  {d}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
