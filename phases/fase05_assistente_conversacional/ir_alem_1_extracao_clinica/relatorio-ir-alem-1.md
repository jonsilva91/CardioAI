# IR ALÉM 1 - Extração de Informações Clínicas com LLM

**CardioAI - Fase 5**
**Autor:** Jonas Luis da Silva (simulado)

## 1. Objetivo

Este relatório documenta a estratégia de extração de informações estruturadas (JSON) a partir de relatos clínicos não estruturados (texto livre), utilizando Modelos de Linguagem de Grande Escala (LLM). O objetivo principal é demonstrar como o Processamento de Linguagem Natural avançado pode aprimorar a triagem inicial feita pelo Assistente Conversacional (Fase 5) e fornecer *insights* antecipados que se conectam com o Classificador de ECG (Fase 4).

## 2. Estratégia de Prompt Engineering

Foi desenvolvida uma estrutura de prompt (System Prompt) rigorosa, utilizando Pydantic para garantir que a saída do LLM obedeça a um *schema* predefinido. 

O prompt obriga o modelo a atuar como um cardiologista e a extrair cinco dimensões principais:
1. Sintomas (lista)
2. Duração
3. Intensidade
4. Fatores de risco (lista)
5. Urgência (baixa/média/alta)
6. Classe de ECG provável (F, N, Q, S, V)

### 2.1 Integração com o Repositório Real (Fase 4 e Fase 5)

A grande inovação desta etapa é a **amarração com os artefatos existentes**:

* **Integração Fase 5 (Watson):** A extração do nível de urgência (`"urgencia": "alta"`) permite um roteamento dinâmico. Em vez de depender apenas do Intent `#emergencia` do Watson (que pode falhar se a frase for muito atípica), o LLM avalia a semântica profunda do relato e pode forçar a ativação do Dialog Node de emergência, recomendando o SAMU (192).
* **Integração Fase 4 (CNN):** O LLM foi instruído sobre as classes do modelo treinado na Fase 4. Se o paciente relata "palpitação e taquicardia", o LLM preenche `classe_ecg_provavel` como **S** (Supraventricular). Quando esse paciente fizer o exame físico de ECG, o sistema já possui uma priorização (triagem) indicando que o médico deve buscar por padrões da classe S.

## 3. Integração Real de API com LLM (OpenAI 'gpt-4o-mini' / Gemini)

Para elevar a arquitetura ao nível de produção, a simulação estática foi substituída por uma integração completa com APIs de LLM via SDK oficial, com suporte nativo a `gpt-4o-mini` e alternativa para Google Gemini.

### 3.1 Carregamento Seguro de Credenciais (.env)
A chave de acesso é gerenciada por meio de variáveis de ambiente (`python-dotenv`), prevenindo vazamento acidental em repositórios:
- Leitura dinâmica com `load_dotenv(find_dotenv(usecwd=True))`.
- Compatibilidade com `OPENAI_API_KEY` e `GEMINI_API_KEY`.
- Validação preventiva com retorno amigável caso a credencial esteja ausente.

### 3.2 Geração de Explicação Diagnóstica Humanizada e Contextualizada
Foi desenvolvida a função `gerar_explicacao_diagnostica_humanizada()`, conectando os dados da CNN da Fase 4 e a anamnese da Fase 5:
- **Entrada:** Contexto do paciente (nome, idade, histórico cardiovascular, sintomas no chat) e métricas do ECG (classe predita N/S/V/F/Q, confiança, frequência cardíaca, ritmo).
- **Processamento:** Prompt clínico estruturado que traduz conceitos eletrocardiográficos técnicos para termos compreensíveis e acolhedores, calibrando a gravidade sem alarmismo precipitado.
- **Direcionamento de Conduta:** Roteamento entre pronto-atendimento/SAMU 192 (emergências como classe V), retorno ambulatorial (arritmias supraventriculares classe S) ou reforço preventivo (classe N normal).

### 3.3 Resiliência e Tratamento de Exceções (try/catch)
A integração prevê falhas comuns de sistemas distribuídos na camada de LLM:
- `AuthenticationError`: Chave inválida ou revogada.
- `RateLimitError`: Exaustão de cota ou concorrência excessiva.
- `APIConnectionError`: Queda de conectividade ou indisponibilidade do endpoint.
- `ValidationError` / `JSONDecodeError`: Desvios de schema na extração estruturada.
- **Fallback Seguro:** Mensagem de contingência ao usuário com recomendação de suporte humano imediato caso ocorra falha de rede ou timeout.

## 4. Resultados e Validação Prática

A validação é executada via `integracao_llm_ecg.py` ou células interativas do notebook.

**Caso 1 (Supraventricular - Classe S):**
* **Contexto:** Paciente relata palpitações e taquicardia paroxística. ECG detecta classe S (confiança 89.4%, FC 128 bpm).
* **Explicação Humanizada:** A IA explica com empatia o significado de um batimento supraventricular, contextualiza com os episódios de ansiedade relatados e orienta com clareza o agendamento de retorno cardiológico.

**Caso 2 (Emergência Ventricular - Classe V):**
* **Contexto:** Paciente hipertenso e fumante com dor forte no peito irradiada e suor frio. ECG detecta classe V (confiança 95.7%).
* **Explicação Humanizada:** A IA identifica a urgência máxima, preserva o tom acolhedor e instrui o paciente e familiares a acionarem imediatamente o SAMU 192 ou dirigirem-se à emergência cardiológica mais próxima.

## 5. Limitações e Governança

* **Alucinação:** LLMs podem inferir dados que o paciente não disse. O prompt instrui o uso estrito dos dados informados e "Não informado" quando ausentes.
* **Responsabilidade Médica:** Triagem e explicações por IA **nunca** substituem o raciocínio clínico ou laudo assinado por médico cardiologista. O resultado opera estritamente como suporte à decisão clínica e comunicação em saúde.
* Este protótipo mantém o disclaimer de uso exclusivamente educacional, conforme o termo de governança definido na Fase 4.

