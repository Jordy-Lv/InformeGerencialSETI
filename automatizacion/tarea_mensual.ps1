# Tarea programada mensual — corre GLPI + AlertOps y deja el informe listo.
# Equivalente en Windows de tarea_mensual.sh (mismo comportamiento; ver
# docs/2026-07-28-desarrollo-mac-despliegue-windows.md para el porqué de
# los dos scripts y cómo instalar este en el Programador de tareas).
#
# Uso en el Programador de tareas de Windows (el primero de cada mes, 1:00 a. m.):
#   Programa/script:   powershell.exe
#   Argumentos:        -ExecutionPolicy Bypass -File "C:\ruta\al\proyecto\automatizacion\tarea_mensual.ps1"
#   Iniciar en:         C:\ruta\al\proyecto
#
# No pasa --abrir: en un servidor sin pantalla no hay quien vea el navegador.
# No necesita --periodo: actualizar_informe.py calcula solo el mes que cerró.

$ErrorActionPreference = "Stop"

$Aqui = $PSScriptRoot                        # ...\automatizacion
$Raiz = Split-Path -Parent $Aqui             # raíz del proyecto
Set-Location $Raiz

$directorioSalida = Join-Path $Aqui "salida"
New-Item -ItemType Directory -Force -Path $directorioSalida | Out-Null
$log = Join-Path $directorioSalida "tarea_mensual.log"
$fecha = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Add-Content -Path $log -Value "=== $fecha ==="

# python.exe (o py.exe, según cómo esté instalado en este equipo — ver la
# nota en el .md si este comando no se reconoce) hace el trabajo real; su
# salida (normal y de error) se agrega al mismo log. La barra "/" funciona
# igual que "\" para Windows en este contexto, y así el script es el mismo
# en cualquier sistema operativo donde corra PowerShell.
& python automatizacion/actualizar_informe.py *>> $log
$codigo = $LASTEXITCODE

if ($codigo -ne 0) {
    Add-Content -Path $log -Value "FALLO (codigo $codigo) - $fecha"
    # Alerta ante fallo: descomentar cuando exista el webhook de Teams y quede
    # definida la variable de entorno TEAMS_WEBHOOK_URL en este equipo.
    # $cuerpo = @{ text = "Automatización GLPI/AlertOps falló el $fecha (código $codigo). Revisar $log en el servidor." } | ConvertTo-Json
    # Invoke-RestMethod -Uri $env:TEAMS_WEBHOOK_URL -Method Post -Body $cuerpo -ContentType "application/json"
} else {
    Add-Content -Path $log -Value "OK - $fecha"
}

exit $codigo
