import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/useAuth";
import styles from "./Login.module.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [wakingUp, setWakingUp] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    setWakingUp(false);

    const wakeTimer = setTimeout(() => {
      setWakingUp(true);
    }, 2000);

    try {
      const result = await login(form.email, form.password);

      if (result.success) {
        navigate("/monitoramento", { replace: true });
        return;
      }

      setError(result.message);
    } finally {
      clearTimeout(wakeTimer);
      setLoading(false);
      setWakingUp(false);
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1>CardioIA</h1>
        <p className={styles.subtitle}>
          Faça login para acessar o portal de cardiologia inteligente (Fase 7).
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <label>
            E-mail
            <input
              type="email"
              name="email"
              placeholder="seu.email@hospital.org"
              value={form.email}
              onChange={handleChange}
              disabled={loading}
              required
            />
          </label>

          <label>
            Senha
            <input
              type="password"
              name="password"
              placeholder="Digite sua senha"
              value={form.password}
              onChange={handleChange}
              disabled={loading}
              required
            />
          </label>

          {wakingUp && (
            <p className={styles.subtitle}>
              ⏳ Servidor acordando, aguarde alguns segundos...
            </p>
          )}

          {error && <p className={styles.error}>{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Autenticando..." : "Entrar"}
          </button>
        </form>

        <div className={styles.credentials}>
          <strong>Autenticação JWT (Fase 7)</strong>
          <span>Utilize as credenciais DEMO_EMAIL / DEMO_PASSWORD configuradas no backend.</span>
        </div>
      </div>
    </div>
  );
}
