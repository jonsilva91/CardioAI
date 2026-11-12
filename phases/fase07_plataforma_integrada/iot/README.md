# 📡 Nó IoT MicroPython (ESP32) — CardioIA Fase 7

Conversão evolutiva do firmware de monitoramento de borda da Fase 3 (`src/fase03_edge_monitor/sketch.ino` em C++/Arduino) para **MicroPython** integrado ao Backend FastAPI da Fase 7 (`POST /api/telemetria`).

---

## 📁 Arquivos do Diretório

- `main.py` — Loop principal de leitura de sensores, pré-análise local na borda, exibição no display OLED I2C, envio HTTP (`urequests`), controle dos LEDs de risco e fila local de resiliência (até 20 leituras).
- `config.py` — Configuração da rede `Wokwi-GUEST`, `BACKEND_URL`, `DEVICE_TOKEN = "SEU_DEVICE_TOKEN"`, `PACIENTE_ID = "PAC-001"`, limiares de pré-análise e pinagem GPIO.
- `ssd1306.py` — Driver oficial do MicroPython para displays OLED SSD1306 (I2C/SPI) com cabeçalho de licença MIT original (`Copyright (c) 2016 Damien P. George`).
- `diagram.json` — Circuito completo para simulação no Wokwi (ESP32 + DHT22 + 2 potenciômetros + botão + LED verde + LED vermelho + OLED SSD1306 I2C).

---

## 🔄 Tabela de Equivalência: C++ (Arduino Fase 3) ➔ MicroPython (Fase 7)

| Funcionalidade / Camada | Fase 3 — C++ (`sketch.ino`) | Fase 7 — MicroPython (`main.py` / `config.py`) |
| :--- | :--- | :--- |
| **Transporte de Telemetria** | `PubSubClient` / MQTT (`mqtt.publish(...)`) | `urequests` / HTTP REST (`requests.post(url, data=..., headers={"X-Device-Token": ...})`) |
| **Conexão Wi-Fi** | `#include <WiFi.h>` / `WiFi.begin(WIFI_SSID, WIFI_PASS)` / `WiFi.status() == WL_CONNECTED` | `import network` / `wlan = network.WLAN(network.STA_IF)` / `wlan.connect(...)` / `wlan.isconnected()` |
| **Sensor de Temperatura (DHT22)** | `#include <DHT.h>` / `DHT dht(PIN_DHT, DHT22)` / `dht.readTemperature()` | `import dht` / `sensor_dht = dht.DHT22(Pin(4))` / `sensor_dht.measure()` + `sensor_dht.temperature()` |
| **Leitura Analógica (Potenciômetros)** | `analogRead(PIN_POT)` + `map(raw, 0, 4095, 40, 180)` | `from machine import ADC, Pin` / `adc = ADC(Pin(34))` / `adc.read()` + função `mapear_adc(...)` |
| **Saída Digital (LEDs de Status)** | `pinMode(PIN_LED, OUTPUT)` / `digitalWrite(PIN_LED, HIGH/LOW)` | `led = Pin(PIN_LED, Pin.OUT)` / `led.value(1)` ou `led.value(0)` |
| **Entrada Digital com Pull-Up (Botão)** | `pinMode(PIN_BTN, INPUT_PULLUP)` / `digitalRead(PIN_BTN) == LOW` | `botao = Pin(15, Pin.IN, Pin.PULL_UP)` / `botao.value() == 0` |
| **Temporização Não-Bloqueante** | `millis()` e `delay(ms)` | `time.ticks_ms()`, `time.ticks_diff(...)` e `time.sleep_ms(ms)` |
| **Serialização JSON** | `#include <ArduinoJson.h>` / `StaticJsonDocument<256>` + `serializeJson(...)` | `import ujson as json` / `json.dumps(payload)` e `resp.json()` |
| **Interface Visual Local (Edge UI)** | Apenas Monitor Serial CSV (`Serial.printf(...)`) | Display gráfico **OLED SSD1306 128x64 I2C** (`ssd1306.SSD1306_I2C`) + logs no console serial |
| **Buffer / Fila Offline** | Array estático C `Sample buffer[120]` (`head`/`tail`) | Lista FIFO Python `fila_offline` limitada a `MAX_QUEUE_SIZE = 20` leituras |

---

## 🔌 Mapeamento de Pinos (ESP32)

| Componente Wokwi | ID no `diagram.json` | Pino ESP32 | Função no Sistema |
| :--- | :--- | :--- | :--- |
| **DHT22** | `dht1` | `GPIO 4` | Leitura de temperatura corporal/ambiente (`temperatura` em °C) |
| **Potenciômetro 1** | `pot1` | `GPIO 34` (ADC1) | Simulação de Frequência Cardíaca (`fc_media`: **40 a 180 BPM**) |
| **Potenciômetro 2** | `pot2` | `GPIO 35` (ADC1) | Simulação de Saturação de O₂ (`spo2_media`: **80 a 100 %**) |
| **Pushbutton** | `btn1` | `GPIO 15` (`PULL_UP`) | Disparo imediato de leitura e envio HTTP (com debounce) |
| **LED Verde** (+ resistor 220 Ω) | `led_green` | `GPIO 2` | Aceso quando o risco retornado é **`BAIXO`** (pisca quando **`MODERADO`**) |
| **LED Vermelho** (+ resistor 220 Ω) | `led_red` | `GPIO 5` | Aceso quando o risco retornado é **`ALTO`** ou `alerta == True` (pisca quando **`MODERADO`**) |
| **OLED SSD1306 I2C (128x64)** | `oled1` | `SCL = GPIO 22`, `SDA = GPIO 21` | Exibe BPM, SpO2, Temperatura, pré-análise Edge e `"Risco 0.xx ALTO"` |

---

## 🧠 Comportamento de Borda (Edge) e Nuvem (Cloud)

1. **Ciclo Periódico (5 s) e Envio Imediato por Botão**:
   - A cada 5 segundos — ou imediatamente quando o botão no `GPIO 15` é pressionado — o ESP32 lê o `DHT22` e os 2 potenciômetros.
2. **Pré-Análise Local na Borda**:
   - Antes mesmo da resposta da nuvem, o dispositivo verifica localmente:
     - `BPM > 120`
     - `SpO2 < 92`
     - `temperatura > 38.0 °C`
   - O resultado preliminar é exibido na linha `Edge:` do display OLED.
3. **Integração HTTP com o Backend FastAPI (`POST /api/telemetria`)**:
   - Envia `{device_id, paciente_id, fc_media, temperatura, spo2_media}` com o cabeçalho `X-Device-Token`.
   - Com a resposta `{probabilidade, classificacao, alerta, protocolos}`:
     - **OLED**: mostra na última linha `Risco 0.xx ALTO` (ex.: `Risco 0.85 ALTO`).
     - **LED Vermelho**: acende fixo se `classificacao == "ALTO"` ou `alerta == True`.
     - **LED Verde**: acende fixo se `classificacao == "BAIXO"`.
     - **Pisca**: alterna os LEDs a cada 300 ms se `classificacao == "MODERADO"`.
4. **Resiliência (Reconexão Wi-Fi, Timeout e Fila de até 20 Leituras)**:
   - Caso o Wi-Fi caia ou o backend no Render esteja em *cold start* (acordando), a requisição respeita o timeout (`HTTP_TIMEOUT_S = 10`) e guarda a amostra em `fila_offline` (até 20 leituras). Assim que o backend responde `200 OK`, a fila é drenada automaticamente em ordem FIFO.

---

## 🚀 Passo a Passo para Montar e Executar no Wokwi.com

1. Acesse [https://wokwi.com](https://wokwi.com) e crie um novo projeto **ESP32** com **MicroPython** (*Start from Scratch → ESP32 → MicroPython*).
2. Na aba **`diagram.json`** do Wokwi, substitua todo o conteúdo pelo arquivo [diagram.json](file:///c:/Users/JonasLuisdaSilva/Documents/CardioAI/phases/fase07_plataforma_integrada/iot/diagram.json) desta pasta.
3. No editor do Wokwi, crie (ou substitua) os três arquivos Python copiando o conteúdo exato desta pasta:
   - **`main.py`** ← conteúdo de [main.py](file:///c:/Users/JonasLuisdaSilva/Documents/CardioAI/phases/fase07_plataforma_integrada/iot/main.py)
   - **`config.py`** ← conteúdo de [config.py](file:///c:/Users/JonasLuisdaSilva/Documents/CardioAI/phases/fase07_plataforma_integrada/iot/config.py)
   - **`ssd1306.py`** ← conteúdo de [ssd1306.py](file:///c:/Users/JonasLuisdaSilva/Documents/CardioAI/phases/fase07_plataforma_integrada/iot/ssd1306.py)
4. No arquivo **`config.py`** dentro do Wokwi, substitua:
   - `DEVICE_TOKEN = "SEU_DEVICE_TOKEN"` pelo valor real configurado na variável `DEVICE_TOKEN` do seu serviço no Render.
   - Confirme se `BACKEND_URL` aponta para a URL pública do seu backend no Render (ex.: `https://cardioai-fase07-backend.onrender.com`).
5. Clique no botão verde **Start the simulation (▶)**:
   - O ESP32 se conectará automaticamente à rede virtual `Wokwi-GUEST`.
   - Gire os potenciômetros **BPM (40-180)** e **SpO2 (80-100%)** ou altere a temperatura clicando sobre o sensor **DHT22**.
   - Pressione o botão azul **Enviar Agora** para disparar uma leitura imediata sem aguardar os 5 segundos e observe o display OLED atualizar para `Risco 0.85 ALTO` e o LED vermelho acender quando `BPM > 110` e `SpO2 < 92`.

