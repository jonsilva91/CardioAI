import { createContext, useMemo, useState } from "react";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem("cardioia_user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem("cardioia_token") || null;
  });

  const login = (email, password) => {
    if (email === "admin@cardioia.com" && password === "123456") {
      const fakeUser = {
        name: "Administrador CardioIA",
        email: "admin@cardioia.com",
        role: "admin",
      };

      const fakeToken = "fake-jwt-cardioia-token";

      localStorage.setItem("cardioia_user", JSON.stringify(fakeUser));
      localStorage.setItem("cardioia_token", fakeToken);

      setUser(fakeUser);
      setToken(fakeToken);

      return { success: true };
    }

    return {
      success: false,
      message: "E-mail ou senha inválidos.",
    };
  };

  const logout = () => {
    localStorage.removeItem("cardioia_user");
    localStorage.removeItem("cardioia_token");
    setUser(null);
    setToken(null);
  };

  const isAuthenticated = Boolean(user && token);

  const value = useMemo(
    () => ({
      user,
      token,
      login,
      logout,
      isAuthenticated,
    }),
    [user, token, isAuthenticated],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
