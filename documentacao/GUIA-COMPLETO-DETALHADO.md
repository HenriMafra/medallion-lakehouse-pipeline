# 📘 Guia COMPLETO e Detalhado — Projeto Medalhão (do zero ao fim)

Este é o documento **mais completo** do projeto. Ele explica **de onde vem cada
coisa**, **como sobe cada parte**, **a sequência exata** e **cada código, um a
um**. Se você ler isto e entender, você consegue explicar o trabalho inteiro e
responder qualquer pergunta. 💪

> Sumário:
> 1. [O que vamos construir](#1)
> 2. [De onde vem CADA coisa (fontes)](#2)
> 3. [A sequência completa (o mapa)](#3)
> 4. [Como SUBIR cada coisa (comando por comando)](#4)
> 5. [Os CÓDIGOS, um a um (bloco a bloco)](#5)
> 6. [Perguntas que o professor pode fazer](#6)

---

<a name="1"></a>
## 1. O que vamos construir

Um **pipeline de engenharia de dados** que pega corridas **reais** de táxi de
Nova York e organiza os dados em **3 camadas de qualidade** (a *Arquitetura
Medalhão*), guardadas como **tabelas Delta** dentro do **HDFS**.

O caminho que o dado percorre (exigido pelo enunciado):

```
   FONTES                      ARMAZENAMENTO DISTRIBUÍDO        LAKEHOUSE (Delta)
 ┌──────────────┐   JDBC                                   ┌─────────────────────┐
 │ MySQL        │───────────┐                              │  /lake (no HDFS)    │
 │ (zonas)      │           │      ┌──────────┐            │   🟫 bronze (cru)   │
 └──────────────┘           ├────► │  SPARK   │ ─────────► │   ⬜ silver (limpo) │
 ┌──────────────┐  hdfs put │      │ + Delta  │            │   🟨 gold (negócio) │
 │ CSV          │───────────┘      └──────────┘            └─────────────────────┘
 │ (corridas)   │
 └──────────────┘
```

- **🟫 Bronze** = dado **cru** (como veio, sem limpar).
- **⬜ Prata** = dado **limpo** (tipos certos, sem lixo).
- **🟨 Ouro** = dado de **negócio** (tabelas prontas para análise).

**Pré-requisito único:** Docker Desktop instalado e aberto. Tudo o resto roda
dentro de containers — você **não** instala Java/Spark/Hadoop na máquina.

---

<a name="2"></a>
## 2. De onde vem CADA coisa (as fontes) 🔎

Nada aqui é inventado: tudo é **aberto, oficial e rastreável**.

### 2.1 Os dados (o "combustível")

| O quê | De onde | Detalhe |
|---|---|---|
| **Corridas de táxi** | NYC TLC (prefeitura de NY) — `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet` | Arquivo **oficial** de janeiro/2024 (~3 milhões de corridas). É **Parquet**; convertemos para **CSV** porque o enunciado pede CSV. Usamos uma **amostra de 300 mil** (aleatória, reproduzível) só para rodar leve. |
| **Tabela de zonas** | NYC TLC — `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv` | As **265 zonas** de NY (id → bairro/distrito). É a nossa **dimensão**, carregada no MySQL. |

> Quem baixa isso é o script `dados/preparar_dados.py` (explicado na seção 5.6).

### 2.2 As imagens Docker (as "peças de software")

| Imagem | De onde | O que é |
|---|---|---|
| `bde2020/hadoop-namenode` | Docker Hub | O **NameNode** do HDFS (o "índice": sabe onde cada bloco está). |
| `bde2020/hadoop-datanode` | Docker Hub | O **DataNode** do HDFS (guarda os blocos de verdade). |
| `mysql:8.0` | Docker Hub | O banco relacional (nossa fonte de zonas). |
| `medallion-spark` | **Construída por nós** | O motor Spark + Delta. Veja abaixo o que entra nela. |

### 2.3 O que entra na imagem do Spark (construída por nós)

A imagem `medallion-spark` é montada pelo `ambiente/spark/Dockerfile` a partir de
uma base **Python** e recebe:

| Item | De onde | Por quê |
|---|---|---|
| Base `python:3.11-slim-bookworm` | Docker Hub | Debian 12 (a última base com **openjdk-17**, o Java homologado pro Spark 3.5). |
| `openjdk-17-jre-headless` | apt (Debian) | O Spark roda na **JVM**, precisa de Java. |
| `pyspark==3.5.3` | pip (PyPI) | O **motor** de processamento. |
| `delta-spark==3.2.1` | pip (PyPI) | A API do **Delta Lake**. |
| `pandas`, `pyarrow`, `requests` | pip (PyPI) | Baixar e converter o dado real. |
| 3 arquivos `.jar` | **Maven Central** (`repo1.maven.org`) | `delta-spark` + `delta-storage` (o Delta na JVM) e `mysql-connector-j` (o driver JDBC do MySQL). |

> 💡 **Por que baixar os `.jar` no build?** Para o `spark-submit` **não** precisar
> buscar nada na internet durante a apresentação. Tudo já fica dentro da imagem.

---

<a name="3"></a>
## 3. A sequência completa (o mapa) 🗺️

Cada passo só usa o que o passo anterior produziu — fluxo **para frente**, nada
retroativo:

| # | Passo | Comando (atalho) | O que ENTRA | O que SAI |
|---|---|---|---|---|
| 0 | Subir ambiente | `1-subir-ambiente.bat` | (imagens Docker) | 4 containers no ar (HDFS, MySQL, Spark) |
| 1 | Preparar dados | `2-baixar-dados.bat` | URLs da NYC TLC | `yellow_tripdata.csv` + `zones_insert.sql` |
| 2 | Carregar fontes | `3-carregar-fontes.bat` | os arquivos do passo 1 | 265 zonas no MySQL + CSV no HDFS `/raw` |
| 3 | 🟫 Bronze | `4-bronze.bat` | MySQL + CSV (do HDFS) | `/lake/bronze/{trips,zones}` (Delta) |
| 4 | ⬜ Prata | `5-prata.bat` | `/lake/bronze` | `/lake/silver/{trips,zones}` (Delta) |
| 5 | 🟨 Ouro | `6-ouro.bat` | `/lake/silver` | `/lake/gold/*` (4 tabelas Delta) |
| 6 | Inspecionar | `7-inspecionar.bat` | `/lake/gold` | mostra estrutura + consultas |

---

<a name="4"></a>
## 4. Como SUBIR cada coisa (comando por comando) 🛠️

Aqui está **cada comando**, o que ele faz por baixo e o que você deve ver. (Os
`.bat` da pasta `passo-a-passo/` só chamam esses comandos — mostro os "crus" para
você entender de verdade.)

### PASSO 0 — Subir o ambiente

```powershell
docker compose -f ambiente/docker-compose.yml up -d --build
```
**O que acontece, em ordem:**
1. `--build` → o Docker **constrói** a imagem `medallion-spark` (lê o `Dockerfile`,
   instala Java + PySpark + Delta, baixa os `.jar`). Só na 1ª vez (~10-15 min).
2. `up -d` → o Docker **baixa** as imagens do Hadoop e do MySQL (1ª vez), cria a
   **rede** privada e os **volumes**, e **liga os 4 containers** em segundo plano (`-d`).

**Como verificar que subiu:**
```powershell
docker compose -f ambiente/docker-compose.yml ps          # os 4 containers "Up"
```
- Abra **http://localhost:9870** → menu *Utilities → Browse the file system* →
  confirme que **não existe `/lake` ainda** (vamos criar). E em *Overview* deve
  aparecer **1 Live Node** (o DataNode registrado).

> ⚠️ **Importante (uma sutileza real):** o `00_subir.ps1` espera o **MySQL** ficar
> pronto antes de continuar. Sem isso, o MySQL ainda está inicializando quando a
> carga das zonas roda, e elas entram **vazias** (0 zonas → join nulo na Ouro).
> Por isso o passo 0 inclui um "esperar o banco aceitar consultas".

### PASSO 1 — Preparar os dados

```powershell
docker compose -f ambiente/docker-compose.yml exec spark python /data/preparar_dados.py
```
**O que faz:** roda o script **dentro do container Spark** (que tem pandas). Ele
baixa o Parquet oficial, tira a amostra de 300 mil, salva como `yellow_tripdata.csv`
e gera o `zones_insert.sql` (os comandos para inserir as 265 zonas).
**Você verá:** mensagens `[download]...`, `[ok] CSV cru gerado...`, `265 zonas`.

### PASSO 2 — Carregar as duas fontes

```powershell
# (a) Zonas -> MySQL
docker compose -f ambiente/docker-compose.yml exec mysql sh -c "mysql -uroot -prootpw < /data/brutos/zones_insert.sql"
docker compose -f ambiente/docker-compose.yml exec mysql mysql -uroot -prootpw -e "SELECT COUNT(*) FROM nyc.taxi_zones;"

# (b) CSV das corridas -> HDFS
docker compose -f ambiente/docker-compose.yml exec namenode hdfs dfs -mkdir -p /raw
docker compose -f ambiente/docker-compose.yml exec namenode hdfs dfs -put -f /data/brutos/yellow_tripdata.csv /raw/
docker compose -f ambiente/docker-compose.yml exec namenode hdfs dfs -ls -h /raw
```
**O que faz:**
- (a) Manda o `zones_insert.sql` para o cliente `mysql` dentro do container → popula
  a tabela `taxi_zones`. A 2ª linha confirma **265**.
- (b) `hdfs dfs -put` **copia o CSV local para dentro do HDFS** (a pasta `/raw`).
  **Esse é o "passando para o HDFS" que o enunciado pede.** Atualize o
  http://localhost:9870 e veja o arquivo aparecer em `/raw`.

### PASSOS 3, 4, 5 — Bronze, Prata, Ouro

```powershell
docker compose -f ambiente/docker-compose.yml exec spark spark-submit /app/jobs/bronze.py
docker compose -f ambiente/docker-compose.yml exec spark spark-submit /app/jobs/silver.py
docker compose -f ambiente/docker-compose.yml exec spark spark-submit /app/jobs/gold.py
```
**O que faz:** `spark-submit` roda cada job PySpark. Cada um **lê a camada anterior
e grava a próxima** como tabela **Delta** no HDFS. (Os jobs ficam na pasta `codigo/`
do seu PC, mas o container os enxerga em `/app/jobs/` — por isso o caminho é esse.)

### PASSO 6 — Inspecionar

```powershell
docker compose -f ambiente/docker-compose.yml exec namenode hdfs dfs -ls -R /lake
docker compose -f ambiente/docker-compose.yml exec spark spark-submit /app/jobs/consultar.py
```
**O que faz:** lista as **3 camadas** no HDFS e roda consultas na Ouro (como um
analista). Veja as pastas `_delta_log` (o "log de transações" que torna aquilo uma
**tabela Delta**, não só arquivos).

### Para PARAR / ZERAR

```powershell
docker compose -f ambiente/docker-compose.yml down       # para (dados ficam salvos)
docker compose -f ambiente/docker-compose.yml down -v    # zera TUDO (apaga HDFS + MySQL)
```

---

<a name="5"></a>
## 5. Os CÓDIGOS, um a um (bloco a bloco) 🧩

Aqui cada arquivo é explicado. O conteúdo completo de cada um está na pasta
indicada (e no `COMECE-AQUI.html`, com botão de copiar).

### 5.1 `ambiente/docker-compose.yml` — a planta do ambiente
Define os **4 serviços**. Pontos-chave de cada um:
- **namenode / datanode** → o HDFS. `mem_limit` pequeno (cabe em pouca RAM);
  `ports: 9870` expõe a interface web; `volumes` nomeados guardam os dados.
- **mysql** → `--innodb-buffer-pool-size=128M` reduz a RAM; `ports: 3307:3306`
  (usamos 3307 fora para não bater com um MySQL local); monta `ambiente/mysql`
  em `/docker-entrypoint-initdb.d` (o schema roda no 1º boot) e `../dados` em
  `/data` (para carregar o SQL).
- **spark** → `build: ./spark` (constrói a nossa imagem); monta `../codigo` em
  `/app/jobs` (os jobs) e `../dados` em `/data`; `command: tail -f /dev/null` deixa
  o container **vivo** para rodarmos `spark-submit` quando quisermos.

> Detalhe: `hostname:` (namenode/datanode/mysql/spark) é o que permite os containers
> se acharem pelo nome dentro da rede do Docker — por isso o Spark conecta em
> `hdfs://namenode:9000` e `jdbc:mysql://mysql:3306`.

### 5.2 `ambiente/hadoop.env` — configuração do HDFS
Cada linha vira uma config do Hadoop. As importantes:
- `CORE_CONF_fs_defaultFS=hdfs://namenode:9000` → o endereço "oficial" do HDFS.
- `HDFS_CONF_dfs_replication=1` → 1 cópia de cada bloco (só temos 1 DataNode).
- `HDFS_CONF_dfs_permissions_enabled=false` → evita erro de permissão quando o Spark grava.
- `...use_datanode_hostname=true` → cliente e servidor se acham pelo **hostname**
  (essencial na rede do Docker).

### 5.3 `ambiente/spark/Dockerfile` — a imagem do Spark
Linha a linha:
1. `FROM python:3.11-slim-bookworm` → base com Java 17 disponível.
2. `apt-get install openjdk-17-jre-headless ...` → instala o Java (o Spark precisa).
3. `pip install pyspark==3.5.3 delta-spark==3.2.1 pandas pyarrow requests` → o motor + Delta + libs de dados.
4. `curl ... .jar` → baixa os 3 jars do Maven (Delta + driver MySQL) **no build**.
5. `ENV SPARK_CONF_DIR=/opt/spark-conf` + `COPY spark-defaults.conf` → deixa as
   configs prontas para o `spark-submit`.

### 5.4 `ambiente/spark/spark-defaults.conf` — config padrão do Spark
Centraliza a "infra" para o comando ficar só `spark-submit job.py`:
- `spark.master local[*]` → modo **local** (1 JVM, leve).
- `spark.jars ...` → os 3 jars (Delta + MySQL).
- `spark.sql.extensions` + `spark.sql.catalog.spark_catalog` → **ligam o Delta Lake**.
- `spark.hadoop.fs.defaultFS hdfs://namenode:9000` → grava no HDFS por padrão.

### 5.5 `ambiente/mysql/01_schema.sql` — a tabela de zonas
Cria o banco `nyc` e a tabela **`taxi_zones`** (LocationID, Borough, Zone,
service_zone) **vazia**. Roda **automaticamente** no 1º boot do MySQL. Criamos só
a estrutura de propósito — popular é um passo visível depois.

### 5.6 `dados/preparar_dados.py` — baixa e prepara o dado real
Três funções:
- `download(url, dest)` → baixa um arquivo (pula se já existe = **idempotente**).
- `build_trips_csv()` → baixa o Parquet, lê com pandas, tira **amostra de 300k**
  (`random_state=42` = reproduzível), salva como CSV, apaga o Parquet.
- `build_zones_sql()` → baixa o CSV de zonas e gera os `INSERT` (escapando aspas).

### 5.7 `codigo/utils_spark.py` — a base dos jobs
Não processa nada; só **centraliza**:
- `HDFS`, `LAKE` e o dicionário `PATHS` → os caminhos das 3 camadas no HDFS.
- `JDBC_URL` / `JDBC_PROPS` → como conectar no MySQL.
- `build_spark(nome)` → cria a SparkSession (já com Delta+HDFS, via o `spark-defaults`).
- `secao(titulo)` → imprime um cabeçalho bonito no console.

### 5.8 🟫 `codigo/bronze.py` — ingestão crua
Blocos:
1. `sys.path.insert(...)` → garante que ele acha o `utils_spark` ao rodar via `spark-submit`.
2. **Lê o CSV do HDFS** com `inferSchema=false` → **tudo como texto** (Bronze é cru,
   não confia no tipo).
3. Adiciona `_fonte` e `_ingerido_em` (colunas de **linhagem**: de onde veio, quando).
4. Grava em Delta (`mode("overwrite")`) em `/lake/bronze/trips`.
5. **Lê as zonas do MySQL** via `spark.read.jdbc(...)` e grava em `/lake/bronze/zones`.
> Regra do Bronze: **não jogar linha fora, não mudar tipo**. É a fotografia do dado bruto.

### 5.9 ⬜ `codigo/silver.py` — limpeza e qualidade
Blocos:
1. Lê o Bronze (`antes = bronze.count()`).
2. **Tipa** cada coluna (`cast`): datas → `timestamp`, valores → `double`, ids → `int`.
3. Cria a coluna derivada **`duracao_min`** (dropoff − pickup, em minutos).
4. **Filtros de qualidade** — cada um com uma razão de negócio:
   - sem data de pickup/dropoff → fora;
   - `trip_distance > 0` e `< 200` (zero ou >200 milhas = erro);
   - `fare_amount >= 0`, `total_amount > 0` (valores impossíveis);
   - `passenger_count > 0`; `0 < duracao_min < 1440` (< 24h);
   - `PULocationID` entre 1 e 265 (zona válida); `year(pickup) == 2024`.
5. Grava em `/lake/silver/trips` e mostra **antes → depois** (removeu ~8%).
6. Limpa as zonas (trim, tira "Unknown", sem duplicatas) → `/lake/silver/zones`.

### 5.10 🟨 `codigo/gold.py` — negócio
Blocos:
1. Lê `silver/trips` (fato) e `silver/zones` (dimensão).
2. **JOIN** `trips.PULocationID = zones.LocationID` → o coração do **modelo
   dimensional** (fato × dimensão), trazendo o bairro/distrito para cada corrida.
3. Gera **4 tabelas** com `groupBy` + `agg`:
   - `receita_por_distrito` (soma, média, gorjeta por borough);
   - `corridas_por_hora` (demanda por hora do dia);
   - `top_zonas_embarque` (top 10 zonas);
   - `formas_pagamento` (mapeando `payment_type` 1→cartão, 2→dinheiro... pelo
     dicionário oficial da TLC).
4. Cada tabela é gravada em `/lake/gold/<nome>` e impressa com `.show()`.

### 5.11 `codigo/consultar.py` e `codigo/historico.py`
- **`consultar.py`** → lê as 4 tabelas Ouro e roda uma **consulta SQL** ad-hoc
  (distritos por tarifa média). Simula o analista consumindo o lakehouse.
- **`historico.py`** → `DESCRIBE HISTORY` numa tabela Delta + lê a **versão 0**
  (o "time travel"). Mostra por que isto é um **lakehouse** e não arquivos soltos.

---

<a name="6"></a>
## 6. Perguntas que o professor pode fazer (com respostas)

**"De onde vêm os dados?"** → Do site oficial da NYC TLC (prefeitura de NY); links
diretos na seção 2. Usamos uma amostra do dado **real**, não sintético.

**"O que o HDFS faz que uma pasta comum não faz?"** → Ele é um sistema de arquivos
**distribuído**: fatia arquivos grandes em blocos, replica e tolera falha. É o
armazenamento clássico do ecossistema Hadoop, exigido antes do Delta.

**"Por que Delta Lake e não só Parquet?"** → Parquet é só o formato. O Delta
adiciona um **log de transações** (`_delta_log`) → dá ACID, controle de schema e
*time travel*. Transforma arquivos numa **tabela** confiável (lakehouse).

**"Por que 3 camadas?"** → Para separar responsabilidades: Bronze (cru/auditável),
Prata (limpeza), Ouro (negócio). Fica **rastreável**, **reprocessável** e testável.

**"Por que a dimensão no MySQL e o fato em CSV?"** → Cenário realista: cadastros
num banco relacional (OLTP), eventos de alto volume em arquivos. O enunciado também
pede as duas fontes.

**"Spark em local mode é de verdade?"** → Sim, mesma API e motor; só roda os
executores como threads numa JVM, ideal para 1 máquina. Para um cluster, muda só o
`--master`.

**"Por que vocês esperam o MySQL no passo 0?"** → Porque o banco leva uns segundos
para inicializar; sem esperar, a carga das zonas rodaria cedo demais e entraria
vazia. É um detalhe de orquestração que deixamos robusto.

---

> 📎 Atalhos: o conteúdo **completo de cada arquivo** está no `COMECE-AQUI.html`
> (com botão copiar). O que **falar** em cada passo está no
> `3-roteiro-apresentacao.md`. O resumo do dia da gravação está no
> `4-checklist-de-gravacao.md`.
