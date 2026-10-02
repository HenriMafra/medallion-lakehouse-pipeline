"""
Consulta as tabelas da camada OURO que ja estao prontas (sem reprocessar).
Simula o que um ANALISTA faria: ler o Data Lakehouse e responder perguntas.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # acha utils_spark.py

from utils_spark import build_spark, PATHS, secao

spark = build_spark("consulta-ouro")
GOLD = PATHS["gold"]

for nome in ["receita_por_distrito", "corridas_por_hora",
             "top_zonas_embarque", "formas_pagamento"]:
    secao(f"GOLD: {nome}")
    spark.read.format("delta").load(f"{GOLD}/{nome}").show(50, truncate=False)

# Exemplo de consulta SQL ad-hoc direto sobre a camada Ouro.
secao("Exemplo SQL ad-hoc: distritos ordenados por tarifa media")
df = spark.read.format("delta").load(f"{GOLD}/receita_por_distrito")
df.createOrReplaceTempView("receita")
spark.sql("""
    SELECT pickup_borough, qtd_corridas, receita_total, tarifa_media
    FROM receita
    WHERE pickup_borough IS NOT NULL
    ORDER BY tarifa_media DESC
""").show(truncate=False)

spark.stop()
