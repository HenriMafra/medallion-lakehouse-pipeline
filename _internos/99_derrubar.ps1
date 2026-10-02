# Derruba os containers. Os dados (HDFS/MySQL) ficam guardados nos volumes.
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Parando e removendo os containers (volumes preservados)..." -ForegroundColor Cyan
docker compose -f $compose down
Write-Host "Pronto. (Para zerar TAMBEM os dados: docker compose -f `"$compose`" down -v)" -ForegroundColor Yellow
