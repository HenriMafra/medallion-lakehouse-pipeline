"""
============================================================================
 CAMADA BRONZE  -  Ingestao CRUA
============================================================================
 O QUE FAZ: traz os dados das DUAS fontes para dentro do Delta Lake (no HDFS)
            exatamente como vieram, sem limpar nem filtrar nada. Apenas
            adiciona colunas de LINHAGEM (de onde veio, quando foi ingerido).

 POR QUE:   o Bronze e a "fotografia" do dado bruto. Se algo der errado nas
            camadas seguintes, sempre podemos reprocessar a partir daqui sem
            ter que baixar tudo de novo da fonte.

 FONTES:    (1) CSV de corridas, ja colocado no HDFS em /raw/yellow_tripdata.csv
            (2) Tabela taxi_zones do MySQL, lida via JDBC.

 SAIDA:     /lake/bronze/trips  e  /lake/bronze/zones  (tabelas Delta no HDFS)
============================================================================
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # acha utils_spark.py

from pyspark.sql import functions as F
from utils_spark import build_spark, PATHS, JDBC_URL, JDBC_PROPS, secao

spark = build_spark("bronze-ingestao")

# ----------------------------------------------------------------------------
# 1) FONTE CSV (corridas)
#    Lemos com cabecalho, mas SEM inferir tipos: no Bronze tudo entra como
#    texto, para preservar 100% a fidelidade do dado cru.
# ----------------------------------------------------------------------------
secao("BRONZE 1/2  -  Corridas (origem: CSV no HDFS)")

trips_raw = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")     # Bronze nao adivinha tipo
    .csv(PATHS["raw_trips"])
)

trips_bronze = (
    trips_raw
    .withColumn("_fonte", F.lit("csv:yellow_tripdata"))
    .withColumn("_ingerido_em", F.current_timestamp())
)

(trips_bronze.write
    .format("delta")
    .mode("overwrite")
    .save(PATHS["bronze_trips"]))

print(f"-> Bronze TRIPS gravado em Delta: {trips_bronze.count():,} linhas")
print("   colunas:", ", ".join(trips_bronze.columns))

# ----------------------------------------------------------------------------
# 2) FONTE MySQL (zonas) - dimensao lida via JDBC
# ----------------------------------------------------------------------------
secao("BRONZE 2/2  -  Zonas (origem: MySQL via JDBC)")

zones_raw = spark.read.jdbc(JDBC_URL, "taxi_zones", properties=JDBC_PROPS)

zones_bronze = (
    zones_raw
    .withColumn("_fonte", F.lit("mysql:taxi_zones"))
    .withColumn("_ingerido_em", F.current_timestamp())
)

(zones_bronze.write
    .format("delta")
    .mode("overwrite")
    .save(PATHS["bronze_zones"]))

print(f"-> Bronze ZONES gravado em Delta: {zones_bronze.count():,} linhas")

secao("BRONZE concluida")
spark.stop()
