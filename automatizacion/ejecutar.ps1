<#
.SYNOPSIS
    Lanza actualizar_informe.py (GLPI + AlertOps) en Windows con doble clic.

.DESCRIPTION
    Envoltorio fino: toda la lógica vive en actualizar_informe.py. Este script
    solo resuelve el intérprete de Python en este equipo — en Windows
    «python3» es el stub de la Microsoft Store y falla con un mensaje
    engañoso sobre instalarlo — y pasa los argumentos tal cual.

.PARAMETER Periodo
    Mes a extraer, AAAA-MM. Por defecto, el último mes cerrado.

.PARAMETER SinAbrir
    No abre el informe en el navegador al terminar. Para correr sin
    supervisión (no la usa la tarea programada: esa usa tarea_mensual.ps1).

.EXAMPLE
    .\automatizacion\ejecutar.ps1

.EXAMPLE
    .\automatizacion\ejecutar.ps1 -Periodo 2026-06

.NOTES
    TEMPORAL (demo): si no se pasa -Periodo, pregunta el mes por número
    antes de correr — ver el bloque marcado más abajo. Quitar ese bloque
    devuelve el comportamiento normal: nunca preguntar nada.

    Códigos de salida, heredados de actualizar_informe.py:
      0  correcto (al menos una fuente generó insumo)
      1  fallaron las dos fuentes, o no hay HTML donde copiar el insumo
      2  falta Python o falta automatizacion\.env
#>
[CmdletBinding()]
param(
    [ValidatePattern('^\d{4}-\d{2}$')]
    [string]$Periodo,
    [switch]$SinAbrir
)

$ErrorActionPreference = 'Stop'

$script = Join-Path $PSScriptRoot 'actualizar_informe.py'
$env:PYTHONUTF8 = '1'   # hoy la consola ya es UTF-8, pero por si acaso

# --- Intérprete -----------------------------------------------------------
# Se prueba «py -3» primero: es el lanzador oficial de Windows y no lo
# secuestra el alias de la Microsoft Store.
$exe = $null; $pre = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
    $exe = 'py'; $pre = @('-3')
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $exe = 'python'
}
if (-not $exe) {
    Write-Error "No se encontró Python. Instálalo desde python.org (3.8 o superior) y vuelve a intentarlo."
    exit 2
}

if (-not (Test-Path (Join-Path $PSScriptRoot '.env'))) {
    Write-Error "Falta automatizacion\.env. Copia .env.ejemplo y completa las credenciales."
    exit 2
}

# --- TEMPORAL: elegir el mes por número, para la demo — quitar después ----
# Solo pregunta si no se pasó -Periodo por línea de comandos. Enter en
# blanco conserva el comportamiento normal (mes cerrado automático).
if (-not $Periodo) {
    $anio = (Get-Date).Year
    $numero = Read-Host "¿Qué mes de $anio quieres consultar? (1-12, Enter = mes cerrado automático)"
    if ($numero) {
        if ($numero -notmatch '^\d{1,2}$' -or [int]$numero -lt 1 -or [int]$numero -gt 12) {
            Write-Error "«$numero» no es un mes válido (debe ser 1-12)."
            exit 2
        }
        $Periodo = "{0}-{1:D2}" -f $anio, [int]$numero
        Write-Output "Consultando $Periodo…"
    }
}

# --- Argumentos -------------------------------------------------------------
$argumentos = @($script)
if ($Periodo)       { $argumentos += @('--periodo', $Periodo) }
if (-not $SinAbrir) { $argumentos += '--abrir' }

& $exe @pre @argumentos
exit $LASTEXITCODE
