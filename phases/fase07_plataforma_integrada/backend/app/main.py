"""Aplicação principal FastAPI da Fase 7 — Plataforma Integrada CardioAI."""

from __future__ import annotations

import time
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from app.agents_service import executar_recomendacao_multiagente
from app.auth import (
    criar_token_jwt,
    exigir_device_token,
    exigir_jwt,
    verificar_credenciais_demo,
)
from app.chat_service import processar_mensagem_chat
from app.config import get_allowed_origins, has_openai_api_key
from app.risk_service import processar_telemetria, verificar_modelo_carregado
from app.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    HistoricoPacienteResponse,
    LoginRequest,
    LoginResponse,
    RecomendacaoResponse,
    StatusPacienteResponse,
    TelemetriaRequest,
    TelemetriaResponse,
)
from app.store import store


def criar_app() -> FastAPI:
    """Cria e configura a instância FastAPI com middlewares e rotas."""
    application = FastAPI(
        title="CardioAI - Plataforma Integrada (Fase 7)",
        description=(
            "Backend unificado de telemetria IoT cardiovascular, predição de risco "
            "com Machine Learning, protocolos clínicos determinísticos, sistema "
            "multiagente (OpenAI Agents SDK) e assistente conversacional de triagem."
        ),
        version="1.0.0",
    )

    origens_permitidas = get_allowed_origins()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origens_permitidas,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.get("/health", response_model=HealthResponse, tags=["Monitoramento"])
    def health_check() -> HealthResponse:
        """Retorna status da API, carregamento do modelo ML e presença da OPENAI_API_KEY (booleano)."""
        modelo_ok = verificar_modelo_carregado()
        tem_chave = has_openai_api_key()
        return HealthResponse(
            status="ok" if modelo_ok else "degraded",
            modelo_carregado=modelo_ok,
            openai_api_key=tem_chave,
            openai_api_key_configurada=tem_chave,
        )

    @application.post("/api/auth/login", response_model=LoginResponse, tags=["Autenticação"])
    def login(payload: LoginRequest) -> LoginResponse:
        """Autentica o usuário de demonstração e emite um token JWT assinado."""
        if not verificar_credenciais_demo(payload.email, payload.senha):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas. Verifique e-mail e senha.",
            )
        token, expires_in = criar_token_jwt(payload.email.strip())
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            email=payload.email.strip(),
            expires_in=expires_in,
        )

    @application.post("/api/telemetria", response_model=TelemetriaResponse, tags=["IoT & Telemetria"])
    def receber_telemetria(
        payload: TelemetriaRequest,
        _device_token: str = Depends(exigir_device_token),
    ) -> TelemetriaResponse:
        """Recebe leituras vitais do dispositivo IoT, calcula risco + protocolos da Fase 6 e guarda em memória."""
        leitura = processar_telemetria(payload)
        store.adicionar_leitura(leitura)
        return TelemetriaResponse(
            probabilidade=leitura.probabilidade,
            classificacao=leitura.classificacao,
            alerta=leitura.alerta,
            protocolos=leitura.protocolos,
            protocolos_detalhados=leitura.protocolos_detalhados,
            paciente_id=leitura.paciente_id,
            device_id=leitura.device_id,
            timestamp=leitura.timestamp,
        )

    @application.get(
        "/api/pacientes/{paciente_id}/status",
        response_model=StatusPacienteResponse,
        tags=["Pacientes"],
    )
    def obter_status_paciente(
        paciente_id: str,
        _jwt_payload: dict[str, Any] = Depends(exigir_jwt),
    ) -> StatusPacienteResponse:
        """Retorna a última leitura do paciente, risco, protocolos e idade da leitura em segundos."""
        ultima = store.obter_ultima_leitura(paciente_id)
        if ultima is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nenhuma leitura de telemetria encontrada para o paciente '{paciente_id}'.",
            )

        idade_seg = round(max(0.0, time.time() - ultima.epoch_seconds), 2)
        risco_dict = {
            "probabilidade": ultima.probabilidade,
            "classe_prevista": ultima.classe_prevista,
            "classificacao": ultima.classificacao,
            "alerta": ultima.alerta,
        }
        return StatusPacienteResponse(
            paciente_id=paciente_id,
            ultima_leitura=ultima,
            risco=risco_dict,
            probabilidade=ultima.probabilidade,
            classificacao=ultima.classificacao,
            alerta=ultima.alerta,
            protocolos=ultima.protocolos,
            protocolos_detalhados=ultima.protocolos_detalhados,
            idade_leitura_segundos=idade_seg,
            idade_segundos=idade_seg,
        )

    @application.get(
        "/api/pacientes/{paciente_id}/historico",
        response_model=HistoricoPacienteResponse,
        tags=["Pacientes"],
    )
    def obter_historico_paciente(
        paciente_id: str,
        limite: int = Query(default=50, ge=1, le=200, description="Quantidade máxima de leituras retornadas"),
        _jwt_payload: dict[str, Any] = Depends(exigir_jwt),
    ) -> HistoricoPacienteResponse:
        """Retorna o histórico recente de leituras do paciente (até 200 leituras em memória)."""
        leituras, total = store.obter_historico(paciente_id, limite=limite)
        return HistoricoPacienteResponse(
            paciente_id=paciente_id,
            total_armazenado=total,
            limite=limite,
            leituras=leituras,
        )

    @application.post(
        "/api/pacientes/{paciente_id}/recomendacao",
        response_model=RecomendacaoResponse,
        tags=["Agentes Clínicos"],
    )
    async def gerar_recomendacao_paciente(
        paciente_id: str,
        _jwt_payload: dict[str, Any] = Depends(exigir_jwt),
    ) -> RecomendacaoResponse:
        """Executa o pipeline multiagente REAL da Fase 6 para a última leitura do paciente (máx. 1x a cada 30s)."""
        ultima = store.obter_ultima_leitura(paciente_id)
        if ultima is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Nenhuma leitura de telemetria encontrada para o paciente '{paciente_id}'. "
                    "Envie dados em POST /api/telemetria antes de solicitar recomendação."
                ),
            )
        return await executar_recomendacao_multiagente(
            paciente_id=paciente_id,
            ultima_leitura=ultima,
        )

    @application.post("/api/chat", response_model=ChatResponse, tags=["Assistente de Triagem"])
    async def conversar_assistente(
        payload: ChatRequest,
        _jwt_payload: dict[str, Any] = Depends(exigir_jwt),
    ) -> ChatResponse:
        """Conversa com o assistente cardiológico de triagem (OpenAI real) mantendo histórico por session_id."""
        return await processar_mensagem_chat(payload)

    return application


app = criar_app()

