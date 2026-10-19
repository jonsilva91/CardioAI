/**
 * Configuração de ambiente e endpoints da API do Portal CardioAI.
 * 
 * Centraliza a URL base do backend para evitar URLs hardcoded pelo projeto.
 * Suporta Vite (import.meta.env.VITE_BACKEND_URL) e retrocompatibilidade
 * com process.env.REACT_APP_BACKEND_URL.
 */

const globalProcess = typeof globalThis !== "undefined" ? globalThis.process : undefined;

const rawBackendUrl =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_BACKEND_URL) ||
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_CHAT_API_URL?.replace(/\/chat\/?$/, "")) ||
  globalProcess?.env?.REACT_APP_BACKEND_URL ||
  "http://localhost:5001";

// Remove barras finais para garantir caminhos padronizados
export const BACKEND_URL = rawBackendUrl.replace(/\/+$/, "");

export const API_ENDPOINTS = {
  chat: `${BACKEND_URL}/chat`,
  sessionClose: `${BACKEND_URL}/chat/session/close`,
  sessionNew: `${BACKEND_URL}/chat/session`,
  health: `${BACKEND_URL}/health`,
};

export default {
  BACKEND_URL,
  API_ENDPOINTS,
};
