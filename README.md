# Challenge IA FIAP + Dasa + Genera — Sprint 1

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

## 1. Visão Geral do Desafio

Nesta Sprint 1, nosso objetivo é propor uma solução de IA generativa capaz de interpretar, agrupar, priorizar e explicar resultados genéticos dos pacientes da Genera, transformando relatórios técnicos em conteúdos claros, resumidos e personalizados.

A proposta desta etapa não é entregar um sistema final implementado, mas sim uma base conceitual e arquitetural sólida, com foco em problema, usuários, user stories, estrutura dos dados, arquitetura inicial e próximos passos.

---

## 2. Problema

Os relatórios genéticos da Genera contêm informações valiosas para prevenção, cuidado e personalização da jornada de saúde. No entanto, esse conteúdo costuma ser técnico, extenso e fragmentado, dificultando a interpretação pelo paciente final.

Atualmente, o principal desafio não é a ausência de informação, mas sim a dificuldade de transformar muitos dados genéticos em entendimento prático e acionável. O usuário precisa entender:

- o que é mais importante no seu resultado;
- quais riscos ou predisposições merecem atenção;
- quais orientações práticas podem ser extraídas do exame;
- como navegar pelos diferentes painéis de forma simples.

---

## 3. Solução Proposta

Nossa proposta é desenvolver um **Copiloto Genético com IA Generativa**, capaz de transformar relatórios genéticos em PDF em uma experiência interativa, clara e personalizada para o paciente.

A solução será híbrida, composta por três camadas principais:

- **Camada de estruturação dos dados**, responsável por interpretar o PDF, extrair seu conteúdo e convertê-lo para um formato organizado, como JSON;
- **Camada de inteligência**, responsável por resumir os achados, agrupar riscos por grandes temas, priorizar resultados relevantes e gerar recomendações práticas com linguagem acessível;
- **Camada de interação**, composta por uma interface visual com cards, painéis e um **chatbot conversacional**, permitindo ao paciente fazer perguntas em linguagem natural sobre o próprio relatório.

Dessa forma, a solução não se limita a exibir o conteúdo do exame: ela atua como um assistente digital capaz de explicar resultados, destacar pontos de atenção, responder dúvidas e apoiar a jornada de cuidado com mais clareza e personalização.

## A ideia é converter relatórios técnicos em uma experiência mais útil, humanizada e acionável para o paciente, mantendo governança científica e segurança no uso da IA.

## 4. Usuários da Solução

### 4.1 Paciente

Usuário principal da solução. Busca compreender melhor seu relatório genético, receber resumos claros, visualizar riscos por tema e obter orientações práticas.

### 4.2 Time de Genômica / Geneticista

Usuário de governança da solução. Precisa controlar fontes científicas, manter o conteúdo confiável e permitir evolução segura do sistema.

---

## 5. User Stories Priorizadas

### US01

**Como paciente, quero visualizar um resumo personalizado dos meus resultados genéticos.**

### US02

**Como paciente, quero entender meus riscos agrupados por grandes temas (ex.: pele, nutrição, doenças crônicas).**

### US03

**Como paciente, quero recomendações práticas baseadas no meu perfil genético.**

### US04 — Governança

**Como time de genômica, quero controlar quais periódicos científicos podem ser usados pela IA.**

---

## 6. Justificativa das User Stories

As user stories escolhidas representam o núcleo do problema do challenge.

As três histórias de paciente atacam diretamente:

- a dificuldade de interpretação do conteúdo técnico;
- a falta de priorização dos resultados;
- a necessidade de transformar informação genética em ação prática.

A user story de governança garante base científica controlada, maior confiança na solução e aderência ao contexto sensível da saúde.

---

## 7. Estrutura dos Dados

Os PDFs analisados apresentam uma estrutura recorrente, contendo elementos como:

- painel do produto;
- categoria;
- característica genética;
- SNP / rsID;
- gene;
- genótipo;
- classificação de predisposição;
- explicação técnica;
- interpretação do resultado;
- recomendações gerais.

A partir disso, propomos transformar cada resultado em uma estrutura JSON.

### Exemplo

```json
{
  "paciente_id": "anon_001",
  "painel": "Genera Skin",
  "categoria": "Cuidados relevantes",
  "caracteristica": "Sensibilidade ao sol",
  "snp": "rs1805007",
  "gene": "MC1R",
  "genotipo": "C,T",
  "classificacao": "Maior predisposição",
  "descricao_resumida": "Predisposição para sensibilidade aos raios ultravioleta",
  "explicacao_paciente": "Você pode ter maior tendência a queimaduras solares e dificuldade de bronzeamento.",
  "recomendacoes": [
    "Evitar exposição prolongada ao sol",
    "Usar protetor solar diariamente",
    "Priorizar horários de menor radiação"
  ],
  "requer_acompanhamento": true,
  "fonte_relatorio": "Genera Skin"
}
```

## 8. Arquitetura Inicial da Solução

### Fluxo proposto

- Upload ou leitura do relatório genético em PDF
- Extração do conteúdo textual e estrutural
- Segmentação por seções e características
- Conversão para JSON estruturado
- Camada de IA para resumo, agrupamento, priorização e recomendação
- Indexação dos dados estruturados para consultas inteligentes
- Exibição em interface amigável ao paciente, com dashboard e chatbot

### Representação resumida

**PDF → Extração → Estruturação em JSON → IA Generativa → Dashboard + Chatbot/Copilot**

### Componentes principais

- **Parser de documento**: responsável por ler o PDF e identificar campos relevantes
- **Base estruturada**: armazena os dados extraídos em formato organizado
- **Motor de IA**: gera resumo, explicações e recomendações
- **Chatbot / Copilot**: responde perguntas em linguagem natural com base no relatório do paciente
- **Interface visual**: apresenta cards, destaques, agrupamentos temáticos e recomendações

## 9. Papel da IA

A IA terá como funções principais:

- resumir os achados do relatório;
- agrupar resultados por tema;
- destacar pontos de maior relevância;
- traduzir linguagem técnica para linguagem acessível;
- gerar recomendações práticas não diagnósticas;
- permitir interação via **chatbot conversacional**, respondendo perguntas sobre o próprio relatório;
- apoiar futuras evoluções com personalização e explicações contextuais baseadas no histórico de resultados.

Dessa forma, a IA não será apenas um mecanismo de resumo, mas sim o núcleo de um **copiloto genético digital**, capaz de transformar informação técnica em entendimento prático e interação guiada.

## 10. Governança e Segurança

Como se trata de dados genéticos e contexto de saúde, a solução deve considerar:

- conformidade com LGPD;
- uso controlado de fontes científicas;
- guard rails para evitar aconselhamento médico indevido;
- transparência sobre limites da IA;
- aviso de que a solução não substitui avaliação médica.

## 11. Vídeo da Sprint

Link da apresentação em vídeo de até 5 minutos:

[Inserir link aqui]

## 12. Conclusão

A Sprint 1 estabelece a base estratégica e técnica da solução. Priorizamos user stories centradas no paciente, apoiadas por uma camada essencial de governança científica, com foco em transformar relatórios genéticos complexos em informação clara, organizada e útil.

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
