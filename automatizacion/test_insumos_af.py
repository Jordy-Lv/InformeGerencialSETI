"""
Pruebas de clasificar_caso_glpi() (insumos_af.py) — unittest de stdlib, sin
dependencias nuevas (decisión del usuario, 02/08/2026).

Se corren con:
    python3 -m unittest discover -s automatizacion -p 'test_*.py'
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from insumos_af import clasificar_caso_glpi  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
