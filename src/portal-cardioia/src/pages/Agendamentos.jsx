import { useEffect, useReducer, useState } from "react";
import Navbar from "../components/Navbar";
import { getAppointments, getPatients } from "../services/fakeApi";
import styles from "./Agendamentos.module.css";

const initialState = {
  patientName: "",
  date: "",
  time: "",
  doctor: "",
  type: "Consulta",
};

function reducer(state, action) {
  switch (action.type) {
    case "UPDATE_FIELD":
      return {
        ...state,
        [action.field]: action.value,
      };
    case "RESET":
      return initialState;
    default:
      return state;
  }
}

export default function Agendamentos() {
  const [formState, dispatch] = useReducer(reducer, initialState);
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);

  useEffect(() => {
    async function loadData() {
      const appointmentsData = await getAppointments();
      const patientsData = await getPatients();

      setAppointments(appointmentsData);
      setPatients(patientsData);
    }

    loadData();
  }, []);

  function handleChange(event) {
    dispatch({
      type: "UPDATE_FIELD",
      field: event.target.name,
      value: event.target.value,
    });
  }

  function handleSubmit(event) {
    event.preventDefault();

    const newAppointment = {
      id: appointments.length + 1,
      ...formState,
    };

    setAppointments((prev) => [...prev, newAppointment]);
    dispatch({ type: "RESET" });
  }

  return (
    <div className={styles.page}>
      <Navbar />

      <main className={styles.content}>
        <div className={styles.header}>
          <h2>Agendamentos</h2>
          <p>Formulário de consultas usando useReducer.</p>
        </div>

        <div className={styles.layout}>
          <section className={styles.formCard}>
            <h3>Novo agendamento</h3>

            <form onSubmit={handleSubmit} className={styles.form}>
              <label>
                Paciente
                <select
                  name="patientName"
                  value={formState.patientName}
                  onChange={handleChange}
                  required
                >
                  <option value="">Selecione</option>
                  {patients.map((patient) => (
                    <option key={patient.id} value={patient.name}>
                      {patient.name}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Data
                <input
                  type="date"
                  name="date"
                  value={formState.date}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Horário
                <input
                  type="time"
                  name="time"
                  value={formState.time}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Médico
                <input
                  type="text"
                  name="doctor"
                  placeholder="Dr. Roberto Cardoso"
                  value={formState.doctor}
                  onChange={handleChange}
                  required
                />
              </label>

              <label>
                Tipo
                <select
                  name="type"
                  value={formState.type}
                  onChange={handleChange}
                >
                  <option value="Consulta">Consulta</option>
                  <option value="Retorno">Retorno</option>
                  <option value="Avaliação">Avaliação</option>
                  <option value="Triagem">Triagem</option>
                </select>
              </label>

              <button type="submit">Salvar agendamento</button>
            </form>
          </section>

          <section className={styles.listCard}>
            <h3>Consultas cadastradas</h3>

            <ul className={styles.list}>
              {appointments.map((appointment) => (
                <li key={appointment.id}>
                  <strong>{appointment.patientName}</strong>
                  <span>{appointment.date}</span>
                  <span>{appointment.time}</span>
                  <span>{appointment.doctor}</span>
                  <span>{appointment.type}</span>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}
