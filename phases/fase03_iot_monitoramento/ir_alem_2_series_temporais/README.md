# IR ALÉM 2 — IA em séries temporais de saúde

Este módulo compara dois métodos para classificação de séries temporais de batimentos cardíacos:

1. **Classificador tradicional:** Regressão Logística com features estatísticas.
2. **Modelo neuromórfico simples:** codificação LIF, transformando janelas de BPM em spikes.

## Localização no repositório

```text
phases/fase03_iot_monitoramento/
├── notebooks/ir_alem_2_series_temporais_saude.ipynb
└── ir_alem_2_series_temporais/
```

## Como executar

Na raiz do repositório:

```bash
pip install -r phases/fase03_iot_monitoramento/ir_alem_2_series_temporais/requirements.txt
jupyter notebook phases/fase03_iot_monitoramento/notebooks/ir_alem_2_series_temporais_saude.ipynb
```

## Ideia do experimento

O dataset sintético cria janelas temporais de BPM com três classes:

- `NORMAL`
- `TAQUICARDIA`
- `IRREGULAR`

Depois comparamos acurácia, matriz de confusão e relatório de classificação.

## Arquivos relacionados

- notebook principal: `../notebooks/ir_alem_2_series_temporais_saude.ipynb`
- implementação LIF: `lif_model.py`
- dependências: `requirements.txt`
- relatório: `../reports/relatorio-ir-alem-2-series-temporais.md`
