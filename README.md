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

---

## Navegação Rápida

- [Fase 1 — Bases Multimodais](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase01_bases_multimodais/README.md)
- [Fase 2 — IA Simbólica e Classificação](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase02_ia_simbolica_classificacao/README.md)
- [Fase 3 — IoT, REST, e-mail e séries temporais](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase03_iot_monitoramento/README.md)
- [Fase 4 — CNN aplicada a ECG](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase04_cnn_ecg/README.md)
- [Fase 5 — Assistente Conversacional](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase05_assistente_conversacional/README.md)
- [Portal React](https://github.com/jonsilva91/CardioAI/blob/main/apps/portal-cardioia/README.md)

---

## Estrutura do Repositório

```
CardioAI/
├── README.md
├── assets/
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
├── docs/
│   ├── references/
│   └── reports/
├── phases/
│   ├── fase01_bases_multimodais/
│   ├── fase02_ia_simbolica_classificacao/
│   ├── fase03_iot_monitoramento/
│   ├── fase04_cnn_ecg/
│   └── fase05_assistente_conversacional/
├── apps/
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

---

## Dados e Referências

- Referências bibliográficas gerais: [`referencias.md`](https://github.com/jonsilva91/CardioAI/blob/main/referencias.md)
- Artigos e textos de apoio: [`docs/references/`](https://github.com/jonsilva91/CardioAI/blob/main/docs/references)
- Dados brutos futuros devem ser colocados em: [`data/raw/`](https://github.com/jonsilva91/CardioAI/blob/main/data/raw)
- Saídas processadas e amostras podem ser organizadas em:
  - [`data/processed/`](https://github.com/jonsilva91/CardioAI/blob/main/data/processed)
  - [`data/samples/`](https://github.com/jonsilva91/CardioAI/blob/main/data/samples)

> Para a Fase 4, datasets grandes não devem ser versionados. O download deve ser feito manualmente e armazenado em `data/raw/`.

---

## Evidências de Entrega

### Repositório

Este repositório contém os artefatos acadêmicos organizados por fase para facilitar navegação, execução e avaliação.

### Vídeo

Vídeo no YouTube (não listado):

[![CardioAI](https://camo.githubusercontent.com/e89429a3dcbbfc19381698fcc2e6e4c95f9c9d7375b59fe3136f7a9b47dee321/68747470733a2f2f696d672e796f75747562652e636f6d2f76692f59555a716352384c6746552f302e6a7067)](https://youtu.be/YUZqcR8LgFU)

---

## Tecnologias Utilizadas

### Ciência de Dados / IA

- Python
- Pandas
- NumPy
- Scikit-learn
- Jupyter Notebook
- TensorFlow/Keras
- IBM watsonx Assistant

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
- `documents/`
- `documents/references/`

---

## Licença

MIT License

---

**Status do Projeto**: Fases 1 a 5 entregues
**Versão**: 5.0
**Curso**: FIAP — Faculdade de Informática e Administração Paulista

---

*Desenvolvido para FIAP – Faculdade de Informática e Administração Paulista*