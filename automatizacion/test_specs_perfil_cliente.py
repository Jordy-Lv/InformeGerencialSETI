"""Pruebas de conformidad de la capacidad OpenSpec ``perfil-cliente``.

Solo usa biblioteca estándar y no carga datos reales. Las comprobaciones
visibles A/B permanecen a cargo de ``verificar_ab.py`` sobre exportaciones.
"""

import re
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
HTML = (RAIZ / "informe-accion-fiduciaria 1.html").read_text(encoding="utf-8")
PERFIL = (RAIZ / "perfiles/accion-fiduciaria.js").read_text(encoding="utf-8")
BASE = (RAIZ / "perfiles/base.js").read_text(encoding="utf-8")
BANCOLDEX = (RAIZ / "perfiles/bancoldex.js").read_text(encoding="utf-8")
SPEC = (RAIZ / "openspec/specs/perfil-cliente/spec.md").read_text(encoding="utf-8")
DELTA = (
    RAIZ
    / "openspec/changes/2026-08-04-f1-perfil-cliente/specs/perfil-cliente/spec.md"
).read_text(encoding="utf-8")
DELTA_F2 = (
    RAIZ
    / "openspec/changes/2026-08-05-f2-contrato-perfil/specs/perfil-cliente/spec.md"
).read_text(encoding="utf-8")
DELTA_F7 = (
    RAIZ
    / "openspec/changes/2026-08-05-f7-bancoldex-aranda/specs/perfil-cliente/spec.md"
).read_text(encoding="utf-8")


def _compacto(texto):
    return re.sub(r"\s+", "", texto)


def _sin_comentarios(texto):
    texto = re.sub(r"/\*.*?\*/", "", texto, flags=re.S)
    return re.sub(r"//[^\n]*", "", texto)


class TestContratoOpenSpec(unittest.TestCase):
    def test_cada_requisito_tiene_shall_y_escenario(self):
        for nombre, documento in (
            ("spec actual", SPEC),
            ("delta F1", DELTA),
            ("delta F2", DELTA_F2),
            ("delta F7", DELTA_F7),
        ):
            bloques = re.split(r"(?=^### Requirement:)", documento, flags=re.M)[1:]
            self.assertGreater(len(bloques), 0, nombre)
            for bloque in bloques:
                with self.subTest(documento=nombre, requisito=bloque.splitlines()[0]):
                    self.assertIn("SHALL", bloque)
                    self.assertIn("#### Scenario:", bloque)


class TestPerfilDesplegado(unittest.TestCase):
    def test_perfil_es_dato_puro_con_identidad_estable(self):
        codigo = _sin_comentarios(PERFIL)
        self.assertIn("window.PERFIL_ACCION_FIDUCIARIA = {", codigo)
        self.assertRegex(codigo, r"\bid\s*:\s*['\"]accion-fiduciaria['\"]")
        self.assertNotRegex(codigo, r"\bfunction\b|=>|\bclass\s")

    def test_resolucion_reutiliza_merge_y_falla_con_contexto(self):
        compacto = _compacto(HTML)
        self.assertIn(
            "constPERFIL_EMBEBIDO=window.__INFORME_CLIENTE__?"
            "window.__ESTADO__?.perfil:null",
            compacto,
        )
        # F7a: con más de un perfil registrado, el embebido debe coincidir
        # por id (antes bastaba con que existiera) — mismo valor para AF, que
        # sigue siendo hoy el único perfil que puede llegar embebido.
        self.assertIn(
            "'accion-fiduciaria':()=>PERFIL_EMBEBIDO?.id==='accion-fiduciaria'?"
            "PERFIL_EMBEBIDO:window.PERFIL_ACCION_FIDUCIARIA",
            compacto,
        )
        self.assertIn("returnfusionarProfundo(padre,propio)", compacto)
        self.assertIn("Perfildesconocido", compacto)
        self.assertIn("Perfilesregistrados", compacto)

    def test_export_transporta_perfil_y_poda_dependencia(self):
        compacto = _compacto(HTML)
        self.assertNotIn("perfil:PERFIL,periodo:REPORTE.periodo", compacto)
        self.assertIn("window.__ESTADO__.perfil=", HTML)
        self.assertIn("est.textContent=codigoEstadoCliente()", compacto)
        self.assertIn("script[data-perfil-cliente]", HTML)
        self.assertIn(
            "doc.querySelectorAll('script[data-perfil-cliente]').forEach(s=>s.remove())",
            compacto,
        )
        self.assertIn(
            "Perfil: la cabecera exportable adjunta el perfil resuelto al estado",
            HTML,
        )
        self.assertIn("Perfil: el entregable no conserva la dependencia externa", HTML)

    def test_almacen_nuevo_conserva_fallbacks_historicos(self):
        compacto = _compacto(HTML)
        self.assertIn("return`informe:${PERFIL.id}:${sufijo}`", compacto)
        self.assertIn("constPOS_STORE_KEY=claveAlmacen('posiciones')", compacto)
        self.assertIn("constPOS_STORE_KEY_VIEJA='informeAF:posiciones'", compacto)
        self.assertLess(
            compacto.index("localStorage.getItem(POS_STORE_KEY)"),
            compacto.index("localStorage.getItem(POS_STORE_KEY_VIEJA)"),
        )
        self.assertIn("constBOLSA_STORE_PREFIX=claveAlmacen('bolsa')+':'", compacto)
        self.assertIn("constBOLSA_STORE_PREFIX_VIEJA='informeAF:bolsa:'", compacto)
        self.assertIn(
            "localStorage.getItem(BOLSA_STORE_PREFIX+firmaOrigen)??"
            "localStorage.getItem(BOLSA_STORE_PREFIX_VIEJA+firmaOrigen)",
            compacto,
        )

    def test_interfaz_y_exportacion_consumen_textos_del_perfil(self):
        compacto = _compacto(HTML)
        self.assertIn("functionhidratarTextosPerfil()", compacto)
        self.assertIn("document.title=PERFIL.textos.tituloDocumento", compacto)
        self.assertIn("data-perfil-texto=\"marcaTopbar\"", compacto)
        self.assertIn("data-perfil-texto=\"clienteHero\"", compacto)
        self.assertIn("PERFIL.textos.nombreArchivo", HTML)
        self.assertRegex(PERFIL, r"\bnombreArchivo\s*:\s*['\"]Accion Fiduciaria['\"]")


class TestContratoDesdePerfil(unittest.TestCase):
    def test_inicio_es_fecha_iso_declarada_en_el_perfil(self):
        self.assertRegex(PERFIL, r"\binicio\s*:\s*['\"]2025-09-01['\"]")

    def test_pipeline_usa_inicio_validado_y_no_lee_el_dom(self):
        codigo = _sin_comentarios(HTML)
        self.assertIn("const INICIO_CONTRATO=inicioContrato()", codigo)
        self.assertGreaterEqual(codigo.count("INICIO_CONTRATO"), 9)
        self.assertNotRegex(
            codigo,
            r"querySelector\('\[data-k=\"finicio\"\]'\)\?\.textContent",
        )
        self.assertNotIn("new Date(2025,8,1)", _compacto(codigo))

    def test_inicio_faltante_o_invalido_falla_con_mensaje(self):
        codigo = _compacto(_sin_comentarios(HTML))
        self.assertIn("functioninicioContrato()", codigo)
        self.assertIn("PERFIL.contrato?.inicio", codigo)
        self.assertIn("requierecontrato.iniciocomofechaAAAA-MM-DD", codigo)
        self.assertIn("tienecontrato.inicioinválido", codigo)
        self.assertIn("newDate(anio,mes,dia)", codigo)

    def test_campo_visual_se_hidrata_desde_el_perfil(self):
        codigo = _compacto(_sin_comentarios(HTML))
        self.assertIn("functionhidratarContratoPerfil()", codigo)
        self.assertIn("campo.textContent=`${d}/${m}/${INICIO_CONTRATO.getFullYear()}`", codigo)
        self.assertIn("hidratarContratoPerfil()", codigo)


class TestPerfilBaseYBancoldex(unittest.TestCase):
    """F7a — perfil raíz sin cliente y Bancóldex, que lo extiende."""

    def test_base_no_representa_ningun_cliente(self):
        self.assertRegex(BASE, r"\bid\s*:\s*['\"]base['\"]")
        self.assertRegex(BASE, r"\bextiende\s*:\s*null\b")
        self.assertNotRegex(BASE, r"\bfunction\b|=>|\bclass\s")
        # Sin contrato.inicio a propósito: resolverPerfil('base') debe fallar
        # explícitamente por F2 si alguien lo resuelve sin extenderlo.
        self.assertNotRegex(BASE, r"\binicio\s*:\s*['\"]\d{4}-\d{2}-\d{2}['\"]")

    def test_bancoldex_extiende_base_no_accion_fiduciaria(self):
        self.assertRegex(BANCOLDEX, r"\bid\s*:\s*['\"]bancoldex['\"]")
        self.assertRegex(BANCOLDEX, r"\bextiende\s*:\s*['\"]base['\"]")
        self.assertNotRegex(BANCOLDEX, r"extiende\s*:\s*['\"]accion-fiduciaria['\"]")
        self.assertNotRegex(BANCOLDEX, r"\bfunction\b|=>|\bclass\s")

    def test_ambos_perfiles_estan_registrados(self):
        compacto = _compacto(HTML)
        self.assertIn(
            "'base':()=>PERFIL_EMBEBIDO?.id==='base'?PERFIL_EMBEBIDO:window.PERFIL_BASE",
            compacto,
        )
        self.assertIn(
            "'bancoldex':()=>PERFIL_EMBEBIDO?.id==='bancoldex'?"
            "PERFIL_EMBEBIDO:window.PERFIL_BANCOLDEX",
            compacto,
        )

    def test_contrato_de_bancoldex_viene_del_pdf_de_referencia(self):
        # CN-2024112, 14/11/2024-14/11/2026: página «Línea base del servicio»
        # de Bancoldex/reporte-bancoldex-2026-07-02.pdf, no inventado.
        self.assertRegex(BANCOLDEX, r"codigo\s*:\s*['\"]CN-2024112['\"]")
        self.assertRegex(BANCOLDEX, r"inicio\s*:\s*['\"]2024-11-14['\"]")
        self.assertRegex(BANCOLDEX, r"vigenciaHasta\s*:\s*['\"]2026-11-14['\"]")

    def test_bancoldex_selecciona_solo_c9(self):
        # resolverTarjetasPerfil() exige al menos una tarjeta (hallazgo al
        # verificar en navegador); c9 es la única sin texto estático
        # heredado de AF. Ver design.md, "Gap preexistente".
        self.assertRegex(BANCOLDEX, r"seleccionadas\s*:\s*\[\s*['\"]c9['\"]\s*\]")

    def test_perfil_activo_se_puede_elegir_por_url(self):
        # F7a: sin esto, 'base'/'bancoldex' quedan registrados pero
        # inalcanzables — resolverPerfil('accion-fiduciaria') estaba fijo al
        # cierre de F5. AF conserva el mismo resultado por defecto.
        compacto = _compacto(HTML)
        self.assertIn(
            "constID_PERFIL_ACTIVO=PERFIL_EMBEBIDO?.id||"
            "newURLSearchParams(window.location.search).get('perfil')||"
            "'accion-fiduciaria'",
            compacto,
        )
        self.assertIn("constPERFIL=resolverPerfil(ID_PERFIL_ACTIVO)", compacto)


if __name__ == "__main__":
    unittest.main()
