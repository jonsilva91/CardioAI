import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/useAuth";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => (location.pathname === path ? styles.active : "");

  return (
    <header className={styles.navbar}>
      <div className={styles.brand}>
        <span className={styles.logo}>❤</span>
        <div>
          <h1>CardioIA</h1>
          <p>Portal Inteligente em Cardiologia</p>
        </div>
      </div>

      <nav className={styles.links}>
        <Link to="/dashboard" className={isActive("/dashboard")}>
          Dashboard
        </Link>
        <Link to="/pacientes" className={isActive("/pacientes")}>
          Pacientes
        </Link>
        <Link to="/agendamentos" className={isActive("/agendamentos")}>
          Agendamentos
        </Link>
      </nav>

      <div className={styles.userArea}>
        <span>{user?.name}</span>
        <button onClick={logout}>Sair</button>
      </div>
    </header>
  );
}
