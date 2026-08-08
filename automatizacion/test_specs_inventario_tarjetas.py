"""Conformidad estática de F3: inventario, perfil y motor legado."""

import re
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
HTML = (RAIZ / "informe-accion-fiduciaria 1.html").read_text(encoding="utf-8")
PERFIL = (RAIZ / "perfiles/accion-fiduciaria.js").read_text(encoding="utf-8")
NOVAVENTA = (RAIZ / "perfiles/novaventa.js").read_text(encoding="utf-8")
BANCOLDEX = (RAIZ / "perfiles/bancoldex.js").read_text(encoding="utf-8")
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
DELTA_F6 = (
    RAIZ
    / "openspec/changes/2026-08-05-f6-perfil-novaventa/specs/inventario-tarjetas/spec.md"
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
            ("delta F6", DELTA_F6),
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
            {"casos", "alertas", "glpi", "disponibilidad", "backups", "indicadores", "ci", "logros", "mitigaciones", "bolsa", "capacidad"},
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
        self.assertIn("const tarjetasPorSlide=new Map(INVENTARIO_TARJETAS.map", HTML)
        self.assertIn("const seleccionadas=new Set(TARJETAS_SELECCIONADAS.map", HTML)
        self.assertIn("return tarjeta ? seleccionadas.has(s.id)&&tarjeta.exportable : true", HTML)
        self.assertIn("jsonEmbebible(perfilEfectivo())", HTML)
        self.assertIn("tarjeta.hidden=!activas.has(t.id)", HTML)

    def test_novaventa_activa_capacidad_y_af_no_la_crea(self):
        self.assertRegex(NOVAVENTA, r"seleccionadas\s*:\s*\[(?s:.*?)'c10'")
        self.assertIn("id:'c10'", HTML)
        self.assertIn("function prepararTarjetaCapacidad()", HTML)
        self.assertIn("if(!PERFIL.fuentes?.consolidado?.capacidad) return;", HTML)
        self.assertIn("prepararTarjetaCapacidad();", HTML)
        self.assertIn("c10:renderC10", HTML)
        self.assertIn('class="capacity-chart"', HTML)
        self.assertIn('Ocupación por filesystem', HTML)


class TestTarjetasBancoldex(unittest.TestCase):
    """Change 2026-08-07: control de línea base (c3b) y firmas (c14)."""

    def test_las_tarjetas_nuevas_estan_en_el_inventario_y_el_dom(self):
        for tarjeta, renderizador in (("c3b", "renderC3b"), ("c14", "renderC14")):
            with self.subTest(tarjeta=tarjeta):
                self.assertIn(f"id:'{tarjeta}'", HTML)
                self.assertIn(f'id="tk-{tarjeta}"', HTML)
                self.assertIn(f'id="det-{tarjeta}"', HTML)
                self.assertIn(f"function {renderizador}()", HTML)
                self.assertIn(f"{tarjeta}:{renderizador}", HTML)

    def test_c13_no_se_reutiliza_para_una_tarjeta(self):
        """c13 ya identifica la diapositiva fija «Gracias»."""
        self.assertIn('class="slideCard" id="c13"', HTML)
        self.assertNotIn("id:'c13'", HTML)
        self.assertNotIn('id="tk-c13"', HTML)

    def test_bancoldex_selecciona_las_dos_tarjetas_y_af_no(self):
        self.assertRegex(BANCOLDEX, r"seleccionadas\s*:\s*\[(?s:.*?)'c3b'")
        self.assertRegex(BANCOLDEX, r"seleccionadas\s*:\s*\[(?s:.*?)'c14'")
        for tarjeta in ("'c3b'", "'c14'"):
            with self.subTest(tarjeta=tarjeta):
                self.assertNotIn(tarjeta, PERFIL)
                self.assertNotIn(tarjeta, NOVAVENTA)

    def test_el_export_poda_las_tarjetas_no_seleccionadas(self):
        """Sin esto, c3b y c14 viajaban dentro del entregable de AF."""
        self.assertIn(
            "const tarjetasActivas=new Set(TARJETAS_SELECCIONADAS.map(t=>t.legado.tarjeta));",
            HTML,
        )
        self.assertIn("if(!tarjetasActivas.has(e.id)) e.remove();", HTML)

    def test_la_diferencia_de_linea_base_la_calcula_el_motor(self):
        self.assertIn("diferencia:Number(f.actual)-Number(f.base)", HTML)
        self.assertNotIn("diferencia:", BANCOLDEX)

    def test_el_lienzo_de_firma_no_depende_del_tamano_en_pantalla(self):
        """El detalle está colapsado al montar: un buffer derivado del rect
        medía 0x0 y toDataURL() devolvía «data:,»."""
        self.assertIn("const FIRMA_ANCHO=600, FIRMA_ALTO=200;", HTML)
        self.assertIn("canvas.width=FIRMA_ANCHO; canvas.height=FIRMA_ALTO;", HTML)

    def test_el_perfil_no_transporta_trazos_de_firma(self):
        self.assertIn("firmantes:", BANCOLDEX)
        # La clave, no la palabra: el comentario del perfil explica justamente
        # por qué el trazo no vive ahí.
        self.assertNotRegex(BANCOLDEX, r"\btrazo\s*:")

    def test_las_columnas_de_mitigacion_son_opcionales(self):
        """AF entrega otro formato: sin declararlas, el marcado no cambia."""
        self.assertIn("function detalleMitigacion(r)", HTML)
        self.assertIn(
            "const cols=PERFIL.fuentes?.cualitativos?.columnas?.mitigaciones;\n    if(!cols) return '';",
            HTML,
        )
        # `columnas` a secas no sirve: AF la declara para otras fuentes. Lo
        # que este change añade es el bloque de columnas de mitigaciones.
        self.assertRegex(BANCOLDEX, r"mitigaciones\s*:\s*\{")
        self.assertNotRegex(PERFIL, r"mitigaciones\s*:\s*\{")
        self.assertNotRegex(NOVAVENTA, r"mitigaciones\s*:\s*\{")

    def test_el_avance_se_reescala_desde_fraccion(self):
        """La hoja trae 0.2; pctNum() no reescala y pintaba «0 %»."""
        self.assertIn("Math.abs(avance)<=1.01?avance*100:avance", HTML)

    def test_las_firmas_tienen_su_propia_seccion(self):
        """c14 colgaba de «Seguimiento del servicio» sin rótulo propio."""
        self.assertIn(
            '<div class="report-section-label" data-tarjetas="c14">'
            "<span>04</span><h2>Aprobación del informe</h2></div>",
            HTML,
        )

    def test_la_seccion_de_firmas_precede_a_su_tarjeta(self):
        rotulo = HTML.index('data-tarjetas="c14"')
        tarjeta = HTML.index('id="tk-c14"')
        self.assertLess(rotulo, tarjeta)
        # Y nada se interpone: el rótulo encabeza esa tarjeta, no otra.
        self.assertNotIn('id="tk-', HTML[rotulo:tarjeta])

    def test_un_rotulo_condicional_se_oculta_sin_sus_tarjetas(self):
        """Sin esto, Acción Fiduciaria vería una sección vacía —y el texto
        del rótulo saldría como diferencia en su A/B."""
        self.assertIn(
            "document.querySelectorAll('.report-section-label[data-tarjetas]')",
            HTML,
        )
        self.assertIn("rotulo.hidden=!suyas.some(id=>activas.has(id));", HTML)

    def test_el_rotulo_oculto_no_se_sigue_pintando(self):
        """`display:flex` gana sobre el `display:none` que el navegador da a
        `[hidden]`: el atributo estaba puesto y la sección se veía igual."""
        self.assertIn(
            ".dash-grid--proposal .report-section-label[hidden]{display:none}",
            HTML,
        )

    def test_el_rotulo_podado_no_viaja_en_el_entregable(self):
        self.assertIn(
            "if(!suyas.some(id=>idsActivos.has(id))) rotulo.remove();", HTML
        )

    def test_c14_usa_el_formato_compacto(self):
        """El formato ancho solapaba la etiqueta con el valor."""
        self.assertIn('<div class="tarjeta-kpi" id="tk-c14">', HTML)
        self.assertNotIn('dash-grid--full" id="tk-c14"', HTML)


class TestEntregableInteractivo(unittest.TestCase):
    """El HTML exportado tiene que responder al clic.

    El arnés A/B compara texto visible y estado, no atributos ni listeners,
    así que un entregable inerte le pasa por delante sin una sola diferencia.
    Estas aserciones cubren los cuatro defectos que lo dejaban muerto.
    """

    def test_la_tarjeta_generada_conserva_el_onclick_inline(self):
        """activarModales() asigna btn.onclick (propiedad), que no se
        serializa: el clon solo lleva atributos."""
        self.assertIn(
            'aria-controls="det-${t.id}" onclick="toggleTarjeta(this)"', HTML
        )

    def test_el_perfil_embebido_no_se_vuelve_a_resolver(self):
        """Ya viene resuelto; volver a hacerlo buscaba window.PERFIL_BASE,
        que el entregable no lleva, y rompía a Bancoldex y Novaventa."""
        self.assertIn("if(propio===PERFIL_EMBEBIDO) return propio;", HTML)

    def test_los_scripts_legados_toleran_que_falte_su_tabla(self):
        """#tbodyCI vive en c11: un perfil que no la selecciona no la lleva."""
        self.assertIn("const tb=document.getElementById('tbodyCI');\n  // Un perfil", HTML)
        self.assertIn("if(!tb) return;", HTML)

    def test_actualizar_resumen_tolera_la_ausencia_del_panel(self):
        """restaurarPresetTarjetas() la alcanza al abrir el entregable, y
        podarClon() ya eliminó #loadPanel."""
        self.assertIn("const resumen=document.getElementById('loadSummary');", HTML)
        self.assertIn("if(!resumen) return;", HTML)

    def test_el_modal_de_autoria_no_viaja_pero_su_contenido_si(self):
        self.assertIn("const modalClon=doc.getElementById('dashboardModal');", HTML)
        self.assertIn("destino?.querySelector('.tarjeta-kpi__detalle-inner')?.prepend(panel);", HTML)


if __name__ == "__main__":
    unittest.main()
