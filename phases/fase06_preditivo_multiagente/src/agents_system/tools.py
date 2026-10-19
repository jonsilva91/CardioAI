"""Tools integradas ao OpenAI Agents SDK para predição de risco e consulta de protocolos."""

import json
from agents import RunContextWrapper, function_tool
from src.agents_system.context import CardioContext
from src.predictor import prever_risco
from src.protocols import consultar_protocolos


@function_tool
def prever_risco_paciente(ctx: RunContextWrapper[CardioContext]) -> str:
    """Calcula a probabilidade e a classificação de risco cardiovascular do paciente usando o modelo de Machine Learning treinado.

    O LLM NUNCA deve calcular probabilidades ou inventar números por conta própria;
    esta ferramenta é a única fonte confiável do valor de probabilidade e classe.
    """
    if not ctx.context.dados_paciente:
        raise ValueError("Nenhum dado de paciente foi encontrado no contexto de execução.")

    resultado = prever_risco(ctx.context.dados_paciente)
    ctx.context.resultado_risco = resultado

    print(
        f"\n🔧 [TOOL] prever_risco_paciente executada com sucesso:"
        f"\n   - Probabilidade: {resultado['probabilidade']:.2f}"
        f"\n   - Classe Prevista: {resultado['classe_prevista']}"
        f"\n   - Classificação: {resultado['classificacao']}"
    )

    return json.dumps(resultado, ensure_ascii=False)


@function_tool
def consultar_base_protocolos(ctx: RunContextWrapper[CardioContext]) -> str:
    """Consulta a base de conhecimento de protocolos médicos a partir dos dados do paciente e da classificação de risco calculada.

    Avalia deterministicamente os limiares clínicos e operacionais para acionar os protocolos pertinentes.
    """
    if ctx.context.resultado_risco is None:
        raise ValueError(
            "O risco do paciente ainda não foi calculado. O agente de risco deve executar "
            "a ferramenta 'prever_risco_paciente' antes de consultar os protocolos."
        )

    classificacao = ctx.context.resultado_risco["classificacao"]
    protocolos = consultar_protocolos(ctx.context.dados_paciente, classificacao)
    ctx.context.protocolos_acionados = protocolos

    print(
        f"\n🔧 [TOOL] consultar_base_protocolos executada com sucesso:"
        f"\n   - Protocolos acionados: {len(protocolos)}"
    )
    for p in protocolos:
        print(f"     * {p['texto']}")

    return json.dumps(protocolos, ensure_ascii=False)
