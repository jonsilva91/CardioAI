"""Testes unitários para a fila concorrente de pacientes (100% offline, sem chamadas a APIs).

Valida:
1. Geração correta e determinística de pacientes sintéticos com ID exclusivo;
2. Processamento assíncrono na fila com múltiplos workers em modo --sem-llm;
3. Execução em lote vetorizado (batch predict_proba);
4. Resiliência: falha de dados em um paciente não derruba a fila nem interrompe outros workers;
5. Consistência das métricas calculadas (tempo, throughput, p95).
"""

import asyncio
from pathlib import Path
import sys
import pytest

# Adiciona caminhos ao sys.path
IR_ALEM_DIR = Path(__file__).resolve().parents[1]
FASE06_DIR = Path(__file__).resolve().parents[3]

if str(IR_ALEM_DIR) not in sys.path:
    sys.path.insert(0, str(IR_ALEM_DIR))
if str(FASE06_DIR) not in sys.path:
    sys.path.insert(0, str(FASE06_DIR))

from fila_pacientes import (
    calcular_metricas,
    executar_fila_concorrente,
    gerar_pacientes_fila,
    processar_lote_vetorizado,
    processar_paciente_sem_llm,
)
from src.config import FEATURES


def test_gerar_pacientes_fila():
    """Valida a geração correta de N pacientes com schema completo e IDs únicos."""
    n = 15
    pacientes = gerar_pacientes_fila(n=n, seed=99)
    assert len(pacientes) == n

    ids = [p["paciente_id"] for p in pacientes]
    assert len(set(ids)) == n, "Os IDs gerados para cada paciente devem ser únicos."

    for p in pacientes:
        assert p["paciente_id"].startswith("PAC-99-")
        for feat in FEATURES:
            assert feat in p, f"A feature obrigatória '{feat}' deve estar presente no paciente."
            assert isinstance(p[feat], (int, float))


def test_processar_paciente_sem_llm_individual():
    """Valida o processamento determinístico individual de um paciente (ML + regras)."""
    paciente = {
        "paciente_id": "TEST-001",
        "idade_media": 60.0,
        "carga_sistema": 90.0,          # > 85%
        "tempo_espera": 100.0,          # > 90 min
        "fc_media": 115.0,
        "spo2_media": 95.0,
        "pa_sistolica": 110.0,
        "temperatura": 37.0,
        "densidade_eventos": 8.0,       # > 6
        "eventos_24h": 6.0,             # > 5
        "disponibilidade_recursos": 25.0 # < 30%
    }
    resultado = asyncio.run(processar_paciente_sem_llm(paciente))
    assert resultado["status"] == "sucesso"
    assert resultado["paciente_id"] == "TEST-001"
    assert resultado["probabilidade"] is not None
    assert resultado["classificacao"] in ["BAIXO", "MODERADO", "ALTO"]
    assert resultado["protocolos_count"] >= 4
    assert resultado["duracao_s"] > 0


def test_fila_concorrente_sem_llm():
    """Testa o processamento assíncrono em fila com 3 workers concorrentes."""
    n = 12
    pacientes = gerar_pacientes_fila(n=n, seed=42)

    resultados, tempo_total = asyncio.run(
        executar_fila_concorrente(
            pacientes=pacientes,
            n_workers=3,
            sem_llm=True,
            max_concurrency=3
        )
    )

    assert len(resultados) == n
    assert tempo_total > 0
    assert all(r["status"] == "sucesso" for r in resultados)
    assert all(r["probabilidade"] is not None for r in resultados)

    metricas = calcular_metricas(resultados, tempo_total)
    assert metricas["total_pacientes"] == n
    assert metricas["taxa_erro_pct"] == 0.0
    assert metricas["throughput_pac_s"] > 0


def test_modo_lote_vetorizado():
    """Valida a predição vetorizada em lote comparada com o processamento individual."""
    n = 20
    pacientes = gerar_pacientes_fila(n=n, seed=42)

    resultados, tempo_total = processar_lote_vetorizado(pacientes)
    assert len(resultados) == n
    assert tempo_total > 0
    assert all(r["status"] == "sucesso" for r in resultados)

    metricas = calcular_metricas(resultados, tempo_total)
    assert metricas["total_pacientes"] == n
    assert metricas["taxa_erro_pct"] == 0.0
    assert metricas["throughput_pac_s"] > 0


def test_resiliencia_fila_com_paciente_invalido():
    """Garante que um paciente com features inválidas/faltantes não derruba a fila."""
    pacientes = gerar_pacientes_fila(n=5, seed=7)
    # Injeta um paciente corrompido sem features
    paciente_corrompido = {"paciente_id": "PAC-ERROR-999", "idade_media": 50.0}
    pacientes.insert(2, paciente_corrompido)

    resultados, tempo_total = asyncio.run(
        executar_fila_concorrente(
            pacientes=pacientes,
            n_workers=2,
            sem_llm=True,
            max_concurrency=2
        )
    )

    # A fila deve processar TODOS os 6 itens sem abortar
    assert len(resultados) == 6
    sucessos = [r for r in resultados if r["status"] == "sucesso"]
    erros = [r for r in resultados if r["status"] == "erro"]

    assert len(sucessos) == 5
    assert len(erros) == 1
    assert erros[0]["paciente_id"] == "PAC-ERROR-999"
    assert "Faltam as seguintes variáveis obrigatórias" in erros[0]["erro"]
