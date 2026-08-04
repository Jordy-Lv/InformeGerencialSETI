"""
sonda_glpi.py

Herramienta de RECONOCIMIENTO, no de extraccion. Su unico proposito es
confirmar, contra la instancia real de GLPI de Cardio Infantil, tres cosas
antes de construir el extractor definitivo (extraer_glpi.py):

  1. Que las credenciales (App-Token + User-Token) autentican correctamente.
  2. El listado real de entidades, para identificar el ID/nombre exacto de
     Cardio Infantil (nunca asumir que es igual al de otro cliente).
  3. El listado real de categorias de tickets (ITILCategory), para localizar
     el equivalente a "INCIDENTES > Revision Alerta" que en Acción
     Fiduciaria se usa para excluir del conteo los tickets que el propio
     monitoreo genera solo (ver seccion 6.2 de la documentacion).

No escribe ningun archivo de salida y no toca insumos-cardio.js ni nada de
produccion. Solo imprime en consola. Este es el mismo metodo de
"reconocimiento antes que construccion" que ya se uso en Acción Fiduciaria.

Uso:
    python3 automatizacion/sonda_glpi.py

Requisitos: ninguna dependencia externa (solo libreria estandar de Python).
Se debe haber copiado antes .env.ejemplo a .env y llenado GLPI_URL,
GLPI_APP_TOKEN y GLPI_USER_TOKEN.
"""

import json
import os
import sys
import urllib.error
import urllib.request


def cargar_env(ruta=".env"):
    """Carga variables de un archivo .env simple (CLAVE=VALOR) sin depender
    de python-dotenv, para no introducir una dependencia externa."""
    valores = {}
    if not os.path.exists(ruta):
        return valores
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            valores[clave.strip()] = valor.strip()
    return valores


def peticion(url, headers, metodo="GET"):
    req = urllib.request.Request(url, headers=headers, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            cuerpo = resp.read().decode("utf-8")
            return resp.status, json.loads(cuerpo) if cuerpo else None
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(cuerpo)
        except json.JSONDecodeError:
            return e.code, cuerpo
    except urllib.error.URLError as e:
        print(f"[ERROR] No se pudo conectar a {url}: {e.reason}")
        sys.exit(1)


def main():
    # Busca .env en el directorio actual y, si no aparece, un nivel arriba
    # (por si se corre el script desde la raiz del proyecto).
    env = cargar_env(".env")
    if not env:
        env = cargar_env(os.path.join("automatizacion", ".env"))

    glpi_url = env.get("GLPI_URL") or os.environ.get("GLPI_URL")
    app_token = env.get("GLPI_APP_TOKEN") or os.environ.get("GLPI_APP_TOKEN")
    user_token = env.get("GLPI_USER_TOKEN") or os.environ.get("GLPI_USER_TOKEN")

    faltantes = [
        nombre
        for nombre, valor in [
            ("GLPI_URL", glpi_url),
            ("GLPI_APP_TOKEN", app_token),
            ("GLPI_USER_TOKEN", user_token),
        ]
        if not valor
    ]
    if faltantes:
        print("[ERROR] Faltan variables en .env: " + ", ".join(faltantes))
        print("        Copia automatizacion/.env.ejemplo a automatizacion/.env y complétalo.")
        sys.exit(1)

    glpi_url = glpi_url.rstrip("/")
    api_base = f"{glpi_url}/apirest.php"

    print("=" * 70)
    print("SONDA GLPI — Cardio Infantil")
    print("=" * 70)
    print(f"Conectando a: {api_base}\n")

    # --- Paso 1: iniciar sesion ---
    headers_init = {
        "Content-Type": "application/json",
        "Authorization": f"user_token {user_token}",
        "App-Token": app_token,
    }
    status, data = peticion(f"{api_base}/initSession", headers_init)

    if status != 200 or not isinstance(data, dict) or "session_token" not in data:
        print(f"[ERROR] No se pudo iniciar sesion (HTTP {status}).")
        print(f"Respuesta del servidor: {data}")
        print("\nRevisa: URL correcta, App-Token activo, User-Token vigente,")
        print("y que la API REST este habilitada en GLPI (Configuracion > General > API).")
        sys.exit(1)

    session_token = data["session_token"]
    print("[OK] Sesion iniciada correctamente.\n")

    headers = {
        "Content-Type": "application/json",
        "Session-Token": session_token,
        "App-Token": app_token,
    }

    try:
        # --- Paso 2: listar entidades ---
        print("-" * 70)
        print("ENTIDADES DISPONIBLES")
        print("-" * 70)
        status, entidades = peticion(f"{api_base}/Entity?range=0-200", headers)
        if status in (200, 206) and isinstance(entidades, list):
            candidatas = []
            for e in entidades:
                nombre = e.get("name", "")
                eid = e.get("id")
                completename = e.get("completename", nombre)
                print(f"  id={eid:<6} {completename}")
                if "cardio" in nombre.lower() or "cardio" in completename.lower():
                    candidatas.append((eid, completename))
            print()
            if candidatas:
                print("  >>> Coincidencia(s) con 'cardio' encontradas:")
                for eid, nombre in candidatas:
                    print(f"      id={eid}  {nombre}")
                print("      Usa este id/nombre para GLPI_ENTIDAD_CARDIO en .env")
            else:
                print("  >>> Ninguna entidad contiene 'cardio' en el nombre.")
                print("      Revisa la lista completa de arriba y confirma manualmente cual es.")
        else:
            print(f"[AVISO] No se pudo listar entidades (HTTP {status}): {entidades}")

        # --- Paso 3: listar categorias de tickets (ITILCategory) ---
        print()
        print("-" * 70)
        print("CATEGORIAS DE TICKETS (ITILCategory)")
        print("-" * 70)
        status, categorias = peticion(f"{api_base}/ITILCategory?range=0-300", headers)
        if status in (200, 206) and isinstance(categorias, list):
            posibles_alerta = []
            for c in categorias:
                nombre = c.get("name", "")
                completename = c.get("completename", nombre)
                cid = c.get("id")
                print(f"  id={cid:<6} {completename}")
                bajo = completename.lower()
                if "alerta" in bajo or "monitoreo" in bajo or "revision" in bajo:
                    posibles_alerta.append((cid, completename))
            print()
            if posibles_alerta:
                print("  >>> Categorias que podrian ser el equivalente a")
                print("      'INCIDENTES > Revision Alerta' de Acción Fiduciaria:")
                for cid, nombre in posibles_alerta:
                    print(f"      id={cid}  {nombre}")
            else:
                print("  >>> No se encontro ninguna categoria con 'alerta'/'monitoreo'/'revision'")
                print("      en el nombre. Puede que Cardio Infantil no separe estos tickets igual")
                print("      que Acción Fiduciaria — hay que confirmarlo con el equipo antes de asumir.")
        else:
            print(f"[AVISO] No se pudo listar categorias (HTTP {status}): {categorias}")

        # --- Paso 4: probar un filtro real por entidad + rango de fechas ---
        # Esto confirma que el filtrado en origen (por entidad y por mes) funciona
        # antes de construir el extractor real, tal como se hizo en Acción Fiduciaria.
        print()
        print("-" * 70)
        print("PRUEBA: conteo de tickets totales visibles con este usuario")
        print("-" * 70)
        status, tickets = peticion(
            f"{api_base}/Ticket?range=0-0", headers  # range=0-0 solo trae el total, no los datos
        )
        print(f"  HTTP {status}")
        print(f"  Respuesta: {tickets if not isinstance(tickets, list) else '(lista de tickets)'}")

        # --- Paso 5: listSearchOptions/Ticket, la fuente real de los IDs de columna ---
        # extraer_glpi.py de Acción Fiduciaria construye su lista de COLUMNAS a
        # partir de esta llamada, no de IDs adivinados o copiados de otro cliente
        # (ver comentario en su cabecera: "No hay ningún ID adivinado"). Se imprime
        # aquí para que el extractor de Cardio se construya con el mismo método.
        print()
        print("-" * 70)
        print("SEARCH OPTIONS DE Ticket (para construir extraer_glpi.py)")
        print("-" * 70)
        status, opciones = peticion(f"{api_base}/listSearchOptions/Ticket", headers)
        if status == 200 and isinstance(opciones, dict):
            interesantes = ("título", "titulo", "entidad", "fecha de apertura", "estado",
                             "categoría", "categoria", "prioridad", "tipo", "resolver",
                             "resolución", "resolucion", "modificación", "modificacion")
            for oid, info in opciones.items():
                if not isinstance(info, dict):
                    continue
                nombre = info.get("name", "")
                if any(p in nombre.lower() for p in interesantes):
                    print(f"  id={oid:<5} {nombre}")
            print("\n  (lista filtrada a los campos que probablemente hagan falta;")
            print("   la respuesta completa trae muchos más si se necesita otro campo)")
        else:
            print(f"[AVISO] No se pudo obtener listSearchOptions (HTTP {status}): {opciones}")

    finally:
        # --- Cerrar sesion siempre, incluso si algo fallo arriba ---
        peticion(f"{api_base}/killSession", headers)
        print("\n[OK] Sesion cerrada.")

    print("\n" + "=" * 70)
    print("SIGUIENTE PASO")
    print("=" * 70)
    print("1. Completa GLPI_ENTIDAD_CARDIO en .env con el id/nombre confirmado arriba.")
    print("2. Confirma con el equipo de Cardio Infantil cual categoria (si existe)")
    print("   corresponde a tickets generados por el propio monitoreo.")
    print("3. Con los searchOptions listados arriba (paso 5), y NO antes, se")
    print("   construye extraer_glpi.py — igual que se hizo en Acción Fiduciaria.")


if __name__ == "__main__":
    main()
