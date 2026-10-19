"""Configurações centrais da Fase 6: caminhos, features, limiares e parâmetros de ambiente."""

from pathlib import Path
import os
from dotenv import load_dotenv

# Diretórios base
FASE06_DIR = Path(__file__).resolve().parent.parent

# Carrega variáveis de ambiente a partir de .env da Fase 6 e da raiz
load_dotenv(FASE06_DIR / ".env")
load_dotenv()
DATA_DIR = FASE06_DIR / "data"
MODELS_DIR = FASE06_DIR / "models"
REPORTS_DIR = FASE06_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
DOCS_DIR = FASE06_DIR / "docs"

# Garante a existência dos diretórios principais
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Arquivos de dados e modelo
DATASET_CSV_PATH = DATA_DIR / "base_sintetica_pico_risco.csv"
MODEL_JOBLIB_PATH = MODELS_DIR / "modelo_pico_risco.joblib"
SESSIONS_DB_PATH = DATA_DIR / "sessions.db"

# Ordem fixa das 10 features exigidas pela especificação
FEATURES = [
    "idade_media",
    "carga_sistema",
    "tempo_espera",
    "fc_media",
    "spo2_media",
    "pa_sistolica",
    "temperatura",
    "densidade_eventos",
    "eventos_24h",
    "disponibilidade_recursos"
]

# Limiares de classificação de risco previstos no enunciado
LIMIAR_RISCO_BAIXO = 0.40
LIMIAR_RISCO_ALTO = 0.70

def classificar_risco(probabilidade: float) -> str:
    """Classifica a probabilidade de risco em BAIXO, MODERADO ou ALTO."""
    if probabilidade < LIMIAR_RISCO_BAIXO:
        return "BAIXO"
    elif probabilidade < LIMIAR_RISCO_ALTO:
        return "MODERADO"
    else:
        return "ALTO"

# Parâmetros de geração sintética
RANDOM_SEED = 42
N_SAMPLES = 5000

# Modelo LLM padrão para os agentes
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
