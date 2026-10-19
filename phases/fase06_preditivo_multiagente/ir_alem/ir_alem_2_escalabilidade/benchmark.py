"""Script de benchmark de escalabilidade e concorrência para o CardioAI.

Executa baterias reais de testes para medir throughput, latência e taxa de erro:
1. Modo Sem LLM (1.000 pacientes):
   - Fila concorrente com 1 worker
   - Fila concorrente com 2 workers
   - Fila concorrente com 4 workers
   - Fila concorrente com 8 workers
   - Modo Lote Vetorizado (predict_proba em batch)

2. Modo Com LLM Real (10 pacientes com OpenAI Agents SDK):
   - Fila concorrente com 1 worker
   - Fila concorrente com 2 workers
   - Fila concorrente com 4 workers

Salva os dados coletados em resultados/benchmark.csv e gráficos em resultados/benchmark.png.
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sys
import time
from typing import Any
import matplotlib.pyplot as plt
import pandas as pd

# Suporte UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CURRENT_DIR = Path(__file__).resolve().parent
RESULTADOS_DIR = CURRENT_DIR / "resultados"
CSV_PATH = RESULTADOS_DIR / "benchmark.csv"
PNG_PATH = RESULTADOS_DIR / "benchmark.png"

from fila_pacientes import (
    calcular_metricas,
    executar_fila_concorrente,
    gerar_pacientes_fila,
    processar_lote_vetorizado,
)


def rodar_benchmark_sem_llm() -> list[dict[str, Any]]:
    """Executa a bateria de 1.000 pacientes no modo sem LLM."""
    print("\n" + "=" * 80)
    print("🚀 BATERIA 1: BENCHMARK SEM LLM (1.000 PACIENTES)")
    print("=" * 80)

    n_pacientes = 1000
    pacientes = gerar_pacientes_fila(n=n_pacientes, seed=42)
    registros: list[dict[str, Any]] = []

    # Workers 1, 2, 4, 8
    for w in [1, 2, 4, 8]:
        print(f"\n▶️ Testando Fila com {w} Worker(s) (1.000 pacientes)...")
        res, t_tot = asyncio.run(
            executar_fila_concorrente(
                pacientes=pacientes,
                n_workers=w,
                sem_llm=True,
                max_concurrency=w
            )
        )
        met = calcular_metricas(res, t_tot)
        print(f"   ⏱️ Tempo Total: {met['tempo_total_s']}s | Throughput: {met['throughput_pac_s']} pac/s | P95: {met['p95_latencia_s']}s")
        registros.append({
            "cenario": f"Fila ({w}w) - Sem LLM",
            "tipo": "Sem LLM",
            "modo": "Fila Assíncrona",
            "n_pacientes": n_pacientes,
            "workers": w,
            "tempo_total_s": met["tempo_total_s"],
            "tempo_medio_paciente_s": met["tempo_medio_s"],
            "throughput_pac_s": met["throughput_pac_s"],
            "p95_latencia_s": met["p95_latencia_s"],
            "taxa_erro_pct": met["taxa_erro_pct"]
        })

    # Modo Lote Vetorizado
    print("\n▶️ Testando Modo Lote Vetorizado (predict_proba em batch, 1.000 pacientes)...")
    res_lote, t_lote = processar_lote_vetorizado(pacientes)
    met_lote = calcular_metricas(res_lote, t_lote)
    print(f"   ⏱️ Tempo Total: {met_lote['tempo_total_s']}s | Throughput: {met_lote['throughput_pac_s']} pac/s | P95: {met_lote['p95_latencia_s']}s")
    registros.append({
        "cenario": "Lote Vetorizado (Batch ML)",
        "tipo": "Sem LLM",
        "modo": "Lote Vetorizado",
        "n_pacientes": n_pacientes,
        "workers": 1,
        "tempo_total_s": met_lote["tempo_total_s"],
        "tempo_medio_paciente_s": met_lote["tempo_medio_s"],
        "throughput_pac_s": met_lote["throughput_pac_s"],
        "p95_latencia_s": met_lote["p95_latencia_s"],
        "taxa_erro_pct": met_lote["taxa_erro_pct"]
    })

    return registros


def rodar_benchmark_com_llm() -> list[dict[str, Any]]:
    """Executa a bateria controlada de 10 pacientes com LLM real dentro de um único event loop."""
    print("\n" + "=" * 80)
    print("🤖 BATERIA 2: BENCHMARK COM LLM REAL (10 PACIENTES - OPENAI AGENTS SDK)")
    print("=" * 80)

    n_pacientes = 10
    pacientes = gerar_pacientes_fila(n=n_pacientes, seed=123)

    async def _executar_todas_rodadas() -> list[dict[str, Any]]:
        registros: list[dict[str, Any]] = []
        for w in [1, 2, 4]:
            print(f"\n▶️ Testando Multiagente com {w} Worker(s) concorrente(s) (10 pacientes)...")
            res, t_tot = await executar_fila_concorrente(
                pacientes=pacientes,
                n_workers=w,
                sem_llm=False,
                max_concurrency=w,
                timeout_s=60.0
            )
            met = calcular_metricas(res, t_tot)
            print(f"   ⏱️ Tempo Total: {met['tempo_total_s']}s | Throughput: {met['throughput_pac_s']} pac/s | Latência Média: {met['tempo_medio_s']}s")

            # Salva o detalhe por paciente desta rodada
            df_detalhe = pd.DataFrame([
                {
                    "paciente_id": r.get("paciente_id"),
                    "status": r.get("status"),
                    "duracao_s": round(r.get("duracao_s", 0.0), 4),
                    "erro": r.get("erro") or ""
                }
                for r in res
            ])
            detalhe_path = RESULTADOS_DIR / f"detalhe_llm_{w}w.csv"
            df_detalhe.to_csv(detalhe_path, index=False, encoding="utf-8")
            print(f"   📄 Detalhe individual salvo em: {detalhe_path}")

            registros.append({
                "cenario": f"Multiagente ({w}w) - LLM Real",
                "tipo": "Com LLM Real",
                "modo": "Fila Assíncrona",
                "n_pacientes": n_pacientes,
                "workers": w,
                "tempo_total_s": met["tempo_total_s"],
                "tempo_medio_paciente_s": met["tempo_medio_s"],
                "throughput_pac_s": met["throughput_pac_s"],
                "p95_latencia_s": met["p95_latencia_s"],
                "taxa_erro_pct": met["taxa_erro_pct"]
            })
        return registros

    return asyncio.run(_executar_todas_rodadas())


def gerar_graficos_benchmark(df: pd.DataFrame, caminho_png: Path) -> None:
    """Gera visualização comparativa profissional de escalabilidade e latência."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=200)
    fig.patch.set_facecolor("#0f172a")

    for ax in axes:
        ax.set_facecolor("#1e293b")
        ax.tick_params(colors="#94a3b8", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#334155")

    # 1. Gráfico Sem LLM: Throughput por Workers e Batch
    ax1 = axes[0]
    df_sem_llm = df[df["tipo"] == "Sem LLM"]
    cores_sem = ["#38bdf8", "#38bdf8", "#38bdf8", "#38bdf8", "#10b981"]
    barras1 = ax1.bar(range(len(df_sem_llm)), df_sem_llm["throughput_pac_s"], color=cores_sem, width=0.6)
    ax1.set_title("Vazão Sem LLM (1.000 pac)", fontsize=10, fontweight="bold", color="#f8fafc", pad=10)
    ax1.set_ylabel("Throughput (pacientes/s)", color="#94a3b8", fontsize=8.5)
    ax1.set_xticks(range(len(df_sem_llm)))
    ax1.set_xticklabels(["1W", "2W", "4W", "8W", "Lote Batch"], rotation=15, color="#cbd5e1")
    for b in barras1:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width()/2, h + max(df_sem_llm["throughput_pac_s"])*0.02,
                 f"{h:.1f}", ha="center", va="bottom", color="#f8fafc", fontsize=7.5, fontweight="bold")

    # 2. Gráfico Com LLM Real: Throughput vs Workers
    ax2 = axes[1]
    df_com_llm = df[df["tipo"] == "Com LLM Real"]
    barras2 = ax2.bar(range(len(df_com_llm)), df_com_llm["throughput_pac_s"], color="#a855f7", width=0.5)
    ax2.set_title("Vazão Multiagente LLM Real (10 pac)", fontsize=10, fontweight="bold", color="#f8fafc", pad=10)
    ax2.set_ylabel("Throughput (pacientes/s)", color="#94a3b8", fontsize=8.5)
    ax2.set_xticks(range(len(df_com_llm)))
    ax2.set_xticklabels(["1 Worker", "2 Workers", "4 Workers"], color="#cbd5e1")
    for b in barras2:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2, h + max(df_com_llm["throughput_pac_s"])*0.02,
                 f"{h:.2f} pac/s", ha="center", va="bottom", color="#f8fafc", fontsize=7.5, fontweight="bold")

    # 3. Gráfico Gargalo de Latência: ML Local vs LLM Roundtrip
    ax3 = axes[2]
    # Compara a latência média da inferência ML local vs LLM
    lat_ml_local = df[df["cenario"].str.contains("Lote")]["tempo_medio_paciente_s"].values[0] * 1000  # em ms
    lat_fila_ml = df[df["cenario"].str.contains(r"Fila \(4w\) - Sem LLM")]["tempo_medio_paciente_s"].values[0] * 1000
    lat_llm = df[df["cenario"].str.contains(r"Multiagente \(4w\)")]["tempo_medio_paciente_s"].values[0]  # em segundos

    comparacao = [
        ("ML Batch\n(Vetorizado)", lat_ml_local, "ms"),
        ("ML Fila 4W\n(Local)", lat_fila_ml, "ms"),
        ("Multiagente\nLLM (4W)", lat_llm * 1000, "ms")  # converte para ms para escala log
    ]

    labels = [c[0] for c in comparacao]
    valores = [c[1] for c in comparacao]
    barras3 = ax3.bar(labels, valores, color=["#10b981", "#38bdf8", "#f43f5e"], width=0.55)
    ax3.set_yscale("log")
    ax3.set_title("Identificação do Gargalo (Latência em Escala Log)", fontsize=10, fontweight="bold", color="#f8fafc", pad=10)
    ax3.set_ylabel("Latência Média por Paciente (ms)", color="#94a3b8", fontsize=8.5)
    for b, c in zip(barras3, comparacao):
        h = b.get_height()
        texto = f"{h:.1f} ms" if h < 1000 else f"{h/1000:.2f} s"
        ax3.text(b.get_x() + b.get_width()/2, h * 1.3, texto, ha="center", va="bottom", color="#f8fafc", fontsize=7.5, fontweight="bold")

    plt.suptitle("CardioAI — Resultados Reais de Benchmark e Escalabilidade", fontsize=13, fontweight="bold", color="#f8fafc", y=1.02)
    plt.tight_layout()
    plt.savefig(caminho_png, format="PNG", dpi=200, bbox_inches="tight")
    plt.close()
    print(f"📊 Gráficos de benchmark gerados em: {caminho_png}")


def main() -> None:
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

    apenas_llm = "--apenas-llm" in sys.argv or "--llm-only" in sys.argv

    print("\n" + "=" * 80)
    print("🏥 INICIANDO BENCHMARK OFICIAL DE ESCALABILIDADE CARDIOAI")
    print(f"📁 Destino dos dados: {CSV_PATH}")
    print(f"📊 Destino dos gráficos: {PNG_PATH}")
    if apenas_llm:
        print("⚡ Modo: Apenas Bateria com LLM Real (reaproveitando resultados Sem LLM de benchmark.csv)")
    print("=" * 80)

    if apenas_llm and CSV_PATH.exists():
        df_anterior = pd.read_csv(CSV_PATH)
        registros_sem = df_anterior[df_anterior["tipo"] == "Sem LLM"].to_dict("records")
    else:
        # 1. Bateria Sem LLM (1.000 pacientes)
        registros_sem = rodar_benchmark_sem_llm()

    # 2. Bateria Com LLM Real (10 pacientes dentro de um único asyncio.run)
    registros_com = rodar_benchmark_com_llm()

    todos = registros_sem + registros_com
    df = pd.DataFrame(todos)

    # Salva CSV
    df.to_csv(CSV_PATH, index=False)
    print(f"\n💾 Tabela de resultados gravada em: {CSV_PATH}")

    # Gera Gráficos
    gerar_graficos_benchmark(df, PNG_PATH)

    print("\n" + "=" * 105)
    print("📋 TABELA RESUMO CONSOLIDADA DO BENCHMARK:")
    print("=" * 105)
    print(f"{'CENÁRIO':<30} | {'PACIENTES':<9} | {'WORKERS':<7} | {'TEMPO TOTAL':<12} | {'MÉDIA/PAC':<10} | {'THROUGHPUT':<12} | {'ERROS':<6}")
    print("-" * 105)
    for r in todos:
        cen = r["cenario"]
        n_p = str(r["n_pacientes"])
        w = str(r["workers"])
        t_tot = f"{r['tempo_total_s']:.2f}s"
        t_med = f"{r['tempo_medio_paciente_s']:.4f}s"
        tp = f"{r['throughput_pac_s']:.2f} pac/s"
        err = f"{r['taxa_erro_pct']:.1f}%"
        print(f"{cen:<30} | {n_p:<9} | {w:<7} | {t_tot:<12} | {t_med:<10} | {tp:<12} | {err:<6}")
    print("=" * 105 + "\n")


if __name__ == "__main__":
    main()
