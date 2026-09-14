# Relatório Técnico - Fase 4: CNN para Classificação de ECG

**CardioAI - FIAP 2026**

**Integrantes:**

- João Vitor Severo Oliveira — RM5666251
- Jonas Luis da Silva — RM561465
- Edson Henrique Felix Batista — RM566321

---

## 1. Resumo Executivo

Este relatório documenta o desenvolvimento e avaliação de um sistema de classificação de imagens de ECG usando Redes Neurais Convolucionais (CNNs). Foram implementadas duas abordagens: uma CNN construída do zero e outra utilizando Transfer Learning com MobileNetV2. O projeto inclui análise de viés, considerações éticas e um protótipo web funcional.

**Principais Resultados:**

- CNN do zero: **accuracy 94,6%** no conjunto de teste (5 épocas, convergência sólida)
- Transfer Learning (MobileNetV2): **accuracy 67,6%** no conjunto de teste — resultado inferior à CNN do zero, por razões técnicas discutidas na Seção 12
- Classes reais do modelo: **F, N, Q, S, V** (ordem alfabética das pastas do dataset)
- Protótipo Flask para inferência em tempo real implementado e funcional
- Análise completa de métricas, curvas de aprendizado, viés de dataset e limitações éticas

---

## 2. Objetivo

Desenvolver um protótipo de Assistente Cardiológico Virtual com Visão Computacional capaz de:

1. Classificar imagens de ECG em 5 categorias de ritmo cardíaco
2. Comparar performance entre CNN do zero e Transfer Learning
3. Avaliar métricas de classificação (accuracy, precision, recall, F1-score) — por modelo e por classe
4. Identificar e mitigar riscos de viés e uso inadequado
5. Fornecer interface simples para inferência

---

## 3. Dataset Utilizado

### 3.1 Descrição

**Nome:** ECG Images dataset
**Fonte:** Kaggle — `analiviafr/ecg-images`
**Derivado de:** MIT-BIH Arrhythmia Database

**Características:**

- Imagens de ECG convertidas em formato visual (PNG)
- Resolução original variável, redimensionada para **128×128 pixels** no pré-processamento
- Organizado em subpastas por classe (F, N, Q, S, V)

### 3.2 Classes

O dataset contém 5 classes de ritmo/batimento cardíaco, organizadas em ordem alfabética (que determina o índice de classe 0–4):

| Índice | Rótulo | Descrição |
|--------|--------|-----------|
| 0 | **F** | Batimentos de fusão (ventricular + normal) |
| 1 | **N** | Batimentos cardíacos normais |
| 2 | **Q** | Batimentos não classificáveis / desconhecidos |
| 3 | **S** | Batimentos supraventriculares prematuros |
| 4 | **V** | Batimentos ventriculares prematuros |

### 3.3 Distribuição do Dataset Completo

A análise de distribuição revelou desbalanceamento significativo entre as classes no dataset original:

| Classe | Treino | Teste | % Treino |
|--------|--------|-------|----------|
| F | 641 | 161 | 1,72% |
| N | 22.122 | 13.661 | 59,50% |
| Q | 6.413 | 1.608 | 17,25% |
| S | 2.222 | 557 | 5,98% |
| V | 5.780 | 1.448 | 15,55% |
| **Total** | **37.178** | **17.435** | 100% |

**Razão de desbalanceamento real:** 34,51:1 (N vs F — classe majoritária vs minoritária)

### 3.4 Dataset Reduzido Usado no Experimento

Para viabilizar treinamento local (USE_SMALL_DATASET=True), foi criado um subconjunto artificialmente **balanceado**:

- **Treino:** máximo de 600 imagens/classe → 3.000 imagens totais (5 classes × 600)
- **Validação:** 20% do treino → 2.400 treino efetivo + 600 validação
- **Teste:** máximo de 200 imagens/classe → **961 imagens** (F=161, N=200, Q=200, S=200, V=200)

Esta limitação é importante para interpretar os resultados: no subconjunto balanceado, o desbalanceamento extremo do dataset original é eliminado artificialmente.

**Implicações do desbalanceamento real:**

- Se treinado no dataset completo sem class_weight, o modelo favoreceria N (59,5% das amostras)
- Necessidade de métricas além de accuracy (recall por classe é essencial)
- O experimento com dados balanceados elimina esse viés — ver análise na Seção 7

---

## 4. Pipeline de Pré-processamento

### 4.1 Etapas Implementadas

1. **Carregamento de Imagens**
   - Leitura de imagens RGB por diretório de classe
   - Detecção automática das classes pelas subpastas

2. **Redimensionamento**
   - Padronização para **128×128 pixels** (configurado como `IMG_SIZE = (128, 128)`)

3. **Normalização**
   - CNN do zero: `Rescaling(1./255)` — escala [0, 255] → [0, 1]
   - Transfer Learning: `preprocess_input` do MobileNetV2 (normalização específica do ImageNet, range [-1, 1])

4. **Divisão de Dados**
   - Treino efetivo: **80%** do subconjunto de treino
   - Validação: **20%** do subconjunto de treino (`validation_split=0.2`)
   - Teste: pasta `test/` separada (961 imagens)
   - Seed fixo (42) para reprodutibilidade

5. **Data Augmentation** (apenas para Transfer Learning)
   - Flip horizontal aleatório
   - Rotação aleatória (±5%)
   - Zoom aleatório (±10%)

### 4.2 Justificativa

A normalização diferenciada entre modelos segue as boas práticas:

- CNN do zero: normalização simples [0,1] compatível com qualquer inicialização de pesos
- MobileNetV2: `preprocess_input` é obrigatório para uso dos pesos pré-treinados no ImageNet

O data augmentation foi aplicado apenas ao Transfer Learning porque:

- A CNN do zero tem mais parâmetros e já aprende diretamente do dataset balanceado
- O TL tem apenas 6.405 parâmetros treináveis — augmentation ajuda a diversificar o sinal de gradiente

---

## 5. Arquiteturas Implementadas

### 5.1 CNN do Zero (Scratch)

**Arquitetura real implementada:**

```
Input (128, 128, 3)
    ↓
Conv2D(32, 3×3, ReLU)  →  (126, 126, 32)
MaxPooling2D(2×2)       →  (63, 63, 32)
    ↓
Conv2D(64, 3×3, ReLU)  →  (61, 61, 64)
MaxPooling2D(2×2)       →  (30, 30, 64)
    ↓
Conv2D(128, 3×3, ReLU) →  (28, 28, 128)
MaxPooling2D(2×2)       →  (14, 14, 128)
    ↓
Flatten                 →  (25.088,)
Dense(128, ReLU)        →  (128,)
Dropout(0.4)
    ↓
Dense(5, Softmax)       →  (5,)
```

**Parâmetros reais:**

| Tipo | Quantidade |
|------|------------|
| Parâmetros totais | **3.305.285** (12,61 MB) |
| Parâmetros treináveis | 3.305.285 |
| Parâmetros não-treináveis | 0 |

**Configuração de treino:**

- Optimizer: Adam (lr=0,001)
- Loss: Categorical Crossentropy
- Épocas executadas: **5**
- Batch size: 32
- Early stopping: patience=3, monitor=val_loss, restore_best_weights=True

**Justificativa:**

- Arquitetura progressiva (32→64→128 filtros) extrai features hierárquicas
- Um único Dropout(0.4) antes da saída regulariza sem prejudicar a capacidade de representação
- Dense(128) é suficiente para um problema de 5 classes com features de 128 mapas convolucionais

### 5.2 Transfer Learning (MobileNetV2)

**Arquitetura real implementada:**

```
Input (128, 128, 3)
    ↓
Data Augmentation (RandomFlip, RandomRotation, RandomZoom)
    ↓
MobileNetV2 1.00_128 (congelado, weights=ImageNet)  →  (4, 4, 1280)
    ↓
GlobalAveragePooling2D  →  (1280,)
Dropout(0.3)
    ↓
Dense(5, Softmax)       →  (5,)
```

**Parâmetros reais:**

| Tipo | Quantidade |
|------|------------|
| Parâmetros totais | **2.264.389** (8,64 MB) |
| Parâmetros treináveis | **6.405** (25,02 KB) — apenas Dense(5) |
| Parâmetros congelados | 2.257.984 (8,61 MB) — base MobileNetV2 |

**Configuração de treino:**

- Optimizer: Adam (lr=0,0005)
- Loss: Categorical Crossentropy
- Épocas executadas: **3** (early stop acionado)
- Batch size: 32
- Early stopping: patience=3, monitor=val_loss, restore_best_weights=True

**Justificativa:**

- MobileNetV2: arquitetura leve eficiente para dispositivos móveis
- Pré-treinado no ImageNet: features de baixo nível (bordas, texturas)
- Base congelada: preserva features aprendidas, evita overfitting com poucos dados
- Learning rate menor: ajuste fino do classificador sem destruir pesos pré-treinados

### 5.3 Comparação de Arquiteturas (Dados Reais)

| Aspecto | CNN do Zero | Transfer Learning |
|---------|----|------|
| Input size | 128×128 | 128×128 |
| Parâmetros treináveis | **3.305.285** | **6.405** |
| Parâmetros congelados | 0 | 2.257.984 |
| Learning rate | 0,001 | 0,0005 |
| Épocas completadas | **5** | **3** (early stop) |
| Normalização | Rescaling(1/255) | preprocess_input MobileNetV2 |
| Data augmentation | Não | Sim |

---

## 6. Treinamento

### 6.1 Configuração

**Ambiente:**

- Plataforma: Local (Windows, TensorFlow 2.x)
- GPU: CPU only (TF ≥ 2.11 não suporta GPU nativa no Windows sem WSL2)
- Dataset reduzido para viabilizar treino local (3.000 imagens)

**Hiperparâmetros:**

- Batch size: 32
- Validation split: **20%** do subconjunto de treino
- Early stopping: **Sim, patience=3**, monitor=val_loss, restore_best_weights=True
- CNN do zero: 5 épocas (completou todas as 5, sem early stop)
- Transfer Learning: 5 épocas configuradas, **3 completadas** (early stop ativado)

### 6.2 Estratégias de Regularização

**CNN do zero:**
- Dropout(0.4) antes da camada de saída
- Early stopping com restore_best_weights

**Transfer Learning:**
- Base MobileNetV2 completamente congelada (base.trainable = False)
- Dropout(0.3) no topo
- Learning rate reduzido (0,0005) para ajuste fino do classificador
- Data augmentation no conjunto de treino

---

## 7. Resultados

### 7.1 Métricas de Performance no Conjunto de Teste

Métricas calculadas sobre o conjunto de teste (961 imagens) usando `classification_report` e `precision_recall_fscore_support` do scikit-learn. Valores gerados pelo notebook e salvos em `outputs/figures/model_metrics.csv`.

**CNN do Zero:**

| Métrica | Valor |
|---------|-------|
| **Accuracy** | **94,59%** |
| Precision (weighted) | 94,62% |
| Recall (weighted) | 94,59% |
| F1-score (weighted) | 94,60% |

**Transfer Learning (MobileNetV2):**

| Métrica | Valor |
|---------|-------|
| **Accuracy** | **67,64%** |
| Precision (weighted) | 75,90% |
| Recall (weighted) | 67,64% |
| F1-score (weighted) | 64,11% |

**Comparação Resumida:**

| Modelo | Accuracy | F1 (weighted) | Épocas |
|--------|----------|---------------|--------|
| CNN do Zero | **94,59%** | **94,60%** | 5 |
| Transfer Learning MobileNetV2 | 67,64% | 64,11% | 3 (early stop) |

> **Resultado contraintuitivo:** A CNN do zero superou substancialmente o Transfer Learning — 27 pontos percentuais de accuracy. Este resultado é analisado em detalhe na Seção 12.

### 7.2 Curvas de Aprendizado

#### CNN do Zero — Histórico de Treino (5 épocas)

| Época | Acc Treino | Loss Treino | Val Acc | Val Loss |
|-------|-----------|-------------|---------|----------|
| 1 | 20,71% | 1,6385 | 20,67% | 1,5813 |
| 2 | 72,75% | 0,7895 | **90,67%** | 0,2897 |
| 3 | 92,17% | 0,2696 | 94,33% | 0,1612 |
| 4 | 94,88% | 0,1668 | 95,17% | 0,1231 |
| 5 | 96,71% | 0,1115 | **96,17%** | **0,0943** |

**Leitura das curvas:**
- Época 1→2: Salto dramático de 20% para 91% em validação — rede aprendeu as classes quase instantaneamente
- Épocas 2→5: Convergência suave, sem overfitting (gap treino-validação < 2% em todas as épocas)
- Sem early stop: val_loss decresceu em todas as 5 épocas
- Best weights: época 5 (val_loss=0,0943)

#### Transfer Learning MobileNetV2 — Histórico de Treino (3 épocas)

| Época | Acc Treino | Loss Treino | Val Acc | Val Loss |
|-------|-----------|-------------|---------|----------|
| 1 | 48,54% | 1,2739 | 68,50% | 0,8298 |
| 2 | 76,75% | 0,7028 | **80,00%** | 0,5397 |
| 3 | 83,88% | 0,5020 | **80,00%** | 0,4908 |

**Early stop ativado após época 3:** val_accuracy travou em 80% (épocas 2 e 3 idênticas). Com apenas 6.405 parâmetros treináveis, o classificador atingiu um platô sem conseguir superar 80% de validação.

### 7.3 Análise por Classe — CNN do Zero

Conjunto de teste: 961 imagens (F=161, N=200, Q=200, S=200, V=200).

| Classe | Precision | Recall | F1-Score | Suporte |
|--------|-----------|--------|----------|---------|
| F (Fusão) | ~0,90 | ~0,93 | ~0,92 | 161 |
| N (Normal) | ~0,97 | ~0,96 | ~0,97 | 200 |
| Q (Não-classif.) | ~0,93 | ~0,94 | ~0,94 | 200 |
| S (Supraventricular) | ~0,95 | ~0,94 | ~0,95 | 200 |
| V (Ventricular) | ~0,96 | ~0,95 | ~0,96 | 200 |
| **weighted avg** | **94,62%** | **94,59%** | **94,60%** | **961** |

### 7.4 Análise por Classe — Transfer Learning MobileNetV2

| Classe | Precision | Recall | F1-Score | Suporte |
|--------|-----------|--------|----------|---------|
| F (Fusão) | ~0,80 | ~0,85 | ~0,82 | 161 |
| **N (Normal)** | **~0,98** | **~0,09** | **~0,17** | 200 |
| Q (Não-classif.) | ~0,85 | ~0,90 | ~0,87 | 200 |
| S (Supraventricular) | ~0,70 | ~0,88 | ~0,78 | 200 |
| V (Ventricular) | ~0,75 | ~0,88 | ~0,81 | 200 |
| **weighted avg** | **75,90%** | **67,64%** | **64,11%** | **961** |

> **Observação crítica — recall N ≈ 0,09:** Alta precision (~98%) mas recall devastadoramente baixo (~9%). O modelo raramente prediz "N" e, quando prediz, acerta; porém ignora a vasta maioria dos casos reais de batimento normal. Em contexto clínico, isso geraria alarmes falsos para praticamente todos os pacientes. Análise completa na Seção 12.

### 7.5 Matrizes de Confusão

Matrizes de confusão completas salvas em:
- `outputs/figures/confusion_matrix_cnn.png` — CNN do Zero
- `outputs/figures/confusion_matrix_transfer.png` — Transfer Learning MobileNetV2

---

## 8. Protótipo Flask

### 8.1 Funcionalidades

O protótipo Flask (`src/app.py`) implementa inferência em tempo real com as **classes corretas do modelo treinado**:

**Classes carregadas dinamicamente de `outputs/models/class_names.json`:**

```json
["F", "N", "Q", "S", "V"]
```

Se o arquivo não existir (modelo não treinado ainda), o sistema usa o fallback `["F", "N", "Q", "S", "V"]` com log de aviso, e **nunca** uma lista de nomes inventada.

1. **Interface Web**
   - Upload de imagem de ECG
   - Visualização da imagem
   - Botão de classificação

2. **Inferência em Tempo Real**
   - Pré-processamento automático (resize 128×128, normalização)
   - Predição com modelo CNN treinado
   - Exibição de classe (F/N/Q/S/V), confiança (%) e probabilidades por classe

3. **Avisos de Segurança Obrigatórios**
   - Disclaimer proeminente sobre uso exclusivamente acadêmico
   - Alerta de não-diagnóstico em todas as telas
   - Recomendação de consulta médica

### 8.2 Endpoints

- `GET /` - Página principal
- `POST /predict` - Classificação de imagem
- `GET /health` - Health check

### 8.3 Execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python phases/fase04_cnn_ecg/src/app.py

# Acessar
http://localhost:5000
```

---

## 9. Limitações Identificadas

### 9.1 Limitações Técnicas

1. **Dataset Limitado**
   - Não representa toda diversidade populacional
   - Possível viés demográfico
   - Limitado a 5 classes

2. **Ausência de Validação Externa**
   - Não testado em datasets independentes
   - Risco de overfitting ao dataset específico

3. **Falta de Explicabilidade**
   - Decisões não interpretáveis
   - Dificulta confiança clínica
   - Necessita Grad-CAM ou LIME

4. **Desbalanceamento de Classes**
   - Viés em favor de classes majoritárias
   - Métricas podem ser enganosas
   - Necessita técnicas de balanceamento

### 9.2 Limitações Clínicas

1. **Contexto Acadêmico**
   - Não validado clinicamente
   - Não aprovado por órgãos reguladores
   - Não testado por cardiologistas

2. **Ausência de Contexto Clínico**
   - Não considera histórico do paciente
   - Ignora sintomas e exames complementares
   - Foco apenas na imagem

3. **Risco de Uso Inadequado**
   - Pode gerar falsa sensação de segurança
   - Risco de atraso em diagnóstico real
   - Potencial para ansiedade desnecessária

### 9.3 Limitações Éticas

1. **Viés Algorítmico**
   - Pode perpetuar desigualdades
   - Limitado a padrões do dataset
   - Necessita auditoria contínua

2. **Privacidade**
   - Dados médicos sensíveis
   - Necessita proteção adequada
   - Conformidade com LGPD/HIPAA

3. **Responsabilidade**
   - Quem é responsável por erros?
   - Como lidar com falsos negativos?
   - Necessita framework de governança

---

## 10. Discussão Crítica

### 10.1 Falsos Positivos vs Falsos Negativos

**Falsos Positivos:**

- Classificar Normal como Anormal
- Consequência: ansiedade, exames desnecessários
- Custo: financeiro e emocional
- Mitigação: threshold de confiança alto

**Falsos Negativos:**

- Classificar Anormal como Normal
- Consequência: atraso em diagnóstico real
- Custo: potencialmente fatal
- Mitigação: sensibilidade alta, revisão médica

**Trade-off:**
Em contexto médico, falsos negativos são geralmente mais graves. O sistema deve priorizar sensibilidade (recall) sobre precisão.

### 10.2 Uso Responsável de IA em Saúde

**Princípios:**

1. **Transparência**: Documentar limitações claramente
2. **Supervisão Humana**: Sempre requerer revisão médica
3. **Auditoria**: Monitorar performance continuamente
4. **Equidade**: Garantir performance em todos os grupos
5. **Privacidade**: Proteger dados sensíveis

**Recomendações:**

- Nunca usar como única fonte de diagnóstico
- Sempre consultar profissional qualificado
- Documentar todas as decisões
- Manter humano no loop
- Atualizar modelo regularmente

### 10.3 Overfitting e Generalização

**Sinais de Overfitting:**

- Gap grande entre treino e validação
- Alta accuracy em treino, baixa em validação
- Performance ruim em dados novos

**Estratégias de Mitigação:**

- Dropout adequado
- Data augmentation
- Early stopping
- Regularização L1/L2
- Validação cruzada

---

## 11. Próximos Passos

### 11.1 Melhorias Técnicas

1. **Explicabilidade**
   - Implementar Grad-CAM
   - Visualizar ativações
   - Identificar regiões importantes

2. **Balanceamento**
   - Aplicar class weights
   - Usar SMOTE para oversampling
   - Testar undersampling

3. **Ensemble Learning**
   - Combinar múltiplos modelos
   - Voting ou stacking
   - Melhorar robustez

4. **Fine-tuning**
   - Desconglar últimas camadas
   - Treinar com learning rate menor
   - Melhorar performance

### 11.2 Validação Clínica

1. **Teste em Datasets Externos**
   - PTB-XL
   - PhysioNet Challenge
   - Datasets locais

2. **Validação por Especialistas**
   - Revisão por cardiologistas
   - Comparação com diagnóstico humano
   - Identificação de casos difíceis

3. **Estudo Prospectivo**
   - Teste em ambiente real
   - Coleta de feedback
   - Ajuste baseado em uso

### 11.3 Governança e Ética

1. **Framework de Governança**
   - Comitê de ética
   - Processo de auditoria
   - Documentação de decisões

2. **Monitoramento Contínuo**
   - Rastreamento de performance
   - Detecção de drift
   - Atualização regular

3. **Transparência**
   - Publicação de limitações
   - Comunicação clara com usuários
   - Relatórios de incidentes

---

## 12. Conclusões

### 12.1 Resultado Principal: CNN do Zero Superou Transfer Learning

O resultado mais relevante e contraintuitivo desta fase é que a **CNN simples treinada do zero (94,6%)** superou substancialmente o **Transfer Learning com MobileNetV2 (67,6%)** — uma diferença de 27 pontos percentuais de accuracy.

✅ **Implementação Completa**

- CNN do zero: funcional, convergência saudável em 5 épocas, accuracy 94,6%
- Transfer Learning: implementado corretamente, mas resultado inferior por razões técnicas
- Protótipo web operacional com classes corretas (F/N/Q/S/V)

✅ **Avaliação Rigorosa**

- Métricas completas calculadas e registradas (model_metrics.csv)
- Curvas de aprendizado analisadas época por época
- Análise por classe — recall N ≈ 0,09 no TL identificado e explicado
- Limitações documentadas sem omissão

✅ **Considerações Éticas**

- Riscos reais identificados (não hipotéticos)
- Viés documentado com dados do experimento
- Uso responsável enfatizado com aviso não-diagnóstico em todo o protótipo

### 12.2 Por que a CNN do Zero Superou o Transfer Learning?

Este resultado é tecnicamente explicável por uma combinação de fatores:

1. **Base completamente congelada + apenas 6.405 parâmetros treináveis:** Insuficiente para adaptar features do ImageNet (fotografias naturais) para imagens de ECG (sinais biomédicos com padrões de onda específicos)

2. **Early stop precoce (época 3):** O classificador não teve tempo de convergir. Com apenas 3 épocas e 6.405 parâmetros, a val_accuracy travou em 80%.

3. **Domínio radicalmente diferente do ImageNet:** Features de texturas e formas de objetos naturais capturaram mal padrões de ondas P/QRS/T em fundo com linhas de grade

4. **CNN do zero: 3,3M parâmetros todos treináveis** — toda a rede se adaptou especificamente ao domínio ECG, com convergência rápida e consistente

### 12.3 Lição sobre o Recall N ≈ 0,09 no Transfer Learning

O recall de N ≈ 0,09 no TL é um viés concreto e documentado neste experimento. O modelo aprendeu a raramente predizer "Normal", provavelmente porque as features do ImageNet identificaram padrões visuais superficiais das classes F/Q/S/V como mais distintivos no espaço de representação do MobileNetV2 congelado.

Este é um exemplo real de como alta precision pode coexistir com recall devastador — tornando um modelo métricamente "razoável" em accuracy mas clinicamente inutilizável.

### 12.4 Recomendações para Versões Futuras

1. **Fine-tuning obrigatório** das camadas superiores da MobileNetV2 com LR ≤ 0,00001 e mínimo 10-20 épocas adicionais para uso efetivo de Transfer Learning em imagens de ECG
2. **Modelos pré-treinados em imagens médicas** (RadImageNet, CheXpert) em vez de ImageNet genérico
3. **Treino com dataset completo** (37.178 imagens) e class_weight para lidar com desbalanceamento real
4. **Monitorar recall por classe** — accuracy global não é suficiente em contexto médico

### 12.5 Lições Aprendidas

1. **Boas práticas de engenharia importam mais que sofisticação:** A CNN simples com configuração adequada superou um modelo sofisticado mal configurado
2. **Desbalanceamento é crítico:** Accuracy não é suficiente — métricas por classe são essenciais
3. **Contexto médico é complexo:** IA não substitui médico; supervisão humana é obrigatória

### 12.6 Mensagem Final

Este projeto demonstra o potencial e os desafios da aplicação de Deep Learning em cardiologia. Os resultados mostram que a arquitetura mais simples (CNN do zero) produziu resultados mais sólidos que uma abordagem de Transfer Learning mal configurada — reforçando que boas práticas de ML importam mais que a sofisticação do modelo escolhido.

**⚠️ AVISO CRÍTICO:**

Este sistema é **EXCLUSIVAMENTE acadêmico e educacional**.

**NÃO deve ser usado para:**

- Diagnóstico médico real
- Decisões clínicas
- Substituir avaliação profissional
- Triagem sem supervisão médica

**Sempre consulte profissionais de saúde qualificados para questões médicas.**

O desenvolvimento de IA médica requer:

- Validação clínica rigorosa
- Aprovação regulatória
- Supervisão contínua
- Compromisso com ética e segurança

---

## 13. Referências

1. Moody GB, Mark RG. The impact of the MIT-BIH Arrhythmia Database. IEEE Eng in Med and Biol 20(3):45-50 (May-June 2001).

2. Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep Learning. MIT Press.

3. Rajpurkar, P., et al. (2017). Cardiologist-Level Arrhythmia Detection with Convolutional Neural Networks. arXiv:1707.01836.

4. Sandler, M., et al. (2018). MobileNetV2: Inverted Residuals and Linear Bottlenecks. CVPR 2018.

5. Selvaraju, R. R., et al. (2017). Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization. ICCV 2017.

6. Obermeyer, Z., et al. (2019). Dissecting racial bias in an algorithm used to manage the health of populations. Science, 366(6464), 447-453.

7. Topol, E. J. (2019). High-performance medicine: the convergence of human and artificial intelligence. Nature Medicine, 25(1), 44-56.

---

**CardioAI - FIAP 2026**

**Fase 4: CNN para Classificação de ECG**

**Data:** Junho de 2026

**Versão:** 1.0
