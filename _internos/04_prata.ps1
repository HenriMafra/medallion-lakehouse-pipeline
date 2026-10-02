# PASSO 4 - Camada PRATA (limpeza, tipagem e filtros de qualidade).
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Rodando o job PRATA..." -ForegroundColor Cyan
docker compose -f $compose exec -T spark spark-submit /app/jobs/silver.py

Write-Host "==> Camada Prata no HDFS:" -ForegroundColor Cyan
docker compose -f $compose exec -T namenode hdfs dfs -ls -R /lake/silver
