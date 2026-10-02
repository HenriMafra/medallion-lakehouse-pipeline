# PASSO 7 (bonus) - Time travel do Delta: historico de versoes + leitura da v0.
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Historico de versoes (DESCRIBE HISTORY) + leitura da versao 0..." -ForegroundColor Cyan
docker compose -f $compose exec -T spark spark-submit /app/jobs/historico.py
