"""
============================================================================
 CAMADA OURO (Gold)  -  Dados PRONTOS PARA O NEGOCIO
============================================================================
 O QUE FAZ: cruza as corridas (FATO) com as zonas (DIMENSAO) e gera tabelas
            AGREGADAS que respondem perguntas de negocio. Cada tabela Gold e
            pequena e rapida -> serve direto a um dashboard ou relatorio.

 POR QUE:   ninguem abre um dashboard e roda 3 milhoes de linhas na hora.
            A Ouro pre-calcula os indicadores (receita, demanda por hora,
            ranking de zonas, formas de pagamento).

 ENTRADA:   /lake/silver/trips  e  /lake/silver/zones
 SAIDA:     4 tabelas Delta em /lake/gold/...
============================================================================
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # acha utils_spark.py

from pyspark.sql import functions as F
from utils_spark import build_spark, PATHS, secao

spark = build_spark("ouro-negocio")

trips = spark.read.format("delta").load(PATHS["silver_trips"])
zones = spark.read.format("delta").load(PATHS["silver_zones"])

# Junta cada corrida com a zona de ORIGEM (PULocationID -> LocationID).
# Esse JOIN fato x dimensao e o coracao do modelo dimensional (estrela).
fato = trips.join(
    zones.select(
        F.col("LocationID").alias("PULocationID"),
        F.col("Borough").alias("pickup_borough"),
        F.col("Zone").alias("pickup_zone"),
    ),
    on="PULocationID",
    how="left",
)

GOLD = PATHS["gold"]

# ---------------------------------------------------------------------------
# OURO 1 - Receita por distrito (borough)
# ---------------------------------------------------------------------------
secao("OURO 1/4  -  Receita por distrito")
receita_distrito = (
    fato.groupBy("pickup_borough")
    .agg(
        F.count("*").alias("qtd_corridas"),
        F.round(F.sum("total_amount"), 2).alias("receita_total"),
        F.round(F.avg("fare_amount"), 2).alias("tarifa_media"),
        F.round(F.avg("tip_amount"), 2).alias("gorjeta_media"),
    )
    .orderBy(F.desc("receita_total"))
)
receita_distrito.write.format("delta").mode("overwrite").save(f"{GOLD}/receita_por_distrito")
receita_distrito.show(truncate=False)

# ---------------------------------------------------------------------------
# OURO 2 - Demanda por hora do dia
# ---------------------------------------------------------------------------
secao("OURO 2/4  -  Demanda por hora do dia")
por_hora = (
    trips.withColumn("hora", F.hour("pickup_ts"))
    .groupBy("hora")
    .agg(
        F.count("*").alias("qtd_corridas"),
        F.round(F.avg("trip_distance"), 2).alias("distancia_media"),
        F.round(F.avg("total_amount"), 2).alias("ticket_medio"),
    )
    .orderBy("hora")
)
por_hora.write.format("delta").mode("overwrite").save(f"{GOLD}/corridas_por_hora")
por_hora.show(24, truncate=False)

# ---------------------------------------------------------------------------
# OURO 3 - Top 10 zonas de embarque
# ---------------------------------------------------------------------------
secao("OURO 3/4  -  Top 10 zonas de embarque")
top_zonas = (
    fato.groupBy("pickup_zone", "pickup_borough")
    .agg(
        F.count("*").alias("qtd_corridas"),
        F.round(F.sum("total_amount"), 2).alias("receita_total"),
    )
    .orderBy(F.desc("qtd_corridas"))
    .limit(10)
)
top_zonas.write.format("delta").mode("overwrite").save(f"{GOLD}/top_zonas_embarque")
top_zonas.show(truncate=False)

# ---------------------------------------------------------------------------
# OURO 4 - Formas de pagamento (mapeadas pelo dicionario oficial da TLC)
# ---------------------------------------------------------------------------
secao("OURO 4/4  -  Formas de pagamento")
pagamentos = (
    trips.withColumn(
        "forma_pagamento",
        F.when(F.col("payment_type") == 1, "Cartao de credito")
         .when(F.col("payment_type") == 2, "Dinheiro")
         .when(F.col("payment_type") == 3, "Sem cobranca")
         .when(F.col("payment_type") == 4, "Disputa")
         .otherwise("Outro"),
    )
    .groupBy("forma_pagamento")
    .agg(
        F.count("*").alias("qtd_corridas"),
        F.round(F.avg("total_amount"), 2).alias("ticket_medio"),
        F.round(F.avg("tip_amount"), 2).alias("gorjeta_media"),
    )
    .orderBy(F.desc("qtd_corridas"))
)
pagamentos.write.format("delta").mode("overwrite").save(f"{GOLD}/formas_pagamento")
pagamentos.show(truncate=False)

secao("OURO concluida  -  camadas prontas para consumo de negocio")
spark.stop()
