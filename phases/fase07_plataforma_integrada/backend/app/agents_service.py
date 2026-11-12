"""Serviço de execução do pipeline multiagente real da Fase 6 via OpenAI Agents SDK.

Importa diretamente `src.agents_system` de `phases/fase06_preditivo_multiagente`
e executa os 4 agentes colaborativos (Orquestrador, Analista de Risco,
Especialista em Protocolos e Planejador de Resposta) sobre os dados completos
da última leitura de telemetria do paciente.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os

from fastapi import HTTPException, status

from app.config import (
    RECOMENDACAO_COOLDOWN_SECONDS,
    get_openai_api_key,
    get_openai_model,
    has_openai_api_key,
)
from app.schemas import LeituraArmazenada, RecomendacaoResponse
from app.store import store

from agents import Runner
from agents.exceptions import OutputGuardrailTripwireTriggered
import src.agents_system as fase06_agents


PROMPT_INICIAL_TRIAGEM = (
    "Inicie a triagem do novo paciente cardiovascular disponível no contexto. "
    "Acione o Agente Analista de Risco para calcular o score, encaminhe ao Especialista "
    "em Protocolos para verificar as diretrizes e, por fim, acione o Planejador de Resposta "
    "para sintetizar o plano operacional completo."
)


async def executar_recomendacao_multiagente(
    paciente_id: str,
    ultima_leitura: LeituraArmazenada,
) -> RecomendacaoResponse:
    """Executa o pipeline multiagente REAL da Fase 6 para a última leitura do paciente.

    Regras:
    - Sem OPENAI_API_KEY: retorna HTTP 503 com mensagem clara (nunca simula resposta).
    - Limite de 1 chamada a cada 30 segundos por paciente (HTTP 429).
    """
    if not has_openai_api_key():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Serviço indisponível: OPENAI_API_KEY não está configurada no servidor. "
                "O pipeline multiagente exige uma chave válida da OpenAI (respostas simuladas são proibidas)."
            ),
        )

    permitido, segundos_restantes = store.verificar_cooldown_recomendacao(
        paciente_id=paciente_id,
        cooldown_segundos=RECOMENDACAO_COOLDOWN_SECONDS,
    )
    if not permitido:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Limite de frequência atingido para o paciente '{paciente_id}': "
                f"permitida apenas 1 recomendação a cada {int(RECOMENDACAO_COOLDOWN_SECONDS)} segundos. "
                f"Aguarde {segundos_restantes:.1f}s."
            ),
        )

    # Garante que a chave esteja visível para o SDK da OpenAI Agents
    os.environ["OPENAI_API_KEY"] = get_openai_api_key()
    model_name = get_openai_model()

    agente_orquestrador, _, _, _ = fase06_agents.criar_sistema_agentes(model=model_name)
    cardio_context = fase06_agents.CardioContext(
        dados_paciente=dict(ultima_leitura.dados_completos)
    )

    try:
        resultado_run = await Runner.run(
            agente_orquestrador,
            PROMPT_INICIAL_TRIAGEM,
            context=cardio_context,
        )
    except OutputGuardrailTripwireTriggered as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Guardrail de integridade clínica acionado pelos agentes: {exc}",
        ) from exc
    except Exception as exc:
        store.liberar_cooldown_recomendacao(paciente_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha ao executar o pipeline multiagente na OpenAI: {exc}",
        ) from exc

    final_output = resultado_run.final_output
    if isinstance(final_output, fase06_agents.RecomendacaoFinal):
        rec = final_output
    elif isinstance(final_output, dict):
        rec = fase06_agents.RecomendacaoFinal(**final_output)
    else:
        rec = fase06_agents.RecomendacaoFinal.model_validate_json(str(final_output))

    return RecomendacaoResponse(
        paciente_id=paciente_id,
        probabilidade=float(rec.probabilidade),
        classificacao=rec.classificacao,
        protocolos_sugeridos=list(rec.protocolos_sugeridos),
        acoes_operacionais=list(rec.acoes_operacionais),
        justificativa=rec.justificativa,
        aviso=rec.aviso,
        gerado_em=datetime.now(timezone.utc).isoformat(),
    )

