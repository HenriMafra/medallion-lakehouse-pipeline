# ✅ Como o vídeo atende CADA exigência do professor

> **Enunciado (literal):** "Deve-se usar o modelo Medallion... organizar as
> informações em um Delta Lake. As três camadas: Bronze (dados brutos), Prata
> (dados limpos e filtrados) e Ouro (dados prontos para negócios). Devem iniciar
> no MySQL e arquivos CSV, passando para o HDFS e repousando finalmente no Delta Lake."

A boa notícia: **o projeto já faz tudo isso.** O vídeo é só mostrar cada parte
acontecendo e **dizer em voz alta** que aquilo atende o requisito.

---

## 🗺️ O mapa: cada exigência → o que MOSTRAR no vídeo

| O professor pede | No vídeo, você MOSTRA isto... | Em que passo |
|---|---|---|
| **Iniciar no MySQL** | a tabela `taxi_zones` no MySQL (fonte relacional) — `SELECT COUNT(*)` = 265 | Passo "Carregar fontes" |
| **Iniciar em arquivos CSV** | o arquivo `yellow_tripdata.csv` (as corridas) | Passo "Dados" / "Carregar fontes" |
| **Passando para o HDFS** | o comando `hdfs dfs -put` jogando o CSV no HDFS + o arquivo aparecendo em `localhost:9870 → /raw` | Passo "Carregar fontes" |
| **Repousando no Delta Lake** | as tabelas em formato **Delta** (a pasta `_delta_log`) dentro do HDFS | Passos Bronze/Prata/Ouro + Inspecionar |
| **Bronze (dados brutos)** | a ingestão **crua** — dado como veio, sem limpar (300.000 corridas + 265 zonas) | Passo Bronze |
| **Prata (limpos e filtrados)** | a **limpeza/filtros**: 300.000 → 275.602 (removeu ~8% de lixo) | Passo Prata |
| **Ouro (prontos para negócios)** | as tabelas **agregadas** (receita por distrito, demanda por hora, top zonas) | Passo Ouro |
| **Modelo Medalhão (3 camadas)** | as **3 pastas** `bronze / silver / gold` lado a lado no HDFS | Passo Inspecionar (`hdfs dfs -ls -R /lake`) |

---

## 🗣️ As 4 "frases mágicas" (deixam o requisito ÓBVIO pro professor)

Fale estas frases nos momentos certos — elas conectam o que está na tela com o
que o enunciado pede:

1. **Ao carregar as fontes:**
   *"O dado começa em DUAS fontes, como o trabalho pede: o MySQL com as zonas e o arquivo CSV com as corridas."*
2. **Ao fazer o `hdfs dfs -put`:**
   *"Agora o dado PASSA PELO HDFS — é exatamente o 'passando para o HDFS' do enunciado."*
3. **Ao rodar Bronze/Prata/Ouro:**
   *"E aqui ele REPOUSA no Delta Lake, organizado na Arquitetura Medalhão em três camadas."*
4. **Na inspeção final:**
   *"As três camadas — Bronze cru, Prata limpo e Ouro pronto para o negócio — todas como tabelas Delta dentro do HDFS."*

---

## 🎯 Resumo do fluxo que prova tudo (a sequência do vídeo)

```
1. Sobe o ambiente (Docker)                         -> ambiente pronto
2. Mostra as fontes:  MySQL (zonas)  +  CSV (corridas)   <- "inicia no MySQL e CSV"
3. hdfs dfs -put do CSV  ->  /raw no HDFS                 <- "passando para o HDFS"
4. 🟫 Bronze: ingestao crua  -> Delta no HDFS             <- "dados brutos" + "Delta Lake"
5. ⬜ Prata: limpa e filtra (300k -> 275k)               <- "dados limpos e filtrados"
6. 🟨 Ouro: agrega p/ negocio (receita, ranking...)      <- "prontos para negocios"
7. Inspeciona: as 3 camadas no HDFS (bronze/silver/gold) <- "modelo Medalhao"
```

Se o vídeo mostra esses 7 momentos e você fala as 4 frases, **todos os requisitos
do enunciado estão visivelmente atendidos**. ✅
