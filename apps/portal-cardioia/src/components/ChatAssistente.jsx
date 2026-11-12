import { useState, useRef, useEffect } from "react";
import { API_ENDPOINTS } from "../config";
import { useAuth } from "../contexts/useAuth";
import styles from "./ChatAssistente.module.css";

const INITIAL_MESSAGE = {
  id: 1,
  role: "bot",
  text: "Olá! Sou o assistente cardiológico de triagem do CardioIA. Posso auxiliar na interpretação de sinais vitais (BPM, SpO2, temperatura), avaliação inicial de sintomas e protocolos de risco. Não substitui avaliação médica.",
  urgent: false,
};

/**
 * Componente de Chat do Assistente Cardiológico de Triagem integrado ao
 * endpoint POST /api/chat do Backend da Fase 7 (OpenAI real + memória por session_id).
 */
export function ChatAssistente({
  title = "Assistente Cardiológico de Triagem (Fase 7)",
  subtitle = "LLM OpenAI · Não substitui avaliação médica.",
  disclaimer = "Não substitui avaliação médica.",
  variant = "full",
  className = "",
}) {
  const { token, logout } = useAuth();
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  async function handleSendMessage(e) {
    if (e && e.preventDefault) e.preventDefault();
    const text = inputValue.trim();
    if (!text || isTyping) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      text,
      urgent: false,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);
    setError(null);

    try {
      const payload = {
        mensagem: text,
      };
      if (sessionId) {
        payload.session_id = sessionId;
      }

      const res = await fetch(API_ENDPOINTS.chat, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });

      if (res.status === 401) {
        logout();
        return;
      }

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        throw new Error(
          data?.detail || `Servidor respondeu com status ${res.status}`
        );
      }

      if (data?.session_id) {
        setSessionId(data.session_id);
      }

      const textoResposta =
        data?.resposta ??
        data?.response ??
        "Desculpe, não consegui gerar uma resposta.";

      const botMessage = {
        id: Date.now() + 1,
        role: "bot",
        text: textoResposta,
        urgent:
          textoResposta.toLowerCase().includes("emergência") ||
          textoResposta.toLowerCase().includes("alerta vermelho"),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(
        err.message ||
          "Não foi possível conectar ao backend do assistente. Verifique se o serviço está ativo."
      );
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "bot",
          text: "Desculpe, tive um problema técnico para responder. Tente novamente em instantes. Não substitui avaliação médica.",
          urgent: false,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  function handleResetSession() {
    setSessionId(null);
    setMessages([
      {
        id: Date.now(),
        role: "bot",
        text: "Sessão reiniciada com sucesso. Como posso ajudar você agora? Não substitui avaliação médica.",
        urgent: false,
      },
    ]);
    setError(null);
  }

  const containerClasses = [
    styles.chatContainer,
    variant === "widget" ? styles.widget : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={containerClasses}>
      <header className={styles.chatHeader}>
        <div className={styles.headerInfo}>
          <h2 className={styles.headerTitle}>{title}</h2>
          {subtitle && <span className={styles.headerSubtitle}>{subtitle}</span>}
        </div>

        <div className={styles.headerActions}>
          {sessionId && (
            <span
              className={styles.sessionBadge}
              title={`ID da sessão: ${sessionId}`}
            >
              <span className={styles.sessionDot}>●</span>
              Sessão: {sessionId.slice(0, 12)}...
            </span>
          )}

          {disclaimer && (
            <span className={styles.disclaimer}>{disclaimer}</span>
          )}

          <button
            type="button"
            className={styles.resetButton}
            onClick={handleResetSession}
            title="Iniciar nova conversa"
          >
            Nova Conversa
          </button>
        </div>
      </header>

      <div className={styles.messageArea}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.messageRow} ${styles[msg.role]}`}
          >
            <div
              className={`${styles.messageBubble} ${
                msg.urgent ? styles.urgent : ""
              }`}
            >
              {msg.urgent && (
                <div className={styles.urgentTag}>⚠️ ATENÇÃO / TRIAGEM</div>
              )}
              {msg.text}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className={`${styles.messageRow} ${styles.bot}`}>
            <div className={styles.typingIndicator}>
              CardioIA está analisando...
            </div>
          </div>
        )}

        {error && <div className={styles.errorBanner}>{error}</div>}

        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputArea}>
        <form onSubmit={handleSendMessage} className={styles.inputForm}>
          <input
            type="text"
            className={styles.chatInput}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Digite sua dúvida clínica ou sintomas para triagem..."
            disabled={isTyping}
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={!inputValue.trim() || isTyping}
          >
            Enviar
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatAssistente;
