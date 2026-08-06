"""Verificación estática de la spec base de store-reporte.

No ejecuta ni modifica el HTML. Fija las invariantes estructurales que ya
están desplegadas mientras el monolito permanece reservado por la PR #12.
Solo usa unittest y biblioteca estándar.
"""

import re
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
HTML = (RAIZ / "informe-accion-fiduciaria 1.html").read_text(encoding="utf-8")
SPEC = (RAIZ / "openspec/specs/store-reporte/spec.md").read_text(encoding="utf-8")


def _delta(change, capacidad):
    """Lee el delta de un change, esté abierto o ya archivado.

    Un change cerrado se mueve a `openspec/changes/archivo/` (convención
    fijada el 05/08/2026, ver `openspec/changes/README.md`). Buscar en las
    dos ubicaciones evita que archivar un change rompa esta prueba, que fue
    exactamente lo que pasó al archivar este.
    """
    for base in ("openspec/changes", "openspec/changes/archivo"):
        ruta = RAIZ / base / change / "specs" / capacidad / "spec.md"
        if ruta.exists():
            return ruta.read_text(encoding="utf-8")
    raise FileNotFoundError(
        f"No se encontró el delta de {change}/{capacidad} ni abierto ni archivado"
    )


DELTA = _delta("2026-08-04-especificar-store-reporte", "store-reporte")


def _entre(inicio, fin):
    i = HTML.index(inicio)
    j = HTML.index(fin, i)
    return HTML[i:j]


def _compacto(texto):
    return re.sub(r"\s+", "", texto)


def _arreglo_js(nombre):
    m = re.search(rf"const\s+{re.escape(nombre)}\s*=\s*\[(.*?)\];", HTML, re.S)
    if not m:
        raise AssertionError(f"No se encontró el arreglo JS {nombre}")
    return re.findall(r"['\"]([^'\"]+)['\"]", m.group(1))


class TestContratoOpenSpec(unittest.TestCase):
    def test_cada_requisito_tiene_shall_y_escenario(self):
        for nombre, documento in (("spec actual", SPEC), ("delta", DELTA)):
            bloques = re.split(r"(?=^### Requirement:)", documento, flags=re.M)[1:]
            self.assertGreater(len(bloques), 0, nombre)
            for bloque in bloques:
                titulo = bloque.splitlines()[0]
                with self.subTest(documento=nombre, requisito=titulo):
                    self.assertIn("SHALL", bloque)
                    self.assertIn("#### Scenario:", bloque)


class TestStoreDesplegado(unittest.TestCase):
    def test_dominios_y_estados_son_los_especificados(self):
        self.assertEqual(
            _arreglo_js("ESTADOS"),
            [
                "no_cargado",
                "valido",
                "sin_registros_confirmado",
                "advertencia",
                "invalido",
            ],
        )
        # F4 conserva el store completo del preset predeterminado aunque una
        # selección temporal oculte tarjetas: los parsers no pierden su
        # destino. El contenido se prueba en la capacidad inventario-tarjetas.
        self.assertIn(
            "constDOMINIOS=[...newSet(TARJETAS_PREDETERMINADAS.flatMap(t=>t.dominios))];",
            _compacto(HTML),
        )
        self.assertIn(
            "constVACIO={estado:'no_cargado',datos:null,fuente:null,notas:[]};",
            _compacto(HTML),
        )

    def test_publicar_valida_antes_de_mutar(self):
        bloque = _entre("publicar(dominio,{estado", "limpiar(dominio)")
        valida_dominio = bloque.index("Dominio desconocido")
        valida_estado = bloque.index("Estado inválido")
        mutacion = bloque.index("this.dominios[dominio]={estado,datos,fuente,notas}")
        self.assertLess(valida_dominio, mutacion)
        self.assertLess(valida_estado, mutacion)
        self.assertIn("this.notificar()", bloque)

    def test_cifra_y_resuelto_conservan_la_semantica_de_cero_confirmado(self):
        store = _compacto(_entre("const REPORTE =", "window.REPORTE = REPORTE"))
        self.assertIn("returne==='valido'||e==='advertencia'", store)
        self.assertIn(
            "returnthis.cifra(dominio)||this.d(dominio).estado==='sin_registros_confirmado'",
            store,
        )

    def test_notificacion_se_agrupa_y_aisla_suscriptores(self):
        bloque = _entre("notificar(){", "publicar(dominio,{estado")
        self.assertIn("if(this._pendiente) return", bloque)
        self.assertIn("Promise.resolve().then", bloque)
        self.assertIn("this._pendiente=false", bloque)
        self.assertIn("this._subs.forEach", bloque)
        self.assertIn("try{ fn(this); }catch", bloque)
        self.assertIn("suscriptor falló", bloque)

    def test_cambio_de_periodo_limpia_store_y_confirmaciones(self):
        bloque = _entre("function aplicarPeriodo(){", "let colaRevalidacion")
        self.assertIn("periodoActivo&&periodoActivo!==firma", bloque)
        self.assertIn("DOMINIOS.forEach(d=>REPORTE.limpiar(d))", bloque)
        self.assertIn("REPORTE.reconciliaciones=[]", bloque)
        self.assertIn("CARGA.logros.confirmado=false", bloque)
        self.assertIn("CARGA.mitigaciones.confirmado=false", bloque)
        self.assertIn("REPORTE.periodo={mes,anio,etiqueta}", bloque)
        self.assertIn("void revalidar()", bloque)

    def test_rehidratacion_ocurre_antes_de_load_y_completa_vacio(self):
        marca = "if(window.__INFORME_CLIENTE__ && window.__ESTADO__){"
        self.assertLess(HTML.index(marca), HTML.index("window.addEventListener('load'"))
        bloque = _entre(marca, "function reset(t)")
        self.assertIn("if(est.periodo) REPORTE.periodo=est.periodo", bloque)
        self.assertIn("DOMINIOS.forEach", bloque)
        self.assertIn("{...VACIO,...est.dominios[k]}", bloque)
        self.assertIn("REPORTE.reconciliaciones=est.reconciliaciones||[]", bloque)
        self.assertIn("Object.assign(DATA_CASOS,est.DATA_CASOS)", bloque)

    def test_consumidores_y_autopruebas_participan_del_store(self):
        self.assertIn("REPORTE.suscribir(actualizarTarjetasDesdeStore)", HTML)
        self.assertIn("Casos: tarjeta y store coinciden", HTML)
        self.assertIn("Casos: modal y store coinciden", HTML)
        self.assertIn("Sesión sin insumos: ningún dominio publica cifras", HTML)
        self.assertIn("Sesión sin insumos: ningún chip afirma «Cumple»", HTML)


if __name__ == "__main__":
    unittest.main()
