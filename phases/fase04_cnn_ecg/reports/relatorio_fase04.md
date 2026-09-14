# Relatório Curto — Fase 4 CNN aplicada a ECG

## Objetivo

Avaliar a viabilidade de uma CNN simples para classificação de imagens de ECG em contexto acadêmico e compará-la com uma abordagem de Transfer Learning (MobileNetV2).

## Base escolhida

**ECG Images derivadas do MIT-BIH Arrhythmia Database**

- Fonte: Kaggle — `analiviafr/ecg-images`
- 5 classes organizadas em subpastas: **F, N, Q, S, V**
- Total treino (completo): 37.178 imagens — desbalanceado (N=59,5%, F=1,7%)
- Experimento real: subconjunto balanceado de 600 imgs/classe → 3.000 imgs treino, 961 imgs teste

## Estratégia experimental

- Carregamento de imagens por classe (diretórios F/N/Q/S/V)
- Divisão: 80% treino / 20% validação (do subconjunto balanceado)
- CNN 2D do zero: 3 blocos Conv+Pool + Dense(128) + Dropout(0.4) + Dense(5)
- Transfer Learning: MobileNetV2 congelado + GlobalAveragePooling2D + Dense(5)
- Avaliação com matriz de confusão e classification_report por classe
- Métricas: accuracy, precision, recall e F1-score (weighted)

## Resultados (experimento executado)

**CNN do Zero — 5 épocas (Adam lr=0,001, 128×128px)**

- **accuracy: 94,59%**
- **precision (weighted): 94,62%**
- **recall (weighted): 94,59%**
- **F1-score (weighted): 94,60%**

**Transfer Learning MobileNetV2 — 3 épocas (early stop, Adam lr=0,0005)**

- accuracy: 67,64%
- precision (weighted): 75,90%
- recall (weighted): 67,64%
- F1-score (weighted): 64,11%

> **Resultado contraintuitivo:** A CNN do zero superou o Transfer Learning por 27 p.p. de accuracy. Ver discussão crítica.

## Matrizes de confusão

Figuras salvas em:

```text
phases/fase04_cnn_ecg/outputs/figures/confusion_matrix_cnn.png
phases/fase04_cnn_ecg/outputs/figures/confusion_matrix_transfer.png
```

## Discussão crítica

**Por que a CNN do zero superou o Transfer Learning?**

- A base MobileNetV2 foi mantida completamente congelada — apenas 6.405 parâmetros treináveis (Dense(5)) de um total de 2,26M. Isso é insuficiente para adaptar features do ImageNet (fotografias naturais) para imagens de ECG (sinais biomédicos com padrões de onda muito específicos).
- O Transfer Learning parou na época 3 (early stop com patience=3) — val_accuracy travou em 80%, indicando que o classificador atingiu um platô com parâmetros insuficientes.
- A CNN do zero tem 3,3M de parâmetros todos treináveis, adaptando-se diretamente ao domínio ECG.

**Recall N ≈ 0,09 no Transfer Learning — viés real documentado:**

- O modelo TL aprendeu a raramente predizer a classe "Normal" (recall ~9%), mesmo com precision alta (~98%).
- Em contexto clínico, isso geraria alarmes falsos para praticamente todos os pacientes com batimento normal.
- Demonstra que accuracy global não é suficiente — métricas por classe são essenciais em saúde.

**Limitações do experimento:**

- Dataset reduzido (USE_SMALL_DATASET=True) para viabilizar treino em CPU local
- Balanceamento artificial (600/classe) não reflete a distribuição epidemiológica real
- Ausência de GPU limitou o número de épocas e impossibilitou fine-tuning do TL
- Sem validação em datasets externos (PTB-XL, PhysioNet)
- Ausência de validação médica real — uso exclusivamente acadêmico

**Uso diagnóstico:** ⚠️ Este modelo **NÃO deve ser usado** para diagnóstico médico real. Caráter exclusivamente acadêmico.

## Próximos passos

- Fine-tuning do TL (descongelar últimas camadas + LR ≤ 0,00001 + 10-20 épocas)
- Treino com dataset completo (37.178 imagens) + class_weight para lidar com desbalanceamento
- Implementar Grad-CAM para explicabilidade
- Validar em datasets externos (PTB-XL, PhysioNet)
- Monitorar recall por classe como métrica primária de segurança
