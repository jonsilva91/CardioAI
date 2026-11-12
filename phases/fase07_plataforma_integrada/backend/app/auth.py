"""Autenticação JWT para usuários do portal e validação de token de dispositivo IoT."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hmac
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.config import (
    get_demo_email,
    get_demo_password,
    get_device_token,
    get_jwt_algorithm,
    get_jwt_exp_minutes,
    get_jwt_secret,
)

security_bearer = HTTPBearer(auto_error=False)


def verificar_credenciais_demo(email: str, senha: str) -> bool:
    """Compara de forma segura o e-mail e a senha com DEMO_EMAIL e DEMO_PASSWORD."""
    email_esperado = get_demo_email()
    senha_esperada = get_demo_password()
    email_ok = hmac.compare_digest(email.strip().lower(), email_esperado.strip().lower())
    senha_ok = hmac.compare_digest(senha, senha_esperada)
    return bool(email_ok and senha_ok)


def criar_token_jwt(email: str) -> tuple[str, int]:
    """Gera um token JWT assinado para o usuário autenticado.

    Returns:
        Tupla (token_jwt, expires_in_seconds)
    """
    exp_minutes = get_jwt_exp_minutes()
    agora = datetime.now(timezone.utc)
    expiracao = agora + timedelta(minutes=exp_minutes)
    payload: dict[str, Any] = {
        "sub": email,
        "iat": int(agora.timestamp()),
        "exp": int(expiracao.timestamp()),
        "role": "clinico_demo",
    }
    token = jwt.encode(payload, get_jwt_secret(), algorithm=get_jwt_algorithm())
    return token, exp_minutes * 60


def exigir_jwt(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
) -> dict[str, Any]:
    """Dependência FastAPI que valida o token Bearer JWT nas rotas protegidas."""
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais JWT ausentes. Envie o header Authorization: Bearer <token>.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            get_jwt_secret(),
            algorithms=[get_jwt_algorithm()],
        )
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT expirado. Realize login novamente.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def exigir_device_token(
    x_device_token: str | None = Header(default=None, alias="X-Device-Token"),
) -> str:
    """Dependência FastAPI que valida o header X-Device-Token enviado pelo dispositivo IoT."""
    token_esperado = get_device_token()
    if not x_device_token or not hmac.compare_digest(x_device_token.strip(), token_esperado):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header X-Device-Token inválido ou ausente.",
        )
    return x_device_token

