"""Testes unitários para o validador de coerência clínica (sem chamadas a APIs externas).

Valida casos coerentes e todas as classes de inconsistência previstas:
a) Variável crítica fora do limiar para protocolo sugerido;
b) Omissão de protocolo obrigatório;
c) Divergência entre probabilidade e classificação pelos limiares do config.py;
d) Relação biunívoca entre classificação ALTO e protocolo de emergência sistêmica.
"""

import sys
from pathlib import Path
import pytest

# Adiciona diretórios relevantes ao sys.path
IR_ALEM_DIR = Path(__file__).resolve().parents[1]
FASE06_DIR = Path(__file__).resolve().parents[3]

if str(IR_ALEM_DIR) not in sys.path:
    sys.path.insert(0, str(IR_ALEM_DIR))
if str(FASE06_DIR) not in sys.path:
    sys.path.insert(0, str(FASE06_DIR))

from coherence_validator import validar_coerencia
from src.protocols import PROTOCOLOS


@pytest.fixture
def paciente_alto_risco():
    """Paciente com alta sobrecarga sistêmica e eventos críticos (semelhante ao novo_caso.json)."""
    return {
        "idade_media": 68.0,
        "carga_sistema": 88.0,          # > 85% -> PROT-02
        "tempo_espera": 95.0,           # > 90 min -> PROT-06
        "fc_media": 115.0,              # <= 120 (normal)
        "spo2_media": 94.0,             # >= 88% (normal)
        "pa_sistolica": 110.0,          # >= 90 (normal)
        "temperatura": 37.1,            # <= 38 (normal)
        "densidade_eventos": 8.0,       # > 6 -> PROT-08
        "eventos_24h": 6.0,             # > 5 -> PROT-04
        "disponibilidade_recursos": 22.0 # < 30% -> PROT-05
    }


@pytest.fixture
def paciente_baixo_risco():
    """Paciente com todos os parâmetros vitais e operacionais dentro das faixas normais."""
    return {
        "idade_media": 45.0,
        "carga_sistema": 40.0,
        "tempo_espera": 35.0,
        "fc_media": 78.0,
        "spo2_media": 98.0,
        "pa_sistolica": 120.0,
        "temperatura": 36.6,
        "densidade_eventos": 1.0,
        "eventos_24h": 0.0,
        "disponibilidade_recursos": 80.0
    }


def test_caso_coerente_alto_risco(paciente_alto_risco):
    """Cenário perfeitamente coerente para paciente em risco ALTO."""
    resultado = {
        "probabilidade": 0.92,
        "classificacao": "ALTO",
        "protocolos_sugeridos": [
            "Se carga do sistema > 85% → abrir unidades temporárias",
            "Se eventos_24h > 5 → ativar equipe de resposta rápida",
            "Se disponibilidade_recursos < 30% → redistribuir insumos",
            "Se tempo_espera > 90 min → priorizar triagem emergencial",
            "Se densidade_eventos > 6 → ativar plano de contingência",
            "Se risco sistêmico alto → ativar estado de emergência"
        ]
    }
    validacao = validar_coerencia(paciente_alto_risco, resultado)
    assert validacao["coerente"] is True
    assert len(validacao["inconsistencias"]) == 0


def test_caso_coerente_baixo_risco(paciente_baixo_risco):
    """Cenário perfeitamente coerente para paciente em risco BAIXO sem protocolos acionados."""
    resultado = {
        "probabilidade": 0.05,
        "classificacao": "BAIXO",
        "protocolos_sugeridos": []
    }
    validacao = validar_coerencia(paciente_baixo_risco, resultado)
    assert validacao["coerente"] is True
    assert len(validacao["inconsistencias"]) == 0


def test_regra_a_protocolo_indevido_sem_atingir_limiar(paciente_alto_risco):
    """Regra A: Sugerir protocolo de SpO2 quando o paciente possui SpO2 normal (94%)."""
    resultado = {
        "probabilidade": 0.92,
        "classificacao": "ALTO",
        "protocolos_sugeridos": [
            "Se carga do sistema > 85% → abrir unidades temporárias",
            "Se eventos_24h > 5 → ativar equipe de resposta rápida",
            "Se disponibilidade_recursos < 30% → redistribuir insumos",
            "Se tempo_espera > 90 min → priorizar triagem emergencial",
            "Se densidade_eventos > 6 → ativar plano de contingência",
            "Se risco sistêmico alto → ativar estado de emergência",
            "Se SPO2 < 88% → iniciar suporte respiratório imediato"  # Indevido! SpO2 é 94%
        ]
    }
    validacao = validar_coerencia(paciente_alto_risco, resultado)
    assert validacao["coerente"] is False
    assert any("Regra A" in inc and "SPO2 < 88%" in inc for inc in validacao["inconsistencias"])


def test_regra_a_protocolo_nao_regulamentado(paciente_baixo_risco):
    """Regra A: Sugerir um protocolo inventado fora da lista oficial da instituição."""
    resultado = {
        "probabilidade": 0.10,
        "classificacao": "BAIXO",
        "protocolos_sugeridos": [
            "Se glicemia > 200 → aplicar insulina regular"  # Não existe nos 10 protocolos oficiais
        ]
    }
    validacao = validar_coerencia(paciente_baixo_risco, resultado)
    assert validacao["coerente"] is False
    assert any("Protocolo não regulamentado" in inc for inc in validacao["inconsistencias"])


def test_regra_b_omissao_de_protocolo_obrigatorio(paciente_alto_risco):
    """Regra B: Deixar de incluir protocolo acionado pelos parâmetros do paciente."""
    resultado = {
        "probabilidade": 0.92,
        "classificacao": "ALTO",
        "protocolos_sugeridos": [
            # Omitiu 'Se carga do sistema > 85% → abrir unidades temporárias' (carga é 88%)
            "Se eventos_24h > 5 → ativar equipe de resposta rápida",
            "Se disponibilidade_recursos < 30% → redistribuir insumos",
            "Se tempo_espera > 90 min → priorizar triagem emergencial",
            "Se densidade_eventos > 6 → ativar plano de contingência",
            "Se risco sistêmico alto → ativar estado de emergência"
        ]
    }
    validacao = validar_coerencia(paciente_alto_risco, resultado)
    assert validacao["coerente"] is False
    assert any("Regra B" in inc and "carga do sistema > 85%" in inc for inc in validacao["inconsistencias"])


def test_regra_c_divergencia_probabilidade_classificacao(paciente_baixo_risco):
    """Regra C: Probabilidade alta (0.85) com classificação 'BAIXO'."""
    resultado = {
        "probabilidade": 0.85,  # Deveria ser ALTO
        "classificacao": "BAIXO",
        "protocolos_sugeridos": []
    }
    validacao = validar_coerencia(paciente_baixo_risco, resultado)
    assert validacao["coerente"] is False
    assert any("Regra C" in inc and "0.85" in inc for inc in validacao["inconsistencias"])


def test_regra_d_alto_sem_risco_sistemico(paciente_alto_risco):
    """Regra D: Classificação ALTO sem o protocolo de estado de emergência."""
    resultado = {
        "probabilidade": 0.92,
        "classificacao": "ALTO",
        "protocolos_sugeridos": [
            "Se carga do sistema > 85% → abrir unidades temporárias",
            "Se eventos_24h > 5 → ativar equipe de resposta rápida",
            "Se disponibilidade_recursos < 30% → redistribuir insumos",
            "Se tempo_espera > 90 min → priorizar triagem emergencial",
            "Se densidade_eventos > 6 → ativar plano de contingência"
            # Omitiu propositalmente: "Se risco sistêmico alto → ativar estado de emergência"
        ]
    }
    validacao = validar_coerencia(paciente_alto_risco, resultado)
    assert validacao["coerente"] is False
    assert any("Regra D" in inc and "risco sistêmico alto" in inc for inc in validacao["inconsistencias"])


def test_regra_d_baixo_com_risco_sistemico(paciente_baixo_risco):
    """Regra D: Inclusão indevida de protocolo de risco sistêmico alto em paciente BAIXO."""
    resultado = {
        "probabilidade": 0.10,
        "classificacao": "BAIXO",
        "protocolos_sugeridos": [
            "Se risco sistêmico alto → ativar estado de emergência"
        ]
    }
    validacao = validar_coerencia(paciente_baixo_risco, resultado)
    assert validacao["coerente"] is False
    assert any("Regra D" in inc and "permitido exclusivamente em risco ALTO" in inc for inc in validacao["inconsistencias"])


def test_simulacao_teste_adulteracao_novo_caso(paciente_alto_risco):
    """Cenário exato de adulteração requerido para o run_auditado.py."""
    # Decisão fraudulenta inserindo SpO2 em paciente com SpO2 = 94%
    resultado_adulterado = {
        "probabilidade": 0.92,
        "classificacao": "ALTO",
        "protocolos_sugeridos": [
            "Se carga do sistema > 85% → abrir unidades temporárias",
            "Se eventos_24h > 5 → ativar equipe de resposta rápida",
            "Se disponibilidade_recursos < 30% → redistribuir insumos",
            "Se tempo_espera > 90 min → priorizar triagem emergencial",
            "Se densidade_eventos > 6 → ativar plano de contingência",
            "Se risco sistêmico alto → ativar estado de emergência",
            "Se SPO2 < 88% → iniciar suporte respiratório imediato"
        ]
    }
    res = validar_coerencia(paciente_alto_risco, resultado_adulterado)
    assert res["coerente"] is False
    assert len(res["inconsistencias"]) == 1
    assert "SPO2 < 88%" in res["inconsistencias"][0]
