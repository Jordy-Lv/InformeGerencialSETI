"""Conformidad estática de F5: canónico, cabeceras y precedencia declarada."""

import re
import unittest
from pathlib import Path

try:
    from .deltas_openspec import leer_delta
except ImportError:  # ejecución directa del archivo, sin paquete
    from deltas_openspec import leer_delta


RAIZ = Path(__file__).resolve().parent.parent
HTML = (RAIZ / "informe-accion-fiduciaria 1.html").read_text(encoding="utf-8")
PERFIL = (RAIZ / "perfiles/accion-fiduciaria.js").read_text(encoding="utf-8")
BANCOLDEX = (RAIZ / "perfiles/bancoldex.js").read_text(encoding="utf-8")
SPEC = (RAIZ / "openspec/specs/adaptadores-fuente/spec.md").read_text(encoding="utf-8")
DELTA = leer_delta("2026-08-05-f5-adaptadores-canonico", "adaptadores-fuente")
DELTA_F7 = leer_delta("2026-08-05-f7-bancoldex-aranda", "adaptadores-fuente")


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
    """F7 (portado el 06/08/2026) — adaptador de Aranda para Bancoldex.
    No toca cargarGlpi(); ver openspec/changes/2026-08-05-f7-bancoldex-aranda/."""

    def test_adaptador_existe_y_no_reemplaza_glpi(self):
        for fragmento in (
            "function clasificarTipoAranda(tipoCaso)",
            "function adaptarArandaACanonico(rows,head,config,clienteFijo)",
            "async function cargarCasosAranda(file)",
        ):
            self.assertIn(fragmento, HTML)
        self.assertIn("async function cargarGlpi(file){\n  reset('glpi');", HTML)
        # cargarGlpi() puede mencionar a Aranda en un comentario cruzado (para
        # explicar por qué un perfil sin `fuentes.glpi` sale temprano), pero
        # su cuerpo no debe invocar el adaptador de Aranda: esa es la
        # garantía real de "no se reescribe cargarGlpi()".
        bloque_glpi = HTML[
            HTML.index("async function cargarGlpi"):
            HTML.index("/* Cierre Bancoldex: Aranda publica")
        ]
        self.assertNotIn("adaptarArandaACanonico(", bloque_glpi)

    def test_clasificador_colapsa_incidente_y_monitoreo(self):
        bloque = HTML[HTML.index("function clasificarTipoAranda"):HTML.index("function adaptarArandaACanonico")]
        self.assertIn("valor==='requerimiento'", bloque)
        self.assertIn("valor==='incidente'||valor==='incidente monitoreo'", bloque)
        self.assertIn("return 'otro'", bloque)

    def test_sla_columna_cumplimiento_es_triestado(self):
        bloque = HTML[HTML.index("function adaptarArandaACanonico"):HTML.index("function resolverOrigenAlternativo")]
        self.assertIn("config.sla.verdaderos.includes(marcaCumplimiento)", bloque)
        self.assertIn("config.sla.falsos.includes(marcaCumplimiento)", bloque)
        self.assertIn(": null", bloque)

    def test_jerarquia_usa_separador_declarado(self):
        bloque = HTML[HTML.index("function adaptarArandaACanonico"):HTML.index("function resolverOrigenAlternativo")]
        self.assertIn("jerarquiaTexto.split(config.jerarquia.separador)", bloque)

    def test_cargador_publica_en_dominio_casos_derivado(self):
        bloque = HTML[HTML.index("async function cargarCasosAranda"):HTML.index("window.cargarCasosAranda")]
        self.assertIn("REPORTE.publicar('casos'", bloque)
        self.assertNotIn("REPORTE.publicar('aranda'", bloque)
        self.assertIn("modo:'aranda-tipo-motor'", bloque)
        self.assertIn("return {", bloque)

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

    def test_configuracion_de_tarjeta_es_declarativa(self):
        self.assertIn("function presentarTarjetaPerfil(tarjeta){", HTML)
        self.assertIn("const configuracion=PERFIL.tarjetas?.configuracion?.[tarjeta.id];", HTML)
        self.assertIn("const ajuste=PERFIL.tarjetas?.presentacion?.[tarjeta.id];", HTML)
        self.assertIn("return ids.map(id=>presentarTarjetaPerfil(INDICE_TARJETAS.get(id)));", HTML)

    def test_modal_aranda_reutiliza_graficas_y_no_tablas(self):
        # Rediseño del 06/08/2026 (feedback en vivo): con un solo periodo real
        # de Aranda, montarHistorico() (rango 3M/6M/12M + resumen de 4 líneas)
        # no aporta nada — todas las cifras son idénticas al total. Se
        # reemplazó por un gráfico de barras propio "Casos por tipo".
        bloque = HTML[
            HTML.index("if(x.modo==='aranda-tipo-motor'){"):
            HTML.index("const m=metricasCasos(x);")
        ]
        self.assertNotIn("montarHistorico", bloque)
        self.assertIn("dash-chart-aranda-tipo", bloque)
        self.assertIn("dash-chart-aranda-motores", bloque)
        self.assertIn("dash-chart-aranda-categorias", bloque)
        self.assertIn("montarAnalisis", bloque)
        self.assertNotIn("<table", bloque)

    def test_modal_aranda_no_reemplaza_incidentes_por_sla(self):
        # Corrección del 06/08/2026 tras feedback en vivo: el panel
        # "Incidentes atribuibles a SETI" debe quedar EXACTO al de Acción
        # Fiduciaria — mismo título, un solo badge, nada más ahí (ni SLA ni
        # una etiqueta distinta como "Incidentes reales"). El cumplimiento
        # de SLA se muestra aparte, en su propio panel con gauge circular
        # (componente .gauge-exec ya existente en el motor, sin usar hasta
        # ahora). La validación de qué cuenta como "atribuible a SETI" para
        # Aranda queda pendiente de definir con el usuario — no se resuelve
        # aquí; ver design.md.
        bloque = HTML[
            HTML.index("if(x.modo==='aranda-tipo-motor'){"):
            HTML.index("const m=metricasCasos(x);")
        ]
        self.assertIn("<h4>Incidentes atribuibles a SETI</h4>", bloque)
        self.assertNotIn("case-analysis__badges", bloque)
        # El panel de incidentes no debe contener el texto de SLA: son cosas
        # separadas, cada una con su propio panel.
        panel_incidentes = bloque[bloque.index("<h4>Incidentes atribuibles a SETI</h4>"):bloque.index("</section>`+")]
        self.assertNotIn("Cumplimiento SLA", panel_incidentes)
        self.assertNotIn("Cumplimiento del SLA", panel_incidentes)
        self.assertIn("gauge('Cumplimiento SLA',slaPct,100)", bloque)
        self.assertIn("<h4>Cumplimiento del SLA</h4>", bloque)
        self.assertIn("norm(c.categoria)==='incidente'", HTML)
        self.assertIn("incidentesReales:{total:incidentesReales.length,cumplidos:slaIncidentesReales.cumplidos}", HTML)

    def test_gauge_exec_reserva_espacio_lateral_para_el_rotulo(self):
        # Hallazgo de la verificación visual del 07/08/2026: `.gauge-exec` es
        # un grid de 150 px con `place-content:center` y sin padding, así que
        # el <span> del rótulo ocupaba los 150 px completos y el texto
        # («Cumplimiento SLA · meta 100%») cruzaba el anillo de color por los
        # dos lados. El padding lateral lo confina al círculo blanco interior
        # (`:before` con inset:10px). Medido en navegador tras la corrección:
        # la esquina de texto más lejana queda a 55,7 px del centro, dentro
        # del radio interior de 65 px.
        regla = HTML[HTML.index(".gauge-exec{"):HTML.index(".gauge-exec:before")]
        self.assertIn("padding:0 26px", regla)
        self.assertIn("width:150px", regla)

    def test_alertslist_no_reemplaza_casos_de_un_perfil_con_fuente_propia(self):
        # publicarCasos(): un perfil con fuentes.casos gestiona su propio
        # dominio 'casos'; este modelo alertas+GLPI no debe sobrescribirlo.
        bloque_publicar = HTML[HTML.index("function publicarCasos()"):HTML.index("function actualizarTarjetaCasos()")]
        self.assertIn("if(PERFIL.fuentes?.casos) return;", bloque_publicar)
        # cargarAlertas(): el bloque que repinta DATA_CASOS/#s5/chartCasos
        # queda condicionado; validar/contar/publicar 'alertas' sigue sin
        # condición (AlertsList se interpreta igual para Bancoldex).
        bloque_alertas = HTML[HTML.index("async function cargarAlertas(file)"):HTML.index("async function cargarAlertasDataAlternativa")]
        self.assertIn("if(!PERFIL.fuentes?.casos){", bloque_alertas)
        self.assertIn("REPORTE.publicar('alertas',{", bloque_alertas)
        # actualizarTarjetaCasos() despacha por el modo publicado, no por perfil,
        # porque varios sitios lo llaman sin saber cuál está activo.
        self.assertIn("if(casosPerfil?.modo==='aranda-tipo-motor') return actualizarTarjetaCasosAranda(casosPerfil);", HTML)

    def test_bancoldex_declara_fuente_casos_aranda_y_alertas(self):
        for fragmento in (
            "extiende: 'base'",
            "adaptador: 'aranda-export'",
            "jerarquia: {separador: '.'}",
            "estrategia: 'columna-cumplimiento'",
            "estrategia: 'archivo-alcance-unico'",
            "['numero del caso']",
            "['fecha registro']",
            "['indicardor de cumplimiento']",
            "glpiTitulo: '2. Exportación Aranda'",
        ):
            self.assertIn(fragmento, BANCOLDEX)
        # Mismo formato genérico de AlertsList que ya usan AF/Novaventa.
        self.assertIn("['alert id', 'alertid']", BANCOLDEX)
        self.assertIn("['created date', 'fecha']", BANCOLDEX)
        self.assertNotRegex(BANCOLDEX, r"\bfunction\b|=>|\bclass\s")

    def test_etiqueta_de_casos_usa_data_perfil_carga(self):
        self.assertIn('data-perfil-carga="glpiTitulo"', HTML)
        self.assertIn('data-perfil-carga="glpiAyuda"', HTML)
        # Default embebido en el HTML cuando el perfil no declara textos.carga.
        self.assertIn(">2. Exportación GLPI<", HTML)

    def test_bancoldex_declara_alertas_en_dominios_y_fuentes_de_c5(self):
        # Hallazgo del 06/08/2026 al probar en navegador: sin 'alertas' en
        # ambas listas, REPORTE.publicar('alertas',...) lanzaba "Dominio
        # desconocido" y validarArchivo('alertas',...) rechazaba cualquier
        # extensión (EXTENSIONES_INSUMO solo registra una fuente si algún
        # tarjeta.fuentes seleccionado la declara).
        self.assertIn("dominios: ['casos', 'alertas']", BANCOLDEX)
        self.assertIn("fuentes: ['glpi', 'alertas']", BANCOLDEX)

    def test_insumos_automaticos_no_se_cargan_para_un_perfil_con_fuente_propia(self):
        # cargarInsumosAutomaticos() intenta un <script> vecino (insumos-af.js)
        # que es de Acción Fiduciaria; sin este guard, un consultor con ese
        # archivo de desarrollo en disco veía el periodo de Bancoldex saltar
        # al mes que trajera ese paquete (hallazgo real, no hipotético).
        bloque = HTML[HTML.index("async function cargarInsumosAutomaticos"):HTML.index("function revalidar()")]
        self.assertIn("if(PERFIL.fuentes?.casos) return;", bloque)


if __name__ == "__main__":
    unittest.main()


class TestConsolidadoNoPisaLaFuentePropiaDeCasos(unittest.TestCase):
    """`cargarCasos()` (hoja «Casos» del consolidado, modelo alertas/
    requerimientos/incidentes de AF) no debe correr para un perfil con fuente
    propia de casos.

    Bug real del 07/08/2026: el consolidado de Bancoldex SÍ trae hoja
    «Casos», y `pintarCasosArandaEnSlide()` ya había reemplazado
    `chartCasos.data.datasets` por una serie por tipo de caso. La escritura
    sobre `datasets[0..2]` o corrompía las cifras de Aranda, o —cuando el
    periodo no tenía casos y `datasets` quedaba vacío— lanzaba un TypeError
    que abortaba el try de `cargarConsolidado()` entero y bloqueaba la
    exportación.
    """

    def test_cargar_casos_tiene_guard_por_fuente_propia(self):
        cuerpo = HTML[HTML.index("function cargarCasos(wb)"):HTML.index("let alertasConsolidadoMes")]
        self.assertIn("if(PERFIL.fuentes?.casos){ alertasConsolidadoMes=null; return null; }", cuerpo)

    def test_el_guard_precede_a_la_escritura_sobre_el_grafico(self):
        cuerpo = HTML[HTML.index("function cargarCasos(wb)"):HTML.index("let alertasConsolidadoMes")]
        self.assertLess(
            cuerpo.index("if(PERFIL.fuentes?.casos)"),
            cuerpo.index("chartCasos.data.datasets[0].data"),
        )

    def test_accion_fiduciaria_conserva_la_lectura_de_la_hoja_casos(self):
        # El guard es por fuente declarada, no por nombre de perfil. AF trae
        # sus casos por GLPI y no declara `fuentes.casos`, así que sigue
        # leyendo la hoja «Casos» igual que antes de este change.
        claves = re.findall(r"^    ([a-zA-Z]+): \{", PERFIL[PERFIL.index("\n  fuentes: {"):], re.M)
        self.assertIn("glpi", claves)
        self.assertNotIn("casos", claves)


class TestExtensionesAdmitidasSeResuelvenAlValidar(unittest.TestCase):
    """El mapa de extensiones por insumo se calculaba una sola vez al parsear,
    contra el preset inicial. `TARJETAS_SELECCIONADAS` se reasigna después
    (restauración del preset y UI de «Tarjetas»), así que quedaba obsoleto y
    la entrada afectada rechazaba todo con la lista vacía: «Usa .».
    Bug real del 07/08/2026.
    """

    def test_es_una_funcion_y_no_un_const_congelado(self):
        self.assertIn("function extensionesInsumo()", HTML)
        self.assertNotIn("const EXTENSIONES_INSUMO=", HTML)

    def test_validar_archivo_la_invoca_en_cada_llamada(self):
        cuerpo = HTML[HTML.index("function validarArchivo(tipo,file)"):HTML.index("function insumoProcesado(tipo)")]
        self.assertIn("extensionesInsumo()[tipo]", cuerpo)

    def test_el_mensaje_nunca_queda_sin_formatos(self):
        # Respaldo a la tabla base: una fuente sin tarjeta que la declare no
        # puede producir «Usa .» — eso no le dice nada al usuario.
        cuerpo = HTML[HTML.index("function validarArchivo(tipo,file)"):HTML.index("function insumoProcesado(tipo)")]
        self.assertIn("EXTENSIONES_POR_FUENTE[tipo]", cuerpo)


class TestInsumoRestauradoSeRevalida(unittest.TestCase):
    """`ejecutarRevalidacion()` recorre los `<input>`. Un insumo restaurado que
    no quede depositado en el suyo no se vuelve a leer al cambiar el periodo:
    se queda congelado con el resultado del mes con el que se guardó.

    Bug real del 07/08/2026: restaurar con el periodo en julio y corregirlo a
    junio dejaba el export de Aranda en «0 casos de jul-26» con el selector
    marcando Junio.
    """

    def _cuerpo_restaurar(self):
        return HTML[
            HTML.index("async function restaurarInsumosGuardados(automatico)"):
            HTML.index("async function borrarInsumosGuardados()")
        ]

    def test_el_archivo_restaurado_se_deposita_en_su_input(self):
        cuerpo = self._cuerpo_restaurar()
        self.assertIn("for(const {tipo,input,cargar} of INSUMOS_PERSIST)", cuerpo)
        self.assertIn("document.getElementById(input).files=dt.files", cuerpo)

    def test_se_deposita_antes_de_cargar(self):
        cuerpo = self._cuerpo_restaurar()
        self.assertLess(cuerpo.index("document.getElementById(input).files"), cuerpo.index("await cargar(f)"))

    def test_la_revalidacion_sigue_leyendo_de_los_inputs(self):
        # Si esto cambiara, el arreglo de arriba dejaría de ser el mecanismo
        # correcto y habría que revisarlo, no dejarlo por inercia.
        cuerpo = HTML[HTML.index("async function ejecutarRevalidacion()"):HTML.index("async function cargarAlertas(file)")]
        self.assertIn("if(fg&&fg.files[0]) await procesar('glpi',fg.files[0],cargarCasosOGlpi)", cuerpo)


class TestRecuentoDeInsumosObligatorios(unittest.TestCase):
    """La entrada física 'glpi' la comparten dos fuentes declarables: `glpi`
    (AF/Novaventa) y `casos` (Bancoldex vía Aranda). Contar solo `fuentes.glpi`
    dejaba a Aranda fuera del recuento pese a estar rotulado como obligatorio
    en pantalla. Alcance confirmado por el usuario el 07/08/2026: para
    Bancoldex AlertsList sí cuenta; lo que no aplica es GLPI.
    """

    def test_la_fuente_propia_de_casos_cuenta_como_insumo_obligatorio(self):
        self.assertIn(
            "const insumosObligatorios=['consolidado',"
            "...((PERFIL.fuentes?.glpi||PERFIL.fuentes?.casos)?['glpi']:[]),"
            "...(PERFIL.fuentes?.alertas?['alertas']:[])];",
            HTML,
        )

    def test_alertslist_sigue_contando_para_quien_lo_declare(self):
        # Bancoldex declara `fuentes.alertas`: AlertsList es obligatorio.
        self.assertIn("alertas: {", BANCOLDEX)

    def test_el_insumo_de_casos_se_resuelve_contra_su_propio_dominio(self):
        cuerpo = HTML[HTML.index("function insumoProcesado(tipo)"):HTML.index("const REGLAS_CRITERIO=")]
        self.assertIn("if(tipo==='glpi'&&PERFIL.fuentes?.casos) return REPORTE.resuelto('casos');", cuerpo)
