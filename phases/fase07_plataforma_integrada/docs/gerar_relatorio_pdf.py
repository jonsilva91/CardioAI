"""Gera o Relatório Técnico da Fase 7 em PDF (máximo de 5 páginas) e valida a contagem de páginas."""

from __future__ import annotations

from pathlib import Path
import shutil
import sys
import pypdfium2 as pdfium
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DOCS_DIR = Path(__file__).resolve().parent
PRINTS_DIR = DOCS_DIR / "prints"
PDF_PATH = DOCS_DIR / "relatorio_tecnico_fase07.pdf"
DIAG_PATH = DOCS_DIR / "diagrama_arquitetura_final.png"
REPO_ROOT = DOCS_DIR.parent.parent.parent


def gerar_pdf() -> int:
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=34,
        rightMargin=34,
        topMargin=28,
        bottomMargin=28,
    )

    styles = getSampleStyleSheet()
    title_st = ParagraphStyle(
        "T",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14.5,
        leading=18,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=3,
    )
    meta_st = ParagraphStyle(
        "M",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )
    h2_st = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12.5,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=5,
        spaceAfter=3,
    )
    body_st = ParagraphStyle(
        "B",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.6,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=3,
    )
    th_st = ParagraphStyle(
        "TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.4,
        leading=9.2,
        textColor=colors.white,
    )
    td_st = ParagraphStyle(
        "TD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.3,
        leading=9.2,
        textColor=colors.HexColor("#1f2937"),
    )

    story = []

    # PÁGINA 1: Objetivo, Links, Diagrama de Arquitetura e Fluxo Ponta a Ponta
    story.append(
        Paragraph("Relatório Técnico — Fase 7: Plataforma Integrada CardioAI", title_st)
    )
    story.append(
        Paragraph(
            "<b>FIAP — Faculdade de Informática e Administração Paulista</b> | "
            "<b>Integrantes:</b> Jonas Luis da Silva (RM561465) &amp; Edson Henrique Felix Batista (RM566321)<br/>"
            "<b>Portal (Vercel):</b> https://cardio-ai-five.vercel.app | "
            "<b>Backend (Render):</b> https://cardioai-fase07-backend.onrender.com (/docs, /health)<br/>"
            "<b>Build APK (EAS):</b> https://expo.dev/accounts/jonsilva91/projects/mobile-cardioia/builds/be64508a-ebc2-4fb2-9ab3-93a89bb8b267<br/>"
            "<b>Projeto Wokwi (MicroPython):</b> https://wokwi.com/projects/480500031706588161 | "
            "<b>Login Demo (Sintético):</b> demo@cardioia.com / CardioIA@2026 (Paciente: PAC-001)",
            meta_st,
        )
    )

    story.append(Paragraph("1. Objetivo da Fase 7", h2_st))
    story.append(
        Paragraph(
            "Consolidar os módulos desenvolvidos nas fases anteriores do ecossistema <b>CardioAI</b> em uma plataforma "
            "integrada de ponta a ponta em nuvem, conectando um dispositivo de borda IoT (<b>ESP32 em MicroPython no Wokwi</b>), "
            "um <b>Backend FastAPI no Render</b> que importa diretamente o modelo preditivo Random Forest (99,9% de acurácia), os "
            "protocolos clínicos determinísticos e o sistema multiagente (<code>OpenAI Agents SDK</code>) da Fase 6, um assistente "
            "conversacional de triagem (<code>gpt-4o-mini</code>), o <b>Portal Web React/Vite na Vercel</b> e o <b>App Mobile Android (APK via EAS Build)</b>.",
            body_st,
        )
    )

    story.append(Paragraph("2. Diagrama de Arquitetura Final", h2_st))
    if DIAG_PATH.exists():
        story.append(Image(str(DIAG_PATH), width=515, height=340))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3. Fluxo dos Dados Ponta a Ponta", h2_st))
    story.append(
        Paragraph(
            "• <b>1. Coleta e Pré-Análise Edge (Wokwi ESP32):</b> A cada 5 s (ou ao pressionar o botão no GPIO 15), o ESP32 lê a "
            "temperatura no DHT22 (GPIO 4), o BPM (40–180) no potenciômetro 1 (GPIO 34) e a SpO2 (80–100%) no potenciômetro 2 (GPIO 35), "
            "executa pré-análise local (<code>BPM &gt; 120</code>, <code>SpO2 &lt; 92</code>, <code>temp &gt; 38 °C</code>) e atualiza o OLED SSD1306 I2C.<br/>"
            "• <b>2. Ingestão Segura (<code>POST /api/telemetria</code>):</b> Envia JSON com <code>paciente_id='PAC-001'</code> e header <code>X-Device-Token</code>.<br/>"
            "• <b>3. Inferência ML + Protocolos (Fase 6):</b> O backend completa as 3 leituras do sensor com as 7 variáveis do "
            "<code>CENARIO_PADRAO</code> (totalizando as 10 features), executa <code>src.predictor.prever_risco</code> e <code>src.protocols.consultar_protocolos</code>, "
            "guarda nas últimas 200 leituras em memória e devolve <code>{probabilidade, classificacao, alerta, protocolos}</code>.<br/>"
            "• <b>4. Retorno ao Dispositivo IoT:</b> O ESP32 exibe <code>'Risco 0.xx ALTO'</code> no OLED e controla os LEDs: vermelho (GPIO 5) se "
            "<code>ALTO</code>/alerta, verde (GPIO 2) se <code>BAIXO</code> e pisca se <code>MODERADO</code>.<br/>"
            "• <b>5. Consumo Web/Mobile e IA Sob Demanda:</b> Portal (Vercel) e App (APK) autenticam via JWT (<code>POST /api/auth/login</code>), "
            "fazem polling a cada 5 s em <code>/status</code> e <code>/historico</code>, e acionam sob demanda os 4 agentes em <code>POST /api/pacientes/PAC-001/recomendacao</code> "
            "e o assistente de triagem em <code>POST /api/chat</code>.",
            body_st,
        )
    )

    # PÁGINA 2: Decisões Arquiteturais, Deploy & CI/CD, Segurança/LGPD e Tabela C++ -> MicroPython
    story.append(PageBreak())

    story.append(Paragraph("4. Decisões Arquiteturais", h2_st))
    story.append(
        Paragraph(
            "• <b>HTTP REST (<code>urequests</code>) em vez de MQTT:</b> Permite que a própria resposta HTTP síncrona de <code>POST /api/telemetria</code> "
            "retorne o score calculado pelo modelo Random Forest na nuvem diretamente para o ESP32 comandar os LEDs e o display OLED, "
            "eliminando a dependência de brokers MQTT públicos intermediários.<br/>"
            "• <b>Polling de 5 s nos Clientes:</b> Sincronizado ao ciclo de 5 s do ESP32, exibindo idade da leitura em segundos ('Ao vivo / sem dados há X s') "
            "e reconectando automaticamente após hibernação do container.<br/>"
            "• <b>LLM e Agentes Apenas Sob Demanda (Controle de Custos):</b> A telemetria contínua a cada 5 s utiliza apenas o Random Forest "
            "(inferência local em microssegundos, custo zero). O pipeline de 4 agentes (<code>OpenAI Agents SDK</code>) e o chat (<code>gpt-4o-mini</code>) "
            "só rodam quando solicitados pelo usuário, com <i>rate-limit</i> de 1 chamada a cada 30 s por paciente (<code>HTTP 429</code>).<br/>"
            "• <b>Sensores + Cenário Padrão ➔ 10 Features:</b> Combina <code>fc_media</code>, <code>temperatura</code> e <code>spo2_media</code> enviados pelo "
            "ESP32 com o baseline hospitalar (<code>idade_media=62</code>, <code>carga_sistema=60</code>, <code>tempo_espera=40</code>, <code>pa_sistolica=120</code>, "
            "<code>densidade_eventos=3</code>, <code>eventos_24h=2</code>, <code>disponibilidade_recursos=60</code>), reutilizando o modelo da Fase 6 sem cópia de código.<br/>"
            "• <b>Edge com Pré-Análise Local e Fila de 20 Leituras:</b> Se o backend estiver acordando, o ESP32 sinaliza alertas locais na borda "
            "e armazena até 20 leituras em fila FIFO em RAM para envio posterior.",
            body_st,
        )
    )

    story.append(Paragraph("5. Deploy em Nuvem e CI/CD", h2_st))
    story.append(
        Paragraph(
            "• <b>Vercel (Portal React/Vite):</b> Deploy automático a cada push no GitHub. O arquivo <code>apps/portal-cardioia/vercel.json</code> "
            "aplica rewrite SPA de todas as rotas para <code>/index.html</code> e consome <code>VITE_API_URL</code>.<br/>"
            "• <b>Render (Backend FastAPI):</b> Definido via Blueprint em <code>render.yaml</code> na raiz (plano Free, <code>healthCheckPath: /health</code>) "
            "com <code>buildFilter.paths</code> restrito ao backend da Fase 7, código/modelo da Fase 6 e <code>render.yaml</code>.<br/>"
            "• <b>Expo EAS Build (APK Android):</b> Atualizado do SDK 49 para o <b>Expo SDK 58</b> (20/20 checks no <code>expo-doctor</code>), "
            "<code>android.package: 'br.com.fiap.cardioia'</code>, <code>versionCode: 1</code> e perfil <code>preview</code> gerando APK instalável.",
            body_st,
        )
    )

    story.append(Paragraph("6. Segurança, Variáveis de Ambiente e LGPD", h2_st))
    story.append(
        Paragraph(
            "• <b>Zero Segredos no Código:</b> <code>JWT_SECRET</code>, <code>DEVICE_TOKEN</code>, <code>DEMO_EMAIL</code>, <code>DEMO_PASSWORD</code> e "
            "<code>OPENAI_API_KEY</code> residem apenas nas variáveis de ambiente. O backend falha no startup (<code>RuntimeError</code>) se alguma "
            "variável obrigatória estiver ausente. <code>GET /health</code> informa apenas um booleano (<code>openai_api_key: true/false</code>).<br/>"
            "• <b>Autenticação e CORS:</b> Rotas clínicas exigem <code>Authorization: Bearer &lt;JWT&gt;</code> (salvo no <code>expo-secure-store</code> no mobile); "
            "a ingestão IoT exige <code>X-Device-Token</code> validado com <code>hmac.compare_digest</code>; o CORS aceita apenas <code>ALLOWED_ORIGINS</code>.<br/>"
            "• <b>LGPD e Ética Médica:</b> Uso exclusivo de dados sintéticos (<code>PAC-001</code>) e disclaimer fixo <i>'Não substitui avaliação médica.'</i>.",
            body_st,
        )
    )

    story.append(Paragraph("7. Conversão C++ (Fase 3) ➔ MicroPython (Fase 7)", h2_st))
    t_conv_data = [
        [
            Paragraph("<b>Camada / Recurso</b>", th_st),
            Paragraph("<b>Fase 3 — C++ (sketch.ino)</b>", th_st),
            Paragraph("<b>Fase 7 — MicroPython (iot/main.py)</b>", th_st),
        ],
        [
            Paragraph("Transporte de Rede", td_st),
            Paragraph("<code>PubSubClient</code> / MQTT (HiveMQ)", td_st),
            Paragraph("<code>urequests.post</code> / HTTPS REST (<code>X-Device-Token</code>)", td_st),
        ],
        [
            Paragraph("Sensor Temperatura", td_st),
            Paragraph("<code>#include &lt;DHT.h&gt;</code> / <code>dht.readTemperature()</code>", td_st),
            Paragraph("<code>import dht</code> / <code>dht.DHT22(Pin(4)).temperature()</code>", td_st),
        ],
        [
            Paragraph("Leitura Analógica", td_st),
            Paragraph("<code>analogRead(34)</code> + <code>map(...)</code> (BPM)", td_st),
            Paragraph("<code>ADC(Pin(34/35)).read()</code> (BPM 40–180 e SpO2 80–100%)", td_st),
        ],
        [
            Paragraph("GPIO Digital", td_st),
            Paragraph("<code>digitalWrite</code> / <code>digitalRead</code>", td_st),
            Paragraph("<code>Pin.value(1/0)</code> / <code>Pin(15, Pin.IN, Pin.PULL_UP)</code>", td_st),
        ],
        [
            Paragraph("Saída Local Edge", td_st),
            Paragraph("Monitor Serial CSV (<code>Serial.printf</code>)", td_st),
            Paragraph("Display <b>OLED SSD1306 I2C</b> (<code>ssd1306.py</code>) + LEDs Verde/Vermelho", td_st),
        ],
    ]
    t_conv = Table(t_conv_data, colWidths=[120, 190, 215])
    t_conv.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f8fafc")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_conv)

    # PÁGINA 3: Resultados Observados, Limitações, Próximos Passos e Evidências Visuais
    story.append(PageBreak())

    story.append(Paragraph("8. Resultados Observados em Produção", h2_st))
    t_res_data = [
        [
            Paragraph("<b>Cenário (PAC-001)</b>", th_st),
            Paragraph("<b>Leituras Enviadas</b>", th_st),
            Paragraph("<b>Risco Predito</b>", th_st),
            Paragraph("<b>Protocolos Acionados e Comportamento Observado</b>", th_st),
        ],
        [
            Paragraph("1. Taquicardia com SpO2 100%", td_st),
            Paragraph("BPM = 180<br/>SpO2 = 100%<br/>Temp = 36.6 °C", td_st),
            Paragraph("<b>0.18 (18%)<br/>BAIXO</b>", td_st),
            Paragraph(
                "1 protocolo individual (<code>Se FC &gt; 120 → iniciar monitoramento intensivo</code>). Com SpO2 em 100% e cenário basal moderado, o Random Forest classifica 18% (BAIXO).",
                td_st,
            ),
        ],
        [
            Paragraph("2. Descompensação Combinada", td_st),
            Paragraph("BPM = 180<br/>SpO2 = 80%<br/>Temp = 36.6 °C", td_st),
            Paragraph("<b>0.86 (86%)<br/>ALTO</b>", td_st),
            Paragraph(
                "<b>3 protocolos acionados</b>: (1) <code>SPO2 &lt; 88% → suporte respiratório</code>; (2) <code>FC &gt; 120 → monitoramento intensivo</code>; (3) <code>risco alto → estado de emergência</code>. OLED mostra <code>Risco 0.86 ALTO</code> e LED vermelho acende.",
                td_st,
            ),
        ],
        [
            Paragraph("3. Paciente Basal Estável", td_st),
            Paragraph("BPM = 75<br/>SpO2 = 98%<br/>Temp = 36.5 °C", td_st),
            Paragraph("<b>0.00 (0%)<br/>BAIXO</b>", td_st),
            Paragraph(
                "0 protocolos acionados. OLED exibe <code>Risco 0.00 BAIXO</code> e LED verde permanece aceso.",
                td_st,
            ),
        ],
    ]
    t_res = Table(t_res_data, colWidths=[105, 85, 75, 260])
    t_res.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f8fafc")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(t_res)
    story.append(Spacer(1, 4))

    story.append(Paragraph("9. Limitações Conhecidas e Mitigações", h2_st))
    story.append(
        Paragraph(
            "• <b>Cold Start no Render Free (~50 s):</b> O serviço hiberna após inatividade; tratado com aviso <i>'Servidor acordando, aguarde'</i> no portal e fila no ESP32.<br/>"
            "• <b>Histórico em Memória (200 leituras/paciente):</b> Armazenado em <code>deque(maxlen=200)</code>, volátil em redeploys.<br/>"
            "• <b>Quedas Ocasionais de TLS no Wokwi:</b> Contornadas pela fila local de até 20 leituras e reconexão automática no MicroPython.<br/>"
            "• <b>CNN de ECG (Fase 4) Fora do Deploy:</b> TensorFlow removido do backend integrado para caber nos 512 MB de RAM do Render Free.<br/>"
            "• <b>Dados Sintéticos e Emulação Android:</b> Dados 100% sintéticos. A validação do APK foi realizada no emulador <b>Android Pixel 7 / Android 13 via Appetize.io</b> (pois o integrante utiliza iOS), além da validação do build no EAS.",
            body_st,
        )
    )

    story.append(Paragraph("10. Próximos Passos", h2_st))
    story.append(
        Paragraph(
            "• Persistência em <b>PostgreSQL/TimescaleDB</b> e cache <b>Redis</b> para múltiplos workers; streaming via <b>WebSockets/SSE</b>; "
            "conversão da CNN da Fase 4 para <b>ONNX Runtime</b>; e prototipagem física com sensores biomédicos <b>MAX30102</b> e <b>DS18B20</b>.",
            body_st,
        )
    )

    story.append(
        Paragraph(
            "11. Evidências de Produção (Wokwi, Portal Vercel e APK no Appetize.io)",
            h2_st,
        )
    )
    imgs_row = []
    for fn, lbl in [
        ("wokwi.png", "Wokwi ESP32 MicroPython"),
        ("portal_monitoramento.png", "Portal Vercel (/monitoramento)"),
        ("apk_appetize.png", "APK Android 13 (Appetize.io)"),
    ]:
        p = PRINTS_DIR / fn
        if p.exists():
            imgs_row.append(
                [
                    Image(str(p), width=165, height=105),
                    Paragraph(f"<b>{lbl}</b> (<code>{fn}</code>)", td_st),
                ]
            )

    if imgs_row:
        t_imgs = Table(
            [[x[0] for x in imgs_row], [x[1] for x in imgs_row]],
            colWidths=[175, 175, 175],
        )
        t_imgs.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        story.append(t_imgs)

    doc.build(story)
    shutil.copy2(PDF_PATH, REPO_ROOT / "docs" / "relatorio_tecnico_fase07.pdf")

    pdf_doc = pdfium.PdfDocument(str(PDF_PATH))
    num_pages = len(pdf_doc)
    print(
        f"PDF gerado com sucesso: {PDF_PATH} | Total de paginas: {num_pages} (Maximo permitido: 5)"
    )
    if num_pages > 5:
        sys.exit(1)
    return num_pages


if __name__ == "__main__":
    gerar_pdf()

