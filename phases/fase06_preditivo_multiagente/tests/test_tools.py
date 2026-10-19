"""Testes unitários para as tools e guardrails do sistema multiagente (sem chamadas a APIs externas)."""

import json
import pytest
from agents import RunContextWrapper
from src.agents_system.context import CardioContext
from src.agents_system.guardrails import validar_saida_planejador
from src.agents_system.schemas import RecomendacaoFinal
from src.agents_system.tools import consultar_base_protocolos, prever_risco_paciente


@pytest.fixture
def contexto_novo_caso() -> tuple[CardioContext, RunContextWrapper]:
    dados = {
        "idade_media": 62,
        "carga_sistema": 92,
        "tempo_espera": 75,
        "fc_media": 118,
        "spo2_media": 89,
        "pa_sistolica": 100,
        "temperatura": 37.5,
        "densidade_eventos": 7,
        "eventos_24h": 5,
        "disponibilidade_recursos": 25,
    }
    ctx = CardioContext(dados_paciente=dados)
    wrapper = RunContextWrapper(ctx)
    return ctx, wrapper


def test_tool_prever_risco_paciente_sucesso(contexto_novo_caso):
    """Valida que a tool prever_risco_paciente preenche o contexto e retorna JSON válido."""
    ctx, wrapper = contexto_novo_caso
    func = getattr(prever_risco_paciente, "__wrapped__", prever_risco_paciente)
    resposta_json = func(wrapper)

    resultado = json.loads(resposta_json)
    assert resultado["classificacao"] == "ALTO"
    assert resultado["classe_prevista"] == 1
    assert resultado["probabilidade"] >= 0.70

    # Verifica gravação no contexto
    assert ctx.resultado_risco is not None
    assert ctx.resultado_risco["classificacao"] == "ALTO"


def test_tool_consultar_base_protocolos_ordem_correta(contexto_novo_caso):
    """Valida que consultar_base_protocolos depende do resultado de risco prévio."""
    ctx, wrapper = contexto_novo_caso
    func_pred = getattr(prever_risco_paciente, "__wrapped__", prever_risco_paciente)
    func_prot = getattr(consultar_base_protocolos, "__wrapped__", consultar_base_protocolos)

    # 1. Sem prever risco antes, deve levantar ValueError
    ctx.resultado_risco = None
    with pytest.raises(ValueError) as exc:
        func_prot(wrapper)
    assert "risco do paciente ainda não foi calculado" in str(exc.value)

    # 2. Executa a predição e depois consulta protocolos
    func_pred(wrapper)
    resposta_prots_json = func_prot(wrapper)
    protocolos = json.loads(resposta_prots_json)

    assert len(protocolos) == 4
    assert ctx.protocolos_acionados is not None
    textos = [p["texto"] for p in protocolos]
    assert "Se risco sistêmico alto → ativar estado de emergência" in textos


def test_guardrail_tripwire_divergencia_probabilidade(contexto_novo_caso):
    """Garante que o guardrail aciona tripwire se a probabilidade informada diferir do modelo."""
    ctx, wrapper = contexto_novo_caso
    func_pred = getattr(prever_risco_paciente, "__wrapped__", prever_risco_paciente)
    func_prot = getattr(consultar_base_protocolos, "__wrapped__", consultar_base_protocolos)

    func_pred(wrapper)
    func_prot(wrapper)

    # Saída adulterada com probabilidade incorreta
    saida_adulterada = RecomendacaoFinal(
        probabilidade=0.30,  # Modelo previu 0.99
        classificacao="BAIXO",
        protocolos_sugeridos=[p["texto"] for p in ctx.protocolos_acionados],
        acoes_operacionais=["Manter leito normal"],
        justificativa="Teste de adulteração",
    )

    func_guard = getattr(validar_saida_planejador, "guardrail_function", validar_saida_planejador)
    res = func_guard(wrapper, None, saida_adulterada)
    assert res.tripwire_triggered is True


def test_guardrail_aprovacao_saida_correta(contexto_novo_caso):
    """Garante que o guardrail aprova quando a saída é 100% coerente com o modelo e regras."""
    ctx, wrapper = contexto_novo_caso
    func_pred = getattr(prever_risco_paciente, "__wrapped__", prever_risco_paciente)
    func_prot = getattr(consultar_base_protocolos, "__wrapped__", consultar_base_protocolos)

    func_pred(wrapper)
    func_prot(wrapper)

    saida_correta = RecomendacaoFinal(
        probabilidade=ctx.resultado_risco["probabilidade"],
        classificacao=ctx.resultado_risco["classificacao"],
        protocolos_sugeridos=[p["texto"] for p in ctx.protocolos_acionados],
        acoes_operacionais=["Abrir unidades temporárias", "Redistribuir insumos"],
        justificativa="Paciente em estado crítico com alta carga sistêmica.",
    )

    func_guard = getattr(validar_saida_planejador, "guardrail_function", validar_saida_planejador)
    res = func_guard(wrapper, None, saida_correta)
    assert res.tripwire_triggered is False


def test_guardrail_tripwire_classificacao_incoerente(contexto_novo_caso):
    """Caso (b): Valida que o tripwire bloqueia quando a classificação diverge dos limiares de config.py."""
    ctx, wrapper = contexto_novo_caso
    func_pred = getattr(prever_risco_paciente, "__wrapped__", prever_risco_paciente)
    func_prot = getattr(consultar_base_protocolos, "__wrapped__", consultar_base_protocolos)

    func_pred(wrapper)
    func_prot(wrapper)

    # Probabilidade 0.99 exige classificação ALTO, mas enviamos MODERADO
    saida_classif_incoerente = RecomendacaoFinal(
        probabilidade=ctx.resultado_risco["probabilidade"],  # 0.99
        classificacao="MODERADO",  # Incoerente: para 0.99 deveria ser ALTO
        protocolos_sugeridos=[p["texto"] for p in ctx.protocolos_acionados],
        acoes_operacionais=["Manter vigilância"],
        justificativa="Classificação deliberadamente inconsistente para teste.",
    )

    func_guard = getattr(validar_saida_planejador, "guardrail_function", validar_saida_planejador)
    res = func_guard(wrapper, None, saida_classif_incoerente)
    assert res.tripwire_triggered is True
    assert "Classificação incoerente" in res.output_info["detalhes"]


def test_guardrail_tripwire_protocolo_fora_da_lista_oficial(contexto_novo_caso):
    """Caso (c): Valida que o tripwire bloqueia quando há protocolo alucinado fora da lista oficial."""
    ctx, wrapper = contexto_novo_caso
    func_pred = getattr(prever_risco_paciente, "__wrapped__", prever_risco_paciente)
    func_prot = getattr(consultar_base_protocolos, "__wrapped__", consultar_base_protocolos)

    func_pred(wrapper)
    func_prot(wrapper)

    # Adiciona um protocolo completamente inventado
    protocolos_com_alucinacao = [p["texto"] for p in ctx.protocolos_acionados] + [
        "Protocolo Inventado: Administrar placebo em dose alta imediatamente"
    ]

    saida_protocolo_invalido = RecomendacaoFinal(
        probabilidade=ctx.resultado_risco["probabilidade"],
        classificacao=ctx.resultado_risco["classificacao"],
        protocolos_sugeridos=protocolos_com_alucinacao,
        acoes_operacionais=["Ação de teste"],
        justificativa="Teste de protocolo fora da lista oficial.",
    )

    func_guard = getattr(validar_saida_planejador, "guardrail_function", validar_saida_planejador)
    res = func_guard(wrapper, None, saida_protocolo_invalido)
    assert res.tripwire_triggered is True
    assert "Protocolo(s) desconhecido(s) ou inventado(s)" in res.output_info["detalhes"]


def test_guardrail_tripwire_protocolo_obrigatorio_ausente(contexto_novo_caso):
    """Caso (d): Valida que o tripwire bloqueia quando um protocolo obrigatório das regras é omitido."""
    ctx, wrapper = contexto_novo_caso
    func_pred = getattr(prever_risco_paciente, "__wrapped__", prever_risco_paciente)
    func_prot = getattr(consultar_base_protocolos, "__wrapped__", consultar_base_protocolos)

    func_pred(wrapper)
    func_prot(wrapper)

    # Omite 2 dos 4 protocolos obrigatórios acionados pelo motor determinístico
    protocolos_incompletos = [p["texto"] for p in ctx.protocolos_acionados][:2]

    saida_incompleta = RecomendacaoFinal(
        probabilidade=ctx.resultado_risco["probabilidade"],
        classificacao=ctx.resultado_risco["classificacao"],
        protocolos_sugeridos=protocolos_incompletos,
        acoes_operacionais=["Ação parcial"],
        justificativa="Omissão de protocolos obrigatórios para teste do tripwire.",
    )

    func_guard = getattr(validar_saida_planejador, "guardrail_function", validar_saida_planejador)
    res = func_guard(wrapper, None, saida_incompleta)
    assert res.tripwire_triggered is True
    assert "Protocolo(s) obrigatório(s)" in res.output_info["detalhes"]

