"""
============================================================================
 CAMADA PRATA (Silver)  -  Dados LIMPOS, TIPADOS e FILTRADOS
============================================================================
 O QUE FAZ: le o Bronze (tudo texto), converte cada coluna para o tipo
            correto, cria colunas derivadas (ex.: duracao da corrida) e
            REMOVE linhas invalidas com regras de qualidade.

 POR QUE:   o negocio nao pode confiar em dado cru. A Prata entrega um
            conjunto coerente, sem nulos criticos, sem valores impossiveis
            (tarifa negativa, distancia zero, data fora do periodo...).

 ENTRADA:   /lake/bronze/trips  e  /lake/bronze/zones
 SAIDA:     /lake/silver/trips  e  /lake/silver/zones
============================================================================
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # acha utils_spark.py

from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, DoubleType
from utils_spark import build_spark, PATHS, secao

spark = build_spark("prata-limpeza")

# ----------------------------------------------------------------------------
# 1) CORRIDAS: tipar -> derivar -> filtrar qualidade
# ----------------------------------------------------------------------------
secao("PRATA 1/2  -  Limpando e tipando as corridas")

bronze = spark.read.format("delta").load(PATHS["bronze_trips"])
antes = bronze.count()

tipado = (
    bronze
    .withColumn("pickup_ts",       F.to_timestamp("tpep_pickup_datetime"))
    .withColumn("dropoff_ts",      F.to_timestamp("tpep_dropoff_datetime"))
    .withColumn("passenger_count", F.col("passenger_count").cast(IntegerType()))
    .withColumn("trip_distance",   F.col("trip_distance").cast(DoubleType()))
    .withColumn("PULocationID",    F.col("PULocationID").cast(IntegerType()))
    .withColumn("DOLocationID",    F.col("DOLocationID").cast(IntegerType()))
    .withColumn("payment_type",    F.col("payment_type").cast(IntegerType()))
    .withColumn("fare_amount",     F.col("fare_amount").cast(DoubleType()))
    .withColumn("tip_amount",      F.col("tip_amount").cast(DoubleType()))
    .withColumn("total_amount",    F.col("total_amount").cast(DoubleType()))
)

# Coluna DERIVADA: duracao da corrida em minutos (util para o negocio).
tipado = tipado.withColumn(
    "duracao_min",
    (F.col("dropoff_ts").cast("long") - F.col("pickup_ts").cast("long")) / 60.0,
)

# Regras de QUALIDADE - cada filtro tem uma justificativa de negocio:
trips_silver = (
    tipado
    .filter(F.col("pickup_ts").isNotNull() & F.col("dropoff_ts").isNotNull())  # sem data -> inutil
    .filter(F.col("trip_distance") > 0)            # corrida precisa ter distancia
    .filter(F.col("trip_distance") < 200)          # > 200 milhas = erro grosseiro
    .filter(F.col("fare_amount") >= 0)             # tarifa negativa = invalida
    .filter(F.col("total_amount") > 0)             # total tem que ser positivo
    .filter(F.col("passenger_count") > 0)          # ao menos 1 passageiro
    .filter(F.col("duracao_min") > 0)              # dropoff depois do pickup
    .filter(F.col("duracao_min") < 1440)           # menos de 24 horas
    .filter((F.col("PULocationID") >= 1) & (F.col("PULocationID") <= 265))  # zona valida
    .filter(F.year("pickup_ts") == 2024)           # so o periodo do dataset
    .select(
        "VendorID", "pickup_ts", "dropoff_ts", "passenger_count",
        "trip_distance", "duracao_min", "PULocationID", "DOLocationID",
        "payment_type", "fare_amount", "tip_amount", "total_amount",
    )
)

(trips_silver.write
    .format("delta")
    .mode("overwrite")
    .save(PATHS["silver_trips"]))

depois = trips_silver.count()
removidas = antes - depois
print(f"-> Corridas: {antes:,} (bronze) -> {depois:,} (prata)")
print(f"   removidas {removidas:,} linhas invalidas "
      f"({100 * removidas / antes:.1f}% do total)")

# ----------------------------------------------------------------------------
# 2) ZONAS: limpeza da dimensao (trim, tipos, sem duplicatas)
# ----------------------------------------------------------------------------
secao("PRATA 2/2  -  Limpando a dimensao de zonas")

zones_bronze = spark.read.format("delta").load(PATHS["bronze_zones"])
zones_silver = (
    zones_bronze
    .withColumn("LocationID", F.col("LocationID").cast(IntegerType()))
    .withColumn("Borough", F.trim(F.col("Borough")))
    .withColumn("Zone", F.trim(F.col("Zone")))
    .filter(F.col("LocationID").isNotNull())
    .filter(F.col("Borough") != "Unknown")        # remove zonas "Unknown"
    .dropDuplicates(["LocationID"])
    .select("LocationID", "Borough", "Zone", "service_zone")
)

(zones_silver.write
    .format("delta")
    .mode("overwrite")
    .save(PATHS["silver_zones"]))

print(f"-> Zonas validas: {zones_silver.count()} bairros")

secao("PRATA concluida")
spark.stop()
