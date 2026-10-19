"""Base de protocolos clínicos e motor determinístico de regras operacionais.

Define os protocolos médicos oficiais fornecidos no enunciado da FIAP Fase 6
e implementa a verificação exata e determinística das condições do paciente e do risco sistêmico.
"""

from typing import Any
from src.predictor import normalizar_dados_paciente

# Lista oficial literal dos 10 protocolos definidos no enunciado da atividade
PROTOCOLOS: list[str] = [
    "Se SPO2 < 88% → iniciar suporte respiratório imediato",
    "Se carga do sistema > 85% → abrir unidades temporárias",
    "Se FC > 120 → iniciar monitoramento intensivo",
    "Se eventos_24h > 5 → ativar equipe de resposta rápida",
    "Se disponibilidade_recursos < 30% → redistribuir insumos",
    "Se tempo_espera > 90 min → priorizar triagem emergencial",
    "Se temperatura > 38°C média → iniciar protocolo infeccioso",
    "Se densidade_eventos > 6 → ativar plano de contingência",
    "Se PA sistólica < 90 → iniciar protocolo de choque",
    "Se risco sistêmico alto → ativar estado de emergência"
]


def consultar_protocolos(dados: dict[str, Any], classificacao: str) -> list[dict[str, Any]]:
    """Avalia deterministicamente as regras clínicas e operacionais para o paciente.

    Args:
        dados: Dicionário com os dados clínicos e operacionais do paciente.
        classificacao: Classificação de risco inferida pelo modelo ('BAIXO', 'MODERADO', 'ALTO').

    Returns:
        Lista de dicionários, cada um contendo id, texto literal, variável, valor do paciente e limiar.
    """
    dados_norm = normalizar_dados_paciente(dados)
    protocolos_acionados: list[dict[str, Any]] = []

    # 1. SpO2 < 88%
    if "spo2_media" in dados_norm and float(dados_norm["spo2_media"]) < 88.0:
        protocolos_acionados.append({
            "id": "PROT-01",
            "texto": PROTOCOLOS[0],
            "variavel": "spo2_media",
            "valor_paciente": float(dados_norm["spo2_media"]),
            "limiar": "< 88%"
        })

    # 2. Carga do sistema > 85%
    if "carga_sistema" in dados_norm and float(dados_norm["carga_sistema"]) > 85.0:
        protocolos_acionados.append({
            "id": "PROT-02",
            "texto": PROTOCOLOS[1],
            "variavel": "carga_sistema",
            "valor_paciente": float(dados_norm["carga_sistema"]),
            "limiar": "> 85%"
        })

    # 3. FC > 120 bpm
    if "fc_media" in dados_norm and float(dados_norm["fc_media"]) > 120.0:
        protocolos_acionados.append({
            "id": "PROT-03",
            "texto": PROTOCOLOS[2],
            "variavel": "fc_media",
            "valor_paciente": float(dados_norm["fc_media"]),
            "limiar": "> 120 bpm"
        })

    # 4. Eventos 24h > 5
    if "eventos_24h" in dados_norm and float(dados_norm["eventos_24h"]) > 5.0:
        protocolos_acionados.append({
            "id": "PROT-04",
            "texto": PROTOCOLOS[3],
            "variavel": "eventos_24h",
            "valor_paciente": float(dados_norm["eventos_24h"]),
            "limiar": "> 5"
        })

    # 5. Disponibilidade de recursos < 30%
    if "disponibilidade_recursos" in dados_norm and float(dados_norm["disponibilidade_recursos"]) < 30.0:
        protocolos_acionados.append({
            "id": "PROT-05",
            "texto": PROTOCOLOS[4],
            "variavel": "disponibilidade_recursos",
            "valor_paciente": float(dados_norm["disponibilidade_recursos"]),
            "limiar": "< 30%"
        })

    # 6. Tempo de espera > 90 min
    if "tempo_espera" in dados_norm and float(dados_norm["tempo_espera"]) > 90.0:
        protocolos_acionados.append({
            "id": "PROT-06",
            "texto": PROTOCOLOS[5],
            "variavel": "tempo_espera",
            "valor_paciente": float(dados_norm["tempo_espera"]),
            "limiar": "> 90 min"
        })

    # 7. Temperatura > 38°C
    if "temperatura" in dados_norm and float(dados_norm["temperatura"]) > 38.0:
        protocolos_acionados.append({
            "id": "PROT-07",
            "texto": PROTOCOLOS[6],
            "variavel": "temperatura",
            "valor_paciente": float(dados_norm["temperatura"]),
            "limiar": "> 38°C"
        })

    # 8. Densidade de eventos > 6
    if "densidade_eventos" in dados_norm and float(dados_norm["densidade_eventos"]) > 6.0:
        protocolos_acionados.append({
            "id": "PROT-08",
            "texto": PROTOCOLOS[7],
            "variavel": "densidade_eventos",
            "valor_paciente": float(dados_norm["densidade_eventos"]),
            "limiar": "> 6"
        })

    # 9. PA Sistólica < 90 mmHg
    if "pa_sistolica" in dados_norm and float(dados_norm["pa_sistolica"]) < 90.0:
        protocolos_acionados.append({
            "id": "PROT-09",
            "texto": PROTOCOLOS[8],
            "variavel": "pa_sistolica",
            "valor_paciente": float(dados_norm["pa_sistolica"]),
            "limiar": "< 90 mmHg"
        })

    # 10. Risco sistêmico ALTO
    if str(classificacao).upper() == "ALTO":
        protocolos_acionados.append({
            "id": "PROT-10",
            "texto": PROTOCOLOS[9],
            "variavel": "classificacao_risco",
            "valor_paciente": classificacao,
            "limiar": "== ALTO"
        })

    return protocolos_acionados
