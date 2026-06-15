# heart.csv — Dicionário de Dados

Dataset de doenças cardíacas baseado no Cleveland Heart Disease Dataset (UCI Machine Learning Repository).

link dataset: https://drive.google.com/drive/folders/11RTU0AH8WymgU_TxGyg3XQdFygAwtZus?usp=drive_link

## Colunas

### `age` — Age
- **Tipo:** Numérico
- **Descrição:** Idade do paciente em anos.

### `sex` — Sex
- **Tipo:** Categórico
- **Descrição:** Sexo biológico do paciente.
  - `1` = masculino
  - `0` = feminino

### `cp` — Chest Pain Type
- **Tipo:** Categórico
- **Descrição:** Tipo de dor no peito.
  - `0` = angina típica
  - `1` = angina atípica
  - `2` = dor não-anginosa
  - `3` = assintomático

### `trestbps` — Resting Blood Pressure
- **Tipo:** Numérico
- **Descrição:** Pressão arterial em repouso (em mmHg) no momento da admissão hospitalar.

### `chol` — Serum Cholesterol
- **Tipo:** Numérico
- **Descrição:** Colesterol sérico em mg/dL.

### `fbs` — Fasting Blood Sugar
- **Tipo:** Categórico
- **Descrição:** Glicemia em jejum.
  - `1` = glicemia em jejum > 120 mg/dL (indica diabetes)
  - `0` = caso contrário

### `restecg` — Resting ECG Results
- **Tipo:** Categórico
- **Descrição:** Resultados do eletrocardiograma em repouso.
  - `0` = normal
  - `1` = anormalidade na onda ST-T (inversão de onda T e/ou elevação ou depressão de ST > 0,05 mV)
  - `2` = hipertrofia ventricular esquerda provável ou definitiva

### `thalach` — Maximum Heart Rate Achieved
- **Tipo:** Numérico
- **Descrição:** Frequência cardíaca máxima atingida durante o teste de esforço (bpm).

### `exang` — Exercise Induced Angina
- **Tipo:** Categórico
- **Descrição:** Angina induzida por exercício.
  - `1` = sim
  - `0` = não

### `oldpeak` — ST Depression
- **Tipo:** Numérico
- **Descrição:** Depressão do segmento ST induzida por exercício em relação ao repouso (em mm).

### `slope` — Slope of Peak Exercise ST Segment
- **Tipo:** Categórico
- **Descrição:** Inclinação do segmento ST no pico do exercício.
  - `0` = descendente (upsloping)
  - `1` = plano (flat)
  - `2` = ascendente (downsloping)

### `ca` — Number of Major Vessels
- **Tipo:** Numérico
- **Descrição:** Número de vasos principais (0–4) coloridos por fluoroscopia.

### `thal` — Thalassemia
- **Tipo:** Categórico
- **Descrição:** Resultado do teste de estresse com tálio.
  - `0` = nulo
  - `1` = defeito fixo
  - `2` = normal
  - `3` = defeito reversível

### `target` — Target (Diagnosis)
- **Tipo:** Categórico
- **Descrição:** Diagnóstico de doença cardíaca.
  - `1` = presença de doença cardíaca
  - `0` = ausência de doença cardíaca

## Observações

- O dataset possui **303 registros** e **14 colunas**.
- A coluna `target` é a variável dependente (rótulo) para modelos de classificação.
- Valores `1` em `target` indicam pacientes com doença cardíaca; valores `0` indicam pacientes saudáveis.
- O dataset é amplamente utilizado em tarefas de classificação binária para predição de risco cardíaco.

---

## Análise Clínica — Variáveis Mais Relevantes para IA em Saúde

### Variáveis de Alta Relevância Clínica

**`cp` — Tipo de dor no peito:** Principal sintoma clínico de doença arterial coronariana. A angina típica é altamente preditiva de isquemia miocárdica.

**`thalach` — FC máxima no esforço:** Baixa capacidade de elevar a FC durante exercício é marcador de disfunção cardíaca e pior prognóstico.

**`oldpeak` — Depressão do ST:** Indicador direto de isquemia miocárdica durante esforço; valores elevados correlacionam fortemente com doença coronariana.

**`ca` — Nº de vasos comprometidos:** Avaliado por fluoroscopia; quanto maior o número, mais extensa a doença arterial coronariana — forte preditor de eventos cardíacos.

**`thal` — Teste de estresse com tálio:** Defeito reversível (`3`) indica isquemia; defeito fixo (`1`) indica infarto prévio — variável de alta especificidade diagnóstica.

**`exang` — Angina induzida por exercício:** Sinal clínico objetivo de isquemia desencadeada por demanda metabólica aumentada.

### Variáveis de Relevância Moderada

**`age` — Idade:** Fator de risco não modificável; risco cardiovascular cresce progressivamente com a idade.

**`sex` — Sexo biológico:** Homens têm risco maior antes dos 55 anos; mulheres apresentam risco elevado pós-menopausa — impacta estratégias de rastreio.

**`slope` — Inclinação do segmento ST:** Complementa a análise do `oldpeak`; descida do ST (`0`) é o padrão mais preocupante.

**`chol` — Colesterol sérico:** Fator de risco clássico para aterosclerose, embora sua relação isolada com o `target` neste dataset seja menos linear do que esperado.

### Variáveis de Menor Poder Preditivo Isolado

**`trestbps`:** Pressão em repouso é fator de risco crônico, mas pouco discriminativa em evento agudo isolado.

**`fbs`:** Glicemia em jejum é proxy grosseiro para diabetes; sozinha tem baixo poder discriminatório no dataset.

**`restecg`:** Alterações de ECG em repouso são relevantes, mas têm alta variabilidade e sobreposição entre grupos.

### Conclusão para Modelagem

Para um modelo de IA voltado à predição de doença cardíaca, as variáveis **`cp`, `thalach`, `oldpeak`, `ca`, `thal` e `exang`** devem receber maior atenção na engenharia de features, pois refletem diretamente mecanismos fisiopatológicos da isquemia miocárdica. Variáveis como `age`, `sex` e `chol` funcionam melhor como fatores contextuais de risco. Técnicas como **SHAP values** ou **feature importance** são recomendadas para validar essas hipóteses empiricamente com os dados.
