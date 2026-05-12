# Fase 3 — Edge Monitor ESP32 (CardioIA)

## Objetivo

Construir um protótipo funcional de monitoramento cardíaco vestível baseado em ESP32 que demonstre o ciclo completo de **Edge Computing** em IoT médico: captura de sinais vitais simulados, armazenamento local resiliente, detecção de conectividade e transmissão dos dados acumulados quando "online". O entregável é avaliado no simulador **Wokwi** — sem necessidade de hardware físico.

## Sensores e periféricos

| Componente | Pino | Função |
| --- | --- | --- |
| DHT22 | GPIO4 | Temperatura (°C) + umidade (%) — sensor obrigatório do enunciado |
| Potenciômetro | GPIO34 (ADC1) | Frequência cardíaca simulada, mapeada para 40–180 BPM |
| Pushbutton | GPIO15 (`INPUT_PULLUP`) | Alterna a flag booleana `online` (Wi-Fi simulado) |
| LED | GPIO2 (com resistor 220 Ω) | Indicador visual do estado de conectividade |

O potenciômetro foi escolhido como segundo sensor porque permite ao avaliador **variar o "BPM" interativamente** durante a apresentação — uma leitura ADC casa diretamente com o pino de saída analógica de sensores de pulso reais (ex.: MAX30102), tornando o código portável a hardware físico sem mudanças estruturais.

## Fluxo de funcionamento

```
        ┌──────────────────────────────────────────────┐
        │  loop()                                      │
        │                                              │
        │  1. readButton()  ── debounce 200 ms         │
        │     └─ se transição offline→online:          │
        │        flushBuffer() (drena tudo no Serial)  │
        │                                              │
        │  2. a cada 5 s:                              │
        │     ├─ dht.readTemperature/Humidity()        │
        │     ├─ analogRead(POT) → map(40..180) BPM    │
        │     └─ handleSample(s):                      │
        │        ├─ online  → printSampleCSV(s)        │
        │        │          (flush antes, se houver)   │
        │        └─ offline → bufferPush(s)            │
        └──────────────────────────────────────────────┘
```

A saída no Monitor Serial segue o formato CSV `timestamp_ms,temp_c,umid_pct,bpm`, com o cabeçalho impresso uma única vez no `setup()`. Linhas de status (`[NET]`, `[FLUSH]`, `[WARN]`, `[ERR]`) usam prefixo entre colchetes para serem facilmente filtradas por um parser downstream (ex.: Node-RED, Python, Grafana).

## Lógica de resiliência offline

A camada de resiliência é um **buffer circular em SRAM** com capacidade fixa de `BUFFER_SIZE = 120` amostras.

### Por que 120 amostras?

- Período de amostragem: **5 s** → 120 × 5 s = **10 minutos** de cobertura offline.
- Esse intervalo cobre as janelas típicas de perda de conexão em um cenário vestível: elevador, banheiro, área morta de rede, troca de access point.
- Custo de memória: cada `Sample` ocupa ~16 bytes (`uint32_t` + 2 × `float` + `uint16_t` + padding), totalizando ~1,9 KB — confortável dentro dos 320 KB de SRAM do ESP32.

### Política de overflow: FIFO drop

Quando o buffer enche estando offline, a amostra **mais antiga** é descartada para abrir espaço para a nova. Em monitoramento cardíaco, a janela recente é a clinicamente mais relevante; descartar dado novo seria pior do que descartar dado antigo. O evento é registrado com `[WARN] buffer cheio, descartando amostra mais antiga` para que o limite do design seja visível.

### Drenagem

A drenagem é disparada por **dois caminhos**:

1. **Transição offline→online** (botão pressionado): `flushBuffer()` é chamado imediatamente dentro de `readButton()`.
2. **Nova amostra estando online com buffer não vazio**: `handleSample()` chama `flushBuffer()` antes de imprimir a amostra recém-gerada.

Ambos os caminhos terminam com `[FLUSH] enviadas N amostras, buffer=0`, tornando explícito o número de amostras drenadas.

## Limitações do simulador

> *Trecho do enunciado da Fase 3:* "esse item (SPIFFS) só funciona em um ESP32 físico e real, enquanto que, seja no simulador Wokwi Web, seja no VSCode com as extensões Wokwi e Platformio, o SPIFFS é volátil. Isso significa que ele é perdido quando se encerra a simulação, e não será possível gravar nenhum arquivo csv no ESP32 através de simuladores. Apenas em chips reais. (...) Pela limitação dos simuladores em executar o recurso SPIFFS, considere o Monitor Serial como sendo uma opção de resiliência offline alternativa."

Por essa razão **explicitamente autorizada pelo enunciado**, o firmware:

- Não grava em SPIFFS nem em microSD (ambos não persistem no Wokwi).
- Usa um buffer circular em RAM como camada de resiliência.
- Trata o `Serial.println` como o canal de "envio à nuvem".

Em hardware físico real, a função `bufferPush` seria substituída por uma escrita em SPIFFS/SD, e `flushBuffer` faria a leitura do arquivo e a publicação via MQTT — o restante do fluxo permaneceria idêntico.

## Como executar

### Opção A — Wokwi Web (mais rápida para a banca avaliar)

1. Acesse o link público abaixo.
2. Clique em **Start the simulation**.
3. Abra o painel Serial Monitor inferior.
4. Interaja com o potenciômetro (arrastar) e com o botão (clicar) para reproduzir os cenários de teste.

**Link público do Wokwi:** <https://wokwi.com/projects/463852249434716161>

### Opção B — Wokwi extension no VS Code

1. Instale as extensões **Wokwi for VS Code** e **PlatformIO IDE**.
2. Abra esta pasta (`src/fase03_edge_monitor/`) como workspace.
3. Compile com PlatformIO (`pio run`).
4. Inicie a simulação Wokwi (`Ctrl+Shift+P` → `Wokwi: Start Simulator`).

### Para publicar no Wokwi Web

1. Acesse <https://wokwi.com> e clique em **Start from Scratch** → **ESP32**.
2. Substitua o conteúdo de `sketch.ino` pelo deste repositório.
3. Substitua o conteúdo de `diagram.json` pelo deste repositório.
4. Crie um arquivo `libraries.txt` com as duas linhas: `DHT sensor library` e `Adafruit Unified Sensor`.
5. Clique em **Save** (login necessário) e copie o link gerado para esta seção.

## Cenários de teste

| # | Ação no simulador | Resultado esperado |
| --- | --- | --- |
| 1 | Iniciar a simulação | Cabeçalho `timestamp_ms,temp_c,umid_pct,bpm` aparece **uma única vez** |
| 2 | Aguardar 30 s sem tocar no botão (`online=false`) | Nenhuma linha CSV no Serial — só mensagens de status |
| 3 | Pressionar o botão (LED acende) | `[NET] online=true` seguido de `[FLUSH] enviadas N amostras` e as N linhas CSV correspondentes |
| 4 | Arrastar o potenciômetro entre 0% e 100% | Campo `bpm` percorre a faixa **40–180** |
| 5 | Pressionar o botão duas vezes em < 200 ms | Apenas uma transição registrada (debounce) |
| 6 | Manter offline por > 10 min (ou reduzir `SAMPLE_INTERVAL_MS` para testar mais rápido) | `[WARN] buffer cheio, descartando amostra mais antiga` aparece após a amostra 121 |
