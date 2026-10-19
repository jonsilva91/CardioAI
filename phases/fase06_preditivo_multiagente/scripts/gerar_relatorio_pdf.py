"""Gera o relatório técnico do modelo em PDF (máximo 2 páginas) a partir das métricas reais."""

from pathlib import Path
import sys
import pypdfium2 as pdfium

# Garante suporte UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak

FASE06_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = FASE06_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
PDF_PATH = REPORTS_DIR / "relatorio_tecnico_modelo.pdf"


def gerar_pdf_relatorio(caminho_pdf: Path) -> None:
    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "RelTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=3
    )
    meta_style = ParagraphStyle(
        "RelMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=8
    )
    h2_style = ParagraphStyle(
        "RelH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=6,
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        "RelBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=4
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1f2937")
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#ffffff")
    )

    story = []

    # ==================== PÁGINA 1 ====================
    story.append(Paragraph("Relatório Técnico: Modelo Preditivo de Pico de Risco", titulo_style))
    story.append(Paragraph(
        "<b>Projeto CardioAI — Fase 6: Coração Sob Controle (FIAP)</b><br/>"
        "<b>Integrantes:</b> Jonas Luis da Silva (RM561465) & Edson Henrique Felix Batista (RM566321) | "
        "<b>Modelo:</b> Random Forest Classifier (200 estimadores) | <b>Artefato:</b> <code>models/modelo_pico_risco.joblib</code>",
        meta_style
    ))

    story.append(Paragraph("1. Justificativa do Algoritmo e Comparação de Modelos", h2_style))
    story.append(Paragraph(
        "O objetivo clínico do modelo é antecipar situações de <b>pico de risco cardiovascular</b> (<code>classe 1</code>) combinando "
        "biomarcadores fisiológicos do paciente (FC, SpO2, PA) e sobrecarga operacional do hospital (carga do sistema, tempo de espera, insumos). "
        "Foram avaliados dois algoritmos fundamentais:<br/>"
        "• <b>Regressão Logística (Baseline com StandardScaler):</b> Modelo linear paramétrico rápido e explicável, mas limitado a hiperplanos contínuos;<br/>"
        "• <b>Random Forest Classifier (200 árvores, random_state=42):</b> Ensemble não-paramétrico baseado em *bagging*, capaz de capturar relações "
        "não-lineares e interações complexas entre múltiplos degraus de decisão.<br/>"
        "O Random Forest foi selecionado como o modelo definitivo por sua superioridade em acurácia e recall na detecção de descontinuidades lógicas.",
        body_style
    ))

    story.append(Paragraph("2. Interpretação das Métricas Reais no Conjunto de Teste (20% — 1.000 amostras)", h2_style))
    
    tabela_metricas = [
        [
            Paragraph("<b>Métrica de Desempenho</b>", table_header_style),
            Paragraph("<b>Regressão Logística (Baseline)</b>", table_header_style),
            Paragraph("<b>Random Forest (Modelo Vencedor)</b>", table_header_style)
        ],
        [
            Paragraph("Acurácia Global", table_cell_style),
            Paragraph("81,60% (0,8160)", table_cell_style),
            Paragraph("<b>99,90% (0,9990)</b>", table_cell_style)
        ],
        [
            Paragraph("Precisão (Classe 1 — Pico de Risco)", table_cell_style),
            Paragraph("69,34% (0,6934)", table_cell_style),
            Paragraph("<b>100,00% (1,0000)</b>", table_cell_style)
        ],
        [
            Paragraph("Recall / Sensibilidade (Classe 1)", table_cell_style),
            Paragraph("55,26% (0,5526)", table_cell_style),
            Paragraph("<b>99,62% (0,9962)</b>", table_cell_style)
        ],
        [
            Paragraph("F1-Score (Classe 1)", table_cell_style),
            Paragraph("61,51% (0,6151)", table_cell_style),
            Paragraph("<b>99,81% (0,9981)</b>", table_cell_style)
        ],
        [
            Paragraph("Validação Cruzada 5-Folds (Acurácia Média)", table_cell_style),
            Paragraph("82,62% ± 0,0080", table_cell_style),
            Paragraph("<b>99,78% ± 0,0019</b>", table_cell_style)
        ],
        [
            Paragraph("Validação Cruzada 5-Folds (F1 Médio)", table_cell_style),
            Paragraph("64,05% ± 0,0177", table_cell_style),
            Paragraph("<b>99,58% ± 0,0037</b>", table_cell_style)
        ]
    ]

    t_metricas = Table(tabela_metricas, colWidths=[180, 180, 180])
    t_metricas.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_metricas)
    story.append(Spacer(1, 4))

    story.append(Paragraph("3. Matriz de Confusão e Análise de Erros Clínicos", h2_style))
    story.append(Paragraph(
        "No conjunto de teste de 1.000 amostras, a matriz de confusão do Random Forest atingiu:<br/>"
        "• <b>Verdadeiros Negativos (TN):</b> 734 | <b>Falsos Positivos (FP):</b> 0 (Especificidade: 100%)<br/>"
        "• <b>Falsos Negativos (FN):</b> 1 | <b>Verdadeiros Positivos (TP):</b> 265 (Sensibilidade: 99,62%)<br/>"
        "Em ambiente de triagem hospitalar, o custo de um <b>Falso Negativo</b> (não identificar um paciente em pico de risco) é crítico. "
        "Com apenas 1 falso negativo em 266 casos de risco real, o modelo demonstrou segurança clínica excepcional.",
        body_style
    ))

    img_matriz = FIGURES_DIR / "matriz_confusao.png"
    if img_matriz.exists():
        story.append(Image(str(img_matriz), width=320, height=140))

    # ==================== PÁGINA 2 ====================
    story.append(PageBreak())

    story.append(Paragraph("4. Importância das Features e Relevância Fisiológica", h2_style))
    story.append(Paragraph(
        "A importância relativa das variáveis pelo critério de <i>Gini Importance</i> (Mean Decrease Impurity) reflete com precisão os "
        "gatilhos determinísticos de risco estabelecidos no enunciado:",
        body_style
    ))

    img_feat = FIGURES_DIR / "importancia_features.png"
    if img_feat.exists():
        story.append(Image(str(img_feat), width=480, height=160))

    story.append(Paragraph(
        "• <b>spO2_media e carga_sistema</b> lideram o ranking de relevância preditiva, confirmando que a descompensação respiratória combinada "
        "à saturação hospitalar são os vetores determinantes de emergência cardiovascular;<br/>"
        "• <b>densidade_eventos e disponibilidade_recursos</b> fornecem o contexto logístico essencial para acionamento de protocolos operacionais.",
        body_style
    ))

    story.append(Paragraph("5. Limiares de Decisão, Calibração e Riscos de Calibração", h2_style))
    story.append(Paragraph(
        "As probabilidades preditas pelo ensemble são mapeadas em três categorias clínicas padronizadas:<br/>"
        "• <b>BAIXO:</b> <code>probabilidade &lt; 0.30</code> — Monitoramento regular de enfermagem e reavaliação periódica;<br/>"
        "• <b>MODERADO:</b> <code>0.30 &le; probabilidade &lt; 0.70</code> — Alerta de vigilância e reserva preventiva de recursos;<br/>"
        "• <b>ALTO:</b> <code>probabilidade &ge; 0.70</code> — Ativação de plano de contingência, leitos temporários e estado de emergência.<br/>"
        "<b>Riscos de Calibração:</b> O modelo Random Forest tende a concentrar probabilidades nos extremos (0 e 1). Na inferência do "
        "paciente do enunciado (<code>novo_caso.json</code>), o score predito foi de <b>0.99 (99%)</b>, acionando confiavelmente o nível ALTO.",
        body_style
    ))

    story.append(Paragraph("6. Estratégia de Monitoramento Contínuo e Retreinamento (MLOps)", h2_style))
    story.append(Paragraph(
        "• <b>Detecção de Data Drift (Deriva de Dados):</b> Monitoramento de desvio de distribuição nas variáveis contínuas (ex: testes KS para SpO2 e FC) "
        "para identificar mudanças sazonais ou alterações de perfil demográfico na unidade cardiológica;<br/>"
        "• <b>Detecção de Concept Drift:</b> Auditoria periódica cruzando predições com desfechos reais observados (admissões em UTI, óbitos, PCR);<br/>"
        "• <b>Política de Retreinamento:</b> Gatilho automático de retreinamento caso o F1-Score caia abaixo de 95% ou a deriva de features ultrapasse p &lt; 0.05;<br/>"
        "• <b>Auditoria Contínua:</b> Todos os dados de entrada, scores inferidos e protocolos sugeridos são persistidos em <code>data/sessions.db</code>.",
        body_style
    ))

    doc.build(story)
    print(f"Relatório técnico gerado em: {caminho_pdf}")


def main() -> None:
    gerar_pdf_relatorio(PDF_PATH)
    doc_verif = pdfium.PdfDocument(str(PDF_PATH))
    total_paginas = len(doc_verif)
    print(f"Total de páginas no relatório: {total_paginas} (Máximo permitido: 2)")
    if total_paginas > 2:
        print(f"❌ ERRO: O relatório ultrapassou 2 páginas ({total_paginas})!")
        sys.exit(1)
    else:
        print("✅ Validação de páginas concluída com sucesso!")


if __name__ == "__main__":
    main()
