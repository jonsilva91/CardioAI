# 📱 CardioAI Mobile - Aplicativo React Native

> **IR ALÉM 2 - Fase 4**: Integração Mobile com CNN para Classificação de ECG

Aplicativo mobile desenvolvido em React Native com Expo para envio de imagens de ECG e exibição da classificação retornada pela CNN treinada na Fase 4.

## 🎯 Objetivo

Criar um protótipo mobile que permita:

- Selecionar imagens de ECG da galeria do dispositivo
- Enviar para o backend FastAPI com o modelo CNN treinado
- Exibir a classificação e confiança da predição
- Mostrar avisos de uso acadêmico

## 🏗️ Arquitetura

```
mobile-cardioia/
├── App.js                      # Componente principal
├── app.json                    # Configuração do Expo
├── package.json                # Dependências
└── src/
    ├── screens/
    │   └── EcgAnalysisScreen.js    # Tela principal de análise
    ├── services/
    │   └── visionApi.js            # Serviço de comunicação com API
    └── components/
        └── ResultCard.js           # Componente de exibição de resultado
```

## 🚀 Tecnologias Utilizadas

- **React Native**: Framework para desenvolvimento mobile
- **Expo**: Plataforma para desenvolvimento e build
- **expo-image-picker**: Seleção de imagens da galeria
- **axios**: Cliente HTTP para comunicação com API
- **FastAPI**: Backend para servir o modelo CNN

## 📋 Pré-requisitos

### Backend (API)

O backend FastAPI deve estar rodando antes de usar o app. Veja instruções em:
[`phases/fase04_cnn_ecg/README.md`](../../phases/fase04_cnn_ecg/README.md)

### Mobile

- Node.js 16+ e npm/yarn
- Expo CLI: `npm install -g expo-cli`
- Dispositivo físico com Expo Go ou emulador Android/iOS

## 🔧 Instalação

### 1. Instalar Dependências

```bash
cd apps/mobile-cardioia
npm install
```

### 2. Configurar IP da API

⚠️ **IMPORTANTE**: Você precisa configurar o IP da sua máquina na rede local.

Edite o arquivo `src/services/visionApi.js`:

```javascript
// Linha 14
const API_BASE_URL = "http://SEU_IP_LOCAL:8000";
```

**Como descobrir seu IP local:**

**Windows:**

```bash
ipconfig
# Procure por "Endereço IPv4" na seção da sua rede ativa
```

**Linux/Mac:**

```bash
ifconfig
# ou
ip addr show
```

**Exemplo:**

```javascript
const API_BASE_URL = "http://192.168.0.10:8000";
```

> ⚠️ **Não use `localhost` ou `127.0.0.1`**: No celular/emulador, isso aponta para o próprio dispositivo, não para sua máquina!

## ▶️ Executando o App

### 1. Iniciar o Backend

Em um terminal, inicie a API FastAPI:

```bash
cd phases/fase04_cnn_ecg

# Ativar ambiente virtual (se ainda não estiver ativo)
.venv\Scripts\activate  # Windows
# ou
source .venv/bin/activate  # Linux/Mac

# Iniciar API
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

Verifique se a API está funcionando acessando:

- http://localhost:8000/health
- http://localhost:8000/docs

### 2. Iniciar o App Mobile

Em outro terminal:

```bash
cd apps/mobile-cardioia
npx expo start
```

### 3. Abrir no Dispositivo

Após executar `npx expo start`, você verá um QR code no terminal.

**Opção 1: Dispositivo Físico (Recomendado)**

1. Instale o app **Expo Go** no seu celular:
   - [Android - Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - [iOS - App Store](https://apps.apple.com/app/expo-go/id982107779)
2. Escaneie o QR code com o app Expo Go
3. Aguarde o carregamento do app

**Opção 2: Emulador**

- Pressione `a` para Android
- Pressione `i` para iOS (apenas no Mac)

## 📱 Como Usar

1. **Selecionar Imagem**
   - Toque em "Selecionar Imagem de ECG"
   - Escolha uma imagem da galeria
   - Veja o preview da imagem selecionada

2. **Classificar**
   - Toque em "Classificar ECG"
   - Aguarde o processamento (pode levar alguns segundos)
   - Veja o resultado com classe prevista e confiança

3. **Interpretar Resultado**
   - **Classe Detectada**: Categoria prevista pelo modelo
   - **Confiança**: Percentual de certeza (0-100%)
   - **Barra de Confiança**: Visual colorido (verde=alta, amarelo=média, vermelho=baixa)
   - **Badge "Resultado Simulado"**: Aparece se o modelo real não estiver carregado

## 🎨 Funcionalidades

### Tela Principal (EcgAnalysisScreen)

- ✅ Seleção de imagem da galeria
- ✅ Preview da imagem selecionada
- ✅ Botão de classificação
- ✅ Loading indicator durante processamento
- ✅ Exibição de resultado com classe e confiança
- ✅ Tratamento de erros com mensagens claras
- ✅ Aviso acadêmico fixo
- ✅ Informação do endpoint da API

### Componente ResultCard

- ✅ Classe prevista destacada
- ✅ Barra de confiança visual e colorida
- ✅ Badge de resultado simulado (quando aplicável)
- ✅ Mensagem de aviso médico
- ✅ Informação adicional sobre uso acadêmico

### Serviço visionApi

- ✅ Comunicação com backend FastAPI
- ✅ Upload de imagem via multipart/form-data
- ✅ Health check da API
- ✅ Tratamento de erros de rede
- ✅ Timeout configurável

## 🔍 Endpoints da API

### GET /health

Verifica status da API e modelo carregado.

**Resposta:**

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_path": "...",
  "keras_available": true,
  "classes": ["Normal", "Myocardial Infarction", ...]
}
```

### POST /predict

Classifica uma imagem de ECG.

**Request:**

- Content-Type: `multipart/form-data`
- Body: `file` (imagem)

**Resposta:**

```json
{
  "predicted_class": "Normal",
  "confidence": 0.91,
  "message": "Resultado acadêmico/simulado. Não substitui avaliação médica.",
  "all_probabilities": {
    "Normal": 91.23,
    "Myocardial Infarction": 5.12,
    ...
  },
  "is_simulated": false
}
```

## 🐛 Troubleshooting

### Erro: "Não foi possível conectar com a API"

**Causas comuns:**

1. Backend não está rodando
2. IP configurado incorretamente em `visionApi.js`
3. Firewall bloqueando a porta 8000
4. Celular e computador em redes diferentes

**Soluções:**

1. Verifique se o backend está rodando: `http://localhost:8000/health`
2. Confirme o IP correto com `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)
3. Desabilite temporariamente o firewall ou adicione exceção para porta 8000
4. Conecte ambos dispositivos na mesma rede Wi-Fi

### Erro: "Network request failed"

- Verifique se o IP está correto
- Teste acessar `http://SEU_IP:8000/health` no navegador do celular
- Certifique-se de que o backend está com `--host 0.0.0.0`

### App não carrega no Expo Go

- Limpe o cache: `npx expo start -c`
- Reinstale dependências: `rm -rf node_modules && npm install`
- Atualize o Expo Go no celular

## ⚠️ Avisos Importantes

### Uso Acadêmico

Este aplicativo é um **protótipo acadêmico** desenvolvido para fins educacionais:

- ✅ Demonstra integração mobile com modelo CNN
- ✅ Mostra pipeline completo de classificação
- ✅ Serve como prova de conceito

- ❌ **NÃO** deve ser usado para diagnóstico médico real
- ❌ **NÃO** substitui avaliação de profissional de saúde
- ❌ **NÃO** é certificado para uso clínico

### Modo Simulado

Se o modelo real não estiver disponível, a API funciona em **modo simulado**:

- Gera resultados determinísticos baseados em características da imagem
- Útil para demonstração e testes
- Claramente indicado com badge "Resultado Simulado"

### Segurança e Privacidade

- Imagens são enviadas para o backend local
- Nenhum dado é armazenado permanentemente
- Use apenas imagens de teste/simuladas
- Não envie dados reais de pacientes

## 📊 Estrutura de Dados

### Formato de Resposta da API

```typescript
interface PredictionResponse {
  predicted_class: string; // Classe prevista
  confidence: number; // Confiança (0-1)
  message: string; // Mensagem de aviso
  all_probabilities?: {
    // Probabilidades de todas as classes
    [className: string]: number;
  };
  is_simulated: boolean; // Se é resultado simulado
}
```

## 🎥 Demonstração

Para criar o vídeo de demonstração (máximo 3 minutos):

1. **Introdução (15s)**
   - Mostre a tela inicial do app
   - Explique o objetivo

2. **Seleção de Imagem (30s)**
   - Demonstre seleção da galeria
   - Mostre preview

3. **Classificação (45s)**
   - Toque em "Classificar ECG"
   - Mostre loading
   - Exiba resultado completo

4. **Detalhes do Resultado (45s)**
   - Explique classe prevista
   - Mostre barra de confiança
   - Destaque avisos

5. **Teste com Outra Imagem (30s)**
   - Repita processo com imagem diferente
   - Mostre consistência

6. **Conclusão (15s)**
   - Reforce caráter acadêmico
   - Mencione tecnologias usadas

## 📚 Referências

- [React Native Documentation](https://reactnative.dev/)
- [Expo Documentation](https://docs.expo.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Expo Image Picker](https://docs.expo.dev/versions/latest/sdk/imagepicker/)

## 👥 Equipe

**FIAP - Projeto CardioAI 2026**

Desenvolvido como parte do IR ALÉM 2 da Fase 4 - Visão Computacional aplicada à Cardiologia.

## 📄 Licença

Este projeto é acadêmico e destinado apenas para fins educacionais.

---

**Made with Bob** 🤖

Para mais informações sobre o projeto completo, consulte o [README principal](../../README.md).
