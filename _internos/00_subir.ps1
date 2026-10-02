# PASSO 0 - Sobe o ambiente (HDFS + MySQL + Spark) e espera ficar pronto.
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> Construindo a imagem do Spark (so demora na 1a vez)..." -ForegroundColor Cyan
docker compose -f $compose build spark

Write-Host "==> Subindo os 4 containers..." -ForegroundColor Cyan
docker compose -f $compose up -d

Write-Host "==> Aguardando o HDFS em http://localhost:9870 ..." -ForegroundColor Cyan
$ok = $false
for ($i = 0; $i -lt 40; $i++) {
    try { Invoke-WebRequest -Uri "http://localhost:9870" -UseBasicParsing -TimeoutSec 3 | Out-Null; $ok = $true; break }
    catch { Start-Sleep -Seconds 3 }
}
if ($ok) { Write-Host "    HDFS pronto!" -ForegroundColor Green }
else { Write-Host "    HDFS demorou - veja 'docker compose logs namenode'" -ForegroundColor Yellow }

# IMPORTANTE: esperar o MySQL aceitar consultas de verdade (a tabela nyc.taxi_zones
# precisa existir). Sem isto, o passo 2 carrega as zonas antes do banco terminar
# de inicializar e a carga falha silenciosamente (0 zonas -> join vazio na Ouro).
Write-Host "==> Aguardando o MySQL aceitar consultas..." -ForegroundColor Cyan
$okdb = $false
for ($i = 0; $i -lt 50; $i++) {
    try { docker compose -f $compose exec -T mysql mysql -uroot -prootpw -e "SELECT 1 FROM nyc.taxi_zones LIMIT 1;" 1>$null 2>$null } catch {}
    if ($LASTEXITCODE -eq 0) { $okdb = $true; break }
    Start-Sleep -Seconds 3
}
if ($okdb) { Write-Host "    MySQL pronto!" -ForegroundColor Green }
else { Write-Host "    MySQL demorou - veja 'docker compose logs mysql'" -ForegroundColor Yellow }

Write-Host "==> Status dos containers:" -ForegroundColor Cyan
docker compose -f $compose ps
Write-Host ""
Write-Host "Interfaces: HDFS http://localhost:9870 | MySQL localhost:3307 (root/rootpw)" -ForegroundColor Green
