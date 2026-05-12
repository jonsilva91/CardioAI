# Relatório — IR ALÉM 1: Comunicação automatizada com REST e e-mail

## 1. Objetivo

O objetivo deste módulo é complementar a Fase 3 do CardioIA com uma camada de comunicação REST em Python, capaz de receber sinais vitais simulados, aplicar uma lógica de verificação de risco e acionar uma automação de e-mail em caso de alerta. A solução representa um fluxo comum em saúde digital: um dispositivo ou simulador coleta dados do paciente, envia os dados para um serviço web e o backend interpreta se a condição exige notificação.

## 2. Arquitetura implementada

O fluxo da solução é composto por quatro etapas principais:

```text
Simulador/Cliente REST
        ↓
API FastAPI - POST /vitals
        ↓
Motor de risco clínico simplificado
        ↓
Automação de e-mail simulado + log local
```

O módulo foi organizado em arquivos separados para facilitar manutenção e clareza:

- `app.py`: expõe a API REST e seus endpoints.
- `risk_engine.py`: contém as regras de risco.
- `email_alert.py`: simula o disparo automático de e-mail.
- `client_simulador.py`: envia leituras simuladas para a API.
- `requirements.txt`: lista as dependências Python necessárias.

## 3. API REST

A API possui endpoints para verificar saúde do serviço, receber sinais vitais, consultar últimas leituras e listar alertas. O endpoint principal é `POST /vitals`, que recebe um JSON com os seguintes campos:

```json
{
  "patient_id": "paciente_001",
  "bpm": 92,
  "temperature": 36.7,
  "movement": 12.5,
  "oxygen": 97.0,
  "source": "simulador_python"
}
```

Ao receber o payload, a API valida os dados, registra a leitura em memória, chama o motor de risco e retorna o resultado da análise. Quando há alerta, a API também chama a automação de e-mail.

## 4. Lógica de risco

A lógica de risco foi criada com regras simples e interpretáveis, adequadas para uma prova de conceito acadêmica. Os principais critérios são:

- BPM acima de 120: alerta de taquicardia.
- BPM acima de 140: risco crítico.
- Temperatura igual ou superior a 38 °C: febre.
- Temperatura igual ou superior a 39 °C: febre alta.
- Movimento igual a zero: possível ausência de movimento.
- SpO2 abaixo de 94%, quando informado: saturação baixa.

Cada condição soma pontos a um score. O resultado final pode ser `NORMAL`, `ALERTA` ou `CRITICO`. Essa abordagem é simples, mas tem a vantagem de ser transparente e auditável, algo importante em sistemas de saúde.

## 5. Automação de e-mail

Por segurança e simplicidade, o projeto não envia e-mail real por SMTP. Em vez disso, a automação gera um arquivo `.eml` com o conteúdo do alerta e registra o evento em um arquivo CSV. Isso simula a ação de uma rotina RPA/e-mail sem depender de credenciais reais.

Os arquivos são gerados em:

```text
src/ir_alem_1_rest_email/sent_emails/
src/ir_alem_1_rest_email/alerts_log.csv
```

Essa estratégia permite demonstrar a automação exigida pela atividade sem expor senhas, tokens ou dados sensíveis.

## 6. Execução

Para executar a API:

```bash
cd src/ir_alem_1_rest_email
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Em outro terminal, execute o cliente simulador:

```bash
python client_simulador.py
```

Durante a execução, algumas leituras normais e algumas leituras de alerta são enviadas automaticamente. As leituras de alerta geram arquivos `.eml` e registros no CSV.

## 7. Conclusão

O módulo IR ALÉM 1 demonstra como o CardioIA pode evoluir de um protótipo IoT para uma arquitetura integrada com backend REST, regras de risco e automação de comunicação. O fluxo é simples, mas representa uma base realista para sistemas de saúde digital, nos quais alertas precisam ser identificados rapidamente e encaminhados para uma equipe responsável.
