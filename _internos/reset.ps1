# Zera o ambiente para uma GRAVACAO limpa: apaga os containers E os volumes
# (HDFS + MySQL), para que cada camada (Bronze/Prata/Ouro) NASCA do zero na
# frente da camera. Os arquivos de dados (dados/brutos) NAO sao apagados.
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Zerando o ambiente (apaga containers e os dados do HDFS/MySQL)..." -ForegroundColor Cyan
docker compose -f $compose down -v

Write-Host ""
Write-Host "Ambiente ZERADO. HDFS e MySQL voltaram a ficar vazios." -ForegroundColor Green
Write-Host "Os arquivos em dados/brutos foram mantidos (passo 2 sera rapido)." -ForegroundColor Green
Write-Host ""
Write-Host "Agora grave rodando, NA ORDEM, a pasta passo-a-passo: 1 -> 2 -> ... -> 7" -ForegroundColor Yellow
