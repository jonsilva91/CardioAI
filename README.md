# CardioAI: A Nova Era da Cardiologia Inteligente

[![FIAP - Faculdade de Informática e Administração Paulista](https://github.com/jonsilva91/CardioAI/raw/main/assets/logo-fiap.png)](https://www.fiap.com.br/)

---

## Integrantes


- **Jonas Luis da Silva** — RM561465
- **Edson Henrique Felix Batista** — RM566321

---

## Visão Geral

O **CardioAI** é um projeto acadêmico da FIAP com foco em **Inteligência Artificial aplicada à cardiologia**. O repositório foi reorganizado para separar claramente os entregáveis por fase, facilitar a avaliação acadêmica e preservar o funcionamento dos artefatos já implementados.

O projeto contempla:

- bases multimodais para cardiologia
- IA simbólica e classificação textual
- portal front-end em React
- monitoramento IoT com API REST e automação de alertas
- análise de séries temporais em saúde
- classificação de imagens de ECG com CNN treinada do zero e Transfer Learning (Fase 4)
- assistente conversacional integrado ao IBM watsonx Assistant (Fase 5)
- modelo preditivo de risco cardiovascular (Random Forest) e orquestração multiagente com OpenAI Agents SDK (Fase 6)
- plataforma integrada em nuvem unificando IoT MicroPython (Wokwi ESP32), Backend FastAPI (Render), Portal React/Vite (Vercel), App Mobile Android (APK via Expo EAS Build), modelo preditivo e agentes de IA (Fase 7)

---

## Navegação Rápida

- [Fase 1 — Bases Multimodais](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase01_bases_multimodais/README.md)
- [Fase 2 — IA Simbólica e Classificação](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase02_ia_simbolica_classificacao/README.md)
- [Fase 3 — IoT, REST, e-mail e séries temporais](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase03_iot_monitoramento/README.md)
- [Fase 4 — CNN aplicada a ECG](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase04_cnn_ecg/README.md)
- [Fase 5 — Assistente Conversacional](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase05_assistente_conversacional/README.md)
- [Fase 6 — Preditivo e Multiagente](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase06_preditivo_multiagente/README.md)
- [Fase 7 — Plataforma Integrada (IoT, Cloud, Web, Mobile & Agentes)](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase07_plataforma_integrada/README.md)
- [Portal React](https://github.com/jonsilva91/CardioAI/blob/main/apps/portal-cardioia/README.md)
- [App Mobile (Expo / EAS Build)](https://github.com/jonsilva91/CardioAI/blob/main/apps/mobile-cardioia/README.md)

---

## Estrutura do Repositório

```
CardioAI/
├── README.md
├── assets/
├── data/
│   └── raw/
├── docs/
│   └── references/
├── phases/
│   ├── fase01_bases_multimodais/
│   ├── fase02_ia_simbolica_classificacao/
│   ├── fase03_iot_monitoramento/
│   ├── fase04_cnn_ecg/
│   ├── fase05_assistente_conversacional/
│   ├── fase06_preditivo_multiagente/
│   └── fase07_plataforma_integrada/
├── apps/
│   ├── mobile-cardioia/
│   └── portal-cardioia/
├── render.yaml
├── config/
├── referencias.md
└── .gitignore
```

---

## Resumo das Fases

### Fase 1 — Bases Multimodais

Organiza materiais de referência, textos clínicos e documentação de bases para uso em IA aplicada à cardiologia.

**Local:** `phases/fase01_bases_multimodais/`

### Fase 2 — IA Simbólica e Classificação Textual

Contém o script de diagnóstico baseado em mapa de conhecimento e o notebook de classificação textual de risco.

**Local:** `phases/fase02_ia_simbolica_classificacao/`

### Fase 3 — IoT, REST, e-mail e séries temporais

Centraliza os entregáveis de monitoramento IoT, API REST com alertas simulados por e-mail, notebook de séries temporais e relatórios.

**Local:** `phases/fase03_iot_monitoramento/`

### Fase 4 — CNN aplicada a ECG

Classificação de sinais de ECG usando uma CNN treinada do zero e Transfer Learning (MobileNetV2), com avaliação completa (accuracy, precision, recall e F1 por classe) e um protótipo Flask de inferência integrado à Fase 5.

**Local:** `phases/fase04_cnn_ecg/`

### Fase 5 — Assistente Conversacional

Assistente conversacional (chatbot) para triagem inicial em saúde, integrado ao portal React, com fluxo de diálogo real modelado no IBM watsonx Assistant (intents, entities e dialog nodes), backend Flask com fallback local, e integração direta com o classificador da Fase 4 para explicar resultados de ECG.

**Local:** `phases/fase05_assistente_conversacional/`

### Fase 6 — Modelo Preditivo e Orquestração Multiagente

Sistema preditivo de pico de risco cardiovascular com Machine Learning supervisionado e arquitetura multiagente para apoio à decisão clínica e operacional no ambiente hospitalar:
- **Base de Dados Sintética:** Geração reproduzindo estritamente as diretrizes da FIAP (5.000 amostras, 10 features clínico-operacionais, seed 42);
- **Modelo Preditivo (*Random Forest*):** 200 estimadores atingindo 99,9% de acurácia, F1-Score de 0,9981 e recall de 99,62% no teste para detecção de pico de risco;
- **Sistema Multiagente (*OpenAI Agents SDK*):** Quatro agentes colaborativos especializados (Orquestrador, Analista de Risco, Especialista em Protocolos e Planejador de Resposta) integrados por *handoffs* nativos;
- **Engenharia de Confiabilidade:** Isolamento de contexto por atendimento (`CardioContext`), persistência e histórico em banco SQLite (`SQLiteSession`) para acompanhamento interativo pós-triagem, e validação de segurança clínica com `OutputGuardrail` determinístico (tripwire contra alucinações e divergências de protocolo).

**Local:** `phases/fase06_preditivo_multiagente/`

### Fase 7 — Plataforma Integrada em Nuvem (IoT, Backend FastAPI, Web, Mobile e Agentes IA)

Consolidação final de todos os módulos do ecossistema **CardioAI** operando integrados em produção:
- **Nó IoT em MicroPython (`phases/fase07_plataforma_integrada/iot/`):** Simulação pública no Wokwi ([https://wokwi.com/projects/480500031706588161](https://wokwi.com/projects/480500031706588161)) com ESP32, DHT22, 2 potenciômetros (`BPM` e `SpO2`), botão de envio imediato, display OLED SSD1306 I2C, LEDs verde/vermelho, pré-análise local na borda e fila offline de até 20 leituras;
- **Backend Unificado FastAPI no Render (`phases/fase07_plataforma_integrada/backend/`):** Hospedado em [https://cardioai-fase07-backend.onrender.com](https://cardioai-fase07-backend.onrender.com), importa diretamente `src.predictor`, `src.protocols` e `src.agents_system` da Fase 6, autentica usuários via JWT e dispositivos via `X-Device-Token`, calcula risco e protocolos em tempo real e expõe o pipeline multiagente (`/recomendacao`) e o assistente de triagem (`/api/chat`);
- **Portal Web em Produção na Vercel (`apps/portal-cardioia/`):** Disponível em [https://cardio-ai-five.vercel.app](https://cardio-ai-five.vercel.app), com login JWT real, dashboard de monitoramento em tempo real (`/monitoramento`, polling 5 s, gráficos `recharts`), recomendação multiagente sob demanda e chat clínico;
- **App Mobile Android (`apps/mobile-cardioia/`):** Atualizado para o Expo SDK 58 (`br.com.fiap.cardioia`), com APK gerado no Expo EAS Build ([https://expo.dev/accounts/jonsilva91/projects/mobile-cardioia/builds/be64508a-ebc2-4fb2-9ab3-93a89bb8b267](https://expo.dev/accounts/jonsilva91/projects/mobile-cardioia/builds/be64508a-ebc2-4fb2-9ab3-93a89bb8b267)) e validado no emulador Android Pixel 7 / Android 13 via Appetize.io.

➡️ **[Acessar documentação completa e relatório da Fase 7](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase07_plataforma_integrada/README.md)**

**Local:** `phases/fase07_plataforma_integrada/`

### Portal CardioIA

Aplicação React + Vite integrada ao backend FastAPI da Fase 7, contando com login JWT real, rota protegida de monitoramento cardiológico em tempo real (`/monitoramento` com polling de 5 s e gráficos `recharts`), acionamento sob demanda da recomendação multiagente (`/recomendacao`), assistente conversacional de triagem (`/assistente`), dashboard, pacientes e agendamentos.

**Local:** `apps/portal-cardioia/`

### App Mobile React Native

Aplicativo mobile em React Native (**Expo SDK 58**, pacote `br.com.fiap.cardioia`) integrado ao backend da Fase 7, com APK Android gerado via **Expo EAS Build**:

**Funcionalidades:**

- Autenticação JWT real (`POST /api/auth/login`) com persistência segura via `expo-secure-store`
- Monitoramento em tempo real do paciente padrão `PAC-001` (BPM, SpO2, Temperatura, risco com cor + texto e protocolos acionados) com atualização a cada 5 s e *pull-to-refresh*
- Solicitação sob demanda de **Recomendação IA** executando o pipeline multiagente da Fase 6 (`POST /api/pacientes/PAC-001/recomendacao`)

➡️ **[Acessar documentação do app mobile](https://github.com/jonsilva91/CardioAI/blob/main/apps/mobile-cardioia/README.md)**

**Local:** `apps/mobile-cardioia/`

---

## Como Executar

### 1. Portal React

```
cd apps/portal-cardioia
npm install
npm run dev
```

Acesse a URL exibida no terminal, normalmente `http://localhost:5173`.

### 2. Fase 2 — Diagnóstico simbólico

```
python phases/fase02_ia_simbolica_classificacao/diagnostico_ontologia.py
```

### 3. Fase 2 — Notebook de classificação textual

```
jupyter notebook phases/fase02_ia_simbolica_classificacao/classificacao_risco.ipynb
```

### 4. Fase 3 — API REST e alerta por e-mail simulado

```
cd phases/fase03_iot_monitoramento/ir_alem_1_rest_email
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Em outro terminal:

```
cd phases/fase03_iot_monitoramento/ir_alem_1_rest_email
python client_simulador.py
```

### 5. Fase 3 — Notebook de séries temporais

```
pip install -r phases/fase03_iot_monitoramento/ir_alem_2_series_temporais/requirements.txt
jupyter notebook phases/fase03_iot_monitoramento/notebooks/ir_alem_2_series_temporais_saude.ipynb
```

### 6. Fase 4 — CNN ECG

```
pip install -r phases/fase04_cnn_ecg/requirements.txt
jupyter notebook phases/fase04_cnn_ecg/notebooks/cnn_ecg_classification.ipynb
python phases/fase04_cnn_ecg/src/train.py
python phases/fase04_cnn_ecg/src/evaluate.py
```

### 7. Fase 4 — API FastAPI (IR ALÉM 2)

```
cd phases/fase04_cnn_ecg
.venv\Scripts\activate
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Acesse: `http://localhost:8000/docs`

### 8. App Mobile React Native (Expo SDK 58 / EAS Build)

```bash
cd apps/mobile-cardioia
cp .env.example .env
npm install
npx expo-doctor
npx expo start
```

A URL do backend é configurada via variável de ambiente `EXPO_PUBLIC_API_URL` (definida em `eas.json` e `.env`). Veja instruções completas em: [apps/mobile-cardioia/README.md](https://github.com/jonsilva91/CardioAI/blob/main/apps/mobile-cardioia/README.md)

### 9. Fase 5 — Assistente Conversacional

Para rodar o backend do chat:

```
cd phases/fase05_assistente_conversacional
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/app.py
```

O chat ficará acessível via Portal React na rota `/assistente`.

### 10. Fase 6 — Preditivo e Multiagente

#### Configuração do Ambiente Virtual:
```bash
cd phases/fase06_preditivo_multiagente
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### Geração da Base e Treinamento do Modelo:
```bash
# Gera a base sintética oficial em data/base_sintetica_pico_risco.csv
python -m src.data_generation

# Executa o treino do Random Forest, gera gráficos em reports/figures e salva models/modelo_pico_risco.joblib
python -m src.train
```

#### Execução dos Agentes (com OpenAI API):
Configure as variáveis de ambiente a partir do modelo `.env.example`:
```bash
cp .env.example .env
# Defina sua chave de API no arquivo .env: OPENAI_API_KEY=sua-chave-aqui
```

Execução dos cenários clínicos:
```bash
# Caso individual (paciente de alto risco do enunciado):
python -m src.agents_system.main --paciente data/exemplos/novo_caso.json

# Modo interativo com histórico em SQLite (permite perguntas de acompanhamento pós-triagem):
python -m src.agents_system.main --paciente data/exemplos/novo_caso.json --interativo

# Outros perfis de teste:
python -m src.agents_system.main --paciente data/exemplos/caso_baixo_risco.json
python -m src.agents_system.main --paciente data/exemplos/caso_moderado_risco.json
```

#### Testes Unitários e Tripwire de Segurança Clínica:
```bash
# Demonstração prática do disparo e captura do OutputGuardrailTripwireTriggered:
python scripts/demo_guardrail.py

# Suíte de testes unitários (15 testes sem chamadas externas):
pytest -v
```

### 11. Fase 7 — Plataforma Integrada (IoT, Backend FastAPI, Portal Web e App Mobile)

```bash
# Backend FastAPI + Testes Automatizados (10 testes pytest)
pip install -r phases/fase07_plataforma_integrada/backend/requirements.txt
pytest phases/fase07_plataforma_integrada/backend/tests -v
uvicorn app.main:app --app-dir phases/fase07_plataforma_integrada/backend --host 0.0.0.0 --port 8000 --reload
```

Veja o guia completo (incluindo links em produção na Vercel e Render, simulação Wokwi MicroPython e instalação do APK Android) em: [phases/fase07_plataforma_integrada/README.md](https://github.com/jonsilva91/CardioAI/blob/main/phases/fase07_plataforma_integrada/README.md)

---

## Dados e Referências

- Referências bibliográficas gerais: [`referencias.md`](https://github.com/jonsilva91/CardioAI/blob/main/referencias.md)
- Artigos e textos de apoio: [`docs/references/`](https://github.com/jonsilva91/CardioAI/blob/main/docs/references)
- Dados brutos futuros devem ser colocados em: [`data/raw/`](https://github.com/jonsilva91/CardioAI/blob/main/data/raw)

> Para a Fase 4, datasets grandes não devem ser versionados. O download deve ser feito manualmente e armazenado em `data/raw/`.

---

## Vídeos

Demonstrações em vídeo das entregas acadêmicas do projeto:

### Vídeo da Fase 5 — Assistente Conversacional e Integração de Modelos
[![Vídeo da Fase 5](https://img.youtube.com/vi/Nu-WhM9n6-s/0.jpg)](https://youtu.be/Nu-WhM9n6-s)
- **Link no YouTube:** [https://youtu.be/Nu-WhM9n6-s](https://youtu.be/Nu-WhM9n6-s)
- **Conteúdo:** Demonstração do chatbot integrado ao IBM watsonx Assistant e explicação de exames de ECG da Fase 4.

### Vídeo da Fase 6 — Entrega Principal (Sistema Preditivo e Multiagente)
- **Link no YouTube (Não Listado):** [https://youtu.be/2cC5odm-Fuw](https://youtu.be/2cC5odm-Fuw)
- **Duração máxima:** 4 minutos
- **Conteúdo:** Apresentação do modelo de Machine Learning (Random Forest 99,9%), demonstração do fluxo multiagente com logs de handoffs no terminal, saída estruturada sob Output Guardrail e modo interativo via SQLiteSession.

### Vídeo da Fase 6 — Ir Além 1 (Desafio Opcional 1)
- **Link no YouTube (Não Listado):** [https://youtu.be/mperrwkEUbA](https://youtu.be/mperrwkEUbA)

### Vídeo da Fase 6 — Ir Além 2 (Desafio Opcional 2)
- **Link no YouTube (Não Listado):** [https://youtu.be/FRKwCTTr1H0](https://youtu.be/FRKwCTTr1H0)

### Vídeo da Fase 7 — Plataforma Integrada (IoT, Cloud, ML, Multiagente, Web e Mobile)
- **Link no YouTube (Não Listado):** [https://youtu.be/e7b1ICpbym0](https://youtu.be/e7b1ICpbym0)
- **Conteúdo:** Demonstração integrada ponta a ponta com o ESP32 MicroPython no Wokwi enviando telemetria para o backend FastAPI no Render, atualização em tempo real no Portal Web (Vercel) e no App Mobile Android (APK / Appetize.io), acionamento do sistema multiagente da Fase 6 e assistente conversacional de triagem.

---

## Tecnologias Utilizadas

### Ciência de Dados / IA

- Python
- Pandas
- NumPy
- Scikit-learn (Random Forest, Logistic Regression)
- Joblib
- Jupyter Notebook
- TensorFlow/Keras
- IBM watsonx Assistant
- OpenAI Agents SDK (`openai-agents`)
- Pydantic
- SQLite (`SQLiteSession`)

### Back-end, Cloud, IoT e Mobile

- FastAPI & Uvicorn
- Autenticação JWT (`PyJWT` / `HS256`) e `expo-secure-store`
- MicroPython (ESP32, `urequests`, `dht`, `ADC`, OLED `SSD1306` I2C)
- Simulador Wokwi
- React Native / Expo SDK 58 (Expo EAS Build — APK Android)
- Render (Deploy Python com Blueprint `render.yaml` e `buildFilter`)
- Vercel (Deploy SPA com `vercel.json`)

### Front-end

- React
- Vite
- React Router DOM
- Recharts (gráficos de série temporal em tempo real)
- Context API
- CSS Modules

### Organização e Versionamento

- Git
- GitHub
- Markdown

---

## Roadmap

### Concluído

- Fase 1 — bases multimodais
- Fase 2 — mapa de conhecimento e classificador textual
- Fase 3 — IoT, REST, e-mail e séries temporais
- Fase 4 — CNN e Transfer Learning para classificação de ECG
- Fase 5 — assistente conversacional com IBM watsonx Assistant
- Fase 6 — modelo preditivo de risco cardiovascular (Random Forest) e orquestração multiagente (OpenAI Agents SDK) com guardrails e persistência SQLite
- Fase 7 — plataforma integrada em nuvem (Wokwi ESP32 MicroPython + FastAPI no Render + Portal React na Vercel + APK Android no Expo EAS Build)
- Portal React funcional

---

## Referências

- UCI Machine Learning Repository
- Kaggle
- SciELO
- Diretrizes SBC, ACC/AHA e ESC

Consultar também:

- `referencias.md`
- `docs/references/`

---

## Licença

MIT License

---

**Status do Projeto**: Fases 1 a 7 entregues
**Versão**: 7.0
**Curso**: FIAP — Faculdade de Informática e Administração Paulista

---

*Desenvolvido para FIAP – Faculdade de Informática e Administração Paulista*