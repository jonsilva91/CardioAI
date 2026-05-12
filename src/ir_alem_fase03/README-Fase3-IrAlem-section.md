## IR ALÉM 1 — Comunicação automatizada com REST e e-mail

Além do fluxo IoT com ESP32, MQTT e dashboard, o projeto implementa uma camada complementar em Python para simular comunicação via API REST e automação de e-mail.

### Fluxo

```text
Cliente REST / Simulador
        ↓
API FastAPI
        ↓
Motor de risco
        ↓
Alerta automatizado por e-mail simulado
```

### Arquivos

```text
src/ir_alem_1_rest_email/
├── app.py
├── client_simulador.py
├── email_alert.py
├── risk_engine.py
├── requirements.txt
└── README.md
```

### Execução

```bash
cd src/ir_alem_1_rest_email
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Em outro terminal:

```bash
python client_simulador.py
```

Quando a API identifica taquicardia, febre, ausência de movimento ou baixa saturação, ela gera um alerta e cria um arquivo `.eml`, simulando o envio automatizado de e-mail.

Relatório: [`documents/fase3/relatorio-ir-alem-1-rest-email.md`](documents/fase3/relatorio-ir-alem-1-rest-email.md)

---

## IR ALÉM 2 — IA em séries temporais de saúde

O projeto também implementa um notebook comparando uma abordagem tradicional de Machine Learning com um modelo neuromórfico simples baseado em LIF.

### Comparação realizada

- Regressão Logística com features estatísticas.
- Codificação LIF com spikes e classificador de leitura.

### Arquivos

```text
notebooks/ir_alem_2_series_temporais_saude.ipynb
src/ir_alem_2_series_temporais/
├── lif_model.py
├── requirements.txt
└── README.md
```

### Execução

```bash
pip install -r src/ir_alem_2_series_temporais/requirements.txt
jupyter notebook notebooks/ir_alem_2_series_temporais_saude.ipynb
```

Relatório: [`documents/fase3/relatorio-ir-alem-2-series-temporais.md`](documents/fase3/relatorio-ir-alem-2-series-temporais.md)

Vídeo: [![Demonstração](https://img.youtube.com/vi/AhfEwcIqmHo/1.jpg)](https://youtu.be/AhfEwcIqmHo)
