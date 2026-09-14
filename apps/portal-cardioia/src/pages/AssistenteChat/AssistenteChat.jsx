import React, { useState, useRef, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import styles from './AssistenteChat.module.css';

export default function AssistenteChat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Olá! Sou o Assistente CardioAI. Posso ajudar a marcar consultas, esclarecer dúvidas sobre ECG ou triar seus sintomas iniciais.\n\n⚠️ AVISO: Sou um protótipo educacional. Não realizo diagnóstico médico. Se for uma emergência, procure um hospital imediatamente.',
      urgent: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userText = inputValue;
    const newUserMsg = { id: Date.now(), sender: 'user', text: userText, urgent: false };

    setMessages(prev => [...prev, newUserMsg]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:5001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userText }),
      });

      const data = await response.json();

      const newBotMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: data.response || "Ocorreu um erro ao processar sua resposta.",
        urgent: data.urgent || false
      };

      setMessages(prev => [...prev, newBotMsg]);
    } catch (error) {
      console.error("Erro ao enviar mensagem:", error);
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: "Desculpe, não consegui conectar ao servidor do assistente. O backend (porta 5001) está rodando?",
        urgent: false
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <Navbar />
      <header className={styles.chatHeader}>
        <h2>Assistente CardioAI (Fase 5)</h2>
        <span className={styles.disclaimer}>Protótipo Não-Diagnóstico</span>
      </header>

      <div className={styles.messageArea}>
        {messages.map((msg) => (
          <div key={msg.id} className={`${styles.messageRow} ${styles[msg.sender]}`}>
            <div className={`${styles.messageBubble} ${msg.urgent ? styles.urgent : ''}`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className={`${styles.messageRow} ${styles.bot}`}>
            <div className={styles.typingIndicator}>CardioAI está digitando...</div>
          </div>
        )}
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
          <button type="submit" className={styles.sendButton} disabled={!inputValue.trim() || isTyping}>
            Enviar
          </button>
        </form>
      </div>
    </div>
  );
}
