# 🔨 Como construir este projeto do zero (na mão)

Este documento mostra **como o projeto foi montado, do nada até funcionar**,
arquivo por arquivo, na ordem certa, explicando **o quê**, **por quê** e **em que
ordem**. Serve para você entender de verdade cada peça (e conseguir explicar /
reconstruir tudo na apresentação “como se soubesse tudo que está fazendo” — porque
vai saber 🙂).

> Diferença entre os documentos do projeto:
> - **`2-como-foi-construido.md`** (este) → como o projeto foi **construído**.
> - **`1-guia-de-uso.md`** → como **rodar** o que já está pronto.
> - **`3-roteiro-apresentacao.md`** → o que **falar** no vídeo.
> - **`LEIA-ME.md`** → referência de arquitetura e conceitos.

---

## A lógica geral (por que nesta ordem)

Construímos de baixo para cima, na ordem em que as peças dependem umas das outras:

```
1. AMBIENTE   -> docker-compose + configs (o "chão de fábrica": HDFS, MySQL, Spark)
2. DADOS      -> baixar dado real e colocar nas fontes (MySQL + CSV no HDFS)
3. PIPELINE   -> jobs PySpark: Bronze -> Prata -> Ouro
4. EMPACOTAR  -> scripts (.ps1/.bat), documentação e Git
```

Primeiro o ambiente (sem ele nada roda), depois os dados (sem dado não há o que
processar), depois o processamento e, por fim, o empacotamento para apresentar e
compartilhar.

---

## ETAPA 0 — Pré-requisitos e a pasta

**O quê:** instalar o Docker Desktop e criar a pasta do projeto.

**Por quê:** tudo roda em containers Docker, então não precisamos instalar
Java/Hadoop/Spark no Windows — só o Docker. Containers garantem que roda igual em
qualquer máquina.

**Como:**
1. Instale o **Docker Desktop** e deixe-o aberto (ícone verde).
2. Crie a pasta `projeto-medallion-nyc` e abra no VS Code.

---

## ETAPA 1 — O ambiente: `ambiente/docker-compose.yml`

**O quê:** o arquivo que define os 4 serviços (containers) e como eles se ligam.

**Por quê primeiro:** é a “planta” de todo o ambiente. Sem ele, não há HDFS,
nem banco, nem Spark. Tudo depende deste arquivo.

**As 4 peças e o papel de cada uma:**

| Serviço | Imagem | Papel |
|---|---|---|
| `namenode` | bde2020/hadoop-namenode | Cérebro do HDFS: sabe **onde** cada bloco está |
| `datanode` | bde2020/hadoop-datanode | Disco do HDFS: guarda os **blocos** de dados |
| `mysql` | mysql:8.0 | Banco relacional: é **uma das fontes** (dimensão de zonas) |
| `spark` | imagem própria | Motor que lê, transforma e grava as 3 camadas Delta |

**Decisões importantes (e o porquê):**
- **Spark em *local mode*** (1 só JVM, configurado no `ambiente/spark/spark-defaults.conf`): muito
  mais leve que um cluster — ideal para rodar em um PC só.
- **`mem_limit` em cada serviço** + **MySQL com `--innodb-buffer-pool-size=128M`**:
  porque a máquina de desenvolvimento tinha pouca RAM (7,7 GB). Limitamos cada
  container para a soma caber.
- **Portas publicadas:** `9870` (web do HDFS, para mostrar no navegador), `3307`
  (MySQL — usamos 3307 e não 3306 para não conflitar com um MySQL local), `4040`
  (web do Spark durante os jobs).
- **`volumes` nomeados** (`hdfs_namenode`, `hdfs_datanode`, `mysql_data`): para os
  dados sobreviverem a um `docker compose -f ambiente/docker-compose.yml down`.
- **`./data:/data`** montado no `namenode` e no `mysql`: truque para conseguirmos
  jogar o CSV local dentro do HDFS (`hdfs dfs -put`) e carregar o SQL no MySQL.

> 👉 Conteúdo completo: veja [`ambiente/docker-compose.yml`](ambiente/docker-compose.yml) — cada bloco
> está comentado em português.

---

## ETAPA 2 — Configuração do HDFS: `ambiente/hadoop.env`

**O quê:** variáveis que configuram o Hadoop/HDFS (lidas pelas imagens bde2020).

**Por quê:** o NameNode e o DataNode precisam saber, por exemplo, o endereço do
sistema de arquivos (`fs.defaultFS=hdfs://namenode:9000`) e que só há **1 cópia**
de cada bloco (`dfs.replication=1`, porque só temos 1 DataNode).

**Detalhe que evita dor de cabeça:** ligamos
`dfs.client.use.datanode.hostname=true` — assim cliente e servidor se enxergam
pelo **hostname** (`namenode`/`datanode`), que é o que funciona dentro da rede do
Docker.

> 👉 Veja [`ambiente/hadoop.env`](ambiente/hadoop.env).

---

## ETAPA 3 — A imagem do Spark: `ambiente/spark/Dockerfile` + `ambiente/spark/spark-defaults.conf`

**O quê:** construímos a **nossa própria imagem** do Spark.

**Por quê não usar uma pronta:** para ter exatamente as versões certas e para
**baixar os `.jar` uma vez** (no build) e rodar **offline** na apresentação.

**O que entra na imagem (e por quê):**
- **`python:3.11-slim-bookworm`** como base. ⚠️ Detalhe que custou um bug real: a
  tag `python:3.11-slim` “pura” hoje aponta para o Debian 13, que **removeu o
  `openjdk-17`** (só tem o 21). O Spark 3.5 é homologado para Java 8/11/**17** —
  por isso fixamos o **`bookworm`** (Debian 12), que ainda tem o `openjdk-17`.
- **`openjdk-17-jre-headless`**: o Spark roda na JVM, precisa de Java.
- **`pyspark==3.5.3` + `delta-spark==3.2.1`**: o motor + o Delta Lake (versões
  compatíveis entre si).
- **`pandas` + `pyarrow` + `requests`**: para baixar e converter o dado real.
- **`curl` dos 3 jars** (delta-spark, delta-storage, mysql-connector): baixados no
  build para o `spark-submit` não precisar buscar nada na hora.
- **`ambiente/spark/spark-defaults.conf`**: centraliza toda a “infra” do Spark (modo local, jars,
  Delta, HDFS). Assim o comando da demo fica só `spark-submit job.py` — limpo.

> 👉 Veja [`ambiente/spark/Dockerfile`](ambiente/spark/Dockerfile) e
> [`ambiente/spark/spark-defaults.conf`](ambiente/spark/spark-defaults.conf).

---

## ETAPA 4 — Schema do MySQL: `ambiente/mysql/01_schema.sql`

**O quê:** cria a base `nyc` e a tabela `taxi_zones` (vazia).

**Por quê:** o MySQL é a nossa **fonte relacional**. Aqui mora a **dimensão** de
zonas (bairros de NYC). O arquivo fica na pasta `/docker-entrypoint-initdb.d`, que
o MySQL roda **automaticamente no primeiro boot**. Criamos só a estrutura vazia de
propósito — carregar os dados é um **passo visível** depois (bom para a demo).

> 👉 Veja [`ambiente/mysql/01_schema.sql`](ambiente/mysql/01_schema.sql).

---

## ETAPA 5 — Subir o ambiente pela 1ª vez e validar

**O quê:** construir a imagem e ligar tudo.

**Por quê agora:** antes de escrever qualquer código de processamento, garantimos
que o “chão de fábrica” está de pé. Validar cedo evita debugar 10 coisas juntas.

**Como:**
```powershell
docker compose -f ambiente/docker-compose.yml build spark      # constroi a imagem do Spark
docker compose -f ambiente/docker-compose.yml up -d            # liga os 4 containers
```
**Validação:** abrir **http://localhost:9870** e ver **“1 Live Node”** (o
DataNode registrado). Isso prova que o HDFS está funcional.

---

## ETAPA 6 — Os dados reais: `dados/preparar_dados.py`

**O quê:** baixa o dado **real** da NYC TLC e prepara as duas fontes.

**Por quê assim:**
- O trabalho exige **dado aberto e real** e proíbe sintético. Usamos o arquivo
  oficial da prefeitura de NY.
- O original é **Parquet**; como o trabalho pede **CSV**, convertemos o Parquet
  real para CSV (muda só o formato, o dado continua real).
- O mês inteiro tem ~3 milhões de corridas. Para a demo rodar leve, tiramos uma
  **amostra aleatória reproduzível de 300 mil** (`random_state=42`) — é um
  subconjunto do dado real, não invenção.
- Geramos também um `.sql` com `INSERT`s das **265 zonas** para o MySQL.

**Como:** o script roda **dentro do container spark** (que tem pandas/pyarrow):
```powershell
docker compose -f ambiente/docker-compose.yml exec spark python /data/preparar_dados.py
```

> 👉 Veja [`dados/preparar_dados.py`](dados/preparar_dados.py).

---

## ETAPA 7 — Carregar as DUAS fontes (MySQL + HDFS)

**O quê:** popular o MySQL com as zonas e **colocar o CSV dentro do HDFS**.

**Por quê:** é o ponto central do enunciado — o dado precisa **“passar pelo HDFS”**
antes do Delta Lake. Aqui isso fica visível.

**Como:**
```powershell
# (1) zonas -> MySQL
docker compose -f ambiente/docker-compose.yml exec mysql sh -c "mysql -uroot -prootpw < /data/brutos/zones_insert.sql"
# (2) CSV das corridas -> HDFS
docker compose -f ambiente/docker-compose.yml exec namenode hdfs dfs -mkdir -p /raw
docker compose -f ambiente/docker-compose.yml exec namenode hdfs dfs -put -f /data/brutos/yellow_tripdata.csv /raw/
```

---

## ETAPA 8 — A base dos jobs: `codigo/utils_spark.py`

**O quê:** um módulo com a `SparkSession` e as constantes (caminhos no HDFS,
conexão MySQL) usadas pelos 3 jobs.

**Por quê:** evita repetir configuração em cada job. Um único lugar define onde
ficam as camadas (`/lake/bronze`, `/lake/silver`, `/lake/gold`) e como conectar
no MySQL via JDBC.

> 👉 Veja [`codigo/utils_spark.py`](codigo/utils_spark.py).

---

## ETAPA 9 — 🟫 Camada BRONZE: `codigo/bronze.py`

**Conceito:** ingestão **crua**. Traz as fontes para o Delta Lake **exatamente
como vieram**, sem limpar nada, só com colunas de **linhagem** (`_fonte`,
`_ingerido_em`).

**Decisão chave:** lemos o CSV com **tudo como texto** (`inferSchema=false`).
No Bronze a regra é preservar a fidelidade do dado bruto; a tipagem vem na Prata.

**Por que existe:** é a “fonte da verdade”. Se a Prata/Ouro derem problema,
reprocessamos a partir daqui sem rebaixar dado da origem.

**Como:** `docker compose -f ambiente/docker-compose.yml exec spark spark-submit /app/jobs/bronze.py`
→ gera `/lake/bronze/trips` (300.000) e `/lake/bronze/zones` (265).

> 👉 Veja [`codigo/bronze.py`](codigo/bronze.py).

---

## ETAPA 10 — ⬜ Camada PRATA: `codigo/silver.py`

**Conceito:** dado **limpo, tipado e filtrado**.

**O que faz:** converte cada coluna para o tipo certo (datas → timestamp, valores
→ número), cria a coluna derivada **`duracao_min`** e aplica **regras de
qualidade** — cada filtro com uma justificativa de negócio (sem data, distância
zero, tarifa negativa, duração impossível, zona inválida, fora do período).

**Resultado real:** `300.000 → 275.602` (removeu ~8% de linhas ruins). Esse
“antes e depois” é a prova do valor da limpeza.

> 👉 Veja [`codigo/silver.py`](codigo/silver.py).

---

## ETAPA 11 — 🟨 Camada OURO: `codigo/gold.py`

**Conceito:** dado **pronto para o negócio**.

**O que faz:** cruza as corridas (**fato**) com as zonas (**dimensão**) — o
**JOIN fato × dimensão**, coração do modelo dimensional — e gera 4 tabelas
agregadas: receita por distrito, demanda por hora, top zonas e formas de
pagamento.

**Por que separar da Prata:** limpeza (Prata) e regra de negócio (Ouro) são
responsabilidades diferentes. Separadas, o pipeline fica testável e rastreável.

> 👉 Veja [`codigo/gold.py`](codigo/gold.py).

---

## ETAPA 12 — Consumo e bônus: `consultar.py` e `historico.py`

- **`consultar.py`** — lê as tabelas Ouro prontas e roda uma consulta SQL ad-hoc,
  simulando o que um **analista** faria.
- **`historico.py`** — mostra o **time travel** do Delta (`DESCRIBE HISTORY` +
  ler a versão 0). É o que diferencia um data lake (arquivos soltos) de um
  **lakehouse** (tabelas com histórico e transações).

> 👉 Veja [`codigo/consultar.py`](codigo/consultar.py) e [`codigo/historico.py`](codigo/historico.py).

---

## ETAPA 13 — Empacotar: scripts, documentação e Git

**O quê:** transformamos os comandos em **scripts numerados** para a demo fluir.

- **`passo-a-passo/1-subir-ambiente.bat` … `8-historico-bonus.bat`** — cada passo isolado.
- **`EXECUTAR-TUDO.bat`** — roda tudo de uma vez (ensaio).
- **`EXECUTAR-TUDO.bat`** e **`passo-a-passo/*.bat`** — versões clicáveis (contornam o
  bloqueio do PowerShell) para compartilhar com quem não é técnico.
- **Documentação** — LEIA-ME, este guia, o guia de uso e o roteiro.
- **Git** — `git init`, commit e push para um repositório **privado** no GitHub,
  para versionar e compartilhar com a dupla.

**Como versionar:**
```powershell
git init -b main
git add -A
git commit -m "Projeto Medalhao completo"
gh repo create projeto-medallion-nyc --private --source . --push
```

---

## Recapitulando a lógica do todo

1. **Ambiente** (Docker) — o chão onde tudo roda.
2. **Fontes** — MySQL (dimensão) + CSV (fato), o dado real entrando.
3. **HDFS** — o dado bruto repousando no armazenamento distribuído.
4. **Medalhão no Delta Lake** — Bronze (cru) → Prata (limpo) → Ouro (negócio).
5. **Consumo** — consultas e indicadores prontos.

Cada etapa depende da anterior e tem uma responsabilidade única — é isso que
torna o pipeline **claro, rastreável e reprocessável**. 🚕📊
