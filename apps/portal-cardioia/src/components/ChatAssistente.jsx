import { useState, useRef, useEffect } from "react";

const API_URL = import.meta.env.VITE_CHAT_API_URL || "http://localhost:5001/chat";

export function ChatAssistente() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Olá! Sou o assistente virtual do CardioIA. Posso ajudar com dúvidas sobre sintomas, agendamento de consulta e resultados de ECG. Importante: este assistente não substitui avaliação médica e não fornece diagnóstico. Como posso ajudar?",
      urgent: false,
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || isTyping) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setIsTyping(true);
    setError(null);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        throw new Error(`Servidor respondeu ${res.status}`);
      }

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: data.response ?? "Desculpe, não consegui gerar uma resposta.",
          urgent: Boolean(data.urgent),
          source: data.source,
        },
      ]);
    } catch (err) {
      setError(
        "Não consegui falar com o assistente agora. Verifique se o backend está rodando.",
      );
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Desculpe, tive um problema técnico para responder. Tente novamente em instantes.",
          urgent: false,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.headerTitle}>Assistente CardioIA</div>
        <div style={styles.headerSubtitle}>Triagem inicial · não substitui avaliação médica</div>
      </div>

      <div style={styles.messagesArea}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.messageRow,
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <div
              style={{
                ...styles.bubble,
                ...(msg.role === "user" ? styles.bubbleUser : styles.bubbleBot),
                ...(msg.urgent ? styles.bubbleUrgent : {}),
              }}
            >
              {msg.urgent && <div style={styles.urgentTag}>⚠️ ATENÇÃO</div>}
              {msg.text}
            </div>
          </div>
        ))}

        {isTyping && (
          <div style={{ ...styles.messageRow, justifyContent: "flex-start" }}>
            <div style={{ ...styles.bubble, ...styles.bubbleBot }}>
              <span style={styles.typingDots}>digitando...</span>
            </div>
          </div>
        )}

        {error && <div style={styles.errorBanner}>{error}</div>}

        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputArea}>
        <textarea
          style={styles.textInput}
          placeholder="Digite sua mensagem..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button
          style={{
            ...styles.sendButton,
            opacity: input.trim() && !isTyping ? 1 : 0.5,
          }}
          onClick={sendMessage}
          disabled={!input.trim() || isTyping}
        >
          Enviar
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    width: "100%",
    maxWidth: 480,
    height: 600,
    border: "1px solid #e2e2e2",
    borderRadius: 12,
    overflow: "hidden",
    fontFamily: "Arial, sans-serif",
    boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
  },
  header: {
    padding: "14px 18px",
    background: "#c62828",
    color: "white",
  },
  headerTitle: {
    fontWeight: "bold",
    fontSize: 16,
  },
  headerSubtitle: {
    fontSize: 12,
    opacity: 0.9,
    marginTop: 2,
  },
  messagesArea: {
    flex: 1,
    overflowY: "auto",
    padding: 16,
    display: "flex",
    flexDirection: "column",
    gap: 10,
    background: "#f7f7f8",
  },
  messageRow: {
    display: "flex",
    width: "100%",
  },
  bubble: {
    maxWidth: "80%",
    padding: "10px 14px",
    borderRadius: 14,
    fontSize: 14,
    lineHeight: 1.4,
    whiteSpace: "pre-wrap",
  },
  bubbleUser: {
    background: "#c62828",
    color: "white",
    borderBottomRightRadius: 4,
  },
  bubbleBot: {
    background: "white",
    color: "#222",
    border: "1px solid #e2e2e2",
    borderBottomLeftRadius: 4,
  },
  bubbleUrgent: {
    background: "#fff3f3",
    border: "2px solid #c62828",
    color: "#7a0000",
    fontWeight: 500,
  },
  urgentTag: {
    fontWeight: "bold",
    fontSize: 12,
    marginBottom: 4,
    color: "#c62828",
  },
  typingDots: {
    fontStyle: "italic",
    color: "#999",
    fontSize: 13,
  },
  errorBanner: {
    fontSize: 12,
    color: "#c62828",
    background: "#fff3f3",
    padding: 8,
    borderRadius: 8,
    textAlign: "center",
  },
  inputArea: {
    display: "flex",
    gap: 8,
    padding: 12,
    borderTop: "1px solid #e2e2e2",
    background: "white",
  },
  textInput: {
    flex: 1,
    resize: "none",
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid #ccc",
    fontSize: 14,
    fontFamily: "inherit",
    outline: "none",
  },
  sendButton: {
    padding: "0 18px",
    borderRadius: 8,
    border: "none",
    background: "#c62828",
    color: "white",
    fontWeight: "bold",
    cursor: "pointer",
  },
};
