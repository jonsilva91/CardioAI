"""Serviço de cálculo de risco cardiovascular e protocolos clínicos integrando a Fase 6.

Importa diretamente `src.predictor` e `src.protocols` de `phases/fase06_preditivo_multiagente`
via `sys.path` configurado em `app.config`, sem qualquer cópia de código.
"""

from __future__ import annotations

from datetime import datetime, timezone
import time

from app.config import CENARIO_PADRAO  # Garante sys.path da Fase 6 antes dos imports abaixo
from app.schemas import LeituraArmazenada, ProtocoloDetalhado, TelemetriaRequest

import src.predictor as fase06_predictor
import src.protocols as fase06_protocols


def verificar_modelo_carregado() -> bool:
    """Verifica se o artefato joblib do modelo preditivo da Fase 6 está carregado e funcional."""
    try:
        artefato = fase06_predictor.carregar_modelo_preditivo()
        return bool(artefato and "model" in artefato)
    except Exception:
        return False


def montar_dados_completos(
    fc_media: float,
    temperatura: float,
    spo2_media: float,
) -> dict[str, float]:
    """Combina o cenário hospitalar padrão com as 3 leituras vitais enviadas pelo dispositivo IoT."""
    dados = dict(CENARIO_PADRAO)
    dados["fc_media"] = float(fc_media)
    dados["temperatura"] = float(temperatura)
    dados["spo2_media"] = float(spo2_media)
    return dados


def processar_telemetria(payload: TelemetriaRequest) -> LeituraArmazenada:
    """Completa o cenário do paciente, executa o modelo real + protocolos da Fase 6 e retorna o registro."""
    dados_completos = montar_dados_completos(
        fc_media=payload.fc_media,
        temperatura=payload.temperatura,
        spo2_media=payload.spo2_media,
    )

    resultado_ml = fase06_predictor.prever_risco(dados_completos)
    probabilidade = float(resultado_ml["probabilidade"])
    classe_prevista = int(resultado_ml["classe_prevista"])
    classificacao = str(resultado_ml["classificacao"])

    protocolos_raw = fase06_protocols.consultar_protocolos(dados_completos, classificacao)
    protocolos_texto = [str(p["texto"]) for p in protocolos_raw]
    protocolos_detalhados = [
        ProtocoloDetalhado(
            id=str(p["id"]),
            texto=str(p["texto"]),
            variavel=str(p["variavel"]),
            valor_paciente=p["valor_paciente"],
            limiar=str(p["limiar"]),
        )
        for p in protocolos_raw
    ]

    alerta = (classificacao == "ALTO") or (len(protocolos_texto) > 0)

    agora_utc = datetime.now(timezone.utc).isoformat()
    epoch_s = time.time()

    return LeituraArmazenada(
        device_id=payload.device_id,
        paciente_id=payload.paciente_id,
        fc_media=payload.fc_media,
        temperatura=payload.temperatura,
        spo2_media=payload.spo2_media,
        dados_completos=dados_completos,
        probabilidade=probabilidade,
        classe_prevista=classe_prevista,
        classificacao=classificacao,  # type: ignore[arg-type]
        alerta=alerta,
        protocolos=protocolos_texto,
        protocolos_detalhados=protocolos_detalhados,
        timestamp=agora_utc,
        epoch_seconds=epoch_s,
    )

