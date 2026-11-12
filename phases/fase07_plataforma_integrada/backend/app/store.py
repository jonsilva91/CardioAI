"""Armazenamento em memória para telemetria de pacientes, rate-limit e sessões de chat.

LIMITAÇÕES ARQUITETURAIS DO ARMAZENAMENTO EM MEMÓRIA (DOCUMENTAÇÃO OBRIGATÓRIA):
1. Volatilidade (Perda em Reinicializações / Redeploys):
   Todos os dados (leituras de telemetria, controle de cooldown de recomendações e
   histórico de conversação do chat) residem exclusivamente na memória RAM do processo
   Python. No plano Free do Render (ou em qualquer reinicialização do container),
   o processo sofre "spin-down" após período de inatividade ou durante novos deploys,
   ocasionando a perda imediata do histórico acumulado.
2. Retenção Limitada por Janela Circular (200 Leituras por Paciente):
   Para evitar exaustão de memória (Out-Of-Memory / OOM) sob fluxo contínuo de telemetria
   IoT, cada paciente possui uma fila circular (`collections.deque`) limitada às últimas
   200 leituras (`MAX_LEITURAS_POR_PACIENTE = 200`). Leituras mais antigas são descartadas
   automaticamente em ordem FIFO.
3. Escopo de Processo Único (Single-Worker):
   O dicionário em memória e seu lock (`threading.RLock`) garantem segurança apenas entre
   threads de um mesmo processo Uvicorn. Se a aplicação for escalada horizontalmente com
   múltiplos workers (`--workers > 1`) ou múltiplas réplicas, o estado não será
   compartilhado entre instâncias. Em ambiente hospitalar produtivo, esta camada deve
   ser substituída por banco de séries temporais (PostgreSQL/TimescaleDB) e cache
   distribuído (Redis).
"""

from __future__ import annotations

from collections import deque
import threading
import time
from typing import Deque

from app.config import MAX_LEITURAS_POR_PACIENTE, RECOMENDACAO_COOLDOWN_SECONDS
from app.schemas import LeituraArmazenada

MAX_HISTORICO_CHAT_MENSAGENS: int = 40


class InMemoryStore:
    """Gerenciador thread-safe de armazenamento em memória da Fase 7."""

    def __init__(self, max_leituras: int = MAX_LEITURAS_POR_PACIENTE) -> None:
        self._max_leituras = max_leituras
        self._lock = threading.RLock()
        self._leituras: dict[str, Deque[LeituraArmazenada]] = {}
        self._ultimo_recomendacao_ts: dict[str, float] = {}
        self._chat_sessions: dict[str, Deque[dict[str, str]]] = {}

    def adicionar_leitura(self, leitura: LeituraArmazenada) -> None:
        """Adiciona uma leitura para o paciente, mantendo no máximo as últimas 200 leituras."""
        with self._lock:
            fila = self._leituras.get(leitura.paciente_id)
            if fila is None:
                fila = deque(maxlen=self._max_leituras)
                self._leituras[leitura.paciente_id] = fila
            fila.append(leitura)

    def obter_ultima_leitura(self, paciente_id: str) -> LeituraArmazenada | None:
        """Retorna a leitura mais recente do paciente ou None se não houver registros."""
        with self._lock:
            fila = self._leituras.get(paciente_id)
            if not fila:
                return None
            return fila[-1]

    def obter_historico(self, paciente_id: str, limite: int = 50) -> tuple[list[LeituraArmazenada], int]:
        """Retorna as últimas `limite` leituras do paciente (da mais recente para a mais antiga) e o total armazenado."""
        with self._lock:
            fila = self._leituras.get(paciente_id)
            if not fila:
                return [], 0
            total = len(fila)
            # Ordem reversa: leitura mais recente primeiro
            leituras_ordenadas = list(reversed(fila))[: max(1, min(limite, self._max_leituras))]
            return leituras_ordenadas, total

    def verificar_cooldown_recomendacao(
        self,
        paciente_id: str,
        cooldown_segundos: float = RECOMENDACAO_COOLDOWN_SECONDS,
    ) -> tuple[bool, float]:
        """Verifica se o paciente pode receber nova recomendação (limite de 1 chamada a cada 30 s).

        Returns:
            Tupla (permitido: bool, segundos_restantes: float)
        """
        agora = time.monotonic()
        with self._lock:
            ultimo = self._ultimo_recomendacao_ts.get(paciente_id)
            if ultimo is not None:
                decorrido = agora - ultimo
                if decorrido < cooldown_segundos:
                    restante = round(cooldown_segundos - decorrido, 2)
                    return False, max(0.01, restante)
            self._ultimo_recomendacao_ts[paciente_id] = agora
            return True, 0.0

    def liberar_cooldown_recomendacao(self, paciente_id: str) -> None:
        """Libera o registro de cooldown caso a execução falhe antes de concluir."""
        with self._lock:
            self._ultimo_recomendacao_ts.pop(paciente_id, None)

    def obter_historico_chat(self, session_id: str) -> list[dict[str, str]]:
        """Retorna a lista de mensagens armazenadas para a sessão de chat informada."""
        with self._lock:
            sessao = self._chat_sessions.get(session_id)
            if not sessao:
                return []
            return list(sessao)

    def adicionar_mensagem_chat(self, session_id: str, role: str, content: str) -> int:
        """Adiciona uma mensagem (`user` ou `assistant`) ao histórico em memória da sessão."""
        with self._lock:
            sessao = self._chat_sessions.get(session_id)
            if sessao is None:
                sessao = deque(maxlen=MAX_HISTORICO_CHAT_MENSAGENS)
                self._chat_sessions[session_id] = sessao
            sessao.append({"role": role, "content": content})
            return len(sessao)

    def limpar_tudo(self) -> None:
        """Limpa todo o estado em memória (utilizado em testes automatizados)."""
        with self._lock:
            self._leituras.clear()
            self._ultimo_recomendacao_ts.clear()
            self._chat_sessions.clear()


# Instância singleton compartilhada pela aplicação
store = InMemoryStore()

