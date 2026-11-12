"""Esquemas Pydantic de entrada e saída para a API FastAPI da Fase 7."""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator


class HealthResponse(BaseModel):
    """Resposta do endpoint GET /health."""

    status: str = Field(default="ok", description="Status operacional da API")
    modelo_carregado: bool = Field(..., description="Indica se o modelo joblib da Fase 6 foi carregado")
    openai_api_key: bool = Field(
        ...,
        description="True/False indicando se OPENAI_API_KEY está presente no ambiente (nunca o valor)",
    )
    openai_api_key_configurada: bool = Field(
        ...,
        description="Alias booleano indicando presença de OPENAI_API_KEY",
    )


class LoginRequest(BaseModel):
    """Payload de autenticação para POST /api/auth/login."""

    email: str = Field(..., min_length=3, max_length=254, description="E-mail do usuário")
    senha: str = Field(..., min_length=1, max_length=256, description="Senha do usuário")

    @model_validator(mode="before")
    @classmethod
    def aceitar_alias_password(cls, data: Any) -> Any:
        """Permite compatibilidade caso o cliente envie 'password' em vez de 'senha'."""
        if isinstance(data, dict) and "senha" not in data and "password" in data:
            novo = dict(data)
            novo["senha"] = novo["password"]
            return novo
        return data


class LoginResponse(BaseModel):
    """Resposta com token JWT emitido após autenticação bem-sucedida."""

    access_token: str = Field(..., description="Token JWT assinado (HS256)")
    token_type: str = Field(default="bearer", description="Tipo do token de autenticação")
    email: str = Field(..., description="E-mail do usuário autenticado")
    expires_in: int = Field(..., description="Tempo de validade do token em segundos")


class TelemetriaRequest(BaseModel):
    """Payload enviado pelo dispositivo IoT para POST /api/telemetria."""

    device_id: str = Field(..., min_length=1, max_length=100, description="Identificador do dispositivo IoT")
    paciente_id: str = Field(..., min_length=1, max_length=100, description="Identificador do paciente")
    fc_media: float = Field(
        ...,
        ge=30.0,
        le=250.0,
        description="Frequência cardíaca média em bpm (faixa fisiológica válida: 30 a 250 bpm)",
    )
    temperatura: float = Field(
        ...,
        ge=25.0,
        le=45.0,
        description="Temperatura corporal em °C (faixa válida: 25 a 45 °C)",
    )
    spo2_media: float = Field(
        ...,
        ge=50.0,
        le=100.0,
        description="Saturação periférica de oxigênio em % (faixa válida: 50 a 100 %)",
    )

    @model_validator(mode="before")
    @classmethod
    def converter_ids_para_str(cls, data: Any) -> Any:
        """Converte paciente_id ou device_id numéricos para string, se necessário."""
        if isinstance(data, dict):
            novo = dict(data)
            if "paciente_id" in novo and isinstance(novo["paciente_id"], int):
                novo["paciente_id"] = str(novo["paciente_id"])
            if "device_id" in novo and isinstance(novo["device_id"], int):
                novo["device_id"] = str(novo["device_id"])
            return novo
        return data


class ProtocoloDetalhado(BaseModel):
    """Representação detalhada de um protocolo acionado pelo motor determinístico da Fase 6."""

    id: str
    texto: str
    variavel: str
    valor_paciente: float | str
    limiar: str


class TelemetriaResponse(BaseModel):
    """Resposta do endpoint POST /api/telemetria após cálculo de risco e protocolos."""

    probabilidade: float = Field(..., ge=0.0, le=1.0, description="Probabilidade prevista pelo modelo ML")
    classificacao: Literal["BAIXO", "MODERADO", "ALTO"] = Field(..., description="Classificação de risco")
    alerta: bool = Field(..., description="Indica se há alerta clínico/operacional ativo")
    protocolos: list[str] = Field(..., description="Textos dos protocolos acionados")
    protocolos_detalhados: list[ProtocoloDetalhado] = Field(
        default_factory=list,
        description="Metadados completos dos protocolos acionados",
    )
    paciente_id: str = Field(..., description="Identificador do paciente")
    device_id: str = Field(..., description="Identificador do dispositivo IoT")
    timestamp: str = Field(..., description="Carimbo de tempo UTC ISO-8601 da leitura")


class LeituraArmazenada(BaseModel):
    """Registro completo de uma leitura de telemetria armazenada em memória."""

    device_id: str
    paciente_id: str
    fc_media: float
    temperatura: float
    spo2_media: float
    dados_completos: dict[str, float]
    probabilidade: float
    classe_prevista: int
    classificacao: Literal["BAIXO", "MODERADO", "ALTO"]
    alerta: bool
    protocolos: list[str]
    protocolos_detalhados: list[ProtocoloDetalhado]
    timestamp: str
    epoch_seconds: float


class StatusPacienteResponse(BaseModel):
    """Resposta do endpoint GET /api/pacientes/{id}/status."""

    paciente_id: str
    ultima_leitura: LeituraArmazenada
    risco: dict[str, Any]
    probabilidade: float
    classificacao: Literal["BAIXO", "MODERADO", "ALTO"]
    alerta: bool
    protocolos: list[str]
    protocolos_detalhados: list[ProtocoloDetalhado]
    idade_leitura_segundos: float = Field(
        ...,
        ge=0.0,
        description="Idade da última leitura em segundos até o momento da consulta",
    )
    idade_segundos: float = Field(
        ...,
        ge=0.0,
        description="Alias para idade da última leitura em segundos",
    )


class HistoricoPacienteResponse(BaseModel):
    """Resposta do endpoint GET /api/pacientes/{id}/historico."""

    paciente_id: str
    total_armazenado: int
    limite: int
    leituras: list[LeituraArmazenada]


class RecomendacaoResponse(BaseModel):
    """Resposta do endpoint POST /api/pacientes/{id}/recomendacao."""

    paciente_id: str
    probabilidade: float
    classificacao: Literal["BAIXO", "MODERADO", "ALTO"]
    protocolos_sugeridos: list[str]
    acoes_operacionais: list[str]
    justificativa: str
    aviso: str
    gerado_em: str


class ChatRequest(BaseModel):
    """Payload de entrada para POST /api/chat."""

    mensagem: str = Field(..., min_length=1, max_length=4000, description="Mensagem enviada pelo usuário")
    session_id: str | None = Field(
        default=None,
        description="Identificador opcional da sessão para manter histórico em memória",
    )


class ChatResponse(BaseModel):
    """Resposta do assistente cardiológico de triagem em POST /api/chat."""

    session_id: str
    resposta: str
    disclaimer: str
    modelo: str
    historico_mensagens: int

