"""Gerador do relatório técnico em PDF (máx. 2 páginas) para a atividade Ir Além 2."""

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
PDF_PATH = CURRENT_DIR / "relatorio_ir_alem_2.pdf"


def gerar_pdf(caminho_pdf: Path = PDF_PATH) -> int:
    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=26,
        bottomMargin=26
    )

    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        "RelTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=15.5,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=2
    )
    subtitulo_style = ParagraphStyle(
        "RelSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=2
    )
    meta_style = ParagraphStyle(
        "RelMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor("#475569"),
        spaceAfter=5
    )
    h2_style = ParagraphStyle(
        "RelH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=9.2,
        leading=11.5,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=3,
        spaceAfter=2
    )
    body_style = ParagraphStyle(
        "RelBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.3,
        leading=9.8,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=3
    )
    callout_style = ParagraphStyle(
        "RelCallout",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.0,
        leading=9.2,
        textColor=colors.HexColor("#0f172a")
    )
    table_cell = ParagraphStyle(
        "RelTableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_header = ParagraphStyle(
        "RelTableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.9,
        leading=8.7,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # PÁGINA 1
    # =========================================================================
    story.append(Paragraph("CardioAI — Relatório Técnico de Escalabilidade e Otimização", titulo_style))
    story.append(Paragraph("Desafio Ir Além 2: Processamento Assíncrono, Fila de Mensagens e Arquitetura Distribuída", subtitulo_style))
    story.append(Paragraph(
        "<b>FIAP</b> — Fase 6: Coração Sob Controle | <b>Disciplina:</b> Otimização e Escalabilidade de Sistemas de IA (Cluster Computing)<br/>"
        "<b>Integrantes:</b> Jonas Luis da Silva (RM561465) & Edson Henrique Felix Batista (RM566321)",
        meta_style
    ))

    story.append(Paragraph("1. Organização Modular Existente e Desacoplamento Técnico", h2_style))
    story.append(Paragraph(
        "O sistema CardioAI foi concebido de forma modular e desacoplada, separando nitidamente a inferência preditiva, o motor de regras, "
        "o quarteto de agentes e a persistência de sessões (conforme ilustrado em <code>docs/diagrama_modulos.png</code>):<br/>"
        "• <b>Módulo Preditivo (<code>src/predictor.py</code>):</b> Carrega o artefato <code>models/modelo_pico_risco.joblib</code> (Random Forest de 200 árvores, "
        "n_samples=5.000). Executa normalização de features com tratamento de espaços, validação estrita das 10 variáveis e inferência de probabilidade.<br/>"
        "• <b>Motor de Protocolos Clínicos (<code>src/protocols.py</code>):</b> Base institucional com 10 diretrizes hospitalares oficiais avaliadas de forma "
        "determinística (<code>consultar_protocolos</code>) para sinais vitais (SpO2 &lt; 88%, FC &gt; 120 bpm, PA &lt; 90) e operacionais (carga &gt; 85%, espera &gt; 90 min).<br/>"
        "• <b>Sistema Multiagente (<code>src/agents_system/cardio_agents.py</code>):</b> Agentes Orquestrador, Analista de Risco, Especialista em Protocolos e Planejador "
        "conectados por handoffs nativos assíncronos do OpenAI Agents SDK, protegidos por <code>OutputGuardrailTripwireTriggered</code>.<br/>"
        "• <b>Orquestração e Persistência (<code>src/agents_system/main.py</code>):</b> Interface CLI com isolamento contextual (<code>CardioContext</code>) e sessões em <code>SQLiteSession</code>.",
        body_style
    ))

    story.append(Paragraph("2. Estratégia de Simulação de Concorrência e Alta Carga (`fila_pacientes.py`)", h2_style))
    story.append(Paragraph(
        "Para simular picos hospitalares de triagem, o módulo <code>fila_pacientes.py</code> adota uma esteira assíncrona orientada a eventos:<br/>"
        "• <b>Fila Assíncrona (<code>asyncio.Queue</code>):</b> Ingestão contínua de <i>N</i> pacientes sintéticos gerados por <code>src.data_generation</code> (com semente configurável).<br/>"
        "• <b>Pool de <i>W</i> Workers Concorrentes:</b> Corrotinas paralelas consumindo a fila e executando o pipeline via <code>Runner.run</code> assíncrono.<br/>"
        "• <b>Controle de Resiliência:</b> <code>asyncio.Semaphore</code> para respeitar cotas de chamadas simultâneas à API; timeout individual configurável por paciente; "
        "retry automático com backoff exponencial ($1.0 \\times 2^{tentativa-1}$) em falhas transitórias de rede/rate limit; e isolamento de erros sem derrubar a fila.<br/>"
        "• <b>Modo Lote Vetorizado (<code>--lote</code>):</b> Agrega todas as amostras em lote matricial e invoca <code>predict_proba</code> do Scikit-Learn de forma vetorizada.",
        body_style
    ))

    story.append(Paragraph("3. Resultados Reais do Benchmark de Escalabilidade (`benchmark.py`)", h2_style))
    story.append(Paragraph(
        "A tabela a seguir consolida as medições reais obtidas no ambiente de testes (registradas em <code>resultados/benchmark.csv</code> e <code>resultados/benchmark.png</code>):",
        body_style
    ))

    # Tabela de benchmark
    tabela_bench_dados = [
        [
            Paragraph("Cenário de Teste", table_header),
            Paragraph("Pacientes", table_header),
            Paragraph("Workers", table_header),
            Paragraph("Tempo Total", table_header),
            Paragraph("Média/Pac", table_header),
            Paragraph("Throughput", table_header),
            Paragraph("Erros", table_header)
        ],
        [
            Paragraph("Fila (1w) — Sem LLM", table_cell), Paragraph("1.000", table_cell), Paragraph("1", table_cell),
            Paragraph("14,09 s", table_cell), Paragraph("14,1 ms", table_cell), Paragraph("70,99 pac/s", table_cell), Paragraph("0,0%", table_cell)
        ],
        [
            Paragraph("Fila (2w) — Sem LLM", table_cell), Paragraph("1.000", table_cell), Paragraph("2", table_cell),
            Paragraph("10,92 s", table_cell), Paragraph("21,8 ms", table_cell), Paragraph("91,58 pac/s", table_cell), Paragraph("0,0%", table_cell)
        ],
        [
            Paragraph("Fila (4w) — Sem LLM", table_cell), Paragraph("1.000", table_cell), Paragraph("4", table_cell),
            Paragraph("13,40 s", table_cell), Paragraph("53,5 ms", table_cell), Paragraph("74,62 pac/s", table_cell), Paragraph("0,0%", table_cell)
        ],
        [
            Paragraph("Fila (8w) — Sem LLM", table_cell), Paragraph("1.000", table_cell), Paragraph("8", table_cell),
            Paragraph("12,76 s", table_cell), Paragraph("101,8 ms", table_cell), Paragraph("78,38 pac/s", table_cell), Paragraph("0,0%", table_cell)
        ],
        [
            Paragraph("<b>Lote Vetorizado (Batch ML)</b>", table_cell), Paragraph("<b>1.000</b>", table_cell), Paragraph("<b>1</b>", table_cell),
            Paragraph("<b>0,0128 s</b>", table_cell), Paragraph("<b>&lt; 0,1 ms</b>", table_cell), Paragraph("<b>77.935,6 pac/s</b>", table_cell), Paragraph("<b>0,0%</b>", table_cell)
        ],
        [
            Paragraph("Multiagente (1w) — LLM Real", table_cell), Paragraph("10", table_cell), Paragraph("1", table_cell),
            Paragraph("85,13 s", table_cell), Paragraph("8,51 s", table_cell), Paragraph("0,12 pac/s", table_cell), Paragraph("0,0%", table_cell)
        ],
        [
            Paragraph("Multiagente (2w) — LLM Real", table_cell), Paragraph("10", table_cell), Paragraph("2", table_cell),
            Paragraph("40,28 s", table_cell), Paragraph("7,87 s", table_cell), Paragraph("0,25 pac/s", table_cell), Paragraph("0,0%", table_cell)
        ],
        [
            Paragraph("<b>Multiagente (4w) — LLM Real</b>", table_cell), Paragraph("<b>10</b>", table_cell), Paragraph("<b>4</b>", table_cell),
            Paragraph("<b>23,50 s</b>", table_cell), Paragraph("<b>8,64 s</b>", table_cell), Paragraph("<b>0,43 pac/s</b>", table_cell), Paragraph("<b>0,0%</b>", table_cell)
        ],
    ]

    t_bench = Table(tabela_bench_dados, colWidths=[135, 52, 45, 65, 65, 85, 45])
    t_bench.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_bench)

    # Quebra obrigatória para a página 2
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2
    # =========================================================================
    story.append(Paragraph("4. Diagnóstico do Gargalo Computacional: ML Local vs LLM Remoto", h2_style))

    box_gargalo = (
        "<b>Conclusão Crítica do Benchmark & Correção do Harness de Testes:</b><br/>"
        "• <b>Sem LLM (Gargalo de CPU & GIL):</b> 2w aumentaram o throughput (71 ➔ 92 pac/s), mas 4w e 8w estagnaram (75 e 78 pac/s) "
        "devido à contenção do GIL no Random Forest. Solução ideal: <b>Lote Vetorizado</b> (77.935 pac/s) ou <i>multiprocessing</i>.<br/>"
        "• <b>Com LLM (Escala Concorrente):</b> A expansão para 4 workers reduziu o tempo total de <b>85,13s para 23,50s</b> (aceleração de <b>3,62x</b>), "
        "comprovando a eficácia do <code>asyncio</code> em sobrepor tempos ociosos de I/O de rede.<br/>"
        "• <b>Diagnóstico e Correção da Taxa de Erro:</b> Na primeira medição houve 10% de falha causada por um bug do próprio harness "
        "(event loop reutilizado e fechado entre chamadas de <code>asyncio.run()</code>, gerando <code>Event loop is closed</code>). "
        "O bug foi corrigido executando as rodadas em um único loop, e a nova medição teve <b>0,0% de erro</b> (100% de sucesso e 0 bloqueios de guardrails)."
    )
    t_gargalo = Table([[Paragraph(box_gargalo, callout_style)]], colWidths=[540])
    t_gargalo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#16a34a")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_gargalo)
    story.append(Spacer(1, 3))

    story.append(Paragraph("5. Arquitetura Distribuída para Ambientes de Alta Escala (Cluster Computing)", h2_style))
    story.append(Paragraph(
        "A partir dos gargalos diagnosticados, projeta-se a evolução do CardioAI para uma topologia corporativa distribuída "
        "(detalhada no diagrama arquitetural <code>docs/diagrama_distribuido.png</code>):",
        body_style
    ))

    # Tabela de Componentes da Arquitetura Distribuída
    dados_dist = [
        [
            Paragraph("Camada da Arquitetura", table_header),
            Paragraph("Tecnologia Proposta", table_header),
            Paragraph("Papel Técnico e Impacto na Escalabilidade", table_header)
        ],
        [
            Paragraph("<b>API Gateway Stateless</b>", table_cell),
            Paragraph("FastAPI + NGINX Ingress<br/>(Container Docker)", table_cell),
            Paragraph("Recebe eventos hospitalares (PEP/IoT), valida esquemas Pydantic e enfileira as mensagens de triagem sem reter conexões abertas, permitindo escala horizontal sem estado.", table_cell)
        ],
        [
            Paragraph("<b>Fila de Mensagens Real</b>", table_cell),
            Paragraph("RabbitMQ / Apache Kafka<br/>/ Redis Streams", table_cell),
            Paragraph("Buffer elástico de absorção de picos de demanda com particionamento por prioridade clínica de atendimento e Dead Letter Queue (DLQ) para tratamento de anomalias sem perda de dados.", table_cell)
        ],
        [
            Paragraph("<b>Workers em Cluster K8s</b>", table_cell),
            Paragraph("Kubernetes HPA<br/>+ KEDA Autoscaler", table_cell),
            Paragraph("Pool elástico de pods executando os agentes do OpenAI Agents SDK. O HPA provisiona instâncias dinamicamente com base no tamanho da fila e consumo de CPU, otimizando custo computacional.", table_cell)
        ],
        [
            Paragraph("<b>Model Serving Desacoplado</b>", table_cell),
            Paragraph("Triton Inference Server<br/>/ TorchServe / FastAPI ML", table_cell),
            Paragraph("Isola o modelo Random Forest em microserviço dedicado com suporte a predição vetorizada em batching dinâmico via gRPC, liberando os workers de agentes de carregar pesos localmente.", table_cell)
        ],
        [
            Paragraph("<b>Cache de Predições</b>", table_cell),
            Paragraph("Redis Cluster (In-Memory)", table_cell),
            Paragraph("Armazena em cache (TTL de 60s) scores de sinais vitais estáveis de pacientes em monitoramento contínuo em leitos, evitando execuções repetidas do modelo e dos agentes.", table_cell)
        ],
        [
            Paragraph("<b>Estado e Sessões Compartilhadas</b>", table_cell),
            Paragraph("PostgreSQL + Redis<br/>(substituindo SQLite)", table_cell),
            Paragraph("Migração do SQLite local para banco relacional distribuído com réplicas de leitura e locks em Redis, permitindo que perguntas interativas sejam atendidas por qualquer worker do cluster.", table_cell)
        ],
        [
            Paragraph("<b>Observabilidade Completa</b>", table_cell),
            Paragraph("Prometheus, Grafana,<br/>OpenTelemetry & Jaeger", table_cell),
            Paragraph("Monitoramento em tempo real de taxas de throughput, latência P95/P99, tamanho da fila e distributed tracing completo para rastrear cada handoff do sistema multiagente.", table_cell)
        ],
    ]

    t_dist = Table(dados_dist, colWidths=[110, 105, 325])
    t_dist.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_dist)
    story.append(Spacer(1, 3))

    story.append(Paragraph(
        "<b>Conclusão:</b> A modularidade do CardioAI e a estratégia de desacoplamento entre inferência em lote (ML) e consumo assíncrono em fila (LLM) "
        "viabilizam a transição segura para ambientes corporativos distribuídos e supercomputadores hospitalares de alta performance.",
        body_style
    ))

    doc.build(story)

    # Validação do número de páginas
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
