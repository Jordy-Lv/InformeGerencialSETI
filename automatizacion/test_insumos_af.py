"""
Pruebas de clasificar_caso_glpi() (insumos_af.py) — unittest de stdlib, sin
dependencias nuevas (decisión del usuario, 02/08/2026).

Se corren con:
    python3 -m unittest discover -s automatizacion -p 'test_*.py'
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from insumos_af import archivo_de, clasificar_caso_glpi, fijar_periodo, incrustar_insumos  # noqa: E402


class TestClasificarCasoGlpi(unittest.TestCase):
    """Categorías reales del muestreo de 1 660 tickets (auditoría F3,
    02/08/2026): con tres niveles, tomar solo el último («Jobs Fallidos», por
    ejemplo) no matcheaba «Revision Alerta» y el ticket se contaba como
    incidente real en vez de revisión."""

    CASOS = [
        ("INCIDENTES > Revision Alerta", "revision"),
        ("INCIDENTES > Revision Alerta > Alto numero de sesiones activas", "revision"),
        ("INCIDENTES > Revision Alerta > Jobs Fallidos", "revision"),
        ("INCIDENTES > Revision Alerta > Bloqueos", "revision"),
        ("INCIDENTES > Revision Alerta > Espacios", "revision"),
        ("INCIDENTES > Revision Alerta > Atraso replica", "revision"),
        ("INCIDENTES > Reportar Falla / Incidente", "incidente"),
        ("REQUERIMIENTOS > Solicitud de acceso", "requerimiento"),
    ]

    def test_categorias_del_muestreo(self):
        for categoria, esperado in self.CASOS:
            with self.subTest(categoria=categoria):
                self.assertEqual(clasificar_caso_glpi(categoria, None), esperado)

    def test_sin_categoria_usa_tipo(self):
        self.assertEqual(clasificar_caso_glpi(None, "Incidente"), "incidente")
        self.assertEqual(clasificar_caso_glpi("", "Requerimiento"), "requerimiento")

    def test_incidente_sin_niveles_tras_el_primero_no_es_revision(self):
        # Sin ">" en la categoría no hay forma de distinguir una revisión de
        # alerta de una falla real: se cuenta como incidente, no se inventa
        # una exclusión sin evidencia en la fuente.
        self.assertEqual(clasificar_caso_glpi("INCIDENTES", None), "incidente")

    def test_categoria_sin_coincidencia_es_otro(self):
        self.assertEqual(clasificar_caso_glpi("Otros > Varios", None), "otro")


class TestIncrustarInsumosIdempotente(unittest.TestCase):
    """Bug reportado 03/08/2026 (hallazgo P6 de la validación de recarga de
    insumos): incrustar dos veces dejaba dos bloques window.__INSUMOS__, y el
    viejo (el que queda más abajo en el documento) ganaba en silencio porque
    los <script> se ejecutan en orden de aparición."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.html_path = Path(self.tmp.name) / "informe.html"
        self.js_path = Path(self.tmp.name) / "insumos-af.js"

    def _escribir(self, texto_html, texto_js):
        self.html_path.write_text(texto_html, encoding="utf-8")
        self.js_path.write_text(texto_js, encoding="utf-8")

    def test_primera_incrustacion_inserta_tras_head(self):
        self._escribir("<html><head><title>x</title></head><body></body></html>",
                        "window.__INSUMOS__ = {\"periodo\":{\"mes\":5,\"anio\":2026}};\n")
        resultado = incrustar_insumos(self.html_path, self.js_path)
        self.assertEqual(resultado.count("window.__INSUMOS__"), 1)
        self.assertLess(resultado.index("window.__INSUMOS__"), resultado.index("<title>"))

    def test_segunda_incrustacion_reemplaza_no_duplica(self):
        self._escribir("<html><head><title>x</title></head><body></body></html>",
                        "window.__INSUMOS__ = {\"periodo\":{\"mes\":5,\"anio\":2026}};\n")
        primera = incrustar_insumos(self.html_path, self.js_path)
        self.html_path.write_text(primera, encoding="utf-8")
        self._escribir(primera,
                        "window.__INSUMOS__ = {\"periodo\":{\"mes\":6,\"anio\":2026}};\n")
        segunda = incrustar_insumos(self.html_path, self.js_path)
        self.assertEqual(segunda.count("window.__INSUMOS__"), 1)
        self.assertIn('"mes":6', segunda)
        self.assertNotIn('"mes":5', segunda)
        self.assertIn("<title>x</title>", segunda)


class TestPeriodoEnArchivoDe(unittest.TestCase):
    """Hallazgos P1+P2 (validación de recarga de insumos, 04/08/2026):
    fijar_periodo() avanza paquete['periodo'] sin tocar archivos.* de otras
    fuentes que no volvieron a correr. Cada archivos.<clave> ahora guarda su
    propio periodo para que el HTML pueda detectar el desfase."""

    def test_archivo_de_guarda_periodo_cuando_se_da(self):
        a = archivo_de(b"contenido", "x.csv", "origen", periodo="2026-07")
        self.assertEqual(a["periodo"], "2026-07")

    def test_archivo_de_sin_periodo_no_agrega_la_clave(self):
        a = archivo_de(b"contenido", "x.csv", "origen")
        self.assertNotIn("periodo", a)

    def test_fijar_periodo_no_toca_archivos_existentes(self):
        paquete = {"periodo": {"mes": 5, "anio": 2026},
                   "archivos": {"glpi": archivo_de(b"x", "glpi.csv", "o", periodo="2026-06")}}
        fijar_periodo(paquete, "2026-07")
        # archivos.glpi sigue con el periodo viejo: la desincronía real que
        # el HTML debe detectar comparando contra paquete['periodo'].
        self.assertEqual(paquete["archivos"]["glpi"]["periodo"], "2026-06")
        self.assertEqual(paquete["periodo"], {"mes": 6, "anio": 2026})


if __name__ == "__main__":
    unittest.main()
