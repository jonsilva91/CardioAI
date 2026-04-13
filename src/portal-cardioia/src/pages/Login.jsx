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

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const result = login(form.email, form.password);

    if (result.success) {
      navigate("/dashboard");
      return;
    }

    setError(result.message);
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1>CardioIA</h1>
        <p className={styles.subtitle}>
          Faça login para acessar o portal de cardiologia inteligente.
        </p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <label>
            E-mail
            <input
              type="email"
              name="email"
              placeholder="admin@cardioia.com"
              value={form.email}
              onChange={handleChange}
            />
          </label>

          <label>
            Senha
            <input
              type="password"
              name="password"
              placeholder="123456"
              value={form.password}
              onChange={handleChange}
            />
          </label>

          {error && <p className={styles.error}>{error}</p>}

          <button type="submit">Entrar</button>
        </form>

        <div className={styles.credentials}>
          <strong>Credenciais de teste</strong>
          <span>E-mail: admin@cardioia.com</span>
          <span>Senha: 123456</span>
        </div>
      </div>
    </div>
  );
}
