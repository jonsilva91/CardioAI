# Fase 3 — Parte 2: MQTT + Dashboard Node-RED (CardioIA)

## Objetivo

Estender o protótipo de monitoramento cardíaco vestível da **Parte 1** (Edge Computing com buffer offline em RAM) para a camada **Fog/Cloud Computing**, conforme enunciado da Fase 3. O ESP32 simulado no Wokwi passa a publicar cada leitura de sinais vitais (temperatura, umidade, BPM) num **broker MQTT público** (HiveMQ), e um **dashboard Node-RED** subscreve aos tópicos para exibir gráfico, gauge e indicador visual de alerta clínico em tempo real.

O firmware é o **mesmo** da Parte 1 — evoluído in-place no módulo `src/fase03_edge_monitor/` — adicionando Wi-Fi + MQTT como canal de publicação **paralelo** ao Serial CSV existente. Esta pasta (`src/fase03_mqtt_dashboard/`) contém apenas os artefatos **novos** da Parte 2: este relatório, o fluxo Node-RED versionado (`nodered/flow.json`) e as evidências visuais (`screenshots/`).

## Arquitetura

```
  ┌─────────────────┐    Wi-Fi      ┌──────────────────┐   MQTT       ┌─────────────────┐
  │  ESP32 (Wokwi)  │ ───Wokwi───▶ │  HiveMQ Broker   │ ─QoS 1/0────▶ │  Node-RED       │
  │  + DHT22        │   GUEST      │  broker.hivemq   │              │  flow.json      │
  │  + Potenciômetro│              │  .com:1883       │              │  Dashboard:     │
  │  + Buffer 120   │              │                  │              │  ├ chart        │
  │    amostras     │              │  Tópicos:        │              │  ├ gauge        │
  │  + Botão online │              │  cardioai/       │              │  └ ui_text      │
  │  + LED          │              │   <deviceId>/    │              │     (alerta)    │
  └─────────────────┘              │   telemetry      │              └─────────────────┘
                                   │   status (LWT)   │
                                   └──────────────────┘
```

Cada amostra coletada pelo ESP32 é publicada **simultaneamente** em dois canais:
- **Serial Monitor** (canal de debug/Parte 1) — linha CSV `ts,temp,umid,bpm`
- **MQTT** (canal de produção/Parte 2) — payload JSON com timestamp, métricas e flag `buffered`

## Fluxo de comunicação MQTT

### Broker

- **Host**: `broker.hivemq.com`
- **Porta**: `1883` (plaintext)
- **Autenticação**: nenhuma (broker público)
- **TLS**: não usado nesta entrega — ver "Limitações e evolução para produção" abaixo

### Tópicos

| Tópico | Direção | QoS | Retain | Conteúdo |
|---|---|---|---|---|
| `cardioai/<deviceId>/telemetry` | ESP32 → broker | 0\* | false | `{"ts":12345,"temp":24.5,"umid":45.2,"bpm":78,"buffered":false}` |
| `cardioai/<deviceId>/status` | ESP32 → broker | 1 | true | `{"online":true}` ou `{"online":false}` (via LWT) |

\* A biblioteca `PubSubClient` (Nick O'Leary) suporta nativamente apenas QoS 0 em `publish()`. As publicações de telemetria são entregues no modo best-effort. Para QoS 1 real nos publishes, a alternativa é migrar para a biblioteca `arduino-mqtt` (256dpi) ou `AsyncMqttClient` — mantemos PubSubClient pela simplicidade e ampla documentação no ecossistema Arduino. A LWT, o connect e o subscribe seguem QoS 1 normalmente, garantindo a entrega ao menos uma vez nos eventos críticos de estado.

### `deviceId`

Derivado do MAC do ESP32: `String((uint32_t)ESP.getEfuseMac(), HEX)`. Estável entre boots e único entre dispositivos — necessário porque o broker é público e múltiplos alunos podem publicar simultaneamente. O `deviceId` é impresso no Serial logo após a conexão Wi-Fi: `[DEV] deviceId=<id>`.

### Last Will and Testament (LWT)

Ao chamar `mqtt.connect(clientId, "cardioai/<deviceId>/status", 1, true, "{\"online\":false}")`, o broker memoriza a mensagem will. Se o ESP32 cair (queda de Wi-Fi, reset, energia), o broker **automaticamente** publica `{"online":false}` no tópico status. Isso permite ao dashboard saber que o dispositivo ficou offline sem ele ter conseguido se despedir. Logo após uma conexão bem-sucedida, o firmware publica `{"online":true}` (também com retain=true), garantindo que novos subscritores vejam o estado correto.

### Reconnect resiliente

- **Wi-Fi**: verificação a cada 5 s; `WiFi.reconnect()` se desconectado (não-bloqueante).
- **MQTT**: backoff exponencial 1 s → 2 s → 4 s → … → 30 s entre tentativas. Cada tentativa loga `[MQTT] reconectando (tentativa N)`. Ao reconectar com sucesso, **drena automaticamente** o buffer de amostras acumuladas durante a desconexão.

### Resiliência: dois gatilhos de bufferização

O buffer de 120 amostras da Parte 1 continua valendo. Agora bufferiza em **qualquer um** dos cenários:
1. **Botão `online=false`** (offline simulado para a demo da banca)
2. **MQTT desconectado** (`!client.connected()`), mesmo com `online=true` — captura quedas reais de Wi-Fi/broker

Em ambos os casos, ao voltar (`online=true` E `mqtt.connected()=true`), `flushBuffer()` drena todas as amostras pendentes em ordem, publicando cada uma com `"buffered":true` no JSON — o dashboard distingue essa "rajada" de replay dos dados em tempo real.

## Configuração do dashboard Node-RED

### Instalação rápida (avaliador)

```bash
# Instala e roda em uma linha
npx -p node-red node-red

# Em seguida, instalar o pacote de dashboard via Manage Palette:
# Settings → Manage Palette → Install → @flowfuse/node-red-dashboard
```

O Node-RED abre em `http://localhost:1880`. O dashboard fica em `http://localhost:1880/dashboard`.

> **Por que `@flowfuse/node-red-dashboard` e não o `node-red-dashboard` clássico?**
> O pacote clássico foi **descontinuado** pela equipe da FlowFuse (mantenedora oficial do Node-RED). A substituição é o Dashboard 2.0, uma reescrita em Vue com a mesma proposta de widgets prontos. A configuração agora exige uma hierarquia explícita: **`ui-base` → `ui-page` → `ui-group` → widgets**, e os tipos de nó usam hífen (`ui-chart`, `ui-gauge`, `ui-text`) em vez de underscore.

### Import do fluxo

1. Menu (☰ no canto superior direito) → **Import**
2. Selecione **Clipboard** e cole o conteúdo de `src/fase03_mqtt_dashboard/nodered/flow.json`
3. Confirme com **Import**

O fluxo aparece na aba **"CardioAI Fase 3"**.

### Configuração do tópico

Por padrão o fluxo subscreve a `cardioai/+/telemetry` (wildcard `+` captura todos os device-ids). Para acompanhar apenas um dispositivo específico, abra o nó `mqtt in` e troque por `cardioai/<seu-deviceId>/telemetry` — o `deviceId` aparece no Serial Monitor do Wokwi logo após o boot.

### Widgets do dashboard (Dashboard 2.0)

| Widget | Tipo | Métrica | Comportamento |
|---|---|---|---|
| Sinais vitais | `ui-chart` | temperatura + BPM | Line chart com janela de 5 min, **duas séries via `msg.topic`** (topic=`"temp"` ou `"bpm"`, payload numérico) |
| Umidade | `ui-gauge` | umidade relativa | Faixa 0–100%, verde 30–70%, amarelo nas extremidades |
| Status clínico | `ui-text` | alerta | `⚠️ LIMITE ULTRAPASSADO` em vermelho ou `✓ NORMAL` em verde |

Os widgets ficam todos dentro de um `ui-group` ("Sinais Vitais") sob uma `ui-page` ("Monitor") configurada num único `ui-base` com caminho `/dashboard`. Essa estrutura é exportada no `flow.json` e o avaliador não precisa montar nada à mão.

### Função de validação JSON

Um nó `function` após o `mqtt in` verifica a presença dos campos obrigatórios (`temp`, `umid`, `bpm`). Mensagens malformadas são descartadas com `node.warn("payload inválido")`, evitando que widgets renderizem lixo.

### Função de cálculo de alerta

```js
const alerta = (msg.payload.bpm > 120) || (msg.payload.temp > 38);
msg.payload.alerta = alerta;
msg.payload.alertaTexto = alerta
  ? "⚠️ LIMITE ULTRAPASSADO"
  : "✓ NORMAL";
return msg;
```

A lógica vive no Node-RED (não no firmware) propositalmente: **ajustar limites não exige reflashar o ESP32** — vantagem real de arquiteturas Cloud/Fog em saúde digital.

## Limites clínicos: justificativa

| Métrica | Limite | Base |
|---|---|---|
| BPM | > 120 | Taquicardia leve em repouso (SBC, ACC/AHA). Acima desse valor sem esforço justifica acompanhamento. |
| Temperatura corporal | > 38 °C | Febre clínica (definição padrão SBC). Em paciente cardíaco, dispara avaliação de processo infeccioso/inflamatório. |

Em produção, esses limites seriam parametrizáveis por paciente (idade, comorbidades, medicação). Uma evolução natural é adicionar um `ui_slider` no Node-RED para que o clínico ajuste em tempo real.

## Limitações e evolução para produção

| Aspecto | Atual (didático) | Evolução |
|---|---|---|
| TLS | Plaintext em :1883 | HiveMQ Cloud em :8883 com `setCACert(rootCA)` e `setCredentials(user, pass)` |
| Auth | Sem | Username/password (HiveMQ Cloud free tier) ou mTLS (AWS IoT Core) |
| QoS publish | 0 (limitação PubSubClient) | 1 via `arduino-mqtt` (256dpi) ou `AsyncMqttClient` |
| Persistência no dashboard | Memória (5 min na `ui-chart`) | InfluxDB ou TimescaleDB + Grafana |
| Limites de alerta | Hardcoded no function | `ui_slider` parametrizável + persistência por paciente |
| Identidade do dispositivo | MAC | Certificado X.509 individual por device |

Essas evoluções saem do escopo da Fase 3 da disciplina mas estão prontas para serem implementadas em sprints futuros.

## Como executar (resumo end-to-end)

1. **Rodar o ESP32 simulado**: abrir <https://wokwi.com/projects/463852249434716161> e clicar em **Start the simulation**. Aguardar no Serial os logs `[WIFI] conectado`, `[DEV] deviceId=...`, `[MQTT] conectado`.
2. **Rodar o Node-RED localmente**: `npx -p node-red node-red` em outro terminal; abrir `http://localhost:1880`.
3. **Instalar `@flowfuse/node-red-dashboard`** (Dashboard 2.0): Settings → Manage Palette → Install → `@flowfuse/node-red-dashboard`.
4. **Importar o fluxo**: Menu → Import → Clipboard → colar o conteúdo de `nodered/flow.json` → Deploy.
5. **Configurar o tópico** (opcional): abrir o nó `mqtt in` e trocar `cardioai/+/telemetry` por `cardioai/<seu-deviceId>/telemetry` lido do Serial do Wokwi.
6. **Abrir o dashboard**: `http://localhost:1880/dashboard`.
7. **Demonstrar os cenários**:
   - Real-time: girar o potenciômetro até `bpm > 120` → o `ui_text` vira vermelho.
   - Real-time: no Wokwi clicar no DHT22 e setar `temperature: 39` → alerta dispara também por febre.
   - Offline buffering: clicar o botão (LED apaga), esperar 30 s, clicar de novo (LED acende) → "rajada" de pontos com `buffered:true` chega no chart.
   - LWT: parar a simulação abruptamente no Wokwi e observar via `mosquitto_sub -h broker.hivemq.com -t 'cardioai/+/status'` que `{"online":false}` é entregue pelo broker.

## Evidências visuais

Capturas de tela versionadas em [`screenshots/`](screenshots/):

- `dashboard-normal.png` — dashboard recebendo dados em tempo real, estado normal
- `dashboard-alerta.png` — alerta clínico disparado por bpm ou temp acima do limite
- `flow-editor.png` — fluxo Node-RED completo no editor

## Referências cruzadas

- **Firmware**: [`src/fase03_edge_monitor/sketch.ino`](../fase03_edge_monitor/sketch.ino) (mesmo módulo da Parte 1, evoluído)
- **Relatório da Parte 1**: [`src/fase03_edge_monitor/RELATORIO.md`](../fase03_edge_monitor/RELATORIO.md)
- **Wokwi público**: <https://wokwi.com/projects/463852249434716161>
- **Fluxo Node-RED**: [`nodered/flow.json`](nodered/flow.json)
