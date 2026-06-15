/**
 * API Service para comunicação com o backend CardioAI
 *
 * IMPORTANTE: Configure o IP correto da sua máquina na rede local
 * Não use 'localhost' pois no celular/emulador isso aponta para o próprio dispositivo
 *
 * Exemplo: http://192.168.0.10:8000
 */

import axios from "axios";

// CONFIGURAÇÃO DA API
// ⚠️ ALTERE ESTE IP PARA O IP DA SUA MÁQUINA NA REDE LOCAL
const API_BASE_URL = "http://192.168.0.10:8000";

// Timeout para requisições (30 segundos)
const API_TIMEOUT = 30000;

// Instância do axios configurada
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    "Content-Type": "multipart/form-data",
  },
});

/**
 * Verifica o status da API
 * @returns {Promise<Object>} Status da API e informações do modelo
 */
export const checkHealth = async () => {
  try {
    const response = await api.get("/health");
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error("Erro ao verificar health da API:", error);
    return {
      success: false,
      error: error.message || "Erro ao conectar com a API",
    };
  }
};

/**
 * Envia uma imagem de ECG para classificação
 * @param {string} imageUri - URI da imagem selecionada
 * @returns {Promise<Object>} Resultado da classificação
 */
export const classifyEcgImage = async (imageUri) => {
  try {
    // Prepara o FormData com a imagem
    const formData = new FormData();

    // Extrai o nome do arquivo da URI
    const filename = imageUri.split("/").pop();

    // Determina o tipo MIME baseado na extensão
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : "image/jpeg";

    // Adiciona a imagem ao FormData
    formData.append("file", {
      uri: imageUri,
      name: filename,
      type: type,
    });

    console.log("Enviando imagem para classificação:", filename);

    // Envia a requisição
    const response = await api.post("/predict", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("Resposta recebida:", response.data);

    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    console.error("Erro ao classificar imagem:", error);

    // Trata diferentes tipos de erro
    if (error.response) {
      // Erro da API (4xx, 5xx)
      return {
        success: false,
        error: error.response.data?.detail || "Erro ao processar imagem",
        statusCode: error.response.status,
      };
    } else if (error.request) {
      // Erro de rede (sem resposta)
      return {
        success: false,
        error:
          "Não foi possível conectar com a API. Verifique se o backend está rodando e se o IP está correto.",
      };
    } else {
      // Outro tipo de erro
      return {
        success: false,
        error: error.message || "Erro desconhecido",
      };
    }
  }
};

/**
 * Obtém a URL base da API
 * @returns {string} URL base configurada
 */
export const getApiBaseUrl = () => API_BASE_URL;

/**
 * Valida se a API está acessível
 * @returns {Promise<boolean>} true se a API está acessível
 */
export const validateApiConnection = async () => {
  try {
    const result = await checkHealth();
    return result.success;
  } catch (error) {
    return false;
  }
};

// Made with Bob
