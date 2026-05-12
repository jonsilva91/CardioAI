"""
CardioIA - Fase 3 - IR ALÉM 1
Motor de risco para sinais vitais recebidos por API REST.

A lógica é propositalmente simples e explicável para fins acadêmicos:
- Taquicardia: BPM acima de 120
- Febre: temperatura acima ou igual a 38 °C
- Ausência de movimento: movimento zerado por período informado pelo cliente
- Crítico: BPM muito elevado, febre alta ou combinação de múltiplos fatores
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

RiskLevel = Literal["NORMAL", "ALERTA", "CRITICO"]


@dataclass
class RiskResult:
    risk_level: RiskLevel
    alert: bool
    reasons: list[str]
    score: int

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_risk(
    bpm: int,
    temperature: float,
    movement: float,
    oxygen: float | None = None,
) -> RiskResult:
    """Avalia risco cardiovascular básico com regras transparentes."""
    reasons: list[str] = []
    score = 0

    if bpm > 140:
        reasons.append("taquicardia crítica: BPM acima de 140")
        score += 3
    elif bpm > 120:
        reasons.append("taquicardia: BPM acima de 120")
        score += 2
    elif bpm < 45:
        reasons.append("bradicardia: BPM abaixo de 45")
        score += 2

    if temperature >= 39.0:
        reasons.append("febre alta: temperatura acima ou igual a 39 °C")
        score += 3
    elif temperature >= 38.0:
        reasons.append("febre: temperatura acima ou igual a 38 °C")
        score += 2

    if movement <= 0:
        reasons.append("ausência de movimento detectada")
        score += 1

    if oxygen is not None:
        if oxygen < 90:
            reasons.append("saturação crítica: SpO2 abaixo de 90%")
            score += 3
        elif oxygen < 94:
            reasons.append("saturação baixa: SpO2 abaixo de 94%")
            score += 2

    if score >= 4:
        risk_level: RiskLevel = "CRITICO"
    elif score >= 2:
        risk_level = "ALERTA"
    else:
        risk_level = "NORMAL"

    return RiskResult(
        risk_level=risk_level,
        alert=risk_level != "NORMAL",
        reasons=reasons if reasons else ["sinais vitais dentro dos limites configurados"],
        score=score,
    )
