# Referências Bibliográficas — CardioIA

Artigos do SciELO que embasam a relevância clínica das variáveis do Cleveland Heart Disease Dataset (`heart.csv`) para modelos de Inteligência Artificial em saúde cardiovascular.

---

## Artigos SciELO

### 1. Diretrizes de doença coronariana crônica — angina estável
**Autores:** Luiz Antonio Machado César et al.
**Ano:** 2004
**Periódico:** Arquivos Brasileiros de Cardiologia
**URL:** https://www.scielo.br/j/abc/a/DSH5Y73Fwx5SHLSXSkfWX6t/
**DOI:** 10.1590/S0066-782X2004002100001
**Variáveis suportadas:** `cp`, `exang`, `oldpeak`, `thalach`, `ca`, `thal`

Diretrizes oficiais da Sociedade Brasileira de Cardiologia para angina estável. Fundamenta a maioria das variáveis do dataset: tipologia da dor torácica (`cp`), angina de esforço (`exang`), depressão do ST como marcador isquêmico (`oldpeak`), FC máxima como parâmetro funcional (`thalach`), cinecoronariografia para avaliação de vasos (`ca`) e cintilografia com tálio (`thal`).

---

### 2. Associação entre fatores de risco para DAC e coronariopatia em cintilografia de perfusão do miocárdio
**Autores:** Paulo Schiavom Duarte et al.
**Ano:** 2007
**Periódico:** Arquivos Brasileiros de Cardiologia
**URL:** https://www.scielo.br/j/abc/a/PmGnPLcWLGvpZVWyKQFWmCh/
**DOI:** 10.1590/S0066-782X2007000300009
**Variáveis suportadas:** `age`, `sex`, `chol`, `thal`

Estudo com 7.183 pacientes submetidos à cintilografia de perfusão miocárdica (exame subjacente à variável `thal`). Demonstra que idade avançada e sexo masculino são os maiores preditores não modificáveis de DAC, e que dislipidemia figura entre os principais fatores de risco modificáveis — validando `age`, `sex` e `chol` como variáveis clinicamente significativas.

---

### 3. Teste de esforço: alterações do segmento ST restritas à fase de recuperação
**Autores:** J. A. Oliveira Filho et al.
**Ano:** 1999
**Periódico:** Revista da Associação Médica Brasileira
**URL:** https://www.scielo.br/j/ramb/a/tcgcjZVPwNHCKxwPrcWy3Yp/
**DOI:** 10.1590/S0104-42301999000200008
**Variáveis suportadas:** `oldpeak`, `exang`, `cp`

Estudo retrospectivo com 19 pacientes mostrando que depressão do ST de 1–4 mm durante o teste ergométrico é indicador confiável de isquemia miocárdica e DAC subjacente, confirmada em 74% dos casos por cineangiocoronariografia. Valida diretamente `oldpeak` como variável diagnóstica e contextualiza `exang` e `cp` como marcadores isquêmicos complementares.

---

### 4. Valor diagnóstico do teste ergométrico na detecção da isquemia miocárdica silenciosa no paciente idoso
**Autores:** João Joaquim de Oliveira, Sandra Regina A. S. Silva
**Ano:** 1997
**Periódico:** Arquivos Brasileiros de Cardiologia
**URL:** https://www.scielo.br/j/abc/a/8pZhGQYmKPRmJB6cd5mmrSF/
**DOI:** 10.1590/S0066-782X1997000700004
**Variáveis suportadas:** `oldpeak`, `thalach`, `age`, `exang`

Estudo com 110 hipertensos idosos vs. 104 controles normotensos (60–72 anos) pelo protocolo Bruce. Hipertensos apresentaram maior depressão isquêmica do ST e menor duração de exercício. Reforça `oldpeak` como indicador isquêmico, `thalach` como marcador funcional e `age` como fator de risco relevante.

---

### 5. Teste Ergométrico Imediato em Pacientes com Dor Torácica na Sala de Emergência
**Autores:** Josiane de Souza, Waldomiro Carlos Manfroi, Carisi Anne Polanczyk
**Ano:** 2002
**Periódico:** Arquivos Brasileiros de Cardiologia
**URL:** https://www.scielo.br/j/abc/a/JF8cXJwrknj5GCGCVDYNh4K/
**DOI:** 10.1590/S0066-782X2002001000012
**Variáveis suportadas:** `cp`, `exang`, `oldpeak`, `thalach`

Revisão sobre acurácia e segurança do teste ergométrico imediato em emergência para dor torácica aguda. Demonstra que a resposta ao esforço — tipo de dor (`cp`, `exang`), depressão do ST (`oldpeak`) e resposta da FC (`thalach`) — estratifica efetivamente o risco coronariano, mapeando diretamente as variáveis de teste de esforço do Cleveland Dataset.

---

### 6. Comparação da aterosclerose coronária em pacientes com infarto do miocárdio e angina do peito
**Autores:** Waldomiro Carlos Manfroi et al.
**Ano:** 1998
**Periódico:** Arquivos Brasileiros de Cardiologia
**URL:** https://www.scielo.br/j/abc/a/hYrLH35BZL45Xw6dhrcWZPw/
**DOI:** 10.1590/S0066-782X1998000700006
**Variáveis suportadas:** `ca`, `cp`, `sex`

Estudo com 191 pacientes por cineangiocoronariografia avaliando número e gravidade dos vasos acometidos — correspondente direto à variável `ca`. Pacientes com IAM tiveram maior comprometimento vascular que pacientes com angina, validando a contagem de vasos como discriminador prognóstico relevante.

---

### 7. Indicação de cintilografia de perfusão do miocárdio baseada em evidências ergométricas e clínico-epidemiológicas
**Autores:** Paulo Schiavom Duarte et al.
**Ano:** 2006
**Periódico:** Arquivos Brasileiros de Cardiologia
**URL:** https://www.scielo.br/j/abc/a/yMZkzhkDXwWFBx5jLDs8Swj/
**DOI:** 10.1590/S0066-782X2006001700004
**Variáveis suportadas:** `thal`, `oldpeak`, `thalach`, `age`, `sex`

Estudo com 2.100 pacientes integrando escore de Duke (duração do exercício, desvio do ST e sintomas de angina) com fatores de risco de Framingham para indicação da cintilografia (`thal`). Confirma que as variáveis de esforço do Cleveland Dataset — `oldpeak`, `thalach`, `exang` — combinadas com `age` e `sex` melhoram significativamente a detecção de DAC.

---

### 8. Fatores de risco para DAC em pacientes admitidos em unidade de hemodinâmica
**Autores:** Maria Karolina Echer Ferreira Feijó et al.
**Ano:** 2009
**Periódico:** Revista Gaúcha de Enfermagem
**URL:** https://www.scielo.br/j/rgenf/a/4FK5YdLXc66TzC6Vh3Kv4Zh/
**DOI:** 10.1590/S1983-14472009000400009
**Variáveis suportadas:** `age`, `sex`, `chol`, `cp`

Estudo transversal com 302 pacientes submetidos a procedimentos hemodinâmicos (idade média 62 ± 11 anos). Dislipidemia em 50,5% dos casos, hipertensão em 73%. Embasamento epidemiológico para `chol` e `age` como preditores de DAC condizentes com o perfil de risco do Cleveland Dataset.

---

## Cobertura das Variáveis

| Variável | Artigos |
|----------|---------|
| `cp` — tipo de dor no peito | 1, 3, 5, 6, 8 |
| `thalach` — FC máxima no esforço | 1, 4, 5, 7 |
| `oldpeak` — depressão do ST | 1, 3, 4, 5, 7 |
| `ca` — nº de vasos comprometidos | 1, 6 |
| `thal` — cintilografia com tálio | 1, 2, 7 |
| `exang` — angina de esforço | 1, 3, 5 |
| `age` — idade | 2, 4, 7, 8 |
| `sex` — sexo | 2, 6, 7 |
| `chol` — colesterol sérico | 2, 8 |
