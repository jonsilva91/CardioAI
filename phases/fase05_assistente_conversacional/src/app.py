import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Try importing ibm-watson
try:
    from ibm_watson import AssistantV2
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    WATSON_SDK_AVAILABLE = True
except ImportError:
    WATSON_SDK_AVAILABLE = False

from intent_engine import LocalIntentEngine

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "phases" / "fase05_assistente_conversacional" / "src" / "conversation_log.db"

# Local engine fallback
local_engine = LocalIntentEngine()

# Setup Watson Assistant
authenticator = None
assistant = None
watson_available = False
session_id = None

WATSON_APIKEY = os.getenv("WATSONX_ASSISTANT_APIKEY")
WATSON_URL = os.getenv("WATSONX_ASSISTANT_URL")
WATSON_ASSISTANT_ID = os.getenv("WATSONX_ASSISTANT_ID")

if WATSON_SDK_AVAILABLE and WATSON_APIKEY and WATSON_URL and WATSON_ASSISTANT_ID:
    try:
        authenticator = IAMAuthenticator(WATSON_APIKEY)
        assistant = AssistantV2(
            version='2023-06-15',
            authenticator=authenticator
        )
        assistant.set_service_url(WATSON_URL)
        watson_available = True
        print("✓ Watson Assistant configurado com sucesso.")
    except Exception as e:
        print(f"⚠️ Erro ao configurar Watson Assistant: {e}")
        watson_available = False
else:
    print("⚠️ Credenciais do Watson Assistant não encontradas ou SDK não instalado.")
    print("Modo Fallback Local ativado.")

def init_db():
    """Inicializa banco de logs se não existir."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_message TEXT,
            bot_response TEXT,
            intent TEXT,
            is_urgent BOOLEAN,
            source TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_conversation(user_message, bot_response, intent, is_urgent, source):
    """Salva log da conversa no SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_logs (timestamp, user_message, bot_response, intent, is_urgent, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), user_message, bot_response, intent, is_urgent, source))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar log: {e}")

# Explicações clínicas por classe, alinhadas ao classificador da Fase 4 (dataset estilo MIT-BIH)
CLASS_EXPLANATIONS = {
    "N": "Normal — batimento cardíaco dentro do padrão esperado, sem sinais de arritmia.",
    "S": "Supraventricular — batimento ectópico originado acima dos ventrículos (ex.: átrios). "
         "Pode estar associado a arritmias como fibrilação atrial e merece acompanhamento médico.",
    "V": "Ventricular — batimento ectópico originado nos ventrículos. Merece atenção médica, "
         "especialmente se for frequente ou vier acompanhado de sintomas.",
    "F": "Fusão — ocorre quando um batimento normal e um batimento ectópico acontecem quase ao "
         "mesmo tempo, se sobrepondo no registro do ECG.",
    "Q": "Não classificável — o padrão do batimento não se encaixou claramente nas outras "
         "categorias; recomenda-se revisão por um profissional.",
}

# Sinônimos aceitos na fala do usuário para cada classe (usado no fallback local, sem Watson)
CLASS_SYNONYMS = {
    "N": ["classe n", "normal"],
    "S": ["classe s", "supraventricular"],
    "V": ["classe v", "ventricular"],
    "F": ["classe f", "fusão", "fusao"],
    "Q": ["classe q", "não classificável", "nao classificavel", "desconhecido"],
}


def _extrair_classe_do_texto(user_message):
    """Fallback: tenta achar a classe citada direto no texto do usuário (usado quando não há Watson)."""
    texto = user_message.lower()
    for classe, sinonimos in CLASS_SYNONYMS.items():
        if any(s in texto for s in sinonimos):
            return classe
    return None


def get_ecg_class_info(intent, user_message, watson_entities=None):
    """
    Busca as classes reais de ECG da Fase 4 e, se o usuário citou uma classe específica
    (via entity @classe_ecg do Watson ou por texto no fallback local), devolve a explicação
    daquela classe. Caso contrário, devolve a lista geral das classes suportadas.
    """
    if intent != "duvida_ecg":
        return None

    class_names_path = PROJECT_ROOT / "phases" / "fase04_cnn_ecg" / "outputs" / "models" / "class_names.json"

    classes = ["F", "N", "Q", "S", "V"]  # Fallback
    if class_names_path.exists():
        try:
            with open(class_names_path, 'r', encoding='utf-8') as f:
                classes = json.load(f)
        except Exception:
            pass

    # 1) Tenta pegar a classe direto da entity reconhecida pelo Watson
    classe_citada = None
    if watson_entities:
        for entity in watson_entities:
            if entity.get('entity') == 'classe_ecg':
                classe_citada = entity.get('value', '').upper()
                break

    # 2) Se não veio do Watson (ou estamos no fallback local), tenta achar no texto
    if not classe_citada:
        classe_citada = _extrair_classe_do_texto(user_message)

    if classe_citada and classe_citada in CLASS_EXPLANATIONS:
        return (
            f"\n\n**Classe {classe_citada}**: {CLASS_EXPLANATIONS[classe_citada]}\n\n"
            f"(Classes reconhecidas pelo nosso classificador da Fase 4: {', '.join(classes)}.)"
        )

    return f"\n\nContexto: Nosso classificador atual (Fase 4) reconhece as seguintes classes: {', '.join(classes)}."


@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal de chat."""
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Mensagem não fornecida'}), 400
        
    user_message = data['message']
    
    # Tenta Watson Assistant primeiro
    if watson_available:
        try:
            global session_id
            if not session_id:
                response = assistant.create_session(assistant_id=WATSON_ASSISTANT_ID).get_result()
                session_id = response['session_id']
                
            response = assistant.message(
                assistant_id=WATSON_ASSISTANT_ID,
                session_id=session_id,
                input={
                    'message_type': 'text',
                    'text': user_message
                }
            ).get_result()
            
            # Extrair resposta
            bot_text = ""
            if 'output' in response and 'generic' in response['output']:
                for item in response['output']['generic']:
                    if item['response_type'] == 'text':
                        bot_text += item['text'] + "\n"
                        
            # Extrair intent
            intent = "unknown"
            if 'output' in response and 'intents' in response['output'] and len(response['output']['intents']) > 0:
                intent = response['output']['intents'][0]['intent']
                
            is_urgent = intent == "emergencia"

            watson_entities = response.get('output', {}).get('entities', [])
            bot_text += get_ecg_class_info(intent, user_message, watson_entities) or ""
            
            log_conversation(user_message, bot_text.strip(), intent, is_urgent, "watson")
            
            return jsonify({
                'response': bot_text.strip(),
                'intent': intent,
                'urgent': is_urgent,
                'source': 'watson'
            })
            
        except Exception as e:
            print(f"Erro na API do Watson, usando fallback local: {e}")
            session_id = None # Reset session on error
    
    # Fallback Local
    bot_response, intent, is_urgent = local_engine.process_message(user_message)
    bot_response += get_ecg_class_info(intent, user_message) or ""
    
    log_conversation(user_message, bot_response, intent, is_urgent, "local_fallback")
    
    return jsonify({
        'response': bot_response,
        'intent': intent,
        'urgent': is_urgent,
        'source': 'local_fallback'
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'watson_available': watson_available
    })


if __name__ == '__main__':
    init_db()
    print("Iniciando backend Flask (Fase 5)")
    app.run(port=5001, debug=True)