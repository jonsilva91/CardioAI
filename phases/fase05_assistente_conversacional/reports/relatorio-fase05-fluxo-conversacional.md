# Relatório Técnico - Fase 5: Assistente Conversacional

**CardioAI - FIAP 2026**

## 1. Objetivo

Este relatório documenta a concepção, modelagem e integração de um assistente conversacional focado no atendimento inicial em saúde (área cardiológica). O assistente foi desenhado para simular triagem de sintomas, fornecer informações sobre agendamentos e esclarecer dúvidas básicas sobre ECG, com forte ênfase na segurança do paciente (encaminhamento de emergências e disclaimer não-diagnóstico).

## 2. Experiência de Modelagem (Watson Assistant)

Foi utilizada a experiência **clássica de Dialog** do IBM watsonx Assistant (Intents, Entities e Dialog Nodes). O fluxo completo foi construído utilizando os recursos tradicionais da plataforma e exportado no formato JSON padrão da ferramenta.

**Justificativa:** A modelagem clássica por Dialog Nodes permite controle explícito do fluxo de conversação e tratamento determinístico de exceções, como a interceptação de situações de emergência (onde a ramificação condicional tradicional é altamente eficaz e previsível).

## 3. Modelo Cognitivo (Intents e Entities)

O assistente foi treinado com os seguintes elementos cognitivos, visando cobrir o fluxo de atendimento inicial:

### 3.1 Intents (Intenções)

1. `#saudacao`: Identifica cumprimentos e aberturas de diálogo (ex.: "olá", "bom dia").
2. `#sintomas_cardiacos`: Captura relatos de desconforto físico relacionados ao sistema cardiovascular (ex.: "dor no peito", "palpitação", "tontura").
3. `#agendamento_consulta`: Identifica a intenção do usuário de marcar ou remarcar uma consulta.
4. `#duvida_ecg`: Detecta perguntas sobre resultados de exames ou termos técnicos (ex.: "o que é classe F?", "arritmia ventricular").
5. `#emergencia`: Intent crítica para capturar sinais de gravidade aguda (ex.: "dor muito forte", "não consigo respirar", "enfartando").
6. `#despedida`: Encerramentos de conversa.
7. `anything_else` (Fallback): Tratamento para intenções não reconhecidas.

### 3.2 Entities (Entidades)

1. `@sintoma`: Extrai o tipo específico de sintoma relatado. Valores principais e sinônimos:
   - `dor_peito` ("aperto no peito", "peito doendo")
   - `palpitacao` ("coração acelerado", "taquicardia")
   - `falta_de_ar` ("respiração curta", "dispneia")

2. `@classe_ecg`: Entidade integrada com a Fase 4 do projeto, mapeando as classes do classificador CNN:
   - `F` ("fusão")
   - `N` ("normal")
   - `Q` ("não classificável")
   - `S` ("supraventricular")
   - `V` ("ventricular")

## 4. Estrutura do Fluxo de Diálogo (Dialog Nodes)

O fluxo de conversa foi estruturado para priorizar a segurança clínica:

1. **Bem-vindo:** Ao iniciar o chat, o bot saúda e apresenta um **aviso de não-diagnóstico**.
2. **Node de Emergência (Prioridade Alta):** Se o intent `#emergencia` é detectado em qualquer momento da conversa, o fluxo é desviado imediatamente para uma instrução clara de acionamento do SAMU (192) ou busca de pronto-socorro.
3. **Triagem de Sintomas:** Captura `#sintomas_cardiacos` e, caso a entidade `@sintoma` esteja presente, contextualiza a resposta recomendando agendamento médico.
4. **Integração ECG:** O node `#duvida_ecg` se propõe a buscar informações dinâmicas (no backend) sobre a classe solicitada.
5. **Fallback:** Mensagem orientadora informando as capacidades do bot caso o usuário saia do escopo.

## 5. Arquitetura de Integração

O assistente foi integrado a um backend em Flask (`src/app.py`):

1. **Endpoint REST:** O aplicativo web (React) comunica-se com a rota `POST /chat`.
2. **Integração com SDK IBM:** A comunicação com o Watson Assistant ocorre através da biblioteca oficial `ibm-watson` (autenticação IAM via variáveis de ambiente).
3. **Motor Local de Fallback:** Como mecanismo de contingência para falhas de rede ou expiração de credenciais do Watson, foi desenvolvido um `intent_engine.py` baseado em expressões regulares (RegEx). Ele espelha as capacidades do Watson localmente para garantir a demonstrabilidade contínua do protótipo.
4. **Integração com Fase 4:** O backend Flask intercepta dúvidas sobre ECG e anexa dinamicamente as classes suportadas pela CNN (lendo de `class_names.json`), conectando o chatbot ao módulo de Visão Computacional.

## 6. Tratamento de Exceções e Segurança Clínica

- **Desvio de Emergência:** O bot jamais fornece aconselhamento diante de sintomas graves.
- **Log Persistente:** Todas as interações são salvas em um banco SQLite (`conversation_log.db`), garantindo rastreabilidade para auditorias ou processos subsequentes (como o módulo RPA do IR ALÉM 2).

## 7. Limitações

- **Ambiente Restrito:** O chatbot foi treinado para um escopo estreito. Perguntas fora da cardiologia básica cairão no fallback.
- **NLP Determinística:** O modelo clássico do Watson requer alto volume de *utterances* (frases de exemplo) para generalizar perfeitamente, algo restrito neste protótipo acadêmico.
- **Integração Simétrica:** A extração clínica aprofundada depende de modelos generativos (LLMs), implementados como etapa avançada no módulo "IR ALÉM 1".
