# PASSO 3 - Camada BRONZE (ingestao crua: CSV + MySQL -> Delta no HDFS).
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Rodando o job BRONZE..." -ForegroundColor Cyan
docker compose -f $compose exec -T spark spark-submit /app/jobs/bronze.py

Write-Host "==> Camada Bronze no HDFS:" -ForegroundColor Cyan
docker compose -f $compose exec -T namenode hdfs dfs -ls -R /lake/bronze
