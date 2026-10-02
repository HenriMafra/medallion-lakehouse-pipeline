# Roda TODO o pipeline em sequencia (util para um ensaio rapido).
$ErrorActionPreference = "Stop"

& "$PSScriptRoot\00_subir.ps1"
& "$PSScriptRoot\01_dados.ps1"
& "$PSScriptRoot\02_fontes.ps1"
& "$PSScriptRoot\03_bronze.ps1"
& "$PSScriptRoot\04_prata.ps1"
& "$PSScriptRoot\05_ouro.ps1"
& "$PSScriptRoot\06_inspecionar.ps1"

Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "  PIPELINE COMPLETO! Bronze -> Prata -> Ouro OK." -ForegroundColor Green
Write-Host "  HDFS:  http://localhost:9870" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
