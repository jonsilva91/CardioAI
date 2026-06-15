"""
Protótipo Flask para classificação de imagens de ECG.
AVISO: Este é um protótipo acadêmico e NÃO deve ser usado para diagnóstico médico real.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, render_template_string, request
from PIL import Image
from tensorflow import keras

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Configuração de caminhos
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = PROJECT_ROOT / "phases" / "fase04_cnn_ecg" / "outputs" / "models" / "cnn_ecg_model.keras"

# Carrega o modelo treinado
model = None
class_names = []

def load_model():
    """Carrega o modelo treinado."""
    global model, class_names
    if MODEL_PATH.exists():
        model = keras.models.load_model(MODEL_PATH)
        # Classes padrão do dataset ECG Images (MIT-BIH)
        class_names = ["Normal", "Myocardial Infarction", "History of MI", "Abnormal Heartbeat", "Other"]
        print(f"✓ Modelo carregado: {MODEL_PATH}")
    else:
        print(f"⚠ Modelo não encontrado em: {MODEL_PATH}")
        print("Execute o treinamento primeiro: python phases/fase04_cnn_ecg/src/train.py")


# Template HTML simples
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CardioAI - Classificador de ECG</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }
        .warning {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 30px;
            color: #856404;
        }
        .warning strong { display: block; margin-bottom: 5px; }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        .upload-area:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }
        .upload-area input[type="file"] { display: none; }
        .upload-icon {
            font-size: 3em;
            color: #667eea;
            margin-bottom: 10px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
            font-weight: bold;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        #preview {
            max-width: 100%;
            max-height: 300px;
            margin: 20px auto;
            display: none;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        #result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 15px;
            display: none;
        }
        .result-success {
            background: #d4edda;
            border: 2px solid #28a745;
            color: #155724;
        }
        .result-error {
            background: #f8d7da;
            border: 2px solid #dc3545;
            color: #721c24;
        }
        .prediction {
            font-size: 1.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .confidence {
            font-size: 1.1em;
            color: #666;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🫀 CardioAI</h1>
        <p class="subtitle">Classificador de ECG com Deep Learning</p>
        
        <div class="warning">
            <strong>⚠️ AVISO IMPORTANTE</strong>
            Este é um protótipo acadêmico desenvolvido para fins educacionais.
            NÃO deve ser usado para diagnóstico médico real. Sempre consulte um profissional de saúde qualificado.
        </div>

        <form id="uploadForm" enctype="multipart/form-data">
            <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📁</div>
                <p><strong>Clique para selecionar uma imagem de ECG</strong></p>
                <p style="color: #999; font-size: 0.9em; margin-top: 10px;">
                    Formatos aceitos: PNG, JPG, JPEG
                </p>
                <input type="file" id="fileInput" name="file" accept="image/*" required>
            </div>
            
            <img id="preview" alt="Preview da imagem">
            
            <button type="submit" class="btn" id="submitBtn" disabled>
                Classificar ECG
            </button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px;">Analisando imagem...</p>
        </div>

        <div id="result"></div>

        <div class="footer">
            <p>CardioAI - FIAP 2026</p>
            <p>Projeto Acadêmico de IA Aplicada à Cardiologia</p>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const preview = document.getElementById('preview');
        const submitBtn = document.getElementById('submitBtn');
        const uploadForm = document.getElementById('uploadForm');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');

        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    submitBtn.disabled = false;
                    result.style.display = 'none';
                }
                reader.readAsDataURL(file);
            }
        });

        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            submitBtn.disabled = true;
            loading.style.display = 'block';
            result.style.display = 'none';
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                loading.style.display = 'none';
                result.style.display = 'block';
                
                if (data.success) {
                    result.className = 'result-success';
                    result.innerHTML = `
                        <h3>✓ Classificação Concluída</h3>
                        <div class="prediction">Classe: ${data.prediction}</div>
                        <div class="confidence">Confiança: ${data.confidence}%</div>
                        <p style="margin-top: 15px; font-size: 0.9em;">
                            <strong>Lembre-se:</strong> Este resultado é apenas uma simulação acadêmica
                            e não substitui avaliação médica profissional.
                        </p>
                    `;
                } else {
                    result.className = 'result-error';
                    result.innerHTML = `
                        <h3>✗ Erro na Classificação</h3>
                        <p>${data.error}</p>
                    `;
                }
            } catch (error) {
                loading.style.display = 'none';
                result.style.display = 'block';
                result.className = 'result-error';
                result.innerHTML = `
                    <h3>✗ Erro de Conexão</h3>
                    <p>Não foi possível processar a imagem. Tente novamente.</p>
                `;
            }
            
            submitBtn.disabled = false;
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Página principal."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint para classificação de imagem."""
    if model is None:
        return jsonify({
            'success': False,
            'error': 'Modelo não carregado. Execute o treinamento primeiro.'
        }), 500
    
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Nenhum arquivo enviado.'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Arquivo vazio.'
        }), 400
    
    try:
        # Carrega e pré-processa a imagem
        image = Image.open(file.stream).convert('RGB')
        image = image.resize((256, 256))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        # Realiza a predição
        predictions = model.predict(image_array, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class] * 100)
        
        return jsonify({
            'success': True,
            'prediction': class_names[predicted_class],
            'confidence': round(confidence, 2),
            'all_probabilities': {
                class_names[i]: round(float(predictions[0][i] * 100), 2)
                for i in range(len(class_names))
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao processar imagem: {str(e)}'
        }), 500


@app.route('/health')
def health():
    """Endpoint de health check."""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'classes': class_names
    })


if __name__ == '__main__':
    load_model()
    print("\n" + "="*60)
    print("🫀 CardioAI - Classificador de ECG")
    print("="*60)
    print("\n⚠️  AVISO: Protótipo acadêmico - NÃO usar para diagnóstico real\n")
    print("Acesse: http://localhost:5000")
    print("\nPressione Ctrl+C para encerrar\n")
    app.run(debug=True, host='0.0.0.0', port=5000)


# Made with Bob