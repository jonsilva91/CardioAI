# IR ALÉM 1 — Comunicação automatizada com REST e e-mail

Este módulo simula um sistema de monitoramento de sinais vitais que recebe dados por uma API REST em Python, avalia risco de saúde e dispara uma automação de e-mail quando há alerta.

## Localização no repositório

```text
phases/fase03_iot_monitoramento/ir_alem_1_rest_email/
```

## Fluxo

```text
Cliente REST / ESP32 / simulador
        ↓
POST /vitals
        ↓
API FastAPI
        ↓
Motor de risco
        ↓
Se houver alerta: gera e-mail simulado (.eml) + log CSV
```

## Como executar

Na raiz do repositório:

```bash
cd phases/fase03_iot_monitoramento/ir_alem_1_rest_email
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Em outro terminal:

```bash
cd phases/fase03_iot_monitoramento/ir_alem_1_rest_email
python client_simulador.py
```

## Endpoints

- `GET /health`: verifica se a API está ativa.
- `POST /vitals`: recebe sinais vitais.
- `GET /vitals/latest`: lista últimas leituras recebidas.
- `GET /alerts`: lista alertas gerados.

## Critérios de risco

- BPM acima de 120: alerta de taquicardia.
- BPM acima de 140: risco crítico.
- Temperatura maior ou igual a 38 °C: febre.
- Temperatura maior ou igual a 39 °C: febre alta.
- Movimento igual a zero: ausência de movimento.
- SpO2 abaixo de 94%, quando informado: saturação baixa.

## E-mail automatizado

Por segurança e simplicidade acadêmica, o envio de e-mail é simulado. Quando um alerta é gerado, o sistema cria arquivos `.eml` em:

```text
sent_emails/
```

Também registra o alerta em:

```text
alerts_log.csv
```

## Observação

Os arquivos gerados localmente são artefatos de execução e não devem ser tratados como datasets permanentes do projeto.
