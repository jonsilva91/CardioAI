"""Gera o documento PDF oficial da Arquitetura Multiagente (exatamente 3 páginas).

Utiliza o framework ReportLab e preenche com os textos e saídas reais obtidos
nas execuções reais com a OpenAI API em reports/execucoes/novo_caso.txt.
"""

from pathlib import Path
import sys
import pypdfium2 as pdfium

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak

FASE06_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = FASE06_DIR / "docs"
PDF_PATH = DOCS_DIR / "arquitetura_multiagente.pdf"
DIAGRAMA_PATH = DOCS_DIR / "diagrama_arquitetura.png"


def gerar_pdf_arquitetura(caminho_pdf: Path) -> None:
    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "ArchTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=2
    )
    meta_style = ParagraphStyle(
        "ArchMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        "ArchH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12.5,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=4,
        spaceAfter=2
    )
    body_style = ParagraphStyle(
        "ArchBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.2,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=3
    )
    code_style = ParagraphStyle(
        "ArchCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=6.8,
        leading=8.6,
        textColor=colors.HexColor("#111827")
    )
    box_header_style = ParagraphStyle(
        "BoxHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.6,
        leading=9.5,
        textColor=colors.HexColor("#1e3a8a")
    )

    story = []

    # ==================== PÁGINA 1 ====================
    story.append(Paragraph("CardioAI: Sistema Preditivo Multiagente", titulo_style))
    story.append(Paragraph(
        "<b>Fase 6 — Coração Sob Controle | FIAP 2026</b><br/>"
        "<b>Integrantes:</b> Jonas Luis da Silva (RM561465) & Edson Henrique Felix Batista (RM566321)<br/>"
        "<b>Framework:</b> OpenAI Agents SDK (<code>openai-agents</code>) | <b>Modelo Base:</b> gpt-4o-mini | "
        "<b>ML:</b> Random Forest Classifier (Acurácia: 99,9% | F1: 0,9981)",
        meta_style
    ))

    story.append(Paragraph("1. Diagrama Geral da Arquitetura Multiagente", h2_style))
    if DIAGRAMA_PATH.exists():
        story.append(Image(str(DIAGRAMA_PATH), width=540, height=205))
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Especialização dos 4 Agentes e Fluxo de Handoffs", h2_style))
    story.append(Paragraph(
        "A arquitetura adota especialização estrita de papéis para eliminar alucinações e desacoplar responsabilidades funcionais:<br/>"
        "• <b>1. Agente Orquestrador:</b> Ponto focal de entrada do sistema. Valida a estrutura JSON do paciente contra o esquema Pydantic "
        "<code>DadosPaciente</code> (10 features obrigatórias). Inicia a triagem disparando o primeiro <i>handoff</i> para o Analista de Risco. "
        "Atua também no modo interativo pós-triagem, respondendo dúvidas do médico sobre as diretrizes adotadas;<br/>"
        "• <b>2. Agente Analista de Risco:</b> Especialista exclusivo em inferência analítica. O LLM é expressamente instruído a <b>nunca inventar "
        "ou estimar probabilidades</b>. Invoca compulsoriamente a ferramenta <code>prever_risco_paciente</code>, executando o modelo Random Forest "
        "treinado (99,9% de acurácia) com contexto isolado, e realiza <i>handoff</i> imediato para o Especialista em Protocolos;<br/>"
        "• <b>3. Agente Especialista em Protocolos:</b> Especialista em conformidade hospitalar. Executa a ferramenta determinística "
        "<code>consultar_base_protocolos</code>, cruzando os sinais vitais e os indicadores operacionais contra a matriz de 10 diretrizes clínicas "
        "oficiais. Registra os protocolos acionados no contexto e transfere o controle para o Agente Planejador;<br/>"
        "• <b>4. Agente Planejador de Resposta:</b> Síntese clínica e operacional do hospital inteligente. Gera ações práticas de alocação de leitos, "
        "remanejamento de insumos e vigilância intensiva. A saída é tipada estritamente no esquema Pydantic <code>RecomendacaoFinal</code> e "
        "monitorada em tempo real por um <b>Output Guardrail determinístico</b>.",
        body_style
    ))

    # ==================== PÁGINA 2 ====================
    story.append(PageBreak())

    story.append(Paragraph("3. Compartilhamento de Estado, Memória Persistente e Guardrails", h2_style))
    story.append(Paragraph(
        "• <b>Isolamento de Contexto (<code>CardioContext</code>):</b> Atendendo às diretrizes de arquitetura limpa, o sistema não utiliza estado global. "
        "Cada paciente possui uma instância de <code>CardioContext</code> injetada via <code>RunContextWrapper</code>, contendo <code>dados_paciente</code>, "
        "<code>resultado_risco</code> e <code>protocolos_acionados</code>, assegurando concorrência segura e isolamento hermético entre atendimentos.<br/>"
        "• <b>Memória Persistente e Sessões SQLite (<code>SQLiteSession</code>):</b> Cada atendimento registra um histórico de mensagens em "
        "<code>data/sessions.db</code>. No modo interativo (<code>--interativo</code>), o profissional de saúde pode questionar a decisão tomada "
        "(ex: <i>'por que o plano de contingência foi acionado?'</i>), e o Orquestrador recupera o histórico da sessão para justificar a conduta.<br/>"
        "• <b>Validação Estrita via Output Guardrail (Tripwire):</b> O Planejador é interceptado pelo decorador <code>@output_guardrail</code>. "
        "O tripwire (<code>OutputGuardrailTripwireTriggered</code>) é disparado imediatamente se: (a) a probabilidade numérica divergir em mais de 0.01 do "
        "Random Forest; (b) a classificação categórica não respeitar os limiares; (c) houver protocolo fora da lista oficial; (d) for omitido algum "
        "protocolo obrigatório; ou (e) for injetado algum protocolo não autorizado pelas variáveis clínicas (ex: protocolo de SpO2 para saturação normal).",
        body_style
    ))

    story.append(Paragraph("4. Exemplo Real de Execução — Paciente do Enunciado (novo_caso.json)", h2_style))
    story.append(Paragraph(
        "Execução real com o modelo <b>gpt-4o-mini</b> e o Random Forest. Saída extraída de <code>reports/execucoes/novo_caso.txt</code>:",
        body_style
    ))

    texto_saida_real = (
        "🔄 [HANDOFF]: Agente Orquestrador ➔ Agente Analista de Risco<br/>"
        "🔧 [TOOL] prever_risco_paciente: Probabilidade = 0.99 | Classe = 1 | Classificação = ALTO<br/>"
        "🔄 [HANDOFF]: Agente Analista de Risco ➔ Agente Especialista em Protocolos<br/>"
        "🔧 [TOOL] consultar_base_protocolos: 4 protocolos acionados<br/>"
        "   * Se carga do sistema > 85% → abrir unidades temporárias<br/>"
        "   * Se disponibilidade_recursos < 30% → redistribuir insumos<br/>"
        "   * Se densidade_eventos > 6 → ativar plano de contingência<br/>"
        "   * Se risco sistêmico alto → ativar estado de emergência<br/>"
        "🔄 [HANDOFF]: Agente Especialista em Protocolos ➔ Agente Planejador de Resposta<br/>"
        "🛡️ [GUARDRAIL]: Saída do Planejador validada com sucesso! Sem violações de integridade.<br/>"
        "----------------------------------------------------------------------------------------------------<br/>"
        "<b>RISCO PREVISTO:</b> 0.99 | <b>CLASSIFICAÇÃO:</b> ALTO<br/>"
        "<b>PROTOCOLOS SUGERIDOS:</b><br/>"
        "- Se carga do sistema > 85% → abrir unidades temporárias<br/>"
        "- Se disponibilidade_recursos < 30% → redistribuir insumos<br/>"
        "- Se densidade_eventos > 6 → ativar plano de contingência<br/>"
        "- Se risco sistêmico alto → ativar estado de emergência<br/>"
        "<b>AÇÕES OPERACIONAIS:</b><br/>"
        "- Monitoramento contínuo dos sinais vitais do paciente em tempo real.<br/>"
        "- Notificar a equipe médica sobre o alto risco cardiovascular identificado.<br/>"
        "- Preparar a equipe para administração imediata de medicamentos cardiovasculares necessários.<br/>"
        "- Estabelecer contato com unidades de terapia intensiva para potencial internação do paciente.<br/>"
        "<b>JUSTIFICATIVA:</b><br/>"
        "Dada a alta probabilidade de 99% para risco cardiovascular, associada a uma classificação de Risco Alto, é fundamental ações imediatas "
        "de cuidado. A sobrecarga do sistema, com carga superior a 85%, indica uma necessidade de abrir unidades temporárias para melhor gerenciamento "
        "dos pacientes. Já a baixa disponibilidade de recursos (25%) requer redistribuição imediata de insumos para garantir suporte eficiente. A densidade "
        "de eventos, superior a 6, sugere que ativar o plano de contingência é necessário para manejo adequado. Conforme os protocolos, devemos ativar "
        "o estado de emergência devido ao risco sistêmico elevado, assegurando medidas apropriadas para a segurança do paciente.<br/>"
        "<b>AVISO:</b> As informações coletadas são de natureza sensível e devem ser tratadas em conformidade com a legislação de proteção de dados e normas de ética médica."
    )

    tabela_box = Table(
        [[Paragraph(texto_saida_real, code_style)]],
        colWidths=[540]
    )
    tabela_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(tabela_box)

    # ==================== PÁGINA 3 ====================
    story.append(PageBreak())

    story.append(Paragraph("5. Demonstração Prática do Tripwire e Modo Interativo", h2_style))
    story.append(Paragraph(
        "Para comprovar a robustez do pipeline em ambiente real, foram conduzidos testes práticos gravados em <code>reports/execucoes/</code>:",
        body_style
    ))

    texto_guardrail = (
        "<b>🚨 Disparo Real do Tripwire (<code>scripts/demo_guardrail.py</code> ➔ <code>reports/execucoes/guardrail.txt</code>):</b><br/>"
        "Ao instruir expressamente o Planejador a adicionar o protocolo <i>'Se SPO2 < 88% → iniciar suporte respiratório imediato'</i> "
        "para o paciente do enunciado (SpO2 = 89%), o <b>Output Guardrail</b> interceptou a recomendação antes da entrega:<br/>"
        "<code>🚨 [TRIPWIRE DISPARADO NO GUARDRAIL]: Protocolo(s) indevido(s) ou não autorizado(s) pelas regras clínicas determinísticas: "
        "['Se SPO2 < 88% → iniciar suporte respiratório imediato']</code><br/>"
        "<code>🚨 EXCEÇÃO CAPTURADA: OutputGuardrailTripwireTriggered — Guardrail OutputGuardrail triggered tripwire</code><br/>"
        "<b>Conclusão:</b> O sistema impediu com sucesso uma alucinação clínica grave e uma conduta invasiva inadequada."
    )
    story.append(Paragraph(texto_guardrail, body_style))
    story.append(Spacer(1, 3))

    texto_interativo = (
        "<b>💬 Pergunta de Acompanhamento no Modo Interativo (<code>reports/execucoes/interativo_novo_caso.txt</code>):</b><br/>"
        "• <b>Pergunta do Profissional:</b> <i>'por que o plano de contingência foi acionado?'</i><br/>"
        "• <b>Resposta Real do Orquestrador (via SQLiteSession):</b> <i>'O plano de contingência foi acionado devido a uma combinação de fatores "
        "que indicam uma sobrecarga crítica no sistema de atendimento: (1) Carga do sistema em 92% (> 85%), indicando operação acima da capacidade; "
        "(2) Disponibilidade de recursos em 25% (< 30%), gerando risco de desabastecimento; (3) Densidade de eventos em 7 (> 6). "
        "Essa soma de condições justifica a ativação do plano de contingência para garantir atendimento seguro sem inferir diagnósticos patológicos.'</i>"
    )
    story.append(Paragraph(texto_interativo, body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("6. Divergências Documentadas do Enunciado e Boas Práticas de Engenharia", h2_style))
    story.append(Paragraph(
        "• <b>Divergência de SpO2:</b> No exemplo textual fornecido no enunciado da FIAP, a saída sugeria a inclusão de <i>'SPO2 < 88%'</i>. "
        "No entanto, os dados brutos do caso informam <code>spo2_media: 89</code>. Como 89 não é menor que 88, nosso motor determinístico "
        "seguiu rigorosamente a regra médica estrita e <b>não acionou</b> suporte respiratório invasivo. O teste do tripwire comprovou que tentar "
        "forçar esse protocolo constitui violação de integridade clínica.<br/>"
        "• <b>Separação entre Modelo e Regras (Caso Moderado 0.59):</b> O paciente de teste com risco moderado (0.59) não atinge limiares de protocolos "
        "críticos, comprovando na prática que a predição de criticidade e as regras de intervenção operam em camadas distintas.<br/>"
        "• <b>Normalização da Chave <code>'disponibilidade recursos'</code>:</b> O dicionário Python do enunciado continha espaço na chave. "
        "A arquitetura CardioAI converte automaticamente espaços em underscores com total interoperabilidade.",
        body_style
    ))

    story.append(Paragraph("7. Comandos para Reprodução Rápida", h2_style))
    story.append(Paragraph(
        "<code>python -m src.agents_system.main --paciente data/exemplos/novo_caso.json</code> &nbsp;|&nbsp; "
        "<code>python scripts/demo_guardrail.py</code> &nbsp;|&nbsp; "
        "<code>pytest -v</code> (15 testes unitários aprovados)",
        code_style
    ))

    doc.build(story)
    print(f"PDF da arquitetura gerado em: {caminho_pdf}")


def main() -> None:
    gerar_pdf_arquitetura(PDF_PATH)
    doc_verif = pdfium.PdfDocument(str(PDF_PATH))
    total_paginas = len(doc_verif)
    print(f"Total de páginas: {total_paginas} (Limite máximo: 3)")
    if total_paginas > 3:
        print(f"❌ ERRO: O PDF ultrapassou o limite de 3 páginas ({total_paginas})!")
        sys.exit(1)
    else:
        print("✅ Validação de páginas concluída com sucesso!")


if __name__ == "__main__":
    main()
