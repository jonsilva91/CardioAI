"""Módulo de processamento concorrente e em fila de pacientes sintéticos.

Implementa arquitetura assíncrona baseada em fila (asyncio.Queue) e pool de W workers
para simular a ingestão contínua e escalabilidade hospitalar:
- Geração de N pacientes sintéticos reaproveitando src.data_generation
- Controle de concorrência com asyncio.Semaphore
- Timeout individual por paciente e retry com backoff exponencial
- Modo --sem-llm para medição pura de throughput do modelo ML + regras
- Modo --lote para predição vetorizada em lote (batch predict_proba)
"""

import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time
from typing import Any
import numpy as np
import pandas as pd

# Suporte UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Caminhos base da Fase 6
FASE06_DIR = Path(__file__).resolve().parents[2]
if str(FASE06_DIR) not in sys.path:
    sys.path.insert(0, str(FASE06_DIR))

from dotenv import load_dotenv
load_dotenv(FASE06_DIR / ".env")
load_dotenv()

from agents import Runner
from agents.exceptions import OutputGuardrailTripwireTriggered
from src.config import FEATURES, OPENAI_MODEL, classificar_risco
from src.data_generation import gerar_base_sintetica
from src.predictor import carregar_modelo_preditivo, prever_risco
from src.protocols import consultar_protocolos
from src.agents_system.cardio_agents import criar_sistema_agentes
from src.agents_system.context import CardioContext
from src.agents_system.schemas import RecomendacaoFinal


def gerar_pacientes_fila(n: int, seed: int = 42) -> list[dict[str, Any]]:
    """Gera N pacientes sintéticos reaproveitando src.data_generation sem duplicar código."""
    df = gerar_base_sintetica(n=n, seed=seed)
    df_features = df.drop(columns=["pico_risco"], errors="ignore")
    pacientes = df_features.to_dict(orient="records")
    for idx, p in enumerate(pacientes, start=1):
        p["paciente_id"] = f"PAC-{seed}-{idx:05d}"
    return pacientes


async def processar_paciente_sem_llm(paciente: dict[str, Any]) -> dict[str, Any]:
    """Processa um paciente executando inferência ML + regras clínicas deterministicamente."""
    t0 = time.perf_counter()
    try:
        # Executa inferência em threadpool para não bloquear o loop de eventos
        res_ml = await asyncio.to_thread(prever_risco, paciente)
        prots = consultar_protocolos(paciente, res_ml["classificacao"])
        duracao = time.perf_counter() - t0
        return {
            "paciente_id": paciente.get("paciente_id"),
            "probabilidade": res_ml["probabilidade"],
            "classificacao": res_ml["classificacao"],
            "protocolos_count": len(prots),
            "status": "sucesso",
            "duracao_s": duracao,
            "erro": None
        }
    except Exception as e:
        duracao = time.perf_counter() - t0
        return {
            "paciente_id": paciente.get("paciente_id"),
            "probabilidade": None,
            "classificacao": None,
            "protocolos_count": 0,
            "status": "erro",
            "duracao_s": duracao,
            "erro": str(e)
        }



async def processar_paciente_com_llm(
    paciente: dict[str, Any],
    semaphore: asyncio.Semaphore,
    timeout_s: float = 45.0,
    max_retries: int = 3,
    model_name: str = OPENAI_MODEL
) -> dict[str, Any]:
    """Processa paciente via sistema multiagente (OpenAI Agents SDK) com controle de resiliência."""
    t0 = time.perf_counter()
    paciente_id = paciente.get("paciente_id", "DESCONHECIDO")

    prompt_inicial = (
        "Inicie a triagem do novo paciente cardiovascular disponível no contexto. "
        "Acione o Agente Analista de Risco para calcular o score, encaminhe ao Especialista "
        "em Protocolos para verificar as diretrizes e, por fim, acione o Planejador de Resposta "
        "para sintetizar o plano operacional completo."
    )

    ultimo_erro = ""
    for tentativa in range(1, max_retries + 1):
        try:
            async with semaphore:
                agente_orquestrador, _, _, _ = criar_sistema_agentes(model=model_name)
                cardio_context = CardioContext(dados_paciente=paciente)

                coro = Runner.run(
                    agente_orquestrador,
                    prompt_inicial,
                    context=cardio_context
                )
                run_result = await asyncio.wait_for(coro, timeout=timeout_s)

                out = run_result.final_output
                if isinstance(out, RecomendacaoFinal):
                    rec = out
                elif isinstance(out, dict):
                    rec = RecomendacaoFinal(**out)
                else:
                    rec = RecomendacaoFinal.model_validate_json(str(out))

                duracao = time.perf_counter() - t0
                return {
                    "paciente_id": paciente_id,
                    "probabilidade": rec.probabilidade,
                    "classificacao": rec.classificacao,
                    "protocolos_count": len(rec.protocolos_sugeridos),
                    "status": "sucesso",
                    "duracao_s": duracao,
                    "erro": None
                }

        except asyncio.TimeoutError:
            ultimo_erro = f"Timeout de {timeout_s}s excedido na tentativa {tentativa}/{max_retries}"
            if tentativa < max_retries:
                espera = 0.5 * (2 ** (tentativa - 1))
                await asyncio.sleep(espera)

        except OutputGuardrailTripwireTriggered as e:
            duracao = time.perf_counter() - t0
            return {
                "paciente_id": paciente_id,
                "probabilidade": None,
                "classificacao": None,
                "protocolos_count": 0,
                "status": "bloqueado_guardrail",
                "duracao_s": duracao,
                "erro": str(e)
            }

        except Exception as e:
            err_msg = str(e)
            ultimo_erro = f"Erro na tentativa {tentativa}/{max_retries}: {err_msg}"
            if any(term in err_msg.lower() for term in ["rate", "429", "limit", "connection", "timeout"]):
                if tentativa < max_retries:
                    espera = 1.0 * (2 ** (tentativa - 1))
                    await asyncio.sleep(espera)
            else:
                break

    duracao = time.perf_counter() - t0
    return {
        "paciente_id": paciente_id,
        "probabilidade": None,
        "classificacao": None,
        "protocolos_count": 0,
        "status": "erro",
        "duracao_s": duracao,
        "erro": ultimo_erro
    }


def processar_lote_vetorizado(pacientes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], float]:
    """Executa a predição vetorizada em batch no modelo de Machine Learning e regras clínicas."""
    t0 = time.perf_counter()
    df = pd.DataFrame(pacientes)
    df_features = df[FEATURES]

    artefato = carregar_modelo_preditivo()
    modelo = artefato["model"]

    # Inferência em lote vetorizada (predict_proba)
    probabilidades = modelo.predict_proba(df_features)[:, 1]

    resultados: list[dict[str, Any]] = []
    for idx, (p, prob) in enumerate(zip(pacientes, probabilidades)):
        t_item_inicio = time.perf_counter()
        prob_arred = round(float(prob), 2)
        classe = classificar_risco(prob_arred)
        prots = consultar_protocolos(p, classe)
        t_item_fim = time.perf_counter()

        resultados.append({
            "paciente_id": p.get("paciente_id", f"PAC-LOTE-{idx+1:05d}"),
            "probabilidade": prob_arred,
            "classificacao": classe,
            "protocolos_count": len(prots),
            "status": "sucesso",
            "duracao_s": t_item_fim - t_item_inicio,
            "erro": None
        })

    tempo_total = time.perf_counter() - t0
    return resultados, tempo_total


async def executar_fila_concorrente(
    pacientes: list[dict[str, Any]],
    n_workers: int = 4,
    sem_llm: bool = True,
    max_concurrency: int = 4,
    timeout_s: float = 45.0,
    model_name: str = OPENAI_MODEL
) -> tuple[list[dict[str, Any]], float]:
    """Alimenta a fila assíncrona e consome com N workers concorrentes."""
    # Pré-aquece o modelo preditivo em memória para isolar a medição de inferência
    if sem_llm:
        carregar_modelo_preditivo()

    fila: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    for p in pacientes:
        await fila.put(p)

    resultados: list[dict[str, Any]] = []
    semaphore = asyncio.Semaphore(max_concurrency)

    async def worker(worker_id: int) -> None:
        while True:
            try:
                paciente = await fila.get()
            except asyncio.CancelledError:
                break

            try:
                if sem_llm:
                    res = await processar_paciente_sem_llm(paciente)
                else:
                    res = await processar_paciente_com_llm(
                        paciente=paciente,
                        semaphore=semaphore,
                        timeout_s=timeout_s,
                        model_name=model_name
                    )
                resultados.append(res)
            finally:
                fila.task_done()

    t0 = time.perf_counter()
    workers = [asyncio.create_task(worker(w_id)) for w_id in range(n_workers)]

    # Aguarda o esvaziamento completo da fila
    await fila.join()

    # Cancela os workers ociosos
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    tempo_total = time.perf_counter() - t0
    return resultados, tempo_total


def calcular_metricas(resultados: list[dict[str, Any]], tempo_total_s: float) -> dict[str, Any]:
    """Calcula estatísticas de desempenho, latência e vazão do lote executado."""
    n_total = len(resultados)
    if n_total == 0:
        return {
            "total_pacientes": 0, "tempo_total_s": 0.0, "tempo_medio_s": 0.0,
            "throughput_pac_s": 0.0, "p95_latencia_s": 0.0, "taxa_erro_pct": 0.0
        }

    duracoes = [r["duracao_s"] for r in resultados]
    erros = [r for r in resultados if r["status"] in ["erro", "bloqueado_guardrail"]]

    return {
        "total_pacientes": n_total,
        "tempo_total_s": round(tempo_total_s, 4),
        "tempo_medio_s": round(float(np.mean(duracoes)), 4),
        "throughput_pac_s": round(n_total / tempo_total_s, 2) if tempo_total_s > 0 else 0.0,
        "p95_latencia_s": round(float(np.percentile(duracoes, 95)), 4),
        "taxa_erro_pct": round((len(erros) / n_total) * 100, 2)
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fila concorrente de pacientes hospitalares CardioAI"
    )
    parser.add_argument("--n", type=int, default=100, help="Número de pacientes sintéticos a processar (padrão: 100)")
    parser.add_argument("--workers", type=int, default=4, help="Número de workers concorrentes (padrão: 4)")
    parser.add_argument("--sem-llm", action="store_true", help="Processa apenas ML + regras determinísticas (sem chamadas a LLM)")
    parser.add_argument("--lote", action="store_true", help="Processa em batch vetorizado (predict_proba do modelo em lote)")
    parser.add_argument("--seed", type=int, default=42, help="Semente pseudoaleatória para reprodutibilidade (padrão: 42)")
    parser.add_argument("--timeout", type=float, default=45.0, help="Timeout por paciente em segundos (padrão: 45s)")
    parser.add_argument("--concurrency", type=int, default=4, help="Limite máximo de concorrência simultânea via Semaphore (padrão: 4)")

    args = parser.parse_args()

    print("=" * 80)
    print("🏥 CARDIOAI — FILA DE PROCESSAMENTO CONCORRENTE DE PACIENTES")
    print(f"📊 Pacientes: {args.n} | Workers: {args.workers} | Seed: {args.seed}")
    modo_str = "LOTE VETORIZADO (ML + Regras)" if args.lote else ("SEM LLM (Fila + ML + Regras)" if args.sem_llm else "COM LLM REAL (OpenAI Agents SDK)")
    print(f"⚙️ Modo de Execução: {modo_str}")
    print("=" * 80)

    pacientes = gerar_pacientes_fila(n=args.n, seed=args.seed)

    if args.lote:
        resultados, tempo_total = processar_lote_vetorizado(pacientes)
    else:
        resultados, tempo_total = asyncio.run(
            executar_fila_concorrente(
                pacientes=pacientes,
                n_workers=args.workers,
                sem_llm=args.sem_llm,
                max_concurrency=args.concurrency,
                timeout_s=args.timeout
            )
        )

    metricas = calcular_metricas(resultados, tempo_total)

    print("\n" + "=" * 80)
    print("📈 RESULTADOS DO PROCESSAMENTO:")
    print(f"⏱️ Tempo Total: {metricas['tempo_total_s']}s")
    print(f"⏱️ Tempo Médio por Paciente: {metricas['tempo_medio_s']}s")
    print(f"🚀 Throughput (Vazão): {metricas['throughput_pac_s']} pacientes/segundo")
    print(f"📊 Latência P95: {metricas['p95_latencia_s']}s")
    print(f"🚨 Taxa de Erro: {metricas['taxa_erro_pct']}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
