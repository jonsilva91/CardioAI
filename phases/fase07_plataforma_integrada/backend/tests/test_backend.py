"""Suíte de testes automatizados (pytest) do Backend FastAPI da Fase 7.

Todos os testes rodam localmente usando o modelo preditivo REAL e os protocolos
determinísticos REAIS da Fase 6, SEM realizar chamadas de rede para a API da OpenAI.
"""

from __future__ import annotations

import logging
import os
from types import SimpleNamespace
from fastapi.testclient import TestClient
import pytest

# Garante variáveis mínimas para o import inicial do módulo app.main caso não haja .env
os.environ.setdefault("JWT_SECRET", "segredo-jwt-inicial-para-import-de-teste-32b")
os.environ.setdefault("DEVICE_TOKEN", "token-iot-inicial-teste")
os.environ.setdefault("DEMO_EMAIL", "clinico.teste@cardioai.local")
os.environ.setdefault("DEMO_PASSWORD", "SenhaForteTeste!2026")

import app.config as app_config
from app.config import CENARIO_PADRAO, DISCLAIMER_FIXO
from app.main import criar_app
from app.store import store
import src.agents_system as fase06_agents


@pytest.fixture(autouse=True)
def limpar_estado_e_ambiente(monkeypatch: pytest.MonkeyPatch):
    """Define variáveis obrigatórias via monkeypatch e limpa o store antes de cada teste."""
    store.limpar_tudo()
    app_config._DEV_JWT_SECRET = None
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEMO_EMAIL", "clinico.teste@cardioai.local")
    monkeypatch.setenv("DEMO_PASSWORD", "SenhaForteTeste!2026")
    monkeypatch.setenv("JWT_SECRET", "segredo-jwt-de-teste-unitario-com-mais-de-32-bytes")
    monkeypatch.setenv("DEVICE_TOKEN", "token-iot-teste-2026")
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:5173,https://cardioai.vercel.app")
    yield
    store.limpar_tudo()


@pytest.fixture
def client() -> TestClient:
    """Retorna um TestClient com a aplicação FastAPI recém-configurada."""
    return TestClient(criar_app())


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Autentica com o usuário configurado no ambiente de teste e retorna Authorization Bearer."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "clinico.teste@cardioai.local", "senha": "SenhaForteTeste!2026"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def device_headers() -> dict[str, str]:
    """Retorna o cabeçalho X-Device-Token válido para o dispositivo IoT."""
    return {"X-Device-Token": "token-iot-teste-2026"}


def test_startup_falha_quando_variaveis_obrigatorias_ausentes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que a aplicação falha no startup indicando claramente qual variável falta."""
    for var_obrigatoria in ("JWT_SECRET", "DEVICE_TOKEN", "DEMO_EMAIL", "DEMO_PASSWORD"):
        monkeypatch.setenv("JWT_SECRET", "segredo-jwt-de-teste-unitario-com-mais-de-32-bytes")
        monkeypatch.setenv("DEVICE_TOKEN", "token-iot-teste-2026")
        monkeypatch.setenv("DEMO_EMAIL", "clinico.teste@cardioai.local")
        monkeypatch.setenv("DEMO_PASSWORD", "SenhaForteTeste!2026")
        monkeypatch.setenv(var_obrigatoria, "")

        with pytest.raises(RuntimeError) as exc_info:
            criar_app()
        assert var_obrigatoria in str(exc_info.value)


def test_app_env_dev_gera_jwt_secret_aleatorio_mas_exige_demais_variaveis(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Se APP_ENV=dev, gera JWT_SECRET aleatório e loga aviso; DEMO_* e DEVICE_TOKEN seguem obrigatórios."""
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("JWT_SECRET", "")
    app_config._DEV_JWT_SECRET = None

    with caplog.at_level(logging.WARNING):
        app_dev = criar_app()
        assert app_dev is not None
        segredo_gerado = app_config.get_jwt_secret()
        assert len(segredo_gerado) >= 32
        assert "APP_ENV=dev" in caplog.text

    # Mesmo em APP_ENV=dev, DEVICE_TOKEN e DEMO_* continuam obrigatórios
    monkeypatch.setenv("DEVICE_TOKEN", "")
    with pytest.raises(RuntimeError, match="DEVICE_TOKEN"):
        criar_app()


def test_health_endpoint_nunca_expoe_valor_da_chave(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Valida GET /health: modelo carregado e flag booleana de OPENAI_API_KEY sem expor o segredo."""
    segredo_falso = "sk-segredo-super-confidencial-nao-expor"
    monkeypatch.setenv("OPENAI_API_KEY", segredo_falso)

    resp = client.get("/health")
    assert resp.status_code == 200
    dados = resp.json()
    assert dados["status"] == "ok"
    assert dados["modelo_carregado"] is True
    assert isinstance(dados["openai_api_key"], bool)
    assert dados["openai_api_key"] is True
    assert segredo_falso not in resp.text

    monkeypatch.setenv("OPENAI_API_KEY", "")
    resp_sem_chave = client.get("/health")
    assert resp_sem_chave.status_code == 200
    assert resp_sem_chave.json()["openai_api_key"] is False


def test_login_sucesso_e_falha(client: TestClient) -> None:
    """Testa login com credenciais válidas e rejeição (401) com senha inválida."""
    resp_ok = client.post(
        "/api/auth/login",
        json={"email": "clinico.teste@cardioai.local", "senha": "SenhaForteTeste!2026"},
    )
    assert resp_ok.status_code == 200
    body = resp_ok.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    resp_err = client.post(
        "/api/auth/login",
        json={"email": "clinico.teste@cardioai.local", "senha": "senha-errada"},
    )
    assert resp_err.status_code == 401


def test_telemetria_exige_device_token_e_valida_faixas(
    client: TestClient,
    device_headers: dict[str, str],
) -> None:
    """Garante que X-Device-Token inválido retorna 401 e valores fora de faixa retornam 422."""
    payload_valido = {
        "device_id": "esp32-uti-01",
        "paciente_id": "pac-001",
        "fc_media": 78.0,
        "temperatura": 36.6,
        "spo2_media": 97.0,
    }
    resp_sem_token = client.post("/api/telemetria", json=payload_valido)
    assert resp_sem_token.status_code == 401

    resp_token_errado = client.post(
        "/api/telemetria",
        json=payload_valido,
        headers={"X-Device-Token": "token-invalido"},
    )
    assert resp_token_errado.status_code == 401

    # Faixas inválidas (FC < 30, SpO2 > 100)
    resp_faixa_invalida = client.post(
        "/api/telemetria",
        json={
            "device_id": "esp32-uti-01",
            "paciente_id": "pac-001",
            "fc_media": 10.0,
            "temperatura": 36.6,
            "spo2_media": 105.0,
        },
        headers=device_headers,
    )
    assert resp_faixa_invalida.status_code == 422


def test_modelo_real_fc_maior_110_e_spo2_menor_92_sobe_risco_para_alto(
    client: TestClient,
    device_headers: dict[str, str],
) -> None:
    """Prova com o modelo REAL da Fase 6 que FC > 110 e SpO2 < 92 elevam o risco para ALTO."""
    assert CENARIO_PADRAO == {
        "idade_media": 62.0,
        "carga_sistema": 60.0,
        "tempo_espera": 40.0,
        "pa_sistolica": 120.0,
        "densidade_eventos": 3.0,
        "eventos_24h": 2.0,
        "disponibilidade_recursos": 60.0,
    }

    # 1. Leitura basal estável -> Risco BAIXO
    resp_estavel = client.post(
        "/api/telemetria",
        json={
            "device_id": "esp32-leito-01",
            "paciente_id": "paciente-real-01",
            "fc_media": 75.0,
            "temperatura": 36.5,
            "spo2_media": 98.0,
        },
        headers=device_headers,
    )
    assert resp_estavel.status_code == 200
    dados_estavel = resp_estavel.json()
    assert dados_estavel["classificacao"] == "BAIXO"
    assert dados_estavel["alerta"] is False

    # 2. Leitura crítica (FC > 110 e SpO2 < 92) -> Risco deve subir para ALTO no modelo real
    resp_critico = client.post(
        "/api/telemetria",
        json={
            "device_id": "esp32-leito-01",
            "paciente_id": "paciente-real-01",
            "fc_media": 115.0,
            "temperatura": 37.4,
            "spo2_media": 90.0,
        },
        headers=device_headers,
    )
    assert resp_critico.status_code == 200
    dados_critico = resp_critico.json()
    assert dados_critico["classificacao"] == "ALTO"
    assert dados_critico["probabilidade"] >= 0.70
    assert dados_critico["alerta"] is True
    assert "Se risco sistêmico alto → ativar estado de emergência" in dados_critico["protocolos"]


def test_status_e_historico_paciente_com_limite_200_leituras(
    client: TestClient,
    auth_headers: dict[str, str],
    device_headers: dict[str, str],
) -> None:
    """Valida GET /api/pacientes/{id}/status e retenção máxima de 200 leituras no histórico."""
    # Sem leituras -> 404
    resp_404 = client.get("/api/pacientes/inexistente/status", headers=auth_headers)
    assert resp_404.status_code == 404

    # Insere 205 leituras para verificar truncamento em 200
    for i in range(205):
        r = client.post(
            "/api/telemetria",
            json={
                "device_id": "esp32-stress",
                "paciente_id": "pac-200",
                "fc_media": 70.0 + (i % 30),
                "temperatura": 36.5,
                "spo2_media": 96.0,
            },
            headers=device_headers,
        )
        assert r.status_code == 200

    resp_status = client.get("/api/pacientes/pac-200/status", headers=auth_headers)
    assert resp_status.status_code == 200
    st = resp_status.json()
    assert st["paciente_id"] == "pac-200"
    assert st["idade_leitura_segundos"] >= 0.0
    assert "ultima_leitura" in st
    assert "risco" in st
    assert "protocolos" in st

    resp_hist = client.get("/api/pacientes/pac-200/historico?limite=50", headers=auth_headers)
    assert resp_hist.status_code == 200
    hist = resp_hist.json()
    assert hist["total_armazenado"] == 200
    assert len(hist["leituras"]) == 50


def test_sem_openai_api_key_recomendacao_e_chat_retornam_503(
    client: TestClient,
    auth_headers: dict[str, str],
    device_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sem OPENAI_API_KEY, /recomendacao e /chat devem retornar 503 com mensagem clara (nunca simular)."""
    monkeypatch.setenv("OPENAI_API_KEY", "")

    client.post(
        "/api/telemetria",
        json={
            "device_id": "esp32-01",
            "paciente_id": "pac-503",
            "fc_media": 118.0,
            "temperatura": 37.8,
            "spo2_media": 89.0,
        },
        headers=device_headers,
    )

    resp_rec = client.post("/api/pacientes/pac-503/recomendacao", headers=auth_headers)
    assert resp_rec.status_code == 503
    assert "OPENAI_API_KEY" in resp_rec.json()["detail"]

    resp_chat = client.post(
        "/api/chat",
        json={"mensagem": "Paciente com SpO2 em 89%, o que fazer?"},
        headers=auth_headers,
    )
    assert resp_chat.status_code == 503
    assert "OPENAI_API_KEY" in resp_chat.json()["detail"]


def test_rate_limit_recomendacao_30_segundos_sem_chamar_openai(
    client: TestClient,
    auth_headers: dict[str, str],
    device_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Valida o limite de 1 chamada a cada 30 s em /recomendacao usando stub local do Runner."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-chave-teste-apenas-para-stub-local")

    async def fake_runner_run(agent, prompt, context=None, **kwargs):
        rec = fase06_agents.RecomendacaoFinal(
            probabilidade=0.85,
            classificacao="ALTO",
            protocolos_sugeridos=["Se risco sistêmico alto → ativar estado de emergência"],
            acoes_operacionais=["Acionar equipe de resposta rápida no leito"],
            justificativa="Paciente com FC > 110 bpm e SpO2 < 92% configurando alto risco.",
            aviso=f"Sistema acadêmico com dados sintéticos. {DISCLAIMER_FIXO}",
        )
        return SimpleNamespace(final_output=rec)

    monkeypatch.setattr("app.agents_service.Runner.run", fake_runner_run)

    client.post(
        "/api/telemetria",
        json={
            "device_id": "esp32-01",
            "paciente_id": "pac-ratelimit",
            "fc_media": 116.0,
            "temperatura": 37.5,
            "spo2_media": 90.0,
        },
        headers=device_headers,
    )

    primeira = client.post("/api/pacientes/pac-ratelimit/recomendacao", headers=auth_headers)
    assert primeira.status_code == 200
    assert primeira.json()["classificacao"] == "ALTO"

    segunda = client.post("/api/pacientes/pac-ratelimit/recomendacao", headers=auth_headers)
    assert segunda.status_code == 429
    assert "30 segundos" in segunda.json()["detail"]


def test_cors_respeita_allowed_origins(client: TestClient) -> None:
    """Verifica que apenas origens listadas em ALLOWED_ORIGINS recebem cabeçalho CORS."""
    resp_permitida = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp_permitida.headers.get("access-control-allow-origin") == "http://localhost:5173"

    resp_bloqueada = client.options(
        "/health",
        headers={
            "Origin": "https://dominio-nao-autorizado.malicioso.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp_bloqueada.headers.get("access-control-allow-origin") is None
