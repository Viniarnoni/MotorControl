param(
    [string]$AppName = "MotorControl",
    [string]$IconPath = "icone.ico"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$fletExe = Join-Path $projectRoot ".venv\Scripts\flet.exe"
if (-not (Test-Path $fletExe)) {
    throw "Flet não encontrado em .venv\Scripts\flet.exe"
}

$packArgs = @(
    "pack"
    "main.py"
    "--name", $AppName
    "--add-data", "src:src"
    "--add-data", "assets:assets"
    "-y"
)

if (Test-Path (Join-Path $projectRoot $IconPath)) {
    $packArgs += @("--icon", $IconPath)
}

& $fletExe @packArgs

if ($LASTEXITCODE -ne 0) {
    throw "Falha no empacotamento do executável."
}

$distDir = Join-Path $projectRoot "dist"
$databasePath = Join-Path $projectRoot "motorcontrol.db"
$exeDir = $distDir

if (Test-Path (Join-Path $distDir $AppName)) {
    $exeDir = Join-Path $distDir $AppName
}

if (Test-Path $databasePath) {
    Copy-Item $databasePath -Destination (Join-Path $exeDir "motorcontrol.db") -Force
}

$assetsSrc = Join-Path $projectRoot "assets"
$assetsDst = Join-Path $exeDir "assets"
if (Test-Path $assetsSrc) {
    New-Item -ItemType Directory -Force -Path $assetsDst | Out-Null
    Copy-Item (Join-Path $assetsSrc "logo.png") -Destination (Join-Path $assetsDst "logo.png") -Force -ErrorAction SilentlyContinue
}

Write-Host "Build concluído em: $exeDir"
