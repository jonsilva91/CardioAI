import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { getPatients } from "../services/fakeApi";
import styles from "./Pacientes.module.css";

export default function Pacientes() {
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    async function loadPatients() {
      const data = await getPatients();
      setPatients(data);
    }

    loadPatients();
  }, []);

  const filteredPatients = patients.filter((patient) =>
    patient.name.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className={styles.page}>
      <Navbar />

      <main className={styles.content}>
        <div className={styles.header}>
          <h2>Pacientes</h2>
          <p>Listagem simulada de pacientes cardiológicos.</p>
        </div>

        <div className={styles.searchBox}>
          <input
            type="text"
            placeholder="Buscar paciente por nome..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className={styles.grid}>
          {filteredPatients.map((patient) => (
            <div className={styles.card} key={patient.id}>
              <h3>{patient.name}</h3>
              <p>
                <strong>Idade:</strong> {patient.age}
              </p>
              <p>
                <strong>Sexo:</strong> {patient.gender}
              </p>
              <p>
                <strong>Condição:</strong> {patient.condition}
              </p>
              <p>
                <strong>Risco:</strong>{" "}
                <span
                  className={
                    patient.riskLevel === "alto"
                      ? styles.highRisk
                      : styles.lowRisk
                  }
                >
                  {patient.riskLevel}
                </span>
              </p>
              <p>
                <strong>Última consulta:</strong> {patient.lastAppointment}
              </p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
