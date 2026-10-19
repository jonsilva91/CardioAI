# Relatório Técnico: Modelo Preditivo de Pico de Risco Cardiovascular
**Projeto CardioAI — Fase 6: Coração Sob Controle (FIAP)**  
**Integrantes:** Jonas Luis da Silva (RM561465) e Edson Henrique Felix Batista (RM566321)  
**Versão do Modelo:** 6.0 | **Artefato:** `models/modelo_pico_risco.joblib`

---

## 1. Justificativa do Algoritmo e Comparação de Modelos

No contexto de monitoramento cardiovascular e suporte à decisão em saúde, o objetivo é antecipar situações críticas (**pico de risco**, `classe 1`) combinando variáveis fisiológicas do paciente e indicadores de carga hospitalar. Para essa tarefa, foram comparados dois algoritmos supervisionados clássicos:

1. **Regressão Logística (Baseline com StandardScaler em Pipeline):** Modelo linear paramétrico rápido e interpretável, que busca encontrar hiperplanos separadores entre as classes.
2. **Random Forest Classifier (Modelo Selecionado, 200 árvores, `random_state=42`):** Ensemble não-paramétrico baseado em *bagging*, capaz de capturar relações não-lineares, descontinuidades e interações complexas entre múltiplos limiares sem suposições de normalidade ou linearidade.

O Random Forest foi selecionado como o modelo oficial da solução por demonstrar superioridade incontestável na detecção de padrões de limiar e descontinuidades do conjunto de dados, alcançando métricas próximas da perfeição sem sobreajuste espúrio, conforme validado por validação cruzada estratificada.

---

## 2. Interpretação das Métricas Reais no Conjunto de Teste (20% — 1.000 amostras)

A divisão treino/teste foi realizada na proporção 80/20 com estratificação de classe (`stratify=y`). A tabela abaixo apresenta os números reais obtidos durante o treinamento:

| Métrica de Avaliação | Regressão Logística (Baseline) | Random Forest (Modelo Vencedor) |
| :--- | :---: | :---: |
| **Acurácia Global** | 81,60% (0,8160) | **99,90% (0,9990)** |
| **Precisão (Classe 1 — Pico de Risco)** | 69,34% (0,6934) | **100,00% (1,0000)** |
| **Recall / Sensibilidade (Classe 1)** | 55,26% (0,5526) | **99,62% (0,9962)** |
| **F1-Score (Classe 1)** | 61,51% (0,6151) | **99,81% (0,9981)** |
| **Validação Cruzada (5-Folds Stratified - Acurácia)** | — | **99,78% ± 0,0019** |
| **Validação Cruzada (5-Folds Stratified - F1)** | — | **99,58% ± 0,0037** |

A Regressão Logística atingiu apenas 55,26% de recall e 81,60% de acurácia porque os critérios geradores do risco são descontinuidades booleanas em múltiplos eixos (degraus de decisão), formato estruturalmente inadequado para funções lineares simples. Já o ensemble de árvores de decisão particiona ortogonalmente o espaço de features, aprendendo com extrema precisão as regiões críticas.

---

## 3. Análise da Matriz de Confusão: Falso Positivo vs. Falso Negativo em Saúde

Em ambientes clínicos de urgência e emergência, o custo de um **Falso Negativo (FN)** é incomparavelmente mais grave do que o de um **Falso Positivo (FP)**:
- **Falso Negativo:** Um paciente em iminência de evento cardíaco grave ou colapso é classificado como "Sem Pico", não recebe intervenção precoce e tem seu prognóstico vital comprometido.
- **Falso Positivo:** Um paciente estável recebe atenção adicional temporária (alerta amarelo), sem prejuízo direto à saúde, apenas com custo de reavaliação.

A matriz de confusão real do Random Forest no conjunto de teste (1.000 casos) evidenciou:
- **Verdadeiros Negativos (TN):** 734 (100% dos pacientes estáveis foram identificados);
- **Falsos Positivos (FP):** **0** (taxa de alarme falso nula);
- **Falsos Negativos (FN):** **Apenas 1** paciente entre os 266 de alto risco;
- **Verdadeiros Positivos (TP):** 265 pacientes críticos detectados com precisão cirúrgica.

O Recall de 99,62% assegura que quase a totalidade dos pacientes críticos foi imediatamente sinalizada para os agentes do sistema.

---

## 4. Limitações Críticas e Propostas de Melhoria

Para assegurar rigor científico e governança ética (disciplina GBA), registram-se quatro limitações fundamentais da modelagem atual:

1. **Rótulo Sintético Determinístico:** A variável alvo `pico_risco` foi construída por uma soma de regras booleanas sobre 6 variáveis (`risk_score >= 2`). Por essa razão, árvores de decisão atingem ~99% de F1 enquanto a regressão linear atinge ~61%. Esse resultado reflete a capacidade do algoritmo de **reaprender uma regra lógica estruturada**, e não uma acurácia diagnóstica sobre patologias humanas reais.
2. **Features de Ruído no Modelo Preditivo:** Das 10 variáveis, quatro (`idade_media`, `pa_sistolica`, `temperatura` e `densidade_eventos`) não integram a fórmula do `risk_score`. Na análise de feature importance, essas variáveis apresentaram importância próxima de zero para o modelo. Contudo, elas são fundamentais na camada médica subsequente para disparo de protocolos clínicos (ex: choque séptico, hipertensão, plano de contingência).
3. **Distribuição Incompatível de Temperatura (Out-of-Distribution):** No código de geração sintética, a temperatura foi gerada com distribuição normal de média 24°C e desvio 5°C (compatível com temperatura de ambiente hospitalar, e não axilar/corporal). Em consequência, pacientes reais com estado febril (37,5°C ou > 38°C) estão fora da distribuição estatística de treinamento do modelo (*out-of-distribution*), exigindo normalização conceitual em futuras versões.
4. **Ausência de Validação Clínica Externa:** O modelo foi treinado e avaliado exclusivamente sobre dados simulados estatisticamente. Não possui validação prospectiva em coortes clínicas hospitalares e jamais deve ser utilizado para prescrição ou conduta diagnóstica direta sem supervisão médica humana.

**Melhorias Futuras:** Implementar datasets clínicos reais (como MIMIC-IV e PhysioNet), adicionar calibração de probabilidades (*Isotonic Regression*) e incorporar aprendizado contínuo com feedback do médico especialista.
