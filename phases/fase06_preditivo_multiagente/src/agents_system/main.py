"""Ponto de entrada (CLI) para execução do Sistema Multiagente CardioAI.

Suporta execução individual de pacientes a partir de arquivos JSON e modo interativo
com persistência de histórico e conversação via SQLiteSession.
"""

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# Garante suporte seguro a UTF-8 no console do Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.config import FASE06_DIR, OPENAI_MODEL, SESSIONS_DB_PATH

# Carrega variáveis de ambiente
load_dotenv(FASE06_DIR / ".env")
load_dotenv()

from agents import Runner
from agents.exceptions import OutputGuardrailTripwireTriggered
from agents.memory.sqlite_session import SQLiteSession

from src.agents_system.cardio_agents import criar_sistema_agentes
from src.agents_system.context import CardioContext
from src.agents_system.schemas import DadosPaciente, RecomendacaoFinal


def verificar_chave_api() -> str:
    """Verifica se a chave da API OpenAI está presente, alertando caso ausente."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("\n" + "=" * 70, file=sys.stderr)
        print("❌ ERRO: A variável de ambiente OPENAI_API_KEY não foi encontrada.", file=sys.stderr)
        print("Para executar o sistema multiagente, forneça uma chave válida em um arquivo .env", file=sys.stderr)
        print(f"ou defina a variável no seu ambiente. Consulte: {FASE06_DIR / '.env.example'}", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)
        sys.exit(1)
    return api_key


def carregar_dados_paciente(caminho_arquivo: Path) -> dict:
    """Carrega e valida o arquivo JSON do paciente contra o esquema Pydantic."""
    if not caminho_arquivo.exists():
        print(f"❌ ERRO: Arquivo de paciente não encontrado em '{caminho_arquivo}'.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados_brutos = json.load(f)
    except Exception as e:
        print(f"❌ ERRO: Falha ao ler JSON do paciente: {e}", file=sys.stderr)
        sys.exit(1)

    # Validação via Pydantic
    try:
        paciente_validado = DadosPaciente.model_validate(dados_brutos)
    except Exception as e:
        print(f"❌ ERRO: Dados do paciente inválidos para as faixas estipuladas:\n{e}", file=sys.stderr)
        sys.exit(1)

    return paciente_validado.model_dump()


def exibir_resultado(rec: RecomendacaoFinal) -> None:
    """Imprime o resultado formatado no padrão exigido pelo enunciado e em formato JSON."""
    print("\n" + "=" * 70)
    print(f"RISCO PREVISTO: {rec.probabilidade:.2f}")
    print(f"CLASSIFICAÇÃO: {rec.classificacao}")
    print("\nPROTOCOLOS SUGERIDOS:")
    if rec.protocolos_sugeridos:
        for p in rec.protocolos_sugeridos:
            print(f"- {p}")
    else:
        print("- Nenhum protocolo crítico acionado.")

    print("\nAÇÕES OPERACIONAIS:")
    if rec.acoes_operacionais:
        for a in rec.acoes_operacionais:
            print(f"- {a}")
    else:
        print("- Manter monitoramento de rotina.")

    print(f"\nJUSTIFICATIVA:\n{rec.justificativa}")
    print(f"\nAVISO:\n{rec.aviso}")
    print("=" * 70)

    # Saída completa em formato JSON
    print("\n📄 SAÍDA COMPLETA (JSON):")
    print(json.dumps(rec.model_dump(), indent=2, ensure_ascii=False))
    print("=" * 70)


def executar_pipeline(caminho_paciente: Path, session_id: str, model_name: str) -> tuple[RecomendacaoFinal | None, Any, CardioContext]:
    """Executa a triagem multiagente para um paciente específico."""
    paciente_dict = carregar_dados_paciente(caminho_paciente)

    print("\n" + "=" * 70)
    print("🏥 CARDIOAI - SISTEMA PREDITIVO MULTIAGENTE DE RISCO CARDÍACO")
    print("=" * 70)
    print(f"📁 Paciente: {caminho_paciente}")
    print(f"🆔 Sessão SQLite: {session_id}")
    print(f"🧠 Modelo LLM: {model_name}")
    print("=" * 70)

    # Instancia os agentes e o contexto compartilhado
    agente_orquestrador, _, _, _ = criar_sistema_agentes(model=model_name)
    cardio_context = CardioContext(dados_paciente=paciente_dict)

    # Configura a sessão persistente em SQLite
    SESSIONS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    session = SQLiteSession(session_id=session_id, db_path=str(SESSIONS_DB_PATH))

    # Prompt inicial disparado para o orquestrador
    prompt_inicial = (
        "Inicie a triagem do novo paciente cardiovascular disponível no contexto. "
        "Acione o Agente Analista de Risco para calcular o score, encaminhe ao Especialista "
        "em Protocolos para verificar as diretrizes e, por fim, acione o Planejador de Resposta "
        "para sintetizar o plano operacional completo."
    )

    try:
        resultado_run = Runner.run_sync(
            agente_orquestrador,
            prompt_inicial,
            context=cardio_context,
            session=session
        )
    except OutputGuardrailTripwireTriggered as e:
        print("\n" + "=" * 70, file=sys.stderr)
        print("🚨 FALHA CRÍTICA DE INTEGRIDADE (Output Guardrail Tripwire Disparado):", file=sys.stderr)
        print(f"A saída produzida violou as regras determinísticas de segurança clínica.\n{e}", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)
        return None, session, cardio_context
    except Exception as e:
        print(f"\n❌ Erro durante a execução dos agentes: {e}", file=sys.stderr)
        return None, session, cardio_context

    final_output = resultado_run.final_output
    if isinstance(final_output, RecomendacaoFinal):
        recomendacao = final_output
    elif isinstance(final_output, dict):
        recomendacao = RecomendacaoFinal(**final_output)
    else:
        try:
            recomendacao = RecomendacaoFinal.model_validate_json(str(final_output))
        except Exception:
            print(f"Saída em formato não estruturado: {final_output}")
            return None, session, cardio_context

    exibir_resultado(recomendacao)
    return recomendacao, session, cardio_context


def modo_interativo(session: SQLiteSession, cardio_context: CardioContext, model_name: str) -> None:
    """Loop de interação pós-triagem para responder perguntas de acompanhamento usando o histórico."""
    agente_orquestrador, _, _, _ = criar_sistema_agentes(model=model_name)

    print("\n💬 MODO INTERATIVO ATIVADO (Sessão mantida via SQLite)")
    print("Você pode fazer perguntas sobre a decisão clínica (ex: 'por que o plano de contingência foi ativado?').")
    print("Digite 'sair' ou 'exit' para encerrar.\n")

    while True:
        try:
            pergunta = input("\n👨‍⚕️ Pergunta: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando sessão interativa.")
            break

        if not pergunta:
            continue
        if pergunta.lower() in ["sair", "exit", "quit", "q"]:
            print("Encerrando sessão interativa. Até logo!")
            break

        print("\n🤖 Processando com histórico da sessão...")
        try:
            resposta = Runner.run_sync(
                agente_orquestrador,
                pergunta,
                context=cardio_context,
                session=session
            )
            print(f"\n💬 Resposta do Orquestrador:\n{resposta.final_output}\n")
        except Exception as e:
            print(f"❌ Erro ao consultar o agente: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sistema Preditivo Multiagente CardioAI (OpenAI Agents SDK)"
    )
    parser.add_argument(
        "--paciente",
        type=str,
        default=str(FASE06_DIR / "data" / "exemplos" / "novo_caso.json"),
        help="Caminho do arquivo JSON com os dados clínicos do paciente."
    )
    parser.add_argument(
        "--interativo",
        action="store_true",
        help="Habilita modo conversacional interativo após a recomendação clínica."
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="ID personalizado para a sessão SQLite (opcional)."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=OPENAI_MODEL,
        help=f"Modelo OpenAI a ser utilizado (padrão: {OPENAI_MODEL})."
    )

    args = parser.parse_args()

    # Validação obrigatória da API KEY
    verificar_chave_api()

    caminho_paciente = Path(args.paciente).resolve()
    session_id = args.session_id or f"sessao_{Path(args.paciente).stem}_{uuid.uuid4().hex[:6]}"

    recomendacao, session, cardio_context = executar_pipeline(
        caminho_paciente=caminho_paciente,
        session_id=session_id,
        model_name=args.model
    )

    if args.interativo and session is not None and cardio_context is not None:
        modo_interativo(session, cardio_context, args.model)


if __name__ == "__main__":
    main()
