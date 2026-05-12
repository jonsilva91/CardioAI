"""
CardioIA - Fase 3 - IR ALÉM 1
Simulação de envio automatizado de e-mail.

Por padrão, este módulo NÃO envia e-mail real. Ele gera um arquivo .eml e registra
um log local, simulando a automação RPA/e-mail exigida no enunciado.
"""
from __future__ import annotations

import csv
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
OUTBOX_DIR = BASE_DIR / "sent_emails"
LOG_FILE = BASE_DIR / "alerts_log.csv"


def _ensure_storage() -> None:
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "patient_id",
                "risk_level",
                "bpm",
                "temperature",
                "movement",
                "oxygen",
                "reasons",
                "eml_file",
            ])


def simulate_email_alert(vitals: dict[str, Any], risk: dict[str, Any]) -> dict[str, str]:
    """Gera um .eml local simulando o disparo automático do alerta por e-mail."""
    _ensure_storage()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    patient_id = str(vitals.get("patient_id", "paciente_desconhecido"))
    risk_level = str(risk.get("risk_level", "ALERTA"))

    subject = f"[CardioIA] Alerta {risk_level} - {patient_id}"

    body = f"""Alerta automatizado do CardioIA - Fase 3\n\nHorário: {now}\nPaciente: {patient_id}\nNível de risco: {risk_level}\nScore: {risk.get('score')}\n\nSinais recebidos:\n- BPM: {vitals.get('bpm')}\n- Temperatura: {vitals.get('temperature')} °C\n- Movimento: {vitals.get('movement')}\n- SpO2: {vitals.get('oxygen')}\n\nMotivos do alerta:\n{chr(10).join('- ' + item for item in risk.get('reasons', []))}\n\nObservação: este é um disparo simulado para fins acadêmicos.\n"""

    msg = EmailMessage()
    msg["From"] = "cardioia-alertas@simulado.local"
    msg["To"] = "equipe-medica@simulado.local"
    msg["Subject"] = subject
    msg.set_content(body)

    filename = f"{safe_now}_{patient_id}_{risk_level}.eml"
    eml_path = OUTBOX_DIR / filename
    eml_path.write_text(msg.as_string(), encoding="utf-8")

    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            now,
            patient_id,
            risk_level,
            vitals.get("bpm"),
            vitals.get("temperature"),
            vitals.get("movement"),
            vitals.get("oxygen"),
            " | ".join(risk.get("reasons", [])),
            str(eml_path),
        ])

    return {
        "status": "simulated_email_created",
        "file": str(eml_path),
        "log": str(LOG_FILE),
        "subject": subject,
    }
