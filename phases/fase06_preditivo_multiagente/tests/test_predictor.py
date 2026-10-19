"""Testes unitários para o módulo predictor."""

import pytest
from src.predictor import normalizar_dados_paciente, prever_risco, validar_features_paciente


@pytest.fixture
def paciente_novo_caso() -> dict:
    return {
        "idade_media": 62,
        "carga_sistema": 92,
        "tempo_espera": 75,
        "fc_media": 118,
        "spo2_media": 89,
        "pa_sistolica": 100,
        "temperatura": 37.5,
        "densidade_eventos": 7,
        "eventos_24h": 5,
        "disponibilidade_recursos": 25,
    }


@pytest.fixture
def paciente_baixo_risco() -> dict:
    return {
        "idade_media": 42,
        "carga_sistema": 45,
        "tempo_espera": 25,
        "fc_media": 72,
        "spo2_media": 98,
        "pa_sistolica": 120,
        "temperatura": 24.5,
        "densidade_eventos": 1,
        "eventos_24h": 0,
        "disponibilidade_recursos": 85,
    }


def test_normalizacao_chaves_com_espaco():
    """Valida a correção de chaves com espaço como 'disponibilidade recursos'."""
    entrada = {"idade_media": 50, "disponibilidade recursos": 30}
    saida = normalizar_dados_paciente(entrada)
    assert "disponibilidade_recursos" in saida
    assert saida["disponibilidade_recursos"] == 30


def test_validar_features_faltantes():
    """Valida se erro claro é lançado quando faltam features obrigatórias."""
    dados_incompletos = {"idade_media": 55, "carga_sistema": 80}
    with pytest.raises(ValueError) as excinfo:
        validar_features_paciente(dados_incompletos)
    assert "Dados do paciente incompletos" in str(excinfo.value)


def test_prever_risco_novo_caso(paciente_novo_caso):
    """Valida a predição correta para o novo_caso do enunciado (Alto Risco)."""
    resultado = prever_risco(paciente_novo_caso)
    assert isinstance(resultado["probabilidade"], float)
    assert resultado["probabilidade"] >= 0.70
    assert resultado["classe_prevista"] == 1
    assert resultado["classificacao"] == "ALTO"


def test_prever_risco_com_chave_com_espaco(paciente_novo_caso):
    """Valida se o predictor aceita o formato com espaço original do enunciado."""
    dados_modificados = dict(paciente_novo_caso)
    dados_modificados["disponibilidade recursos"] = dados_modificados.pop("disponibilidade_recursos")
    resultado = prever_risco(dados_modificados)
    assert resultado["classificacao"] == "ALTO"
    assert resultado["classe_prevista"] == 1


def test_prever_risco_paciente_baixo_risco(paciente_baixo_risco):
    """Valida a predição para paciente estável (Baixo Risco)."""
    resultado = prever_risco(paciente_baixo_risco)
    assert resultado["probabilidade"] < 0.40
    assert resultado["classe_prevista"] == 0
    assert resultado["classificacao"] == "BAIXO"
