"""Contexto tipado para compartilhamento de estado entre agentes do OpenAI Agents SDK."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CardioContext:
    """Estrutura de dados compartilhada entre todos os agentes durante a execução.

    Evita estado global, garantindo que cada paciente ou sessão possua seu
    próprio escopo isolado de execução.
    """
    dados_paciente: dict[str, Any] = field(default_factory=dict)
    resultado_risco: dict[str, Any] | None = None
    protocolos_acionados: list[dict[str, Any]] | None = None
