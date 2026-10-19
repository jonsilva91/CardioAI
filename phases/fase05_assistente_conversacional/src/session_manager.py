import time
import uuid
import logging
from typing import Optional, Dict, Tuple, Any

try:
    from ibm_cloud_sdk_core import ApiException
except ImportError:
    ApiException = Exception

logger = logging.getLogger(__name__)


class WatsonSessionManager:
    """
    Gerenciador de sessões individualizadas para o IBM Watson Assistant.

    Resolve o problema de compartilhamento global de session_id:
    - Mantém registro em memória de cada sessão ativa com seu respectivo timestamp.
    - Suporta expiração baseada em inatividade (TTL configurável).
    - Detecta automaticamente quando o Watson Assistant invalida/expira a sessão na nuvem (erro 404/Invalid Session)
      e realiza auto-recuperação (re-cria sessão e re-executa a mensagem sem quebrar a experiência do usuário).
    - Permite encerramento explícito (delete_session) para liberação de recursos.
    - Fornece suporte ao modo fallback local (gerando sessões simuladas rastreáveis).
    """

    def __init__(self, assistant_client=None, assistant_id: Optional[str] = None, ttl_seconds: int = 1800):
        self.assistant = assistant_client
        self.assistant_id = assistant_id
        self.ttl_seconds = ttl_seconds
        # Estrutura em memória: { session_id: {"created_at": float, "last_activity": float} }
        self._sessions: Dict[str, Dict[str, float]] = {}

    @property
    def is_watson_ready(self) -> bool:
        """Verifica se o cliente Watson e o ID do assistente estão configurados."""
        return self.assistant is not None and bool(self.assistant_id)

    def create_session(self) -> str:
        """
        Cria uma nova sessão no Watson Assistant ou gera uma sessão local de fallback.
        """
        if self.is_watson_ready:
            try:
                res = self.assistant.create_session(assistant_id=self.assistant_id).get_result()
                session_id = res.get("session_id")
                if not session_id:
                    raise ValueError("Resposta do Watson não conteve 'session_id'")
                now = time.time()
                self._sessions[session_id] = {
                    "created_at": now,
                    "last_activity": now
                }
                logger.info(f"✓ Nova sessão Watson criada com sucesso: {session_id}")
                return session_id
            except Exception as e:
                logger.error(f"Erro ao criar sessão no Watson Assistant: {e}")
                raise

        # Fallback local (sessão simulada com UUID)
        local_session_id = f"local-{uuid.uuid4()}"
        now = time.time()
        self._sessions[local_session_id] = {
            "created_at": now,
            "last_activity": now
        }
        return local_session_id

    def touch_session(self, session_id: str) -> None:
        """Atualiza o timestamp da última atividade da sessão."""
        if session_id in self._sessions:
            self._sessions[session_id]["last_activity"] = time.time()
        else:
            now = time.time()
            self._sessions[session_id] = {
                "created_at": now,
                "last_activity": now
            }

    def is_session_expired(self, session_id: str) -> bool:
        """Verifica se a sessão expirou por inatividade local (TTL)."""
        session = self._sessions.get(session_id)
        if not session:
            return True
        return (time.time() - session.get("last_activity", 0)) > self.ttl_seconds

    def delete_session(self, session_id: str) -> bool:
        """
        Encerra e limpa a sessão no Watson Assistant e na memória local.
        """
        if not session_id:
            return False

        # Remove do rastreamento local
        self._sessions.pop(session_id, None)

        # Se for sessão do Watson e cliente estiver disponível, deleta na nuvem
        if self.is_watson_ready and not session_id.startswith("local-"):
            try:
                self.assistant.delete_session(
                    assistant_id=self.assistant_id,
                    session_id=session_id
                ).get_result()
                logger.info(f"✓ Sessão Watson encerrada na nuvem: {session_id}")
                return True
            except ApiException as ae:
                # 404 significa que a sessão já havia sido limpa ou expirada pelo Watson
                if ae.code == 404:
                    logger.info(f"Sessão {session_id} já não existia no Watson (já expirada).")
                    return True
                logger.warning(f"Aviso ao deletar sessão no Watson: {ae}")
                return False
            except Exception as e:
                logger.warning(f"Erro ao deletar sessão {session_id}: {e}")
                return False

        return True

    def cleanup_inactive_sessions(self) -> int:
        """
        Varre as sessões em memória e descarta as inativas que excederam o TTL.
        Retorna o número de sessões descartadas.
        """
        now = time.time()
        expired_ids = [
            sid for sid, data in self._sessions.items()
            if (now - data.get("last_activity", 0)) > self.ttl_seconds
        ]
        for sid in expired_ids:
            self.delete_session(sid)
        return len(expired_ids)

    def send_message(self, text: str, session_id: Optional[str] = None) -> Tuple[Dict[str, Any], str, bool]:
        """
        Envia mensagem ao Watson Assistant com tratamento robusto de ciclo de vida de sessão:
        - Cria sessão se nenhuma for informada ou se a informada estiver localmente expirada.
        - Se o Watson responder com 404 (Sessão Expirada/Inválida), captura a exceção,
          cria automaticamente uma nova sessão e re-envia a mensagem de forma transparente.
        
        Retorna:
            (response_dict, active_session_id, is_new_session)
        """
        if not self.is_watson_ready:
            raise RuntimeError("Watson Assistant não está disponível/configurado.")

        self.cleanup_inactive_sessions()

        active_session_id = session_id
        is_new_session = False

        # 1. Se a sessão informada for nula ou estiver localmente expirada pelo TTL, cria uma nova
        if not active_session_id or self.is_session_expired(active_session_id):
            if active_session_id:
                logger.info(f"Sessão {active_session_id} expirou localmente por inatividade. Criando nova...")
                self._sessions.pop(active_session_id, None)
            active_session_id = self.create_session()
            is_new_session = True

        # 2. Tenta enviar mensagem para a sessão ativa
        try:
            response = self.assistant.message(
                assistant_id=self.assistant_id,
                session_id=active_session_id,
                input={
                    'message_type': 'text',
                    'text': text
                }
            ).get_result()
            self.touch_session(active_session_id)
            return response, active_session_id, is_new_session

        except ApiException as ae:
            # Erro 404 ("Invalid Session") ou 400 (GUID inválido) indica sessão expirada na IBM
            if ae.code in (404, 400) or "invalid session" in str(ae.message).lower() or "not found" in str(ae.message).lower():
                logger.warning(
                    f"⚠️ Sessão do Watson ({active_session_id}) expirou na nuvem ({ae.code}: {ae.message}). "
                    f"Recriando sessão automaticamente e reprocessando mensagem..."
                )
                self._sessions.pop(active_session_id, None)
                active_session_id = self.create_session()
                is_new_session = True

                # Re-executa mensagem com nova sessão
                response = self.assistant.message(
                    assistant_id=self.assistant_id,
                    session_id=active_session_id,
                    input={
                        'message_type': 'text',
                        'text': text
                    }
                ).get_result()
                self.touch_session(active_session_id)
                return response, active_session_id, is_new_session
            else:
                raise
