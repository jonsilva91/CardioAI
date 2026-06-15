/**
 * EcgAnalysisScreen
 * Tela principal para análise de imagens de ECG
 */

import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ScrollView,
  ActivityIndicator,
  Alert,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { classifyEcgImage, getApiBaseUrl } from "../services/visionApi";
import ResultCard from "../components/ResultCard";

const EcgAnalysisScreen = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  /**
   * Solicita permissão e abre a galeria de imagens
   */
  const pickImage = async () => {
    try {
      // Solicita permissão para acessar a galeria
      const { status } =
        await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (status !== "granted") {
        Alert.alert(
          "Permissão Necessária",
          "Precisamos de permissão para acessar suas fotos.",
        );
        return;
      }

      // Abre o seletor de imagens
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });

      if (!result.canceled) {
        setSelectedImage(result.assets[0].uri);
        setResult(null); // Limpa resultado anterior
        setError(null); // Limpa erro anterior
      }
    } catch (err) {
      console.error("Erro ao selecionar imagem:", err);
      Alert.alert("Erro", "Não foi possível selecionar a imagem.");
    }
  };

  /**
   * Envia a imagem para classificação
   */
  const handleClassify = async () => {
    if (!selectedImage) {
      Alert.alert("Atenção", "Selecione uma imagem primeiro.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await classifyEcgImage(selectedImage);

      if (response.success) {
        setResult(response.data);
      } else {
        setError(response.error);
        Alert.alert(
          "Erro na Classificação",
          response.error || "Não foi possível classificar a imagem.",
        );
      }
    } catch (err) {
      console.error("Erro ao classificar:", err);
      setError("Erro inesperado ao classificar a imagem.");
      Alert.alert("Erro", "Erro inesperado ao classificar a imagem.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
    >
      {/* Cabeçalho */}
      <View style={styles.header}>
        <Text style={styles.headerIcon}>🫀</Text>
        <Text style={styles.title}>CardioIA</Text>
        <Text style={styles.subtitle}>Análise de ECG</Text>
      </View>

      {/* Aviso Acadêmico */}
      <View style={styles.academicWarning}>
        <Text style={styles.warningIcon}>⚠️</Text>
        <Text style={styles.warningText}>
          Este protótipo é acadêmico e não substitui diagnóstico médico.
        </Text>
      </View>

      {/* Informação da API */}
      <View style={styles.apiInfo}>
        <Text style={styles.apiInfoText}>API: {getApiBaseUrl()}</Text>
      </View>

      {/* Botão de Seleção de Imagem */}
      <TouchableOpacity
        style={styles.selectButton}
        onPress={pickImage}
        activeOpacity={0.7}
      >
        <Text style={styles.selectButtonIcon}>📁</Text>
        <Text style={styles.selectButtonText}>
          {selectedImage ? "Trocar Imagem" : "Selecionar Imagem de ECG"}
        </Text>
      </TouchableOpacity>

      {/* Preview da Imagem */}
      {selectedImage && (
        <View style={styles.imageContainer}>
          <Image source={{ uri: selectedImage }} style={styles.image} />
        </View>
      )}

      {/* Botão de Classificação */}
      {selectedImage && (
        <TouchableOpacity
          style={[
            styles.classifyButton,
            isLoading && styles.classifyButtonDisabled,
          ]}
          onPress={handleClassify}
          disabled={isLoading}
          activeOpacity={0.7}
        >
          {isLoading ? (
            <ActivityIndicator color="#ffffff" size="small" />
          ) : (
            <>
              <Text style={styles.classifyButtonIcon}>🔍</Text>
              <Text style={styles.classifyButtonText}>Classificar ECG</Text>
            </>
          )}
        </TouchableOpacity>
      )}

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#667eea" />
          <Text style={styles.loadingText}>Analisando imagem...</Text>
        </View>
      )}

      {/* Resultado */}
      {result && <ResultCard result={result} />}

      {/* Erro */}
      {error && !isLoading && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorIcon}>❌</Text>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>CardioAI - FIAP 2026</Text>
        <Text style={styles.footerSubtext}>
          Projeto Acadêmico de IA Aplicada
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  contentContainer: {
    padding: 20,
    paddingTop: 60,
  },
  header: {
    alignItems: "center",
    marginBottom: 20,
  },
  headerIcon: {
    fontSize: 48,
    marginBottom: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#667eea",
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 18,
    color: "#666",
  },
  academicWarning: {
    flexDirection: "row",
    backgroundColor: "#fff3cd",
    borderRadius: 10,
    padding: 15,
    marginBottom: 20,
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
  apiInfo: {
    backgroundColor: "#e7f3ff",
    borderRadius: 8,
    padding: 10,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#b3d9ff",
  },
  apiInfoText: {
    fontSize: 12,
    color: "#004085",
    textAlign: "center",
  },
  selectButton: {
    backgroundColor: "#ffffff",
    borderRadius: 15,
    padding: 20,
    alignItems: "center",
    marginBottom: 20,
    borderWidth: 2,
    borderColor: "#667eea",
    borderStyle: "dashed",
  },
  selectButtonIcon: {
    fontSize: 40,
    marginBottom: 10,
  },
  selectButtonText: {
    fontSize: 16,
    color: "#667eea",
    fontWeight: "600",
  },
  imageContainer: {
    backgroundColor: "#ffffff",
    borderRadius: 15,
    padding: 10,
    marginBottom: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  image: {
    width: "100%",
    height: 300,
    borderRadius: 10,
    resizeMode: "contain",
  },
  classifyButton: {
    backgroundColor: "#667eea",
    borderRadius: 25,
    padding: 18,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 20,
    shadowColor: "#667eea",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  classifyButtonDisabled: {
    backgroundColor: "#cccccc",
    shadowOpacity: 0,
  },
  classifyButtonIcon: {
    fontSize: 24,
    marginRight: 10,
  },
  classifyButtonText: {
    fontSize: 18,
    color: "#ffffff",
    fontWeight: "bold",
  },
  loadingContainer: {
    alignItems: "center",
    padding: 30,
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: "#667eea",
    fontWeight: "600",
  },
  errorContainer: {
    backgroundColor: "#f8d7da",
    borderRadius: 10,
    padding: 20,
    marginTop: 20,
    borderWidth: 1,
    borderColor: "#dc3545",
    alignItems: "center",
  },
  errorIcon: {
    fontSize: 40,
    marginBottom: 10,
  },
  errorText: {
    fontSize: 14,
    color: "#721c24",
    textAlign: "center",
    lineHeight: 20,
  },
  footer: {
    marginTop: 40,
    marginBottom: 20,
    alignItems: "center",
  },
  footerText: {
    fontSize: 14,
    color: "#999",
    marginBottom: 5,
  },
  footerSubtext: {
    fontSize: 12,
    color: "#bbb",
  },
});

export default EcgAnalysisScreen;

// Made with Bob
