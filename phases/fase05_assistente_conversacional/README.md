# Fase 5 — Assistente Cardiológico Conversacional

Esta fase introduz um assistente conversacional (chatbot) no contexto do **CardioAI**, projetado para triagem inicial de sintomas, agendamentos e esclarecimento de dúvidas sobre ECG.

A solução integra o **IBM watsonx Assistant** a um backend **Flask**, que por sua vez se conecta ao frontend React desenvolvido nas fases anteriores.

## Componentes

1. **watson/skill-cardioia.json**: Export oficial do modelo de diálogo do Watson Assistant (Intents, Entities e Dialog Nodes).
2. **src/app.py**: Backend Flask que serve os endpoints `/chat`, `/chat/session` e `/chat/session/close`, integrando com a API do Watson via SDK oficial. Possui log em SQLite com rastreamento por sessão.
3. **src/session_manager.py**: Gerenciador de sessões individuais do Watson Assistant com suporte a expiração (TTL), auto-recuperação de sessões expiradas (404 / Invalid Session) e encerramento explícito (`delete_session`).
4. **src/intent_engine.py**: Motor de regras local para atuar como *fallback* caso a API do Watson falhe ou não possua credenciais configuradas.
5. **reports/**: Relatório técnico descrevendo o fluxo conversacional e as decisões de modelagem.

## Como Executar (Backend)

### 1. Preparar Ambiente

Navegue até a pasta desta fase e ative o ambiente virtual:

```bash
cd phases/fase05_assistente_conversacional
python -m venv .venv
.venv\Scripts\activate  # No Windows
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo `.env.example` para `.env`:

```bash
copy .env.example .env   # No Windows (cmd)
# ou cp .env.example .env (PowerShell / Linux)
```

Configure as variáveis de ambiente necessárias:

```env
# Watson Assistant
WATSONX_ASSISTANT_APIKEY=sua-api-key
WATSONX_ASSISTANT_URL=sua-url-do-servico
WATSONX_ASSISTANT_ID=seu-assistant-id
WATSONX_ASSISTANT_VERSION=2023-06-15

# Configurações do Servidor Backend
PORT=5001
HOST=0.0.0.0
FLASK_DEBUG=True
CORS_ORIGINS=*

# Gerenciamento de Sessão Individual (TTL em segundos)
SESSION_TTL_SECONDS=1800
```

Se o `.env` não for fornecido ou as credenciais forem inválidas, o backend iniciará automaticamente no **Modo Fallback Local**, garantindo que a demonstração funcione independentemente da conexão externa.

### 3. Iniciar o Servidor

```bash
python src/app.py
```

O servidor iniciará na porta configurada em `PORT` (padrão `5001`). A interface de chat (localizada no portal React) se comunicará com este serviço.

## Ciclo de Vida e Gerenciamento de Sessão

- **Sessões Individuais:** Cada cliente mantém seu próprio identificador de sessão (`session_id`). Não há compartilhamento global de sessão entre usuários.
- **Tratamento de Expiração:** Quando uma sessão expira no Watson Assistant (erro 404 / Invalid Session) ou localmente por inatividade (TTL), o backend detecta a expiração automaticamente, cria uma nova sessão, reprocessa a mensagem e devolve o novo `session_id` ao frontend.
- **Encerramento Explícito:** O frontend ou consumidor da API pode chamar `POST /chat/session/close` enviando `{ "session_id": "..." }` para liberar os recursos da sessão na nuvem IBM.

## Integração com a Fase 4

O assistente foi desenhado para entender a entidade `@classe_ecg` (F, N, Q, S, V). Quando um usuário questiona sobre o significado de uma classe detectada no seu exame, o backend consulta o arquivo `class_names.json` gerado pelo modelo da Fase 4 para garantir consistência da informação fornecida.

---

## 🛠️ Correções Pós-Feedback da Banca / Professor

Em resposta aos apontamentos sobre o skill em nó único, sessão única compartilhada, componentes duplicados no frontend, simulação no IR ALÉM 1 e limiares fixos no IR ALÉM 2, foram implementadas as seguintes melhorias:

### 1. Sessão Individualizada e Portal Unificado
- **Backend (`src/session_manager.py`):** Cada usuário/aba recebe seu próprio `session_id` mantido individualmente em memória e sincronizado com o Watson Assistant, incluindo tratamento de expiração (404 / TTL) e encerramento explícito (`delete_session`).
- **Frontend Portal (`apps/portal-cardioia/`):** Os dois componentes duplicados foram unificados em um único componente modular [`ChatAssistente.jsx`](../../apps/portal-cardioia/src/components/ChatAssistente.jsx), consumindo a URL do backend centralizada em [`src/config.js`](../../apps/portal-cardioia/src/config.js) (`VITE_BACKEND_URL`).
- **Evidência Comprobatória:** Captura demonstrando duas abas operando simultaneamente com sessões independentes do Watson (`b4b3bdf1...` e `3fc7ca10...`) salva em [`evidencias/sessoes_separadas.png`](evidencias/sessoes_separadas.png).

### 2. IR ALÉM 1: Extração Clínica com IA Generativa Real
- **Eliminação de Mocks:** Removida do notebook [`extracao_informacoes_clinicas.ipynb`](ir_alem_1_extracao_clinica/extracao_informacoes_clinicas.ipynb) qualquer simulação local.
- **Chamadas Reais:** O notebook importa e utiliza [`integracao_llm_ecg.py`](ir_alem_1_extracao_clinica/integracao_llm_ecg.py), realizando chamadas reais à API da OpenAI (`gpt-4o-mini`) com Structured Outputs (Pydantic `ExtracaoClinica`) e geração diagnóstica humanizada para o laudo de ECG.
- **Governança:** Sem a chave `OPENAI_API_KEY` (configurada via `.env` ou Colab Secrets), a execução é abortada com erro claro, sem jamais simular dados clínicos. Todas as células foram executadas com a chave ativa e suas saídas reais encontram-se persistidas no notebook.

### 3. IR ALÉM 2: Machine Learning e Persistência NoSQL Real
- **Modelo Supervisionado (`modelo_risco.joblib`):** Substituição de limiares manuais fixos por classificador Random Forest calibrado com variáveis hemodinâmicas avançadas (PAM, Pressão de Pulso, Índice de Choque e Duplo Produto).
- **Log Transparente e Conexão NoSQL Real:** O robô [`robo_monitoramento.py`](ir_alem_2_rpa_dados_hibridos/robo_monitoramento.py) emite logs explícitos indicando `[NoSQL - MONGODB REAL]` vs. `[NoSQL - FALLBACK LOCAL]`.
- **Evidências de Execução e Consulta NoSQL:**
  - Log completo de execução com MongoDB Atlas Real: [`evidencias/execucao_mongo_real.log`](evidencias/execucao_mongo_real.log).
  - Script e resultado de consulta (equivalente `mongosh` com contagem e documentos BSON/JSON): [`evidencias/consulta_mongo.py`](evidencias/consulta_mongo.py) e [`evidencias/consulta_mongo.txt`](evidencias/consulta_mongo.txt).
- **Relatório Técnico:** Atualizado em [`relatorio-tecnico-ir-alem-2.md`](ir_alem_2_rpa_dados_hibridos/relatorio-tecnico-ir-alem-2.md) (Seção 3.4) documentando abertamente como limitação o fato de o modelo ter sido treinado com base sintética rotulada por regras clínicas da SBC/SBH, recomendando retreinamento futuro com prontuários reais desidentificados (MIMIC-IV / PhysioNet).

### 4. Watson Assistant: Redesenho do Skill com Perguntas de Continuidade
- Elaborado documento de especificação técnica [`docs/watson_fluxo_continuidade.md`](docs/watson_fluxo_continuidade.md) detalhando os novos fluxos guiados (*multi-turn*) com slots, steps e variáveis de contexto:
  - *Sintomas:* sintoma inicial → tempo de duração → intensidade (0 a 10) → sinais de alarme (*red flags*) → conduta estratificada (emergência vs. ambulatorial);
  - *ECG:* classe identificada na Fase 4 (N, S, V, F, Q) → explicação humanizada da eletrofisiologia → histórico do paciente → próximo passo;
  - *Agendamento:* motivo → período preferencial → confirmação no Portal CardioAI.

---

⚠️ **AVISO:** Este assistente é um protótipo acadêmico. Todas as respostas possuem avisos de isenção de responsabilidade médica e fluxos de emergência direcionam o usuário para o telefone 192.

