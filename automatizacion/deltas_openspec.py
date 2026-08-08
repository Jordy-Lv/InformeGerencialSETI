"""Localiza el delta de spec de un change, esté abierto o ya archivado.

Las pruebas de conformidad leen los deltas de `openspec/changes/` para
comprobar que lo implementado coincide con lo especificado. El problema es
que un change no vive siempre en el mismo sitio: al cerrarse se mueve a
`openspec/changes/archivo/` (convención del 05/08/2026, ver
`openspec/changes/README.md`).

Con la ruta escrita a mano en cada prueba, archivar un change rompía la
suite entera — ya pasó al archivar `2026-08-04-especificar-store-reporte`, y
volvía a estar a punto de pasar con los siete de F1–F7. La corrección no es
recordar actualizar las rutas: es que la prueba no dependa de en qué fase
del ciclo está el change que la respalda.

Solo stdlib, como el resto de `automatizacion/`.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_BASES = ("openspec/changes", "openspec/changes/archivo")


def ruta_delta(change, capacidad):
    """Devuelve la ruta del delta, lo busque donde lo busque.

    Falla con el nombre del change y de la capacidad si no está en ninguna
    de las dos ubicaciones: un delta que desaparece es un error de la
    especificación, no algo que la prueba deba tolerar en silencio.
    """
    for base in _BASES:
        ruta = RAIZ / base / change / "specs" / capacidad / "spec.md"
        if ruta.exists():
            return ruta
    raise FileNotFoundError(
        f"No se encontró el delta de {change}/{capacidad}: "
        f"no está abierto en openspec/changes/ ni archivado en archivo/."
    )


def leer_delta(change, capacidad):
    return ruta_delta(change, capacidad).read_text(encoding="utf-8")
