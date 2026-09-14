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

## 3. Resultados e Validação

O notebook `extracao_informacoes_clinicas.ipynb` executa simulações práticas. 

**Caso de Uso 2 (Emergência):**
* **Input:** "Estou com uma dor no peito muito forte, insuportável, irradiando para o braço esquerdo. Também sinto muita falta de ar. Sou fumante e hipertenso."
* **Output Estruturado:**
  ```json
  {
    "sintomas": ["dor no peito intensa", "falta de ar"],
    "duracao": "30 minutos",
    "intensidade": "alta",
    "fatores_risco": ["hipertensão", "tabagismo"],
    "urgencia": "alta",
    "classe_ecg_provavel": "V"
  }
  ```
* **Ação no Sistema:** O parser de validação lê `"urgencia": "alta"` e ativa o protocolo de emergência imediato (bypass no fluxo normal do chatbot). A classe **V** (Ventricular) é sugerida como a provável manifestação no ECG (relacionada frequentemente a isquemias graves e infartos).

## 4. Limitações e Governança

* **Alucinação:** LLMs podem inferir dados que o paciente não disse. O prompt deve instruir o uso de "Não informado" quando necessário.
* **Responsabilidade Médica:** Triagem por IA **nunca** substitui o raciocínio clínico humano. O uso da `classe_ecg_provavel` é apenas para *priorização na fila de atendimento*, não como diagnóstico prévio. 
* Este protótipo mantém o disclaimer de uso exclusivamente educacional, conforme o termo de governança definido na Fase 4.
