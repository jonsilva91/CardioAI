"""Configurações centrais do Backend da Fase 7 e integração de caminho com a Fase 6.

Este módulo resolve dinamicamente o caminho para `phases/fase06_preditivo_multiagente`
e o adiciona ao `sys.path` para permitir a importação direta de `src.predictor`,
`src.protocols` e `src.agents_system` sem duplicação de código.

Também define e documenta o Cenário Hospitalar Padrão (`CENARIO_PADRAO`) utilizado
para complementar as variáveis fisiológicas enviadas pelo dispositivo IoT
(`fc_media`, `temperatura`, `spo2_media`), formando o vetor completo de 10 features
exigido pelo modelo preditivo da Fase 6.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import secrets
import sys
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Resolução de diretórios a partir da localização deste arquivo (app/config.py)
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
FASE07_DIR = BACKEND_DIR.parent
PHASES_DIR = FASE07_DIR.parent
REPO_ROOT = PHASES_DIR.parent
FASE06_DIR = PHASES_DIR / "fase06_preditivo_multiagente"

# Adiciona phases/fase06_preditivo_multiagente ao sys.path (sem copiar código)
if str(FASE06_DIR) not in sys.path:
    sys.path.insert(0, str(FASE06_DIR))

# Carrega variáveis de ambiente (priorizando o .env do backend da Fase 7,
# com fallback para o .env da Fase 6 e da raiz do repositório)
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(FASE06_DIR / ".env")
load_dotenv(REPO_ROOT / ".env")

# ============================================================================
# CENÁRIO HOSPITALAR PADRÃO (Baseline Contextual para Telemetria IoT)
# ============================================================================
# Justificativa clínica e arquitetural:
# O dispositivo vestível / beira-leito IoT (ESP32) coleta em tempo real 3 sinais vitais
# diretos do paciente: frequência cardíaca (`fc_media`), temperatura (`temperatura`) e
# saturação periférica de oxigênio (`spo2_media`).
# O modelo preditivo da Fase 6 requer 10 variáveis (sinais vitais + contexto clínico e
# operacional hospitalar). O backend completa as 7 variáveis contextuais com este
# cenário padrão representativo de um paciente adulto/idoso (62 anos), normotenso na
# triagem inicial (PA sistólica 120 mmHg), inserido em uma unidade hospitalar sob
# operação moderada (carga de 60%, espera de 40 min, disponibilidade de 60% de recursos,
# densidade de 3 eventos e 2 eventos nas últimas 24h).
# Dessa forma, alterações agudas captadas pelo sensor IoT (como taquicardia FC > 110 bpm
# combinada com hipóxia SpO2 < 92%) elevam imediatamente o risco previsto para ALTO.
CENARIO_PADRAO: dict[str, float] = {
    "idade_media": 62.0,
    "carga_sistema": 60.0,
    "tempo_espera": 40.0,
    "pa_sistolica": 120.0,
    "densidade_eventos": 3.0,
    "eventos_24h": 2.0,
    "disponibilidade_recursos": 60.0,
}

# Limites operacionais e mensagens padronizadas
MAX_LEITURAS_POR_PACIENTE: int = 200
RECOMENDACAO_COOLDOWN_SECONDS: float = 30.0
DISCLAIMER_FIXO: str = "Não substitui avaliação médica."

# Segredo JWT efêmero por processo (utilizado apenas quando APP_ENV=dev e JWT_SECRET está ausente)
_DEV_JWT_SECRET: str | None = None


def get_app_env() -> str:
    """Retorna o ambiente de execução configurado em APP_ENV."""
    return os.getenv("APP_ENV", "").strip().lower()


def get_openai_api_key() -> str:
    """Retorna a chave da OpenAI configurada no ambiente (ou string vazia se ausente)."""
    return os.getenv("OPENAI_API_KEY", "").strip()


def has_openai_api_key() -> bool:
    """Indica se há uma OPENAI_API_KEY configurada (True/False, nunca expõe o valor)."""
    return bool(get_openai_api_key())


def get_openai_model() -> str:
    """Retorna o modelo OpenAI configurado via OPENAI_MODEL (padrão: gpt-4o-mini)."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def get_jwt_secret() -> str:
    """Retorna o segredo de assinatura JWT configurado em JWT_SECRET.

    Se ausente/vazio:
    - Em APP_ENV=dev: gera segredo aleatório por processo via secrets.token_urlsafe e emite warning.
    - Caso contrário: lança RuntimeError informando que JWT_SECRET é obrigatório.
    """
    global _DEV_JWT_SECRET
    secret = os.getenv("JWT_SECRET", "").strip()
    if secret:
        return secret

    if get_app_env() == "dev":
        if _DEV_JWT_SECRET is None:
            _DEV_JWT_SECRET = secrets.token_urlsafe(32)
            logger.warning(
                "APP_ENV=dev e JWT_SECRET não definido: gerado JWT_SECRET aleatório efêmero para este processo."
            )
        return _DEV_JWT_SECRET

    raise RuntimeError(
        "Configuração obrigatória ausente: a variável de ambiente 'JWT_SECRET' deve ser definida (ou use APP_ENV=dev em desenvolvimento)."
    )


def get_jwt_algorithm() -> str:
    """Algoritmo padrão de assinatura JWT."""
    return "HS256"


def get_jwt_exp_minutes() -> int:
    """Tempo de expiração do token JWT em minutos."""
    try:
        return int(os.getenv("JWT_EXP_MINUTES", "480"))
    except ValueError:
        return 480


def get_device_token() -> str:
    """Retorna o token obrigatório esperado no header X-Device-Token para ingestão IoT."""
    token = os.getenv("DEVICE_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Configuração obrigatória ausente: a variável de ambiente 'DEVICE_TOKEN' não está definida."
        )
    return token


def get_demo_email() -> str:
    """Retorna o e-mail obrigatório do usuário de demonstração autorizado no login."""
    email = os.getenv("DEMO_EMAIL", "").strip()
    if not email:
        raise RuntimeError(
            "Configuração obrigatória ausente: a variável de ambiente 'DEMO_EMAIL' não está definida."
        )
    return email


def get_demo_password() -> str:
    """Retorna a senha obrigatória do usuário de demonstração autorizado no login."""
    password = os.getenv("DEMO_PASSWORD", "").strip()
    if not password:
        raise RuntimeError(
            "Configuração obrigatória ausente: a variável de ambiente 'DEMO_PASSWORD' não está definida."
        )
    return password


def get_allowed_origins() -> list[str]:
    """Retorna a lista de origens permitidas pelo CORS a partir de ALLOWED_ORIGINS (padrão localhost)."""
    raw = (
        os.getenv("ALLOWED_ORIGINS", "").strip()
        or "http://localhost:5173,http://localhost:3000"
    )
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins


def validar_configuracao_obrigatoria() -> None:
    """Valida no startup se todas as variáveis obrigatórias estão preenchidas (sem exibir valores)."""
    faltantes: list[str] = []

    if not os.getenv("JWT_SECRET", "").strip():
        if get_app_env() == "dev":
            get_jwt_secret()
        else:
            faltantes.append("JWT_SECRET")

    for var_name in ("DEVICE_TOKEN", "DEMO_EMAIL", "DEMO_PASSWORD"):
        if not os.getenv(var_name, "").strip():
            faltantes.append(var_name)

    if faltantes:
        lista_str = ", ".join(faltantes)
        raise RuntimeError(
            f"Falha no startup do backend: variáveis de ambiente obrigatórias ausentes ou vazias: {lista_str}."
        )
