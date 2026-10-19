"""Gerador do relatório técnico em PDF (máx. 2 páginas) para a atividade Ir Além 1."""

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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

CURRENT_DIR = Path(__file__).resolve().parent
PDF_PATH = CURRENT_DIR / "relatorio_ir_alem_1.pdf"


def gerar_pdf(caminho_pdf: Path = PDF_PATH) -> int:
    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=28,
        bottomMargin=28
    )

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "RelTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=2
    )
    subtitulo_style = ParagraphStyle(
        "RelSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=2
    )
    meta_style = ParagraphStyle(
        "RelMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#475569"),
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        "RelH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=4,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        "RelBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.6,
        leading=10.2,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4
    )
    code_style = ParagraphStyle(
        "RelCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=6.5,
        leading=8.2,
        textColor=colors.HexColor("#0f172a")
    )
    callout_style = ParagraphStyle(
        "RelCallout",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor("#0f172a")
    )
    table_cell = ParagraphStyle(
        "RelTableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.0,
        leading=8.8,
        textColor=colors.HexColor("#1e293b")
    )
    table_header = ParagraphStyle(
        "RelTableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.0,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # PÁGINA 1
    # =========================================================================
    story.append(Paragraph("CardioAI — Relatório Técnico de Governança e Auditoria Médica", titulo_style))
    story.append(Paragraph("Desafio Ir Além 1: Camada de Governança, Rastreabilidade e Auditoria em Sistemas Multiagente", subtitulo_style))
    story.append(Paragraph(
        "<b>FIAP</b> — Fase 6: Coração Sob Controle | <b>Disciplina:</b> Governança, Boas Práticas e Arquitetura de IA (GBA)<br/>"
        "<b>Integrantes:</b> Jonas Luis da Silva (RM561465) & Edson Henrique Felix Batista (RM566321)",
        meta_style
    ))

    story.append(Paragraph("1. Registro Estruturado de Decisões e Telemetria Nativa (OpenAI Agents SDK)", h2_style))
    story.append(Paragraph(
        "Em aplicações de Inteligência Artificial para saúde, a auditoria não pode depender de parsing volátil de texto no terminal. "
        "No CardioAI, a classe <code>AuditRunHooks</code> herda de <code>RunHooks</code> do <b>OpenAI Agents SDK</b> para interceptar callbacks nativos assíncronos "
        "(<code>on_agent_start</code>, <code>on_handoff</code>, <code>on_tool_start</code> e <code>on_tool_end</code>). Cada deliberação é persistida "
        "de forma append-only no arquivo <code>logs/decisoes.jsonl</code> com UUIDv4 exclusivo, carimbo temporal ISO-8601, integridade criptográfica SHA-256 dos dados brutos, "
        "sequência comprovada de handoffs entre agentes, ferramentas executadas com seus parâmetros e saídas, validação de coerência e status do guardrail.",
        body_style
    ))

    # Box com JSON real de produção
    json_real_texto = (
        "<b>{</b><br/>"
        '&nbsp;&nbsp;<b>"id_decisao"</b>: "a7d58a73-b0fa-40df-b99a-864587987470", <b>"timestamp"</b>: "2026-10-15T20:33:57.303Z",<br/>'
        '&nbsp;&nbsp;<b>"session_id"</b>: "audit_novo_caso_9a5a85", <b>"hash_dados_entrada"</b>: "3a89b22083c1a61063685a2893ee076f...b8",<br/>'
        '&nbsp;&nbsp;<b>"dados_paciente"</b>: {"idade": 62, "carga_sistema": 92%, "spo2": 89%, "pa_sistolica": 100, "densidade_eventos": 7, ...},<br/>'
        '&nbsp;&nbsp;<b>"modelo_preditivo"</b>: {"nome": "RandomForestClassifier", "sklearn_version": "1.9.0", "accuracy": 0.999, "f1_score": 0.9981},<br/>'
        '&nbsp;&nbsp;<b>"probabilidade"</b>: 0.99, <b>"classificacao"</b>: "ALTO", <b>"guardrail_status"</b>: "aprovado",<br/>'
        '&nbsp;&nbsp;<b>"protocolos_sugeridos"</b>: ["Carga > 85% -> unidades temporárias", "Recursos < 30% -> redistribuir insumos",<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Densidade > 6 -> contingência", "Risco sistêmico alto -> estado de emergência"],<br/>'
        '&nbsp;&nbsp;<b>"sequencia_handoffs"</b>: ["Orquestrador -> Analista de Risco", "Analista de Risco -> Esp. Protocolos", "Esp. Protocolos -> Planejador"],<br/>'
        '&nbsp;&nbsp;<b>"tools_chamadas"</b>: ["prever_risco_paciente (concluido)", "consultar_base_protocolos (concluido)"],<br/>'
        '&nbsp;&nbsp;<b>"validacao_coerencia"</b>: {"coerente": true, "inconsistencias": []}<br/>'
        "<b>}</b>"
    )

    t_json = Table([[Paragraph(json_real_texto, code_style)]], colWidths=[540])
    t_json.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_json)
    story.append(Spacer(1, 4))

    story.append(Paragraph("2. Validação Determinística de Coerência Clínica (`coherence_validator.py`)", h2_style))
    story.append(Paragraph(
        "Para blindar a decisão médica contra alucinações de modelos de linguagem, o CardioAI emprega o <code>coherence_validator.py</code>. "
        "O validador <b>reutiliza estritamente as diretrizes de <code>src/protocols.py</code> e limiares de <code>src/config.py</code> sem duplicar código</b>, "
        "operando como uma barreira regulamentar determinística que avalia quatro invariantes assistenciais:",
        body_style
    ))

    story.append(Paragraph(
        "• <b>Regra A (Condição Crítica Real):</b> Cada protocolo sugerido deve ter sua variável clínica ou operacional estritamente acima/abaixo do limiar regulamentar. Protocolos inventados ou ativados sem critério objetivo são reprovados.<br/>"
        "• <b>Regra B (Prevenção de Omissão de Conduta):</b> Nenhum protocolo que as diretrizes determinísticas exijam pode ficar de fora da recomendação final sintetizada pelo agente consolidador.<br/>"
        "• <b>Regra C (Conformidade com Limiares de Machine Learning):</b> O score de probabilidade inferido deve mapear perfeitamente para a classe correspondente (&lt;0.30 BAIXO, 0.30–0.70 MODERADO, &gt;0.70 ALTO).<br/>"
        "• <b>Regra D (Biunivocidade de Emergência Sistêmica):</b> A classificação ALTO exige compulsoriamente a ativação de <i>'Se risco sistêmico alto → ativar estado de emergência'</i>; em contrapartida, pacientes BAIXO ou MODERADO não podem conter esse protocolo sob hipótese alguma.",
        body_style
    ))

    # Quebra obrigatória para a página 2
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2
    # =========================================================================
    story.append(Paragraph("3. Detecção em Teste de Adulteração e Rastreabilidade Criptográfica", h2_style))

    # Box de teste de adulteração
    adulteracao_box = (
        "<b>Evidência do Teste Controlado de Adulteração (<code>run_auditado.py</code>):</b><br/>"
        "Para comprovar a robustez da governança, simulou-se a inserção fraudulenta da conduta de oxigenoterapia "
        "<i>'Se SPO2 &lt; 88% → iniciar suporte respiratório imediato'</i> na decisão do <b>novo_caso</b> (SpO2 real: 89.0%).<br/>"
        "<b>Resultado do Validador:</b> <code>coerente: false</code> | <b>Inconsistência capturada:</b> <i>'Protocolo indevido (Regra A): "
        "sugerido mas dados vitais não atingem o limiar de acionamento'</i>. Status no log gravado como <b>reprovado_por_coerencia</b>."
    )
    t_adulteracao = Table([[Paragraph(adulteracao_box, callout_style)]], colWidths=[540])
    t_adulteracao.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#f43f5e")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_adulteracao)
    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "A rastreabilidade é fundamentada em três pilares criptográficos e estruturais:<br/>"
        "• <b>Hash SHA-256 de Entrada:</b> As 10 variáveis do paciente são serializadas em JSON canônico ordenado. O hash resultante (ex: <code>3a89b22...1ab8</code>) "
        "impede alteração retroativa dos sinais vitais utilizados na decisão (non-repudiation).<br/>"
        "• <b>Metadados do Modelo (.joblib):</b> A função <code>obter_metadados_modelo()</code> lê dinamicamente do arquivo binário a versão do Scikit-Learn (1.9.0), data de treino e métricas auditáveis (Acurácia: 99,9%, F1-Score: 0,9981).<br/>"
        "• <b>Auditoria Interativa (CLI):</b> O script <code>consultar_auditoria.py</code> permite inspecionar decisões, filtrar por sessão, classe ou flag de incoerência.",
        body_style
    ))

    story.append(Paragraph("4. Princípios de Governança em Saúde e Mapeamento Concreto no Código", h2_style))
    story.append(Paragraph(
        "A governança de inteligência artificial em ambientes hospitalares transcende aspectos puramente técnicos, "
        "alinhando-se a preceitos bioéticos e legislações vigentes (LGPD, Resoluções CFM e diretrizes internacionais de Software as a Medical Device — SaMD):",
        body_style
    ))

    # Tabela de Princípios de Governança
    dados_tabela = [
        [
            Paragraph("Princípio Ético / Legal", table_header),
            Paragraph("Exigência Regulamentar na Saúde", table_header),
            Paragraph("Componente Concreto no CardioAI", table_header)
        ],
        [
            Paragraph("<b>Explicabilidade</b><br/>(Explainability)", table_cell),
            Paragraph("O profissional médico precisa compreender os fatores que motivaram o score e as regras de contingência.", table_cell),
            Paragraph("<code>cardio_agents.py</code> instrui o Planejador a justificar cada ação pelas variáveis críticas; <code>coherence_validator.py</code> garante fidelidade aos fatos.", table_cell)
        ],
        [
            Paragraph("<b>Accountability & Rastreabilidade</b>", table_cell),
            Paragraph("Cadeia ininterrupta de custódia das decisões: quem inferiu, quando, quais ferramentas foram executadas e quem aprovou.", table_cell),
            Paragraph("<code>audit_logger.py</code> grava log append-only com hash SHA-256 da entrada, métricas do <code>.joblib</code>, UUIDv4 e sequência real de handoffs via <code>AuditRunHooks</code>.", table_cell)
        ],
        [
            Paragraph("<b>LGPD & Minimização de Dados</b>", table_cell),
            Paragraph("Uso estrito dos dados indispensáveis ao atendimento, vedando exposição de dados sensíveis e PII desnecessárias.", table_cell),
            Paragraph("<code>data_generation.py</code> gera dados sintéticos controlados; o pipeline transaciona exclusivamente 10 variáveis numéricas sem identificadores civis ou PII.", table_cell)
        ],
        [
            Paragraph("<b>Humano no Loop</b><br/>(Human-in-the-Loop)", table_cell),
            Paragraph("A IA não substitui a soberania médica, vedando diagnósticos definitivos ou prescrições automáticas sem validação.", table_cell),
            Paragraph("Guardrail em <code>guardrails.py</code> e avisos em <code>schemas.py</code> garantem suporte analítico a risco operacional, alertando que o sistema não emite diagnóstico.", table_cell)
        ],
    ]

    t_gov = Table(dados_tabela, colWidths=[105, 215, 220])
    t_gov.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_gov)
    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "<b>Conclusão:</b> A camada de governança do CardioAI assegura total conformidade regulamentar, integridade determinística "
        "e auditabilidade completa, viabilizando o uso seguro de sistemas multiagente em ambientes hospitalares críticos.",
        body_style
    ))

    doc.build(story)

    # Validação do número de páginas com pypdfium2
    pdf = pdfium.PdfDocument(str(caminho_pdf))
    total_paginas = len(pdf)
    print(f"✅ Relatório PDF gerado em: {caminho_pdf} ({total_paginas} páginas)")
    return total_paginas


if __name__ == "__main__":
    total = gerar_pdf()
    if total > 2:
        print(f"❌ ATENÇÃO: O relatório excedeu 2 páginas ({total} páginas). Reduza o conteúdo!")
        sys.exit(1)
    else:
        print(f"🎉 SUCESSO: O relatório tem exatamente {total} páginas (dentro do limite máximo de 2 páginas).")
