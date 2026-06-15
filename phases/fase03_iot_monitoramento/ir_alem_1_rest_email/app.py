"""
CardioIA - Fase 3 - IR ALÉM 1
API REST para recebimento de sinais vitais e automação de alerta por e-mail.

Como executar:
    uvicorn app:app --reload --port 8000

Endpoints principais:
    GET  /health
    POST /vitals
    GET  /vitals/latest
    GET  /alerts
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from email_alert import simulate_email_alert
from risk_engine import evaluate_risk

app = FastAPI(
    title="CardioIA Fase 3 - REST Alert API",
    description="API acadêmica para monitoramento de sinais vitais, risco e alerta automatizado.",
    version="1.0.0",
)

VITALS_STORE: list[dict] = []
ALERTS_STORE: list[dict] = []


class VitalSigns(BaseModel):
    patient_id: str = Field(default="paciente_001", examples=["paciente_001"])
    bpm: int = Field(ge=0, le=250, examples=[92])
    temperature: float = Field(ge=25, le=45, examples=[36.7])
    movement: float = Field(ge=0, le=100, examples=[12.5])
    oxygen: Optional[float] = Field(default=None, ge=0, le=100, examples=[97.0])
    source: str = Field(default="simulador_python", examples=["esp32_wokwi"])


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "CardioIA REST Alert API",
        "stored_vitals": len(VITALS_STORE),
        "stored_alerts": len(ALERTS_STORE),
    }


@app.post("/vitals")
def receive_vitals(vitals: VitalSigns) -> dict:
    received_at = datetime.now().isoformat(timespec="seconds")
    vitals_dict = vitals.dict()
    vitals_dict["received_at"] = received_at

    risk = evaluate_risk(
        bpm=vitals.bpm,
        temperature=vitals.temperature,
        movement=vitals.movement,
        oxygen=vitals.oxygen,
    ).to_dict()

    record = {
        "received_at": received_at,
        "vitals": vitals_dict,
        "risk": risk,
    }
    VITALS_STORE.append(record)

    email_result = None
    if risk["alert"]:
        email_result = simulate_email_alert(vitals=vitals_dict, risk=risk)
        alert_record = {
            "received_at": received_at,
            "patient_id": vitals.patient_id,
            "risk": risk,
            "email": email_result,
            "vitals": vitals_dict,
        }
        ALERTS_STORE.append(alert_record)

    return {
        "status": "received",
        "patient_id": vitals.patient_id,
        "risk": risk,
        "email_automation": email_result,
    }


@app.get("/vitals/latest")
def latest_vitals(limit: int = 10) -> dict:
    return {
        "count": min(limit, len(VITALS_STORE)),
        "items": VITALS_STORE[-limit:],
    }


@app.get("/alerts")
def alerts(limit: int = 20) -> dict:
    return {
        "count": min(limit, len(ALERTS_STORE)),
        "items": ALERTS_STORE[-limit:],
    }
