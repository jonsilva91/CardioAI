import os
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Configuração de Logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("CardioAI_Backend")

import sys

# 1. Configuração de Diretórios e sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

PHASE_ROOT = BASE_DIR.parent
ENV_PATH = PHASE_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info(f"Variáveis de ambiente carregadas de: {ENV_PATH}")
else:
    load_dotenv()
    logger.info("Variáveis de ambiente carregadas do ambiente padrão.")

# Variáveis do Servidor e Watson (sem portas ou URLs hardcoded)
PORT = int(os.getenv("PORT", os.getenv("FLASK_PORT", 5001)))
HOST = os.getenv("HOST", "0.0.0.0")
DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", 1800))

WATSON_APIKEY = os.getenv("WATSONX_ASSISTANT_APIKEY")
WATSON_URL = os.getenv("WATSONX_ASSISTANT_URL")
WATSON_ASSISTANT_ID = os.getenv("WATSONX_ASSISTANT_ID")
WATSON_VERSION = os.getenv("WATSONX_ASSISTANT_VERSION", "2023-06-15")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "conversation_log.db"

# Try importing ibm-watson
try:
    from ibm_watson import AssistantV2
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    from ibm_cloud_sdk_core import ApiException
    WATSON_SDK_AVAILABLE = True
except ImportError:
    WATSON_SDK_AVAILABLE = False
    ApiException = Exception

from intent_engine import LocalIntentEngine
from session_manager import WatsonSessionManager

# Inicialização da Aplicação Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})

# Motor local de regras para fallback
local_engine = LocalIntentEngine()

# Configuração do Watson Assistant e do Gerenciador de Sessão Individual
assistant = None
watson_available = False

if WATSON_SDK_AVAILABLE and WATSON_APIKEY and WATSON_URL and WATSON_ASSISTANT_ID:
    try:
        authenticator = IAMAuthenticator(WATSON_APIKEY)
        assistant = AssistantV2(
            version=WATSON_VERSION,
            authenticator=authenticator
        )
        assistant.set_service_url(WATSON_URL)
        session_manager = WatsonSessionManager(
            assistant_client=assistant,
            assistant_id=WATSON_ASSISTANT_ID,
            ttl_seconds=SESSION_TTL_SECONDS
        )
        watson_available = True
        logger.info("✓ Watson Assistant conectado com sucesso. Gerenciamento de sessão individual ativo.")
    except Exception as e:
        logger.error(f"⚠️ Erro ao configurar Watson Assistant: {e}")
        session_manager = WatsonSessionManager(ttl_seconds=SESSION_TTL_SECONDS)
        watson_available = False
else:
    logger.warning("⚠️ Credenciais do Watson Assistant ausentes ou SDK indisponível. Operando em Fallback Local.")
    session_manager = WatsonSessionManager(ttl_seconds=SESSION_TTL_SECONDS)
    watson_available = False


def init_db():
    """Inicializa banco de logs SQLite se não existir e migra schema para incluir session_id."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT,
            user_message TEXT,
            bot_response TEXT,
            intent TEXT,
            is_urgent BOOLEAN,
            source TEXT
        )
    ''')
    # Checagem retrocompatível para adicionar session_id caso a tabela seja de versão anterior
    cursor.execute("PRAGMA table_info(conversation_logs)")
    columns = [row[1] for row in cursor.fetchall()]
    if "session_id" not in columns:
        cursor.execute("ALTER TABLE conversation_logs ADD COLUMN session_id TEXT")
    conn.commit()
    conn.close()


def log_conversation(session_id, user_message, bot_response, intent, is_urgent, source):
    """Salva log da conversa com o identificador de sessão correspondente no SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversation_logs (session_id, timestamp, user_message, bot_response, intent, is_urgent, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, datetime.now().isoformat(), user_message, bot_response, intent, is_urgent, source))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Erro ao salvar log de conversa no SQLite: {e}")


# Explicações clínicas por classe alinhadas à Fase 4 (CNN ECG)
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

CLASS_SYNONYMS = {
    "N": ["classe n", "normal"],
    "S": ["classe s", "supraventricular"],
    "V": ["classe v", "ventricular"],
    "F": ["classe f", "fusão", "fusao"],
    "Q": ["classe q", "não classificável", "nao classificavel", "desconhecido"],
}


def _extrair_classe_do_texto(user_message):
    """Fallback: identifica a classe citada diretamente no texto do usuário."""
    texto = user_message.lower()
    for classe, sinonimos in CLASS_SYNONYMS.items():
        if any(s in texto for s in sinonimos):
            return classe
    return None


def get_ecg_class_info(intent, user_message, watson_entities=None):
    """
    Busca classes de ECG da Fase 4 e anexa explicação clínica contextualizada.
    """
    if intent != "duvida_ecg":
        return None

    class_names_path = PROJECT_ROOT / "phases" / "fase04_cnn_ecg" / "outputs" / "models" / "class_names.json"
    classes = ["F", "N", "Q", "S", "V"]
    if class_names_path.exists():
        try:
            with open(class_names_path, 'r', encoding='utf-8') as f:
                classes = json.load(f)
        except Exception:
            pass

    classe_citada = None
    if watson_entities:
        for entity in watson_entities:
            if entity.get('entity') == 'classe_ecg':
                classe_citada = entity.get('value', '').upper()
                break

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
    """
    Endpoint principal de chat:
    - Recebe a mensagem e opcionalmente o session_id do cliente.
    - Mantém a sessão individualizada no Watson Assistant.
    - Se a sessão expirou na IBM ou localmente, recria e responde sem erro.
    - Retorna o session_id ativo para o frontend persistir na conversa.
    """
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'Mensagem não fornecida'}), 400

    user_message = data['message']
    client_session_id = data.get('session_id') or data.get('sessionId')

    # 1. Tenta Watson Assistant se disponível
    if watson_available:
        try:
            watson_response, active_session_id, is_new_session = session_manager.send_message(
                text=user_message,
                session_id=client_session_id
            )

            # Extração de respostas de texto
            bot_text = ""
            if 'output' in watson_response and 'generic' in watson_response['output']:
                for item in watson_response['output']['generic']:
                    if item.get('response_type') == 'text':
                        bot_text += item.get('text', '') + "\n"

            # Extração de intenções
            intent = "unknown"
            intents = watson_response.get('output', {}).get('intents', [])
            if intents:
                intent = intents[0].get('intent', 'unknown')

            is_urgent = (intent == "emergencia")

            watson_entities = watson_response.get('output', {}).get('entities', [])
            ecg_info = get_ecg_class_info(intent, user_message, watson_entities)
            if ecg_info:
                bot_text += ecg_info

            bot_text = bot_text.strip()
            log_conversation(active_session_id, user_message, bot_text, intent, is_urgent, "watson")

            return jsonify({
                'response': bot_text,
                'intent': intent,
                'urgent': is_urgent,
                'source': 'watson',
                'session_id': active_session_id,
                'is_new_session': is_new_session
            })

        except Exception as e:
            logger.error(f"Erro na API do Watson Assistant: {e}. Acionando Fallback Local.")

    # 2. Modo Fallback Local (quando Watson falha ou credenciais não existem)
    active_session_id = client_session_id or session_manager.create_session()
    session_manager.touch_session(active_session_id)

    bot_response, intent, is_urgent = local_engine.process_message(user_message)
    ecg_info = get_ecg_class_info(intent, user_message)
    if ecg_info:
        bot_response += ecg_info

    log_conversation(active_session_id, user_message, bot_response, intent, is_urgent, "local_fallback")

    return jsonify({
        'response': bot_response,
        'intent': intent,
        'urgent': is_urgent,
        'source': 'local_fallback',
        'session_id': active_session_id,
        'is_new_session': False
    })


@app.route('/chat/session', methods=['POST', 'GET'])
def create_session():
    """
    Endpoint para inicializar antecipadamente uma sessão individual do Watson Assistant.
    """
    try:
        new_sid = session_manager.create_session()
        return jsonify({
            'status': 'created',
            'session_id': new_sid,
            'watson_available': watson_available
        })
    except Exception as e:
        logger.error(f"Erro ao criar sessão explícita: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/chat/session/close', methods=['POST'])
@app.route('/chat/reset', methods=['POST'])
def close_session():
    """
    Endpoint para encerramento explícito de sessão.
    Libera a sessão no Watson Assistant (delete_session) e remove do cache local.
    """
    data = request.json or {}
    sid = data.get('session_id') or data.get('sessionId') or request.args.get('session_id')
    if not sid:
        return jsonify({'error': 'session_id não informado para encerramento'}), 400

    success = session_manager.delete_session(sid)
    logger.info(f"Encerramento de sessão solicitado para {sid}. Sucesso: {success}")
    return jsonify({
        'status': 'closed' if success else 'not_found',
        'session_id': sid
    })


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de verificação de integridade do serviço e contagem de sessões ativas."""
    return jsonify({
        'status': 'ok',
        'watson_available': watson_available,
        'active_sessions_tracked': len(session_manager._sessions),
        'watson_version': WATSON_VERSION,
        'port': PORT
    })


if __name__ == '__main__':
    init_db()
    logger.info(f"Iniciando backend CardioAI (Fase 5) em {HOST}:{PORT} (Debug={DEBUG})...")
    app.run(host=HOST, port=PORT, debug=DEBUG)