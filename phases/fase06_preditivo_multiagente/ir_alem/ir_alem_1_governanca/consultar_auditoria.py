"""Ferramenta CLI para consulta, filtragem e auditoria de decisões do CardioAI.

Lê o log append-only logs/decisoes.jsonl e possibilita filtros por classificação de risco,
session_id e detecção imediata de decisões incoerentes ou adulteradas.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Any

# Suporte UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_LOG_PATH = Path(__file__).resolve().parent / "logs" / "decisoes.jsonl"


def carregar_logs(caminho_log: Path) -> list[dict[str, Any]]:
    """Lê todas as decisões do arquivo JSONL."""
    if not caminho_log.exists():
        print(f"⚠️ Arquivo de log não encontrado em: {caminho_log}")
        return []

    registros: list[dict[str, Any]] = []
    with open(caminho_log, "r", encoding="utf-8") as f:
        for idx, linha in enumerate(f, start=1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                registros.append(json.loads(linha))
            except json.JSONDecodeError as e:
                print(f"⚠️ Erro ao decodificar linha {idx}: {e}", file=sys.stderr)
    return registros


def formatar_tabela_resumo(registros: list[dict[str, Any]]) -> None:
    """Imprime uma tabela formatada no terminal com as decisões filtradas."""
    print("\n" + "=" * 115)
    print(f"{'ID DECISÃO':<10} | {'DATA/HORA (UTC)':<20} | {'SESSÃO':<18} | {'PROB':<5} | {'CLASSE':<8} | {'COERENTE':<8} | {'GUARDRAIL':<9} | {'TIPO':<12}")
    print("=" * 115)

    for r in registros:
        id_curto = str(r.get("id_decisao", ""))[:8]
        ts = str(r.get("timestamp", ""))[:19].replace("T", " ")
        sess = str(r.get("session_id", ""))[:18]
        prob = f"{float(r.get('probabilidade', 0.0)):.2f}" if r.get("probabilidade") is not None else "N/A"
        classe = str(r.get("classificacao", "N/A"))
        coerente_bool = r.get("validacao_coerencia", {}).get("coerente", False)
        coerente = "SIM ✅" if coerente_bool else "NÃO ❌"
        guard = str(r.get("guardrail_status", "N/A")).upper()
        guard_fmt = f"{guard} ✅" if guard == "APROVADO" else f"{guard} 🚨"
        tipo = "ADULTERAÇÃO" if r.get("teste_adulteracao") else "PADRÃO"

        print(f"{id_curto:<10} | {ts:<20} | {sess:<18} | {prob:<5} | {classe:<8} | {coerente:<8} | {guard_fmt:<9} | {tipo:<12}")

    print("=" * 115)


def exibir_detalhes_registro(r: dict[str, Any]) -> None:
    """Exibe os dados detalhados de uma decisão específica."""
    print("\n" + "-" * 75)
    print(f"🔍 DETALHES DA DECISÃO: {r.get('id_decisao')}")
    print(f"📅 Timestamp: {r.get('timestamp')}")
    print(f"🆔 Session ID: {r.get('session_id')}")
    print(f"🔒 SHA-256 Entrada: {r.get('hash_dados_entrada')}")
    print(f"🤖 Modelo LLM: {r.get('modelo_llm')}")

    mod_pred = r.get("modelo_preditivo", {})
    print(f"🧠 Modelo ML: {mod_pred.get('nome')} (v{mod_pred.get('versao_sklearn')}) - Acurácia: {mod_pred.get('metricas', {}).get('accuracy')}")

    print(f"📊 Probabilidade: {r.get('probabilidade')} | Classificação: {r.get('classificacao')}")
    print(f"🛡️ Guardrail Status: {r.get('guardrail_status')}")

    val = r.get("validacao_coerencia", {})
    coerente_str = "COERENTE ✅" if val.get("coerente") else "INCOERENTE ❌"
    print(f"⚖️ Validação de Coerência: {coerente_str}")
    if val.get("inconsistencias"):
        print("   Inconsistências detectadas:")
        for inc in val["inconsistencias"]:
            print(f"   - ⚠️ {inc}")

    print("\n📋 Protocolos Sugeridos:")
    for prot in r.get("protocolos_sugeridos", []):
        print(f"   • {prot}")

    print("\n🔄 Sequência de Handoffs:")
    for h in r.get("sequencia_handoffs", []):
        print(f"   ➔ {h.get('de')} ➔ {h.get('para')}")

    print("\n🔧 Ferramentas (Tools) Chamadas:")
    for t in r.get("tools_chamadas", []):
        print(f"   • [{t.get('agente')}] {t.get('tool')} ({t.get('status')})")

    if r.get("teste_adulteracao"):
        print("\n🧪 ATENÇÃO: Este registro é marcado como TESTE CONTROLADO DE ADULTERAÇÃO.")
    print("-" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consulta e auditoria de decisões do sistema multiagente CardioAI"
    )
    parser.add_argument(
        "--log",
        type=str,
        default=str(DEFAULT_LOG_PATH),
        help=f"Caminho do arquivo de log jsonl (padrão: {DEFAULT_LOG_PATH})"
    )
    parser.add_argument(
        "--classificacao",
        type=str,
        choices=["BAIXO", "MODERADO", "ALTO"],
        help="Filtrar por classificação de risco (BAIXO, MODERADO ou ALTO)"
    )
    parser.add_argument(
        "--session-id",
        type=str,
        help="Filtrar por identificador de sessão (ou parte dele)"
    )
    parser.add_argument(
        "--incoerentes",
        action="store_true",
        help="Filtrar exclusivamente decisões identificadas como incoerentes ou adulteradas"
    )
    parser.add_argument(
        "--detalhes",
        action="store_true",
        help="Exibir visualização detalhada de cada registro retornado"
    )

    args = parser.parse_args()

    caminho_log = Path(args.log).resolve()
    registros = carregar_logs(caminho_log)

    if not registros:
        print(f"Nenhum registro encontrado em {caminho_log}.")
        return

    # Aplicação de filtros
    filtrados = registros

    if args.classificacao:
        filtrados = [
            r for r in filtrados
            if str(r.get("classificacao", "")).upper() == args.classificacao.upper()
        ]

    if args.session_id:
        termo = args.session_id.lower()
        filtrados = [
            r for r in filtrados
            if termo in str(r.get("session_id", "")).lower()
        ]

    if args.incoerentes:
        filtrados = [
            r for r in filtrados
            if not r.get("validacao_coerencia", {}).get("coerente", True)
        ]

    print("\n" + "=" * 75)
    print("📋 RELATÓRIO DE AUDITORIA — CARDIOAI")
    print(f"📁 Log consultado: {caminho_log}")
    print(f"📊 Total no arquivo: {len(registros)} | Registros filtrados: {len(filtrados)}")
    print("=" * 75)

    if not filtrados:
        print("\nNenhuma decisão atendeu aos filtros especificados.")
        return

    formatar_tabela_resumo(filtrados)

    if args.detalhes:
        for r in filtrados:
            exibir_detalhes_registro(r)


if __name__ == "__main__":
    main()
