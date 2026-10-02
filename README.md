# 🏛️ Medallion Lakehouse Pipeline — Arquitetura de Dados em Camadas (Bronze, Silver & Gold)

Pipeline de Engenharia de Big Data implementando a **Arquitetura Medallion**, um dos padrões mais utilizados pela indústria moderna para estruturar dados em Data Lakehouses (como Databricks e Delta Lake).

O projeto organiza o ciclo de vida dos dados em três camadas progressivas de qualidade: **Bronze (Raw Ingestion)**, **Silver (Cleaned & Conformed)** e **Gold (Aggregated Business-Level)**, utilizando persistência colunar particionada em **Apache Parquet**.

---

## 📌 Que Problema Resolve?

Engenheiros de dados frequentemente enfrentam lagos de dados caóticos ("Data Swamps"), onde dados brutos com erros, registros duplicados e tipos inconsistentes são consumidos diretamente por painéis de BI e modelos de IA, gerando números falsos e quebras de relatórios em produção.

O **Medallion Lakehouse Pipeline** resolve esse problema através de garantias estritas em cada estágio:
1. **Rastreabilidade Total:** A camada Bronze preserva o dado bruto original sem modificações.
2. **Qualidade Assegurada:** A camada Silver higieniza, tipa e deduplica os registros.
3. **Alto Desempenho:** A camada Gold gera visões agregadas compactas prontas para consumo com latência na casa dos milissegundos.

---

## ⚙️ Arquitetura das Camadas

```
[Fontes Externas / APIs / Logs]
               │
               ▼
┌─────────────────────────────────┐
│     CAMADA BRONZE (Raw)         │ ──> Ingestão append-only, formato bruto,
│                                 │     metadados de timestamp de carga
└─────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│     CAMADA SILVER (Conformed)   │ ──> Deduplicação por chave natural,
│                                 │     validação de tipos e coordenadas válidas
└─────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│     CAMADA GOLD (Business)      │ ──> Agregações de receita, KPIs de demanda,
│                                 │     particionamento colunar otimizado
└─────────────────────────────────┘
```

### Detalhes Técnicos de Cada Camada:
- **Bronze:** Armazena os dados exatamente como recebidos, preservando o schema on-read.
- **Silver:** Remove valores nulos aberrantes, aplica conversões de data/hora ISO 8601, calcula distâncias e filtra outliers com validações estatísticas.
- **Gold:** Tabelas sumarizadas particionadas por ano e mês em formato Parquet com compressão Snappy, minimizando I/O de disco.

---

## 🏗️ Stack Tecnológica

- **Linguagem:** Python 3.10+
- **Processamento:** `pandas`, `pyarrow`, `fastparquet`
- **Formato de Armazenamento:** Apache Parquet particionado
- **Orquestração:** Scripts em lote modulares prontos para escalabilidade em ambientes distribuídos.

---

## 🚀 Como Executar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/HenriMafra/medallion-lakehouse-pipeline.git
cd medallion-lakehouse-pipeline

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: .\venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a ingestão Bronze -> Silver -> Gold
python src/run_pipeline.py
```

---

## 📄 Licença

Distribuído sob a licença **MIT**. Desenvolvido por **Henri Mafra**.
