# IR ALÉM 1: Ética e Governança em Visão Computacional Médica

**CardioAI - Fase 4**

**FIAP 2026**

---

## 1. Introdução

Este relatório aborda os aspectos éticos e de governança relacionados ao uso de Visão Computacional e Deep Learning para classificação de imagens de ECG. O objetivo é identificar riscos, analisar vieses e propor estratégias de mitigação para garantir o uso responsável de IA em contexto médico.

---

## 2. Análise de Desbalanceamento do Dataset

### 2.1 Identificação do Problema

O dataset ECG Images apresenta **desbalanceamento significativo** entre as classes:

**Distribuição Típica Observada:**

- **Normal (N)**: ~70-80% das amostras
- **Supraventricular (S)**: ~5-10%
- **Ventricular (V)**: ~5-10%
- **Fusion (F)**: ~1-3%
- **Unknown (Q)**: ~1-3%

**Razão de Desbalanceamento:** Até 80:1 entre classe majoritária e minoritária

### 2.2 Impactos do Desbalanceamento

#### 2.2.1 Viés de Predição

**Problema:**
O modelo tende a favorecer a classe majoritária (Normal) para maximizar accuracy geral.

**Consequências:**

- **Falsos Negativos em Classes Minoritárias**: Arritmias graves podem ser classificadas como normais
- **Baixa Sensibilidade**: Dificuldade em detectar casos raros mas críticos
- **Métricas Enganosas**: Alta accuracy geral mascara baixa performance em classes importantes

**Exemplo Prático:**

```
Cenário: 1000 amostras (900 Normal, 100 Anormal)
Modelo ingênuo: Classifica tudo como Normal
Accuracy: 90% (enganosa!)
Recall para Anormal: 0% (crítico!)
```

#### 2.2.2 Viés de Representação

**Problema:**
Classes minoritárias têm menos exemplos para aprendizado.

**Consequências:**

- Modelo aprende menos padrões de arritmias raras
- Maior variância nas predições de classes minoritárias
- Dificuldade em generalizar para novos casos

#### 2.2.3 Viés Clínico

**Problema:**
Desbalanceamento pode não refletir prevalência real na população.

**Consequências:**

- Modelo otimizado para dataset específico
- Performance ruim em populações diferentes
- Risco de perpetuar desigualdades em saúde

### 2.3 Visualização do Desbalanceamento

O notebook inclui análise visual completa:

1. **Gráfico de Barras**: Quantidade absoluta por classe
2. **Gráfico de Pizza**: Proporção percentual
3. **Tabela Detalhada**: Contagens e percentuais
4. **Razão de Desbalanceamento**: Métrica quantitativa

**Código de Análise:**

```python
# Calcular distribuição
class_counts = {}
for cls in classes:
    class_dir = os.path.join(DATA_DIR, cls)
    class_counts[cls] = len(os.listdir(class_dir))

# Identificar desbalanceamento
max_count = max(class_counts.values())
min_count = min(class_counts.values())
imbalance_ratio = max_count / min_count

if imbalance_ratio > 2:
    print("⚠️ Dataset significativamente desbalanceado!")
```

---

## 3. Riscos de Viés Algorítmico

### 3.1 Tipos de Viés Identificados

#### 3.1.1 Viés de Seleção

**Origem:**

- Dataset coletado de população específica
- Possível sub-representação de grupos demográficos
- Limitado a equipamentos e protocolos específicos

**Impacto:**

- Modelo pode não funcionar bem em outras populações
- Risco de disparidade em performance entre grupos
- Perpetuação de desigualdades em saúde

#### 3.1.2 Viés de Medição

**Origem:**

- Qualidade variável de imagens
- Diferentes equipamentos de ECG
- Variação em técnicas de aquisição

**Impacto:**

- Sensibilidade a artefatos específicos
- Dificuldade com imagens de qualidade diferente
- Falhas em condições não representadas no treino

#### 3.1.3 Viés de Rotulação

**Origem:**

- Erros humanos na classificação original
- Inconsistência entre anotadores
- Casos ambíguos ou limítrofes

**Impacto:**

- Modelo aprende padrões incorretos
- Propagação de erros humanos
- Dificuldade em casos complexos

#### 3.1.4 Viés de Agregação

**Origem:**

- Tratamento uniforme de subgrupos heterogêneos
- Ignorar variações individuais
- Simplificação excessiva de categorias

**Impacto:**

- Performance ruim em subgrupos específicos
- Perda de nuances clínicas importantes
- Decisões inadequadas para casos atípicos

### 3.2 Análise de Erros por Classe

O sistema implementa análise detalhada de erros:

```python
def analyze_errors(y_true, y_pred, classes):
    for i, cls in enumerate(classes):
        class_indices = np.where(y_true == i)[0]
        class_predictions = y_pred[class_indices]

        # Calcular taxa de erro
        errors = np.sum(class_predictions != i)
        error_rate = (errors / len(class_indices)) * 100

        # Identificar confusões
        wrong_predictions = class_predictions[class_predictions != i]
        unique, counts = np.unique(wrong_predictions, return_counts=True)

        print(f"{cls}: Taxa de erro = {error_rate:.2f}%")
        print(f"Confundido com: {dict(zip(classes[unique], counts))}")
```

**Insights Esperados:**

- Classes minoritárias: maior taxa de erro
- Confusões sistemáticas entre classes similares
- Necessidade de mais dados ou features específicas

---

## 4. Falsos Positivos vs Falsos Negativos

### 4.1 Definições no Contexto Médico

#### Falso Positivo (FP)

**Definição:** Classificar ECG normal como anormal

**Exemplo:**

- Paciente saudável classificado com arritmia
- ECG normal identificado como Ventricular

**Consequências:**

- ✗ Ansiedade e estresse desnecessários
- ✗ Exames complementares desnecessários
- ✗ Custos financeiros adicionais
- ✗ Sobrecarga do sistema de saúde
- ✗ Possível tratamento desnecessário

**Gravidade:** Moderada a Alta

#### Falso Negativo (FN)

**Definição:** Classificar ECG anormal como normal

**Exemplo:**

- Arritmia grave classificada como normal
- Batimento ventricular identificado como normal

**Consequências:**

- ✗✗✗ Atraso em diagnóstico crítico
- ✗✗✗ Progressão de doença não tratada
- ✗✗✗ Risco de eventos cardíacos graves
- ✗✗✗ Potencialmente fatal
- ✗✗✗ Responsabilidade legal

**Gravidade:** Crítica

### 4.2 Trade-off e Decisão Clínica

**Princípio Fundamental:**

> Em contexto médico, **falsos negativos são geralmente mais graves** que falsos positivos.

**Implicações:**

1. **Priorizar Sensibilidade (Recall)**
   - Detectar o máximo de casos positivos
   - Aceitar mais falsos positivos
   - Reduzir falsos negativos críticos

2. **Ajustar Threshold de Decisão**
   - Threshold mais baixo → mais sensível
   - Mais alertas, mas menos casos perdidos
   - Revisão humana filtra falsos positivos

3. **Implementar Sistema de Alerta**
   - Casos suspeitos sempre revisados
   - Múltiplos níveis de confiança
   - Escalação para especialista

### 4.3 Análise Quantitativa

**Matriz de Confusão Interpretada:**

```
                Predito
              N    S    V    F    Q
Real    N   [TN] [FP] [FP] [FP] [FP]
        S   [FN] [TP] [FP] [FP] [FP]
        V   [FN] [FP] [TP] [FP] [FP]
        F   [FN] [FP] [FP] [TP] [FP]
        Q   [FN] [FP] [FP] [FP] [TP]
```

**Análise Crítica:**

- **FN em V (Ventricular)**: Extremamente grave
- **FN em S (Supraventricular)**: Muito grave
- **FP em N (Normal)**: Menos grave, mas custoso
- **Confusão F↔V**: Requer atenção especial

### 4.4 Métricas Apropriadas

**Além de Accuracy:**

1. **Recall (Sensibilidade)**
   - Proporção de positivos corretamente identificados
   - Crítico para não perder casos graves
   - Fórmula: TP / (TP + FN)

2. **Precision**
   - Proporção de predições positivas corretas
   - Importante para evitar alarmes falsos
   - Fórmula: TP / (TP + FP)

3. **F1-Score**
   - Média harmônica de Precision e Recall
   - Balanceia ambos os aspectos
   - Fórmula: 2 × (Precision × Recall) / (Precision + Recall)

4. **Specificity**
   - Proporção de negativos corretamente identificados
   - Complementa Recall
   - Fórmula: TN / (TN + FP)

**Recomendação:**
Priorizar **Recall** para classes críticas (V, S) mesmo que reduza Precision geral.

---

## 5. Estratégias de Mitigação

### 5.1 Balanceamento de Classes

#### 5.1.1 Class Weights

**Implementação:**

```python
from sklearn.utils.class_weight import compute_class_weight

# Calcular pesos
class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)

# Aplicar no treinamento
model.fit(
    train_data,
    class_weight=dict(enumerate(class_weights)),
    ...
)
```

**Vantagens:**

- Simples de implementar
- Não altera dataset
- Penaliza erros em classes minoritárias

**Desvantagens:**

- Pode causar overfitting em classes pequenas
- Requer ajuste fino de pesos

#### 5.1.2 Oversampling (SMOTE)

**Implementação:**

```python
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```

**Vantagens:**

- Aumenta exemplos de classes minoritárias
- Cria variações sintéticas
- Melhora aprendizado

**Desvantagens:**

- Pode gerar exemplos irrealistas
- Aumenta tempo de treino
- Risco de overfitting

#### 5.1.3 Undersampling

**Implementação:**

```python
from imblearn.under_sampling import RandomUnderSampler

rus = RandomUnderSampler(random_state=42)
X_resampled, y_resampled = rus.fit_resample(X_train, y_train)
```

**Vantagens:**

- Reduz dominância da classe majoritária
- Treino mais rápido
- Menos overfitting

**Desvantagens:**

- Perde informação da classe majoritária
- Pode reduzir performance geral

#### 5.1.4 Ensemble com Balanceamento

**Implementação:**

```python
from imblearn.ensemble import BalancedRandomForestClassifier

# Ou criar ensemble manual
models = []
for i in range(n_models):
    # Criar subset balanceado
    X_balanced, y_balanced = create_balanced_subset(X_train, y_train)
    model = train_model(X_balanced, y_balanced)
    models.append(model)

# Predição por votação
predictions = majority_vote(models, X_test)
```

**Vantagens:**

- Combina múltiplas estratégias
- Mais robusto
- Melhor generalização

### 5.2 Validação Externa

#### 5.2.1 Cross-Validation Estratificada

**Implementação:**

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for train_idx, val_idx in skf.split(X, y):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]

    model = train_model(X_train, y_train)
    evaluate_model(model, X_val, y_val)
```

**Benefícios:**

- Avaliação mais robusta
- Mantém proporção de classes
- Reduz variância de estimativas

#### 5.2.2 Teste em Datasets Independentes

**Estratégia:**

1. Treinar no ECG Images (MIT-BIH)
2. Testar no PTB-XL
3. Testar no PhysioNet Challenge
4. Comparar performance

**Objetivo:**

- Verificar generalização
- Identificar overfitting
- Validar robustez

#### 5.2.3 Validação por Especialistas

**Processo:**

1. Selecionar casos desafiadores
2. Obter diagnóstico de cardiologistas
3. Comparar com predições do modelo
4. Analisar discordâncias
5. Ajustar modelo baseado em feedback

**Importância:**

- Validação clínica real
- Identificação de casos limítrofes
- Melhoria contínua

### 5.3 Explicabilidade (XAI)

#### 5.3.1 Grad-CAM

**Implementação:**

```python
import tensorflow as tf

def make_gradcam_heatmap(img_array, model, last_conv_layer_name):
    grad_model = tf.keras.models.Model(
        [model.inputs],
        [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)
        class_channel = predictions[:, class_idx]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)

    return heatmap.numpy()
```

**Benefícios:**

- Visualiza regiões importantes
- Aumenta confiança clínica
- Identifica erros do modelo
- Facilita debugging

#### 5.3.2 LIME (Local Interpretable Model-agnostic Explanations)

**Implementação:**

```python
from lime import lime_image

explainer = lime_image.LimeImageExplainer()
explanation = explainer.explain_instance(
    image,
    model.predict,
    top_labels=5,
    hide_color=0,
    num_samples=1000
)
```

**Benefícios:**

- Explicações locais
- Independente de modelo
- Interpretável por humanos

#### 5.3.3 Attention Mechanisms

**Implementação:**

```python
# Adicionar camada de atenção
attention = layers.Attention()([query, value])
```

**Benefícios:**

- Atenção aprendida automaticamente
- Integrado ao modelo
- Melhora performance e interpretabilidade

### 5.4 Revisão Clínica Obrigatória

#### 5.4.1 Sistema de Níveis de Confiança

**Implementação:**

```python
def classify_with_confidence(prediction_probs):
    max_prob = np.max(prediction_probs)
    predicted_class = np.argmax(prediction_probs)

    if max_prob > 0.9:
        confidence = "ALTA"
        action = "Informar resultado"
    elif max_prob > 0.7:
        confidence = "MÉDIA"
        action = "Revisão recomendada"
    else:
        confidence = "BAIXA"
        action = "Revisão obrigatória"

    return predicted_class, confidence, action
```

**Níveis:**

1. **Alta Confiança (>90%)**: Informar com disclaimer
2. **Média Confiança (70-90%)**: Revisão recomendada
3. **Baixa Confiança (<70%)**: Revisão obrigatória

#### 5.4.2 Workflow de Revisão

```
Imagem ECG
    ↓
Predição IA
    ↓
Confiança?
    ↓
├─ Alta → Informar + Disclaimer
├─ Média → Fila de Revisão (Prioridade Normal)
└─ Baixa → Fila de Revisão (Prioridade Alta)
    ↓
Cardiologista
    ↓
Diagnóstico Final
```

#### 5.4.3 Auditoria de Decisões

**Registro Obrigatório:**

- Timestamp
- Imagem original
- Predição do modelo
- Confiança
- Revisão humana (se aplicável)
- Diagnóstico final
- Ações tomadas

**Objetivo:**

- Rastreabilidade completa
- Análise de erros
- Melhoria contínua
- Responsabilidade legal

### 5.5 Monitoramento Contínuo

#### 5.5.1 Detecção de Data Drift

**Implementação:**

```python
from scipy.stats import ks_2samp

def detect_drift(train_data, production_data, threshold=0.05):
    statistic, p_value = ks_2samp(train_data, production_data)

    if p_value < threshold:
        print("⚠️ Data drift detectado!")
        return True
    return False
```

**Monitorar:**

- Distribuição de features
- Distribuição de predições
- Taxa de confiança
- Performance por classe

#### 5.5.2 Performance Tracking

**Métricas a Monitorar:**

```python
metrics = {
    'accuracy': [],
    'precision_per_class': {},
    'recall_per_class': {},
    'f1_per_class': {},
    'confusion_matrix': [],
    'prediction_confidence': [],
    'inference_time': [],
    'error_rate_per_class': {}
}
```

**Alertas:**

- Queda de accuracy > 5%
- Recall crítico < 80%
- Aumento de falsos negativos
- Drift significativo

#### 5.5.3 Retreinamento Periódico

**Estratégia:**

1. **Coleta de Novos Dados**
   - Casos revisados por especialistas
   - Erros identificados
   - Novos padrões

2. **Avaliação de Necessidade**
   - Performance atual vs baseline
   - Quantidade de novos dados
   - Mudanças no domínio

3. **Retreinamento**
   - Combinar dados antigos e novos
   - Validar em holdout set
   - A/B testing antes de deploy

4. **Validação**
   - Performance em dados novos
   - Não degradar em dados antigos
   - Aprovação de especialistas

---

## 6. Framework de Governança

### 6.1 Princípios Éticos

#### 6.1.1 Beneficência

**Definição:** Agir no melhor interesse do paciente

**Aplicação:**

- Priorizar segurança sobre performance
- Sempre incluir supervisão humana
- Transparência sobre limitações

#### 6.1.2 Não-Maleficência

**Definição:** Não causar dano

**Aplicação:**

- Minimizar falsos negativos
- Evitar viés discriminatório
- Proteger privacidade

#### 6.1.3 Autonomia

**Definição:** Respeitar decisões do paciente

**Aplicação:**

- Consentimento informado
- Direito de recusar IA
- Explicação clara de resultados

#### 6.1.4 Justiça

**Definição:** Distribuição equitativa de benefícios

**Aplicação:**

- Performance igual em todos os grupos
- Acesso equitativo
- Não perpetuar desigualdades

### 6.2 Comitê de Ética em IA

**Composição:**

- Cardiologistas
- Cientistas de dados
- Especialistas em ética
- Representantes de pacientes
- Advogados especializados

**Responsabilidades:**

- Aprovar novos modelos
- Revisar incidentes
- Atualizar políticas
- Auditar decisões

### 6.3 Conformidade Regulatória

#### 6.3.1 LGPD (Brasil)

- Consentimento explícito
- Direito ao esquecimento
- Portabilidade de dados
- Segurança adequada

#### 6.3.2 HIPAA (EUA)

- Proteção de PHI
- Controle de acesso
- Auditoria de logs
- Criptografia

#### 6.3.3 GDPR (Europa)

- Direito à explicação
- Privacidade por design
- Avaliação de impacto
- Notificação de violações

#### 6.3.4 Anvisa/FDA

- Validação clínica
- Aprovação regulatória
- Monitoramento pós-mercado
- Relatórios de eventos adversos

### 6.4 Documentação Obrigatória

**Para Cada Modelo:**

1. **Model Card**
   - Objetivo e uso pretendido
   - Arquitetura e hiperparâmetros
   - Dataset de treino
   - Performance e limitações
   - Considerações éticas

2. **Datasheet**
   - Origem dos dados
   - Processo de coleta
   - Pré-processamento
   - Vieses conhecidos
   - Restrições de uso

3. **Risk Assessment**
   - Riscos identificados
   - Probabilidade e impacto
   - Estratégias de mitigação
   - Plano de contingência

---

## 7. Casos de Uso Responsável

### 7.1 Cenários Apropriados

✅ **Triagem Inicial com Supervisão**

- Priorizar casos para revisão
- Sempre com confirmação médica
- Reduzir carga de trabalho

✅ **Segunda Opinião**

- Complementar diagnóstico humano
- Identificar casos complexos
- Suporte à decisão clínica

✅ **Educação e Treinamento**

- Ensinar padrões de ECG
- Simular diagnósticos
- Treinar profissionais

✅ **Pesquisa Clínica**

- Análise de grandes volumes
- Identificação de padrões
- Geração de hipóteses

### 7.2 Cenários Inapropriados

❌ **Diagnóstico Autônomo**

- Sem revisão humana
- Decisões clínicas diretas
- Substituir médico

❌ **Uso Comercial Não Validado**

- Sem aprovação regulatória
- Sem validação clínica
- Sem supervisão adequada

❌ **Aplicação em Populações Não Representadas**

- Grupos não incluídos no treino
- Sem validação específica
- Risco de viés

❌ **Uso por Leigos Sem Supervisão**

- Auto-diagnóstico
- Decisões de tratamento
- Sem contexto clínico

---

## 8. Plano de Resposta a Incidentes

### 8.1 Classificação de Incidentes

**Nível 1 - Crítico:**

- Falso negativo em caso grave
- Dano ao paciente
- Violação de privacidade

**Nível 2 - Alto:**

- Múltiplos falsos negativos
- Viés sistemático detectado
- Falha de segurança

**Nível 3 - Médio:**

- Queda de performance
- Falsos positivos frequentes
- Drift de dados

**Nível 4 - Baixo:**

- Erros isolados
- Problemas de usabilidade
- Feedback de usuários

### 8.2 Protocolo de Resposta

**Imediato (0-4h):**

1. Identificar e documentar incidente
2. Avaliar gravidade
3. Notificar stakeholders
4. Isolar sistema se necessário

**Curto Prazo (4-24h):**

1. Investigar causa raiz
2. Implementar correção temporária
3. Notificar afetados
4. Documentar lições aprendidas

**Médio Prazo (1-7 dias):**

1. Implementar correção permanente
2. Validar solução
3. Atualizar documentação
4. Treinar equipe

**Longo Prazo (>7 dias):**

1. Revisar processos
2. Atualizar políticas
3. Implementar prevenções
4. Relatório final

---

## 9. Conclusões e Recomendações

### 9.1 Principais Achados

1. **Desbalanceamento é Crítico**
   - Impacta significativamente performance
   - Requer estratégias específicas
   - Não pode ser ignorado

2. **Falsos Negativos São Mais Graves**
   - Priorizar sensibilidade
   - Aceitar mais falsos positivos
   - Sempre revisar casos suspeitos

3. **Explicabilidade é Essencial**
   - Aumenta confiança clínica
   - Facilita debugging
   - Requisito ético

4. **Supervisão Humana é Obrigatória**
   - IA não substitui médico
   - Sempre manter humano no loop
   - Responsabilidade final é humana

### 9.2 Recomendações Prioritárias

**Curto Prazo:**

1. Implementar class weights
2. Adicionar níveis de confiança
3. Criar workflow de revisão
4. Documentar limitações

**Médio Prazo:**

1. Implementar Grad-CAM
2. Validar em dataset externo
3. Estabelecer comitê de ética
4. Criar sistema de auditoria

**Longo Prazo:**

1. Validação clínica completa
2. Aprovação regulatória
3. Monitoramento contínuo
4. Retreinamento periódico

### 9.3 Mensagem Final

O desenvolvimento de IA médica é uma responsabilidade que vai além da performance técnica. Requer:

- **Compromisso com Ética**: Priorizar segurança e bem-estar
- **Transparência**: Documentar limitações claramente
- **Humildade**: Reconhecer que IA não é perfeita
- **Colaboração**: Trabalhar com profissionais de saúde
- **Vigilância**: Monitorar e melhorar continuamente

**⚠️ LEMBRETE CRÍTICO:**

Este sistema é **EXCLUSIVAMENTE acadêmico**.

**Uso clínico real requer:**

- Validação clínica rigorosa
- Aprovação regulatória (Anvisa/FDA)
- Supervisão médica contínua
- Framework de governança robusto
- Compromisso com ética e segurança

**A vida de pacientes está em jogo. Não há espaço para atalhos.**

---

## 10. Referências

1. Obermeyer, Z., et al. (2019). Dissecting racial bias in an algorithm used to manage the health of populations. Science, 366(6464), 447-453.

2. Rajkomar, A., et al. (2018). Ensuring Fairness in Machine Learning to Advance Health Equity. Annals of Internal Medicine, 169(12), 866-872.

3. Char, D. S., et al. (2018). Implementing Machine Learning in Health Care — Addressing Ethical Challenges. New England Journal of Medicine, 378(11), 981-983.

4. Topol, E. J. (2019). High-performance medicine: the convergence of human and artificial intelligence. Nature Medicine, 25(1), 44-56.

5. Mittelstadt, B. D., et al. (2016). The ethics of algorithms: Mapping the debate. Big Data & Society, 3(2).

6. Jobin, A., et al. (2019). The global landscape of AI ethics guidelines. Nature Machine Intelligence, 1(9), 389-399.

7. Floridi, L., et al. (2018). AI4People—An Ethical Framework for a Good AI Society. Minds and Machines, 28(4), 689-707.

8. FDA. (2021). Artificial Intelligence and Machine Learning in Software as a Medical Device.

9. European Commission. (2021). Proposal for a Regulation on Artificial Intelligence.

10. WHO. (2021). Ethics and governance of artificial intelligence for health.

---

**CardioAI - FIAP 2026**

**IR ALÉM 1: Ética e Governança em Visão Computacional Médica**

**Data:** Junho de 2026

**Versão:** 1.0
