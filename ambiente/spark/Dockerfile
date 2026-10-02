# ============================================================================
#  Imagem do motor SPARK + DELTA LAKE (enxuta, baseada em python-slim).
#  Construimos a nossa propria imagem para:
#    - ter PySpark + Delta na versao certa (3.5.3 / 3.2.1),
#    - baixar os .jar UMA vez (no build) e rodar OFFLINE na apresentacao,
#    - ter pandas/pyarrow para preparar o CSV real da NYC TLC.
# ============================================================================
# Fixamos o Debian 12 "bookworm": e a ultima base com openjdk-17 (o Java
# homologado para o Spark 3.5). O 'python:3.11-slim' puro ja aponta para o
# Debian 13, que so traz o openjdk-21 (nao suportado pelo Spark 3.5).
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

# Java e pre-requisito do Spark (Spark roda na JVM). procps -> comando 'ps'
# que o Spark usa internamente. curl/ca-certificates -> baixar os jars.
RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless procps curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Bibliotecas Python:
#   pyspark      -> o motor de processamento distribuido
#   delta-spark  -> API Python do Delta Lake (formato das tabelas)
#   pandas/pyarrow -> ler o parquet oficial da TLC e gerar o CSV cru
#   requests     -> baixar os dados abertos
RUN pip install --no-cache-dir \
        pyspark==3.5.3 \
        delta-spark==3.2.1 \
        pandas==2.2.2 \
        pyarrow==16.1.0 \
        requests==2.32.3

# Baixa os .jar necessarios AGORA (build tem internet). Assim o spark-submit
# nao precisa buscar nada no Maven durante a demonstracao.
#   delta-spark/delta-storage -> implementacao do formato Delta na JVM
#   mysql-connector-j        -> driver JDBC para ler do MySQL
ENV JARS_DIR=/opt/jars
RUN mkdir -p "$JARS_DIR" && cd "$JARS_DIR" && \
    curl -fsSL -o delta-spark_2.12-3.2.1.jar  https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.1/delta-spark_2.12-3.2.1.jar && \
    curl -fsSL -o delta-storage-3.2.1.jar     https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.1/delta-storage-3.2.1.jar && \
    curl -fsSL -o mysql-connector-j-8.4.0.jar https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.4.0/mysql-connector-j-8.4.0.jar

# Configuracao padrao do Spark: assim o comando da demo fica so
# "spark-submit job.py" (jars, Delta e HDFS ja vem ligados por aqui).
ENV SPARK_CONF_DIR=/opt/spark-conf
COPY spark-defaults.conf /opt/spark-conf/spark-defaults.conf

WORKDIR /app
