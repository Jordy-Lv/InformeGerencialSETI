"""
Pruebas de reconciliar()/verificar() (extraer_indisponibilidades.py) —
unittest de stdlib, sin dependencias nuevas.

Se corren con:
    python3 -m unittest discover -s automatizacion -p 'test_*.py'
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extraer_indisponibilidades import reconciliar, verificar  # noqa: E402


def _fila(caso_glpi, atribuible, **extra):
    base = {"cliente": "Accion Fiduciaria", "caso_glpi": caso_glpi, "atribuible": atribuible,
            "servicio": "", "objeto": "", "tipo_evento": "", "motivo": ""}
    base.update(extra)
    return base


def _incidente(id_glpi, categoria="INCIDENTES > Reportar Falla / Incidente"):
    return {"ID": id_glpi, "Categoría": categoria, "Tipo": None}


class TestReconciliarDuplicados(unittest.TestCase):
    """Hallazgo P3 (validación de recarga de insumos, 04/08/2026): dos filas
    del log para el mismo NUMERO CASO GLPI con «Atribuible a SETI» distinto
    ganaban en silencio (la última leída). Ahora se sigue resolviendo igual
    —no hay forma de adivinar cuál fila es la correcta— pero queda
    reportado en `duplicados` y en verificar()."""

    def test_sin_duplicados(self):
        filas = [_fila("111", "SI")]
        reconciliadas, duplicados = reconciliar(filas, {"111": _incidente("111")})
        self.assertEqual(duplicados, {})
        self.assertEqual(reconciliadas[0]["atribuible"], "SI")

    def test_detecta_duplicado_con_atribucion_distinta(self):
        filas = [_fila("111", "SI"), _fila("111", "NO")]
        reconciliadas, duplicados = reconciliar(filas, {"111": _incidente("111")})
        self.assertIn("111", duplicados)
        self.assertEqual(duplicados["111"], ["SI", "NO"])
        # Comportamiento existente conservado: gana la última fila leída.
        self.assertEqual(reconciliadas[0]["atribuible"], "NO")

    def test_no_marca_duplicado_si_la_atribucion_es_igual(self):
        filas = [_fila("111", "SI"), _fila("111", "Si")]  # mismo valor, distinto caso
        _, duplicados = reconciliar(filas, {"111": _incidente("111")})
        self.assertEqual(duplicados, {})

    def test_verificar_reporta_los_duplicados(self):
        filas = [_fila("111", "SI"), _fila("111", "NO")]
        reconciliadas, duplicados = reconciliar(filas, {"111": _incidente("111")})
        problemas = verificar(reconciliadas, [], hubo_cruce=True, duplicados=duplicados)
        self.assertTrue(any("111" in p and "SI/NO" in p for p in problemas))

    def test_verificar_sin_duplicados_no_los_menciona(self):
        filas = [_fila("111", "SI")]
        reconciliadas, duplicados = reconciliar(filas, {"111": _incidente("111")})
        problemas = verificar(reconciliadas, [], hubo_cruce=True, duplicados=duplicados)
        self.assertFalse(any("NUMERO CASO GLPI aparece" in p for p in problemas))


if __name__ == "__main__":
    unittest.main()
