import { useContext } from "react";
import { AuthContext } from "./AuthContextDefinition"; // ajuste o caminho relativo conforme onde o useAuth.jsx está

export function useAuth() {
  return useContext(AuthContext);
}
