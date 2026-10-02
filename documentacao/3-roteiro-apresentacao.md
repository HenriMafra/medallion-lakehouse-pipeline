# 🎬 Roteiro da Apresentação — Projeto Medalhão (NYC Taxi)

> **Como usar este roteiro:** abra o VS Code com a pasta do projeto à esquerda e
> um **terminal integrado** (PowerShell) embaixo. Vá lendo os blocos **🗣️ FALE**
> enquanto roda os comandos dos blocos **⌨️ RODE** e aponta para o que aparece
> nos blocos **👀 MOSTRE**. O bloco **💡 PORQUÊ** é a explicação que sustenta a
> fala caso o professor pergunte “por quê?”.
>
> Tempo total estimado: **8–12 minutos**.

---

## ✅ Antes de gravar (checklist de 1 minuto)

- [ ] **Docker Desktop ligado** (ícone verde).
- [ ] Já rodou **uma vez** o pipeline inteiro antes (assim as imagens e os dados
      já estão baixados e a gravação flui sem esperas).
- [ ] VS Code aberto na pasta `projeto-medallion-nyc`, terminal PowerShell na raiz.
- [ ] Um navegador aberto em **http://localhost:9870** (HDFS) numa aba.
- [ ] Feche programas pesados (a stack usa bastante RAM).

> 💡 **Dica de ouro:** deixe os arquivos `codigo/bronze.py`, `silver.py`, `gold.py`
> abertos em abas. Em cada etapa, mostre o código **e** o resultado rodando.

---

## ATO 0 — Abertura (≈1 min)

**🗣️ FALE:**
> “Nosso trabalho é um pipeline de engenharia de dados que usa a **Arquitetura
> Medalhão** sobre um **Delta Lake** rodando em **HDFS**. Os dados são **reais**:
> são as corridas de táxi amarelo de Nova York, dados públicos da prefeitura.
> A ideia da arquitetura Medalhão é organizar o dado em três camadas de
> qualidade crescente: **Bronze**, que é o dado cru; **Prata**, o dado limpo; e
> **Ouro**, o dado pronto para o negócio. O dado começa em **duas fontes** — um
> banco **MySQL** e um **arquivo CSV** —, passa pelo **HDFS** e termina como
> tabelas **Delta** organizadas nessas três camadas. Tudo roda em containers
> Docker; vou subir o ambiente e mostrar os dados andando de camada em camada.”

**👀 MOSTRE:** o diagrama da seção 2 do `LEIA-ME.md` (ou o `ambiente/docker-compose.yml`,
apontando os 4 serviços: `namenode`, `datanode`, `mysql`, `spark`).

**💡 PORQUÊ:** o `ambiente/docker-compose.yml` é a “planta” do ambiente. Cada serviço é
uma peça: HDFS (namenode+datanode) para armazenar, MySQL como fonte relacional
e Spark como motor de processamento.

---

## ATO 1 — Subir o ambiente (≈1 min)

**⌨️ RODE:**
```powershell
.\passo-a-passo\1-subir-ambiente.bat
```

**🗣️ FALE enquanto sobe:**
> “Esse comando constrói a imagem do Spark e sobe os quatro containers. O
> `namenode` é o cérebro do HDFS, ele sabe onde cada bloco de arquivo está; o
> `datanode` é quem guarda os blocos de verdade; o `mysql` é uma das fontes; e o
> `spark` é o motor que vai processar tudo.”

**👀 MOSTRE:** ao final, o `docker compose -f ambiente/docker-compose.yml ps` listando os 4 containers *Up*.
Depois abra **http://localhost:9870** e aponte: **“1 Live Node”** (é o nosso
DataNode) e a aba **Utilities → Browse the file system** (ainda vazia).

**💡 PORQUÊ:** mostrar a UI do HDFS prova que temos um sistema de arquivos
distribuído de verdade no ar — não é uma pasta comum do Windows.

---

## ATO 2 — Mostrar as fontes CRUAS (≈1 min)

**🗣️ FALE:**
> “Antes de processar, deixa eu mostrar de onde o dado vem. Hoje as nossas duas
> fontes estão **vazias/separadas**: o MySQL só tem a estrutura da tabela de
> zonas, e o CSV das corridas ainda está fora do HDFS.”

**⌨️ RODE (MySQL ainda só com o schema):**
```powershell
docker compose -f ambiente/docker-compose.yml exec mysql mysql -uroot -prootpw -e "SHOW TABLES FROM nyc; SELECT COUNT(*) AS zonas FROM nyc.taxi_zones;"
```
**👀 MOSTRE:** a tabela `taxi_zones` existe, mas com **0 linhas**.

**💡 PORQUÊ:** isso evidencia o “antes e depois”. Em seguida vamos popular o
MySQL e levar o CSV ao HDFS — o público vê o dado entrando no sistema.

---

## ATO 3 — Preparar os dados reais (≈1 min)

**⌨️ RODE:**
```powershell
.\passo-a-passo\2-baixar-dados.bat
```

**🗣️ FALE:**
> “Esse passo baixa o arquivo **oficial** da NYC TLC e gera nosso CSV cru. O
> arquivo original é um Parquet com cerca de 3 milhões de corridas; para a demo
> rodar leve, pego uma **amostra aleatória reproduzível de 300 mil corridas** —
> continua sendo dado **real**, não inventado. Ele também gera os comandos SQL
> para inserir as 265 zonas de Nova York no MySQL.”

**👀 MOSTRE:** a listagem final com `yellow_tripdata.csv` (~45 MB) e
`zones_insert.sql` em `dados/brutos/`.

**💡 PORQUÊ:** o enunciado exige **dado aberto e real** e proíbe dado sintético.
A amostragem é uma fatia do dado real — prática padrão em engenharia de dados.

---

## ATO 4 — Carregar as fontes: MySQL + HDFS (≈1,5 min) ⭐

**⌨️ RODE:**
```powershell
.\passo-a-passo\3-carregar-fontes.bat
```

**🗣️ FALE:**
> “Agora carrego as duas fontes. Primeiro **populo o MySQL** com as zonas — essa
> é a nossa **dimensão**, o cadastro de bairros. Depois, e isso é o ponto-chave
> do enunciado, eu **coloco o CSV das corridas dentro do HDFS** com o comando
> `hdfs dfs -put`. O dado sai do disco local e passa a viver no sistema de
> arquivos distribuído.”

**👀 MOSTRE 1:** a contagem `zonas_no_mysql = 265`.
**👀 MOSTRE 2:** a saída do `hdfs dfs -ls -h /raw` com o `yellow_tripdata.csv`.
**👀 MOSTRE 3 (impactante):** atualize **http://localhost:9870** → *Utilities →
Browse the file system* → pasta **/raw** → o CSV aparece lá, com tamanho e
número de blocos. **Esse é o “passando para o HDFS” do enunciado, ao vivo.**

**💡 PORQUÊ:** o trabalho pede explicitamente que o dado **“passe pelo HDFS”**
antes do Delta Lake. Aqui isso fica visível: o CSV é fatiado em blocos e
distribuído pelo DataNode.

---

## ATO 5 — 🟫 Camada BRONZE (≈1,5 min)

**👀 MOSTRE primeiro o código** `codigo/bronze.py` (aponte os 2 blocos: leitura do
CSV no HDFS e leitura do MySQL via JDBC; e as colunas de linhagem `_fonte` e
`_ingerido_em`).

**⌨️ RODE:**
```powershell
.\passo-a-passo\4-bronze.bat
```

**🗣️ FALE:**
> “A camada Bronze é a ingestão **crua**. Eu leio o CSV direto do HDFS e a tabela
> de zonas do MySQL, e gravo as duas como tabelas **Delta**, **sem limpar nada**.
> Repare que eu leio o CSV com tudo como **texto** — no Bronze a regra é
> preservar o dado exatamente como veio. Só adiciono duas colunas de
> **linhagem**: de onde veio e quando foi ingerido.”

**👀 MOSTRE:** a contagem `Bronze TRIPS: 300.000 linhas` e `Bronze ZONES: 265`.
Depois o `hdfs dfs -ls -R /lake/bronze`: aponte a pasta **`_delta_log`** dentro
de `trips` — “esse log de transações é o que torna isto uma **tabela Delta**, e
não um monte de arquivos soltos”.

**💡 PORQUÊ:** Bronze = fonte da verdade. Se a Prata ou a Ouro derem problema,
reprocessamos a partir do Bronze sem baixar nada de novo da origem.

---

## ATO 6 — ⬜ Camada PRATA (≈2 min) ⭐

**👀 MOSTRE primeiro** `codigo/silver.py` (aponte os `cast` de tipos, a coluna
derivada `duracao_min` e a **lista de filtros de qualidade** com os comentários).

**⌨️ RODE:**
```powershell
.\passo-a-passo\5-prata.bat
```

**🗣️ FALE:**
> “Na Prata o dado vira confiável. Eu converto cada coluna para o **tipo certo** —
> datas viram timestamp, valores viram número — crio a coluna **duração da
> corrida** e aplico **regras de qualidade**: removo corridas sem data, com
> distância zero ou absurda, com tarifa negativa, com duração impossível, e
> mantenho só o período do dataset. Cada filtro tem uma justificativa de
> negócio.”

**👀 MOSTRE (o número que impressiona):** a linha
`Corridas: 300.000 (bronze) -> XXX.XXX (prata) | removidas YY linhas (Z%)`.
> 🗣️ “Olha aqui: a Prata **descartou Z% de registros ruins**. É exatamente o
> trabalho de limpeza que diferencia o dado cru do dado pronto para análise.”

**💡 PORQUÊ:** separar limpeza (Prata) de regra de negócio (Ouro) deixa o
pipeline testável e rastreável — você sabe exatamente onde cada linha “morreu”.

---

## ATO 7 — 🟨 Camada OURO (≈2 min) ⭐⭐

**👀 MOSTRE primeiro** `codigo/gold.py` (aponte o **JOIN** entre `trips` (fato) e
`zones` (dimensão) e os 4 `groupBy`).

**⌨️ RODE:**
```powershell
.\passo-a-passo\6-ouro.bat
```

**🗣️ FALE:**
> “A camada Ouro é o dado pronto para o negócio. Aqui eu **cruzo** as corridas
> com as zonas — esse é o JOIN entre **fato e dimensão**, o coração do modelo
> dimensional — e gero quatro tabelas que respondem perguntas reais: **receita
> por distrito**, **demanda por hora do dia**, **top 10 zonas de embarque** e
> **formas de pagamento**.”

**👀 MOSTRE:** as quatro tabelas que o job imprime na tela. Pause na **receita
por distrito** (Manhattan lidera) e na **demanda por hora** (picos de manhã e
fim de tarde).
> 🗣️ “Repare que isso já é informação de negócio: dá pra ver de qual distrito
> sai mais dinheiro e em que horários a demanda explode.”

**💡 PORQUÊ:** ninguém roda 300 mil linhas num dashboard ao vivo. A Ouro
**pré-calcula** os indicadores em tabelas pequenas e rápidas.

---

## ATO 8 — Inspeção final / consumo (≈1 min)

**⌨️ RODE:**
```powershell
.\passo-a-passo\7-inspecionar.bat
```

**🗣️ FALE:**
> “Por fim, mostro a estrutura completa do nosso **Data Lakehouse** no HDFS — as
> três camadas Bronze, Prata e Ouro lado a lado — e faço uma **consulta SQL**
> direto na camada Ouro, como um analista faria no dia a dia.”

**👀 MOSTRE:** o `hdfs dfs -ls -R /lake` com as 3 pastas, e o resultado do
`spark.sql(...)` ordenando os distritos por tarifa média. Volte ao navegador
**http://localhost:9870** e navegue por `/lake/gold` para mostrar os Parquets +
`_delta_log` fisicamente no HDFS.

---

## ATO 9 — Bônus: o que torna isto um “lakehouse” (opcional, ≈1 min)

**🗣️ FALE:**
> “Um detalhe que vale destacar: como gravamos em **Delta Lake**, cada tabela tem
> um **log de transações**. Isso dá transações ACID e até **‘viagem no tempo’** —
> consultar versões anteriores da tabela.”

**⌨️ RODE (mostra o histórico de versões + lê a versão 0 da tabela Ouro):**
```powershell
docker compose -f ambiente/docker-compose.yml exec spark spark-submit /app/jobs/historico.py
```
Isso imprime o `DESCRIBE HISTORY` (cada escrita = uma versão no `_delta_log`) e
relê a tabela "na versão 0".
> Dica: rode a Ouro (`6-ouro.bat`) **de novo** antes — aí aparece a **versão 1**
> no histórico, deixando o conceito de versionamento ainda mais claro.

**💡 PORQUÊ:** é o que diferencia um **data lake** (arquivos soltos) de um
**data lakehouse** (tabelas confiáveis com histórico).

---

## ATO 10 — Encerramento (≈30 s)

**🗣️ FALE:**
> “Recapitulando: o dado nasceu em **MySQL e CSV**, **passou pelo HDFS** e
> **repousou no Delta Lake**, organizado na Arquitetura Medalhão — **Bronze**
> cru, **Prata** limpo e **Ouro** pronto para o negócio. Tudo com dado **real**
> e demonstrado ao vivo. Obrigado!”

---

## 🧠 Perguntas que o professor pode fazer (com respostas prontas)

**“Por que Delta Lake e não só Parquet?”**
> Parquet é só o formato do arquivo. O Delta adiciona um **log de transações**
> (`_delta_log`) que dá ACID, controle de schema e time travel — transforma
> arquivos soltos numa **tabela** confiável.

**“Por que a dimensão está no MySQL e o fato em CSV?”**
> É o cenário realista: cadastros (zonas) vivem num banco relacional (OLTP) e
> eventos de alto volume (corridas) chegam como arquivos. O enunciado também
> pede as duas fontes: MySQL **e** CSV.

**“O que o HDFS faz aqui que uma pasta normal não faria?”**
> O HDFS fatia arquivos grandes em **blocos distribuídos** com replicação e
> tolerância a falha, e é acessado por todo o cluster. É o armazenamento
> distribuído clássico do ecossistema Hadoop, exigido pelo trabalho.

**“Por que três camadas? Não dava pra fazer tudo de uma vez?”**
> Dava, mas ficaria impossível de manter. Separar **cru / limpo / negócio**
> deixa o pipeline **rastreável**, **reprocessável** e **testável** por etapa.

**“Isso é dado sintético?”**
> Não. É o arquivo oficial da NYC TLC; usamos uma **amostra** do dado real para
> a demo rodar rápido.

**“Spark em local mode é ‘de verdade’?”**
> Sim — é o mesmo motor e a mesma API. O *local mode* só roda os executores como
> threads na mesma JVM, ideal para uma máquina única. O código sobe igual num
> cluster real, só mudando o `--master`.

---

## 📋 Cola rápida (todos os comandos em ordem)

```powershell
.\passo-a-passo\1-subir-ambiente.bat
.\passo-a-passo\2-baixar-dados.bat
.\passo-a-passo\3-carregar-fontes.bat
.\passo-a-passo\4-bronze.bat
.\passo-a-passo\5-prata.bat
.\passo-a-passo\6-ouro.bat
.\passo-a-passo\7-inspecionar.bat
# no fim da apresentação:
.\passo-a-passo\9-parar.bat
```

---

## 📤 Saída de referência (teste real executado em 11/06/2026)

Estes são os números **reais** que este pipeline produziu nesta máquina. Servem
para você saber o que esperar e conferir se a sua execução bateu.

**Preparação dos dados:**
```
o mes completo tem 2,964,624 corridas reais
usando amostra reproduzivel de 300,000 corridas
CSV cru gerado: yellow_tripdata.csv (30.0 MB)
SQL de zonas gerado: 265 zonas
```

**Carga das fontes:**
```
zonas_no_mysql = 265
/raw/yellow_tripdata.csv -> 30.0 M no HDFS
```

**🟫 Bronze:** `300.000` corridas + `265` zonas (gravadas em Delta).

**⬜ Prata:**
```
Corridas: 300.000 (bronze) -> 275.602 (prata)
removidas 24.398 linhas invalidas (8.1% do total)
Zonas validas: 263 bairros
```

**🟨 Ouro — Receita por distrito:**
```
Manhattan      247166 corridas   R$ 5.593.100   tarifa media 14.72
Queens          25339 corridas   R$ 1.848.664   tarifa media 53.22  (aeroportos)
Brooklyn         1678 corridas   R$    54.266
Bronx             474 corridas   R$    16.725
```

**🟨 Ouro — Demanda por hora:** vale às 04h (~1.364 corridas) e pico às
17–18h (~19.700 corridas) — padrão clássico de rush.

**🟨 Ouro — Top zonas de embarque:** Midtown Center, JFK Airport, Upper East
Side. (JFK fatura R$ 1,12 mi — corridas longas de aeroporto.)

**🟨 Ouro — Formas de pagamento:**
```
Cartao de credito  229.826   ticket 28.09   gorjeta 4.16
Dinheiro            42.447   ticket 23.71   gorjeta 0.00  (gorjeta em dinheiro nao e registrada)
```

**Estrutura final no HDFS** (`hdfs dfs -ls -R /lake`): as 3 camadas, cada tabela
com sua pasta `_delta_log` (o log de transações) + arquivos `.snappy.parquet`.

> ✅ Pipeline validado de ponta a ponta: subiu o ambiente, baixou dado real,
> passou pelo HDFS e repousou no Delta Lake nas 3 camadas. Tudo reproduzível.
