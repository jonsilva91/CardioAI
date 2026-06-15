# CardioAI: A Nova Era da Cardiologia Inteligente

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" width="40%">
  </a>
</p>

---

## Integrantes

- **João Vitor Severo Oliveira** — RM5666251
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
- preparação da Fase 4 com CNN aplicada a ECG

---

## Navegação Rápida

- [Fase 1 — Bases Multimodais](phases/fase01_bases_multimodais/README.md)
- [Fase 2 — IA Simbólica e Classificação](phases/fase02_ia_simbolica_classificacao/README.md)
- [Fase 3 — IoT, REST, e-mail e séries temporais](phases/fase03_iot_monitoramento/README.md)
- [Fase 4 — CNN aplicada a ECG](phases/fase04_cnn_ecg/README.md)
- [Portal React](apps/portal-cardioia/README.md)

---

## Estrutura do Repositório

```text
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
│   └── fase04_cnn_ecg/
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

Estrutura inicial preparada para classificação de ECG com CNN simples, incluindo notebook, scripts de treino/avaliação e diretórios de saída.

**Local:** `phases/fase04_cnn_ecg/`

### Portal CardioIA

Aplicação React + Vite para autenticação simulada, dashboard, pacientes e agendamentos.

**Local:** `apps/portal-cardioia/`

### IR ALÉM 2 — Aplicativo Mobile React Native

Aplicativo mobile em React Native/Expo para classificação de imagens de ECG, integrando com o modelo CNN da Fase 4 via API FastAPI.

**Funcionalidades:**

- Seleção de imagens da galeria
- Upload e classificação via API
- Exibição de resultado com confiança
- Avisos de uso acadêmico

➡️ **[Acessar documentação do app mobile](apps/mobile-cardioia/README.md)**

**Local:** `apps/mobile-cardioia/`

---

## Como Executar

### 1. Portal React

```bash
cd apps/portal-cardioia
npm install
npm run dev
```

Acesse a URL exibida no terminal, normalmente `http://localhost:5173`.

### 2. Fase 2 — Diagnóstico simbólico

```bash
python phases/fase02_ia_simbolica_classificacao/diagnostico_ontologia.py
```

### 3. Fase 2 — Notebook de classificação textual

```bash
jupyter notebook phases/fase02_ia_simbolica_classificacao/classificacao_risco.ipynb
```

### 4. Fase 3 — API REST e alerta por e-mail simulado

```bash
cd phases/fase03_iot_monitoramento/ir_alem_1_rest_email
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Em outro terminal:

```bash
cd phases/fase03_iot_monitoramento/ir_alem_1_rest_email
python client_simulador.py
```

### 5. Fase 3 — Notebook de séries temporais

```bash
pip install -r phases/fase03_iot_monitoramento/ir_alem_2_series_temporais/requirements.txt
jupyter notebook phases/fase03_iot_monitoramento/notebooks/ir_alem_2_series_temporais_saude.ipynb
```

### 6. Fase 4 — CNN ECG

```bash
pip install -r phases/fase04_cnn_ecg/requirements.txt
jupyter notebook phases/fase04_cnn_ecg/notebooks/cnn_ecg_classification.ipynb
python phases/fase04_cnn_ecg/src/train.py
python phases/fase04_cnn_ecg/src/evaluate.py
```

### 7. Fase 4 — API FastAPI (IR ALÉM 2)

```bash
cd phases/fase04_cnn_ecg
.venv\Scripts\activate
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000/docs`

### 8. App Mobile React Native (IR ALÉM 2)

**Backend (terminal 1):**

```bash
cd phases/fase04_cnn_ecg
.venv\Scripts\activate
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**Mobile (terminal 2):**

```bash
cd apps/mobile-cardioia
npm install
npx expo start
```

⚠️ **Configure o IP da sua máquina em `src/services/visionApi.js` antes de executar!**

Veja instruções completas em: [apps/mobile-cardioia/README.md](apps/mobile-cardioia/README.md)

---

## Dados e Referências

- Referências bibliográficas gerais: [`referencias.md`](referencias.md)
- Artigos e textos de apoio: [`docs/references/`](docs/references/)
- Dados brutos futuros devem ser colocados em: [`data/raw/`](data/raw/)
- Saídas processadas e amostras podem ser organizadas em:
  - [`data/processed/`](data/processed/)
  - [`data/samples/`](data/samples/)

> Para a Fase 4, datasets grandes não devem ser versionados. O download deve ser feito manualmente e armazenado em `data/raw/`.

---

## Evidências de Entrega

### Repositório

Este repositório contém os artefatos acadêmicos organizados por fase para facilitar navegação, execução e avaliação.

### Vídeo

Vídeo no YouTube (não listado):

[![WCardioAI](https://img.youtube.com/vi/YUZqcR8LgFU/0.jpg)](https://youtu.be/YUZqcR8LgFU)

---

## Tecnologias Utilizadas

### Ciência de Dados / IA

- Python
- Pandas
- NumPy
- Scikit-learn
- Jupyter Notebook
- TensorFlow/Keras ou PyTorch na evolução da Fase 4

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
- Portal React funcional

### Próximos passos

- integração do portal com back-end real
- persistência de pacientes e consultas
- classificador mais robusto de risco
- visualização de exames de ECG
- rede neural para classificação de imagens cardiológicas
- integração multimodal entre texto, imagem e dados clínicos

---

## IR ALÉM Fase 3— Comunicação automatizada com REST e e-mail

Fase 3 do projeto CardioIA expande a solução para o contexto de **IoT na saúde**, com monitoramento contínuo de sinais vitais, comunicação entre sistemas e análise de séries temporais.

A documentação completa do Ir Além está disponível em:

➡️ [Acessar README do Ir Além da Fase 3](src/ir_alem_fase03/README-Fase3-IrAlem-section.md)

---

## Evidências de Entrega

### Repositório

Este repositório contém todos os arquivos exigidos das fases implementadas.

### Vídeo

Vídeo no YouTube (não listado):

[![WCardioAI](https://img.youtube.com/vi/YUZqcR8LgFU/0.jpg)](https://youtu.be/YUZqcR8LgFU)

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

**Status do Projeto**: Em evolução  
**Versão**: 4.0  
**Curso**: FIAP — Faculdade de Informática e Administração Paulista

---

_Desenvolvido para FIAP – Faculdade de Informática e Administração Paulista_
