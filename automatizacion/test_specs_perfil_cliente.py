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
NOVAVENTA = (RAIZ / "perfiles/novaventa.js").read_text(encoding="utf-8")
SPEC = (RAIZ / "openspec/specs/perfil-cliente/spec.md").read_text(encoding="utf-8")
DELTA = (
    RAIZ
    / "openspec/changes/2026-08-04-f1-perfil-cliente/specs/perfil-cliente/spec.md"
).read_text(encoding="utf-8")
DELTA_F2 = (
    RAIZ
    / "openspec/changes/2026-08-05-f2-contrato-perfil/specs/perfil-cliente/spec.md"
).read_text(encoding="utf-8")
DELTA_F6 = (
    RAIZ
    / "openspec/changes/2026-08-05-f6-perfil-novaventa/specs/perfil-cliente/spec.md"
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
            ("delta F6", DELTA_F6),
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
        self.assertIn("'accion-fiduciaria':()=>PERFIL_EMBEBIDO?.id==='accion-fiduciaria'", compacto)
        self.assertIn("window.PERFIL_ACCION_FIDUCIARIA", compacto)
        self.assertIn("'novaventa':()=>PERFIL_EMBEBIDO?.id==='novaventa'", compacto)
        self.assertIn("window.PERFIL_NOVAVENTA", compacto)
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


class TestCapacidadNovaventa(unittest.TestCase):
    def test_perfil_declara_capacidad_sin_convertirla_en_bolsa(self):
        codigo = _sin_comentarios(NOVAVENTA)
        self.assertIn("capacidad: {hojas: ['Capacidad']", codigo)
        self.assertIn("'c10'", codigo)
        self.assertNotIn("bolsa:", codigo)

    def test_capacidad_publica_su_dominio_independiente(self):
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn("functioncargarCapacidad(wb)", compacto)
        self.assertIn("REPORTE.publicar('capacidad'", HTML)
        bloque = HTML[HTML.index("function cargarCapacidad"):HTML.index("function cargarDisponibilidad")]
        self.assertNotIn("publicar('bolsa'", bloque)
        self.assertIn("filesystems", bloque)
        self.assertIn("ocupacionMaxima", bloque)
        self.assertIn("resolverCabecera(rows,declaracion.cabecera?.campos||[['cliente'],['tipo ci']],declaracion.cabecera?.estrategia).fila", bloque)

    def test_data_alternativa_ignora_el_resumen_posterior_al_bloque_de_alertas(self):
        bloque = HTML[HTML.index("async function cargarAlertasDataAlternativa"):HTML.index("// GLPI agrupa")]
        self.assertIn("const filasDetalle=[]", bloque)
        self.assertIn("if(filasDetalle.length) break", bloque)
        self.assertIn("const casos=filasDetalle.map", bloque)

    def test_data_de_otro_periodo_no_se_presenta_como_cero_confirmado(self):
        bloque = HTML[HTML.index("async function cargarAlertasDataAlternativa"):HTML.index("// GLPI agrupa")]
        self.assertIn("ninguna está fechada en ${etiquetaPeriodo(mes,anio)}", bloque)
        self.assertIn("const sinCoberturaPeriodo=!total&&casos.length", bloque)
        self.assertIn("const respaldoConsolidado=sinCoberturaPeriodo&&Number.isFinite(alertasConsolidadoMes)", bloque)
        self.assertIn("if(!respaldoConsolidado){ DATA_CASOS.alertas[i]=total", bloque)
        self.assertIn("estado:sinCoberturaPeriodo?(respaldoConsolidado?'advertencia':'invalido')", bloque)
        self.assertIn("bloquear('alertas',motivo)", bloque)
        self.assertIn("filasExcluidas:excluidas", bloque)
        self.assertIn("notas:CARGA.avisos.filter", bloque)

    def test_novaventa_declara_disponibilidad_en_la_tabla_del_corte_vigente(self):
        self.assertIn("disponibilidad: {estrategia: 'tabla-con-fechas', hoja: 'Grafica Dispo y Gestion', tabla: 'Disponibilidad Real'}", NOVAVENTA)
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn("functioncargarDisponibilidadTabla(wb,declaracion)", compacto)
        self.assertIn("declaracion?.estrategia==='tabla-con-fechas'", compacto)

    def test_novaventa_declara_su_taxonomia_de_indicadores(self):
        self.assertIn("aliases: ['cumplimiento tiempos de atencion']", NOVAVENTA)
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn("functiondefinicionIndicador(nombreFuente)", compacto)
        self.assertIn("filter(r=>!!definicionIndicador(r[cIndicador]))", compacto)

    def test_preset_novaventa_tiene_solo_tarjetas_con_fuente_o_referencia(self):
        seleccion = NOVAVENTA[NOVAVENTA.index("seleccionadas:"):NOVAVENTA.index("presentacion:")]
        self.assertIn("'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c10', 'c12'", seleccion)
        self.assertNotIn("'c9'", seleccion)
        self.assertNotIn("'c8m'", seleccion)
        self.assertNotIn("'c11'", seleccion)
        self.assertIn("inicio: '2025-07-21'", NOVAVENTA)
        self.assertIn("vigenciaHasta: '2026-07-20'", NOVAVENTA)
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn("functionpresentarTarjetaPerfil(tarjeta)", compacto)
        self.assertIn("constt=presentarTarjetaPerfil(base)", compacto)
        self.assertIn("functionrenderC3()", compacto)
        self.assertIn("constficha=PERFIL.lineaBase", compacto)

    def test_novaventa_orienta_el_destino_de_sus_dos_excel(self):
        self.assertIn("consolidadoTitulo: '1. Consolidado mensual Novaventa'", NOVAVENTA)
        self.assertIn("Data_<mes>.xlsx aquí", NOVAVENTA)
        self.assertIn("data-perfil-carga", HTML)
        self.assertIn("PERFIL.textos.carga", HTML)


class TestRegistroPersistenteDeClientes(unittest.TestCase):
    def test_registro_local_separa_perfiles_base_y_personalizados(self):
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn("constCLIENTES_REGISTRO_KEY='informe:clientes:registro:v1'", compacto)
        self.assertIn("functionleerRegistroClientes()", compacto)
        self.assertIn("functionguardarRegistroClientes(clientes)", compacto)
        self.assertIn("constIDS_PERFILES_BASE=Object.freeze(Object.keys(PERFILES_REGISTRADOS))", compacto)
        self.assertIn("functionobtenerPerfilRegistrado(id)", compacto)
        self.assertIn("PERFILES_REGISTRADOS[id]||(()=>obtenerPerfilRegistrado(id))", compacto)

    def test_cliente_nuevo_hereda_una_plantilla_validada(self):
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn("Tipodeinsumos", compacto)
        self.assertIn("IDS_PERFILES_BASE.includes(plantilla)", compacto)
        self.assertIn("extiende:plantilla", compacto)
        self.assertIn("Laautomatizacióninterpretaalcargar", compacto)
        self.assertIn("tarjetas:{seleccionadas,presentacion:presentacionInicialCliente(nombre)}", compacto)

    def test_alta_no_duplica_metricas_ni_tarjetas_de_los_insumos(self):
        bloque = HTML[HTML.index("function pintarGestionClientes"):HTML.index("function guardarClienteFormulario")]
        self.assertNotIn('name="metaDisponibilidad"', bloque)
        self.assertNotIn('name="tarjetas"', bloque)
        self.assertNotIn('name="instancias"', bloque)
        self.assertIn("no se registran manualmente al crear el cliente", bloque)
        guardar = HTML[HTML.index("function guardarClienteFormulario"):HTML.index("function eliminarCliente")]
        self.assertIn("metas:{disponibilidad:null,gestionServicio:null,entregables:null,backups:null}", guardar)
        self.assertIn("presentacion:presentacionInicialCliente(nombre)", guardar)
        self.assertIn("function presentacionInicialCliente(nombre)", HTML)

    def test_administrador_conserva_el_formulario_al_cambiar_plantilla(self):
        bloque = HTML[HTML.index("function pintarGestionClientes"):HTML.index("function guardarClienteFormulario")]
        self.assertIn('aria-haspopup="dialog"', HTML)
        self.assertIn('aria-expanded="false"', HTML)
        self.assertIn('data-insumos-descripcion', bloque)
        self.assertIn("detalle.textContent=", bloque)
        self.assertNotIn("plantillaNueva=e.target.value;pintarGestionClientes()", bloque)
        self.assertIn("document.getElementById('btnClientes')?.setAttribute('aria-expanded','true')", HTML)
        self.assertIn("document.getElementById('btnClientes')?.setAttribute('aria-expanded','false')", HTML)
        poda = HTML[HTML.index("function podarClon"):HTML.index("async function exportarHTML")]
        self.assertIn("doc.getElementById('clientesModal')?.remove()", poda)

    def test_barra_de_autoria_compacta_y_sin_ayuda_redundante(self):
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn(".topbar>.btn{width:140px;min-width:0;max-width:140px;height:40px;min-height:40px", compacto)
        self.assertNotIn('id="hintEdit"', HTML)
        self.assertNotIn("getElementById('hintEdit')", HTML)

    def test_preset_de_cliente_se_guarda_en_su_ficha(self):
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn("functionguardarPresetClienteActivo(ids)", compacto)
        self.assertIn("guardarPresetClienteActivo(idsTarjetasSeleccionadas())", compacto)
        self.assertIn("perfil:fusionarProfundo(cliente.perfil,{tarjetas:{seleccionadas:[...ids]}})", compacto)

    def test_eliminacion_no_permite_borrar_perfiles_base(self):
        compacto = _compacto(_sin_comentarios(HTML))
        self.assertIn("Plantillabaseprotegida", compacto)
        self.assertIn("functioneliminarCliente(id)", compacto)
        self.assertIn("filter(c=>c.id!==id)", compacto)
        self.assertIn("cambiarClienteActivo(cliente.plantilla)", compacto)


if __name__ == "__main__":
    unittest.main()
