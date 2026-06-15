/**
 * CardioAI Mobile App
 * Aplicativo React Native para classificação de imagens de ECG
 *
 * IR ALÉM 2 - Fase 4
 * FIAP 2026
 */

import React from "react";
import { StatusBar } from "expo-status-bar";
import { SafeAreaView, StyleSheet } from "react-native";
import EcgAnalysisScreen from "./src/screens/EcgAnalysisScreen";

export default function App() {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <EcgAnalysisScreen />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
});

// Made with Bob
