# 🚀 Guia Passo a Passo — como rodar o projeto (para a dupla)

Este guia é para quem recebeu a pasta do projeto e quer **rodar tudo do zero**,
mesmo sem saber nada de Docker ou Spark. É só seguir na ordem. 🙂

> **Resumo:** instale o Docker Desktop → abra o Docker → dê 2 cliques em
> **`EXECUTAR-TUDO.bat`** (ou siga a pasta **`passo-a-passo`** um de cada vez). Pronto.

---

## 1. O que é este projeto (30 segundos)

Um pipeline de dados que pega corridas **reais** de táxi de Nova York, faz o dado
passar por um **HDFS** e organiza tudo num **Delta Lake** em três camadas:
**Bronze** (cru) → **Prata** (limpo) → **Ouro** (pronto para negócio) — a famosa
**Arquitetura Medalhão**. Tudo roda em containers Docker; você não instala nada
de Java/Spark/Hadoop na sua máquina.

---

## 2. Pré-requisitos (faça uma vez)

### a) Instalar o Docker Desktop
1. Baixe em: **https://www.docker.com/products/docker-desktop/**
2. Instale (aceite ativar o **WSL2** se ele pedir — é o padrão no Windows).
3. **Reinicie o PC** se o instalador pedir.

### b) Abrir o Docker Desktop e esperar ficar verde
- Abra o **Docker Desktop** pelo menu Iniciar.
- Espere o ícone da baleia (canto inferior) ficar **verde / "Engine running"**.
- ⚠️ **Sem o Docker aberto, nada funciona.** Sempre abra ele antes.

### c) Ter internet na primeira vez
A primeira execução **baixa ~3 GB** (imagens do Docker) e os dados reais (~50 MB).
Depois disso, roda offline.

> 💻 **Recomendado:** 8 GB de RAM ou mais e ~6 GB de disco livre. Se sua máquina
> tiver pouca RAM e os containers ficarem instáveis, veja a seção **Problemas →
> "Pouca memória"** no fim deste guia.

---

## 3. Rodar — Modo Fácil (recomendado) ✅

1. Abra a pasta do projeto.
2. Dê **dois cliques** em **`EXECUTAR-TUDO.bat`**.
3. Vai abrir uma janela preta. Aperte uma tecla quando pedir.
4. **Espere.** Na primeira vez demora **10–15 min** (baixando tudo). Nas próximas,
   é rápido.
5. No fim, aparece a mensagem de conclusão e o link **http://localhost:9870**.

Pronto — o pipeline inteiro rodou: ambiente no ar, dados baixados, Bronze, Prata
e Ouro criados.

---

## 4. Rodar — Modo Guiado (um passo de cada vez) 🧭

Se você quer **ver cada etapa acontecendo** (ótimo para entender ou apresentar),
abra a pasta **`passo-a-passo`** e dê dois cliques **na ordem**:

| Arquivo | O que faz |
|---|---|
| `1-subir-ambiente.bat` | Liga o HDFS + MySQL + Spark (1ª vez constrói a imagem) |
| `2-baixar-dados.bat` | Baixa as corridas reais da NYC + as zonas |
| `3-carregar-fontes.bat` | Põe as zonas no MySQL e o CSV no HDFS |
| `4-bronze.bat` | 🟫 Ingestão crua → Delta no HDFS |
| `5-prata.bat` | ⬜ Limpeza, tipos e filtros de qualidade |
| `6-ouro.bat` | 🟨 Agregações de negócio (receita, demanda, etc.) |
| `7-inspecionar.bat` | Mostra a estrutura no HDFS + consulta a Ouro |
| `8-historico-bonus.bat` | (Bônus) “viagem no tempo” do Delta Lake |
| `9-parar.bat` | Desliga os containers |

Cada janela mostra o resultado e espera você apertar uma tecla para fechar.

---

## 5. O que você deve VER (confira se bateu)

- **Passo 2:** “o mes completo tem 2,964,624 corridas reais” → amostra de 300.000.
- **Passo 3:** `zonas_no_mysql = 265` e o `yellow_tripdata.csv` (30 MB) no HDFS.
- **Passo 4 (Bronze):** `300.000` corridas + `265` zonas gravadas.
- **Passo 5 (Prata):** `300.000 → 275.602` (removeu ~8% de linhas ruins).
- **Passo 6 (Ouro):** tabelas com **Manhattan** liderando a receita, pico de
  demanda às **17–18h**, **JFK** no top de zonas.

Para ver no navegador: abra **http://localhost:9870** → menu **Utilities → Browse
the file system** → pasta **/lake** (estão lá as 3 camadas no HDFS).

---

## 6. Como parar (libera memória)

Dê dois cliques em **`passo-a-passo/9-parar.bat`**. Os dados ficam
salvos; para voltar, é só rodar de novo.

> Para apagar **tudo**, inclusive os dados, abra um PowerShell na pasta e rode:
> `docker compose -f ambiente/docker-compose.yml down -v`

---

## 7. Entender o projeto a fundo (opcional)

- **`LEIA-ME.md`** — arquitetura e todos os conceitos explicados (Medalhão, Delta
  Lake, HDFS, fato × dimensão).
- **`3-roteiro-apresentacao.md`** — roteiro de apresentação com “o que falar” em
  cada etapa e perguntas que o professor pode fazer (com respostas).

---

## 8. 🛠️ Problemas comuns (e soluções)

| Problema | Solução |
|---|---|
| **“error during connect / docker daemon”** | O Docker Desktop não está aberto. Abra e espere ficar verde. |
| **A janela fecha sozinha / nada acontece** | Abra pelo `.bat` (ele já contorna o bloqueio do PowerShell). Não tente rodar os `.ps1` direto com 2 cliques. |
| **“O Windows protegeu o seu PC” (SmartScreen) ao abrir um `.bat`** | Normal para arquivo que veio da internet. Clique em **Mais informações → Executar assim mesmo**. |
| **“...cannot be loaded because running scripts is disabled”** | Use os `.bat` (recomendado). Ou rode uma vez no PowerShell: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| **Primeira vez está MUITO demorada** | Normal: está baixando ~3 GB. Deixe terminar (10–15 min). |
| **“port is already allocated” (porta 9870/3307/4040/9864)** | Algo já usa essa porta. Feche o outro programa, ou me avise para trocar a porta no `ambiente/docker-compose.yml`. |
| **Pouca memória / container “killed” / muito lento** | Sua máquina tem pouca RAM. Veja o passo abaixo. |
| **Quero zerar tudo e começar limpo** | PowerShell na pasta: `docker compose -f ambiente/docker-compose.yml down -v` e rode de novo. |

### Pouca memória (máquinas com 8 GB ou menos)
O projeto já vem com um arquivo **`documentacao/ajuste-memoria-wslconfig.txt`** na raiz, pronto. Faça:

1. **Copie** o `documentacao/ajuste-memoria-wslconfig.txt` para a pasta do seu usuário, **renomeando**
   para `.wslconfig` (com ponto, sem o `.exemplo`):
   destino → `C:\Users\SEU-USUARIO\.wslconfig`
2. Abra esse `.wslconfig` e ajuste `memory` para ~70% da sua RAM
   (8 GB → `memory=5GB`; 16 GB → `memory=10GB`).
3. Abra um PowerShell, rode `wsl --shutdown` e reabra o Docker Desktop.

> Em máquinas com **16 GB ou mais**, você normalmente **nem precisa** disso —
> rode direto o `EXECUTAR-TUDO.bat`.

---

✅ **É isso!** Qualquer travada, manda a mensagem da janela preta (o erro) para a
dupla. Bons estudos! 🚕📊
