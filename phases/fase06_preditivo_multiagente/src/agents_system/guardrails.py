"""Módulo de validação de saída (output guardrails) com tripwire determinístico."""

from typing import Any
from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, output_guardrail
from src.agents_system.context import CardioContext
from src.agents_system.schemas import RecomendacaoFinal
from src.config import classificar_risco
from src.protocols import PROTOCOLOS


@output_guardrail
def validar_saida_planejador(
    ctx: RunContextWrapper[CardioContext],
    agent: Agent,
    output: Any
) -> GuardrailFunctionOutput:
    """Valida estritamente a saída gerada pelo Agente Planejador antes de ser entregue.

    Aciona tripwire se:
    (a) a probabilidade da saída diferir da calculada pela ferramenta de ML (ctx.context.resultado_risco);
    (b) houver protocolo sugerido que não conste na lista oficial PROTOCOLOS do enunciado;
    (c) faltar algum protocolo acionado pelo motor determinístico (ctx.context.protocolos_acionados);
    (d) a classificação de risco não bater com os limiares oficiais.
    """
    erros: list[str] = []

    # Extrai o objeto tipado ou dicionário
    if isinstance(output, RecomendacaoFinal):
        rec = output
    elif isinstance(output, dict):
        rec = RecomendacaoFinal(**output)
    else:
        # Se for string ou outro tipo, tenta converter ou avisa
        try:
            rec = RecomendacaoFinal.model_validate_json(output)
        except Exception:
            return GuardrailFunctionOutput(
                output_info={"erro": "Formato de saída incompatível com RecomendacaoFinal."},
                tripwire_triggered=True
            )

    # (a) e (d): Valida probabilidade e classificação em relação ao modelo de ML
    if ctx.context.resultado_risco is not None:
        prob_modelo = float(ctx.context.resultado_risco["probabilidade"])
        if abs(rec.probabilidade - prob_modelo) > 0.01:
            erros.append(
                f"Divergência de probabilidade: modelo calculou {prob_modelo:.2f}, "
                f"mas a saída gerada informou {rec.probabilidade:.2f}."
            )

        classif_esperada = classificar_risco(rec.probabilidade)
        if rec.classificacao != classif_esperada:
            erros.append(
                f"Classificação incoerente: para probabilidade {rec.probabilidade:.2f}, "
                f"a classificação correta é '{classif_esperada}', mas foi informado '{rec.classificacao}'."
            )

    # (b) e (c): Valida integridade e fidelidade dos protocolos
    if ctx.context.protocolos_acionados is not None:
        protocolos_esperados = {p["texto"].strip() for p in ctx.context.protocolos_acionados}
        protocolos_recebidos = {p.strip() for p in rec.protocolos_sugeridos}

        # (b) Algum protocolo não existe na lista oficial do enunciado
        invalidos = [p for p in protocolos_recebidos if p not in PROTOCOLOS]
        if invalidos:
            erros.append(f"Protocolo(s) desconhecido(s) ou inventado(s) na saída: {invalidos}")

        # (c) Faltou algum protocolo acionado pelas regras
        faltantes = protocolos_esperados - protocolos_recebidos
        if faltantes:
            erros.append(
                f"Protocolo(s) obrigatório(s) acionado(s) pelas regras clínicas que foram omitidos: {list(faltantes)}"
            )

        # (d) Protocolo extra não acionado pelas regras determinísticas do paciente
        extras = protocolos_recebidos - protocolos_esperados
        if extras:
            erros.append(
                f"Protocolo(s) indevido(s) ou não autorizado(s) pelas regras clínicas determinísticas: {list(extras)}"
            )

    if erros:
        msg_erro = "; ".join(erros)
        print(f"\n🚨 [TRIPWIRE DISPARADO NO GUARDRAIL]: {msg_erro}")
        return GuardrailFunctionOutput(
            output_info={"erros": erros, "detalhes": msg_erro},
            tripwire_triggered=True
        )

    print("\n🛡️ [GUARDRAIL]: Saída do Planejador validada com sucesso! Sem violações de integridade.")
    return GuardrailFunctionOutput(
        output_info={"status": "aprovado"},
        tripwire_triggered=False
    )
