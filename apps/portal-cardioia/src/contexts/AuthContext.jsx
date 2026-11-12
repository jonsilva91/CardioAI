import { useCallback, useMemo, useState } from "react";
import { API_ENDPOINTS } from "../config";
import { AuthContext } from "./AuthContextDefinition";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const storedToken = localStorage.getItem("cardioia_token");
      const storedUser = localStorage.getItem("cardioia_user");
      if (!storedToken || storedToken === "fake-jwt-cardioia-token") {
        return null;
      }
      return storedUser ? JSON.parse(storedUser) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(() => {
    const storedToken = localStorage.getItem("cardioia_token");
    if (!storedToken || storedToken === "fake-jwt-cardioia-token") {
      localStorage.removeItem("cardioia_token");
      localStorage.removeItem("cardioia_user");
      return null;
    }
    return storedToken;
  });

  const logout = useCallback(() => {
    localStorage.removeItem("cardioia_user");
    localStorage.removeItem("cardioia_token");
    setUser(null);
    setToken(null);
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      const response = await fetch(API_ENDPOINTS.login, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          email: email.trim(),
          senha: password,
        }),
      });

      let payload = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }

      if (!response.ok) {
        return {
          success: false,
          message:
            payload?.detail ||
            payload?.message ||
            "E-mail ou senha inválidos.",
        };
      }

      const authUser = {
        name: payload.email || email.trim(),
        email: payload.email || email.trim(),
        role: "admin",
      };

      localStorage.setItem("cardioia_user", JSON.stringify(authUser));
      localStorage.setItem("cardioia_token", payload.access_token);

      setUser(authUser);
      setToken(payload.access_token);

      return { success: true };
    } catch {
      return {
        success: false,
        message:
          "Não foi possível conectar ao servidor. Verifique se o backend está online.",
      };
    }
  }, []);

  const isAuthenticated = Boolean(user && token);

  const value = useMemo(
    () => ({
      user,
      token,
      login,
      logout,
      isAuthenticated,
    }),
    [user, token, login, logout, isAuthenticated]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
