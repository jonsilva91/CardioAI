import Navbar from "../../components/Navbar";
import ChatAssistente from "../../components/ChatAssistente";
import styles from "./AssistenteChat.module.css";

/**
 * Página do Assistente Conversacional (Fase 5).
 * Estrutura a página do portal utilizando o layout padrão (Navbar + content)
 * e delega o fluxo conversacional ao componente modular ChatAssistente.
 */
export default function AssistenteChat() {
  return (
    <div className={styles.page}>
      <Navbar />
      <main className={styles.content}>
        <ChatAssistente />
      </main>
    </div>
  );
}
