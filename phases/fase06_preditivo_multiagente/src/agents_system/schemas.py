"""Esquemas de dados Pydantic para validação de entrada e saída estruturada dos agentes."""

from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator


class DadosPaciente(BaseModel):
    """Esquema de validação dos dados de entrada do paciente clínico/operacional."""

    idade_media: float = Field(..., ge=0, le=120, description="Idade média do paciente em anos")
    carga_sistema: float = Field(..., ge=0, le=100, description="Carga operacional do sistema de saúde (0 a 100%)")
    tempo_espera: float = Field(..., ge=0, le=300, description="Tempo de espera em minutos")
    fc_media: float = Field(..., ge=30, le=250, description="Frequência cardíaca média em bpm")
    spo2_media: float = Field(..., ge=50, le=100, description="Saturação periférica de oxigênio em %")
    pa_sistolica: float = Field(..., ge=50, le=250, description="Pressão arterial sistólica em mmHg")
    temperatura: float = Field(..., ge=10, le=45, description="Temperatura em °C")
    densidade_eventos: float = Field(..., ge=0, le=50, description="Densidade de eventos críticos na unidade")
    eventos_24h: float = Field(..., ge=0, le=50, description="Número de eventos graves nas últimas 24 horas")
    disponibilidade_recursos: float = Field(..., ge=0, le=100, description="Disponibilidade de recursos (0 a 100%)")

    @model_validator(mode="before")
    @classmethod
    def normalizar_chaves_entrada(cls, data: Any) -> Any:
        """Garante a conversão de chaves com espaço (ex: 'disponibilidade recursos') para underscores."""
        if isinstance(data, dict):
            return {str(k).strip().replace(" ", "_"): v for k, v in data.items()}
        return data


class RecomendacaoFinal(BaseModel):
    """Esquema da resposta final consolidada pelo Agente Planejador de Resposta."""

    probabilidade: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probabilidade prevista de pico de risco cardiovascular, calculada exclusivamente pelo modelo ML"
    )
    classificacao: Literal["BAIXO", "MODERADO", "ALTO"] = Field(
        ...,
        description="Classificação categórica baseada nos limiares definidos"
    )
    protocolos_sugeridos: list[str] = Field(
        ...,
        description="Lista textual dos protocolos clínicos/operacionais acionados pelas regras determinísticas"
    )
    acoes_operacionais: list[str] = Field(
        ...,
        description="Ações práticas, organizacionais e clínicas imediatas recomendadas para a equipe hospitalar"
    )
    justificativa: str = Field(
        ...,
        description="Justificativa clínica detalhada explicando como o risco e os protocolos se relacionam às variáveis do paciente"
    )
    aviso: str = Field(
        default="Sistema acadêmico com dados sintéticos. Não substitui avaliação médica.",
        description="Aviso ético e regulatório obrigatório"
    )
