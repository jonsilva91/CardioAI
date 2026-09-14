# IR ALÉM 2 - Automação RPA e Persistência Híbrida de Dados

**CardioAI - Fase 5**
**Autor:** Jonas Luis da Silva (simulado)

## 1. Objetivo

Este documento descreve a implementação de um Robô de Automação de Processos (RPA) projetado para monitorar dados simulados de sensores IoT (como pressão arterial e frequência cardíaca) de pacientes. O sistema utiliza uma arquitetura híbrida de banco de dados para separar dados estruturados (telemetria) de dados semi-estruturados (logs de auditoria e rastreabilidade).

## 2. Arquitetura de Dados Híbrida

O projeto utiliza dois repositórios de dados com propósitos distintos:

1. **Banco Relacional (SQLite - `pacientes.db`):** 
   * **Uso:** Armazenamento tabular de séries temporais geradas por sensores (pressão sistólica/diastólica, frequência cardíaca).
   * **Justificativa:** A linguagem SQL é ideal para filtragens rápidas, agregações (como médias de FC) e janelamento (ex: buscar as últimas 10 leituras).
2. **Banco Não-Relacional (JSON Estruturado - `logs_alertas.json`):**
   * **Uso:** Funciona como um repositório NoSQL leve (estilo MongoDB/TinyDB) para persistir o histórico de anomalias detectadas.
   * **Justificativa:** Os alertas gerados contêm estruturas variáveis (listas de anomalias, metadados heterogêneos), tornando esquemas flexíveis (document-oriented) muito superiores às tabelas rígidas do modelo relacional para fins de auditoria e rastreabilidade (log).

## 3. Lógica do Robô (RPA)

O script `robo_monitoramento.py` atua como o motor RPA:
1. **Extração:** Lê as amostras mais recentes no `pacientes.db`.
2. **Avaliação (Regras):** Aplica *thresholds* clínicos simulados:
   * Pressão Sistólica >= 160 ou Diastólica >= 100 → Crise Hipertensiva
   * Frequência Cardíaca >= 100 → Taquicardia
   * Frequência Cardíaca <= 50 → Bradicardia
3. **Persistência de Rastreabilidade:** Se uma anomalia for identificada, o robô empacota todos os dados (motivo, valor bruto da leitura original, timestamp) e salva no arquivo `logs_alertas.json`.

## 4. Rastreabilidade e Governança

Ao empacotar os `dados_brutos` da anomalia no JSON de auditoria, o sistema atinge nível máximo de rastreabilidade (Data Lineage). Qualquer alerta gerado pode ser reproduzido e justificado, atendendo a normativas éticas essenciais em sistemas autônomos na saúde. Se o RPA gera um alarme para "Taquicardia", o log contém exatamente qual foi a FC naquele milissegundo de leitura.
