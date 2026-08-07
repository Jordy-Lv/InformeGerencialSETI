@echo off
setlocal
REM ---------------------------------------------------------------------------
REM  Lanzador de instalar_tarea_programada.ps1 para doble clic.
REM
REM  Igual que ejecutar.bat: el -ExecutionPolicy Bypass de aqui abajo afecta
REM  solo a este proceso, no cambia ninguna configuracion del sistema ni
REM  requiere permisos de administrador.
REM
REM  Correrlo UNA SOLA VEZ, en el equipo donde va a quedar la tarea programada.
REM ---------------------------------------------------------------------------

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_tarea_programada.ps1"
set CODIGO=%ERRORLEVEL%

echo.
echo    Codigo de salida: %CODIGO%   (0 = tarea registrada correctamente)
echo.
pause

exit /b %CODIGO%
