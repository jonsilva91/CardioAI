# CardioAI — Relatório Técnico de Governança e Auditoria (Ir Além 1)
**Fase 6: Coração Sob Controle — Sistema Preditivo Multiagente**  
**Disciplina:** Governança, Boas Práticas e Arquitetura de IA (GBA)  
**Grupo:** Jonas Luis da Silva (RM561465) e Edson Henrique Felix Batista (RM566321)  
**Instituição:** FIAP — Engenharia de Software / Inteligência Artificial

---

## 1. Visão Geral e Registro Estruturado de Decisões

Em aplicações de Inteligência Artificial voltadas à saúde, a confiabilidade operacional depende de mecanismos rigorosos de governança, rastreabilidade e integridade regulamentar. Para atender a essas diretrizes, a camada **Ir Além 1** do sistema **CardioAI** implementa um pipeline append-only de auditoria contínua, persistindo cada deliberação clínica em `logs/decisoes.jsonl`.

Diferentemente de soluções baseadas em parsing frágil de strings de terminal, a telemetria do CardioAI é capturada de forma nativa por meio da classe `AuditRunHooks`, derivada de `RunHooks` do **OpenAI Agents SDK**. A classe intercepta os eventos assíncronos do orquestrador (`on_agent_start`, `on_handoff`, `on_tool_start`, `on_tool_end`), garantindo o registro exato da sequência de agentes percorridos e ferramentas invocadas.

### Registro Real Auditado em Produção (`decisoes.jsonl` — Linha 1)

```json
{
  "id_decisao": "a7d58a73-b0fa-40df-b99a-864587987470",
  "timestamp": "2026-10-15T20:33:57.303750+00:00",
  "session_id": "audit_novo_caso_9a5a85",
  "hash_dados_entrada": "3a89b22083c1a61063685a2893ee076f37a96faf86a40ab16c682d951b6c1ab8",
  "dados_paciente": {
    "idade_media": 62.0, "carga_sistema": 92.0, "tempo_espera": 75.0, "fc_media": 118.0,
    "spo2_media": 89.0, "pa_sistolica": 100.0, "temperatura": 37.5, "densidade_eventos": 7.0,
    "eventos_24h": 5.0, "disponibilidade_recursos": 25.0
  },
  "modelo_preditivo": {
    "nome": "RandomForestClassifier", "versao_sklearn": "1.9.0", "data_treinamento": "2026-10-15T14:14:15.310191",
    "metricas": {"accuracy": 0.999, "f1_score_classe_1": 0.9981, "recall_classe_1": 0.9962, "precision_classe_1": 1.0}
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
    {"de": "Agente Orquestrador", "para": "Agente Analista de Risco"},
    {"de": "Agente Analista de Risco", "para": "Agente Especialista em Protocolos"},
    {"de": "Agente Especialista em Protocolos", "para": "Agente Planejador de Resposta"}
  ],
  "tools_chamadas": [
    {"agente": "Agente Analista de Risco", "tool": "prever_risco_paciente", "status": "concluido"},
    {"agente": "Agente Especialista em Protocolos", "tool": "consultar_base_protocolos", "status": "concluido"}
  ],
  "validacao_coerencia": {"coerente": true, "inconsistencias": []},
  "guardrail_status": "aprovado"
}
```

---

## 2. Validação Determinística de Coerência Clínica

Para impedir alucinações de conduta e desvios de conduta hospitalar, o módulo `coherence_validator.py` estabelece quatro barreiras de checagem clínica sem duplicação de regras, importando deterministicamente as diretrizes de `src/protocols.py` e os limiares de `src/config.py`:

1. **Regra A (Validação de Parâmetros Críticos):** Cada protocolo sugerido pelo agente é inspecionado contra os sinais vitais reais. Se um protocolo for sugerido sem que a variável correspondente tenha violado o limiar, a decisão é reprovada.
2. **Regra B (Prevenção de Omissão de Conduta):** Se os dados do paciente atingem o critério de ativação de uma diretriz oficial, o validador exige sua presença mandatória na recomendação, impedindo omissão assistencial.
3. **Regra C (Conformidade de Limiares):** A probabilidade inferida pelo modelo preditivo é confrontada com a função `classificar_risco` de `src/config.py` (< 0.30 BAIXO, 0.30–0.70 MODERADO, > 0.70 ALTO).
4. **Regra D (Biunivocidade de Emergência Sistêmica):** A classificação ALTO exige estritamente a ativação de `Se risco sistêmico alto → ativar estado de emergência`; para as classes BAIXO e MODERADO, a presença dessa diretriz constitui violação de governança.

### Demonstração de Reprovação em Teste Controlado de Adulteração

No arquivo `run_auditado.py`, injetou-se fraudulentamente o protocolo de oxigenoterapia (`Se SPO2 < 88% → iniciar suporte respiratório imediato`) na recomendação do paciente de alto risco, cujos dados reais indicavam SpO2 de 89.0%. O validador reprovou imediatamente a decisão:
```
[TESTE DE ADULTERAÇÃO CONTROLADO]
* Detecção: Protocolo indevido (Regra A): 'Se SPO2 < 88% → iniciar suporte respiratório imediato' 
  foi sugerido, mas os dados vitais do paciente não atingem o limiar de acionamento.
Resultado da Auditoria: REPROVADO COM SUCESSO (guardrail_status: reprovado_por_coerencia)
```

---

## 3. Rastreabilidade Criptográfica e Versionamento de Modelos

A trilha de auditoria do CardioAI garante o non-repudiation e a reprodutibilidade técnico-científica das decisões:
- **Hash Criptográfico de Entrada (SHA-256):** As 10 features do paciente são convertidas em JSON canônico ordenado por chaves e hasheadas via SHA-256 (`hash_dados_entrada`). Qualquer alteração posterior em um único sinal vital invalida a correspondência criptográfica da decisão.
- **Metadados do Modelo ML (.joblib):** A função `obter_metadados_modelo()` de `audit_logger.py` extrai diretamente do arquivo binário `models/modelo_pico_risco.joblib` a versão do Scikit-Learn (1.9.0), data de treinamento (`trained_at`) e métricas de generalização (Acurácia: 99,9%, F1-Score: 0,9981, Recall: 99,62%).
- **Sessões Isoladas e Persistentes:** O rastreamento utiliza `SQLiteSession`, associando cada execução a um identificador exclusivo para inspeção detalhada via `consultar_auditoria.py`.

---

## 4. Princípios de Governança em Saúde e Mapeamento no Código

A tabela a seguir evidencia como os pilares éticos e regulatórios de IA médica foram materializados na arquitetura:

| Princípio de Governança | Exigência Regulamentar em Saúde | Implementação Concreta no Repositório CardioAI |
| :--- | :--- | :--- |
| **Explicabilidade** | O profissional de saúde deve compreender a lógica das recomendações emitidas. | `coherence_validator.py` valida justificativas ancoradas nas variáveis do paciente; `cardio_agents.py` instrui o Planejador a detalhar os sinais vitais críticos. |
| **Accountability** | Responsabilização clara, rastreando quem decidiu, quando e através de quais etapas. | `audit_logger.py` (via `AuditRunHooks`) registra a sequência exata de agentes (`handoffs`), tools acionadas, UUID da decisão e carimbo temporal ISO-8601. |
| **LGPD e Minimização** | Tratamento restrito de dados sensíveis e proteção contra vazamentos de privacidade. | `data_generation.py` gera bases exclusivamente sintéticas parametrizadas; apenas 10 features clínico-operacionais estritamente necessárias são trafegadas. |
| **Humano no Loop (HITL)** | A IA não deve tomar condutas autônomas nem substituir o julgamento clínico. | Guardrail e avisos mandatórios em `schemas.py` e `guardrails.py` reforçam que o sistema atua como suporte analítico de risco, sem emitir diagnósticos médicos. |
