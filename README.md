# CardioAI: A Nova Era da Cardiologia Inteligente

[![FIAP - Faculdade de Informática e Administração Paulista](https://github.com/jonsilva91/CardioAI/raw/main/assets/logo-fiap.png)](https://www.fiap.com.br/)

---

## Integrantes


- **Jonas Luis da Silva** — RM561465
- **Edson Henrique Felix Batista** — RM566321

---

## Visão Geral

O **CardioAI** é um projeto acadêmico da FIAP com foco em **Inteligência Artificial aplicada à cardiologia**. O repositório foi reorganizado para separar claramente os entregáveis por fase, facilitar a avaliação acadêmica e preservar o funcionamento dos artefatos já implementados.

O projeto contempla:

- bases multimodais para cardiologia
- IA simbólica e classificação textual
- portal front-end em React
- monitoramento IoT com API REST e automação de alertas
- análise de séries temporais em saúde
- classificação de imagens de ECG com CNN treinada do zero e Transfer Learning (Fase 4)
- assistente conversacional integrado ao IBM watsonx Assistant (Fase 5)
- modelo preditivo de risco cardiovascular (Random Forest) e orquestração multiagente com OpenAI Agents SDK (Fase 6)

---

## Navegação Rápida

- [Fase 1 — Bases Multimodais](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase01_bases_multimodais/README.md)
- [Fase 2 — IA Simbólica e Classificação](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase02_ia_simbolica_classificacao/README.md)
- [Fase 3 — IoT, REST, e-mail e séries temporais](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase03_iot_monitoramento/README.md)
- [Fase 4 — CNN aplicada a ECG](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase04_cnn_ecg/README.md)
- [Fase 5 — Assistente Conversacional](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase05_assistente_conversacional/README.md)
- [Fase 6 — Preditivo e Multiagente](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase06_preditivo_multiagente/README.md)
- [Portal React](https://github.com/jonsilva91/CardioAI/blob/main/apps/portal-cardioia/README.md)

---

## Estrutura do Repositório

```
CardioAI/
├── README.md
├── assets/
├── data/
│   └── raw/
├── docs/
│   └── references/
├── phases/
│   ├── fase01_bases_multimodais/
│   ├── fase02_ia_simbolica_classificacao/
│   ├── fase03_iot_monitoramento/
│   ├── fase04_cnn_ecg/
│   ├── fase05_assistente_conversacional/
│   └── fase06_preditivo_multiagente/
├── apps/
│   ├── mobile-cardioia/
│   └── portal-cardioia/
├── config/
├── referencias.md
└── .gitignore
```

---

## Resumo das Fases

### Fase 1 — Bases Multimodais

Organiza materiais de referência, textos clínicos e documentação de bases para uso em IA aplicada à cardiologia.

**Local:** `phases/fase01_bases_multimodais/`

### Fase 2 — IA Simbólica e Classificação Textual

Contém o script de diagnóstico baseado em mapa de conhecimento e o notebook de classificação textual de risco.

**Local:** `phases/fase02_ia_simbolica_classificacao/`

### Fase 3 — IoT, REST, e-mail e séries temporais

Centraliza os entregáveis de monitoramento IoT, API REST com alertas simulados por e-mail, notebook de séries temporais e relatórios.

**Local:** `phases/fase03_iot_monitoramento/`

### Fase 4 — CNN aplicada a ECG

Classificação de sinais de ECG usando uma CNN treinada do zero e Transfer Learning (MobileNetV2), com avaliação completa (accuracy, precision, recall e F1 por classe) e um protótipo Flask de inferência integrado à Fase 5.

**Local:** `phases/fase04_cnn_ecg/`

### Fase 5 — Assistente Conversacional

Assistente conversacional (chatbot) para triagem inicial em saúde, integrado ao portal React, com fluxo de diálogo real modelado no IBM watsonx Assistant (intents, entities e dialog nodes), backend Flask com fallback local, e integração direta com o classificador da Fase 4 para explicar resultados de ECG.

**Local:** `phases/fase05_assistente_conversacional/`

### Fase 6 — Modelo Preditivo e Orquestração Multiagente

Sistema preditivo de pico de risco cardiovascular com Machine Learning supervisionado e arquitetura multiagente para apoio à decisão clínica e operacional no ambiente hospitalar:
- **Base de Dados Sintética:** Geração reproduzindo estritamente as diretrizes da FIAP (5.000 amostras, 10 features clínico-operacionais, seed 42);
- **Modelo Preditivo (*Random Forest*):** 200 estimadores atingindo 99,9% de acurácia, F1-Score de 0,9981 e recall de 99,62% no teste para detecção de pico de risco;
- **Sistema Multiagente (*OpenAI Agents SDK*):** Quatro agentes colaborativos especializados (Orquestrador, Analista de Risco, Especialista em Protocolos e Planejador de Resposta) integrados por *handoffs* nativos;
- **Engenharia de Confiabilidade:** Isolamento de contexto por atendimento (`CardioContext`), persistência e histórico em banco SQLite (`SQLiteSession`) para acompanhamento interativo pós-triagem, e validação de segurança clínica com `OutputGuardrail` determinístico (tripwire contra alucinações e divergências de protocolo).

**Local:** `phases/fase06_preditivo_multiagente/`

### Portal CardioIA

Aplicação React + Vite para autenticação simulada, dashboard, pacientes, agendamentos e o assistente conversacional (rota `/assistente`).

**Local:** `apps/portal-cardioia/`

### App Mobile React Native

Aplicativo mobile em React Native/Expo para classificação de imagens de ECG, integrando com o modelo CNN da Fase 4 via API FastAPI.

**Funcionalidades:**

- Seleção de imagens da galeria
- Upload e classificação via API
- Exibição de resultado com confiança
- Avisos de uso acadêmico

➡️ **[Acessar documentação do app mobile](https://github.com/jonsilva91/CardioAI/blob/main/apps/mobile-cardioia/README.md)**

**Local:** `apps/mobile-cardioia/`

---

## Como Executar

### 1. Portal React

```
cd apps/portal-cardioia
npm install
npm run dev
```

Acesse a URL exibida no terminal, normalmente `http://localhost:5173`.

### 2. Fase 2 — Diagnóstico simbólico

```
python phases/fase02_ia_simbolica_classificacao/diagnostico_ontologia.py
```

### 3. Fase 2 — Notebook de classificação textual

```
jupyter notebook phases/fase02_ia_simbolica_classificacao/classificacao_risco.ipynb
```

### 4. Fase 3 — API REST e alerta por e-mail simulado

```
cd phases/fase03_iot_monitoramento/ir_alem_1_rest_email
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Em outro terminal:

```
cd phases/fase03_iot_monitoramento/ir_alem_1_rest_email
python client_simulador.py
```

### 5. Fase 3 — Notebook de séries temporais

```
pip install -r phases/fase03_iot_monitoramento/ir_alem_2_series_temporais/requirements.txt
jupyter notebook phases/fase03_iot_monitoramento/notebooks/ir_alem_2_series_temporais_saude.ipynb
```

### 6. Fase 4 — CNN ECG

```
pip install -r phases/fase04_cnn_ecg/requirements.txt
jupyter notebook phases/fase04_cnn_ecg/notebooks/cnn_ecg_classification.ipynb
python phases/fase04_cnn_ecg/src/train.py
python phases/fase04_cnn_ecg/src/evaluate.py
```

### 7. Fase 4 — API FastAPI (IR ALÉM 2)

```
cd phases/fase04_cnn_ecg
.venv\Scripts\activate
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000/docs`

### 8. App Mobile React Native (IR ALÉM 2)

**Backend (terminal 1):**

```
cd phases/fase04_cnn_ecg
.venv\Scripts\activate
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**Mobile (terminal 2):**

```
cd apps/mobile-cardioia
npm install
npx expo start
```

⚠️ **Configure o IP da sua máquina em `src/services/visionApi.js` antes de executar!**

Veja instruções completas em: [apps/mobile-cardioia/README.md](https://github.com/jonsilva91/CardioAI/blob/main/apps/mobile-cardioia/README.md)

### 9. Fase 5 — Assistente Conversacional

Para rodar o backend do chat:

```
cd phases/fase05_assistente_conversacional
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/app.py
```

O chat ficará acessível via Portal React na rota `/assistente`.

### 10. Fase 6 — Preditivo e Multiagente

#### Configuração do Ambiente Virtual:
```bash
cd phases/fase06_preditivo_multiagente
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### Geração da Base e Treinamento do Modelo:
```bash
# Gera a base sintética oficial em data/base_sintetica_pico_risco.csv
python -m src.data_generation

# Executa o treino do Random Forest, gera gráficos em reports/figures e salva models/modelo_pico_risco.joblib
python -m src.train
```

#### Execução dos Agentes (com OpenAI API):
Configure as variáveis de ambiente a partir do modelo `.env.example`:
```bash
cp .env.example .env
# Defina sua chave de API no arquivo .env: OPENAI_API_KEY=sua-chave-aqui
```

Execução dos cenários clínicos:
```bash
# Caso individual (paciente de alto risco do enunciado):
python -m src.agents_system.main --paciente data/exemplos/novo_caso.json

# Modo interativo com histórico em SQLite (permite perguntas de acompanhamento pós-triagem):
python -m src.agents_system.main --paciente data/exemplos/novo_caso.json --interativo

# Outros perfis de teste:
python -m src.agents_system.main --paciente data/exemplos/caso_baixo_risco.json
python -m src.agents_system.main --paciente data/exemplos/caso_moderado_risco.json
```

#### Testes Unitários e Tripwire de Segurança Clínica:
```bash
# Demonstração prática do disparo e captura do OutputGuardrailTripwireTriggered:
python scripts/demo_guardrail.py

# Suíte de testes unitários (15 testes sem chamadas externas):
pytest -v
```

---

## Dados e Referências

- Referências bibliográficas gerais: [`referencias.md`](https://github.com/jonsilva91/CardioAI/blob/main/referencias.md)
- Artigos e textos de apoio: [`docs/references/`](https://github.com/jonsilva91/CardioAI/blob/main/docs/references)
- Dados brutos futuros devem ser colocados em: [`data/raw/`](https://github.com/jonsilva91/CardioAI/blob/main/data/raw)

> Para a Fase 4, datasets grandes não devem ser versionados. O download deve ser feito manualmente e armazenado em `data/raw/`.

---

## Vídeos

Demonstrações em vídeo das entregas acadêmicas do projeto:

### Vídeo da Fase 5 — Assistente Conversacional e Integração de Modelos
[![Vídeo da Fase 5](https://img.youtube.com/vi/Nu-WhM9n6-s/0.jpg)](https://youtu.be/Nu-WhM9n6-s)
- **Link no YouTube:** [https://youtu.be/Nu-WhM9n6-s](https://youtu.be/Nu-WhM9n6-s)
- **Conteúdo:** Demonstração do chatbot integrado ao IBM watsonx Assistant e explicação de exames de ECG da Fase 4.

### Vídeo da Fase 6 — Entrega Principal (Sistema Preditivo e Multiagente)
- **Link no YouTube (Não Listado):** [https://youtu.be/2cC5odm-Fuw](https://youtu.be/2cC5odm-Fuw)
- **Duração máxima:** 4 minutos
- **Conteúdo:** Apresentação do modelo de Machine Learning (Random Forest 99,9%), demonstração do fluxo multiagente com logs de handoffs no terminal, saída estruturada sob Output Guardrail e modo interativo via SQLiteSession.

### Vídeo da Fase 6 — Ir Além 1 (Desafio Opcional 1)
- **Link no YouTube (Não Listado):** [https://youtu.be/mperrwkEUbA](https://youtu.be/mperrwkEUbA)

### Vídeo da Fase 6 — Ir Além 2 (Desafio Opcional 2)
- **Link no YouTube (Não Listado):** [https://youtu.be/FRKwCTTr1H0](https://youtu.be/FRKwCTTr1H0)

---

## Tecnologias Utilizadas

### Ciência de Dados / IA

- Python
- Pandas
- NumPy
- Scikit-learn (Random Forest, Logistic Regression)
- Joblib
- Jupyter Notebook
- TensorFlow/Keras
- IBM watsonx Assistant
- OpenAI Agents SDK (`openai-agents`)
- Pydantic
- SQLite (`SQLiteSession`)

### Front-end

- React
- Vite
- React Router DOM
- Context API
- CSS Modules

### Organização e Versionamento

- Git
- GitHub
- Markdown

---

## Roadmap

### Concluído

- Fase 1 — bases multimodais
- Fase 2 — mapa de conhecimento e classificador textual
- Fase 3 — IoT, REST, e-mail e séries temporais
- Fase 4 — CNN e Transfer Learning para classificação de ECG
- Fase 5 — assistente conversacional com IBM watsonx Assistant
- Fase 6 — modelo preditivo de risco cardiovascular (Random Forest) e orquestração multiagente (OpenAI Agents SDK) com guardrails e persistência SQLite
- Portal React funcional

### Próximos passos

- integração do portal com back-end real de persistência
- classificador mais robusto de risco
- expandir cobertura de intents do assistente conversacional
- visualização de exames de ECG no portal

---

## Referências

- UCI Machine Learning Repository
- Kaggle
- SciELO
- Diretrizes SBC, ACC/AHA e ESC

Consultar também:

- `referencias.md`
- `docs/references/`

---

## Licença

MIT License

---

**Status do Projeto**: Fases 1 a 6 entregues
**Versão**: 6.0
**Curso**: FIAP — Faculdade de Informática e Administração Paulista

---

*Desenvolvido para FIAP – Faculdade de Informática e Administração Paulista*