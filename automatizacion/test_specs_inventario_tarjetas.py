"""Conformidad estática de F3: inventario, perfil y motor legado."""

import re
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
HTML = (RAIZ / "informe-accion-fiduciaria 1.html").read_text(encoding="utf-8")
PERFIL = (RAIZ / "perfiles/accion-fiduciaria.js").read_text(encoding="utf-8")
SPEC = (RAIZ / "openspec/specs/inventario-tarjetas/spec.md").read_text(encoding="utf-8")
DELTA = (
    RAIZ
    / "openspec/changes/2026-08-05-f3-inventario-tarjetas/specs/inventario-tarjetas/spec.md"
).read_text(encoding="utf-8")
DELTA_STORE = (
    RAIZ
    / "openspec/changes/2026-08-05-f3-inventario-tarjetas/specs/store-reporte/spec.md"
).read_text(encoding="utf-8")
DELTA_F4_INVENTARIO = (
    RAIZ
    / "openspec/changes/2026-08-05-f4-plantilla-preset/specs/inventario-tarjetas/spec.md"
).read_text(encoding="utf-8")
DELTA_F4_PRESET = (
    RAIZ
    / "openspec/changes/2026-08-05-f4-plantilla-preset/specs/preset-tarjetas/spec.md"
).read_text(encoding="utf-8")

IDS = ["c3", "c4", "c5", "c6", "c7", "c8", "c8m", "c9", "c11", "c12"]
CRITERIOS = [
    "Indicadores del periodo (3 métricas)",
    "GLPI: requerimientos, incidentes y SLA",
    "AlertsList: total y prioridad alta",
    "Disponibilidad por CI",
    "Ejecución de backups",
    "Logros importados o ausencia confirmada",
    "Mitigaciones importadas o ausencia confirmada",
]


class TestContratoOpenSpec(unittest.TestCase):
    def test_cada_requisito_tiene_shall_y_escenario(self):
        for nombre, documento in (
            ("spec actual", SPEC),
            ("delta inventario", DELTA),
            ("delta store", DELTA_STORE),
            ("delta F4 inventario", DELTA_F4_INVENTARIO),
            ("delta F4 preset", DELTA_F4_PRESET),
        ):
            bloques = re.split(r"(?=^### Requirement:)", documento, flags=re.M)[1:]
            self.assertGreater(len(bloques), 0, nombre)
            for bloque in bloques:
                with self.subTest(documento=nombre, requisito=bloque.splitlines()[0]):
                    self.assertIn("SHALL", bloque)
                    self.assertIn("#### Scenario:", bloque)


class TestInventarioDesplegado(unittest.TestCase):
    def test_perfil_declara_las_diez_tarjetas_en_orden(self):
        patron = r"seleccionadas\s*:\s*\[(.*?)\]"
        encontrados = re.search(patron, PERFIL, re.S)
        self.assertIsNotNone(encontrados)
        self.assertEqual(re.findall(r"['\"]([^'\"]+)['\"]", encontrados.group(1)), IDS)

    def test_cada_tarjeta_declara_su_identidad_legado(self):
        for tarjeta in IDS:
            with self.subTest(tarjeta=tarjeta):
                sufijo = tarjeta[1:]
                self.assertRegex(HTML, rf"(?s)id:'{re.escape(tarjeta)}'.*?tarjeta:'tk-{re.escape(tarjeta)}'.*?slide:'s{re.escape(sufijo)}'")
                self.assertIn(f'id="tk-{tarjeta}"', HTML)
                self.assertIn(f'id="s{sufijo}"', HTML)

    def test_criterios_conservan_texto_y_orden(self):
        inventario = HTML[HTML.index("const INVENTARIO_TARJETAS"):HTML.index("const INDICE_TARJETAS")]
        posiciones = [inventario.index(texto) for texto in CRITERIOS]
        self.assertEqual(posiciones, sorted(posiciones))
        self.assertIn("TARJETAS_SELECCIONADAS.flatMap", HTML)
        self.assertNotIn("const c=CARGA.consolidado;\n  return [", HTML)

    def test_listas_fijas_se_derivan_del_inventario(self):
        self.assertIn("const DOMINIOS=[...new Set(TARJETAS_PREDETERMINADAS.flatMap", HTML)
        self.assertIn("TARJETAS_SELECCIONADAS.flatMap(t=>t.fuentes)", HTML)
        self.assertIn("const RENDERIZADORES_TARJETA=", HTML)
        self.assertIn("TARJETAS_SELECCIONADAS.forEach(t=>{", HTML)

    def test_inventario_conserva_los_diez_dominios_del_store(self):
        inventario = HTML[HTML.index("const INVENTARIO_TARJETAS"):HTML.index("const INDICE_TARJETAS")]
        dominios = set(re.findall(r"dominios:\[([^\]]*)\]", inventario))
        valores = set()
        for grupo in dominios:
            valores.update(re.findall(r"['\"]([^'\"]+)['\"]", grupo))
        self.assertEqual(
            valores,
            {"casos", "alertas", "glpi", "disponibilidad", "backups", "indicadores", "ci", "logros", "mitigaciones", "bolsa"},
        )

    def test_autoprueba_embebida_coteja_inventario_y_dom(self):
        self.assertIn("Inventario: las diez tarjetas declaradas corresponden al DOM legado", HTML)
        self.assertIn("Inventario: los siete criterios se derivan de las tarjetas", HTML)

    def test_plantilla_y_preset_se_construyen_desde_el_inventario(self):
        for tarjeta in IDS:
            with self.subTest(tarjeta=tarjeta):
                self.assertRegex(
                    HTML,
                    rf"(?s)id:'{re.escape(tarjeta)}'.*?presentacion:\{{.*?\}}",
                )
        self.assertIn("function montarTarjetasDesdeInventario()", HTML)
        self.assertIn("function resumenTarjeta(t)", HTML)
        self.assertIn("const CLAVE_PRESET_TARJETAS=claveAlmacen('preset-tarjetas')", HTML)
        self.assertIn("function resolverPresetGuardado()", HTML)
        self.assertIn("function aplicarPresetTarjetas(ids", HTML)

    def test_pdf_y_exportado_usan_la_seleccion_efectiva(self):
        self.assertIn("const seleccionadas=new Map(TARJETAS_SELECCIONADAS.map", HTML)
        self.assertIn("jsonEmbebible(perfilEfectivo())", HTML)
        self.assertIn("tarjeta.hidden=!activas.has(t.id)", HTML)


if __name__ == "__main__":
    unittest.main()
