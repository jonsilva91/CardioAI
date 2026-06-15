import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import { getAppointments, getPatients } from "../services/fakeApi";
import styles from "./Dashboard.module.css";

export default function Dashboard() {
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    async function loadData() {
      const patientsData = await getPatients();
      const appointmentsData = await getAppointments();

      setPatients(patientsData);
      setAppointments(appointmentsData);
    }

    loadData();
  }, []);

  const highRisk = patients.filter((p) => p.riskLevel === "alto").length;
  const lowRisk = patients.filter((p) => p.riskLevel === "baixo").length;

  return (
    <div className={styles.page}>
      <Navbar />

      <main className={styles.content}>
        <section className={styles.header}>
          <h2>Dashboard Clínico</h2>
          <p>Visão geral dos pacientes e consultas simuladas do CardioIA.</p>
        </section>

        <section className={styles.statsGrid}>
          <StatCard
            title="Pacientes cadastrados"
            value={patients.length}
            subtitle="Base simulada"
          />
          <StatCard
            title="Consultas agendadas"
            value={appointments.length}
            subtitle="Agenda atual"
          />
          <StatCard
            title="Alto risco"
            value={highRisk}
            subtitle="Pacientes prioritários"
          />
          <StatCard
            title="Baixo risco"
            value={lowRisk}
            subtitle="Casos menos urgentes"
          />
        </section>

        <section className={styles.panelGrid}>
          <div className={styles.panel}>
            <h3>Pacientes recentes</h3>

            <div className={styles.tableWrapper}>
              <table>
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Idade</th>
                    <th>Condição</th>
                    <th>Risco</th>
                  </tr>
                </thead>
                <tbody>
                  {patients.map((patient) => (
                    <tr key={patient.id}>
                      <td>{patient.name}</td>
                      <td>{patient.age}</td>
                      <td>{patient.condition}</td>
                      <td>
                        <span
                          className={
                            patient.riskLevel === "alto"
                              ? styles.highRisk
                              : styles.lowRisk
                          }
                        >
                          {patient.riskLevel}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className={styles.panel}>
            <h3>Próximas consultas</h3>
            <ul className={styles.appointmentList}>
              {appointments.map((appointment) => (
                <li key={appointment.id}>
                  <strong>{appointment.patientName}</strong>
                  <span>
                    {appointment.date} às {appointment.time}
                  </span>
                  <span>{appointment.doctor}</span>
                  <span>{appointment.type}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
    </div>
  );
}
