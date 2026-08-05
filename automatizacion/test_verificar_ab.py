"""Pruebas del arnés A/B y sus dorados persistentes (stdlib puro)."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verificar_ab import (  # noqa: E402
    ErrorDorado,
    _fixture,
    cargar_dorado,
    comparar_con_dorado,
    crear_dorado,
    guardar_dorado,
    main,
    texto_dorado,
)


class TestDorados(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        self.export = _fixture(mes=5, anio=2026)
        self.ruta_html = self.raiz / "export-sintetico.html"
        self.ruta_html.write_text(self.export, encoding="utf-8")
        self.ruta_dorado = self.raiz / "accion-fiduciaria-2026-06.json"

    def test_creacion_es_determinista_y_no_expone_valores(self):
        primero = crear_dorado(self.export, "accion-fiduciaria", "2026-06")
        segundo = crear_dorado(self.export, "accion-fiduciaria", "2026-06")
        self.assertEqual(texto_dorado(primero), texto_dorado(segundo))

        serializado = texto_dorado(primero)
        self.assertNotIn("54 casos", serializado)
        self.assertNotIn("CN-SINTETICO-001", serializado)
        self.assertNotIn("Ficha contractual detalle", serializado)
        self.assertEqual(primero["esquema"], 1)
        self.assertIn("__ESTADO__", primero["componentes"])

    def test_periodo_base_cero_debe_coincidir(self):
        with self.assertRaisesRegex(ErrorDorado, "no coincide"):
            crear_dorado(self.export, "accion-fiduciaria", "2026-07")

    def test_plantilla_sin_estado_no_es_export_valido(self):
        with self.assertRaisesRegex(ErrorDorado, "window.__ESTADO__"):
            crear_dorado("<html><body>plantilla</body></html>", "accion-fiduciaria", "2026-06")

    def test_export_igual_pasa_y_cifra_distinta_falla(self):
        dorado = crear_dorado(self.export, "accion-fiduciaria", "2026-06")
        self.assertEqual(comparar_con_dorado(self.export, dorado), [])

        cambiado = _fixture(valor_casos="999 casos", mes=5, anio=2026)
        diferencias = comparar_con_dorado(cambiado, dorado)
        reporte = "\n".join(diferencias)
        self.assertIn("__ESTADO__", reporte)
        self.assertIn(".tarjeta-kpi__valor", reporte)

    def test_no_sobrescribe_sin_opcion_explicita(self):
        dorado = crear_dorado(self.export, "accion-fiduciaria", "2026-06")
        guardar_dorado(self.ruta_dorado, dorado)
        original = self.ruta_dorado.read_bytes()

        with self.assertRaisesRegex(ErrorDorado, "ya existe"):
            guardar_dorado(self.ruta_dorado, dorado)
        self.assertEqual(self.ruta_dorado.read_bytes(), original)

        guardar_dorado(self.ruta_dorado, dorado, reemplazar=True)
        self.assertEqual(cargar_dorado(self.ruta_dorado), dorado)

    def test_cli_crea_verifica_y_detecta_regresion(self):
        salida = io.StringIO()
        errores = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = main([
                "--crear-dorado", str(self.ruta_html),
                "--cliente", "accion-fiduciaria",
                "--periodo", "2026-06",
                "--salida", str(self.ruta_dorado),
            ])
        self.assertEqual(codigo, 0, errores.getvalue())
        self.assertTrue(self.ruta_dorado.exists())

        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = main([str(self.ruta_html), "--contra-dorado", str(self.ruta_dorado)])
        self.assertEqual(codigo, 0)
        self.assertIn("0 diferencias", salida.getvalue())

        cambiado = self.raiz / "export-cambiado.html"
        cambiado.write_text(_fixture(valor_casos="999 casos", mes=5, anio=2026), encoding="utf-8")
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = main([str(cambiado), "--contra-dorado", str(self.ruta_dorado)])
        self.assertEqual(codigo, 1)
        self.assertIn("diferencia(s)", salida.getvalue())

    def test_json_guardado_solo_contiene_contrato_publico(self):
        dorado = crear_dorado(self.export, "accion-fiduciaria", "2026-06")
        guardar_dorado(self.ruta_dorado, dorado)
        guardado = json.loads(self.ruta_dorado.read_text(encoding="utf-8"))
        self.assertEqual(
            set(guardado),
            {"cliente", "componentes", "esquema", "huella_total", "periodo"},
        )


class TestCompatibilidadCli(unittest.TestCase):
    def test_comparacion_directa_de_dos_html_se_conserva(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            a = raiz / "a.html"
            b = raiz / "b.html"
            a.write_text(_fixture(), encoding="utf-8")
            b.write_text(_fixture(), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(a), str(b)]), 0)

            b.write_text(_fixture(valor_casos="999 casos"), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(a), str(b)]), 1)


if __name__ == "__main__":
    unittest.main()
