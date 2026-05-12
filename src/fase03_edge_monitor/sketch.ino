/*
 * CardioIA — Fase 3 — Edge Monitor ESP32
 *
 * Limitação assumida: SPIFFS e shields microSD não são persistentes em
 * simuladores Wokwi (Web e extensão VS Code) — o filesystem é volátil
 * e os arquivos desaparecem ao encerrar a simulação. O enunciado da
 * Fase 3 autoriza tratar o Monitor Serial como o canal de "envio à
 * nuvem", então este firmware usa um buffer circular em SRAM (120
 * amostras ≈ 10 min a 1 amostra a cada 5 s) como camada de resiliência
 * offline. Em hardware físico, essa camada seria substituída por
 * SPIFFS ou microSD sem alterar o restante do fluxo.
 *
 * Sensores:
 *   - DHT22 (GPIO4)    → temperatura (°C) e umidade (%)
 *   - Potenciômetro    → frequência cardíaca simulada (40–180 BPM)
 *                        no GPIO34 (ADC1), permitindo ao avaliador
 *                        variar o "BPM" interativamente na demo.
 *
 * Conectividade:
 *   - Pushbutton no GPIO15 (INPUT_PULLUP) alterna a flag `online`.
 *   - LED no GPIO2 reflete o estado de conectividade.
 *   - Debounce de 200 ms via millis().
 *
 * Saída CSV no Serial: timestamp_ms,temp_c,umid_pct,bpm
 */

#include <Arduino.h>
#include <DHT.h>

static const uint32_t SAMPLE_INTERVAL_MS = 5000;
static const uint16_t BUFFER_SIZE        = 120;
static const uint32_t DEBOUNCE_MS        = 200;

static const uint8_t PIN_DHT = 4;
static const uint8_t PIN_POT = 34;
static const uint8_t PIN_BTN = 15;
static const uint8_t PIN_LED = 2;

struct Sample {
  uint32_t ts_ms;
  float    temp_c;
  float    umid_pct;
  uint16_t bpm;
};

DHT dht(PIN_DHT, DHT22);

static Sample   buffer[BUFFER_SIZE];
static uint16_t head  = 0;
static uint16_t tail  = 0;
static uint16_t count = 0;

static bool     online       = false;
static uint32_t lastBtnMs    = 0;
static int      lastBtnState = HIGH;
static uint32_t lastSampleMs = 0;

static void bufferPush(const Sample& s) {
  if (count == BUFFER_SIZE) {
    // FIFO drop: preservamos a janela recente, que é a clinicamente relevante
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

static void printSampleCSV(const Sample& s) {
  Serial.printf("%lu,%.2f,%.2f,%u\n",
                (unsigned long)s.ts_ms, s.temp_c, s.umid_pct, s.bpm);
}

static void flushBuffer() {
  if (count == 0) return;
  uint16_t n = count;
  Sample s;
  while (bufferPop(s)) {
    printSampleCSV(s);
  }
  Serial.printf("[FLUSH] enviadas %u amostras, buffer=0\n", n);
}

static void readButton() {
  int s = digitalRead(PIN_BTN);
  uint32_t now = millis();
  // Borda de descida HIGH→LOW = pressão, com debounce de 200 ms
  if (s == LOW && lastBtnState == HIGH && (now - lastBtnMs) >= DEBOUNCE_MS) {
    online = !online;
    digitalWrite(PIN_LED, online ? HIGH : LOW);
    Serial.printf("[NET] online=%s\n", online ? "true" : "false");
    lastBtnMs = now;
    if (online) {
      // Transição offline→online drena tudo o que estiver pendente
      flushBuffer();
    }
  }
  lastBtnState = s;
}

static void handleSample(const Sample& s) {
  if (online) {
    if (count > 0) flushBuffer();
    printSampleCSV(s);
  } else {
    bufferPush(s);
  }
}

void setup() {
  Serial.begin(115200);
  delay(100);
  dht.begin();
  pinMode(PIN_BTN, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);
  // Cabeçalho CSV emitido uma única vez no boot
  Serial.println("timestamp_ms,temp_c,umid_pct,bpm");
}

void loop() {
  readButton();

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
