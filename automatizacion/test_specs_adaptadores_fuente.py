"""Conformidad estática de F5: canónico, cabeceras y precedencia declarada."""

import re
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
HTML = (RAIZ / "informe-accion-fiduciaria 1.html").read_text(encoding="utf-8")
PERFIL = (RAIZ / "perfiles/accion-fiduciaria.js").read_text(encoding="utf-8")
SPEC = (RAIZ / "openspec/specs/adaptadores-fuente/spec.md").read_text(encoding="utf-8")
DELTA = (
    RAIZ / "openspec/changes/2026-08-05-f5-adaptadores-canonico/specs/adaptadores-fuente/spec.md"
).read_text(encoding="utf-8")


class TestContratoOpenSpec(unittest.TestCase):
    def test_requisitos_y_escenarios_son_verificables(self):
        for nombre, documento in (("spec actual", SPEC), ("delta F5", DELTA)):
            bloques = re.split(r"(?=^### Requirement:)", documento, flags=re.M)[1:]
            self.assertGreater(len(bloques), 0, nombre)
            for bloque in bloques:
                with self.subTest(documento=nombre, requisito=bloque.splitlines()[0]):
                    self.assertIn("SHALL", bloque)
                    self.assertIn("#### Scenario:", bloque)


class TestAdaptadoresCanonicos(unittest.TestCase):
    def test_modelo_y_adaptadores_existen(self):
        for fragmento in (
            "function casoCanonico(caso)",
            "function adaptarGlpiACanonico(rows,head,config)",
            "function adaptarAlertasACanonico(rows,head,clienteDeFila)",
            "const TIPOS_CASO_CANONICO",
            "slaCumplido:caso.slaCumplido",
            "atribuibleSeti:caso.atribuibleSeti",
        ):
            self.assertIn(fragmento, HTML)

    def test_sla_nulo_no_es_cumplimiento(self):
        self.assertIn("c.slaCumplido===true", HTML)
        self.assertIn("F5: SLA desconocido no cuenta como cumplimiento", HTML)
        self.assertIn("slaCumplido:null", HTML)

    def test_cabecera_ambigua_se_rechaza_con_candidatos(self):
        self.assertIn("function candidatosCabecera(rows,campos)", HTML)
        self.assertIn("function resolverCabecera(rows,campos,estrategia='primera-fila-con')", HTML)
        self.assertIn("Encabezado ambiguo: las filas ${candidatos.join(', ')}", HTML)
        self.assertIn("resolverCabecera(rows,fuenteGlpi.cabecera.campos", HTML)
        self.assertIn("resolverCabecera(rows,campos,fuenteAlertas.cabecera.estrategia)", HTML)

    def test_perfil_declara_fuentes_y_precedencia(self):
        for fragmento in (
            "fuentes:", "lector: 'tabular-xlsx'", "clasificador: 'glpi-por-categoria'",
            "{id: 'alertops', precedencia: 1, ambito: 'mes-en-curso'}",
            "{id: 'consolidado-data', precedencia: 2, ambito: 'historico'}",
        ):
            self.assertIn(fragmento, PERFIL)
        self.assertIn("function resolverOrigenAlternativo(declaracion,ambito)", HTML)
        self.assertIn("reconciliarAlertas()", HTML)

    def test_cargadores_conservan_sus_nombres_y_pasan_por_adaptador(self):
        self.assertRegex(HTML, r"(?s)async function cargarGlpi\(file\).*?adaptarGlpiACanonico")
        self.assertRegex(HTML, r"(?s)async function cargarAlertas\(file\).*?adaptarAlertasACanonico")


if __name__ == "__main__":
    unittest.main()
