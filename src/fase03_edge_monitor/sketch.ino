/*
 * CardioIA — Fase 3 — Edge Monitor ESP32 (Partes 1 + 2)
 *
 * Parte 1 — Edge Computing (preservada integralmente):
 *   - SPIFFS e microSD não persistem no simulador Wokwi (limitação documentada
 *     pelo próprio enunciado). Buffer circular em SRAM (120 amostras ≈ 10 min
 *     a 1 amostra/5 s) atua como camada de resiliência offline. Cada amostra
 *     publicada é registrada no Serial em formato CSV
 *     (timestamp_ms,temp_c,umid_pct,bpm) — canal mantido como evidência da
 *     Parte 1.
 *
 * Parte 2 — Fog/Cloud Computing (adição não-destrutiva):
 *   - Wi-Fi simulado (rede Wokwi-GUEST) conecta o ESP32 à internet real.
 *   - Cliente MQTT (PubSubClient) publica em broker.hivemq.com:1883 sob o
 *     tópico cardioai/<deviceId>/telemetry com payload JSON. Last Will and
 *     Testament em cardioai/<deviceId>/status publica {"online":false} se o
 *     dispositivo cair sem desconectar limpo.
 *   - Cada amostra é emitida SIMULTANEAMENTE no Serial (CSV) e MQTT (JSON),
 *     mantendo retrocompatibilidade total com a Parte 1.
 *   - PubSubClient suporta nativamente apenas QoS 0 em publish (QoS 1 em
 *     connect/LWT/subscribe). Para QoS 1 nas publicações, trocar para a
 *     biblioteca arduino-mqtt (256dpi) — discutido no RELATORIO.
 *
 * Sensores e periféricos:
 *   - DHT22 (GPIO4)      → temperatura (°C) e umidade (%)
 *   - Potenciômetro      → BPM simulado (40–180), GPIO34 (ADC1)
 *   - Pushbutton (GPIO15, INPUT_PULLUP) → alterna a flag `online`
 *     (offline simulado para a banca demonstrar buffering)
 *   - LED (GPIO2)        → reflete `online`; debounce 200 ms via millis()
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

static const uint32_t SAMPLE_INTERVAL_MS = 5000;
static const uint16_t BUFFER_SIZE        = 120;
static const uint32_t DEBOUNCE_MS        = 200;

static const uint8_t PIN_DHT = 4;
static const uint8_t PIN_POT = 34;
static const uint8_t PIN_BTN = 15;
static const uint8_t PIN_LED = 2;

static const char*    WIFI_SSID       = "Wokwi-GUEST";
static const char*    WIFI_PASS       = "";
static const uint32_t WIFI_TIMEOUT_MS = 10000;

static const char*    MQTT_HOST = "broker.hivemq.com";
static const uint16_t MQTT_PORT = 1883;

struct Sample {
  uint32_t ts_ms;
  float    temp_c;
  float    umid_pct;
  uint16_t bpm;
};

DHT          dht(PIN_DHT, DHT22);
WiFiClient   espClient;
PubSubClient mqtt(espClient);

static Sample   buffer[BUFFER_SIZE];
static uint16_t head  = 0;
static uint16_t tail  = 0;
static uint16_t count = 0;

static bool     online        = false;
static uint32_t lastBtnMs     = 0;
static int      lastBtnState  = HIGH;
static uint32_t lastSampleMs  = 0;
static uint32_t lastWifiCheck = 0;
static uint32_t nextMqttAttemptMs = 0;
static uint32_t mqttBackoffMs     = 1000;

static String deviceId;
static String topicTelemetry;
static String topicStatus;

// ---------------------------------------------------------------- buffer FIFO

static void bufferPush(const Sample& s) {
  if (count == BUFFER_SIZE) {
    // FIFO drop: preservamos a janela recente, clinicamente mais relevante
    tail = (tail + 1) % BUFFER_SIZE;
    count--;
    Serial.println("[WARN] buffer cheio, descartando amostra mais antiga");
  }
  buffer[head] = s;
  head = (head + 1) % BUFFER_SIZE;
  count++;
}

static bool bufferPop(Sample& out) {
  if (count == 0) return false;
  out  = buffer[tail];
  tail = (tail + 1) % BUFFER_SIZE;
  count--;
  return true;
}

// ----------------------------------------------------------- canais de saída

static void emitSerialCSV(const Sample& s) {
  Serial.printf("%lu,%.2f,%.2f,%u\n",
                (unsigned long)s.ts_ms, s.temp_c, s.umid_pct, s.bpm);
}

static bool emitMqttJSON(const Sample& s, bool buffered) {
  if (!mqtt.connected()) return false;
  StaticJsonDocument<256> doc;
  doc["ts"]       = s.ts_ms;
  doc["temp"]     = s.temp_c;
  doc["umid"]     = s.umid_pct;
  doc["bpm"]      = s.bpm;
  doc["buffered"] = buffered;
  char payload[256];
  size_t len = serializeJson(doc, payload, sizeof(payload));
  return mqtt.publish(topicTelemetry.c_str(),
                      (const uint8_t*)payload, len, false);
}

// Canal duplo: cada amostra vai simultaneamente para Serial (Parte 1) e MQTT (Parte 2)
static void publishSample(const Sample& s, bool buffered) {
  emitSerialCSV(s);
  emitMqttJSON(s, buffered);
}

static void flushBuffer() {
  if (count == 0) return;
  uint16_t n = count;
  Sample s;
  while (bufferPop(s)) {
    publishSample(s, true);
  }
  Serial.printf("[FLUSH] enviadas %u amostras, buffer=0\n", n);
}

// ------------------------------------------------------------------ botão

static void readButton() {
  int s = digitalRead(PIN_BTN);
  uint32_t now = millis();
  if (s == LOW && lastBtnState == HIGH && (now - lastBtnMs) >= DEBOUNCE_MS) {
    online = !online;
    digitalWrite(PIN_LED, online ? HIGH : LOW);
    Serial.printf("[NET] online=%s\n", online ? "true" : "false");
    lastBtnMs = now;
    // Drena apenas quando ambos os canais estão prontos (resiliência dual-channel)
    if (online && mqtt.connected()) {
      flushBuffer();
    }
  }
  lastBtnState = s;
}

// ------------------------------------------------------------ amostra → canal

static void handleSample(const Sample& s) {
  if (online && mqtt.connected()) {
    if (count > 0) flushBuffer();
    publishSample(s, false);
  } else {
    bufferPush(s);
  }
}

// ----------------------------------------------------------------- Wi-Fi

static void connectWiFi() {
  Serial.printf("[WIFI] conectando a %s...\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - t0) < WIFI_TIMEOUT_MS) {
    delay(200);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[WIFI] conectado, ip=%s\n",
                  WiFi.localIP().toString().c_str());
  } else {
    Serial.println("[WIFI] timeout, seguindo offline");
  }
}

static void checkWiFi() {
  uint32_t now = millis();
  if (now - lastWifiCheck < 5000) return;
  lastWifiCheck = now;
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WIFI] desconectado, tentando reconectar");
    WiFi.reconnect();
  }
}

// ------------------------------------------------------------------- MQTT

static bool mqttConnect() {
  String clientId = "cardioai-" + deviceId;
  const char* willPayload = "{\"online\":false}";
  if (mqtt.connect(clientId.c_str(),
                   topicStatus.c_str(), 1, true, willPayload)) {
    Serial.println("[MQTT] conectado");
    // Status online com retain=true para novos subscritores verem o estado atual
    mqtt.publish(topicStatus.c_str(), "{\"online\":true}", true);
    mqttBackoffMs = 1000;
    return true;
  }
  return false;
}

static void mqttReconnectIfNeeded() {
  if (mqtt.connected()) return;
  if (WiFi.status() != WL_CONNECTED) return;

  uint32_t now = millis();
  if (now < nextMqttAttemptMs) return;

  static uint32_t attempt = 0;
  attempt++;
  Serial.printf("[MQTT] reconectando (tentativa %lu)\n",
                (unsigned long)attempt);
  if (mqttConnect()) {
    attempt = 0;
    // Drenar pendências assim que reconectar
    if (online && count > 0) flushBuffer();
  } else {
    nextMqttAttemptMs = now + mqttBackoffMs;
    mqttBackoffMs = min((uint32_t)30000, mqttBackoffMs * 2);
  }
}

// ------------------------------------------------------------------ setup/loop

void setup() {
  Serial.begin(115200);
  delay(100);

  // Cabeçalho CSV emitido uma única vez no boot — preserva 100% da Parte 1
  Serial.println("timestamp_ms,temp_c,umid_pct,bpm");

  dht.begin();
  pinMode(PIN_BTN, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  connectWiFi();

  deviceId       = String((uint32_t)ESP.getEfuseMac(), HEX);
  topicTelemetry = "cardioai/" + deviceId + "/telemetry";
  topicStatus    = "cardioai/" + deviceId + "/status";
  Serial.printf("[DEV] deviceId=%s\n", deviceId.c_str());

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(512);
  mqttConnect();
}

void loop() {
  readButton();
  checkWiFi();
  mqttReconnectIfNeeded();
  mqtt.loop();

  uint32_t now = millis();
  if (now - lastSampleMs >= SAMPLE_INTERVAL_MS) {
    lastSampleMs = now;

    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (isnan(t) || isnan(h)) {
      Serial.println("[ERR] DHT leitura inválida");
      return;
    }

    int raw = analogRead(PIN_POT);
    uint16_t bpm = (uint16_t) map(raw, 0, 4095, 40, 180);

    Sample s = { now, t, h, bpm };
    handleSample(s);
  }
}
