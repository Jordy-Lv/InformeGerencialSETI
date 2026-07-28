#!/usr/bin/env python3
"""
Punto de entrada único para la tarea programada mensual.

Corre las dos extracciones —GLPI y AlertOps— una tras otra. Cada una:

  1. Llama a su API y descarga los datos.
  2. Guarda el insumo original en `salida/` (`glpi-AAAA-MM.csv`,
     `alertops-AAAA-MM.csv`) — el archivo tal cual llegó de la fuente, para
     archivo y auditoría.
  3. Aporta su parte a `salida/insumos-af.js`, la copia ya convertida
     (base64 + huella) que el informe sabe leer.

Este script añade el último paso, el que hasta ahora había que hacer a mano:
copia ese `insumos-af.js` **junto al HTML del informe**. Al abrirlo, las
fuentes que hayan funcionado ya están cargadas — nadie mueve un archivo.

Además, si `RUTA_ONEDRIVE` está configurada (`.env`), deja en la carpeta del
mes (junto a los CSV originales) un **HTML autocontenido**: no es una copia
del informe con `insumos-af.js` al lado — los datos quedan **incrustados
dentro del propio archivo** (`incrustar_insumos`), así que sigue abriendo con
todo cargado aunque alguien lo copie, lo descargue o lo mueva solo, sin el
resto de la carpeta.

Una fuente que falle no cancela la otra: se corren siempre las dos, y al
final se informa qué salió bien y qué no. Si ambas fallan, no se toca el
`insumos-af.js` que ya estuviera junto al HTML (uno viejo sigue siendo mejor
que ninguno; el informe además delata su fecha de extracción si quedara
desactualizado).

Uso:

    python3 automatizacion/actualizar_informe.py                 # el mes que ya cerró (agosto -> reporta julio)
    python3 automatizacion/actualizar_informe.py --periodo 2026-06
    python3 automatizacion/actualizar_informe.py --sin-copiar     # solo genera, no toca el HTML
    python3 automatizacion/actualizar_informe.py --abrir          # además, lo abre al terminar

Es el único script que hay que programar (cron / Programador de tareas) para
la ejecución del primero de cada mes — **sin** `--abrir` ahí: en un servidor
desatendido no hay quien vea el navegador, y no tiene sentido intentar abrir
uno. `--abrir` es para cuando alguien corre esto a mano y quiere ver el
resultado de una vez, sin buscar el archivo.
"""

import argparse
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
from insumos_af import MESES_ES, copiar_resguardo, incrustar_insumos, mes_cerrado  # noqa: E402
from sonda_glpi import cargar_env  # noqa: E402

SALIDA = AQUI / "salida"
HTML = AQUI.parent / "informe-accion-fiduciaria 1.html"


def nombre_informe(periodo):
    anio, mes = periodo.split("-")
    return f"Informe Accion Fiduciaria {MESES_ES[int(mes) - 1].capitalize()} {anio}.html"


def correr(script, periodo):
    titulo = f" {script} "
    print(f"\n{titulo.center(60, '=')}", flush=True)
    r = subprocess.run([sys.executable, str(AQUI / script), "--periodo", periodo])
    return r.returncode == 0


def main():
    # Los dos extractores leen .env dentro de su propio subproceso (vía
    # subprocess.run) — esa variable nunca vuelve a este proceso. RUTA_ONEDRIVE
    # se usa aquí mismo (copiar_resguardo del HTML), así que este proceso
    # también necesita cargar .env por su cuenta, no asumir que ya quedó en
    # el entorno.
    cargar_env()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--periodo", default=mes_cerrado(),
                   help="Mes a extraer, formato AAAA-MM (por defecto, el mes que ya cerró: "
                        "si se corre en agosto, julio)")
    p.add_argument("--sin-copiar", action="store_true",
                   help="Genera insumos-af.js en salida/ pero no lo copia junto al HTML")
    p.add_argument("--abrir", action="store_true",
                   help="Abre el HTML en el navegador por defecto al terminar (no usar en la tarea programada)")
    args = p.parse_args()

    ok_glpi = correr("extraer_glpi.py", args.periodo)
    ok_alertas = correr("extraer_alertas.py", args.periodo)

    print(f"\n{' Resumen '.center(60, '=')}", flush=True)
    print(f"  GLPI:     {'OK' if ok_glpi else 'FALLÓ — revisa el mensaje de arriba'}", flush=True)
    print(f"  AlertOps: {'OK' if ok_alertas else 'FALLÓ — revisa el mensaje de arriba'}", flush=True)

    js = SALIDA / "insumos-af.js"
    if not js.exists():
        print(f"\nNo hay {js} que copiar (fallaron ambas fuentes, o es la primera vez "
              "y ninguna llegó a escribir nada).", file=sys.stderr)
        return 1

    if args.sin_copiar:
        print(f"\nGenerado en {js}. No se copió (--sin-copiar).")
        return 0 if (ok_glpi or ok_alertas) else 1

    if not HTML.exists():
        print(f"\nAviso: no encontré el HTML en {HTML}; {js} quedó sin copiar.", file=sys.stderr)
        return 1

    destino = HTML.parent / "insumos-af.js"
    shutil.copy2(js, destino)
    print(f"\nCopiado junto al informe: {destino}")
    print("  Al abrir el HTML, las fuentes que hayan funcionado se cargan solas;")
    print("  la que haya fallado sigue siendo manual, sin bloquear a la otra.")

    # Copia a la carpeta del mes en OneDrive, junto a los CSV originales que
    # copiar_resguardo() ya deja ahí por cada extractor. No es una copia
    # simple del HTML: los datos van incrustados dentro del propio archivo,
    # no en un insumos-af.js vecino — así no hace falta que nada más viaje
    # junto a él, y no queda ningún archivo técnico suelto en esa carpeta.
    try:
        html_incrustado = incrustar_insumos(HTML, js)
    except (OSError, ValueError) as e:
        print(f"Aviso: no se pudo incrustar los insumos en el HTML ({e}); "
              "no se copió nada a RUTA_ONEDRIVE.", file=sys.stderr)
    else:
        temporal = SALIDA / "informe-incrustado.html"
        temporal.write_text(html_incrustado, encoding="utf-8")
        # proteger=False: el informe no es un registro de auditoría como los
        # CSV, es una vista de la extracción más reciente — siempre se
        # actualiza solo, sin necesitar FORZAR_ONEDRIVE en cada corrida.
        copia_html = copiar_resguardo(temporal, nombre_informe(args.periodo), args.periodo, proteger=False)
        if copia_html:
            print(f"Informe autocontenido copiado también a: {copia_html}")

    if args.abrir:
        try:
            abierto = webbrowser.open(HTML.resolve().as_uri())
            print(f"\n{'Abierto en el navegador.' if abierto else 'No se pudo abrir el navegador — ábrelo a mano.'}")
        except Exception as e:
            print(f"\nNo se pudo abrir el navegador ({e}); ábrelo a mano: {HTML}", file=sys.stderr)
    else:
        print(f"\nCorre con --abrir para que además lo abra. Manual: {HTML}")

    return 0 if (ok_glpi or ok_alertas) else 1


if __name__ == "__main__":
    sys.exit(main())
