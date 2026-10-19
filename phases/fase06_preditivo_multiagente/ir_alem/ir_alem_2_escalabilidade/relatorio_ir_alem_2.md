# CardioAI — Relatório Técnico de Escalabilidade e Otimização (Ir Além 2)
**Fase 6: Coração Sob Controle — Sistema Preditivo Multiagente**  
**Disciplina:** Otimização e Escalabilidade de Sistemas de IA (Cluster Computing)  
**Grupo:** Jonas Luis da Silva (RM561465) e Edson Henrique Felix Batista (RM566321)  
**Instituição:** FIAP — Engenharia de Software / Inteligência Artificial

---

## 1. Organização Modular Existente e Desacoplamento

A arquitetura da Fase 6 do **CardioAI** foi concebida sob os princípios de alta coesão e baixo acoplamento, viabilizando o isolamento de cada estágio analítico e assistencial:

- **Módulo Preditivo (`src/predictor.py`):** Encapsula o artefato serializado `models/modelo_pico_risco.joblib` (Random Forest treinado com 200 árvores sobre 5.000 registros sintéticos). Realiza a normalização e validação das 10 features clínico-operacionais e provê predição probabilística calibrada (`prever_risco`).
- **Motor de Protocolos Clínicos (`src/protocols.py`):** Mantém as 10 diretrizes hospitalares regulamentares da atividade e avalia deterministicamente as condições do paciente (`consultar_protocolos`), sem dependência de modelos estocásticos.
- **Sistema Multiagente (`src/agents_system/cardio_agents.py`):** Quatro agentes colaborativos especializados (Orquestrador, Analista de Risco, Especialista em Protocolos e Planejador de Resposta) orquestrados pelo **OpenAI Agents SDK** com handoffs nativos e proteção via `OutputGuardrailTripwireTriggered`.
- **Orquestração e Persistência (`src/agents_system/main.py`):** Interface CLI, persistência de sessões conversacionais via `SQLiteSession` e isolamento de contexto com `CardioContext`.

O mapeamento estrutural entre esses componentes encontra-se documentado no artefato gráfico `docs/diagrama_modulos.png`.

---

## 2. Estratégia de Simulação de Concorrência e Alta Carga

Para avaliar o comportamento do sistema diante de picos de demanda hospitalar (ex: surtos epidemiológicos ou sobrecarga em prontos-socorros), implementou-se o módulo `fila_pacientes.py`, que combina:

1. **Ingestão Assíncrona Contínua (`asyncio.Queue`):** Fila FIFO em memória alimentada por $N$ pacientes sintéticos gerados dinamicamente via `src.data_generation.gerar_base_sintetica` (com semente configurável para estrita reprodutibilidade).
2. **Pool Concorrente de $W$ Workers:** Tarefas assíncronas (`asyncio.create_task`) consumindo a fila em paralelo e invocando `Runner.run` do SDK de agentes.
3. **Controle de Resiliência Hospitalar:**
   - `asyncio.Semaphore`: Limita o número de conexões simultâneas à API para prevenir estouro de cota e rate limiting;
   - `asyncio.wait_for`: Timeout configurável por paciente (ex: 45s a 60s), evitando que requisições presas congelem a esteira;
   - **Backoff Exponencial:** Mecanismo de retry automático ($1.0 \times 2^{tentativa-1}$) diante de erros transitórios de rede ou HTTP 429;
   - **Isolamento de Falhas:** Pacientes com inconsistências graves têm o erro registrado sem interromper o processamento da fila.
4. **Modo Lote Vetorizado (`--lote`):** Processamento em batch onde todas as amostras são agregadas em um único DataFrame e submetidas simultaneamente ao método `predict_proba` do Scikit-Learn em C/BLAS, seguido da checagem em lote das diretrizes clínicas.

---

## 3. Resultados Reais do Benchmark e Identificação de Gargalos

Executou-se o script `benchmark.py` com medições empíricas salvas em `resultados/benchmark.csv` e gráficos gerados em `resultados/benchmark.png`:

| Cenário de Teste | Pacientes | Workers | Tempo Total | Latência Média | Throughput | Taxa de Erro |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila (1w) — Sem LLM** | 1.000 | 1 | 14,09 s | 14,1 ms | 70,99 pac/s | 0,0% |
| **Fila (2w) — Sem LLM** | 1.000 | 2 | 10,92 s | 21,8 ms | 91,58 pac/s | 0,0% |
| **Fila (4w) — Sem LLM** | 1.000 | 4 | 13,40 s | 53,5 ms | 74,62 pac/s | 0,0% |
| **Fila (8w) — Sem LLM** | 1.000 | 8 | 12,76 s | 101,8 ms | 78,38 pac/s | 0,0% |
| **Lote Vetorizado (Batch ML)** | **1.000** | **1** | **0,0128 s** | **< 0,1 ms** | **77.935,64 pac/s** | **0,0%** |
| **Multiagente (1w) — LLM Real** | 10 | 1 | 85,13 s | 8,51 s | 0,12 pac/s | 0,0% |
| **Multiagente (2w) — LLM Real** | 10 | 2 | 40,28 s | 7,87 s | 0,25 pac/s | 0,0% |
| **Multiagente (4w) — LLM Real** | **10** | **4** | **23,50 s** | **8,64 s** | **0,43 pac/s** | **0,0%** |

### Interpretação Crítica dos Resultados e Análise Teórico-Prática

1. **Dinâmica do Modo Sem LLM (Gargalo de CPU e o Limite do GIL):**
   - Na fila local sem LLM, a transição de 1 para 2 workers proporcionou aumento expressivo de vazão (**70,99 $\to$ 91,58 pac/s**, redução de 14,09s para 10,92s), absorvendo tempos de enfileiramento e despachos assíncronos.
   - Contudo, a expansão para 4 e 8 workers **não elevou o throughput** (estagnando em **74,62 e 78,38 pac/s**). Isso ocorre porque a inferência do Random Forest e a checagem de diretrizes são tarefas estritamente **CPU-bound**. No Python padrão (CPython), o loop de eventos `asyncio` opera sob a contenção do **Global Interpreter Lock (GIL)**. Ao instanciar mais workers concorrentes em uma única CPU, o custo de troca de contexto (*context switching*) e disputa pelo interpretador supera qualquer benefício concorrente.
   - **Solução Definitiva para ML:** Para modelos de aprendizado de máquina, a escalabilidade ótima não decorre de filas assíncronas concorrentes, mas sim do **Lote Vetorizado (Batch)**, que delega tensores e matrizes diretamente a rotinas compiladas em C/BLAS (**77.935 pac/s**), ou do uso de **multiprocessing** (`ProcessPoolExecutor` / microserviço desacoplado), permitindo paralelismo real em múltiplos núcleos de CPU sem o bloqueio do GIL.

2. **O Verdadeiro Gargalo do Sistema É a Latência Externa do LLM:**
   - A execução multiagente real exige **7,8s a 8,6s por paciente**, devido às múltiplas rodadas sequenciais de handoff (Orquestrador $\to$ Analista $\to$ Especialista $\to$ Planejador), cada qual gerando roundtrips de rede HTTP e inferência estocástica de tokens na nuvem OpenAI.
   - **Escalabilidade Concorrente Comprovada:** Ao elevar os workers de 1 para 4 no modo multiagente, o tempo total despencou de **85,13s para 23,50s** (ganho de vazão de **$3,62\times$**), confirmando que tarefas **I/O-bound** (espera de rede) se beneficiam amplamente do `asyncio` para sobrepor latências ociosas.

3. **Diagnóstico e Correção da Taxa de Erro:**
   Na primeira medição houve 10% de falha causada por um bug do próprio harness de benchmark (event loop reutilizado e fechado entre chamadas sucessivas de `asyncio.run()`, prendendo o cliente assíncrono da OpenAI ao loop anterior com a mensagem `Event loop is closed`). O bug foi corrigido executando todas as rodadas com LLM em sequência dentro de um único loop (`asyncio.run()`), e a nova medição teve **0,0% de erro** em todos os cenários (1w, 2w e 4w), com 100% dos pacientes processados com sucesso e zero bloqueios de guardrails clínicos.

---

## 4. Arquitetura Distribuída Proposta para Produção (Cluster Computing)

Para suportar operações hospitalares de alta escala, o CardioAI deve evoluir para a topologia distribuída detalhada em `docs/diagrama_distribuido.png`:

```
[Clientes: PEP / IoT / Web] ──HTTP/REST──▶ [API Gateway Stateless (FastAPI)]
                                                        │ Enqueue
                                                        ▼
                                       [Broker Distribuído: RabbitMQ / Kafka]
                                                        │ Consume (Assíncrono)
                                                        ▼
[Model Serving: Triton Batch] ◀──Inference── [Pool de Workers Multiagente (K8s)]
             │                                          │ Persistência
             ▼                                          ▼
[Cache: Redis Cluster] ───────────────────▶ [Estado & Logs: Postgres / OpenTelemetry]
```

1. **API Gateway Stateless (FastAPI + Ingress NGINX):** Recebe as requisições de prontuários eletrônicos (PEP) e monitores de leito, valida esquemas Pydantic e enfileira as mensagens assincronamente sem reter conexões abertas.
2. **Broker Distribuído de Mensagens (RabbitMQ / Apache Kafka):** Desacopla a recepção do processamento analítico. O particionamento de tópicos (`fila.pacientes.triagem`) e filas com prioridade garantem que casos críticos sejam consumidos prioritariamente, contando com Dead Letter Queue (DLQ) para reprocessamento de anomalias.
3. **Workers em Containers Kubernetes com Autoscaling (HPA):** O Horizontal Pod Autoscaler monitora o comprimento da fila de mensagens (via KEDA) e a utilização de CPU, provisionando pods adicionais de forma elástica durante picos de triagem e reduzindo custos em períodos de calmaria.
4. **Model Serving Desacoplado (Triton / TorchServe):** O modelo Random Forest é servido em microserviço dedicado otimizado com batching dinâmico. Os workers de agentes consultam o modelo via gRPC de baixa latência em vez de carregar pesos localmente em cada pod.
5. **Camada de Cache de Predições (Redis Cluster):** Armazena hashes de sinais vitais de monitoramento contínuo (TTL de 60 segundos), retornando probabilidades cacheadas instantaneamente para pacientes com parâmetros estáveis.
6. **Sessões Compartilhadas:** Substituição do `SQLiteSession` local por PostgreSQL e Redis Cluster, viabilizando persistência transacional ACID de conversas e histórico de follow-up acessível por qualquer worker do cluster.
7. **Observabilidade Unificada:** Métricas de throughput e tempo de fila via Prometheus e Grafana, distributed tracing com OpenTelemetry e Jaeger para auditar cada handoff entre agentes, e logs estruturados centralizados no Elasticsearch.
