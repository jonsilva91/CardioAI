# Portal CardioIA — React + Vite (Fase 7)

Aplicação web do projeto CardioAI integrada ao Backend FastAPI da Fase 7 para monitoramento cardiológico IoT em tempo real, gráficos de série temporal (`recharts`), recomendação clínica do Sistema Multiagente (Fase 6) e assistente conversacional de triagem (`POST /api/chat`).

## Localização no repositório

```text
apps/portal-cardioia/
```

## Funcionalidades

- Autenticação real com JWT (`POST /api/auth/login`), logout e rotas protegidas (redirecionamento automático em `401`)
- Página `/monitoramento` como rota inicial após login:
  - Indicador de risco em destaque (`BAIXO` / `MODERADO` / `ALTO` com cor e texto + probabilidade)
  - Cards de BPM, SpO2, Temperatura e Horário da última leitura
  - Lista de protocolos clínicos acionados
  - Gráfico de série histórica com `recharts` (`GET /api/pacientes/{id}/historico`)
  - Polling automático a cada 5 s com indicador `"Ao vivo / Sem dados novos há X s"`
  - Botão **"Gerar recomendação com IA"** (`POST /api/pacientes/{id}/recomendacao`)
  - Aviso `"Servidor acordando, aguarde..."` durante cold start do backend
- Assistente conversacional integrado a `POST /api/chat` (OpenAI + memória por `session_id`)
- Configuração SPA para deploy na Vercel (`vercel.json`)

## Configuração de Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

Conteúdo de `.env.example`:

```env
VITE_API_URL=https://cardioai-fase07-backend.onrender.com
```

## Credenciais de Acesso

Utilize os valores configurados nas variáveis de ambiente `DEMO_EMAIL` e `DEMO_PASSWORD` do backend da Fase 7.

## Como Executar

```bash
cd apps/portal-cardioia
npm install
npm run dev
```
