# Portal CardioIA — React + Vite

Aplicação front-end do projeto CardioAI para visualização acadêmica de pacientes, métricas e agendamentos.

## Localização no repositório

```text
apps/portal-cardioia/
```

## Funcionalidades

- autenticação simulada
- proteção de rotas
- dashboard com métricas resumidas
- listagem de pacientes
- agendamento de consultas
- navegação com React Router
- dados simulados em JSON local

## Estrutura principal

```text
apps/portal-cardioia/
├── package.json
├── vite.config.js
├── index.html
└── src/
    ├── components/
    ├── contexts/
    ├── data/
    ├── pages/
    ├── services/
    ├── App.jsx
    ├── main.jsx
    └── routes.jsx
```

## Credenciais de acesso

```text
E-mail: admin@cardioia.com
Senha: 123456
```

## Como executar

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

- React
- Vite
- React Router DOM
- Context API
- CSS Modules

## Observações

- O portal foi movido de `src/portal-cardioia/` para `apps/portal-cardioia/`.
- A lógica interna da aplicação foi preservada.
