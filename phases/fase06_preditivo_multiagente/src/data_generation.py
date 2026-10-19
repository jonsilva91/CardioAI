"""Geração da base de dados sintética de pico de risco cardiovascular.

Reproduz exatamente o código fornecido no enunciado oficial da FIAP Fase 6:
- Seed aleatória: 42
- Amostras: 5000
- 10 features com distribuições estipuladas
- Cálculo determinístico de risk_score e rótulo pico_risco (risk_score >= 2)
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Garante suporte a UTF-8 no stdout em terminais Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.config import DATASET_CSV_PATH, RANDOM_SEED, N_SAMPLES


def gerar_base_sintetica(n: int = N_SAMPLES, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Gera a base sintética com n amostras e semente fixa conforme o enunciado."""
    np.random.seed(seed)

    # Geração dos dados conforme especificações do enunciado da atividade
    df = pd.DataFrame({
        "idade_media": np.random.normal(55, 12, n).clip(18, 90),
        "carga_sistema": np.random.uniform(30, 100, n),
        "tempo_espera": np.random.normal(45, 20, n).clip(5, 180),
        "fc_media": np.random.normal(85, 15, n).clip(50, 150),
        "spo2_media": np.random.normal(95, 3, n).clip(70, 100),
        "pa_sistolica": np.random.normal(125, 20, n).clip(80, 200),
        "temperatura": np.random.normal(24, 5, n).clip(10, 40),
        "densidade_eventos": np.random.poisson(3, n),
        "eventos_24h": np.random.poisson(2, n),
        "disponibilidade_recursos": np.random.uniform(20, 100, n)
    })

    # Regra determinística de risco sistêmico com 6 critérios clínicos/operacionais
    risk_score = (
        (df["carga_sistema"] > 80).astype(int) +
        (df["tempo_espera"] > 60).astype(int) +
        (df["spo2_media"] < 92).astype(int) +
        (df["fc_media"] > 110).astype(int) +
        (df["eventos_24h"] > 4).astype(int) +
        (df["disponibilidade_recursos"] < 40).astype(int)
    )

    # Rótulo binário: pico de risco ativo se pelo menos 2 critérios forem atendidos
    df["pico_risco"] = (risk_score >= 2).astype(int)

    return df


def salvar_base_sintetica(caminho_csv: Path = DATASET_CSV_PATH) -> pd.DataFrame:
    """Gera e salva a base sintética no caminho indicado."""
    df = gerar_base_sintetica()
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho_csv, index=False)
    
    # Resumo no terminal
    n_total = len(df)
    n_pos = df["pico_risco"].sum()
    pct_pos = (n_pos / n_total) * 100
    pct_neg = 100 - pct_pos
    print(f"✅ Base sintética gerada com sucesso em: {caminho_csv}")
    print(f"📊 Total de registros: {n_total}")
    print(f"📈 Distribuição de classes:")
    print(f"   - Classe 0 (Sem pico): {n_total - n_pos} ({pct_neg:.1f}%)")
    print(f"   - Classe 1 (Pico de risco): {n_pos} ({pct_pos:.1f}%)")
    
    return df


if __name__ == "__main__":
    salvar_base_sintetica()
