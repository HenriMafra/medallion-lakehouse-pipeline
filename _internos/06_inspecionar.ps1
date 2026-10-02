# PASSO 6 - Inspeciona o resultado: estrutura no HDFS + consulta da Ouro.
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Estrutura completa do Data Lakehouse no HDFS:" -ForegroundColor Cyan
docker compose -f $compose exec -T namenode hdfs dfs -ls -R /lake

Write-Host "==> Consultando as tabelas OURO (como um analista faria):" -ForegroundColor Cyan
docker compose -f $compose exec -T spark spark-submit /app/jobs/consultar.py
