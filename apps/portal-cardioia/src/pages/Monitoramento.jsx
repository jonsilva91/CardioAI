import { useCallback, useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import Navbar from "../components/Navbar";
import { API_ENDPOINTS } from "../config";
import { useAuth } from "../contexts/useAuth";
import styles from "./Monitoramento.module.css";

const POLLING_INTERVAL_MS = 5000;

function formatarHorario(isoString) {
  if (!isoString) return "--:--:--";
  try {
    const dt = new Date(isoString);
    return dt.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return isoString;
  }
}

export default function Monitoramento() {
  const { token, logout } = useAuth();

  const [pacienteId, setPacienteId] = useState("PAC-001");
  const [statusData, setStatusData] = useState(null);
  const [historico, setHistorico] = useState([]);
  const [carregandoInicial, setCarregandoInicial] = useState(true);
  const [servidorAcordando, setServidorAcordando] = useState(false);
  const [erroStatus, setErroStatus] = useState("");

  const [recomendacao, setRecomendacao] = useState(null);
  const [carregandoIA, setCarregandoIA] = useState(false);
  const [erroIA, setErroIA] = useState("");

  const buscarTelemetria = useCallback(
    async (primeiraCarga = false) => {
      const idLimpo = pacienteId.trim();
      if (!idLimpo || !token) return;

      let wakeTimer = null;
      if (primeiraCarga) {
        setCarregandoInicial(true);
        wakeTimer = setTimeout(() => {
          setServidorAcordando(true);
        }, 1800);
      }

      try {
        const headers = {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        };

        const [resStatus, resHist] = await Promise.all([
          fetch(API_ENDPOINTS.pacienteStatus(idLimpo), { headers }),
          fetch(API_ENDPOINTS.pacienteHistorico(idLimpo, 50), { headers }),
        ]);

        if (resStatus.status === 401 || resHist.status === 401) {
          logout();
          return;
        }

        if (resStatus.status === 404) {
          setStatusData(null);
          setHistorico([]);
          setErroStatus(
            `Sem dados de telemetria para o paciente '${idLimpo}'. Envie uma leitura via dispositivo IoT (/api/telemetria).`
          );
          return;
        }

        if (!resStatus.ok) {
          throw new Error(`Falha ao consultar status (${resStatus.status})`);
        }

        const dadosStatus = await resStatus.json();
        setStatusData(dadosStatus);
        setErroStatus("");

        if (resHist.ok) {
          const dadosHist = await resHist.json();
          const leituras = Array.isArray(dadosHist.leituras)
            ? [...dadosHist.leituras].reverse()
            : [];
          setHistorico(
            leituras.map((item, idx) => ({
              indice: idx + 1,
              horario: formatarHorario(item.timestamp),
              BPM: Number(item.fc_media),
              SpO2: Number(item.spo2_media),
              Temperatura: Number(item.temperatura),
            }))
          );
        }
      } catch {
        setErroStatus(
          "Não foi possível obter os dados de monitoramento no momento."
        );
      } finally {
        if (wakeTimer) clearTimeout(wakeTimer);
        setCarregandoInicial(false);
        setServidorAcordando(false);
      }
    },
    [pacienteId, token, logout]
  );

  useEffect(() => {
    buscarTelemetria(true);
    const interval = setInterval(() => {
      buscarTelemetria(false);
    }, POLLING_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [buscarTelemetria]);

  async function handleGerarRecomendacao() {
    const idLimpo = pacienteId.trim();
    if (!idLimpo || !token) return;

    setCarregandoIA(true);
    setErroIA("");

    try {
      const res = await fetch(API_ENDPOINTS.pacienteRecomendacao(idLimpo), {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.status === 401) {
        logout();
        return;
      }

      const data = await res.json().catch(() => null);
      if (!res.ok) {
        throw new Error(
          data?.detail || `Erro ao gerar recomendação (${res.status})`
        );
      }

      setRecomendacao(data);
    } catch (err) {
      setErroIA(err.message || "Falha ao consultar agentes de IA.");
    } finally {
      setCarregandoIA(false);
    }
  }

  const leitura = statusData?.ultima_leitura;
  const classificacao = String(
    statusData?.classificacao || "BAIXO"
  ).toUpperCase();
  const probabilidadePct =
    statusData?.probabilidade !== undefined
      ? Math.round(Number(statusData.probabilidade) * 100)
      : 0;
  const idadeSegundos =
    statusData?.idade_leitura_segundos !== undefined
      ? Math.round(Number(statusData.idade_leitura_segundos))
      : null;

  const classeCorRisco =
    classificacao === "ALTO"
      ? styles.riskAlto
      : classificacao === "MODERADO"
        ? styles.riskModerado
        : styles.riskBaixo;

  const textoRisco =
    classificacao === "ALTO"
      ? "RISCO ALTO — EMERGÊNCIA / ALERTA ATIVO"
      : classificacao === "MODERADO"
        ? "RISCO MODERADO — ATENÇÃO CLÍNICA"
        : "RISCO BAIXO — PACIENTE ESTÁVEL";

  const aoVivo = idadeSegundos !== null && idadeSegundos <= 15;
  const protocolos = Array.isArray(statusData?.protocolos)
    ? statusData.protocolos
    : [];

  return (
    <div className={styles.page}>
      <Navbar />

      <main className={styles.content}>
        <section className={styles.topBar}>
          <div className={styles.titleGroup}>
            <h2>Monitoramento Cardiológico em Tempo Real</h2>
            <p>
              Telemetria IoT com predição de risco (Machine Learning Fase 6) e
              atualização automática a cada 5 s.
            </p>
          </div>

          <div className={styles.controlsGroup}>
            <div className={styles.patientSelector}>
              <label htmlFor="pacienteIdInput">Paciente:</label>
              <input
                id="pacienteIdInput"
                type="text"
                value={pacienteId}
                onChange={(e) => {
                  setPacienteId(e.target.value);
                  setRecomendacao(null);
                  setErroIA("");
                }}
              />
            </div>

            {idadeSegundos !== null ? (
              <span className={aoVivo ? styles.liveBadge : styles.staleBadge}>
                {aoVivo
                  ? `● Ao vivo (atualizado há ${idadeSegundos} s)`
                  : `⏳ Sem dados novos há ${idadeSegundos} s`}
              </span>
            ) : (
              <span className={styles.staleBadge}>⏳ Sem dados</span>
            )}
          </div>
        </section>

        {(servidorAcordando || carregandoInicial) && !statusData && (
          <div className={styles.wakeBanner}>
            ⏳ Servidor acordando, aguarde... Conectando ao backend no Render.
          </div>
        )}

        {erroStatus && <div className={styles.errorBanner}>{erroStatus}</div>}

        {statusData && leitura && (
          <>
            {/* Indicador de Risco Grande (Probabilidade + BAIXO/MODERADO/ALTO com Cor e Texto) */}
            <section className={`${styles.riskHero} ${classeCorRisco}`}>
              <div>
                <div className={styles.riskLabelSmall}>
                  Classificação do Modelo Preditivo (Fase 6)
                </div>
                <div className={styles.riskClassText}>{textoRisco}</div>
                <div className={styles.riskSubText}>
                  Dispositivo: <strong>{leitura.device_id}</strong> • Paciente:{" "}
                  <strong>{statusData.paciente_id}</strong>
                </div>
              </div>

              <div className={styles.riskProbBox}>
                <div className={styles.riskProbValue}>{probabilidadePct}%</div>
                <div className={styles.riskProbCaption}>
                  Probabilidade ({Number(statusData.probabilidade).toFixed(2)})
                </div>
              </div>
            </section>

            {/* Cards BPM, SpO2, Temperatura e Horário */}
            <section className={styles.cardsGrid}>
              <div className={styles.vitalCard}>
                <div className={styles.vitalHeader}>Frequência Cardíaca</div>
                <div>
                  <span className={styles.vitalNumber}>
                    {Number(leitura.fc_media).toFixed(0)}
                  </span>
                  <span className={styles.vitalUnit}>BPM</span>
                </div>
                <div className={styles.vitalMeta}>Faixa normal: 60–100 bpm</div>
              </div>

              <div className={styles.vitalCard}>
                <div className={styles.vitalHeader}>Saturação de O₂ (SpO2)</div>
                <div>
                  <span className={styles.vitalNumber}>
                    {Number(leitura.spo2_media).toFixed(1)}
                  </span>
                  <span className={styles.vitalUnit}>%</span>
                </div>
                <div className={styles.vitalMeta}>Alvo clínico: ≥ 94%</div>
              </div>

              <div className={styles.vitalCard}>
                <div className={styles.vitalHeader}>Temperatura Corporal</div>
                <div>
                  <span className={styles.vitalNumber}>
                    {Number(leitura.temperatura).toFixed(1)}
                  </span>
                  <span className={styles.vitalUnit}>°C</span>
                </div>
                <div className={styles.vitalMeta}>Limiar febril: &gt; 38.0 °C</div>
              </div>

              <div className={styles.vitalCard}>
                <div className={styles.vitalHeader}>Horário da Leitura</div>
                <div>
                  <span className={styles.vitalNumber}>
                    {formatarHorario(leitura.timestamp)}
                  </span>
                </div>
                <div className={styles.vitalMeta}>
                  Idade da leitura: {idadeSegundos} s
                </div>
              </div>
            </section>

            {/* Gráfico de Série Temporal (Recharts) + Protocolos */}
            <section className={styles.mainGrid}>
              <div className={styles.panel}>
                <h3>Série Histórica de Sinais Vitais (/historico)</h3>
                <div className={styles.chartContainer}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={historico}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="horario" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="BPM"
                        stroke="#ef4444"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="SpO2"
                        stroke="#2563eb"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="Temperatura"
                        stroke="#f59e0b"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className={styles.panel}>
                <h3>Protocolos Clínicos Acionados</h3>
                {protocolos.length === 0 ? (
                  <p className={styles.emptyProtocol}>
                    Nenhum protocolo emergencial acionado na leitura atual.
                  </p>
                ) : (
                  <ul className={styles.protocolList}>
                    {protocolos.map((prot, index) => (
                      <li key={`${index}-${prot}`} className={styles.protocolItem}>
                        {prot}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </section>

            {/* Botão "Gerar recomendação com IA" e Resposta dos Agentes */}
            <section className={styles.aiSection}>
              <div className={styles.aiHeader}>
                <div>
                  <h3>Pipeline Multiagente de Triagem (Fase 6)</h3>
                  <p style={{ color: "#64748b", fontSize: "14px" }}>
                    Orquestrador + Analista de Risco + Especialista em Protocolos
                    + Planejador de Resposta
                  </p>
                </div>

                <button
                  type="button"
                  className={styles.aiButton}
                  onClick={handleGerarRecomendacao}
                  disabled={carregandoIA}
                >
                  {carregandoIA
                    ? "Executando Agentes IA..."
                    : "✨ Gerar recomendação com IA"}
                </button>
              </div>

              {erroIA && <div className={styles.errorBanner}>{erroIA}</div>}

              {recomendacao && (
                <div className={styles.aiResult}>
                  <div>
                    <strong>Classificação Consolidada:</strong>{" "}
                    {recomendacao.classificacao} (Probabilidade:{" "}
                    {Math.round((recomendacao.probabilidade || 0) * 100)}%)
                  </div>

                  <h4>Protocolos Sugeridos</h4>
                  <ul>
                    {(recomendacao.protocolos_sugeridos || []).map((p, i) => (
                      <li key={`prot-${i}`}>{p}</li>
                    ))}
                  </ul>

                  <h4>Ações Operacionais Recomendadas</h4>
                  <ul>
                    {(recomendacao.acoes_operacionais || []).map((a, i) => (
                      <li key={`acao-${i}`}>{a}</li>
                    ))}
                  </ul>

                  <h4>Justificativa Clínica</h4>
                  <p className={styles.aiJustification}>
                    {recomendacao.justificativa}
                  </p>

                  <div className={styles.aiDisclaimer}>
                    {recomendacao.aviso}
                  </div>
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

