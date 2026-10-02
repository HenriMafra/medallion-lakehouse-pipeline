# PASSO 1 - Prepara os dados REAIS da NYC TLC (roda dentro do container spark).
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Baixando/convertendo dados reais (na 1a vez baixa ~50 MB)..." -ForegroundColor Cyan
docker compose -f $compose exec -T spark python /data/preparar_dados.py

Write-Host "==> Arquivos gerados em dados/brutos:" -ForegroundColor Cyan
Get-ChildItem "$proj\dados\brutos" | Select-Object Name, @{N='MB';E={[math]::Round($_.Length/1MB,2)}}
