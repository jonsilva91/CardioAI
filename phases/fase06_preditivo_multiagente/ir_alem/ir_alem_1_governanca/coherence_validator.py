"""Validador determinístico de coerência clínica e regulamentar.

Verifica se as decisões geradas pelo sistema multiagente estão em estrita
conformidade com as regras clínicas, limiares operacionais e diretrizes do hospital,
reaproveitando as regras oficiais de src.protocols e os limiares de src.config.
"""

import sys
from pathlib import Path
from typing import Any

# Garante resolução dos módulos da Fase 6 sem duplicação de código
FASE06_DIR = Path(__file__).resolve().parents[2]
if str(FASE06_DIR) not in sys.path:
    sys.path.insert(0, str(FASE06_DIR))

from src.config import classificar_risco
from src.predictor import normalizar_dados_paciente
from src.protocols import PROTOCOLOS, consultar_protocolos


def validar_coerencia(
    dados: dict[str, Any],
    resultado: dict[str, Any] | Any
) -> dict[str, Any]:
    """Valida a coerência determinística da decisão contra as regras clínicas oficiais.

    Verificações realizadas:
    a) Cada protocolo sugerido tem sua variável crítica realmente acima/abaixo do limiar.
    b) Nenhum protocolo que as regras exigem ficou de fora (omissão de conduta).
    c) Score (probabilidade) e classificação batem com os limiares do config.py.
    d) Classificação ALTO sem 'risco sistêmico alto' é incoerente (e vice-versa).

    Args:
        dados: Dicionário contendo os dados clínicos e operacionais do paciente.
        resultado: Dicionário ou objeto (ex: RecomendacaoFinal) contendo:
                   - probabilidade (float)
                   - classificacao (str: 'BAIXO', 'MODERADO', 'ALTO')
                   - protocolos_sugeridos (list[str])

    Returns:
        Dicionário com:
            - coerente (bool): True se nenhuma inconsistência foi encontrada.
            - inconsistencias (list[str]): Lista descritiva de todas as violações encontradas.
    """
    inconsistencias: list[str] = []

    # Extração e normalização dos campos do resultado
    if hasattr(resultado, "model_dump"):
        res_dict = resultado.model_dump()
    elif isinstance(resultado, dict):
        res_dict = resultado
    else:
        res_dict = {
            "probabilidade": getattr(resultado, "probabilidade", None),
            "classificacao": getattr(resultado, "classificacao", None),
            "protocolos_sugeridos": getattr(resultado, "protocolos_sugeridos", []),
        }

    prob = res_dict.get("probabilidade")
    classificacao = str(res_dict.get("classificacao", "")).strip().upper()
    protocolos_sugeridos = res_dict.get("protocolos_sugeridos") or []
    if not isinstance(protocolos_sugeridos, list):
        protocolos_sugeridos = [str(protocolos_sugeridos)]

    dados_norm = normalizar_dados_paciente(dados)

    # -------------------------------------------------------------------------
    # c) Score e classificação batem com os limiares do config.py
    # -------------------------------------------------------------------------
    if prob is None:
        inconsistencias.append("Probabilidade de risco ausente no resultado.")
        classificacao_esperada = None
    else:
        try:
            prob_float = float(prob)
            classificacao_esperada = classificar_risco(prob_float)
            if classificacao != classificacao_esperada:
                inconsistencias.append(
                    f"Inconsistência de classificação (Regra C): probabilidade {prob_float:.2f} "
                    f"resulta na classificação '{classificacao_esperada}' pelos limiares do config.py, "
                    f"mas a decisão apresentou '{classificacao}'."
                )
        except (ValueError, TypeError) as e:
            inconsistencias.append(f"Probabilidade inválida ({prob}): {e}")
            classificacao_esperada = None

    # Protocolo oficial de risco sistêmico (índice 9 em PROTOCOLOS)
    protocolo_emergencia = PROTOCOLOS[9]  # "Se risco sistêmico alto → ativar estado de emergência"

    # -------------------------------------------------------------------------
    # d) Classificação ALTO sem 'risco sistêmico alto' é incoerente (e vice-versa)
    # -------------------------------------------------------------------------
    possui_emergencia = any(
        protocolo_emergencia.lower() in p.lower() or "estado de emergência" in p.lower()
        for p in protocolos_sugeridos
    )

    if classificacao == "ALTO" and not possui_emergencia:
        inconsistencias.append(
            f"Inconsistência de risco sistêmico (Regra D): classificação ALTO exige obrigatoriamente "
            f"o protocolo '{protocolo_emergencia}', que não foi sugerido."
        )

    if classificacao != "ALTO" and possui_emergencia:
        inconsistencias.append(
            f"Inconsistência de risco sistêmico (Regra D): protocolo '{protocolo_emergencia}' "
            f"foi ativado indevidamente para classificação '{classificacao}' (permitido exclusivamente em risco ALTO)."
        )

    # Consulta dos protocolos obrigatórios pelas regras determinísticas
    # Usa a classificação declarada (ou a esperada se disponível) para avaliar as diretrizes
    classe_para_regras = classificacao if classificacao in ["BAIXO", "MODERADO", "ALTO"] else (classificacao_esperada or "BAIXO")
    protocolos_esperados_info = consultar_protocolos(dados_norm, classe_para_regras)
    textos_esperados = [p["texto"] for p in protocolos_esperados_info]
    set_esperados = set(textos_esperados)
    set_sugeridos = set(protocolos_sugeridos)

    # -------------------------------------------------------------------------
    # a) Cada protocolo sugerido tem sua variável crítica realmente acima/abaixo do limiar
    # -------------------------------------------------------------------------
    for prot_sugerido in protocolos_sugeridos:
        # Verifica se pertence ao conjunto oficial de 10 protocolos
        if prot_sugerido not in PROTOCOLOS:
            inconsistencias.append(
                f"Protocolo não regulamentado (Regra A): '{prot_sugerido}' não pertence à lista "
                f"oficial de protocolos hospitalares da instituição."
            )
            continue

        # Se pertence à lista oficial, verifica se as variáveis do paciente justificam sua ativação
        if prot_sugerido not in set_esperados:
            inconsistencias.append(
                f"Protocolo indevido (Regra A): '{prot_sugerido}' foi sugerido, mas os dados vitais "
                f"do paciente não atingem o limiar de acionamento."
            )

    # -------------------------------------------------------------------------
    # b) Nenhum protocolo que as regras exigem ficou de fora
    # -------------------------------------------------------------------------
    for prot_esperado in textos_esperados:
        if prot_esperado not in set_sugeridos:
            inconsistencias.append(
                f"Protocolo obrigatório omitido (Regra B): '{prot_esperado}' deveria ter sido ativado "
                f"com base nos parâmetros clínicos do paciente, mas foi omitido."
            )

    return {
        "coerente": len(inconsistencias) == 0,
        "inconsistencias": inconsistencias,
    }
