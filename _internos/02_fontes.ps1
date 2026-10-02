# PASSO 2 - Carrega as DUAS fontes: zonas no MySQL e CSV das corridas no HDFS.
$ErrorActionPreference = "Stop"
$proj = Split-Path $PSScriptRoot -Parent
$compose = Join-Path $proj "ambiente\docker-compose.yml"

Write-Host "==> (1/2) Populando o MySQL com as zonas (via INSERTs)..." -ForegroundColor Cyan
docker compose -f $compose exec -T mysql sh -c "mysql -uroot -prootpw < /data/brutos/zones_insert.sql"
docker compose -f $compose exec -T mysql mysql -uroot -prootpw -e "SELECT COUNT(*) AS zonas_no_mysql FROM nyc.taxi_zones;"

Write-Host "==> (2/2) Colocando o CSV cru DENTRO do HDFS..." -ForegroundColor Cyan
docker compose -f $compose exec -T namenode hdfs dfs -mkdir -p /raw
docker compose -f $compose exec -T namenode hdfs dfs -put -f /data/brutos/yellow_tripdata.csv /raw/yellow_tripdata.csv
docker compose -f $compose exec -T namenode hdfs dfs -ls -h /raw
