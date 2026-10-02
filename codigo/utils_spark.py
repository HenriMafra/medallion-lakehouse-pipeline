"""
Funcoes e constantes compartilhadas pelos 3 jobs (Bronze / Prata / Ouro).

Toda a configuracao "pesada" do Spark (jars, Delta, HDFS) fica no arquivo
spark-defaults.conf (dentro da imagem). Aqui guardamos apenas:
  - os CAMINHOS das camadas no HDFS,
  - os dados de conexao com o MySQL,
  - um criador de SparkSession e um helper de impressao.
"""
from pyspark.sql import SparkSession

# Raiz do HDFS (NameNode). Tudo abaixo de /lake sao as 3 camadas Medalhao.
HDFS = "hdfs://namenode:9000"
LAKE = f"{HDFS}/lake"

PATHS = {
    "raw_trips":    f"{HDFS}/raw/yellow_tripdata.csv",  # CSV cru ja dentro do HDFS
    "bronze_trips": f"{LAKE}/bronze/trips",
    "bronze_zones": f"{LAKE}/bronze/zones",
    "silver_trips": f"{LAKE}/silver/trips",
    "silver_zones": f"{LAKE}/silver/zones",
    "gold":         f"{LAKE}/gold",
}

# Conexao com a fonte relacional (MySQL). Driver vem do jar mysql-connector-j.
JDBC_URL = "jdbc:mysql://mysql:3306/nyc"
JDBC_PROPS = {
    "user": "spark",
    "password": "spark",
    "driver": "com.mysql.cj.jdbc.Driver",
}


def build_spark(app_name: str) -> SparkSession:
    """SparkSession ja configurada via spark-defaults.conf (Delta + HDFS)."""
    spark = SparkSession.builder.appName(app_name).getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def secao(titulo: str) -> None:
    """Cabecalho destacado no console (facilita acompanhar a demo)."""
    print("\n" + "=" * 72)
    print("  " + titulo)
    print("=" * 72)
