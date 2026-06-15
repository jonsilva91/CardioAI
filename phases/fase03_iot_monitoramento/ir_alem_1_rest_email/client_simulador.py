"""
CardioIA - Fase 3 - IR ALÉM 1
Cliente REST que simula envio de sinais vitais para a API.

Como executar, com a API rodando:
    python client_simulador.py
"""
from __future__ import annotations

import random
import time
from typing import Any

import requests

API_URL = "http://127.0.0.1:8000/vitals"


def generate_sample(i: int) -> dict[str, Any]:
    """Gera leituras normais e, em alguns ciclos, leituras de alerta."""
    if i in {5, 9}:
        return {
            "patient_id": "paciente_001",
            "bpm": random.randint(126, 148),
            "temperature": round(random.uniform(38.0, 39.4), 1),
            "movement": random.choice([0, 2]),
            "oxygen": round(random.uniform(92, 97), 1),
            "source": "simulador_python_alerta",
        }

    return {
        "patient_id": "paciente_001",
        "bpm": random.randint(68, 105),
        "temperature": round(random.uniform(36.1, 37.4), 1),
        "movement": round(random.uniform(5, 40), 1),
        "oxygen": round(random.uniform(95, 99), 1),
        "source": "simulador_python_normal",
    }


def main() -> None:
    print("CardioIA - Cliente REST de sinais vitais")
    print(f"Enviando para: {API_URL}")

    for i in range(1, 13):
        payload = generate_sample(i)
        print(f"\n[{i:02d}] Enviando payload: {payload}")

        try:
            response = requests.post(API_URL, json=payload, timeout=10)
            print("Status HTTP:", response.status_code)
            print("Resposta:", response.json())
        except requests.RequestException as exc:
            print("Erro ao enviar para API:", exc)

        time.sleep(1)


if __name__ == "__main__":
    main()
