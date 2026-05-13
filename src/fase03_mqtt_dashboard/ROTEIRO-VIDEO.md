# Roteiro do vídeo — CardioIA Fase 3 (≤ 5 min)

## Antes de gravar

Abra em janelas separadas:
1. Wokwi rodando — <https://wokwi.com/projects/463852249434716161>
2. Node-RED dashboard — <http://localhost:1880/dashboard>
3. README.md do repo (para o fechamento)

---

## Roteiro

### 1. Abertura (0:00 – 0:20)

**Tela:** README do projeto

> "Grupo CardioIA — João Vitor, Jonas e Edson. Fase 3: protótipo de monitoramento cardíaco vestível em ESP32, com Edge Computing, transmissão MQTT à nuvem e dashboard Node-RED com alertas clínicos. Tudo simulado no Wokwi."

### 2. Arquitetura (0:20 – 0:45)

**Tela:** diagrama do RELATORIO.md

> "A cada 5 s o ESP32 lê DHT22 (temp e umidade) e potenciômetro (BPM 40–180). Cada amostra sai em dois canais: CSV no Serial e JSON via MQTT no HiveMQ. Um Node-RED local assina e renderiza o dashboard."

### 3. Parte 1 — Edge no Wokwi (0:45 – 2:00)

**Tela:** Wokwi + Serial Monitor

> "Circuito: ESP32, DHT22, potenciômetro, botão e LED. No Serial: cabeçalho CSV, `[WIFI] conectado`, `[DEV] deviceId`, `[MQTT] conectado`, e as amostras CSV a cada 5 s."

**▶ Aperta o botão (offline):**
> "Offline. As linhas param. As amostras estão indo para um buffer circular em RAM — 120 amostras, ~10 min de cobertura offline."

**Espera 20–25 s, aperta de novo:**
> "Online. Vejam a rajada de linhas CSV drenadas e o `[FLUSH] enviadas N amostras, buffer=0`. Resiliência funcionando."

### 4. Parte 2 — Cloud + Dashboard (2:00 – 3:30)

**Tela:** Node-RED dashboard

> "Mesma simulação, agora pela ótica da nuvem. Chart com temp + BPM, gauge de umidade, indicador de status clínico. Tudo chegando via MQTT desde o ESP32."

**▶ Gira o potenciômetro para BPM > 120:**
> "BPM passa de 120 → status vira `⚠️ LIMITE ULTRAPASSADO`. A regra de alerta vive no Node-RED, não no firmware — ajustar limites não exige reflashar o ESP32."

**▶ Clica no DHT22, seta `temperature: 39`:**
> "Alerta dispara também pela via de temperatura. Limites: `bpm > 120` (taquicardia) ou `temp > 38` (febre), conforme diretrizes SBC."

### 5. Pontos técnicos (3:30 – 4:20)

**Tela:** sketch.ino ou flow.json

> "PubSubClient + ArduinoJson. Payload JSON com timestamp, métricas e flag `buffered`. Last Will armado: se o ESP32 cair, o broker publica `online:false` sozinho. Reconnect com backoff exponencial. Node-RED usa o Dashboard 2.0 da FlowFuse (`ui-base → ui-page → ui-group → widgets`), com séries via `msg.topic` e função JSON para o alerta. Tudo versionado no `flow.json`."

### 6. Fechamento (4:20 – 4:50)

**Tela:** README com seção Fase 3

> "No repo: link Wokwi, dois relatórios técnicos, fluxo Node-RED versionado, três screenshots e código C++ comentado. Firmware único, Parte 2 adicionada in-place sobre a Parte 1 com Serial CSV preservado. Obrigado!"

---

## Dicas

- Fale calmo — 130 a 150 palavras/min, não 200.
- Bloco 5 é o cortável se passar do tempo: vire numa frase só.
- Termine 5–10 s antes do limite para margem.
- Gravação em uma tomada só evita edição. Se errar, pausa 3 s, repete, corta depois.
