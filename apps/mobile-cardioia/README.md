# 📱 CardioIA Mobile — Monitoramento IoT & Recomendação Multiagente (Fase 7)

Aplicativo React Native (Expo) integrado ao Backend FastAPI da Fase 7 (hospedado no Render) para monitoramento em tempo real de sinais vitais coletados via IoT (BPM, SpO2, Temperatura), classificação de risco cardiovascular com Machine Learning, protocolos clínicos e parecer do Sistema Multiagente.

## 🏗️ Estrutura do Projeto

```
apps/mobile-cardioia/
├── App.js                              # Fluxo principal (Login <-> Monitoramento)
├── index.js                            # Registro do componente raiz no Expo
├── app.json                            # Configuração do Expo (br.com.fiap.cardioia)
├── eas.json                            # Perfis EAS Build (development, preview APK, production)
├── package.json                        # Dependências Expo SDK atual
├── assets/
│   ├── icon.png                        # Ícone principal CardioIA (1024x1024)
│   ├── adaptive-icon.png               # Ícone adaptativo Android (1024x1024)
│   ├── splash.png                      # Tela de abertura CardioIA
│   └── favicon.png                     # Favicon web
└── src/
    ├── screens/
    │   ├── LoginScreen.js              # Autenticação JWT (POST /api/auth/login)
    │   └── MonitoramentoScreen.js      # Monitoramento 5s + Pull-to-refresh + Recomendação IA
    └── services/
        └── api.js                      # Cliente HTTP + persistência em expo-secure-store
```

## ⚙️ Configuração da URL do Backend

A URL do backend é lida exclusivamente da variável pública `EXPO_PUBLIC_API_URL` (definida em `eas.json` no perfil `preview` ou em arquivo `.env` local):

```env
EXPO_PUBLIC_API_URL=https://SEU-APP.onrender.com
```

## 📦 Build de APK no EAS

O perfil `preview` em `eas.json` está configurado com `android.buildType: "apk"`:

```bash
cd apps/mobile-cardioia
eas build -p android --profile preview
```
