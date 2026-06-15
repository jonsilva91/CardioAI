# Fase 3 — IoT, Monitoramento, REST, e-mail e Séries Temporais

Esta fase consolida os entregáveis de monitoramento em saúde do CardioAI, agora organizados diretamente em uma pasta própria para facilitar localização e avaliação.

## Estrutura da fase

```text
phases/fase03_iot_monitoramento/
├── README.md
├── iot/
│   ├── wokwi/
│   ├── node-red/
│   └── docs/
├── ir_alem_1_rest_email/
├── ir_alem_2_series_temporais/
├── notebooks/
└── reports/
```

## Conteúdo principal

### 1. IoT

Diretório reservado para materiais de simulação, fluxos e documentação visual:

- `iot/wokwi/`
- `iot/node-red/`
- `iot/docs/`

### 2. IR ALÉM 1 — REST + e-mail

Módulo em Python com:

- API FastAPI
- motor de risco explicável
- cliente simulador
- geração de alerta por e-mail simulado em `.eml`

Local:

- [`ir_alem_1_rest_email/`](./ir_alem_1_rest_email/)

### 3. IR ALÉM 2 — Séries temporais

Experimento com comparação entre abordagem tradicional e codificação neuromórfica LIF.

Locais:

- notebook: [`notebooks/ir_alem_2_series_temporais_saude.ipynb`](./notebooks/ir_alem_2_series_temporais_saude.ipynb)
- código de apoio: [`ir_alem_2_series_temporais/`](./ir_alem_2_series_temporais/)

### 4. Relatórios

- [`reports/relatorio-ir-alem-1-rest-email.md`](./reports/relatorio-ir-alem-1-rest-email.md)
- [`reports/relatorio-ir-alem-2-series-temporais.md`](./reports/relatorio-ir-alem-2-series-temporais.md)

## Como executar

### API REST e alerta por e-mail

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

### Notebook de séries temporais

```bash
pip install -r phases/fase03_iot_monitoramento/ir_alem_2_series_temporais/requirements.txt
jupyter notebook phases/fase03_iot_monitoramento/notebooks/ir_alem_2_series_temporais_saude.ipynb
```

## Observações

- Os caminhos foram reorganizados sem alterar a lógica principal dos scripts.
- O objetivo desta fase é destacar claramente os entregáveis de IoT e IA temporal.
- Arquivos temporários de ambiente virtual não devem ser versionados.
