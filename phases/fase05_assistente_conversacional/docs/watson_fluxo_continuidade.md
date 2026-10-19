# Proposta de Redesenho do Skill IBM watsonx Assistant: Fluxo de Continuidade (Slots e Steps)

> **CardioAI — Fase 5: Assistente Conversacional**  
> Documento técnico de especificação para transição de nós de diálogo isolados (*one-turn*) para fluxos conversacionais ramificados (*multi-turn*) com coleta de variáveis de contexto, estratificação de risco e perguntas de continuidade.

---

## 1. Diagnóstico do Problema & Motivação Clínica

### 1.1. O Limite da Abordagem Anterior (*One-Turn*)
Na versão inicial do skill (`watson/skill-cardioia.json`), o diálogo utilizava **um único nó plano por intenção**:
- O usuário dizia `"estou com dor no peito"`;
- O Watson disparava a intenção `#sintomas_cardiacos` e respondia imediatamente com uma mensagem fixa sugerindo agendamento, sem investigar o tempo de início, a gravidade ou a presença de sinais vitais de alarme.

Em triagem médica digital e suporte à decisão cardiológica, **essa abordagem é inadequada e potencialmente perigosa**:
1. Não diferencia um desconforto muscular leve crônico de uma síndrome coronariana aguda (infarto);
2. Não coleta dados suficientes para alimentar os pipelines preditivos posteriores (Fase 4 - CNN de ECG e Fase 6 - Random Forest de Risco Sistêmico);
3. Interrompe a conversa no primeiro turno, gerando fricção e desconfiança no usuário.

### 1.2. O Novo Paradigma (*Multi-Turn com Slots / Actions*)
A nova especificação desenhada abaixo estrutura **jornadas conversacionais guiadas**, nas quais o assistente retém o estado do paciente na sessão (`context.skills['main skill'].user_defined`) e conduz uma anamnese digital estruturada.

---

## 2. Fluxo 1: Triagem Aprofundada de Sintomas Cardíacos (`#sintomas_cardiacos`)

### 2.1. Diagrama de Estados do Fluxo

```
[ Usuário relata sintoma ]
           │
           ▼
[ Passo 1: Identificação do Sintoma ] ──► Salva $sintoma_identificado
           │
           ▼
[ Passo 2: Duração dos Sintomas ] ──────► "Há quanto tempo você começou a sentir isso?"
           │                             (Salva $sintoma_duracao)
           ▼
[ Passo 3: Intensidade da Dor (0-10) ] ─► "Em uma escala de 0 a 10, quão intenso é o incômodo?"
           │                             (Salva $sintoma_intensidade)
           ▼
[ Passo 4: Investigação de Red Flags ] ─► "Sente irradiação pro braço esquerdo, mandíbula, suor frio ou tontura?"
           │                             (Salva $sinais_alarme)
           ▼
   ┌───────────────────────┬───────────────────────┐
   │ Intensidade >= 7 OU   │ Intensidade < 7 E     │
   │ Sinais Alarme = SIM   │ Sinais Alarme = NÃO   │
   ▼                       ▼                       ▼
[ EMERGÊNCIA IMEDIATA ]  [ RISCO MODERADO ]      [ BAIXO RISCO / ROTINA ]
- Ligue 192 (SAMU)       - Aconselhamento de     - Oferta direta de
- Buscar PS Imediato       repouso imediato        agendamento no Portal
- Alerta visual no chat  - Consulta prioritária  - Orientações de hábitos
```

### 2.2. Detalhamento dos Passos (Slots / Steps)

| Passo | Pergunta / Prompt do Assistente | Resposta Esperada / Entidade | Variável de Contexto |
| :---: | :--- | :--- | :--- |
| **Passo 1** | Identificação inicial do sintoma na mensagem de entrada. | `@sintoma:dor_peito`, `@sintoma:palpitacao`, `@sintoma:falta_de_ar` | `$sintoma_identificado` |
| **Passo 2** | *"Para eu te orientar melhor: há quanto tempo esse sintoma começou? (Exemplo: minutos, algumas horas ou dias)?"* | `@sys-time`, `@sys-number` ou texto livre | `$sintoma_duracao` |
| **Passo 3** | *"Em uma escala de 0 a 10, onde 0 é nenhum incômodo e 10 é uma dor insuportável, que nota você daria agora?"* | `@sys-number` (0 a 10) | `$sintoma_intensidade` |
| **Passo 4** | *"Você está sentindo algum destes sinais associados: suor frio, falta de ar súbita, dor irradiando para o braço esquerdo ou mandíbula?"* | `sim` / `não` / `@sinal_alarme` | `$sinais_alarme` |
| **Passo 5** | Avaliação das regras de desvio clínico: | Condição lógica combinada | `$conduta_clinica` |

### 2.3. Respostas Ramificadas do Passo 5:
- **Cenário Crítico (Emergência):**
  > *"⚠️ **ATENÇÃO MÉDICA URGENTE:** Pela intensidade relatada ($sintoma_intensidade/10) e a presença de sintomas de alerta, há risco de evento coronariano agudo. **Não dirija.** Peça ajuda imediata a alguém próximo, ligue para o **SAMU (192)** ou dirija-se ao pronto-socorro mais próximo agora."*
- **Cenário Subagudo (Moderado):**
  > *"Entendido. Seu relato de $sintoma_identificado com duração de $sintoma_duracao requer investigação presencial com cardiologista para realizar exames como eletrocardiograma e ecocardiograma. Deseja que eu verifique os horários disponíveis na aba de Agendamentos?"*

---

## 3. Fluxo 2: Dúvidas e Laudos de ECG da Fase 4 (`#duvida_ecg`)

### 3.1. Integração com as 5 Classes do Modelo CNN
O modelo da Fase 4 classifica batimentos em cinco categorias da AAMI:
- **N** (Normal / Sinusal)
- **S** (Ectopia Supraventricular)
- **V** (Ectopia Ventricular / Pré-ventricular)
- **F** (Batimento de Fusão)
- **Q** (Batimento Desconhecido / Marca-passo)

### 3.2. Fluxo Guiado de Continuidade

```
[ Usuário pergunta sobre ECG ]
           │
           ▼
[ Passo 1: Identificação da Classe ] ──► "Qual foi a classe ou sigla indicada no seu traçado (N, S, V, F ou Q)?"
           │                            (Salva $classe_ecg)
           ▼
[ Passo 2: Explicação Fisiopatológica ] ─► Apresenta a tradução do jargão técnico em linguagem acessível
           │
           ▼
[ Passo 3: Correlação com Sintomas ] ────► "Você sentiu palpitação, tontura ou dor durante a realização do exame?"
           │                            (Salva $sintomas_associados_ecg)
           ▼
[ Passo 4: Próximo Passo Orientado ] ───► Encaminha conduta com base na severidade da classe
```

### 3.3. Tabela de Conduta por Classe de ECG

| Classe | Descrição Humanizada ao Paciente | Nível de Urgência | Ação Recomendada |
| :---: | :--- | :---: | :--- |
| **N** | *"A classe N indica um batimento sinusal normal. Isso significa que o impulso elétrico do seu coração seguiu o trajeto fisiológico esperado durante o registro."* | Baixa | Manter acompanhamento de rotina e prevenção anual. |
| **S** | *"A classe S representa um batimento ectópico supraventricular. Ocorre quando uma contração prematura surge nas câmaras superiores (átrios). Comum em episódios de estresse, excesso de cafeína ou arritmias supraventriculares."* | Moderada | Marcar consulta com cardiologista clínico para investigar gatilhos e traçado completo de Holter. |
| **V** | *"A classe V indica contrações ventriculares prematuras. São disparos elétricos originados nos ventrículos, as principais bombas do coração. Podem causar sensação de 'falha no peito' ou vertigem."* | Alta | Avaliação médica prioritária. Se acompanhado de dor no peito ou síncope, procurar atendimento imediato. |
| **F** | *"A classe F representa batimentos de fusão, quando um impulso normal e um ventricular colidem no mesmo ciclo cardíaco."* | Moderada/Alta | Requer revisão do laudo pelo especialista para correlacionar com a clínica. |
| **Q** | *"A classe Q é reservada para padrões atípicos ou traçados associados a estimulação elétrica artificial (como marcapasso)."* | Especializada | Agendar revisão de marcapasso ou novo traçado com equipe de eletrofisiologia. |

---

## 4. Fluxo 3: Agendamento Humanizado de Consulta (`#agendamento_consulta`)

### 4.1. Passos Conversacionais de Apoio à Recepção
1. **Passo 1 (Motivo da Consulta):**  
   *"Você gostaria de agendar uma consulta para rotina/check-up, retorno de exames ou por conta de um sintoma recente?"*
2. **Passo 2 (Preferência de Turno e Unidade):**  
   *"Qual período fica mais conveniente para você: manhã ou tarde? Temos unidades no Centro e na Zona Sul."*
3. **Passo 3 (Confirmação e Transição para o Portal):**  
   *"Perfeito! Já reservei as opções no sistema. Você pode confirmar o profissional e horário exato diretamente na aba **Agendamentos** do nosso Portal CardioAI."*

---

## 5. Mapeamento das Variáveis de Sessão no Watson

Para que o backend Flask e o Portal React possam consumir o estado da triagem, as seguintes variáveis devem ser mantidas no contexto da conversa:

```json
{
  "context": {
    "skills": {
      "main skill": {
        "user_defined": {
          "paciente_nome": "string",
          "sintoma_tipo": "dor_peito | palpitacao | falta_de_ar | outro",
          "sintoma_duracao": "string",
          "sintoma_intensidade": 0,
          "sinais_alarme": true,
          "ecg_classe": "N | S | V | F | Q",
          "status_triagem": "em_andamento | concluida",
          "nivel_urgencia": "BAIXA | MODERADA | ALTA | CRITICA"
        }
      }
    }
  }
}
```

---

## 6. Roteiro para Importação no IBM watsonx Assistant

Ao atualizar o skill no console da IBM Cloud:
1. Acesse o **watsonx Assistant** e selecione o assistente **CardioAI**;
2. Na aba **Actions** ou **Dialog**, adicione os passos filhos (*child steps*) correspondentes a cada um dos slots especificados nos diagramas acima;
3. Ative a captura de respostas obrigatórias antes da resposta final (*Slots must be filled*);
4. Exporte o novo arquivo JSON atualizado e salve-o em `phases/fase05_assistente_conversacional/watson/skill-cardioia.json` para manter o versionamento contínuo no repositório.
