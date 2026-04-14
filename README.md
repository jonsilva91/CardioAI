# CardioIA: A Nova Era da Cardiologia Inteligente

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

O **CardioIA** é um projeto acadêmico desenvolvido para a FIAP com foco em **Inteligência Artificial aplicada à cardiologia**. A proposta evolui por fases, integrando diferentes tipos de dados e componentes tecnológicos para simular um ecossistema inteligente de apoio clínico.

O projeto contempla:

- **Dados numéricos** de pacientes cardíacos
- **Dados textuais** com sintomas, descrições clínicas e conhecimento médico
- **Dados visuais** com imagens de ECG
- **Classificação textual de risco**
- **Portal front-end em React** para visualização de pacientes, agendamentos e métricas
- Evolução futura para modelos mais avançados de IA, NLP e visão computacional

---

## Objetivos do Projeto

### Fase 1

Coletar, organizar e documentar bases multimodais para cardiologia, com governança, rastreabilidade e potencial de uso em Machine Learning.

### Fase 2

Implementar componentes práticos de IA simbólica e classificação textual:

- leitura de frases com sintomas
- mapeamento sintoma → doença
- classificador básico de risco com TF-IDF + Scikit-learn

### Ir Além 1

Construir a interface do **Portal CardioIA** com:

- autenticação simulada
- proteção de rotas
- dashboard com métricas
- listagem de pacientes
- agendamento de consultas
- navegação responsiva com React + Vite

---

## Estrutura do Repositório

```text
CardioAI/
├── documents/
│   ├── frases_pacientes.txt
│   ├── mapa_conhecimento.csv
│   └── heart-explain.md
│   ├── references/
│   │   ├── 01_diretrizes_doenca_coronariana_cronica_angina_estavel.txt
│   │   ├── 02_associacao_fatores_risco_dac_cintilografia.txt
│   │   ├── 03_teste_esforco_alteracoes_segmento_st_recuperacao.txt
│   │   ├── 04_valor_diagnostico_teste_ergometrico_isquemia_silenciosa_idoso.txt
│   │   ├── 05_teste_ergometrico_imediato_dor_toracica_emergencia.txt
│   │   ├── 06_comparacao_aterosclerose_coronaria_infarto_angina.txt
│   │   ├── 07_indicacao_cintilografia_perfusao_miocardio_escores.txt
│   │   └── 08_fatores_risco_dac_unidade_hemodinamica.txt
│
├── data/
│    ├── frases_risco.csv
|    ├── pacientes_cardio.csv
|    ├── resultado_diagnostico.csv
├── src/
│   ├── diagnostico_ontologia.py
│   ├── classificacao_risco.ipynb
│   └── portal-cardioia/
│       ├── package.json
│       ├── vite.config.js
│       ├── index.html
│       └── src/
│           ├── App.jsx
│           ├── main.jsx
│           ├── routes.jsx
│           ├── components/
│           ├── contexts/
│           ├── data/
│           ├── pages/
│           └── services/
├── referencias.md
└── README.md
```

---

# Fase 1 — Bases Multimodais em Cardiologia

## Parte 1: Dados Numéricos

**Arquivo**: `heart.csv`  
**Tamanho**: 303 registros × 14 variáveis  
**Status**: ✅ Atende ao mínimo de 100 linhas

### Aplicação

Essa base serve como apoio para tarefas de:

- classificação binária de doença cardíaca
- análise de variáveis clínicas
- feature engineering
- futuros modelos supervisionados

### Variáveis de destaque

- `cp` — tipo de dor no peito
- `thalach` — frequência cardíaca máxima
- `oldpeak` — depressão do segmento ST
- `ca` — número de vasos acometidos
- `thal` — resultado do teste com tálio
- `exang` — angina induzida por exercício

---

## Parte 2: Dados Textuais

**Pasta**: `documents/`  
**Status**: ✅ Atende ao mínimo exigido

### Arquivos

- `diagnostico_insuficiencia_cardiaca.txt`
- `arritmias_classificacao_tratamento.txt`
- `infarto_agudo_miocardio.txt`

### Aplicações

- classificação de sintomas
- extração de entidades médicas
- apoio a NLP clínico
- busca semântica
- construção de mapa de conhecimento

---

## Parte 3: Dados Visuais

**Tipo**: imagens de ECG  
**Quantidade**: 10.148+ imagens  
**Status**: ✅ Atende ao mínimo exigido

### Possibilidades futuras

- classificação de ECG normal vs. anormal
- visão computacional aplicada à triagem
- uso de CNN e interpretabilidade

---

## Governança de Dados

- Sem dados pessoais identificáveis
- Fontes documentadas
- Versionamento por Git
- Organização por modalidade
- Estrutura preparada para evolução em IA multimodal

---

# Fase 2 — IA Simbólica + Classificação Textual

## Parte 1 — Mapeamento sintoma → doença

Foram criados artefatos para representar relações clínicas simples entre sintomas e diagnósticos cardiovasculares.

### Arquivos

- `data/frase_diagnostico.py`
- `dcouments/mapa_conhecimento.csv`

### Objetivo

Ler frases em linguagem natural, identificar sintomas e sugerir diagnósticos com base em um mapa de conhecimento simples.

### Exemplos de doenças trabalhadas

- infarto agudo do miocárdio
- insuficiência cardíaca
- arritmia
- angina
- hipertensão

---

## Parte 2 — Classificador básico de risco

Foi construída uma base simulada de frases médicas rotuladas e um notebook para classificação de risco.

### Arquivos

- `data/frases_risco.csv`
- `src/classificacao_risco.ipynb`

### Tecnologias

- Python
- Pandas
- Scikit-learn
- TF-IDF
- Logistic Regression / Decision Tree

### Objetivo

Classificar frases médicas como:

- **alto risco**
- **baixo risco**

### Exemplo de frase

- `"sinto dor no peito e falta de ar"` → alto risco
- `"tive um leve incômodo nas costas"` → baixo risco

### Etapas do notebook

- carregamento da base
- vetorização com TF-IDF
- treino do classificador
- avaliação com acurácia
- testes com frases novas

---

# Ir Além 1 — Portal CardioIA em React + Vite

Foi desenvolvido um portal front-end simulando a rotina de um sistema cardiológico.

## Funcionalidades implementadas

- autenticação fake com Context API
- token fake salvo no `localStorage`
- proteção de rotas
- dashboard com métricas resumidas
- listagem de pacientes
- formulário de agendamento com `useReducer`
- estilização com CSS Modules
- dados simulados em JSON local

## Estrutura do portal

```text
src/portal-cardioia/
├── package.json
├── index.html
└── src/
    ├── components/
    │   ├── Navbar.jsx
    │   ├── ProtectedRoute.jsx
    │   └── StatCard.jsx
    ├── contexts/
    │   ├── AuthContext.jsx
    │   └── useAuth.jsx
    ├── data/
    │   ├── patients.json
    │   └── appointments.json
    ├── pages/
    │   ├── Login.jsx
    │   ├── Dashboard.jsx
    │   ├── Pacientes.jsx
    │   └── Agendamentos.jsx
    ├── services/
    │   └── fakeApi.js
    ├── App.jsx
    ├── main.jsx
    └── routes.jsx
```

---

## Credenciais do Portal

```text
E-mail: admin@cardioia.com
Senha: 123456
```

---

## Telas do Portal

### Login

Tela inicial com autenticação simulada.

### Dashboard

Painel com:

- total de pacientes
- total de consultas
- casos de alto risco
- casos de baixo risco

### Pacientes

Listagem simulada de pacientes com:

- nome
- idade
- sexo
- condição clínica
- nível de risco
- última consulta

### Agendamentos

Formulário de consultas usando `useReducer`, com listagem das consultas cadastradas.

---

## Como Executar o Portal

### 1. Entrar na pasta do front-end

```bash
cd src/portal-cardioia
```

### 2. Instalar dependências

```bash
npm install
```

### 3. Executar em modo de desenvolvimento

```bash
npm run dev
```

### 4. Abrir no navegador

Acesse a URL exibida no terminal, normalmente:

```text
http://localhost:5173
```

### Observação

Caso o navegador bloqueie o render por política de segurança/extensões, testar:

- em janela anônima
- em outro navegador
- ou com extensões desativadas

---

## Tecnologias Utilizadas

### Ciência de Dados / IA

- Python
- Pandas
- NumPy
- Scikit-learn
- Jupyter Notebook

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

## Roadmap do Projeto

### Concluído

- Fase 1 — bases multimodais
- Fase 2 — mapa de conhecimento e classificador textual
- Ir Além 1 — portal front-end funcional

### Próximos passos possíveis

- integração do portal com back-end real
- persistência de pacientes e consultas
- classificador mais robusto de risco
- visualização de exames de ECG
- rede neural para classificação de imagens cardiológicas
- integração multimodal entre texto, imagem e dados clínicos

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
**Versão**: 2.0  
**Curso**: FIAP — Faculdade de Informática e Administração Paulista

---

**Versão**: 1.1-phase1 | **Data**: 10/03/2026 | **Status**: Fase 1 ✅

_Desenvolvido para FIAP – Faculdade de Informática e Administração Paulista_
