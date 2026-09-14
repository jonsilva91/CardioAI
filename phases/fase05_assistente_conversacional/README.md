# Fase 5 — Assistente Cardiológico Conversacional

Esta fase introduz um assistente conversacional (chatbot) no contexto do **CardioAI**, projetado para triagem inicial de sintomas, agendamentos e esclarecimento de dúvidas sobre ECG.

A solução integra o **IBM watsonx Assistant** a um backend **Flask**, que por sua vez se conecta ao frontend React desenvolvido nas fases anteriores.

## Componentes

1. **watson/skill-cardioia.json**: Export oficial do modelo de diálogo do Watson Assistant (Intents, Entities e Dialog Nodes).
2. **src/app.py**: Backend Flask que serve o endpoint `/chat`, integrando com a API do Watson via SDK oficial. Possui log em SQLite.
3. **src/intent_engine.py**: Motor de regras local para atuar como *fallback* caso a API do Watson falhe ou não possua credenciais configuradas.
4. **reports/**: Relatório técnico descrevendo o fluxo conversacional e as decisões de modelagem.

## Como Executar (Backend)

### 1. Preparar Ambiente

Navegue até a pasta desta fase e crie um ambiente virtual:

```bash
cd phases/fase05_assistente_conversacional
python -m venv .venv
.venv\Scripts\activate  # No Windows
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente (Opcional)

Para utilizar o Watson Assistant real, crie um arquivo `.env` na raiz da `fase05_assistente_conversacional` com:

```env
WATSONX_ASSISTANT_APIKEY=sua-api-key
WATSONX_ASSISTANT_URL=sua-url-do-servico
WATSONX_ASSISTANT_ID=seu-assistant-id
```

Se o `.env` não for fornecido, o backend iniciará automaticamente no **Modo Fallback Local**, garantindo que a demonstração funcione independentemente da conexão externa.

### 3. Iniciar o Servidor

```bash
python src/app.py
```

O servidor iniciará na porta `5001`. A interface de chat (localizada no portal React) se comunicará com este serviço.

## Integração com a Fase 4

O assistente foi desenhado para entender a entidade `@classe_ecg` (F, N, Q, S, V). Quando um usuário questiona sobre o significado de uma classe detectada no seu exame, o backend consulta o arquivo `class_names.json` gerado pelo modelo da Fase 4 para garantir consistência da informação fornecida.

⚠️ **AVISO:** Este assistente é um protótipo acadêmico. Todas as respostas possuem avisos de isenção de responsabilidade médica e fluxos de emergência direcionam o usuário para o telefone 192.
