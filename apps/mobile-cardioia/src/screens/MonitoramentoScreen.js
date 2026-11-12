import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import {
  buscarStatusPaciente,
  limparSessao,
  solicitarRecomendacaoIA,
} from "../services/api";

const INTERVALO_POLLING_MS = 5000;

function obterTemaRisco(classificacao) {
  const nivel = String(classificacao || "").toUpperCase();
  if (nivel === "ALTO") {
    return {
      corFundo: "#7f1d1d",
      corBorda: "#ef4444",
      corTexto: "#fecaca",
      rotulo: "RISCO ALTO",
    };
  }
  if (nivel === "MODERADO") {
    return {
      corFundo: "#78350f",
      corBorda: "#f59e0b",
      corTexto: "#fde68a",
      rotulo: "RISCO MODERADO",
    };
  }
  return {
    corFundo: "#14532d",
    corBorda: "#22c55e",
    corTexto: "#bbf7d0",
    rotulo: "RISCO BAIXO",
  };
}

export default function MonitoramentoScreen({ sessao, onLogout }) {
  const [pacienteId, setPacienteId] = useState("paciente-01");
  const [statusDados, setStatusDados] = useState(null);
  const [carregandoStatus, setCarregandoStatus] = useState(true);
  const [atualizandoPull, setAtualizandoPull] = useState(false);
  const [erroStatus, setErroStatus] = useState(null);

  const [recomendacao, setRecomendacao] = useState(null);
  const [carregandoIA, setCarregandoIA] = useState(false);
  const [erroIA, setErroIA] = useState(null);

  const handleSair = useCallback(async () => {
    await limparSessao();
    onLogout();
  }, [onLogout]);

  const carregarDados = useCallback(
    async (silencioso = false) => {
      if (!pacienteId.trim()) return;
      if (!silencioso) {
        setCarregandoStatus(true);
      }

      try {
        const dados = await buscarStatusPaciente(pacienteId, sessao.token);
        setStatusDados(dados);
        setErroStatus(null);
      } catch (err) {
        if (err.status === 401) {
          await handleSair();
          return;
        }
        setErroStatus(err.message || "Falha ao consultar status do paciente.");
      } finally {
        setCarregandoStatus(false);
        setAtualizandoPull(false);
      }
    },
    [pacienteId, sessao.token, handleSair]
  );

  useEffect(() => {
    carregarDados(false);
    const timer = setInterval(() => {
      carregarDados(true);
    }, INTERVALO_POLLING_MS);

    return () => clearInterval(timer);
  }, [carregarDados]);

  const onRefresh = () => {
    setAtualizandoPull(true);
    carregarDados(true);
  };

  const handleGerarRecomendacao = async () => {
    setCarregandoIA(true);
    setErroIA(null);
    try {
      const resposta = await solicitarRecomendacaoIA(pacienteId, sessao.token);
      setRecomendacao(resposta);
    } catch (err) {
      if (err.status === 401) {
        await handleSair();
        return;
      }
      setErroIA(err.message || "Não foi possível obter a recomendação da IA.");
    } finally {
      setCarregandoIA(false);
    }
  };

  const leitura = statusDados?.ultima_leitura;
  const temaRisco = obterTemaRisco(statusDados?.classificacao);
  const idadeSegundos =
    statusDados?.idade_leitura_segundos !== undefined
      ? Math.round(Number(statusDados.idade_leitura_segundos))
      : null;
  const protocolos = Array.isArray(statusDados?.protocolos)
    ? statusDados.protocolos
    : [];

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={atualizandoPull}
          onRefresh={onRefresh}
          tintColor="#38bdf8"
        />
      }
    >
      {/* Cabeçalho */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>CardioIA</Text>
          <Text style={styles.headerSub}>
            {sessao.email || "Monitoramento em Tempo Real"}
          </Text>
        </View>
        <TouchableOpacity style={styles.logoutBtn} onPress={handleSair}>
          <Text style={styles.logoutText}>Sair</Text>
        </TouchableOpacity>
      </View>

      {/* Seletor de Paciente */}
      <View style={styles.patientBar}>
        <Text style={styles.patientLabel}>Paciente ID:</Text>
        <TextInput
          style={styles.patientInput}
          value={pacienteId}
          onChangeText={(novo) => {
            setPacienteId(novo);
            setRecomendacao(null);
            setErroIA(null);
          }}
          placeholder="paciente-01"
          placeholderTextColor="#64748b"
          autoCapitalize="none"
        />
        <TouchableOpacity
          style={styles.refreshMiniBtn}
          onPress={() => carregarDados(false)}
        >
          <Text style={styles.refreshMiniText}>Atualizar</Text>
        </TouchableOpacity>
      </View>

      {/* Indicador de atualização a cada 5s */}
      <View style={styles.ageRow}>
        <Text style={styles.ageText}>
          {idadeSegundos !== null
            ? `Atualizado há ${idadeSegundos} s`
            : "Aguardando leitura..."}
        </Text>
        <Text style={styles.pollingHint}>Auto-refresh: 5 s • Puxe p/ atualizar</Text>
      </View>

      {carregandoStatus && !statusDados ? (
        <View style={styles.centerBox}>
          <ActivityIndicator size="large" color="#38bdf8" />
          <Text style={styles.loadingText}>Carregando telemetria...</Text>
        </View>
      ) : null}

      {erroStatus ? (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>Aviso de Telemetria</Text>
          <Text style={styles.errorMsg}>{erroStatus}</Text>
        </View>
      ) : null}

      {statusDados && leitura ? (
        <>
          {/* Banner de Risco com Cor + Texto */}
          <View
            style={[
              styles.riskBanner,
              {
                backgroundColor: temaRisco.corFundo,
                borderColor: temaRisco.corBorda,
              },
            ]}
          >
            <View style={styles.riskHeaderRow}>
              <Text style={[styles.riskTitle, { color: temaRisco.corTexto }]}>
                {temaRisco.rotulo}
              </Text>
              <Text style={[styles.riskProb, { color: temaRisco.corTexto }]}>
                Probabilidade: {Math.round((statusDados.probabilidade || 0) * 100)}%
              </Text>
            </View>
            <Text style={[styles.riskSub, { color: temaRisco.corTexto }]}>
              {statusDados.alerta
                ? "⚠️ Alerta clínico/operacional ativo para este paciente"
                : "Parâmetros dentro do limiar de estabilidade operacional"}
            </Text>
          </View>

          {/* Cards de Sinais Vitais (BPM, SpO2, Temperatura) */}
          <View style={styles.vitalsGrid}>
            <View style={styles.vitalCard}>
              <Text style={styles.vitalLabel}>Frequência (BPM)</Text>
              <Text style={styles.vitalValue}>
                {Number(leitura.fc_media).toFixed(0)}
              </Text>
              <Text style={styles.vitalUnit}>bpm</Text>
            </View>

            <View style={styles.vitalCard}>
              <Text style={styles.vitalLabel}>Saturação (SpO2)</Text>
              <Text style={styles.vitalValue}>
                {Number(leitura.spo2_media).toFixed(1)}
              </Text>
              <Text style={styles.vitalUnit}>%</Text>
            </View>

            <View style={styles.vitalCard}>
              <Text style={styles.vitalLabel}>Temperatura</Text>
              <Text style={styles.vitalValue}>
                {Number(leitura.temperatura).toFixed(1)}
              </Text>
              <Text style={styles.vitalUnit}>°C</Text>
            </View>
          </View>

          {/* Protocolos Acionados */}
          <View style={styles.sectionCard}>
            <Text style={styles.sectionTitle}>Protocolos Acionados</Text>
            {protocolos.length === 0 ? (
              <Text style={styles.emptyProtocols}>
                Nenhum protocolo crítico acionado no momento.
              </Text>
            ) : (
              protocolos.map((prot, idx) => (
                <View key={`${idx}-${prot}`} style={styles.protocolItem}>
                  <Text style={styles.protocolBullet}>•</Text>
                  <Text style={styles.protocolText}>{prot}</Text>
                </View>
              ))
            )}
          </View>

          {/* Botão Recomendação IA (/recomendacao) */}
          <TouchableOpacity
            style={[styles.aiButton, carregandoIA && styles.aiButtonDisabled]}
            onPress={handleGerarRecomendacao}
            disabled={carregandoIA}
          >
            {carregandoIA ? (
              <View style={styles.aiLoadingRow}>
                <ActivityIndicator color="#ffffff" />
                <Text style={styles.aiButtonText}>
                  {"  "}Executando Agentes IA...
                </Text>
              </View>
            ) : (
              <Text style={styles.aiButtonText}>✨ Recomendação IA</Text>
            )}
          </TouchableOpacity>

          {erroIA ? (
            <View style={styles.errorCard}>
              <Text style={styles.errorMsg}>{erroIA}</Text>
            </View>
          ) : null}

          {recomendacao ? (
            <View style={styles.aiResultCard}>
              <Text style={styles.aiResultTitle}>
                Parecer do Sistema Multiagente (Fase 6)
              </Text>
              <Text style={styles.aiMeta}>
                Classificação: {recomendacao.classificacao} (
                {Math.round((recomendacao.probabilidade || 0) * 100)}%)
              </Text>

              <Text style={styles.aiSubHeader}>Ações Operacionais:</Text>
              {(recomendacao.acoes_operacionais || []).map((acao, i) => (
                <Text key={`acao-${i}`} style={styles.aiListItem}>
                  • {acao}
                </Text>
              ))}

              <Text style={styles.aiSubHeader}>Justificativa Clínica:</Text>
              <Text style={styles.aiBodyText}>
                {recomendacao.justificativa}
              </Text>

              <View style={styles.disclaimerBox}>
                <Text style={styles.disclaimerText}>{recomendacao.aviso}</Text>
              </View>
            </View>
          ) : null}
        </>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0f172a",
  },
  content: {
    padding: 16,
    paddingBottom: 40,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 14,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: "800",
    color: "#f8fafc",
  },
  headerSub: {
    fontSize: 12,
    color: "#94a3b8",
  },
  logoutBtn: {
    backgroundColor: "#334155",
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
  },
  logoutText: {
    color: "#f8fafc",
    fontWeight: "600",
    fontSize: 13,
  },
  patientBar: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#1e293b",
    borderRadius: 10,
    padding: 10,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#334155",
  },
  patientLabel: {
    color: "#cbd5e1",
    fontSize: 13,
    fontWeight: "600",
    marginRight: 8,
  },
  patientInput: {
    flex: 1,
    backgroundColor: "#0f172a",
    color: "#f8fafc",
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 14,
    borderWidth: 1,
    borderColor: "#334155",
  },
  refreshMiniBtn: {
    marginLeft: 8,
    backgroundColor: "#0284c7",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  refreshMiniText: {
    color: "#ffffff",
    fontSize: 12,
    fontWeight: "700",
  },
  ageRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  ageText: {
    color: "#38bdf8",
    fontSize: 13,
    fontWeight: "700",
  },
  pollingHint: {
    color: "#64748b",
    fontSize: 11,
  },
  centerBox: {
    padding: 32,
    alignItems: "center",
  },
  loadingText: {
    color: "#94a3b8",
    marginTop: 10,
  },
  riskBanner: {
    borderRadius: 12,
    padding: 16,
    borderWidth: 1.5,
    marginBottom: 14,
  },
  riskHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  riskTitle: {
    fontSize: 18,
    fontWeight: "800",
  },
  riskProb: {
    fontSize: 14,
    fontWeight: "700",
  },
  riskSub: {
    fontSize: 12,
  },
  vitalsGrid: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 14,
  },
  vitalCard: {
    flex: 1,
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 12,
    marginHorizontal: 4,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#334155",
  },
  vitalLabel: {
    color: "#94a3b8",
    fontSize: 11,
    fontWeight: "600",
    marginBottom: 6,
    textAlign: "center",
  },
  vitalValue: {
    color: "#f8fafc",
    fontSize: 24,
    fontWeight: "800",
  },
  vitalUnit: {
    color: "#64748b",
    fontSize: 12,
    marginTop: 2,
  },
  sectionCard: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#334155",
  },
  sectionTitle: {
    color: "#f8fafc",
    fontSize: 15,
    fontWeight: "700",
    marginBottom: 10,
  },
  emptyProtocols: {
    color: "#94a3b8",
    fontSize: 13,
    fontStyle: "italic",
  },
  protocolItem: {
    flexDirection: "row",
    marginBottom: 6,
  },
  protocolBullet: {
    color: "#f87171",
    fontSize: 15,
    marginRight: 8,
    fontWeight: "700",
  },
  protocolText: {
    color: "#e2e8f0",
    fontSize: 13,
    flex: 1,
  },
  aiButton: {
    backgroundColor: "#2563eb",
    borderRadius: 12,
    paddingVertical: 15,
    alignItems: "center",
    marginBottom: 14,
  },
  aiButtonDisabled: {
    opacity: 0.7,
  },
  aiLoadingRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  aiButtonText: {
    color: "#ffffff",
    fontSize: 16,
    fontWeight: "700",
  },
  aiResultCard: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: "#3b82f6",
    marginBottom: 16,
  },
  aiResultTitle: {
    color: "#93c5fd",
    fontSize: 16,
    fontWeight: "800",
    marginBottom: 4,
  },
  aiMeta: {
    color: "#cbd5e1",
    fontSize: 13,
    fontWeight: "600",
    marginBottom: 10,
  },
  aiSubHeader: {
    color: "#f8fafc",
    fontSize: 13,
    fontWeight: "700",
    marginTop: 8,
    marginBottom: 4,
  },
  aiListItem: {
    color: "#e2e8f0",
    fontSize: 13,
    marginBottom: 4,
    lineHeight: 19,
  },
  aiBodyText: {
    color: "#cbd5e1",
    fontSize: 13,
    lineHeight: 20,
  },
  disclaimerBox: {
    marginTop: 12,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "#334155",
  },
  disclaimerText: {
    color: "#94a3b8",
    fontSize: 11,
    fontStyle: "italic",
  },
  errorCard: {
    backgroundColor: "#450a0a",
    borderColor: "#dc2626",
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 14,
  },
  errorTitle: {
    color: "#fecaca",
    fontWeight: "700",
    fontSize: 13,
    marginBottom: 4,
  },
  errorMsg: {
    color: "#fca5a5",
    fontSize: 13,
  },
});

