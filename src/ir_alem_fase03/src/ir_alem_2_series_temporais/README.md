# IR ALÉM 2 — IA em séries temporais de saúde

Este módulo compara dois métodos para classificação de séries temporais de batimentos cardíacos:

1. **Classificador tradicional:** Regressão Logística com features estatísticas.
2. **Modelo neuromórfico simples:** codificação LIF, transformando janelas de BPM em spikes.

O notebook principal está em:

```text
notebooks/ir_alem_2_series_temporais_saude.ipynb
```

## Como executar

Na raiz do repositório:

```bash
pip install numpy pandas scikit-learn matplotlib jupyter
jupyter notebook notebooks/ir_alem_2_series_temporais_saude.ipynb
```

## Ideia do experimento

O dataset sintético cria janelas temporais de BPM com três classes:

- `NORMAL`
- `TAQUICARDIA`
- `IRREGULAR`

Depois comparamos acurácia, matriz de confusão e relatório de classificação.
