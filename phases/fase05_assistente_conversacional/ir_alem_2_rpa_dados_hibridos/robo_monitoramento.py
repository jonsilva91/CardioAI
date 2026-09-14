import os
import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path

# Configuração de caminhos
BASE_DIR = Path(__file__).resolve().parent
DB_RELACIONAL_PATH = BASE_DIR / "pacientes.db"
DB_NAO_RELACIONAL_PATH = BASE_DIR / "logs_alertas.json" # Usado como banco NoSQL simples (TinyDB like)

def init_dbs():
    """Inicializa os bancos de dados simulados para o RPA."""
    
    # 1. Banco Relacional (SQLite) - Dados Estruturados de Sensores/IoT
    conn = sqlite3.connect(DB_RELACIONAL_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leituras_sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            pressao_sistolica INTEGER,
            pressao_diastolica INTEGER,
            frequencia_cardiaca INTEGER,
            timestamp TEXT
        )
    ''')
    
    # Inserir alguns dados simulados se estiver vazio
    cursor.execute('SELECT COUNT(*) FROM leituras_sensores')
    if cursor.fetchone()[0] == 0:
        dados_iniciais = [
            (101, 120, 80, 75, datetime.now().isoformat()),
            (102, 180, 110, 120, datetime.now().isoformat()), # Anomalia crítica (Crise hipertensiva + Taquicardia)
            (103, 110, 70, 60, datetime.now().isoformat()),
            (104, 130, 85, 115, datetime.now().isoformat()) # Anomalia leve (Taquicardia)
        ]
        cursor.executemany('''
            INSERT INTO leituras_sensores (paciente_id, pressao_sistolica, pressao_diastolica, frequencia_cardiaca, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', dados_iniciais)
        conn.commit()
    conn.close()

    # 2. Banco Não-Relacional (JSON estruturado) - Logs e Metadados não estruturados
    if not DB_NAO_RELACIONAL_PATH.exists():
        with open(DB_NAO_RELACIONAL_PATH, 'w', encoding='utf-8') as f:
            json.dump({"alertas": []}, f)


def detectar_anomalias():
    """Lê do banco relacional e aplica regras para detectar anomalias."""
    print(f"[{datetime.now().isoformat()}] RPA Monitoramento Iniciado...")
    conn = sqlite3.connect(DB_RELACIONAL_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM leituras_sensores ORDER BY timestamp DESC LIMIT 10')
    registros = cursor.fetchall()
    conn.close()
    
    alertas_gerados = []
    
    for reg in registros:
        id_leitura, paciente_id, sistolica, diastolica, fc, timestamp = reg
        
        anomalias = []
        if sistolica >= 160 or diastolica >= 100:
            anomalias.append("Crise Hipertensiva")
        if fc >= 100:
            anomalias.append("Taquicardia")
        if fc <= 50:
            anomalias.append("Bradicardia")
            
        if anomalias:
            alerta = {
                "id_alerta": f"ALT-{int(time.time())}-{paciente_id}",
                "timestamp_deteccao": datetime.now().isoformat(),
                "paciente_id": paciente_id,
                "motivos": anomalias,
                "dados_brutos": {
                    "pressao": f"{sistolica}/{diastolica}",
                    "fc": fc,
                    "timestamp_leitura": timestamp
                },
                "status": "NOVO",
                "metadados": {
                    "fonte_dados": "SQLite (Sensor IoT Simulado)",
                    "motor_regras": "RPA v1.0"
                }
            }
            alertas_gerados.append(alerta)
            print(f"⚠️ Anomalia detectada para Paciente {paciente_id}: {', '.join(anomalias)}")
            
    return alertas_gerados


def persistir_alertas(alertas_novos):
    """Salva os alertas no banco não-relacional (rastreabilidade)."""
    if not alertas_novos:
        print("Nenhuma anomalia nova detectada no ciclo.")
        return
        
    with open(DB_NAO_RELACIONAL_PATH, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        
    dados["alertas"].extend(alertas_novos)
    
    with open(DB_NAO_RELACIONAL_PATH, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
        
    print(f"💾 {len(alertas_novos)} novos alertas salvos no banco não-relacional de logs.")


def job():
    """Função principal do loop do RPA."""
    init_dbs()
    alertas = detectar_anomalias()
    persistir_alertas(alertas)
    print("Ciclo de monitoramento finalizado.\n" + "-"*40)


if __name__ == "__main__":
    print("🤖 Iniciando Robô de Monitoramento CardioAI (IR ALÉM 2)")
    # Simulação de loop agendado. Executa 3 ciclos para demonstração.
    for _ in range(3):
        job()
        time.sleep(2) # Em produção, seria `schedule.every(5).minutes.do(job)`
