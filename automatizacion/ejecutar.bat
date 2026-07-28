@echo off
setlocal
REM ---------------------------------------------------------------------------
REM  Lanzador de actualizar_informe.py (GLPI + AlertOps) para doble clic.
REM
REM  Existe porque en este equipo la politica de ejecucion de PowerShell esta
REM  en Restricted: un .ps1 no se puede lanzar desde la consola aunque el
REM  archivo sea correcto. El -ExecutionPolicy Bypass de aqui abajo afecta solo
REM  a este proceso; NO cambia ninguna configuracion del sistema ni requiere
REM  permisos de administrador.
REM
REM  Uso:
REM    ejecutar.bat                    ultimo mes cerrado, abre el informe
REM    ejecutar.bat -Periodo 2026-05
REM
REM  Tambien se puede hacer doble clic: corre igual y deja la ventana abierta
REM  para leer el resultado.
REM
REM  No pregunta nada en ningun momento.
REM ---------------------------------------------------------------------------

REM Si se lanzo con doble clic, cmd.exe lleva la ruta de este .bat en su propia
REM linea de comandos. Solo en ese caso conviene esperar antes de cerrar.
REM
REM Y solo si ademas no se pasaron argumentos: un "cmd /c ejecutar.bat -Periodo"
REM tambien coincide con esa deteccion, y ahi una pausa dejaria colgada para
REM siempre a una tarea programada. Un doble clic nunca lleva argumentos.
set "INTERACTIVO="
if "%~1"=="" echo %cmdcmdline% | find /i "%~nx0" >nul && set "INTERACTIVO=1"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ejecutar.ps1" %*
set CODIGO=%ERRORLEVEL%

if defined INTERACTIVO (
    echo.
    echo    Codigo de salida: %CODIGO%   ^(0 correcto ^| 1 fallaron GLPI y AlertOps ^| 2 configuracion^)
    echo.
    pause
)

exit /b %CODIGO%
