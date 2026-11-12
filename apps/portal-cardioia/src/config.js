/**
 * Configuração central da API do Portal CardioIA (Fase 7).
 * Utiliza exclusivamente a variável de ambiente VITE_API_URL.
 */

const rawApiUrl =
  import.meta.env.VITE_API_URL || "https://cardioai-fase07-backend.onrender.com";

export const API_URL = rawApiUrl.replace(/\/+$/, "");
export const BACKEND_URL = API_URL;

export const API_ENDPOINTS = {
  health: `${API_URL}/health`,
  login: `${API_URL}/api/auth/login`,
  telemetria: `${API_URL}/api/telemetria`,
  pacienteStatus: (id) =>
    `${API_URL}/api/pacientes/${encodeURIComponent(id)}/status`,
  pacienteHistorico: (id, limite = 50) =>
    `${API_URL}/api/pacientes/${encodeURIComponent(id)}/historico?limite=${limite}`,
  pacienteRecomendacao: (id) =>
    `${API_URL}/api/pacientes/${encodeURIComponent(id)}/recomendacao`,
  chat: `${API_URL}/api/chat`,
};

export default {
  API_URL,
  BACKEND_URL,
  API_ENDPOINTS,
};
