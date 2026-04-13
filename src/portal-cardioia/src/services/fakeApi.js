import patients from "../data/patients.json";
import appointments from "../data/appointments.json";

export function getPatients() {
  return Promise.resolve(patients);
}

export function getAppointments() {
  return Promise.resolve(appointments);
}
