/**
 * Serviço de comunicação com o Backend FastAPI da Fase 7 e persistência segura de JWT.
 *
 * - URL base lida de EXPO_PUBLIC_API_URL (sem IP fixo e sem segredos no código).
 * - Token JWT armazenado com segurança via expo-secure-store.
 */

import * as SecureStore from "expo-secure-store";

const RAW_API_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  "https://cardioai-fase07-backend.onrender.com";

export const API_BASE_URL = RAW_API_URL.replace(/\/+$/, "");

const TOKEN_STORAGE_KEY = "cardioia_jwt_token";
const EMAIL_STORAGE_KEY = "cardioia_user_email";

let memoryTokenFallback = null;
let memoryEmailFallback = null;

export async function salvarSessao(token, email) {
  memoryTokenFallback = token;
  memoryEmailFallback = email || "";
  try {
    await SecureStore.setItemAsync(TOKEN_STORAGE_KEY, token);
    if (email) {
      await SecureStore.setItemAsync(EMAIL_STORAGE_KEY, email);
    }
  } catch {
    // Fallback em memória caso executado em ambiente web sem SecureStore nativo
  }
}

export async function obterSessaoSalva() {
  try {
    const token = await SecureStore.getItemAsync(TOKEN_STORAGE_KEY);
    const email = await SecureStore.getItemAsync(EMAIL_STORAGE_KEY);
    if (token) {
      return { token, email: email || "" };
    }
  } catch {
    // Ignora erro em plataforma sem suporte nativo a Keychain/Keystore
  }
  return {
    token: memoryTokenFallback,
    email: memoryEmailFallback || "",
  };
}

export async function limparSessao() {
  memoryTokenFallback = null;
  memoryEmailFallback = null;
  try {
    await SecureStore.deleteItemAsync(TOKEN_STORAGE_KEY);
    await SecureStore.deleteItemAsync(EMAIL_STORAGE_KEY);
  } catch {
    // Ignora erro em plataforma web
  }
}

async function parseJsonOuErro(response) {
  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const detalhe =
      (payload && (payload.detail || payload.message)) ||
      `Erro HTTP ${response.status}`;
    const err = new Error(
      typeof detalhe === "string" ? detalhe : JSON.stringify(detalhe)
    );
    err.status = response.status;
    throw err;
  }

  return payload;
}

export async function loginUsuario(email, senha) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      email: email.trim(),
      senha,
    }),
  });

  const data = await parseJsonOuErro(response);
  await salvarSessao(data.access_token, data.email || email.trim());
  return data;
}

export async function buscarStatusPaciente(pacienteId = "PAC-001", token) {
  const idCodificado = encodeURIComponent(
    (pacienteId || "PAC-001").trim()
  );
  const response = await fetch(
    `${API_BASE_URL}/api/pacientes/${idCodificado}/status`,
    {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return parseJsonOuErro(response);
}

export async function solicitarRecomendacaoIA(pacienteId = "PAC-001", token) {
  const idCodificado = encodeURIComponent(
    (pacienteId || "PAC-001").trim()
  );
  const response = await fetch(
    `${API_BASE_URL}/api/pacientes/${idCodificado}/recomendacao`,
    {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return parseJsonOuErro(response);
}

