import { useState, useRef, useEffect } from "react";
import { API_ENDPOINTS } from "../config";
import styles from "./ChatAssistente.module.css";

const INITIAL_MESSAGE = {
  id: 1,
  role: "bot",
  text: "Olá! Sou o assistente virtual do CardioAI. Posso ajudar com dúvidas sobre sintomas, agendamento de consulta e resultados de ECG. Importante: este assistente não substitui avaliação médica e não fornece diagnóstico. Como posso ajudar?",
  urgent: false,
};

/**
 * Componente modular e reutilizável de Chat do Assistente CardioAI.
 * 
 * Centraliza todo o fluxo de mensagens, gerenciamento de sessão individual
 * com o Watson Assistant (Fase 5), tratamento de urgência e renderização.
 */
export function ChatAssistente({
  title = "Assistente CardioAI (Fase 5)",
  subtitle = "Triagem inicial · não substitui avaliação médica",
  disclaimer = "Protótipo Não-Diagnóstico",
  variant = "full", // "full" ou "widget"
  className = "",
}) {
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
      const res = await fetch(API_ENDPOINTS.chat, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        throw new Error(`Servidor respondeu ${res.status}`);
      }

      const data = await res.json();

      // Mantém a sessão individual sincronizada com o Watson Assistant
      if (data.session_id) {
        setSessionId(data.session_id);
      }

      const botMessage = {
        id: Date.now() + 1,
        role: "bot",
        text: data.response ?? "Desculpe, não consegui gerar uma resposta.",
        urgent: Boolean(data.urgent),
        source: data.source,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error("Erro ao comunicar com o assistente:", err);
      setError(
        "Não foi possível conectar ao backend do assistente. Verifique se o serviço está ativo.",
      );
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "bot",
          text: "Desculpe, tive um problema técnico para responder. Tente novamente em instantes.",
          urgent: false,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  async function handleResetSession() {
    if (sessionId) {
      try {
        await fetch(API_ENDPOINTS.sessionClose, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId }),
        });
      } catch (err) {
        console.warn("Aviso ao encerrar sessão no backend:", err);
      }
    }

    setSessionId(null);
    setMessages([
      {
        id: Date.now(),
        role: "bot",
        text: "Sessão reiniciada com sucesso. Como posso ajudar você agora?",
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
              Sessão: {sessionId.startsWith("local-") ? `Local (${sessionId.slice(6, 14)})` : `${sessionId.slice(0, 10)}...`}
            </span>
          )}

          {disclaimer && (
            <span className={styles.disclaimer}>{disclaimer}</span>
          )}

          <button
            type="button"
            className={styles.resetButton}
            onClick={handleResetSession}
            title="Encerrar sessão atual e iniciar nova conversa"
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
                <div className={styles.urgentTag}>⚠️ ATENÇÃO / EMERGÊNCIA</div>
              )}
              {msg.text}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className={`${styles.messageRow} ${styles.bot}`}>
            <div className={styles.typingIndicator}>
              CardioAI está digitando...
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
            placeholder="Digite sua mensagem (ex: sinto dor no peito, ou o que é classe V?)..."
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
