-- ===========================================================================
--  Schema da FONTE RELACIONAL (MySQL / OLTP) do pipeline.
--
--  taxi_zones e a DIMENSAO geografica: cada LocationID (1..265) corresponde
--  a um bairro/zona de Nova York. As corridas (fatos, em CSV) referenciam
--  esses IDs em PULocationID (origem) e DOLocationID (destino).
--
--  Este arquivo roda automaticamente no PRIMEIRO boot do container MySQL
--  (pasta /docker-entrypoint-initdb.d). Ele apenas CRIA a estrutura vazia;
--  os dados sao carregados depois, como um passo VISIVEL da apresentacao,
--  a partir do arquivo oficial taxi_zone_lookup.csv da NYC TLC.
-- ===========================================================================

CREATE DATABASE IF NOT EXISTS nyc;
USE nyc;

CREATE TABLE IF NOT EXISTS taxi_zones (
    LocationID    INT PRIMARY KEY,      -- id da zona (chave usada pelas corridas)
    Borough       VARCHAR(64),          -- distrito (Manhattan, Brooklyn, ...)
    Zone          VARCHAR(128),         -- nome do bairro/zona
    service_zone  VARCHAR(64)           -- categoria tarifaria da zona
);

-- O Spark se conecta como usuario 'spark' (criado pelas variaveis do compose).
-- Garantimos que ele enxerga a base 'nyc'.
GRANT ALL PRIVILEGES ON nyc.* TO 'spark'@'%';
FLUSH PRIVILEGES;
