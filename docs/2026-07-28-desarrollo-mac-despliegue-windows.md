# Desarrollo en Mac, despliegue en el Windows corporativo

Encargo del 28/07/2026: Yordy trabaja y prueba toda la automatización desde su
Mac — es donde vive este repositorio y donde corren las pruebas de este mismo
día. Pero la tarea programada mensual (GLPI + AlertOps) no puede quedar
corriendo ahí: tiene que vivir en el equipo Windows corporativo, que es el que
va a estar encendido y disponible sin depender del portátil de una persona.

Este documento explica qué es compatible tal cual, qué había que adaptar, y
cómo llevar esto del Mac de desarrollo al Windows de producción.

## Por qué esto no era un problema desde el principio

Todo `automatizacion/*.py` se escribió en Python 3 estándar, sin ninguna
librería externa que instalar, y usando `pathlib.Path` para cualquier ruta de
archivo en vez de escribir `/` a mano. `pathlib` se adapta solo al separador
del sistema operativo donde corre (`/` en macOS y Linux, `\` en Windows), así
que ningún script `.py` de este repositorio tiene nada específico de macOS.
Es la misma razón por la que el plan de cierre siempre habló de tres
candidatos de servidor (el de Carlos Barrera, Azure Functions, un equipo de
oficina) sin que el sistema operativo de ninguno de ellos fuera un problema.

Lo único que sí estaba atado a macOS/Linux era el **envoltorio de la tarea
programada** (`tarea_mensual.sh`, escrito en Bash) — eso es lo que se resolvió
hoy.

## Qué es compatible ya, sin tocar nada

| Pieza | Corre en Windows tal cual |
|---|---|
| `sonda_glpi.py`, `extraer_glpi.py`, `sonda_alertops.py`, `extraer_alertas.py`, `insumos_af.py`, `actualizar_informe.py` | Sí — solo cambia invocarlos con `python` en vez de `python3` (ver más abajo) |
| `automatizacion/.env` / `.env.ejemplo` | Sí — mismo formato de texto, sin diferencias |
| `informe-accion-fiduciaria 1.html` | Sí — se abre igual en el navegador que esté instalado en ese equipo |
| `insumos-af.js` | Sí — es el mismo archivo generado, sin nada específico de sistema operativo |

## Lo único que había que adaptar: el envoltorio de la tarea programada

`tarea_mensual.sh` es Bash: no corre en Windows sin instalar WSL o Git Bash,
que son una complicación innecesaria cuando Windows ya trae PowerShell de
fábrica. Se creó su equivalente exacto:

**`automatizacion/tarea_mensual.ps1`** (PowerShell) — mismo comportamiento
línea por línea que la versión de Bash: entra a la raíz del proyecto, corre
`actualizar_informe.py`, deja el log con fecha en
`automatizacion/salida/tarea_mensual.log`, distingue «OK» de «FALLO (código
N)», y tiene el mismo bloque ya escrito (comentado) para conectar una alerta
de Teams con `Invoke-RestMethod` en cuanto exista el webhook — el equivalente
de PowerShell al `curl` de la versión de Bash.

Se probó igual de riguroso que la versión de Bash, en este mismo Mac (con
PowerShell 7 instalado vía Homebrew solo para esta verificación, ya que
PowerShell Core es multiplataforma):

- **Corrida exitosa:** código de salida `0`, log con «OK». Confirmado con
  las credenciales reales de GLPI y AlertOps.
- **Corrida forzada a fallar** (retirando `automatizacion/.env` a propósito):
  código de salida `1`, log con «FALLO (codigo 1)». El script distingue los
  dos casos correctamente, igual que `tarea_mensual.sh`.

Ambos wrappers (`.sh` y `.ps1`) quedan en el repositorio. Cuál se usa depende
solo de en qué sistema operativo esté el equipo donde se programe la tarea —
el `.sh` para Linux/macOS, el `.ps1` para Windows.

## Cómo llevar el código del Mac de desarrollo al Windows corporativo

Dos formas, de más a menos recomendable:

1. **Con git** (si el equipo Windows tiene acceso al repositorio remoto):
   clonarlo una vez y actualizarlo con `git pull` cada vez que haya cambios.
   Es la forma que evita copiar archivos a mano y olvidarse de alguno.
2. **Copia manual de la carpeta**: llevar `automatizacion/` completa más
   `informe-accion-fiduciaria 1.html` (manteniendo la misma posición relativa:
   el HTML un nivel arriba de `automatizacion/`) por USB, OneDrive o el medio
   que sea. Más simple para una sola vez, pero exige acordarse de repetirlo
   cada vez que el código cambie.

En ningún caso debe copiarse `automatizacion/.env` por un canal que quede
archivado sin cifrar (chat, correo, un OneDrive compartido) — las credenciales
se escriben directamente en el `.env` del equipo Windows, a mano, la primera
vez.

## Instalar y programar en el Windows corporativo, paso a paso

1. **Instalar Python 3**, si ese equipo no lo tiene. Desde
   [python.org](https://www.python.org/downloads/windows/), marcando la
   casilla «Add python.exe to PATH» durante la instalación — sin eso, ni
   `python` ni el Programador de tareas van a encontrar el intérprete.
2. **Llevar el código** (ver sección anterior).
3. **Crear `automatizacion\.env`** en ese equipo, con el mismo contenido que
   `automatizacion\.env.ejemplo`, completado con las credenciales (idealmente
   ya cuentas de servicio, no personales — ver el plan de cierre).
4. **Probar a mano primero**, en PowerShell:

   ```powershell
   cd C:\ruta\al\proyecto
   python automatizacion\actualizar_informe.py --abrir
   ```

   Debe imprimir el resumen de GLPI/AlertOps y abrir el informe en el
   navegador. Si `python` no se reconoce como comando, probar `py` en su
   lugar (`py automatizacion\actualizar_informe.py --abrir`) — depende de
   cómo haya quedado instalado Python en ese equipo específico.
5. **Configurar el Programador de tareas de Windows**:

   | Campo | Valor |
   |---|---|
   | Programa o script | `powershell.exe` |
   | Argumentos | `-ExecutionPolicy Bypass -File "C:\ruta\al\proyecto\automatizacion\tarea_mensual.ps1"` |
   | Iniciar en | `C:\ruta\al\proyecto` |
   | Desencadenador | Mensual, día 1, 1:00 a. m. |

   El `-ExecutionPolicy Bypass` es necesario porque Windows, por defecto,
   bloquea la ejecución de scripts `.ps1` que no estén firmados; ese flag lo
   permite solo para esta ejecución puntual, sin cambiar la política general
   del equipo.
6. **No usar `--abrir`** en la tarea programada — ni en la versión de Bash ni
   en la de PowerShell. Un servidor sin pantalla no tiene quién vea el
   navegador; `--abrir` es solo para cuando alguien lo corre a mano.

## Diferencias a tener en cuenta (y cuáles ya están resueltas)

- **`python` vs `python3`**: en Windows el comando suele ser `python` (a veces
  `py`); en macOS/Linux suele ser `python3`. Ya resuelto: `tarea_mensual.ps1`
  usa `python`, `tarea_mensual.sh` usa `python3` — cada wrapper ya trae el
  comando correcto para su sistema.
- **Separador de rutas (`/` vs `\`)**: resuelto en los scripts de Python
  gracias a `pathlib`. En los dos wrappers de la tarea programada se usó `/`
  deliberadamente en ambos (Windows acepta `/` igual que `\` en este
  contexto), así que ninguno de los dos tiene una ruta que solo funcione en
  un sistema operativo.
- **Saltos de línea (LF vs CRLF)**: `tarea_mensual.sh` usa LF (estándar Unix),
  `tarea_mensual.ps1` puede terminar con CRLF si se edita en un editor de
  Windows — PowerShell tolera ambos, así que no es necesario normalizarlo.
- **Apertura del navegador con `--abrir`**: el módulo `webbrowser` de Python
  es multiplataforma — abre el navegador predeterminado igual en Windows que
  en macOS. No necesitó ningún cambio.
- **Política de ejecución de PowerShell**: ver el punto del
  `-ExecutionPolicy Bypass` arriba — es lo único genuinamente distinto de
  programar una tarea en Windows frente a un `crontab` en Linux/macOS.

## Qué NO cambia entre los dos sistemas operativos

La lógica de los extractores, el formato de `insumos-af.js`, las
comprobaciones de hash y periodo, y el HTML del informe son exactamente los
mismos archivos, sin ninguna rama de código distinta según el sistema
operativo. Lo único que cambia es *quién* invoca a `actualizar_informe.py` —
`cron` con `tarea_mensual.sh` en un mundo Unix, el Programador de tareas con
`tarea_mensual.ps1` en Windows — y el propio `actualizar_informe.py` ni se
entera de cuál de los dos lo llamó.
