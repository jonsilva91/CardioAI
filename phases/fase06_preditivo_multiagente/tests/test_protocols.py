"""Testes unitários para o motor determinístico de protocolos clínicos."""

import pytest
from src.protocols import PROTOCOLOS, consultar_protocolos


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


def test_tamanho_e_integridade_lista_protocolos():
    """Garante que a lista oficial possui exatamente os 10 protocolos do enunciado."""
    assert len(PROTOCOLOS) == 10
    assert "Se SPO2 < 88% → iniciar suporte respiratório imediato" in PROTOCOLOS
    assert "Se risco sistêmico alto → ativar estado de emergência" in PROTOCOLOS


def test_protocolos_acionados_novo_caso(paciente_novo_caso):
    """Valida o acionamento estrito dos protocolos para o novo_caso do enunciado.

    Resultado esperado:
    - Carga do sistema > 85%
    - Disponibilidade de recursos < 30%
    - Densidade de eventos > 6
    - Risco sistêmico alto
    Divergência documentada: SpO2 é 89, logo o protocolo SpO2 < 88% NÃO deve ser acionado.
    """
    protocolos = consultar_protocolos(paciente_novo_caso, classificacao="ALTO")
    textos = [p["texto"] for p in protocolos]

    assert "Se carga do sistema > 85% → abrir unidades temporárias" in textos
    assert "Se disponibilidade_recursos < 30% → redistribuir insumos" in textos
    assert "Se densidade_eventos > 6 → ativar plano de contingência" in textos
    assert "Se risco sistêmico alto → ativar estado de emergência" in textos

    # Validação estrita da regra literal de SpO2: 89 não é menor que 88
    assert "Se SPO2 < 88% → iniciar suporte respiratório imediato" not in textos
    assert len(protocolos) == 4


def test_paciente_sem_protocolos_acionados():
    """Valida que paciente estável com classificação BAIXO não aciona nenhum protocolo emergencial."""
    paciente_normal = {
        "idade_media": 35,
        "carga_sistema": 50,
        "tempo_espera": 30,
        "fc_media": 70,
        "spo2_media": 98,
        "pa_sistolica": 115,
        "temperatura": 36.5,
        "densidade_eventos": 2,
        "eventos_24h": 1,
        "disponibilidade_recursos": 70,
    }
    protocolos = consultar_protocolos(paciente_normal, classificacao="BAIXO")
    assert len(protocolos) == 0
