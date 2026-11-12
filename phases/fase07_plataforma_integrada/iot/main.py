"""Firmware MicroPython (ESP32) — CardioIA Fase 7 (Plataforma Integrada).

Conversão evolutiva de `src/fase03_edge_monitor/sketch.ino` (C++) para MicroPython:
- Lê Temperatura no DHT22, BPM (40–180) no potenciômetro 1 e SpO2 (80–100%) no potenciômetro 2.
- A cada 5 s (ou imediatamente ao pressionar o botão):
  1. Realiza pré-análise local na borda (BPM > 120, SpO2 < 92, temp > 38 °C).
  2. Atualiza o display OLED SSD1306 I2C com os sinais vitais e status local.
  3. Envia POST para `/api/telemetria` com header `X-Device-Token` via `urequests`.
  4. Com a resposta do backend (modelo ML + protocolos da Fase 6):
     - Acende LED vermelho se `ALTO` / `alerta=True`;
     - Acende LED verde se `BAIXO`;
     - Pisca se `MODERADO`;
     - Exibe `"Risco 0.xx ALTO"` (probabilidade e classificação) no display OLED.
  5. Em caso de falha/timeout (ex.: backend no Render acordando), armazena a leitura em
     fila circular local de até 20 leituras e reenvia assim que a conexão restabelecer.
"""

import time
try:
    import ujson as json
except ImportError:
    import json

try:
    import urequests as requests
except ImportError:
    import requests

import dht
from machine import ADC, I2C, Pin
import network

import config
from ssd1306 import SSD1306_I2C

# Inicialização de hardware
sensor_dht = dht.DHT22(Pin(config.PIN_DHT))

adc_bpm = ADC(Pin(config.PIN_POT_BPM))
adc_bpm.atten(ADC.ATTN_11DB)
adc_bpm.width(ADC.WIDTH_12BIT)

adc_spo2 = ADC(Pin(config.PIN_POT_SPO2))
adc_spo2.atten(ADC.ATTN_11DB)
adc_spo2.width(ADC.WIDTH_12BIT)

botao_envio = Pin(config.PIN_BTN, Pin.IN, Pin.PULL_UP)
led_verde = Pin(config.PIN_LED_GREEN, Pin.OUT, value=0)
led_vermelho = Pin(config.PIN_LED_RED, Pin.OUT, value=0)

i2c = I2C(0, scl=Pin(config.PIN_I2C_SCL), sda=Pin(config.PIN_I2C_SDA), freq=400000)
oled = SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, i2c, addr=config.OLED_I2C_ADDR)

wlan = network.WLAN(network.STA_IF)

# Estado local e fila circular de até 20 leituras
fila_offline = []
estado_risco_atual = "BAIXO"
alerta_atual = False
prob_atual = 0.0
tem_resposta_cloud = False
estado_pisca = 0
ultimo_pisca_ms = 0


def mapear_adc(valor_raw, min_out, max_out):
    """Converte leitura ADC de 12 bits (0..4095) para a faixa fisiológica desejada."""
    if valor_raw < 0:
        valor_raw = 0
    elif valor_raw > 4095:
        valor_raw = 4095
    return min_out + (valor_raw * (max_out - min_out)) / 4095.0


def conectar_wifi():
    """Conecta ou reconecta ao Wi-Fi Wokwi-GUEST com timeout configurável."""
    if not wlan.active():
        wlan.active(True)
    if wlan.isconnected():
        return True

    print(f"[WIFI] Conectando a {config.WIFI_SSID}...")
    wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
    inicio = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), inicio) > (config.WIFI_TIMEOUT_S * 1000):
            print("[WIFI] Timeout ao conectar. Operando em modo Edge/Offline.")
            return False
        time.sleep_ms(200)

    ip_info = wlan.ifconfig()[0]
    print(f"[WIFI] Conectado! IP={ip_info}")
    return True


def enfileirar_leitura(payload):
    """Guarda leitura na fila local (máximo de 20 leituras, descarta a mais antiga se cheia)."""
    if len(fila_offline) >= config.MAX_QUEUE_SIZE:
        fila_offline.pop(0)
        print("[QUEUE] Fila cheia (20 leituras); descartando amostra mais antiga.")
    fila_offline.append(payload)
    print(f"[QUEUE] Leitura armazenada localmente (pendentes={len(fila_offline)}/{config.MAX_QUEUE_SIZE}).")


def pre_analise_local(bpm, spo2, temp):
    """Avalia limiares críticos localmente na borda (BPM > 120, SpO2 < 92, temp > 38)."""
    alertas_borda = []
    if bpm > config.EDGE_BPM_HIGH:
        alertas_borda.append("FC>120")
    if spo2 < config.EDGE_SPO2_LOW:
        alertas_borda.append("SpO2<92")
    if temp > config.EDGE_TEMP_HIGH:
        alertas_borda.append("T>38")
    return alertas_borda


def atualizar_leds():
    """Controla os LEDs verde e vermelho conforme a classificação de risco e alerta."""
    global estado_pisca, ultimo_pisca_ms

    classif = str(estado_risco_atual).upper()
    if classif == "ALTO" or alerta_atual:
        led_vermelho.value(1)
        led_verde.value(0)
    elif classif == "MODERADO":
        agora = time.ticks_ms()
        if time.ticks_diff(agora, ultimo_pisca_ms) >= config.BLINK_INTERVAL_MS:
            ultimo_pisca_ms = agora
            estado_pisca = 0 if estado_pisca else 1
            led_verde.value(estado_pisca)
            led_vermelho.value(estado_pisca)
    else:
        led_verde.value(1)
        led_vermelho.value(0)


def atualizar_oled(bpm, spo2, temp, alertas_borda, linha_risco):
    """Renderiza os sinais vitais, pré-análise local e o resultado de risco no OLED SSD1306."""
    oled.fill(0)
    oled.text(f"CardioIA {config.PACIENTE_ID}", 0, 0)
    oled.text(f"BPM:{int(bpm)} SpO2:{int(spo2)}%", 0, 14)
    oled.text(f"Temp: {temp:.1f} C", 0, 26)

    if alertas_borda:
        oled.text("Edge:" + ",".join(alertas_borda)[:11], 0, 38)
    else:
        oled.text("Edge: Normal", 0, 38)

    oled.text(linha_risco[:16], 0, 52)
    oled.show()


def enviar_post_telemetria(payload):
    """Envia payload JSON para POST /api/telemetria usando urequests com X-Device-Token."""
    url = config.BACKEND_URL.rstrip("/") + "/api/telemetria"
    headers = {
        "Content-Type": "application/json",
        "X-Device-Token": config.DEVICE_TOKEN,
    }
    corpo = json.dumps(payload)
    resp = None
    try:
        try:
            resp = requests.post(url, data=corpo, headers=headers, timeout=config.HTTP_TIMEOUT_S)
        except TypeError:
            # Fallback para versões de urequests que não aceitam o argumento timeout nomeado
            resp = requests.post(url, data=corpo, headers=headers)

        if resp.status_code == 200:
            dados = resp.json()
            return True, dados
        else:
            print(f"[HTTP] Erro {resp.status_code}: {resp.text}")
            return False, None
    except Exception as exc:
        print(f"[HTTP] Falha/Timeout ao enviar telemetria: {exc}")
        return False, None
    finally:
        if resp is not None:
            try:
                resp.close()
            except Exception:
                pass


def drenar_fila_offline():
    """Tenta reenviar as leituras acumuladas na fila local quando o backend responde."""
    global fila_offline
    if not fila_offline:
        return
    print(f"[FLUSH] Drenando {len(fila_offline)} leituras pendentes da fila local...")
    while fila_offline:
        amostra = fila_offline[0]
        ok, _ = enviar_post_telemetria(amostra)
        if ok:
            fila_offline.pop(0)
        else:
            print("[FLUSH] Backend indisponível durante drenagem; mantendo restante na fila.")
            break


def ler_sensores():
    """Lê temperatura no DHT22 e mapeia BPM (40-180) e SpO2 (80-100) nos potenciômetros."""
    try:
        sensor_dht.measure()
        temp = float(sensor_dht.temperature())
    except Exception as exc:
        print(f"[WARN] Falha na leitura do DHT22 ({exc}); usando 36.5 C.")
        temp = 36.5

    raw_bpm = adc_bpm.read()
    raw_spo2 = adc_spo2.read()

    bpm = round(mapear_adc(raw_bpm, config.BPM_MIN, config.BPM_MAX), 1)
    spo2 = round(mapear_adc(raw_spo2, config.SPO2_MIN, config.SPO2_MAX), 1)
    return bpm, spo2, round(temp, 1)


def executar_ciclo_coleta(origem="TIMER"):
    """Executa leitura, pré-análise local, exibição no OLED, envio HTTP e atualização de LEDs."""
    global estado_risco_atual, alerta_atual, prob_atual, tem_resposta_cloud

    bpm, spo2, temp = ler_sensores()
    alertas_borda = pre_analise_local(bpm, spo2, temp)

    print(
        f"[{origem}] PAC={config.PACIENTE_ID} | BPM={bpm:.0f} | SpO2={spo2:.1f}% | Temp={temp:.1f}C | Edge={alertas_borda}"
    )

    # Atualiza OLED imediatamente após a pré-análise local
    status_preliminar = (
        f"Risco {prob_atual:.2f} {estado_risco_atual}"
        if tem_resposta_cloud
        else ("Edge ALERTA" if alertas_borda else "Enviando HTTP...")
    )
    atualizar_oled(bpm, spo2, temp, alertas_borda, status_preliminar)

    payload = {
        "device_id": config.DEVICE_ID,
        "paciente_id": config.PACIENTE_ID,
        "fc_media": bpm,
        "temperatura": temp,
        "spo2_media": spo2,
    }

    if not conectar_wifi():
        enfileirar_leitura(payload)
        estado_risco_atual = "ALTO" if alertas_borda else "BAIXO"
        alerta_atual = bool(alertas_borda)
        atualizar_leds()
        atualizar_oled(bpm, spo2, temp, alertas_borda, f"Fila:{len(fila_offline)} Offline")
        return

    # Se havia leituras na fila, tenta drenar antes da leitura atual
    if fila_offline:
        drenar_fila_offline()

    sucesso, resposta = enviar_post_telemetria(payload)
    if sucesso and resposta is not None:
        prob_atual = float(resposta.get("probabilidade", 0.0))
        estado_risco_atual = str(resposta.get("classificacao", "BAIXO")).upper()
        alerta_atual = bool(resposta.get("alerta", False))
        tem_resposta_cloud = True

        linha_risco = f"Risco {prob_atual:.2f} {estado_risco_atual}"
        print(f"[CLOUD] Resposta: {linha_risco} | Alerta={alerta_atual}")
        atualizar_leds()
        atualizar_oled(bpm, spo2, temp, alertas_borda, linha_risco)
    else:
        enfileirar_leitura(payload)
        estado_risco_atual = "ALTO" if alertas_borda else "MODERADO"
        alerta_atual = bool(alertas_borda)
        atualizar_leds()
        atualizar_oled(bpm, spo2, temp, alertas_borda, f"Wait Render({len(fila_offline)})")


def main():
    print("============================================================")
    print("CardioIA Fase 7 - Edge Monitor MicroPython (ESP32)")
    print("============================================================")
    atualizar_oled(0, 0, 0.0, [], "Iniciando...")
    conectar_wifi()

    ultimo_envio_ms = time.ticks_add(time.ticks_ms(), -config.SAMPLE_INTERVAL_MS)
    ultimo_btn_ms = 0
    ultimo_estado_btn = 1

    while True:
        agora_ms = time.ticks_ms()

        # Leitura do botão com debounce para envio imediato
        estado_btn = botao_envio.value()
        if (
            estado_btn == 0
            and ultimo_estado_btn == 1
            and time.ticks_diff(agora_ms, ultimo_btn_ms) >= config.DEBOUNCE_MS
        ):
            ultimo_btn_ms = agora_ms
            print("[BTN] Botão pressionado! Disparando leitura e envio imediato...")
            executar_ciclo_coleta(origem="BOTAO")
            ultimo_envio_ms = time.ticks_ms()
        ultimo_estado_btn = estado_btn

        # Ciclo periódico a cada 5 segundos
        if time.ticks_diff(agora_ms, ultimo_envio_ms) >= config.SAMPLE_INTERVAL_MS:
            ultimo_envio_ms = agora_ms
            executar_ciclo_coleta(origem="TIMER_5S")

        # Atualiza estado dos LEDs (garante pisca contínuo quando MODERADO)
        atualizar_leds()
        time.sleep_ms(50)


if __name__ == "__main__":
    main()

