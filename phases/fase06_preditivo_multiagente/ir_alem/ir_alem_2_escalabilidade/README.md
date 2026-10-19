# CardioAI — Ir Além 2: Otimização e Escalabilidade de Sistemas de IA

**Fase 6: Coração Sob Controle — Sistema Preditivo Multiagente**  
**Disciplina:** Otimização e Escalabilidade de Sistemas de IA (Cluster Computing)  
**Grupo:** Jonas Luis da Silva (RM561465) e Edson Henrique Felix Batista (RM566321)  
**Instituição:** FIAP — Engenharia de Software / Inteligência Artificial

---

## 🎯 Objetivo da Atividade

Desenvolver uma camada completa de **escalabilidade, processamento assíncrono em fila e análise de concorrência** para o sistema multiagente hospitalar **CardioAI**, **SEM duplicar o código principal** (reaproveitando integralmente os módulos de `src/`):

1. **Documentação Modular e Diagramação Técnica:** Mapeamento visual das fronteiras entre inferência preditiva, motor de regras determinísticas, agentes e orquestração (`docs/diagrama_modulos.png`), além da proposta de arquitetura distribuída para produção (`docs/diagrama_distribuido.png`).
2. **Fila Assíncrona e Pool Concorrente de Workers (`fila_pacientes.py`):** Ingestão contínua com `asyncio.Queue`, controle de vazão com `asyncio.Semaphore`, timeouts por paciente, retry com backoff exponencial e suporte a modo lote vetorizado (`--lote`).
3. **Baterias Empíricas de Benchmark (`benchmark.py`):** Medição real de throughput, latência e taxa de erro em cenários com e sem LLM (1.000 pacientes sem LLM com 1, 2, 4 e 8 workers + batch mode; 10 pacientes com LLM real com 1, 2 e 4 workers).
4. **Relatório Técnico Especializado (`relatorio_ir_alem_2.pdf`):** Diagnóstico do gargalo computacional e caminhos arquiteturais para clusters Kubernetes, microserviços de model serving e observabilidade distribuída.

---

## 🏗️ Estrutura de Arquivos

```
phases/fase06_preditivo_multiagente/ir_alem/ir_alem_2_escalabilidade/
├── README.md                      # Documentação completa, guia de execução e resultados
├── fila_pacientes.py              # Ingestão em fila concorrente (asyncio.Queue + Workers + Lote)
├── benchmark.py                   # Script de medição empírica e geração de CSV/PNG
├── gerar_pdf_escalabilidade.py    # Script ReportLab compilador do relatório técnico (máx. 2 páginas)
├── relatorio_ir_alem_2.md         # Relatório técnico completo de Cluster Computing
├── relatorio_ir_alem_2.pdf        # Relatório PDF de exatamente 2 páginas (validado via pypdfium2)
├── docs/
│   ├── diagrama_modulos.png       # Diagrama em alta resolução da arquitetura modular existente
│   └── diagrama_distribuido.png   # Diagrama da arquitetura distribuída proposta para produção
├── resultados/
│   ├── benchmark.csv              # Tabela com as medições reais de todas as baterias
│   └── benchmark.png              # Gráficos comparativos de vazão e escala logarítmica de latência
└── tests/
    └── test_fila.py               # Suíte de 5 testes unitários assíncronos (100% offline)
```

---

## 🚀 Como Executar

### 1. Processamento Concorrente com `fila_pacientes.py`

```bash
# Modo Sem LLM (rápido, mede throughput puro do Random Forest + regras):
python fila_pacientes.py --n 100 --workers 4 --sem-llm

# Modo Lote Vetorizado (executa predict_proba em lote matricial):
python fila_pacientes.py --n 1000 --lote

# Modo Com LLM Real (executa o sistema multiagente via OpenAI Agents SDK):
python fila_pacientes.py --n 5 --workers 2
```

### 2. Execução da Bateria Oficial de Benchmark

Executa os testes empíricos de 1.000 pacientes sem LLM (1w, 2w, 4w, 8w e lote) e os 10 pacientes com LLM real (1w, 2w e 4w), regravando `resultados/benchmark.csv` e `resultados/benchmark.png`:

```bash
python benchmark.py
```

### 3. Execução da Suíte de Testes Unitários

Executa os 5 testes de integridade da fila, concorrência e resiliência a falhas (sem custo de API):

```bash
pytest tests/test_fila.py -v
```

### 4. Compilação do Relatório Técnico em PDF

Compila o relatório formal de 2 páginas e valida a contagem via `pypdfium2`:

```bash
python gerar_pdf_escalabilidade.py
```

---

## 📊 Resultados Reais do Benchmark (`benchmark.csv`)

| Cenário de Teste | Pacientes | Workers | Tempo Total | Latência Média | Throughput | Erros |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila (1w) — Sem LLM** | 1.000 | 1 | 14,09 s | 14,1 ms | 70,99 pac/s | 0,0% |
| **Fila (2w) — Sem LLM** | 1.000 | 2 | 10,92 s | 21,8 ms | 91,58 pac/s | 0,0% |
| **Fila (4w) — Sem LLM** | 1.000 | 4 | 13,40 s | 53,5 ms | 74,62 pac/s | 0,0% |
| **Fila (8w) — Sem LLM** | 1.000 | 8 | 12,76 s | 101,8 ms | 78,38 pac/s | 0,0% |
| **Lote Vetorizado (Batch ML)** | **1.000** | **1** | **0,0128 s** | **< 0,1 ms** | **77.935,64 pac/s** | **0,0%** |
| **Multiagente (1w) — LLM Real** | 10 | 1 | 85,13 s | 8,51 s | 0,12 pac/s | 0,0% |
| **Multiagente (2w) — LLM Real** | 10 | 2 | 40,28 s | 7,87 s | 0,25 pac/s | 0,0% |
| **Multiagente (4w) — LLM Real** | **10** | **4** | **23,50 s** | **8,64 s** | **0,43 pac/s** | **0,0%** |

### 💡 Diagnóstico do Gargalo Computacional e Análise Crítica
- **Comportamento Sem LLM (Gargalo de CPU & GIL):** Na fila sem LLM, 2 workers aumentaram a vazão (70,99 $\to$ 91,58 pac/s), mas 4 e 8 workers não aumentaram (74,62 e 78,38 pac/s). Como a inferência do Random Forest é CPU-bound, no Python o `asyncio` concorre pelo Global Interpreter Lock (GIL), gerando overhead de troca de contexto sem paralelismo multicore real. Para ML a solução ótima é o **Lote Vetorizado (Batch em C/BLAS com ~78 mil pac/s)** ou **multiprocessing**.
- **O gargalo real reside na latência de rede e geração remota do LLM:** A esteira multiagente consome entre **7,8s e 8,6s por paciente** devido aos roundtrips de rede e geração de tokens.
- **Escala Concorrente Comprovada:** A elevação de 1 para 4 workers no modo multiagente reduziu o tempo total de **85,13s para 23,50s** (ganho de vazão de **$3,62\times$**), comprovando a eficácia do paralelismo assíncrono para sobrepor tempos ociosos de I/O de rede.
- **Diagnóstico e Correção da Taxa de Erro:** Na primeira medição houve 10% de falha causada por um bug do próprio harness (event loop reutilizado entre `asyncio.run()`, prendendo o cliente assíncrono da OpenAI com a mensagem `Event loop is closed`). O bug foi corrigido executando as rodadas em um único loop, e a nova medição teve **0,0% de erro** em todos os cenários (1w, 2w e 4w), com 100% de sucesso e zero bloqueios de guardrails clínicos.

---

## 🖼️ Diagramas Arquiteturais

- **Arquitetura Modular Existente:** [`docs/diagrama_modulos.png`](docs/diagrama_modulos.png)
- **Proposta de Arquitetura Distribuída para Produção:** [`docs/diagrama_distribuido.png`](docs/diagrama_distribuido.png)

---

## 📺 Demonstração em Vídeo

- **Link no YouTube (Não Listado):** [https://youtu.be/FRKwCTTr1H0](https://youtu.be/FRKwCTTr1H0)
- **Duração máxima:** 4 minutos
- **Conteúdo abordado:**
  1. Demonstração prática da execução da fila assíncrona (`fila_pacientes.py`);
  2. Comparação ao vivo entre o processamento paciente a paciente e o modo lote vetorizado;
  3. Apresentação dos gráficos de benchmark gerados e explicação do gargalo do LLM;
  4. Detalhamento da arquitetura distribuída proposta (FastAPI, RabbitMQ/Kafka, K8s HPA, Triton e Redis).
