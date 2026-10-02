# 🎥 Checklist do dia da gravação (resumo de 1 página)

> O roteiro **completo** (com tudo que falar) está em
> [`3-roteiro-apresentacao.md`](3-roteiro-apresentacao.md). Este aqui é o resumo
> rápido para o dia, focado em **provar que vocês entendem** o que estão fazendo.

---

## ✅ Antes de apertar REC

1. **Docker Desktop aberto** (verde).
2. Dê 2 cliques em **`PREPARAR-GRAVACAO.bat`** → zera o ambiente (HDFS e MySQL
   ficam **vazios**). Isso é o que permite mostrar cada camada **nascendo**.
3. Abra o navegador em **http://localhost:9870** (deixe numa aba).
4. Abra o VS Code na pasta do projeto, com um terminal embaixo.

---

## 🎬 A ordem + o que MOSTRAR e o que DIZER (a prova de domínio)

| Passo (em `passo-a-passo/`) | MOSTRE na tela | DIGA para provar que entende |
|---|---|---|
| **antes de tudo** | Em http://localhost:9870 → *Utilities → Browse* → não existe `/lake`. No MySQL, `taxi_zones` **vazia** | "Repare: está tudo vazio. Vou construir as camadas do zero agora." |
| **1 · subir** | os 4 containers subindo (`docker compose ps`) | "namenode é o cérebro do HDFS, datanode é o disco, mysql é uma fonte, spark é o motor." |
| **2 · dados** | o CSV real (300 mil corridas) e o SQL das zonas | "É dado **real** da prefeitura de NY; uso uma amostra do dado oficial, não inventado." |
| **3 · fontes** | `zonas_no_mysql = 265` e o CSV aparecendo em `/raw` no HDFS (atualize o 9870) | "Aqui o dado **passa pelo HDFS** — é o que o enunciado pede antes do Delta Lake." |
| **4 · 🟫 bronze** | as contagens + a pasta `_delta_log` no HDFS | "Bronze é o dado **cru**, sem limpar nada. O `_delta_log` é o que torna isto uma **tabela Delta**." |
| **5 · ⬜ prata** | `300.000 → ~275.602` (removeu ~8%) | "Aqui limpo: removo tarifa negativa, distância zero, datas inválidas. O dado vira confiável." |
| **6 · 🟨 ouro** | as 4 tabelas (Manhattan lidera; pico às 17–18h) | "Ouro é o dado de **negócio**. Cruzo corridas com zonas (join **fato × dimensão**)." |
| **7 · inspecionar** | as 3 camadas no HDFS + consulta SQL na Ouro | "Bronze, Prata e Ouro lado a lado. Um analista consome direto a Ouro." |

> 💡 **A "mágica" honesta:** como você zerou antes, o público vê o `/lake`
> **vazio** virar **Bronze → Prata → Ouro** ao vivo. Nada estava pronto.

---

## 👥 Sugestão de divisão entre a dupla

- **Pessoa A** — explica a **arquitetura** (os 4 containers, o porquê do HDFS e do
  Medalhão) e conduz os passos **1, 2, 3**.
- **Pessoa B** — explica e roda as **camadas 4, 5, 6** (Bronze/Prata/Ouro) e a
  inspeção **7**, destacando os números de negócio.
- Os dois respondem juntos as **perguntas** (lista pronta no fim do
  [`3-roteiro-apresentacao.md`](3-roteiro-apresentacao.md)).

---

## 🧠 Se quiser impressionar (bônus, opcional)

- Rode **`passo-a-passo/8-historico-bonus.bat`** e mostre o **histórico de versões**
  do Delta (DESCRIBE HISTORY) — explique que dá pra "voltar no tempo" e consultar
  versões antigas. É o que diferencia um *data lake* de um *lakehouse*.

---

## 🔁 Errou no meio da gravação?

Sem pânico: rode **`PREPARAR-GRAVACAO.bat`** de novo (zera tudo) e recomece do
passo 1. Como tudo é reprodutível, dá pra regravar quantas vezes quiser.
