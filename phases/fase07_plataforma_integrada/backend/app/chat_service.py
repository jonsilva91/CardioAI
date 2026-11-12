"""Serviço de chat conversacional com LLM real (OpenAI) para triagem cardiológica.

Mantém histórico de conversação em memória por `session_id`, atua no papel de
assistente cardiológico de triagem e inclui obrigatoriamente o disclaimer fixo
"Não substitui avaliação médica.".
"""

from __future__ import annotations

import uuid
from fastapi import HTTPException, status
from openai import AsyncOpenAI

from app.config import (
    DISCLAIMER_FIXO,
    get_openai_api_key,
    get_openai_model,
    has_openai_api_key,
)
from app.schemas import ChatRequest, ChatResponse
from app.store import store

SYSTEM_PROMPT_TRIAGEM_CARDIO = f"""Você é o Assistente Cardiológico de Triagem da plataforma CardioAI.
Seu papel é auxiliar profissionais de saúde e pacientes na triagem inicial de sintomas cardiovasculares, interpretação educativa de sinais vitais (frequência cardíaca, saturação de oxigênio SpO2, temperatura e pressão arterial) e orientação sobre protocolos hospitalares de risco.

Diretrizes obrigatórias:
1. Responda sempre em português, de forma clara, objetiva, empática e tecnicamente rigorosa.
2. Identifique sinais de alerta vermelho (dor torácica opressiva, dispneia aguda, síncope, SpO2 < 92%, FC > 110 bpm ou < 50 bpm, PA sistólica < 90 mmHg) e recomende atendimento emergencial imediato quando presentes.
3. NUNCA emita diagnósticos médicos definitivos nem prescreva medicamentos ou dosagens.
4. Ao final de TODA resposta, inclua exatamente a frase de aviso ético: "{DISCLAIMER_FIXO}"
"""


async def processar_mensagem_chat(payload: ChatRequest) -> ChatResponse:
    """Envia a mensagem com o histórico da sessão para o modelo OpenAI real e retorna a resposta.

    Sem OPENAI_API_KEY: retorna HTTP 503 com mensagem clara (nunca simula resposta).
    """
    if not has_openai_api_key():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Serviço indisponível: OPENAI_API_KEY não está configurada no servidor. "
                "O assistente conversacional exige uma chave válida da OpenAI (respostas simuladas são proibidas)."
            ),
        )

    session_id = (payload.session_id or "").strip() or f"sess_{uuid.uuid4().hex[:12]}"
    model_name = get_openai_model()
    api_key = get_openai_api_key()

    historico_anterior = store.obter_historico_chat(session_id)
    mensagens_llm: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT_TRIAGEM_CARDIO},
        *historico_anterior,
        {"role": "user", "content": payload.mensagem.strip()},
    ]

    client = AsyncOpenAI(api_key=api_key)
    try:
        completion = await client.chat.completions.create(
            model=model_name,
            messages=mensagens_llm,  # type: ignore[arg-type]
            temperature=0.3,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Falha ao comunicar com a API da OpenAI: {exc}",
        ) from exc

    conteudo = (completion.choices[0].message.content or "").strip()
    if DISCLAIMER_FIXO not in conteudo:
        conteudo = f"{conteudo}\n\n{DISCLAIMER_FIXO}".strip()

    store.adicionar_mensagem_chat(session_id, "user", payload.mensagem.strip())
    total_historico = store.adicionar_mensagem_chat(session_id, "assistant", conteudo)

    return ChatResponse(
        session_id=session_id,
        resposta=conteudo,
        disclaimer=DISCLAIMER_FIXO,
        modelo=model_name,
        historico_mensagens=total_historico,
    )

