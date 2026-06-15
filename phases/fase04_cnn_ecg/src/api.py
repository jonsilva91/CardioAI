"""
API FastAPI para classificação de imagens de ECG - IR ALÉM 2
Integração com aplicativo mobile React Native

AVISO: Este é um protótipo acadêmico e NÃO deve ser usado para diagnóstico médico real.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

# Tentativa de importar TensorFlow/Keras
try:
    from tensorflow import keras
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False
    print("⚠️ TensorFlow não disponível. Usando modo simulado.")

app = FastAPI(
    title="CardioAI API",
    description="API para classificação de imagens de ECG usando CNN",
    version="1.0.0"
)

# Configuração CORS para permitir chamadas do app mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de caminhos
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "phases" / "fase04_cnn_ecg" / "outputs" / "models" / "cardioia_cnn_model.keras"

# Variáveis globais
model = None
class_names = ["Normal", "Myocardial Infarction", "History of MI", "Abnormal Heartbeat", "Other"]

# Modelos Pydantic para resposta
class PredictionResponse(BaseModel):
    predicted_class: str
    confidence: float
    message: str
    all_probabilities: Optional[dict] = None
    is_simulated: bool = False


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
    keras_available: bool
    classes: list[str]


def load_model():
    """Carrega o modelo treinado se disponível."""
    global model
    
    if not KERAS_AVAILABLE:
        print("⚠️ TensorFlow não disponível. API funcionará em modo simulado.")
        return
    
    if MODEL_PATH.exists():
        try:
            model = keras.models.load_model(MODEL_PATH)
            print(f"✓ Modelo carregado: {MODEL_PATH}")
        except Exception as e:
            print(f"⚠️ Erro ao carregar modelo: {e}")
            print("API funcionará em modo simulado.")
    else:
        print(f"⚠️ Modelo não encontrado em: {MODEL_PATH}")
        print("API funcionará em modo simulado para demonstração.")


def simulate_prediction(image_array: np.ndarray) -> tuple[str, float, dict]:
    """
    Simula uma predição quando o modelo real não está disponível.
    Usa características simples da imagem para gerar resultado controlado.
    """
    # Calcula média de intensidade da imagem para gerar resultado "determinístico"
    mean_intensity = float(np.mean(image_array))
    
    # Gera probabilidades baseadas na intensidade média
    # Isso garante que a mesma imagem sempre retorne o mesmo resultado
    if mean_intensity < 0.3:
        probabilities = [0.85, 0.05, 0.03, 0.04, 0.03]  # Normal
    elif mean_intensity < 0.5:
        probabilities = [0.10, 0.75, 0.05, 0.05, 0.05]  # Myocardial Infarction
    elif mean_intensity < 0.7:
        probabilities = [0.05, 0.10, 0.70, 0.10, 0.05]  # History of MI
    else:
        probabilities = [0.05, 0.05, 0.05, 0.80, 0.05]  # Abnormal Heartbeat
    
    predicted_idx = np.argmax(probabilities)
    predicted_class = class_names[predicted_idx]
    confidence = probabilities[predicted_idx]
    
    all_probs = {
        class_names[i]: round(probabilities[i] * 100, 2)
        for i in range(len(class_names))
    }
    
    return predicted_class, confidence, all_probs


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz da API."""
    return {
        "message": "CardioAI API - Classificação de ECG",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs"
        },
        "warning": "Protótipo acadêmico - NÃO usar para diagnóstico médico real"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Endpoint de health check.
    Retorna status da API e informações sobre o modelo.
    """
    return HealthResponse(
        status="ok",
        model_loaded=model is not None,
        model_path=str(MODEL_PATH),
        keras_available=KERAS_AVAILABLE,
        classes=class_names
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_ecg(file: UploadFile = File(...)):
    """
    Endpoint para classificação de imagem de ECG.
    
    Recebe uma imagem via multipart/form-data e retorna:
    - predicted_class: classe prevista
    - confidence: confiança da predição (0-1)
    - message: mensagem de aviso
    - all_probabilities: probabilidades de todas as classes
    - is_simulated: indica se é resultado simulado
    """
    # Validação do tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Arquivo deve ser uma imagem (PNG, JPG, JPEG)"
        )
    
    try:
        # Lê e pré-processa a imagem
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Redimensiona para o tamanho esperado pelo modelo (256x256)
        image = image.resize((256, 256))
        
        # Converte para array numpy e normaliza
        image_array = np.array(image) / 255.0
        
        # Expande dimensão de batch
        image_array = np.expand_dims(image_array, axis=0)
        
        # Realiza predição (real ou simulada)
        if model is not None and KERAS_AVAILABLE:
            # Predição com modelo real
            predictions = model.predict(image_array, verbose=0)
            predicted_idx = np.argmax(predictions[0])
            predicted_class = class_names[predicted_idx]
            confidence = float(predictions[0][predicted_idx])
            
            all_probs = {
                class_names[i]: round(float(predictions[0][i] * 100), 2)
                for i in range(len(class_names))
            }
            is_simulated = False
        else:
            # Predição simulada
            predicted_class, confidence, all_probs = simulate_prediction(image_array)
            is_simulated = True
        
        return PredictionResponse(
            predicted_class=predicted_class,
            confidence=round(confidence, 4),
            message="Resultado acadêmico/simulado. Não substitui avaliação médica.",
            all_probabilities=all_probs,
            is_simulated=is_simulated
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar imagem: {str(e)}"
        )


# Importação adicional necessária
import io


# Evento de inicialização
@app.on_event("startup")
async def startup_event():
    """Carrega o modelo na inicialização da API."""
    print("\n" + "="*60)
    print("🫀 CardioAI API - Classificação de ECG")
    print("="*60)
    print("\n⚠️  AVISO: Protótipo acadêmico - NÃO usar para diagnóstico real\n")
    load_model()
    print("\n✓ API iniciada com sucesso!")
    print("📖 Documentação: http://localhost:8000/docs")
    print("🏥 Health check: http://localhost:8000/health")
    print("\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# Made with Bob