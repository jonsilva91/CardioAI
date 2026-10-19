"""Módulo de inferência e predição de risco cardiovascular.

Carrega o modelo salvo em joblib, normaliza os dados de entrada do paciente,
valida a completude das features requeridas e infere a probabilidade e a classificação de risco.
"""

from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd

from src.config import FEATURES, MODEL_JOBLIB_PATH, classificar_risco

# Cache do modelo carregado em memória
_MODEL_CACHE: dict[str, Any] | None = None


def carregar_modelo_preditivo(caminho_modelo: Path = MODEL_JOBLIB_PATH) -> dict[str, Any]:
    """Carrega o pacote de artefatos do modelo treinado a partir do arquivo joblib."""
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    if not caminho_modelo.exists():
        raise FileNotFoundError(
            f"Modelo preditivo não encontrado em '{caminho_modelo}'. "
            "Execute 'python -m src.train' para treinar e salvar o modelo."
        )

    artefato = joblib.load(caminho_modelo)
    _MODEL_CACHE = artefato
    return artefato


def normalizar_dados_paciente(dados: dict[str, Any]) -> dict[str, Any]:
    """Normaliza as chaves do dicionário (ex: substitui espaços por underscores).

    Resolve o erro documentado no enunciado onde 'disponibilidade recursos' vinha com espaço.
    """
    normalizado: dict[str, Any] = {}
    for chave, valor in dados.items():
        chave_limpa = str(chave).strip().replace(" ", "_")
        normalizado[chave_limpa] = valor
    return normalizado


def validar_features_paciente(dados_normalizados: dict[str, Any]) -> None:
    """Verifica se todas as 10 features obrigatórias estão presentes no dicionário."""
    faltantes = [feat for feat in FEATURES if feat not in dados_normalizados]
    if faltantes:
        raise ValueError(
            f"Dados do paciente incompletos. Faltam as seguintes variáveis obrigatórias: {faltantes}. "
            f"Variáveis esperadas: {FEATURES}"
        )


def prever_risco(dados: dict[str, Any]) -> dict[str, Any]:
    """Recebe dados de um paciente e retorna probabilidade, classe e classificação de risco.

    Args:
        dados: Dicionário contendo as 10 variáveis do paciente.

    Returns:
        Dicionário com:
            - probabilidade: float arredondado a 2 casas decimais (probabilidade da classe 1)
            - classe_prevista: 0 ou 1
            - classificacao: 'BAIXO', 'MODERADO' ou 'ALTO'
    """
    dados_norm = normalizar_dados_paciente(dados)
    validar_features_paciente(dados_norm)

    # Garante a ordem exata das features esperada pelo modelo
    df_paciente = pd.DataFrame([[float(dados_norm[feat]) for feat in FEATURES]], columns=FEATURES)

    artefato = carregar_modelo_preditivo()
    modelo = artefato["model"]

    # Obtenção de probabilidades e classe
    probabilidades = modelo.predict_proba(df_paciente)[0]
    prob_classe_1 = float(probabilidades[1])
    prob_arredondada = round(prob_classe_1, 2)
    classe_prevista = int(modelo.predict(df_paciente)[0])

    classificacao = classificar_risco(prob_arredondada)

    return {
        "probabilidade": prob_arredondada,
        "classe_prevista": classe_prevista,
        "classificacao": classificacao,
    }
