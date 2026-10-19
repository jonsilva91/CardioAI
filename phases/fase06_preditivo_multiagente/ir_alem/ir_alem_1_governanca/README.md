# CardioAI — Ir Além 1: Governança, Rastreabilidade e Auditoria em IA Médica

**Fase 6: Coração Sob Controle — Sistema Preditivo Multiagente**  
**Disciplina:** Governança, Boas Práticas e Arquitetura de IA (GBA)  
**Grupo:** Jonas Luis da Silva (RM561465) e Edson Henrique Felix Batista (RM566321)  
**Instituição:** FIAP — Engenharia de Software / Inteligência Artificial

---

## 🎯 Objetivo da Atividade

Implementar uma camada completa e contínua de **governança, integridade clínica e auditoria automatizada** para as decisões do sistema multiagente hospitalar **CardioAI**, **SEM duplicar código ou regras**.

Os componentes importam diretamente os módulos centrais da Fase 6:
- `src.predictor`: inferência preditiva e carregamento do modelo;
- `src.protocols`: base oficial dos 10 protocolos e motor determinístico de regras;
- `src.config`: limiares de classificação de risco e parametrizações globais;
- `src.agents_system.cardio_agents`: instanciação do quarteto colaborativo de agentes do OpenAI Agents SDK.

---

## 🏗️ Estrutura de Arquivos

```
phases/fase06_preditivo_multiagente/ir_alem/ir_alem_1_governanca/
├── README.md                      # Documentação completa, guia de execução e arquitetura
├── audit_logger.py                # Logger append-only (JSONL) com AuditRunHooks e extração de .joblib
├── coherence_validator.py         # Validador determinístico de coerência clínica (regras A, B, C e D)
├── run_auditado.py                # Execução auditada real com LLM (3 casos + teste de adulteração)
├── consultar_auditoria.py         # Ferramenta CLI de consulta, filtragem e inspeção detalhada
├── gerar_pdf_governanca.py        # Script ReportLab gerador do relatório técnico (máx. 2 páginas)
├── relatorio_ir_alem_1.md         # Relatório técnico completo de governança e bioética
├── relatorio_ir_alem_1.pdf        # PDF compilado de exatamente 2 páginas (validado via pypdfium2)
├── logs/
│   └── decisoes.jsonl             # Log append-only de produção (ignorado no git)
├── evidencias/
│   ├── evidencia_log.jsonl        # Trecho REAL autenticado do log de decisões (versionado)
│   └── evidencia_execucao.png     # Screenshot em alta resolução do terminal de execução
└── tests/
    └── test_coherence.py          # Suíte de 9 testes unitários (100% offline, sem chamadas a APIs)
```

---

## 🚀 Como Executar

### 1. Pré-requisitos e Configuração de Ambiente

A partir da raiz do repositório CardioAI, garanta que as dependências estejam instaladas e a chave `OPENAI_API_KEY` esteja presente no arquivo `.env` da Fase 6 (`phases/fase06_preditivo_multiagente/.env`):

```bash
cd phases/fase06_preditivo_multiagente
pip install -r requirements.txt
```

### 2. Execução Auditada Completa (com LLM Real)

Executa o pipeline multiagente para os três pacientes de teste (`novo_caso.json`, `caso_baixo_risco.json`, `caso_moderado_risco.json`) e adiciona um quarto caso demonstrativo de detecção de adulteração:

```bash
# Executado a partir da pasta ir_alem_1_governanca:
python run_auditado.py

# Ou a partir da raiz do repositório:
python phases/fase06_preditivo_multiagente/ir_alem/ir_alem_1_governanca/run_auditado.py
```

**Saída esperada no terminal:**
```
========================================================================================================================
📊 RESUMO CONSOLIDADO DA AUDITORIA MULTIAGENTE — CARDIOAI
========================================================================================================================
CASO                         | PROB  | CLASSE   | PROTOCOLOS | COERÊNCIA    | GUARDRAIL  | HANDOFFS | TOOLS
------------------------------------------------------------------------------------------------------------------------
1. Novo Caso (Alto Risco)    | 0.99  | ALTO     | 4 regras   | COERENTE ✅   | APROVADO   | 3 etapas | 2    
2. Caso Baixo Risco          | 0.00  | BAIXO    | 0 regras   | COERENTE ✅   | APROVADO   | 3 etapas | 2    
3. Caso Moderado Risco       | 0.59  | MODERADO | 0 regras   | COERENTE ✅   | APROVADO   | 3 etapas | 2    
Teste Adulteração (novo_caso) | 0.99  | ALTO     | 5 regras   | REPROVADO ❌  | REPROVADO  | 3 etapas | 2    
========================================================================================================================
```

### 3. Consulta e Filtragem de Decisões Auditadas (CLI)

O utilitário `consultar_auditoria.py` lê `logs/decisoes.jsonl` e permite inspeções forenses no histórico de decisões:

```bash
# Listagem geral resumida de todas as decisões
python consultar_auditoria.py

# Filtrar exclusivamente decisões incoerentes ou adulteradas com detalhes expandidos:
python consultar_auditoria.py --incoerentes --detalhes

# Filtrar por classificação de risco (BAIXO, MODERADO ou ALTO):
python consultar_auditoria.py --classificacao MODERADO

# Filtrar por session_id específico:
python consultar_auditoria.py --session-id audit_novo_caso
```

### 4. Execução da Suíte de Testes Unitários

Executa os 9 testes unitários de coerência (cenários coerentes, omissão de conduta, protocolo indevido, divergência score/classe, regra biunívoca de risco sistêmico e adulteração):

```bash
pytest tests/test_coherence.py -v
```

### 5. Compilação do Relatório Técnico em PDF

Gera o relatório em PDF com exatamente 2 páginas e valida a contagem via `pypdfium2`:

```bash
python gerar_pdf_governanca.py
```

---

## 🔍 Exemplo Real de Registro de Auditoria (`decisoes.jsonl`)

Abaixo é apresentado um registro real gerado pelo sistema durante a execução auditada (`a7d58a73-b0fa-40df-b99a-864587987470`):

```json
{
  "id_decisao": "a7d58a73-b0fa-40df-b99a-864587987470",
  "timestamp": "2026-10-15T20:33:57.303750+00:00",
  "session_id": "audit_novo_caso_9a5a85",
  "hash_dados_entrada": "3a89b22083c1a61063685a2893ee076f37a96faf86a40ab16c682d951b6c1ab8",
  "dados_paciente": {
    "idade_media": 62.0,
    "carga_sistema": 92.0,
    "tempo_espera": 75.0,
    "fc_media": 118.0,
    "spo2_media": 89.0,
    "pa_sistolica": 100.0,
    "temperatura": 37.5,
    "densidade_eventos": 7.0,
    "eventos_24h": 5.0,
    "disponibilidade_recursos": 25.0
  },
  "modelo_preditivo": {
    "nome": "RandomForestClassifier",
    "versao_sklearn": "1.9.0",
    "data_treinamento": "2026-10-15T14:14:15.310191",
    "features": [
      "idade_media", "carga_sistema", "tempo_espera", "fc_media", "spo2_media",
      "pa_sistolica", "temperatura", "densidade_eventos", "eventos_24h", "disponibilidade_recursos"
    ],
    "metricas": {
      "accuracy": 0.999,
      "f1_score_classe_1": 0.9981167608286252,
      "recall_classe_1": 0.9962406015037594,
      "precision_classe_1": 1.0,
      "cv_accuracy_mean": 0.9978,
      "cv_f1_mean": 0.9958426015566413
    }
  },
  "modelo_llm": "gpt-4o-mini",
  "probabilidade": 0.99,
  "classificacao": "ALTO",
  "protocolos_sugeridos": [
    "Se carga do sistema > 85% → abrir unidades temporárias",
    "Se disponibilidade_recursos < 30% → redistribuir insumos",
    "Se densidade_eventos > 6 → ativar plano de contingência",
    "Se risco sistêmico alto → ativar estado de emergência"
  ],
  "sequencia_handoffs": [
    {"de": "Agente Orquestrador", "para": "Agente Analista de Risco", "timestamp": "2026-10-15T20:33:44.061792+00:00"},
    {"de": "Agente Analista de Risco", "para": "Agente Especialista em Protocolos", "timestamp": "2026-10-15T20:33:49.426168+00:00"},
    {"de": "Agente Especialista em Protocolos", "para": "Agente Planejador de Resposta", "timestamp": "2026-10-15T20:33:52.166106+00:00"}
  ],
  "agentes_percorridos": [
    "Agente Orquestrador",
    "Agente Analista de Risco",
    "Agente Especialista em Protocolos",
    "Agente Planejador de Resposta"
  ],
  "tools_chamadas": [
    {
      "agente": "Agente Analista de Risco",
      "tool": "prever_risco_paciente",
      "timestamp_inicio": "2026-10-15T20:33:45.230802+00:00",
      "status": "concluido",
      "timestamp_fim": "2026-10-15T20:33:48.224817+00:00",
      "resultado": "{\"probabilidade\": 0.99, \"classe_prevista\": 1, \"classificacao\": \"ALTO\"}"
    },
    {
      "agente": "Agente Especialista em Protocolos",
      "tool": "consultar_base_protocolos",
      "timestamp_inicio": "2026-10-15T20:33:50.869827+00:00",
      "status": "concluido",
      "timestamp_fim": "2026-10-15T20:33:50.869827+00:00",
      "resultado": "[{\"id\": \"PROT-02\", \"texto\": \"Se carga do sistema > 85% → abrir unidades temporárias\", ...}, ...]"
    }
  ],
  "validacao_coerencia": {
    "coerente": true,
    "inconsistencias": []
  },
  "guardrail_status": "aprovado",
  "acoes_operacionais": [
    "Aumentar equipe de enfermagem para suporte imediato.",
    "Revisar e redistribuir leitos disponíveis.",
    "Ativar triagem preferencial para novos pacientes.",
    "Implementar comunicação contínua entre as equipes."
  ],
  "justificativa": "A alta probabilidade de 99% indica um pico de risco cardiovascular. Com a carga do sistema em 92% e a densidade de eventos em 7, a ativação de protocolos é crítica para evitar colapso...",
  "aviso": "A utilização desta análise deve ser feita de acordo com as normas de ética e regulatórias vigentes.",
  "teste_adulteracao": false
}
```

---

## 📺 Demonstração em Vídeo

- **Link no YouTube (Não Listado):** [https://youtu.be/mperrwkEUbA](https://youtu.be/mperrwkEUbA)
- **Duração máxima:** 4 minutos
- **Conteúdo abordado:**
  1. Demonstração da execução de `run_auditado.py` no terminal;
  2. Apresentação da captura de handoffs e tools via `AuditRunHooks`;
  3. Reprovação instantânea no teste controlado de adulteração;
  4. Consulta e filtragem com `consultar_auditoria.py`;
  5. Explicação dos pilares de governança em saúde (LGPD, explicabilidade e human-in-the-loop).
