<#
.SYNOPSIS
    Registra en el Programador de tareas de Windows la corrida mensual de
    tarea_mensual.ps1: el día 1 de cada mes, a las 8:00 a. m.

.DESCRIPTION
    Correrlo una sola vez, en el equipo donde va a vivir la automatización
    desatendida (ver docs/2026-07-28-desarrollo-mac-despliegue-windows.md).

    Pregunta si la tarea debe correr aunque nadie tenga sesión iniciada en
    Windows ("headless"):

      - Respuesta No (Enter, por defecto): se registra con -LogonType
        Interactive — "ejecutar solo si el usuario tiene sesión iniciada".
        No pide ni guarda contraseña. Es el modo recomendado mientras
        RUTA_ONEDRIVE/RUTA_INDISPONIBILIDADES dependan del cliente de
        OneDrive de este usuario (normalmente no sincroniza sin sesión
        activa) — ver «Lo que falta» en automatizacion/README.md.

      - Respuesta Sí: pide la contraseña de la cuenta (Get-Credential, cuadro
        nativo de Windows; esa contraseña nunca se muestra en pantalla ni
        queda en ningún archivo de este proyecto — el Programador de tareas
        la guarda cifrada, como con cualquier tarea "Ejecutar tanto si el
        usuario inició sesión como si no"). La extracción de GLPI/AlertOps
        funciona igual sin sesión iniciada; lo que puede quedar pendiente
        hasta el siguiente inicio de sesión es la copia a RUTA_ONEDRIVE /
        RUTA_INDISPONIBILIDADES, si OneDrive en este equipo no sincroniza sin
        una sesión activa.

    No hace falta ser administrador para el modo normal; el modo headless si
    puede pedir permisos elevados según la política del equipo.

.EXAMPLE
    .\automatizacion\instalar_tarea_programada.ps1
#>

$ErrorActionPreference = 'Stop'

$NOMBRE_TAREA = 'Automatizacion Informes Accion Fiduciaria'
$script = Join-Path $PSScriptRoot 'tarea_mensual.ps1'

if (-not (Test-Path $script)) {
    Write-Error "No encuentro $script junto a este instalador."
    exit 1
}

$accion = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-ExecutionPolicy Bypass -File `"$script`""

$disparador = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At (Get-Date -Hour 8 -Minute 0 -Second 0)

$config = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries

$respuesta = Read-Host "¿Correr tambien si nadie ha iniciado sesion en Windows a esa hora? (S/N, Enter = No)"

if ($respuesta -match '^[sS]') {
    Write-Output ""
    Write-Output "Modo headless: la contraseña se pide abajo y queda cifrada en el Programador"
    Write-Output "de tareas de Windows — no se guarda en ningun archivo de este proyecto."
    $cred = Get-Credential -UserName "$env:USERDOMAIN\$env:USERNAME" -Message "Cuenta con la que correra la tarea sin sesion iniciada"

    Register-ScheduledTask -TaskName $NOMBRE_TAREA -Action $accion -Trigger $disparador `
        -Settings $config -User $cred.UserName -Password $cred.GetNetworkCredential().Password `
        -RunLevel Highest -Force | Out-Null

    Write-Output ""
    Write-Output "Tarea '$NOMBRE_TAREA' registrada en modo headless: corre el dia 1 de cada mes a las 8:00 a. m.,"
    Write-Output "con sesion iniciada o sin ella."
    Write-Output "Aviso: si OneDrive en este equipo no sincroniza sin sesion activa, la copia a"
    Write-Output "RUTA_ONEDRIVE/RUTA_INDISPONIBILIDADES puede quedar pendiente hasta el siguiente inicio de sesion."
} else {
    $principal = New-ScheduledTaskPrincipal -UserId $env:UserName -LogonType Interactive -RunLevel Limited

    Register-ScheduledTask -TaskName $NOMBRE_TAREA -Action $accion -Trigger $disparador `
        -Principal $principal -Settings $config -Force | Out-Null

    Write-Output ""
    Write-Output "Tarea '$NOMBRE_TAREA' registrada: corre el dia 1 de cada mes a las 8:00 a. m.,"
    Write-Output "solo si hay una sesion de Windows iniciada."
}

Write-Output ""
Write-Output "Verificar en el Programador de tareas (taskschd.msc), Biblioteca del Programador de tareas."
Write-Output "Log de cada corrida: automatizacion\salida\tarea_mensual.log"
