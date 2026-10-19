# Portal CardioIA — React + Vite

Aplicação front-end do projeto CardioAI para visualização acadêmica de pacientes, métricas, agendamentos e assistente conversacional (Fase 5).

## Localização no repositório

```text
apps/portal-cardioia/
```

## Funcionalidades

- Autenticação simulada com rotas protegidas
- Dashboard com métricas resumidas e pacientes em risco
- Listagem de pacientes e agendamento de consultas
- Assistente conversacional cardiológico integrado ao backend do Watson Assistant (Fase 5)
- Gerenciamento de sessão individual por cliente com suporte a reinicialização ("Nova Conversa")
- Navegação SPA com React Router

## Estrutura Principal

```text
apps/portal-cardioia/
├── .env.example              # Exemplo de variáveis de ambiente do front-end
├── package.json
├── vite.config.js
├── index.html
└── src/
    ├── components/
    │   ├── ChatAssistente.jsx          # Componente único, modular e consolidado de chat
    │   ├── ChatAssistente.module.css   # Estilos centralizados do chat
    │   ├── Navbar.jsx
    │   ├── ProtectedRoute.jsx
    │   └── StatCard.jsx
    ├── config.js                       # Centralização de URLs do backend e endpoints
    ├── contexts/
    ├── data/
    ├── pages/
    │   ├── AssistenteChat/             # Página do assistente consumindo ChatAssistente
    │   ├── Agendamentos.jsx
    │   ├── Dashboard.jsx
    │   ├── Login.jsx
    │   └── Pacientes.jsx
    ├── services/
    ├── App.jsx
    ├── main.jsx
    └── routes.jsx
```

## Configuração de Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

Conteúdo padrão do `.env`:

```env
# URL base do servidor backend (Flask / Watson Assistant - Fase 5)
VITE_BACKEND_URL=http://localhost:5001
```

O arquivo `src/config.js` carrega essa configuração automaticamente, garantindo que nenhuma URL fique hardcoded no código.

## Credenciais de Acesso

```text
E-mail: admin@cardioia.com
Senha: 123456
```

## Como Executar

```bash
cd apps/portal-cardioia
npm install
npm run dev
```

Acesse a URL exibida no terminal, normalmente:

```text
http://localhost:5173
```

## Tecnologias

- React 19
- Vite
- React Router DOM
- CSS Modules
