"""Definição dos 4 agentes especializados e orquestração de handoffs com o OpenAI Agents SDK."""

import sys
from typing import Any
from agents import Agent, RunContextWrapper, handoff
from src.agents_system.context import CardioContext
from src.agents_system.guardrails import validar_saida_planejador
from src.agents_system.schemas import RecomendacaoFinal
from src.agents_system.tools import consultar_base_protocolos, prever_risco_paciente
from src.config import OPENAI_MODEL

# Garante suporte UTF-8 no stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Funções de logging para os handoffs (visíveis no terminal e vídeo de demonstração)
def on_handoff_analista_risco(ctx: RunContextWrapper[CardioContext]) -> None:
    print("\n🔄 [HANDOFF]: Agente Orquestrador ➔ Agente Analista de Risco")


def on_handoff_especialista_protocolos(ctx: RunContextWrapper[CardioContext]) -> None:
    print("\n🔄 [HANDOFF]: Agente Analista de Risco ➔ Agente Especialista em Protocolos")


def on_handoff_planejador_resposta(ctx: RunContextWrapper[CardioContext]) -> None:
    print("\n🔄 [HANDOFF]: Agente Especialista em Protocolos ➔ Agente Planejador de Resposta")


def criar_sistema_agentes(model: str = OPENAI_MODEL) -> tuple[Agent, Agent, Agent, Agent]:
    """Instancia os quatro agentes colaborativos configurando tools, handoffs e guardrails."""

    # 4. Agente Planejador de Resposta (Consolidador final)
    agente_planejador = Agent(
        name="Agente Planejador de Resposta",
        model=model,
        handoff_description="Especialista em sintetizar recomendações clínicas e operacionais finais com base no risco e protocolos.",
        instructions="""Você é o Agente Planejador de Resposta do sistema CardioAI.
Sua missão é consolidar os dados do paciente, o risco predito pelo modelo de ML e os protocolos clínicos acionados.
Você DEVE:
1. Utilizar a probabilidade e a classificação exatamente como fornecidas pelo modelo de ML através do contexto.
2. Ter clareza absoluta de que a probabilidade predita refere-se a "pico de risco (sobrecarga/criticidade do cenário)", e NUNCA a "complicações cardiovasculares". Você NUNCA deve afirmar diagnósticos clínicos.
3. Utilizar a lista de protocolos exatamente como retornada pela ferramenta de protocolos (com a mesma redação oficial).
4. Elaborar ações operacionais práticas, hospitalares e emergenciais imediatas adequadas para a equipe médica e de enfermagem (gestão de leitos, contingência e suporte).
5. Redigir uma justificativa sólida, conectando as variáveis críticas do paciente e da unidade (ex: saturação de O2, carga de leitos, tempo de espera, FC, densidade de eventos) às decisões operacionais tomadas, sem inferir diagnósticos médicos.
6. Produzir a resposta estritamente conforme o esquema RecomendacaoFinal.
NUNCA invente números de probabilidade, nunca afirme diagnósticos e nunca adicione protocolos fora da lista oficial.
""",
        output_type=RecomendacaoFinal,
        output_guardrails=[validar_saida_planejador],
    )

    # 3. Agente Especialista em Protocolos
    agente_protocolos = Agent(
        name="Agente Especialista em Protocolos",
        model=model,
        handoff_description="Especialista médico responsável por consultar a base de protocolos clínicos determinísticos.",
        instructions="""Você é o Agente Especialista em Protocolos do sistema CardioAI.
Sua missão é consultar a base de diretrizes clínicas e operacionais.
Passos obrigatórios:
1. Chame a ferramenta `consultar_base_protocolos`.
2. Verifique os protocolos retornados e faça uma breve síntese das regras atendidas.
3. Transfira a responsabilidade (handoff) imediatamente para o `Agente Planejador de Resposta` para que ele estruture as ações e o plano final.
NUNCA adicione regras inventadas nem utilize outro método de consulta.
""",
        tools=[consultar_base_protocolos],
        handoffs=[
            handoff(
                agente_planejador,
                tool_description_override="Transfere para o Agente Planejador de Resposta para consolidar a recomendação final.",
                on_handoff=on_handoff_planejador_resposta
            )
        ]
    )

    # 2. Agente Analista de Risco
    agente_risco = Agent(
        name="Agente Analista de Risco",
        model=model,
        handoff_description="Especialista em Machine Learning responsável por acionar o modelo preditivo de pico de risco.",
        instructions="""Você é o Agente Analista de Risco do sistema CardioAI.
Sua missão é calcular o score preditivo de pico de risco (sobrecarga/criticidade do cenário) do paciente.
Passos obrigatórios:
1. Chame a ferramenta `prever_risco_paciente` para obter a probabilidade e classificação calculadas pelo modelo de ML treinado.
2. Analise brevemente os dados que mais contribuíram para o score de criticidade do cenário, sem afirmar diagnósticos.
3. Transfira a responsabilidade (handoff) imediatamente para o `Agente Especialista em Protocolos`.
NUNCA estime ou invente probabilidades por conta própria e NUNCA afirme diagnósticos; a inferência deve vir exclusivamente da ferramenta.
""",
        tools=[prever_risco_paciente],
        handoffs=[
            handoff(
                agente_protocolos,
                tool_description_override="Transfere para o Agente Especialista em Protocolos para cruzar os dados com as diretrizes clínicas.",
                on_handoff=on_handoff_especialista_protocolos
            )
        ]
    )

    # 1. Agente Orquestrador (Ponto de entrada do sistema)
    agente_orquestrador = Agent(
        name="Agente Orquestrador",
        model=model,
        handoff_description="Coordenador central do fluxo clínico. Valida dados e responde dúvidas de acompanhamento.",
        instructions="""Você é o Agente Orquestrador do sistema CardioAI (Hospital Inteligente).
Sua missão é coordenar o fluxo preditivo e atuar como interlocutor principal com os profissionais de saúde.
IMPORTANTE: A probabilidade estimada refere-se estritamente a "pico de risco (sobrecarga/criticidade do cenário)", e NUNCA a "complicações cardiovasculares". Você NÃO pode afirmar diagnósticos clínicos.

Fluxo padrão de atendimento a novo paciente:
1. Verifique se os dados do paciente estão disponíveis no contexto.
2. Informe o início da triagem cardiovascular/operacional e transfira imediatamente o fluxo (handoff) para o `Agente Analista de Risco`.

Perguntas de acompanhamento (modo interativo / follow-up):
Se o usuário fizer perguntas posteriores (ex: 'por que o plano de contingência foi acionado?'), responda diretamente como texto de forma clara, humanizada e profissional utilizando o histórico da conversa, o contexto clínico já avaliado e as regras determinísticas que embasaram a decisão. Lembre-se sempre de que o risco indica sobrecarga e criticidade do cenário de atendimento, não um diagnóstico de doença. NÃO faça handoff para o Analista de Risco em perguntas de dúvidas ou esclarecimentos.
""",
        handoffs=[
            handoff(
                agente_risco,
                tool_description_override="Transfere o novo caso para o Agente Analista de Risco calcular o score preditivo.",
                on_handoff=on_handoff_analista_risco
            )
        ]
    )

    return agente_orquestrador, agente_risco, agente_protocolos, agente_planejador
