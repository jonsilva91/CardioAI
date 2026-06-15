/**
 * ResultCard Component
 * Exibe o resultado da classificação de ECG
 */

import React from "react";
import { View, Text, StyleSheet } from "react-native";

const ResultCard = ({ result }) => {
  if (!result) return null;

  const { predicted_class, confidence, message, is_simulated } = result;

  // Define cor baseada na confiança
  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return "#28a745"; // Verde - alta confiança
    if (conf >= 0.6) return "#ffc107"; // Amarelo - média confiança
    return "#dc3545"; // Vermelho - baixa confiança
  };

  const confidenceColor = getConfidenceColor(confidence);
  const confidencePercent = (confidence * 100).toFixed(2);

  return (
    <View style={styles.container}>
      {/* Cabeçalho */}
      <View style={styles.header}>
        <Text style={styles.headerIcon}>✓</Text>
        <Text style={styles.headerText}>Classificação Concluída</Text>
      </View>

      {/* Classe Prevista */}
      <View style={styles.resultSection}>
        <Text style={styles.label}>Classe Detectada:</Text>
        <Text style={styles.predictedClass}>{predicted_class}</Text>
      </View>

      {/* Confiança */}
      <View style={styles.resultSection}>
        <Text style={styles.label}>Confiança:</Text>
        <View style={styles.confidenceContainer}>
          <View
            style={[
              styles.confidenceBar,
              {
                width: `${confidencePercent}%`,
                backgroundColor: confidenceColor,
              },
            ]}
          />
          <Text style={[styles.confidenceText, { color: confidenceColor }]}>
            {confidencePercent}%
          </Text>
        </View>
      </View>

      {/* Badge de Simulação */}
      {is_simulated && (
        <View style={styles.simulatedBadge}>
          <Text style={styles.simulatedText}>⚠️ Resultado Simulado</Text>
        </View>
      )}

      {/* Mensagem de Aviso */}
      <View style={styles.warningBox}>
        <Text style={styles.warningIcon}>⚠️</Text>
        <Text style={styles.warningText}>{message}</Text>
      </View>

      {/* Informação Adicional */}
      <View style={styles.infoBox}>
        <Text style={styles.infoText}>
          Este resultado é gerado por um modelo de Deep Learning treinado para
          fins acadêmicos. Sempre consulte um profissional de saúde qualificado
          para diagnóstico real.
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#ffffff",
    borderRadius: 15,
    padding: 20,
    marginTop: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
    paddingBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  headerIcon: {
    fontSize: 24,
    marginRight: 10,
    color: "#28a745",
  },
  headerText: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#333",
  },
  resultSection: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    color: "#666",
    marginBottom: 8,
    fontWeight: "600",
  },
  predictedClass: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#667eea",
  },
  confidenceContainer: {
    position: "relative",
    height: 30,
    backgroundColor: "#f0f0f0",
    borderRadius: 15,
    overflow: "hidden",
    justifyContent: "center",
  },
  confidenceBar: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    borderRadius: 15,
  },
  confidenceText: {
    fontSize: 16,
    fontWeight: "bold",
    textAlign: "center",
    zIndex: 1,
  },
  simulatedBadge: {
    backgroundColor: "#fff3cd",
    borderRadius: 8,
    padding: 10,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: "#ffc107",
  },
  simulatedText: {
    color: "#856404",
    fontSize: 14,
    fontWeight: "600",
    textAlign: "center",
  },
  warningBox: {
    flexDirection: "row",
    backgroundColor: "#fff3cd",
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: "#ffc107",
  },
  warningIcon: {
    fontSize: 20,
    marginRight: 10,
  },
  warningText: {
    flex: 1,
    fontSize: 14,
    color: "#856404",
    lineHeight: 20,
  },
  infoBox: {
    backgroundColor: "#e7f3ff",
    borderRadius: 10,
    padding: 15,
    borderWidth: 1,
    borderColor: "#b3d9ff",
  },
  infoText: {
    fontSize: 13,
    color: "#004085",
    lineHeight: 18,
    textAlign: "center",
  },
});

export default ResultCard;

// Made with Bob
