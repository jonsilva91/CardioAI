import React, { useEffect, useState } from "react";
import { ActivityIndicator, SafeAreaView, StyleSheet, View } from "react-native";
import { StatusBar } from "expo-status-bar";
import LoginScreen from "./src/screens/LoginScreen";
import MonitoramentoScreen from "./src/screens/MonitoramentoScreen";
import { obterSessaoSalva } from "./src/services/api";

export default function App() {
  const [sessao, setSessao] = useState(null);
  const [inicializando, setInicializando] = useState(true);

  useEffect(() => {
    let ativo = true;
    obterSessaoSalva()
      .then((dados) => {
        if (ativo && dados?.token) {
          setSessao(dados);
        }
      })
      .finally(() => {
        if (ativo) {
          setInicializando(false);
        }
      });
    return () => {
      ativo = false;
    };
  }, []);

  if (inicializando) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" />
        <View style={styles.loadingWrap}>
          <ActivityIndicator size="large" color="#38bdf8" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      {sessao?.token ? (
        <MonitoramentoScreen
          sessao={sessao}
          onLogout={() => setSessao(null)}
        />
      ) : (
        <LoginScreen onLoginSuccess={(novaSessao) => setSessao(novaSessao)} />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a",
  },
  loadingWrap: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
});
