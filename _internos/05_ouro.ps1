# PASSO 5 - Camada OURO (agregacoes de negocio: join fato x dimensao).
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Rodando o job OURO..." -ForegroundColor Cyan
docker compose -f $compose exec -T spark spark-submit /app/jobs/gold.py

Write-Host "==> Camada Ouro no HDFS:" -ForegroundColor Cyan
docker compose -f $compose exec -T namenode hdfs dfs -ls -R /lake/gold
