"""Pipeline de execução auditada do sistema multiagente CardioAI.

Executa os casos reais com o modelo LLM e o OpenAI Agents SDK, acoplando
a camada de auditoria e validação determinística de governança:
- Rastreamento nativo de handoffs e tools via AuditRunHooks
- Validação determinística de coerência clínica (coherence_validator)
- Registro estruturado append-only em logs/decisoes.jsonl
- Teste controlado de detecção de adulteração fraudulenta de conduta
- Apresentação tabular de resultados e métricas de auditoria
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from typing import Any
import uuid

# Suporte UTF-8 no console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Caminhos base da Fase 6
FASE06_DIR = Path(__file__).resolve().parents[2]
IR_ALEM_DIR = Path(__file__).resolve().parent

if str(FASE06_DIR) not in sys.path:
    sys.path.insert(0, str(FASE06_DIR))
if str(IR_ALEM_DIR) not in sys.path:
    sys.path.insert(0, str(IR_ALEM_DIR))

from dotenv import load_dotenv

# Carrega chaves da Fase 6
load_dotenv(FASE06_DIR / ".env")
load_dotenv()

from agents import Runner
from agents.exceptions import OutputGuardrailTripwireTriggered
from agents.memory.sqlite_session import SQLiteSession

from audit_logger import AuditRunHooks, registrar_decisao
from coherence_validator import validar_coerencia
from src.agents_system.cardio_agents import criar_sistema_agentes
from src.agents_system.context import CardioContext
from src.agents_system.schemas import DadosPaciente, RecomendacaoFinal
from src.config import OPENAI_MODEL, SESSIONS_DB_PATH
from src.protocols import PROTOCOLOS

LOG_FILE = IR_ALEM_DIR / "logs" / "decisoes.jsonl"


def verificar_credenciais() -> str:
    """Verifica e retorna a chave da OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("\n❌ ERRO: OPENAI_API_KEY não encontrada no .env da Fase 6.", file=sys.stderr)
        sys.exit(1)
    return api_key


def carregar_paciente(caminho: Path) -> dict[str, Any]:
    """Lê e valida o paciente com o schema Pydantic."""
    with open(caminho, "r", encoding="utf-8") as f:
        bruto = json.load(f)
    validado = DadosPaciente.model_validate(bruto)
    return validado.model_dump()


def executar_paciente_auditado(
    caminho_paciente: Path,
    nome_caso: str,
    model_name: str = OPENAI_MODEL
) -> dict[str, Any]:
    """Executa o pipeline multiagente para um paciente e registra a auditoria."""
    paciente_dict = carregar_paciente(caminho_paciente)
    session_id = f"audit_{Path(caminho_paciente).stem}_{uuid.uuid4().hex[:6]}"

    print("\n" + "=" * 80)
    print(f"🏥 EXECUTANDO CASO CLÍNICO: {nome_caso}")
    print(f"📁 Arquivo: {caminho_paciente.name} | Sessão: {session_id}")
    print("=" * 80)

    agente_orquestrador, _, _, _ = criar_sistema_agentes(model=model_name)
    cardio_context = CardioContext(dados_paciente=paciente_dict)

    SESSIONS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    session = SQLiteSession(session_id=session_id, db_path=str(SESSIONS_DB_PATH))

    audit_hooks = AuditRunHooks()

    prompt_inicial = (
        "Inicie a triagem do novo paciente cardiovascular disponível no contexto. "
        "Acione o Agente Analista de Risco para calcular o score, encaminhe ao Especialista "
        "em Protocolos para verificar as diretrizes e, por fim, acione o Planejador de Resposta "
        "para sintetizar o plano operacional completo."
    )

    guardrail_status = "aprovado"
    recomendacao: RecomendacaoFinal | None = None

    try:
        resultado_run = Runner.run_sync(
            agente_orquestrador,
            prompt_inicial,
            context=cardio_context,
            session=session,
            hooks=audit_hooks
        )

        final_out = resultado_run.final_output
        if isinstance(final_out, RecomendacaoFinal):
            recomendacao = final_out
        elif isinstance(final_out, dict):
            recomendacao = RecomendacaoFinal(**final_out)
        else:
            recomendacao = RecomendacaoFinal.model_validate_json(str(final_out))

    except OutputGuardrailTripwireTriggered as e:
        print(f"\n🚨 TRIPWIRE DO GUARDRAIL DISPARADO: {e}")
        guardrail_status = "bloqueado"
    except Exception as e:
        print(f"\n❌ ERRO NA EXECUÇÃO: {e}")
        guardrail_status = "bloqueado"

    # Coleta de métricas e validação de coerência
    if recomendacao is not None:
        prob = recomendacao.probabilidade
        classe = recomendacao.classificacao
        protocolos = recomendacao.protocolos_sugeridos
        acoes = recomendacao.acoes_operacionais
        just = recomendacao.justificativa
        aviso = recomendacao.aviso
    else:
        prob = None
        classe = None
        protocolos = []
        acoes = []
        just = "Execução bloqueada pelo guardrail de integridade."
        aviso = ""

    validacao = validar_coerencia(
        dados=paciente_dict,
        resultado={
            "probabilidade": prob,
            "classificacao": classe,
            "protocolos_sugeridos": protocolos
        }
    )

    print(f"📊 Probabilidade: {prob} | Classificação: {classe}")
    print(f"🛡️ Guardrail: {guardrail_status.upper()} | Coerência: {'COERENTE ✅' if validacao['coerente'] else 'INCOERENTE ❌'}")
    print(f"🔄 Handoffs ({len(audit_hooks.handoffs)}): {' ➔ '.join([h['para'] for h in audit_hooks.handoffs])}")
    print(f"🔧 Tools executadas ({len(audit_hooks.tools_chamadas)}): {[t['tool'] for t in audit_hooks.tools_chamadas]}")

    registro = registrar_decisao(
        session_id=session_id,
        dados_paciente=paciente_dict,
        probabilidade=prob,
        classificacao=classe,
        protocolos_sugeridos=protocolos,
        validacao_coerencia=validacao,
        guardrail_status=guardrail_status,
        hooks=audit_hooks,
        modelo_llm=model_name,
        caminho_log=LOG_FILE,
        acoes_operacionais=acoes,
        justificativa=just,
        aviso=aviso,
        teste_adulteracao=False
    )

    return {
        "caso": nome_caso,
        "arquivo": caminho_paciente.name,
        "probabilidade": prob,
        "classificacao": classe,
        "protocolos": protocolos,
        "coerente": validacao["coerente"],
        "inconsistencias": validacao["inconsistencias"],
        "guardrail": guardrail_status,
        "handoffs_count": len(audit_hooks.handoffs),
        "tools_count": len(audit_hooks.tools_chamadas),
        "registro_id": registro["id_decisao"],
        "recomendacao_obj": recomendacao,
        "paciente_dict": paciente_dict,
        "hooks": audit_hooks
    }


def executar_teste_adulteracao(resultado_base: dict[str, Any]) -> dict[str, Any]:
    """Executa o teste auditado de adulteração fraudulenta de decisão clínica.

    Injeta propositalmente o protocolo de SpO2 ('Se SPO2 < 88% → iniciar suporte respiratório imediato')
    na decisão do novo_caso (cuja SpO2 real é 94%, não atingindo o critério).
    Demonstra a eficácia da auditoria em reprovar a conduta adulterada.
    """
    print("\n" + "=" * 80)
    print("🧪 EXECUTANDO TESTE CONTROLADO DE ADULTERAÇÃO (GOVERNANÇA)")
    print("Cenário: Injeção forçada de conduta indevida (Protocolo SpO2) no caso de Alto Risco")
    print("=" * 80)

    paciente_dict = resultado_base["paciente_dict"]
    recomendacao_original = resultado_base["recomendacao_obj"]

    # Cria uma decisão adulterada
    protocolo_spo2_injetado = PROTOCOLOS[0]  # "Se SPO2 < 88% → iniciar suporte respiratório imediato"
    protocolos_adulterados = list(recomendacao_original.protocolos_sugeridos)
    if protocolo_spo2_injetado not in protocolos_adulterados:
        protocolos_adulterados.append(protocolo_spo2_injetado)

    resultado_fraudulento = {
        "probabilidade": recomendacao_original.probabilidade,
        "classificacao": recomendacao_original.classificacao,
        "protocolos_sugeridos": protocolos_adulterados
    }

    # Validação determinística da decisão adulterada
    validacao_adulterada = validar_coerencia(paciente_dict, resultado_fraudulento)

    print(f"⚠️ SpO2 real do paciente: {paciente_dict.get('spo2_media')}% (Normal >= 88%)")
    print(f"🚨 Protocolo fraudulento inserido: '{protocolo_spo2_injetado}'")
    print(f"⚖️ Resultado da Auditoria: {'APROVADO ❌ (FALHA DE GOVERNANÇA)' if validacao_adulterada['coerente'] else 'REPROVADO COM SUCESSO ✅'}")

    for inc in validacao_adulterada["inconsistencias"]:
        print(f"   • Detecção: {inc}")

    session_id_adulteracao = f"audit_tamper_test_{uuid.uuid4().hex[:6]}"

    # Registra no log com tag clara de teste de adulteração
    registro = registrar_decisao(
        session_id=session_id_adulteracao,
        dados_paciente=paciente_dict,
        probabilidade=resultado_fraudulento["probabilidade"],
        classificacao=resultado_fraudulento["classificacao"],
        protocolos_sugeridos=resultado_fraudulento["protocolos_sugeridos"],
        validacao_coerencia=validacao_adulterada,
        guardrail_status="reprovado_por_coerencia",
        hooks=resultado_base["hooks"],
        modelo_llm=OPENAI_MODEL,
        caminho_log=LOG_FILE,
        acoes_operacionais=recomendacao_original.acoes_operacionais,
        justificativa="[TESTE DE ADULTERAÇÃO CONTROLADO] Decisão simulada com injeção manual de protocolo de oxigenoterapia.",
        aviso=recomendacao_original.aviso,
        teste_adulteracao=True
    )

    return {
        "caso": "Teste Adulteração (novo_caso)",
        "arquivo": "novo_caso.json",
        "probabilidade": resultado_fraudulento["probabilidade"],
        "classificacao": resultado_fraudulento["classificacao"],
        "protocolos": resultado_fraudulento["protocolos_sugeridos"],
        "coerente": validacao_adulterada["coerente"],
        "inconsistencias": validacao_adulterada["inconsistencias"],
        "guardrail": "reprovado",
        "handoffs_count": len(resultado_base["hooks"].handoffs),
        "tools_count": len(resultado_base["hooks"].tools_chamadas),
        "registro_id": registro["id_decisao"],
        "teste_adulteracao": True
    }


def imprimir_tabela_resumo(resultados: list[dict[str, Any]]) -> None:
    """Gera tabela consolidada de auditoria no terminal."""
    print("\n" + "=" * 120)
    print("📊 RESUMO CONSOLIDADO DA AUDITORIA MULTIAGENTE — CARDIOAI")
    print("=" * 120)
    print(f"{'CASO':<28} | {'PROB':<5} | {'CLASSE':<8} | {'PROTOCOLOS':<10} | {'COERÊNCIA':<12} | {'GUARDRAIL':<10} | {'HANDOFFS':<8} | {'TOOLS':<5}")
    print("-" * 120)

    for r in resultados:
        caso = r["caso"]
        prob = f"{r['probabilidade']:.2f}" if r["probabilidade"] is not None else "N/A"
        classe = str(r["classificacao"])
        n_prot = f"{len(r['protocolos'])} regras"
        coerente = "COERENTE ✅" if r["coerente"] else "REPROVADO ❌"
        guard = r["guardrail"].upper()
        handoffs = f"{r['handoffs_count']} etapas"
        tools = str(r["tools_count"])

        print(f"{caso:<28} | {prob:<5} | {classe:<8} | {n_prot:<10} | {coerente:<12} | {guard:<10} | {handoffs:<8} | {tools:<5}")

    print("=" * 120)
    print(f"📁 Log append-only gravado em: {LOG_FILE}")
    print("=" * 120 + "\n")


def main() -> None:
    verificar_credenciais()

    # Limpa log anterior se necessário ou mantém append-only
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    casos = [
        (FASE06_DIR / "data" / "exemplos" / "novo_caso.json", "1. Novo Caso (Alto Risco)"),
        (FASE06_DIR / "data" / "exemplos" / "caso_baixo_risco.json", "2. Caso Baixo Risco"),
        (FASE06_DIR / "data" / "exemplos" / "caso_moderado_risco.json", "3. Caso Moderado Risco")
    ]

    resultados: list[dict[str, Any]] = []

    # 1. Execução dos 3 casos reais com LLM
    for caminho, nome in casos:
        res = executar_paciente_auditado(caminho, nome)
        resultados.append(res)

    # 2. Execução do caso de teste de adulteração
    res_novo_caso = resultados[0]
    res_adulterado = executar_teste_adulteracao(res_novo_caso)
    resultados.append(res_adulterado)

    # 3. Impressão da tabela resumo
    imprimir_tabela_resumo(resultados)


if __name__ == "__main__":
    main()
