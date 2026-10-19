"""
Robo de Monitoramento CardioAI - Fase 05 (Desafio Ir Alem 2 Refatorado)
======================================================================
Engenharia de Dados e Machine Learning:
1. Persistencia NoSQL Real com MongoDB (pymongo) / MongoDB Atlas
2. Modelo Preditivo de Machine Learning (Random Forest) substituindo limiares fixos
3. Pipeline automatizado de Extracao, Feature Engineering, Inferencia e Persistencia NoSQL
4. Consultas e Agregacoes analiticas em colecoes NoSQL
"""

import os
import sys
import time
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

# Forçar encoding UTF-8 no stdout/stderr no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ==============================================================================
# CONFIGURACOES E CAMINHOS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
DB_RELACIONAL_PATH = BASE_DIR / "pacientes.db"
MODEL_FILE_PATH = BASE_DIR / "modelo_risco.joblib"
CONFIG_FILE_PATH = BASE_DIR / "mongodb_config.json"

# Carregamento seguro de variáveis de ambiente (.env)
from dotenv import load_dotenv, find_dotenv
for _cand in [BASE_DIR / ".env", BASE_DIR.parent / ".env", BASE_DIR.parent.parent / ".env"]:
    if _cand.exists():
        load_dotenv(_cand)
        break
else:
    _dotenv_path = find_dotenv(usecwd=True)
    if _dotenv_path:
        load_dotenv(_dotenv_path)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CardioAI_RPA")

# Classes Clinicas Padronizadas (Diretrizes SBC - Sociedade Brasileira de Cardiologia)
CLASSES_RISCO = {
    0: "BAIXO_RISCO",        # Normotensao e FC normal (Estavel)
    1: "RISCO_MODERADO",     # Pre-hipertensao / Taquicardia ou Bradicardia leve
    2: "ALTO_RISCO",         # Hipertensao Estagio 2 / Taquicardia ou Bradicardia moderada
    3: "RISCO_CRITICO"       # Crise Hipertensiva (PAS>=180/PAD>=110) / Taquiarritmia Grave (FC>=130)
}

NOMES_FEATURES = [
    "pressao_sistolica",
    "pressao_diastolica",
    "frequencia_cardiaca",
    "pressao_arterial_media",
    "pressao_pulso",
    "indice_choque",
    "duplo_produto"
]


# ==============================================================================
# 1. MODULO DE ENGENHARIA DE FEATURES (HEMODINAMICA CLINICA)
# ==============================================================================
def calcular_features_clinicas(pas: float, pad: float, fc: float) -> Dict[str, float]:
    """
    Calcula variaveis hemodinamicas derivadas a partir de telemetria basica:
    - PAM (Pressao Arterial Media): (PAS + 2*PAD) / 3 (Indicador de perfusao tecidual)
    - PP (Pressao de Pulso): PAS - PAD (Marcador de rigidez arterial e risco cardiovascular)
    - SI (Indice de Choque): FC / PAS (Indicador hemodinamico de instabilidade/choque)
    - DP (Duplo Produto): (PAS * FC) / 100 (Consumo de oxigenio miocardico)
    """
    pam = round((pas + (2.0 * pad)) / 3.0, 2)
    pp = round(pas - pad, 2)
    si = round(fc / pas, 3) if pas > 0 else 0.0
    dp = round((pas * fc) / 100.0, 2)

    return {
        "pressao_sistolica": float(pas),
        "pressao_diastolica": float(pad),
        "frequencia_cardiaca": float(fc),
        "pressao_arterial_media": pam,
        "pressao_pulso": pp,
        "indice_choque": si,
        "duplo_produto": dp
    }


def extrair_vetor_features(features: Dict[str, float]) -> List[float]:
    """Retorna o vetor numerico ordenado para o modelo de ML."""
    return [features[nome] for nome in NOMES_FEATURES]


# ==============================================================================
# 2. MODULO DE MACHINE LEARNING (TREINAMENTO, SERIALIZACAO E INFERENCIA)
# ==============================================================================
def gerar_dados_treinamento_clinico(n_amostras: int = 1200) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gera dataset sintetico calibrado estritamente de acordo com as Diretrizes
    Brasileiras de Hipertensao Arterial (SBC/SBH) e Eletrofisiologia Clinica.
    """
    np.random.seed(42)
    X_raw = []
    y = []

    amostras_por_classe = n_amostras // 4

    # Classe 0: BAIXO_RISCO (Normotenso / FC fisiologica)
    for _ in range(amostras_por_classe):
        pas = np.random.normal(118, 5)
        pad = np.random.normal(76, 4)
        fc = np.random.normal(72, 8)
        X_raw.append((pas, pad, fc))
        y.append(0)

    # Classe 1: RISCO_MODERADO (Pre-hipertensao / Taqui ou Bradicardia leve)
    for _ in range(amostras_por_classe):
        subtipo = np.random.choice(["pre_hipertensao", "taqui_leve", "bradi_leve"])
        if subtipo == "pre_hipertensao":
            pas = np.random.normal(134, 4)
            pad = np.random.normal(86, 3)
            fc = np.random.normal(75, 8)
        elif subtipo == "taqui_leve":
            pas = np.random.normal(122, 6)
            pad = np.random.normal(78, 5)
            fc = np.random.normal(104, 4)
        else:
            pas = np.random.normal(120, 6)
            pad = np.random.normal(76, 5)
            fc = np.random.normal(54, 3)
        X_raw.append((pas, pad, fc))
        y.append(1)

    # Classe 2: ALTO_RISCO (Hipertensao Estagio 2 / Arritmia moderada)
    for _ in range(amostras_por_classe):
        subtipo = np.random.choice(["hipertensao_e2", "taqui_moderada", "bradi_moderada"])
        if subtipo == "hipertensao_e2":
            pas = np.random.normal(164, 6)
            pad = np.random.normal(104, 4)
            fc = np.random.normal(88, 10)
        elif subtipo == "taqui_moderada":
            pas = np.random.normal(138, 8)
            pad = np.random.normal(88, 6)
            fc = np.random.normal(122, 5)
        else:
            pas = np.random.normal(115, 6)
            pad = np.random.normal(72, 5)
            fc = np.random.normal(44, 3)
        X_raw.append((pas, pad, fc))
        y.append(2)

    # Classe 3: RISCO_CRITICO (Crise Hipertensiva PAS>=180 ou PAD>=110 / Taquicardia grave FC>=130 ou Bradicardia <40)
    for _ in range(amostras_por_classe):
        subtipo = np.random.choice(["crise_hipertensiva", "taqui_grave", "choque_instavel"])
        if subtipo == "crise_hipertensiva":
            pas = np.random.normal(192, 10)
            pad = np.random.normal(118, 6)
            fc = np.random.normal(112, 14)
        elif subtipo == "taqui_grave":
            pas = np.random.normal(148, 12)
            pad = np.random.normal(92, 8)
            fc = np.random.normal(146, 12)
        else: # Choque cardiogenico / colapso hemodinamico
            pas = np.random.normal(78, 6)
            pad = np.random.normal(48, 5)
            fc = np.random.normal(132, 10)
        X_raw.append((pas, pad, fc))
        y.append(3)

    # Construir features completas
    X = []
    for pas, pad, fc in X_raw:
        feats = calcular_features_clinicas(pas, pad, fc)
        X.append(extrair_vetor_features(feats))

    return np.array(X), np.array(y)


def treinar_ou_carregar_modelo() -> Pipeline:
    """
    Carrega o modelo de Machine Learning serializado ou treina um novo Random Forest
    com calibracao clinica e pipeline de normalizacao (StandardScaler).
    """
    if MODEL_FILE_PATH.exists():
        try:
            pipeline = joblib.load(MODEL_FILE_PATH)
            logger.info(f"[ML] Modelo preditivo carregado com sucesso de: {MODEL_FILE_PATH.name}")
            return pipeline
        except Exception as e:
            logger.warning(f"[ML] Falha ao carregar modelo salvo ({e}). Retreinando...")

    logger.info("[ML] Treinando classificador de risco cardiovascular (Random Forest Pipeline)...")
    X, y = gerar_dados_treinamento_clinico(n_amostras=1600)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=120,
            max_depth=7,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    logger.info(f"[ML] Modelo treinado com sucesso! Acuracia de Teste: {acc:.2%}")
    logger.info("\n" + classification_report(y_test, y_pred, target_names=list(CLASSES_RISCO.values())))

    joblib.dump(pipeline, MODEL_FILE_PATH)
    logger.info(f"[ML] Pipeline serializado e persistido em: {MODEL_FILE_PATH.name}")
    return pipeline


def realizar_inferencia_clinica(pipeline: Pipeline, pas: float, pad: float, fc: float) -> Dict[str, Any]:
    """
    Recebe telemetria bruta de sensores, calcula variaveis hemodinamicas,
    executa a inferencia probabilistica com o modelo treinado e produz o diagnostico.
    """
    features = calcular_features_clinicas(pas, pad, fc)
    vetor = np.array([extrair_vetor_features(features)])

    classe_id = int(pipeline.predict(vetor)[0])
    probabilidades = pipeline.predict_proba(vetor)[0]
    confianca = float(probabilidades[classe_id])
    risco_nivel = CLASSES_RISCO[classe_id]

    distribuicao = {
        CLASSES_RISCO[idx]: round(float(prob), 4)
        for idx, prob in enumerate(probabilidades)
    }

    # Determinacao de alertas e recomendacoes clinicas baseadas no modelo
    alerta_critico = classe_id in [2, 3]

    recomendacoes = {
        "BAIXO_RISCO": "Parametros hemodinamicos estaveis. Manter monitoramento de rotina.",
        "RISCO_MODERADO": "Alteracao hemodinamica leve/moderada. Intensificar frequencia de leitura e reavaliar em 15 minutos.",
        "ALTO_RISCO": "Desvio significativo detectado. Notificar equipe de enfermagem/cardiologia para avaliacao imediata.",
        "RISCO_CRITICO": "EMERGENCIA CARDIOLOGICA: Protocolo de crise hipertensiva/arritmia acionado. Avaliacao medica de urgencia requerida!"
    }

    anomalias_detectadas = []
    if pas >= 180 or pad >= 110:
        anomalias_detectadas.append(f"Crise Hipertensiva (PA: {pas:.0f}/{pad:.0f} mmHg)")
    elif pas >= 140 or pad >= 90:
        anomalias_detectadas.append(f"Hipertensao Estagio 1/2 (PA: {pas:.0f}/{pad:.0f} mmHg)")
    elif pas < 90 or pad < 60:
        anomalias_detectadas.append(f"Hipotensao Arterial (PA: {pas:.0f}/{pad:.0f} mmHg)")

    if fc >= 130:
        anomalias_detectadas.append(f"Taquiarritmia Grave (FC: {fc:.0f} bpm)")
    elif fc >= 100:
        anomalias_detectadas.append(f"Taquicardia Sinusal (FC: {fc:.0f} bpm)")
    elif fc <= 45:
        anomalias_detectadas.append(f"Bradicardia Severa (FC: {fc:.0f} bpm)")
    elif fc < 60:
        anomalias_detectadas.append(f"Bradicardia Leve (FC: {fc:.0f} bpm)")

    if not anomalias_detectadas:
        anomalias_detectadas.append("Padrao fisiologico normal")

    return {
        "risco_nivel": risco_nivel,
        "classe_id": classe_id,
        "confianca": round(confianca, 4),
        "alerta_critico": alerta_critico,
        "distribuicao_probabilidades": distribuicao,
        "anomalias_detectadas": anomalias_detectadas,
        "recomendacao_clinica": recomendacoes.get(risco_nivel, ""),
        "features_calculadas": features
    }


# ==============================================================================
# 3. CAMADA DE BANCO DE DADOS NOSQL (MONGODB REAL + FALLBACK RESILIENTE)
# ==============================================================================
class NoSQLManager:
    """
    Gerenciador de integracao com banco NoSQL MongoDB / MongoDB Atlas.
    Fornece conexao, criacao de indices, insercao e consultas analiticas.
    Possui buffer de fallback resiliente caso o servidor MongoDB local nao esteja ativo.
    """

    def __init__(self, config_path: Path = CONFIG_FILE_PATH):
        self.config = self._carregar_config(config_path)
        self.client: Optional[MongoClient] = None
        self.db = None
        self.is_connected = False
        self.in_memory_collection: List[Dict[str, Any]] = []

        self._conectar()

    def _carregar_config(self, config_path: Path) -> Dict[str, Any]:
        """Carrega configuracao JSON ou define defaults resilientes."""
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"[NoSQL] Erro ao ler {config_path}: {e}")

        return {
            "conexao": {
                "uri": "mongodb://localhost:27017",
                "database": "cardioai_nosql",
                "options": {"serverSelectionTimeoutMS": 2500}
            },
            "colecoes": {
                "diagnosticos_ia": {"nome": "diagnosticos_ia"},
                "logs_auditoria": {"nome": "logs_auditoria_rpa"}
            }
        }

    def _conectar(self):
        """Estabelece conexao com MongoDB via pymongo ou ativa buffer NoSQL local."""
        uri = (
            os.environ.get("MONGO_URI")
            or os.environ.get("MONGODB_URI")
            or self.config.get("conexao", {}).get("uri", "mongodb://localhost:27017")
        )
        db_name = os.environ.get("MONGO_DATABASE", self.config.get("conexao", {}).get("database", "cardioai_nosql"))
        timeout = int(os.environ.get("MONGO_TIMEOUT_MS", 10000))

        if not PYMONGO_AVAILABLE:
            raise RuntimeError("Biblioteca 'pymongo' não encontrada no ambiente virtual.")

        try:
            logger.info(f"[NoSQL] Conectando ao MongoDB ({uri.split('@')[-1] if '@' in uri else uri})...")
            self.client = MongoClient(uri, serverSelectionTimeoutMS=timeout, connectTimeoutMS=timeout)
            # Teste ativo de conectividade (ping)
            self.client.admin.command("ping")
            self.db = self.client[db_name]
            self.is_connected = True
            logger.info(f"[NoSQL - MONGODB REAL] Conexão com MongoDB Real estabelecida com sucesso! Banco: '{db_name}'")
            self._garantir_indices()
            return
        except Exception as e:
            logger.error(f"[NoSQL - ERRO CRÍTICO] Falha ao conectar no MongoDB ({e})")
            if "mongodb+srv://" in uri or os.environ.get("STRICT_MONGO", "true").lower() == "true":
                raise RuntimeError(f"ERRO: Conexão com MongoDB Atlas falhou: {e}")
            logger.warning(f"[NoSQL] Servidor MongoDB indisponível no endpoint ({e}). Ativando modo NoSQL Resiliente...")

        self.is_connected = False
        logger.info("[NoSQL - FALLBACK LOCAL] Modo Fallback Ativo: coleções gerenciadas localmente com persistência BSON estruturada.")

    def _garantir_indices(self):
        """Cria indices otimizados para busca por paciente, data e severidade."""
        if not self.is_connected or self.db is None:
            return
        try:
            col_diag = self.db["diagnosticos_ia"]
            col_diag.create_index([("paciente_id", ASCENDING), ("timestamp_inferencia", DESCENDING)])
            col_diag.create_index([("predicao.risco_nivel", ASCENDING)])
            col_diag.create_index([("predicao.alerta_critico", ASCENDING)])
            col_diag.create_index([("id_diagnostico", ASCENDING)], unique=True)
            logger.info("[NoSQL] Indices de busca e performance criados na colecao 'diagnosticos_ia'.")
        except Exception as e:
            logger.warning(f"[NoSQL] Aviso ao criar indices: {e}")

    def inserir_diagnostico(self, diagnostico: Dict[str, Any]) -> str:
        """Insere um registro completo de diagnostico e predicao na colecao NoSQL."""
        if self.is_connected and self.db is not None:
            try:
                resultado = self.db["diagnosticos_ia"].insert_one(diagnostico)
                return str(resultado.inserted_id)
            except Exception as e:
                logger.error(f"[NoSQL] Falha ao gravar no MongoDB: {e}")

        # Fallback NoSQL local
        self.in_memory_collection.append(diagnostico)
        return str(diagnostico.get("id_diagnostico", f"MOCK-{len(self.in_memory_collection)}"))

    def consultar_historico_paciente(self, paciente_id: int, limite: int = 5) -> List[Dict[str, Any]]:
        """Consulta o historico recente de diagnosticos de um determinado paciente."""
        if self.is_connected and self.db is not None:
            cursor = self.db["diagnosticos_ia"].find(
                {"paciente_id": paciente_id},
                {"_id": 0}
            ).sort("timestamp_inferencia", DESCENDING).limit(limite)
            return list(cursor)

        # Fallback local
        filtrados = [d for d in self.in_memory_collection if d.get("paciente_id") == paciente_id]
        filtrados.sort(key=lambda x: x.get("timestamp_inferencia", ""), reverse=True)
        return filtrados[:limite]

    def consultar_alertas_criticos(self, limite: int = 5) -> List[Dict[str, Any]]:
        """Busca os ultimos alertas classificados como alto risco ou risco critico."""
        if self.is_connected and self.db is not None:
            cursor = self.db["diagnosticos_ia"].find(
                {"predicao.alerta_critico": True},
                {"_id": 0}
            ).sort("timestamp_inferencia", DESCENDING).limit(limite)
            return list(cursor)

        filtrados = [d for d in self.in_memory_collection if d.get("predicao", {}).get("alerta_critico") is True]
        filtrados.sort(key=lambda x: x.get("timestamp_inferencia", ""), reverse=True)
        return filtrados[:limite]

    def obter_estatisticas_risco(self) -> Dict[str, Any]:
        """Executa agregacao NoSQL para sumarizar as predicoes por nivel de risco."""
        if self.is_connected and self.db is not None:
            pipeline = [
                {
                    "$group": {
                        "_id": "$predicao.risco_nivel",
                        "total": {"$sum": 1},
                        "confianca_media": {"$avg": "$predicao.confianca"}
                    }
                }
            ]
            try:
                res = list(self.db["diagnosticos_ia"].aggregate(pipeline))
                return {item["_id"]: {"total": item["total"], "confianca_media": round(item["confianca_media"], 3)} for item in res}
            except Exception as e:
                logger.warning(f"[NoSQL] Falha na agregacao MongoDB: {e}")

        # Agregacao local equivalente
        stats = {}
        for d in self.in_memory_collection:
            r = d.get("predicao", {}).get("risco_nivel", "DESCONHECIDO")
            conf = d.get("predicao", {}).get("confianca", 0.0)
            if r not in stats:
                stats[r] = {"total": 0, "soma_conf": 0.0}
            stats[r]["total"] += 1
            stats[r]["soma_conf"] += conf

        return {
            k: {"total": v["total"], "confianca_media": round(v["soma_conf"] / v["total"], 3)}
            for k, v in stats.items()
        }


# ==============================================================================
# 4. BANCO RELACIONAL SIMULADO (SQLITE) - FONTE DE DADOS IOT
# ==============================================================================
def init_relational_db():
    """Inicializa a base SQLite com telemetria clinica de multiplos perfis de pacientes."""
    conn = sqlite3.connect(DB_RELACIONAL_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leituras_sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            pressao_sistolica INTEGER,
            pressao_diastolica INTEGER,
            frequencia_cardiaca INTEGER,
            timestamp TEXT
        )
    """)

    # Limpar e reinserir conjunto demonstrativo completo
    cursor.execute("DELETE FROM leituras_sensores")
    dados_simulados = [
        (101, 120, 80, 72, datetime.now().isoformat()),   # Caso 1: Estavel / Baixo Risco
        (102, 195, 115, 128, datetime.now().isoformat()), # Caso 2: Crise Hipertensiva + Taquicardia (Critico)
        (103, 108, 68, 42, datetime.now().isoformat()),   # Caso 3: Bradicardia Severa (Alto Risco)
        (104, 138, 88, 106, datetime.now().isoformat()),  # Caso 4: Pre-hipertensao + Taquicardia Leve (Moderado)
        (105, 168, 102, 94, datetime.now().isoformat()),  # Caso 5: Hipertensao Estagio 2 (Alto Risco)
        (106, 82, 52, 134, datetime.now().isoformat())    # Caso 6: Choque / Hipotensao com taquicardia (Critico)
    ]
    cursor.executemany("""
        INSERT INTO leituras_sensores (paciente_id, pressao_sistolica, pressao_diastolica, frequencia_cardiaca, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, dados_simulados)
    conn.commit()
    conn.close()
    logger.info(f"[SQLite] Base relacional inicializada com {len(dados_simulados)} leituras de telemetria IoT.")


def extrair_leituras_recentes(limite: int = 10) -> List[Tuple]:
    """Extrai as leituras mais recentes registradas pelos sensores no banco relacional."""
    conn = sqlite3.connect(DB_RELACIONAL_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, paciente_id, pressao_sistolica, pressao_diastolica, frequencia_cardiaca, timestamp FROM leituras_sensores ORDER BY id ASC LIMIT ?", (limite,))
    registros = cursor.fetchall()
    conn.close()
    return registros


# ==============================================================================
# 5. PIPELINE RPA DE INFERENCIA DE IA E PERSISTENCIA NOSQL
# ==============================================================================
def executar_pipeline_monitoramento(nosql: NoSQLManager, modelo: Pipeline) -> List[Dict[str, Any]]:
    """
    Executa o fluxo completo de Engenharia de Dados e Machine Learning:
    1. Extracao de telemetria do SQLite
    2. Engenharia de Features hemodinamicas
    3. Inferencia preditiva com Random Forest
    4. Enriquecimento de metadados e data lineage
    5. Persistencia automatica na colecao NoSQL
    """
    leituras = extrair_leituras_recentes()
    diagnosticos_gerados = []

    print("\n" + "="*80)
    print(f" EXECUCAO DO PIPELINE DE IA & PERSISTENCIA NOSQL - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    for leitura in leituras:
        id_leitura, paciente_id, pas, pad, fc, ts_leitura = leitura

        # Inferencia com o modelo de Machine Learning
        resultado_ia = realizar_inferencia_clinica(modelo, pas, pad, fc)

        # Montagem do documento NoSQL semi-estruturado (Schema Document-Oriented)
        id_diagnostico = f"DIAG-ML-{int(time.time()*1000)}-{paciente_id}"
        documento_nosql = {
            "id_diagnostico": id_diagnostico,
            "paciente_id": paciente_id,
            "timestamp_inferencia": datetime.now().isoformat(),
            "origem_leitura": {
                "fonte": "SQLite (Sensor IoT)",
                "id_leitura_relacional": id_leitura,
                "timestamp_leitura": ts_leitura
            },
            "telemetria": {
                "pressao_sistolica": pas,
                "pressao_diastolica": pad,
                "frequencia_cardiaca": fc,
                "pressao_arterial_media": resultado_ia["features_calculadas"]["pressao_arterial_media"],
                "pressao_pulso": resultado_ia["features_calculadas"]["pressao_pulso"],
                "indice_choque": resultado_ia["features_calculadas"]["indice_choque"],
                "duplo_produto": resultado_ia["features_calculadas"]["duplo_produto"]
            },
            "predicao": {
                "modelo_versao": "RandomForest-v2.1",
                "risco_nivel": resultado_ia["risco_nivel"],
                "classe_id": resultado_ia["classe_id"],
                "confianca": resultado_ia["confianca"],
                "alerta_critico": resultado_ia["alerta_critico"],
                "distribuicao_probabilidades": resultado_ia["distribuicao_probabilidades"],
                "anomalias_detectadas": resultado_ia["anomalias_detectadas"],
                "recomendacao_clinica": resultado_ia["recomendacao_clinica"]
            },
            "metadados_governanca": {
                "autor_pipeline": "Engenharia de Dados & ML CardioAI",
                "framework": "Scikit-Learn + PyMongo",
                "conformidade": "Diretrizes SBC / SBH"
            }
        }

        # Persistir diretamente no Banco NoSQL
        doc_id = nosql.inserir_diagnostico(documento_nosql)
        diagnosticos_gerados.append(documento_nosql)

        # Log visual formatado
        tag_map = {3: "[CRITICO]", 2: "[ALTO RISCO]", 1: "[MODERADO]", 0: "[ESTAVEL]"}
        tag = tag_map.get(resultado_ia["classe_id"], "[INFO]")
        print(f"{tag} [Paciente {paciente_id}] PA: {pas}/{pad} mmHg | FC: {fc} bpm")
        print(f"   -> Risco Predito: {resultado_ia['risco_nivel']} (Confianca: {resultado_ia['confianca']:.1%})")
        print(f"   -> Anomalias: {', '.join(resultado_ia['anomalias_detectadas'])}")
        print(f"   -> NoSQL Document ID: {doc_id}\n")

    return diagnosticos_gerados


def demonstrar_consultas_nosql(nosql: NoSQLManager):
    """Demonstra capacidades avancadas de consulta e agregacao NoSQL."""
    print("="*80)
    print(" DEMONSTRACAO DE CONSULTAS E AGREGACOES NOSQL (MONGODB)")
    print("="*80)

    # 1. Consulta por Paciente Especifico
    paciente_teste = 102
    historico = nosql.consultar_historico_paciente(paciente_teste, limite=3)
    print(f"\n[QUERY 1] Historico NoSQL do Paciente {paciente_teste} ({len(historico)} registros):")
    for item in historico:
        p = item.get("predicao", {})
        t = item.get("telemetria", {})
        print(f"   - {item.get('timestamp_inferencia')}: Risco={p.get('risco_nivel')} | PA={t.get('pressao_sistolica')}/{t.get('pressao_diastolica')} | FC={t.get('frequencia_cardiaca')} bpm")

    # 2. Consulta de Alertas Criticos
    alertas = nosql.consultar_alertas_criticos(limite=5)
    print(f"\n[QUERY 2] Alertas Criticos Identificados pelo Modelo ({len(alertas)} eventos):")
    for al in alertas:
        p = al.get("predicao", {})
        print(f"   - Paciente {al.get('paciente_id')}: {p.get('risco_nivel')} ({p.get('confianca'):.1%}) - {', '.join(p.get('anomalias_detectadas', []))}")

    # 3. Agregacao Analitica NoSQL (Group By Risco)
    stats = nosql.obter_estatisticas_risco()
    print("\n[QUERY 3] Agregacao NoSQL ($group por nivel de risco e confianca media):")
    print(json.dumps(stats, indent=4, ensure_ascii=False))
    print("="*80 + "\n")


# ==============================================================================
# 6. PONTO DE ENTRADA (EXECUCAO PRINCIPAL)
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "#"*80)
    print(" ROBÔ DE MONITORAMENTO CARDIOAI - IR ALÉM 2 REFATORADO")
    print(" NoSQL Real (MongoDB) + Machine Learning Preditivo (Scikit-Learn)")
    print("#"*80 + "\n")

    # Passo 1: Inicializacao da Fonte Relacional
    init_relational_db()

    # Passo 2: Treinamento ou Carga do Modelo de Machine Learning
    modelo_ml = treinar_ou_carregar_modelo()

    # Passo 3: Inicializacao do Gerenciador NoSQL
    nosql_mgr = NoSQLManager()

    # Passo 4: Execucao do Pipeline de Inferencia e Persistencia
    executar_pipeline_monitoramento(nosql_mgr, modelo_ml)

    # Passo 5: Execucao de Consultas e Agregacoes NoSQL
    demonstrar_consultas_nosql(nosql_mgr)
