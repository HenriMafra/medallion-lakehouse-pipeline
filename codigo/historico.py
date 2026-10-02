"""
BONUS - Mostra o "time travel" do Delta Lake: o historico de versoes de uma
tabela. Cada escrita gera uma nova versao no _delta_log, o que permite auditar
e ate consultar versoes anteriores. E o que diferencia um data lake (arquivos
soltos) de um data LAKEHOUSE (tabelas com historico e transacoes).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # acha utils_spark.py

from utils_spark import build_spark, PATHS, secao

spark = build_spark("historico-delta")

tabela = f"{PATHS['gold']}/receita_por_distrito"

secao("Historico de versoes da tabela OURO 'receita_por_distrito'")
(spark.sql(f"DESCRIBE HISTORY delta.`{tabela}`")
      .select("version", "timestamp", "operation", "operationMetrics")
      .show(truncate=False))

secao("Lendo a VERSAO 0 da tabela (viagem no tempo)")
(spark.read.format("delta").option("versionAsOf", 0).load(tabela)
      .show(truncate=False))

spark.stop()
