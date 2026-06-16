# Fase 4 — CNN para Classificação de ECG

**CardioAI - FIAP 2026**

---

## 🎯 Objetivo

Desenvolver um **Assistente Cardiológico Virtual com Visão Computacional** capaz de classificar imagens de ECG usando Redes Neurais Convolucionais (CNNs). O projeto implementa duas abordagens:

1. **CNN do Zero (Scratch)** - Arquitetura construída manualmente
2. **Transfer Learning** - Utilizando MobileNetV2 pré-treinado

Além disso, inclui análise de viés, considerações éticas (IR ALÉM 1) e um protótipo web funcional.

---

## ⚠️ AVISO IMPORTANTE

Este é um **protótipo acadêmico** desenvolvido para fins educacionais.

**NÃO deve ser usado para:**

- Diagnóstico médico real
- Decisões clínicas
- Substituir avaliação profissional

**Sempre consulte profissionais de saúde qualificados.**

---

## 📁 Estrutura da Fase

```text
phases/fase04_cnn_ecg/
├── README.md                          # Este arquivo
├── requirements.txt                   # Dependências Python
├── notebooks/
│   ├── cnn_ecg_classification.ipynb   # Notebook original (básico)
│   └── fase04_cnn_ecg_colab.ipynb    # Notebook completo para Google Colab
├── src/
│   ├── dataset.py                     # Carregamento e pré-processamento
│   ├── model_cnn.py                   # CNN do zero
│   ├── model_transfer.py              # Transfer Learning
│   ├── train.py                       # Script de treinamento
│   ├── evaluate.py                    # Script de avaliação
│   └── app.py                         # Protótipo Flask
├── reports/
│   ├── relatorio-fase04-cnn-ecg.md   # Relatório técnico principal
│   └── relatorio-ir-alem-1-governanca.md  # Relatório de ética e governança
└── outputs/
    ├── figures/                       # Gráficos e visualizações
    └── models/                        # Modelos treinados (.keras)
```

---

## 📊 Dataset

### Dataset Recomendado

**Nome:** ECG Images dataset

**Fonte:** [Kaggle - ECG Images](https://www.kaggle.com/datasets/analiviafr/ecg-images)

**Características:**

- Imagens de ECG 128X128 pixels
- 5 classes de arritmia cardíaca
- Formato: PNG
- Derivado do MIT-BIH Arrhythmia Database

### Classes

1. **Normal (N)** - Batimentos normais
2. **Supraventricular (S)** - Batimentos supraventriculares prematuros
3. **Ventricular (V)** - Batimentos ventriculares prematuros
4. **Fusion (F)** - Batimentos de fusão
5. **Unknown (Q)** - Batimentos não classificáveis

### Como Baixar

**Instruções detalhadas:** `../../../data/raw/ecg_images/README.md`

**Resumo:**

1. Acesse o [link do Kaggle](https://www.kaggle.com/datasets/shayanfazeli/heartbeat)
2. Faça login ou crie uma conta
3. Baixe o dataset
4. Extraia para `../../data/raw/ecg_images/`
5. Organize em subdiretórios por classe

**Estrutura esperada:**

```text
data/raw/ecg_images/
├── Normal/
├── Supraventricular/
├── Ventricular/
├── Fusion/
└── Unknown/
```

---

## 🚀 Como Executar

### Opção 1: Google Colab (Recomendado)

**Vantagens:**

- GPU gratuita
- Ambiente pré-configurado
- Fácil compartilhamento

**Passos:**

1. Abra o notebook no Colab:
   - Acesse: [Google Colab](https://colab.research.google.com/)
   - Upload: `notebooks/fase04_cnn_ecg_colab.ipynb`
   - Ou use: `File > Open notebook > GitHub` e cole o link do repositório

2. Configure o dataset:

   ```python
   # Opção A: Upload manual
   from google.colab import files
   uploaded = files.upload()

   # Opção B: Google Drive
   from google.colab import drive
   drive.mount('/content/drive')
   DATA_DIR = '/content/drive/MyDrive/ecg_images'

   # Opção C: Kaggle API
   !pip install kaggle
   !mkdir -p ~/.kaggle
   # Upload kaggle.json
   !kaggle datasets download -d analiviafr/ecg-images
   !unzip archive.zip -d ecg_images
   ```

3. Execute as células sequencialmente

4. Baixe os modelos treinados ao final

### Opção 2: Execução Local

#### Pré-requisitos

- Python 3.8+
- pip
- (Opcional) GPU com CUDA para treinamento mais rápido

#### Instalação

```bash
# 1. Clone o repositório (se ainda não fez)
git clone https://github.com/seu-usuario/CardioAI.git
cd CardioAI

# 2. Crie ambiente virtual (recomendado)
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Instale dependências
pip install -r phases/fase04_cnn_ecg/requirements.txt

# 4. Baixe e organize o dataset
# Siga as instruções em data/raw/ecg_images/README.md
```

#### Treinamento

```bash
# Treinar CNN do zero
python phases/fase04_cnn_ecg/src/train.py

# O modelo será salvo em:
# phases/fase04_cnn_ecg/outputs/models/cnn_ecg_model.keras
```

#### Avaliação

```bash
# Avaliar modelo treinado
python phases/fase04_cnn_ecg/src/evaluate.py

# Gera:
# - Métricas (accuracy, precision, recall, F1)
# - Matriz de confusão
# - Relatório por classe
# - Figura salva em outputs/figures/
```

#### Protótipo Flask

```bash
# Executar aplicação web
python phases/fase04_cnn_ecg/src/app.py

# Acesse no navegador:
# http://localhost:5000
```

**Funcionalidades do Flask:**

- Upload de imagem de ECG
- Classificação em tempo real
- Exibição de classe e confiança
- Avisos de uso acadêmico

#### Jupyter Notebook Local

```bash
# Iniciar Jupyter
jupyter notebook

# Abrir:
# phases/fase04_cnn_ecg/notebooks/fase04_cnn_ecg_colab.ipynb
```

---

## 🧠 Modelos Implementados

### 1. CNN do Zero (Scratch)

**Arquivo:** `src/model_cnn.py`

**Arquitetura:**

```
Input (256x256x3)
    ↓
Conv2D(32) + MaxPool + Dropout(0.2)
    ↓
Conv2D(64) + MaxPool + Dropout(0.2)
    ↓
Conv2D(128) + MaxPool + Dropout(0.3)
    ↓
Flatten
    ↓
Dense(256) + Dropout(0.4)
    ↓
Dense(128) + Dropout(0.3)
    ↓
Dense(5) + Softmax
```

**Características:**

- ~2.5M parâmetros treináveis
- Dropout para regularização
- Adam optimizer (lr=0.001)

**Uso:**

```python
from src.model_cnn import build_cnn_model

model = build_cnn_model(
    input_shape=(128, 128, 3),
    num_classes=5
)
```

### 2. Transfer Learning (MobileNetV2)

**Arquivo:** `src/model_transfer.py`

**Arquitetura:**

```
Input (256x256x3)
    ↓
MobileNetV2 (pré-treinado, congelado)
    ↓
GlobalAveragePooling2D
    ↓
Dense(256) + Dropout(0.5)
    ↓
Dense(128) + Dropout(0.3)
    ↓
Dense(5) + Softmax
```

**Características:**

- Base MobileNetV2 pré-treinada no ImageNet
- ~0.5M parâmetros treináveis (apenas classificador)
- Adam optimizer (lr=0.0001)

**Uso:**

```python
from src.model_transfer import build_transfer_model

model = build_transfer_model(
    input_shape=(128, 128, 3),
    num_classes=5,
    base_model='mobilenetv2'  # ou 'vgg16', 'resnet50'
)
```

**Outros modelos disponíveis:**

- VGG16
- ResNet50

---

## 📈 Resultados Esperados

### Métricas

O sistema calcula e exibe:

- **Accuracy**: Proporção de predições corretas
- **Precision**: Proporção de positivos corretos
- **Recall**: Proporção de positivos identificados
- **F1-Score**: Média harmônica de Precision e Recall

**Por classe e geral (weighted average)**

### Visualizações

1. **Curvas de Aprendizado**
   - Accuracy vs Época (treino e validação)
   - Loss vs Época (treino e validação)

2. **Matriz de Confusão**
   - Visualização de acertos e erros por classe
   - Identificação de confusões sistemáticas

3. **Distribuição de Classes**
   - Análise de desbalanceamento
   - Gráficos de barras e pizza

4. **Análise de Erros**
   - Taxa de erro por classe
   - Padrões de confusão

### Performance Típica

**CNN do Zero:**

- Accuracy: 85-92% (depende do dataset)
- Convergência: 15-20 épocas
- Tempo: ~30-60 min (GPU)

**Transfer Learning:**

- Accuracy: 90-95% (geralmente melhor)
- Convergência: 10-15 épocas
- Tempo: ~20-40 min (GPU)

---

## 🔍 IR ALÉM 1: Ética e Governança

### Análises Implementadas

1. **Desbalanceamento de Classes**
   - Visualização da distribuição
   - Cálculo de razão de desbalanceamento
   - Alertas automáticos

2. **Análise de Viés**
   - Identificação de viés de seleção
   - Análise de erros por classe
   - Detecção de confusões sistemáticas

3. **Falsos Positivos vs Falsos Negativos**
   - Discussão de impactos clínicos
   - Trade-off entre sensibilidade e precisão
   - Recomendações de threshold

4. **Estratégias de Mitigação**
   - Class weights
   - Oversampling/Undersampling
   - Validação externa
   - Explicabilidade (Grad-CAM)
   - Revisão clínica obrigatória
   - Monitoramento contínuo

### Relatórios

**Relatório Principal:**
`reports/relatorio-fase04-cnn-ecg.md`

- Pipeline completo
- Arquiteturas detalhadas
- Resultados e métricas
- Limitações técnicas e clínicas

**Relatório de Governança:**
`reports/relatorio-ir-alem-1-governanca.md`

- Análise de desbalanceamento
- Riscos de viés
- Falsos positivos/negativos
- Estratégias de mitigação
- Framework de governança
- Conformidade regulatória

---

## ⚙️ Configurações Avançadas

### Hiperparâmetros

**Treino:**

```python
EPOCHS = 20
BATCH_SIZE = 32
LEARNING_RATE_CNN = 0.001
LEARNING_RATE_TRANSFER = 0.0001
```

**Data Augmentation:**

```python
rotation_range = 10
width_shift_range = 0.1
height_shift_range = 0.1
horizontal_flip = True
zoom_range = 0.1
```

**Divisão de Dados:**

```python
TRAIN_SPLIT = 0.7
VALIDATION_SPLIT = 0.2
TEST_SPLIT = 0.1
```

### Personalização

**Adicionar novo modelo base:**

```python
# Em src/model_transfer.py
def build_transfer_model(..., base_model='efficientnet'):
    if base_model == 'efficientnet':
        base = applications.EfficientNetB0(...)
    # ...
```

**Ajustar arquitetura:**

```python
# Em src/model_cnn.py
# Adicionar mais camadas convolucionais
layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
layers.MaxPooling2D((2, 2)),
```

**Implementar class weights:**

```python
from sklearn.utils.class_weight import compute_class_weight

class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)

model.fit(..., class_weight=dict(enumerate(class_weights)))
```

---

## 🐛 Troubleshooting

### Problemas Comuns

**1. Dataset não encontrado**

```
FileNotFoundError: Diretório de dados não encontrado
```

**Solução:** Verifique se o dataset está em `data/raw/ecg_images/` com subdiretórios por classe.

**2. Memória insuficiente**

```
ResourceExhaustedError: OOM when allocating tensor
```

**Solução:** Reduza `BATCH_SIZE` ou use imagens menores.

**3. Modelo não carrega no Flask**

```
⚠ Modelo não encontrado
```

**Solução:** Execute `train.py` primeiro para gerar o modelo.

**4. GPU não detectada**

```
GPU disponível: []
```

**Solução:** Instale TensorFlow-GPU ou use Google Colab.

**5. Importação falha**

```
ModuleNotFoundError: No module named 'tensorflow'
```

**Solução:** Instale dependências: `pip install -r requirements.txt`

---

## 📚 Documentação Adicional

### Arquivos de Referência

- **Dataset:** `../../data/raw/ecg_images/README.md`
- **Relatório Técnico:** `reports/relatorio-fase04-cnn-ecg.md`
- **Governança:** `reports/relatorio-ir-alem-1-governanca.md`
- **Notebook Completo:** `notebooks/fase04_cnn_ecg_colab.ipynb`

### Links Úteis

- [TensorFlow Documentation](https://www.tensorflow.org/api_docs)
- [Keras Applications](https://keras.io/api/applications/)
- [MIT-BIH Database](https://physionet.org/content/mitdb/)
- [Kaggle ECG Dataset](https://www.kaggle.com/datasets/shayanfazeli/heartbeat)

---

## 👥 Integrantes e Divisão de Tarefas

**Equipe CardioAI:**

- **Jonas Luis da Silva** — RM561465
  - Transfer Learning
  - Implementação da CNN do zero
  - Análise de métricas
  - Protótipo Flask
  - Relatórios

- **Edson Henrique Felix Batista** — RM566321
  - Pré-processamento de dados
  - Análise de viés (IR ALÉM 1)
  - Visualizações
  - Documentação técnica

**Trabalho Colaborativo:**

- Revisão de código
- Testes e validação
- Documentação final

---

## 🚧 Limitações e Trabalhos Futuros

### Limitações Atuais

1. **Dataset Limitado**
   - Não representa toda diversidade populacional
   - Possível viés demográfico

2. **Ausência de Validação Clínica**
   - Não testado por cardiologistas
   - Não aprovado por órgãos reguladores

3. **Falta de Explicabilidade**
   - Decisões não interpretáveis
   - Necessita Grad-CAM ou LIME

4. **Contexto Acadêmico**
   - Não adequado para uso clínico real
   - Requer validação rigorosa

### Próximos Passos

1. **Técnicos**
   - Implementar Grad-CAM
   - Aplicar class weights
   - Testar ensemble learning
   - Fine-tuning de modelos

2. **Validação**
   - Testar em datasets externos
   - Validação por especialistas
   - Estudo prospectivo

3. **Governança**
   - Estabelecer comitê de ética
   - Implementar auditoria
   - Monitoramento contínuo

---

## 📄 Licença e Uso

**Licença:** MIT (para fins acadêmicos)

**Uso Permitido:**

- Educação e pesquisa
- Desenvolvimento acadêmico
- Aprendizado de IA

**Uso Proibido:**

- Diagnóstico médico real
- Aplicações comerciais sem validação
- Substituir profissionais de saúde

---

## 📞 Contato e Suporte

**Repositório:** [GitHub - CardioAI](https://github.com/jonsilva91/CardioAI)

**Issues:** Use o GitHub Issues para reportar problemas

**Dúvidas:** Consulte os relatórios em `reports/` ou abra uma issue

---

## 🙏 Agradecimentos

- **FIAP** - Pela oportunidade de desenvolver este projeto
- **MIT-BIH** - Pelo dataset público
- **Kaggle** - Pela plataforma de compartilhamento
- **TensorFlow/Keras** - Pelas ferramentas de Deep Learning
- **Comunidade Open Source** - Pelas bibliotecas e recursos

---

**CardioAI - FIAP 2026**

**Fase 4: CNN para Classificação de ECG**

**Versão:** 1.0

**Data:** Junho de 2026

---

**⚠️ LEMBRETE FINAL:**

Este projeto é **EXCLUSIVAMENTE acadêmico e educacional**.

**NÃO use para diagnóstico médico real.**

**Sempre consulte profissionais de saúde qualificados.**
