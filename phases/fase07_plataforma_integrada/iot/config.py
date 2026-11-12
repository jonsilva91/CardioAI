"""Configurações do nó IoT MicroPython (ESP32) — CardioIA Fase 7.

Centraliza credenciais de rede Wi-Fi do simulador Wokwi, endpoint do backend
FastAPI no Render, identificação do paciente/dispositivo e mapeamento de pinos GPIO.
"""

# Rede Wi-Fi padrão do simulador Wokwi
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""
WIFI_TIMEOUT_S = 10

# Endpoint do Backend FastAPI da Fase 7 e autenticação do dispositivo
BACKEND_URL = "https://cardioai-fase07-backend.onrender.com"
DEVICE_TOKEN = "SEU_DEVICE_TOKEN"
PACIENTE_ID = "PAC-001"
DEVICE_ID = "esp32-wokwi-01"

# Parâmetros de temporização, timeout e fila offline (resiliência a cold start no Render)
SAMPLE_INTERVAL_MS = 5000
DEBOUNCE_MS = 250
BLINK_INTERVAL_MS = 300
HTTP_TIMEOUT_S = 10
MAX_QUEUE_SIZE = 20

# Limiares de pré-análise local na borda (Edge Computing)
EDGE_BPM_HIGH = 120
EDGE_SPO2_LOW = 92
EDGE_TEMP_HIGH = 38.0

# Faixas de mapeamento dos potenciômetros (ADC 12 bits: 0..4095)
BPM_MIN = 40
BPM_MAX = 180
SPO2_MIN = 80
SPO2_MAX = 100

# Mapeamento de pinos GPIO no ESP32
PIN_DHT = 4          # Sensor DHT22 (temperatura)
PIN_POT_BPM = 34     # Potenciômetro 1 -> Frequência Cardíaca (BPM)
PIN_POT_SPO2 = 35    # Potenciômetro 2 -> Saturação de O2 (SpO2 %)
PIN_BTN = 15         # Botão de envio imediato (PULL_UP)
PIN_LED_GREEN = 2    # LED Verde (Risco BAIXO)
PIN_LED_RED = 5      # LED Vermelho (Risco ALTO / Alerta)
PIN_I2C_SCL = 22     # OLED SSD1306 I2C Clock
PIN_I2C_SDA = 21     # OLED SSD1306 I2C Data
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_I2C_ADDR = 0x3C

