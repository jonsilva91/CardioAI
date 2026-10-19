"""Módulo de auditoria e governança para decisões do sistema multiagente CardioAI.

Registra todas as decisões clínicas e operacionais em log estruturado (JSONL),
capturando telemetria nativa do OpenAI Agents SDK via RunHooks (handoffs e tools),
metadados do modelo de Machine Learning treinado, integridade criptográfica (SHA-256)
e resultado da validação determinística de coerência.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any
import uuid

# Garante resolução dos módulos da Fase 6 sem duplicação de código
FASE06_DIR = Path(__file__).resolve().parents[2]
if str(FASE06_DIR) not in sys.path:
    sys.path.insert(0, str(FASE06_DIR))

from agents import RunHooks
from src.config import OPENAI_MODEL
from src.predictor import carregar_modelo_preditivo

# Caminho padrão para o arquivo de log de decisões
DEFAULT_LOG_PATH = Path(__file__).resolve().parent / "logs" / "decisoes.jsonl"


class AuditRunHooks(RunHooks):
    """Captura telemetria nativa da orquestração de agentes via callbacks do SDK.

    Registra a sequência real de handoffs e todas as tools executadas sem necessidade
    de parsing frágil de strings ou captura manual de stdout.
    """

    def __init__(self) -> None:
        super().__init__()
        self.handoffs: list[dict[str, Any]] = []
        self.tools_chamadas: list[dict[str, Any]] = []
        self.agentes_percorridos: list[str] = []

    async def on_agent_start(self, context: Any, agent: Any) -> None:
        nome_agente = getattr(agent, "name", str(agent))
        if nome_agente not in self.agentes_percorridos:
            self.agentes_percorridos.append(nome_agente)

    async def on_agent_end(self, context: Any, agent: Any, output: Any) -> None:
        pass

    async def on_handoff(self, context: Any, from_agent: Any, to_agent: Any) -> None:
        origem = getattr(from_agent, "name", str(from_agent))
        destino = getattr(to_agent, "name", str(to_agent))
        self.handoffs.append({
            "de": origem,
            "para": destino,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        if destino not in self.agentes_percorridos:
            self.agentes_percorridos.append(destino)

    async def on_tool_start(self, context: Any, agent: Any, tool: Any) -> None:
        nome_agente = getattr(agent, "name", str(agent))
        nome_tool = getattr(tool, "name", str(tool))
        self.tools_chamadas.append({
            "agente": nome_agente,
            "tool": nome_tool,
            "timestamp_inicio": datetime.now(timezone.utc).isoformat(),
            "status": "executando"
        })

    async def on_tool_end(self, context: Any, agent: Any, tool: Any, result: Any) -> None:
        nome_tool = getattr(tool, "name", str(tool))
        # Atualiza a última tool correspondente para concluída
        for item in reversed(self.tools_chamadas):
            if item.get("tool") == nome_tool and item.get("status") == "executando":
                item["status"] = "concluido"
                item["timestamp_fim"] = datetime.now(timezone.utc).isoformat()
                # Serialização segura do resultado
                if hasattr(result, "model_dump"):
                    item["resultado"] = result.model_dump()
                elif isinstance(result, (dict, list, str, int, float, bool)) or result is None:
                    item["resultado"] = result
                else:
                    item["resultado"] = str(result)
                break


def calcular_hash_sha256(dados: dict[str, Any]) -> str:
    """Calcula hash criptográfico SHA-256 dos dados brutos com chaves ordenadas."""
    dados_canonicos = json.dumps(dados, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(dados_canonicos.encode("utf-8")).hexdigest()


def obter_metadados_modelo() -> dict[str, Any]:
    """Extrai versão e métricas de desempenho diretamente do artefato .joblib."""
    try:
        artefato = carregar_modelo_preditivo()
        metricas = artefato.get("metrics", {})
        return {
            "nome": artefato.get("model_name", "RandomForestClassifier"),
            "versao_sklearn": artefato.get("sklearn_version", "1.9.0"),
            "data_treinamento": artefato.get("trained_at", ""),
            "features": artefato.get("features", []),
            "metricas": {
                "accuracy": metricas.get("accuracy"),
                "f1_score_classe_1": metricas.get("f1_class_1"),
                "recall_classe_1": metricas.get("recall_class_1"),
                "precision_classe_1": metricas.get("precision_class_1"),
                "cv_accuracy_mean": metricas.get("cv_accuracy_mean"),
                "cv_f1_mean": metricas.get("cv_f1_mean"),
            }
        }
    except Exception as e:
        return {
            "nome": "RandomForestClassifier",
            "erro_leitura": str(e)
        }


def registrar_decisao(
    session_id: str,
    dados_paciente: dict[str, Any],
    probabilidade: float | None,
    classificacao: str | None,
    protocolos_sugeridos: list[str],
    validacao_coerencia: dict[str, Any],
    guardrail_status: str,
    hooks: AuditRunHooks | None = None,
    modelo_llm: str = OPENAI_MODEL,
    caminho_log: Path = DEFAULT_LOG_PATH,
    acoes_operacionais: list[str] | None = None,
    justificativa: str | None = None,
    aviso: str | None = None,
    teste_adulteracao: bool = False,
    decision_id: str | None = None
) -> dict[str, Any]:
    """Registra uma decisão clínica em formato JSON Lines para fins de auditoria e governança.

    Args:
        session_id: Identificador único da sessão clínica.
        dados_paciente: Dicionário contendo as 10 variáveis do paciente.
        probabilidade: Probabilidade calculada pelo modelo preditivo.
        classificacao: Classificação de risco ('BAIXO', 'MODERADO', 'ALTO').
        protocolos_sugeridos: Lista de protocolos recomendados pelo sistema.
        validacao_coerencia: Dicionário retornado pela função validar_coerencia.
        guardrail_status: 'aprovado' ou 'bloqueado'.
        hooks: Instância de AuditRunHooks contendo handoffs e tools rastreadas.
        modelo_llm: Nome do modelo de linguagem utilizado.
        caminho_log: Caminho para o arquivo de log .jsonl.
        acoes_operacionais: Lista opcional de ações operacionais.
        justificativa: Justificativa clínica/operacional gerada pelo agente.
        aviso: Aviso regulatório sobre ausência de diagnóstico.
        teste_adulteracao: Indica se o registro é um teste controlado de adulteração.
        decision_id: UUID4 opcional (gerado automaticamente se ausente).

    Returns:
        Dicionário com o registro completo persistido.
    """
    id_decisao = decision_id or str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    hash_entrada = calcular_hash_sha256(dados_paciente)
    metadados_modelo = obter_metadados_modelo()

    handoffs = hooks.handoffs if hooks else []
    tools_chamadas = hooks.tools_chamadas if hooks else []
    agentes_percorridos = hooks.agentes_percorridos if hooks else []

    registro = {
        "id_decisao": id_decisao,
        "timestamp": timestamp,
        "session_id": session_id,
        "hash_dados_entrada": hash_entrada,
        "dados_paciente": dados_paciente,
        "modelo_preditivo": metadados_modelo,
        "modelo_llm": modelo_llm,
        "probabilidade": probabilidade,
        "classificacao": classificacao,
        "protocolos_sugeridos": protocolos_sugeridos,
        "sequencia_handoffs": handoffs,
        "agentes_percorridos": agentes_percorridos,
        "tools_chamadas": tools_chamadas,
        "validacao_coerencia": validacao_coerencia,
        "guardrail_status": guardrail_status,
        "acoes_operacionais": acoes_operacionais or [],
        "justificativa": justificativa or "",
        "aviso": aviso or "",
        "teste_adulteracao": teste_adulteracao
    }

    caminho_log = Path(caminho_log)
    caminho_log.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    return registro
