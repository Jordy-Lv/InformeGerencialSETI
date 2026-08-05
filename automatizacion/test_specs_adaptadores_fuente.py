"""Conformidad estática de F5: canónico, cabeceras y precedencia declarada."""

import re
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
HTML = (RAIZ / "informe-accion-fiduciaria 1.html").read_text(encoding="utf-8")
PERFIL = (RAIZ / "perfiles/accion-fiduciaria.js").read_text(encoding="utf-8")
BASE = (RAIZ / "perfiles/base.js").read_text(encoding="utf-8")
BANCOLDEX = (RAIZ / "perfiles/bancoldex.js").read_text(encoding="utf-8")
SPEC = (RAIZ / "openspec/specs/adaptadores-fuente/spec.md").read_text(encoding="utf-8")
DELTA = (
    RAIZ / "openspec/changes/2026-08-05-f5-adaptadores-canonico/specs/adaptadores-fuente/spec.md"
).read_text(encoding="utf-8")
DELTA_F7 = (
    RAIZ / "openspec/changes/2026-08-05-f7-bancoldex-aranda/specs/adaptadores-fuente/spec.md"
).read_text(encoding="utf-8")


class TestContratoOpenSpec(unittest.TestCase):
    def test_requisitos_y_escenarios_son_verificables(self):
        for nombre, documento in (("spec actual", SPEC), ("delta F5", DELTA), ("delta F7", DELTA_F7)):
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


class TestAdaptadorAranda(unittest.TestCase):
    """F7a — adaptador de Aranda (Bancóldex). No toca cargarGlpi()."""

    def test_adaptador_existe_y_no_reemplaza_glpi(self):
        for fragmento in (
            "function clasificarTipoAranda(tipoCaso)",
            "function adaptarArandaACanonico(rows,head,config,clienteFijo)",
            "async function cargarCasosAranda(file)",
        ):
            self.assertIn(fragmento, HTML)
        # cargarGlpi() sigue siendo exactamente la de F5: ninguna rama nueva
        # por cliente dentro de la función existente. El corte excluye el
        # comentario de F7a que la sigue (menciona "Aranda" en prosa).
        self.assertIn("async function cargarGlpi(file){\n  reset('glpi');", HTML)
        bloque_glpi = HTML[
            HTML.index("async function cargarGlpi"):
            HTML.index("/* F7a — cargador de casos de Aranda")
        ]
        self.assertNotIn("aranda", bloque_glpi.lower())

    def test_clasificador_colapsa_incidente_y_monitoreo(self):
        bloque = HTML[HTML.index("function clasificarTipoAranda"):HTML.index("function adaptarArandaACanonico")]
        self.assertIn("valor==='requerimiento'", bloque)
        self.assertIn("valor==='incidente'||valor==='incidente monitoreo'", bloque)
        self.assertIn("return 'otro'", bloque)

    def test_sla_columna_cumplimiento_es_triestado(self):
        bloque = HTML[HTML.index("function adaptarArandaACanonico"):HTML.index("function metricasSlaCanonico")]
        self.assertIn("config.sla.verdaderos.includes(marcaCumplimiento)", bloque)
        self.assertIn("config.sla.falsos.includes(marcaCumplimiento)", bloque)
        self.assertIn(": null", bloque)

    def test_jerarquia_usa_separador_declarado(self):
        bloque = HTML[HTML.index("function adaptarArandaACanonico"):HTML.index("function metricasSlaCanonico")]
        self.assertIn("jerarquiaTexto.split(config.jerarquia.separador)", bloque)

    def test_cargador_no_publica_dominio_inexistente(self):
        bloque = HTML[HTML.index("async function cargarCasosAranda"):HTML.index("window.cargarCasosAranda")]
        self.assertNotIn("REPORTE.publicar(", bloque)
        self.assertIn("return {", bloque)

    def test_bancoldex_declara_fuente_casos_aranda(self):
        for fragmento in (
            "extiende: 'base'",
            "adaptador: 'aranda-export'",
            "jerarquia: {separador: '.'}",
            "estrategia: 'columna-cumplimiento'",
            "estrategia: 'archivo-alcance-unico'",
            "['numero del caso']",
            "['fecha registro']",
            "['indicardor de cumplimiento']",
        ):
            self.assertIn(fragmento, BANCOLDEX)
        self.assertNotRegex(BANCOLDEX, r"\bfunction\b|=>|\bclass\s")

    def test_base_no_representa_cliente_y_esta_registrado(self):
        self.assertIn("id: 'base'", BASE)
        self.assertIn("extiende: null", BASE)
        # Sin un contrato.inicio con fecha real declarado (la prosa del
        # comentario sí menciona la clave; ver test_specs_perfil_cliente.py
        # para la comprobación precisa por regex sobre el objeto).
        self.assertIn("'base': ()=>PERFIL_EMBEBIDO?.id==='base'?PERFIL_EMBEBIDO:window.PERFIL_BASE", HTML)
        self.assertIn("'bancoldex': ()=>PERFIL_EMBEBIDO?.id==='bancoldex'?PERFIL_EMBEBIDO:window.PERFIL_BANCOLDEX", HTML)


class TestLectoresConsolidadoGeneralizados(unittest.TestCase):
    """F7b — indicadores/backups/disponibilidad parametrizados por perfil,
    con el mismo valor por defecto que AF tenía codificado (0 diferencias)."""

    def test_cargar_casos_o_glpi_no_toca_cargarglpi(self):
        self.assertIn(
            "function cargarCasosOGlpi(file){ return PERFIL.fuentes?.casos ? cargarCasosAranda(file) : cargarGlpi(file); }",
            HTML,
        )
        for sitio in (
            "cargar:f=>cargarCasosOGlpi(f)",
            "procesarFuente('glpi','fileGlpi','glpi',cargarCasosOGlpi,'la sábana de casos')",
            "procesar('glpi',fg.files[0],cargarCasosOGlpi)",
        ):
            self.assertIn(sitio, HTML)
        # cargarGlpi() en sí no cambió: sigue siendo la de F5, sin ninguna
        # mención a Aranda dentro de su cuerpo.
        bloque_glpi = HTML[HTML.index("async function cargarGlpi"):HTML.index("/* F7a — cargador de casos de Aranda")]
        self.assertNotIn("aranda", bloque_glpi.lower())

    def test_indicadores_usa_definicion_declarada_con_default_af(self):
        self.assertIn(
            "const metricas=PERFIL.fuentes?.consolidado?.indicadores?.metricas||ETIQUETA_INDICADOR;",
            HTML,
        )
        self.assertIn(
            "const nombresHoja=PERFIL.fuentes?.consolidado?.indicadores?.hojas||['indicadores','inidcadores'];",
            HTML,
        )
        self.assertIn("const datos=rows.slice(h+1).filter(r=>!!definicionIndicador(r[cIndicador]));", HTML)

    def test_backups_usa_hoja_y_columna_declaradas_con_default_af(self):
        self.assertIn("const nombreHojaBackups=declaracionBackups?.hoja||'Backups';", HTML)
        self.assertIn("const nombreColBackups=norm(declaracionBackups?.columna||'instancias');", HTML)

    def test_meta_de_backups_configurable_por_perfil(self):
        self.assertIn(
            "const metaBackups=metaDeclarada===null?null:(metaDeclarada===undefined?99.3:Number(metaDeclarada)*100);",
            HTML,
        )

    def test_disponibilidad_por_tabla_despacha_sin_afectar_af(self):
        self.assertIn("function cargarDisponibilidadTabla(wb,declaracion){", HTML)
        self.assertIn(
            "if(declaracionDispo?.estrategia==='tabla-con-fechas') return cargarDisponibilidadTabla(wb,declaracionDispo);",
            HTML,
        )

    def test_linea_base_de_perfil_no_reemplaza_la_ficha_legado_de_af(self):
        self.assertIn("const ficha=PERFIL.lineaBase;", HTML)
        bloque = HTML[HTML.index("function renderC3()"):HTML.index("function renderC3()") + 2000]
        self.assertIn("if(!ficha){", bloque)
        self.assertIn("CN-'+con", bloque)  # rama legado de AF intacta

    def test_presentacion_de_tarjeta_es_solo_visual_no_logica(self):
        self.assertIn("function presentarTarjetaPerfil(tarjeta){", HTML)
        self.assertIn("const ajuste=PERFIL.tarjetas?.presentacion?.[tarjeta.id];", HTML)
        self.assertIn("return ids.map(id=>presentarTarjetaPerfil(INDICE_TARJETAS.get(id)));", HTML)

    def test_resumen_de_ci_usa_la_meta_del_dominio_no_un_literal(self):
        # Cuarto lugar con «99,30%» quemado, encontrado al probar en
        # navegador con datos reales completos (no al verificar solo la
        # lectura): actualizarTarjetasDesdeStore() pintaba el resumen de
        # c11 con el literal de AF sin importar la meta real del dominio.
        self.assertIn(
            "if(m) m.textContent=`${ok} de ${n} cumplen la meta de ${pct(ci.datos.meta??99.3,ci.datos.meta!=null?2:1)}`;",
            HTML,
        )
        self.assertNotIn("cumplen la meta de 99,30%`", HTML)


if __name__ == "__main__":
    unittest.main()
