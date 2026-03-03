# CardioIA: A Nova Era da Cardiologia Inteligente – Fase 1

<p align="center">
<a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width=40% height=40%></a>
</p>

---

## Visão Geral

O **CardioIA** é um ecossistema de IA integrado para análise de dados cardiovasculares, combinando:

- **Dados Numéricos**: Sinais vitais, exames laboratoriais, telemonitoramento IoT
- **Dados Textuais**: Relatórios clínicos, diretrizes, anamnese estruturada  
- **Dados Visuais**: ECG, radiografias, ecocardiogramas, angiogramas
- **Modelos IA**: ML supervisionado, deep learning (CNN, RNN), NLP, agentes autônomos

### Objetivo Fase 1
Coleta e governança de bases multimodais com 100+ registros numéricos, 2+ textos clínicos e 100+ imagens de exames, garantindo privacidade, rastreabilidade e alinhamento com requisitos PBL FIAP.

---

## Estrutura do Repositório

```
CardioAI/
├── assets/
│   ├── docs/                                    # Dados textuais clínicos
│   │   ├── diagnostico_insuficiencia_cardiaca.txt
│   │   ├── arritmias_classificacao_tratamento.txt  
│   │   └── infarto_agudo_miocardio.txt
│   └── logo-fiap.png
├── data/
│   ├── pacientes_cardio.csv                     # Dataset numérico (150 x 20)
│   └── images/                                  # Exames visuais (120 imagens)
├── document/                                    # Documentação oficial
│   └── ai_project_document_fiap.md
├── scripts/
│   ├── check_assets.py                          # Validação de integridade
│   └── readme.md
├── src/                                         # Código fonte futuro
├── config/                                      # Configurações
├── requirements.txt                             # Dependências
└── README.md                                    # Este arquivo
```

---

## Parte 1: Dados Numéricos

**Arquivo**: `data/pacientes_cardio.csv`  
**Tamanho**: 150 registros × 20 variáveis  
**Status**: ✅ Atende mínimo de 100 linhas  
**Link Público**: [INSERIR_LINK_PUBLICO_DADOS_NUMERICOS]

### Variáveis
- ID_Paciente, Data_Consulta, Idade, Sexo
- PA_Sistolica, PA_Diastolica, Frequencia_Cardiaca, IMC  
- Colesterol_Total, HDL, LDL, Triglicerides, Glicemia
- Historico_Familiar_ICC, Tabagismo, Diabetes, Hipertensao
- Sopro_Cardiaco, Arritmia, Sintomas_Principal, Risco_Cardiovascular

### Aplicações IA
- **Triagem**: Classificação automática de risco cardiovascular
- **Regressão**: Previsão de PA sistólica, colesterol
- **Classificação**: Presença de arritmia (binária), risco (multiclasse)
- **Clustering**: Identificar subgrupos de pacientes
- **Feature Selection**: Importância de variáveis para downstream

### Origem
Simulado, fins acadêmicos, repositório público, licença MIT

---

## Parte 2: Dados Textuais

**Pasta**: `assets/docs/`  
**Quantidade**: 3 arquivos .txt  
**Status**: ✅ Atende mínimo de 2 arquivos  

### Documentos
1. **diagnostico_insuficiencia_cardiaca.txt**
2. **arritmias_classificacao_tratamento.txt**
3. **infarto_agudo_miocardio.txt**

### Aplicações NLP
- **NER**: Extração de entidades clínicas (diagnósticos, medicamentos, achados)
- **Classificação**: Agrupar por diagnóstico, triagem automática
- **Sumarização**: Resumo de relatórios e histórico clínico
- **Busca Semântica**: Linking sintoma-diagnóstico, recuperação de informação
- **Urgência**: Detecção automática de sinais de alerta
- **Normalização**: Padronização de terminologia (SNOMED CT, ICD-10)

### Fonte
Diretrizes de cardiologia compiladas (SBC, ACC/AHA, ESC)

---

## Parte 3: Dados Visuais

**Pasta**: `data/images/`  
**Quantidade**: 120 imagens PNG  
**Status**: ✅ Atende mínimo de 100 imagens  
**Link Público**: [INSERIR_LINK_PUBLICO_IMAGENS]

### Tipos (4 exames × 30 imagens)
- **ECG**: Eletrocardiogramas (arritmias, isquemia, infarto, bloqueios)
- **RX Tórax**: Radiografias (cardiomegalia, edema, derrame)
- **ECO**: Ecocardiogramas (função sis/dias, estruturas valvulares)
- **Angiografia**: Coronariografia (estenoses, oclusões)

### Aplicações VC
- **Detecção**: Alterações de ST, ondas Q, arritmias
- **Classificação**: Normal vs patológico (CNN)
- **Segmentação**: Contornos de câmaras (U-Net, DeepLab)
- **Medição**: Diâmetros, espessuras, fração de ejeção
- **Interpretabilidade**: Heatmaps (Grad-CAM)

### Importância Clínica
Triagem rápida, suporte diagnóstico, redução tempo resposta, prevenção, educação médica

---

## Governança de Dados

### Privacidade
✅ Sem PII (nomes, RG, CPF, endereços)  
✅ IDs anonimizados (P0001, P0002, ...)  
✅ Datas genéricas  

### Licenças
✅ Dataset: Public Domain / MIT  
✅ Imagens: Creative Commons / Simuladas  
✅ Textos: Diretrizes públicas (SciELO, BVS)  

### Rastreabilidade
✅ Metadados por arquivo  
✅ Versionamento Git  
✅ Changelog mantido  

### Balanceamento
**Risco**: Baixo 23%, Moderado 30%, Alto 30%, M.Alto 17%  
**Sexo**: M 52%, F 48% (equilibrado)  
**Idade**: 25-39: 20%, 40-54: 40%, 55-69: 30%, 70+: 10%

### Vieses Identificados
| Viés | Mitigação |
|------|-----------|
| Selection | Validar com SUS/IBGE |
| Age | Coletar >70 anos |
| Sex | Estratificar análise |
| Measurement | Padronizar protocolo |

---

## Validação Rápida

### Sem instalação
```bash
# Linhas CSV (esperado: 151)
wc -l data/pacientes_cardio.csv

# Textos (esperado: 3)
ls assets/docs/*.txt | wc -l

# Imagens (esperado: 120)
ls data/images/ | wc -l
```

### Com Python
```bash
pip install -r requirements.txt
python scripts/check_assets.py
```

Resultado esperado: [SUCESSO] Todos os requisitos atendidos!

### Análise exploratória
```python
import pandas as pd
df = pd.read_csv('data/pacientes_cardio.csv')
print(df.shape)  # (150, 20)
print(df['Risco_Cardiovascular'].value_counts())
```

---

## Roadmap

### Fase 1 (Atual) ✅
- Data collection & governance
- Asset validation
- Clinical documentation

### Fase 2: Feature Engineering (Q2 2024)
- Data cleaning & standardization
- Feature engineering
- EDA & visualization

### Fase 3: Supervised Learning (Q3 2024)
- Classification models
- Regression models
- Model evaluation & comparison

### Fase 4: Computer Vision (Q4 2024)
- CNN classification
- U-Net segmentation
- Transfer Learning (ResNet, VGG)

### Fase 5: NLP (Q1 2025)
- NER, topic modeling
- BERT embeddings
- Text summarization

### Fase 6: IoT & Real-time (Q2 2025)
- REST API
- Real-time pipeline (Kafka)
- Automated alerts

### Fase 7: LLM Agents (Q3 2025)
- Chatbot (GPT, Claude, Llama)
- RAG (Retrieval-Augmented Generation)
- Web UI (Streamlit)

---

## Referências

**Diretrizes**: [SBC](http://www.arquivosonline.com.br/) | [ACC/AHA](https://www.acc.org/) | [ESC](https://www.escardio.org/)

**Datasets**: [UCI ML](https://archive.ics.uci.edu/) | [Kaggle](https://www.kaggle.com/) | [PhysioNet](https://physionet.org/) 

**Ferramentas**: Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch, spaCy, FastAPI

---

## Licença

MIT License

---

**Versão**: 1.0-phase1 | **Data**: 03/03/2024 | Status: Fase 1 ✅

*Desenvolvido para FIAP – Faculdade de Informática e Administração Paulista*
