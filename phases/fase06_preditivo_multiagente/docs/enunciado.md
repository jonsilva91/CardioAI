# ENUNCIADO — FASE 6: Coração Sob Controle (FIAP / CardioIA)

> Texto original da atividade, copiado do Portal do Aluno. Fonte de verdade para geração da base, protocolos e requisitos.

## Contribuições da atividade para o desenvolvimento do projeto

Estamos chegando na reta final da evolução da CardioIA, e após consolidarmos a etapa de interação conversacional, a Fase 6 marca uma mudança estratégica no projeto: passamos da comunicação inteligente para a inteligência preditiva orientada a risco.

Nesta etapa, o sistema deixa de atuar apenas de forma reativa e passa a operar de maneira analítica, identificando padrões em dados clínicos simulados e transformando essas informações em suporte estruturado à decisão.

A proposta desta fase é explorar como modelos de Machine Learning podem ser integrados a arquiteturas baseadas em agentes especializados, permitindo que diferentes componentes do sistema colaborem entre si para interpretar cenários e organizar respostas estratégicas. Mais do que prever um evento isolado, buscamos compreender como probabilidades, protocolos e regras operacionais podem ser articulados dentro de uma lógica sistêmica, uma verdadeira orquestração de agentes.

Assim, o desafio consiste em desenvolver um Sistema Preditivo Multiagente para Eventos Cardíacos, utilizando exclusivamente técnicas, arquiteturas e exemplos trabalhados nas disciplinas desta fase ou de fases anteriores, respeitando o material apresentado nas disciplinas.

## Objetivo geral desta atividade

- Treinar um modelo de Machine Learning para prever picos de risco cardíaco, utilizando a base sintética apresentada em aula, aplicando as etapas de preparação de dados, separação entre treino e teste e validação conforme demonstrado nos exemplos nas disciplinas.
- Integrar esse modelo a uma arquitetura multiagente, estruturando o fluxo de chamada do modelo dentro de um agente específico e garantindo que o resultado da predição possa ser compartilhado entre os demais agentes do sistema.
- Utilizar agentes especializados para analisar o risco previsto e cruzar esse resultado com a base de protocolos simulada, organizando as informações de forma lógica e coerente, conforme a arquitetura vista em sala.
- Gerar uma recomendação final estruturada com base na colaboração entre agentes, apresentando de forma clara a probabilidade calculada, a classificação de risco e os protocolos sugeridos, demonstrando o funcionamento completo do pipeline multiagente.
- Trabalho em equipe e colaboração interdisciplinar: desenvolvimento em grupo com divisão equilibrada de tarefas.

Ao final desta fase, a equipe terá desenvolvido uma solução prática que demonstra como agentes conversacionais podem ser aplicados em contextos de saúde digital, respeitando boas práticas técnicas e conceituais.

---

## Atividade detalhada: Obrigatório

### PARTE 1 – MODELO PREDITIVO DE PICO DE RISCO

Para viabilizar o desenvolvimento sem restrições de privacidade ou acesso a dados sensíveis, serão fornecidos a seguir os códigos para geração de bases de dados sintéticas realistas:

Base de dados de treinamento de modelo preditivo para predição de risco do paciente (`risk_score`):

```python
import numpy as np
import pandas as pd

np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "idade_media": np.random.normal(55, 12, n).clip(18, 90),
    "carga_sistema": np.random.uniform(30, 100, n),
    "tempo_espera": np.random.normal(45, 20, n).clip(5, 180),
    "fc_media": np.random.normal(85, 15, n).clip(50, 150),
    "spo2_media": np.random.normal(95, 3, n).clip(70, 100),
    "pa_sistolica": np.random.normal(125, 20, n).clip(80, 200),
    "temperatura": np.random.normal(24, 5, n).clip(10, 40),
    "densidade_eventos": np.random.poisson(3, n),
    "eventos_24h": np.random.poisson(2, n),
    "disponibilidade_recursos": np.random.uniform(20, 100, n)
})

risk_score = (
    (df["carga_sistema"] > 80).astype(int) +
    (df["tempo_espera"] > 60).astype(int) +
    (df["spo2_media"] < 92).astype(int) +
    (df["fc_media"] > 110).astype(int) +
    (df["eventos_24h"] > 4).astype(int) +
    (df["disponibilidade_recursos"] < 40).astype(int)
)

df["pico_risco"] = (risk_score >= 2).astype(int)
```

Base de conhecimento contendo protocolos médicos:

```python
protocolos = [
    "Se SPO2 < 88% → iniciar suporte respiratório imediato",
    "Se carga do sistema > 85% → abrir unidades temporárias",
    "Se FC > 120 → iniciar monitoramento intensivo",
    "Se eventos_24h > 5 → ativar equipe de resposta rápida",
    "Se disponibilidade_recursos < 30% → redistribuir insumos",
    "Se tempo_espera > 90 min → priorizar triagem emergencial",
    "Se temperatura > 38°C média → iniciar protocolo infeccioso",
    "Se densidade_eventos > 6 → ativar plano de contingência",
    "Se PA sistólica < 90 → iniciar protocolo de choque",
    "Se risco sistêmico alto → ativar estado de emergência"
]
```

Essas bases simuladas deverão ser utilizadas para:
1. Treinamento do modelo preditivo;
2. Validação do Sistema (métricas de assertividade);
3. Integração com o pipeline Multiagente: com base nos dados de um novo paciente, o sistema deverá chamar o agente de ML que dará um score de risco para o paciente usando o modelo de ML. Em seguida, com esse resultado e os protocolos, um segundo agente deverá dar a resposta final.

Para testar o seu sistema, simule dados de um novo paciente, como o exemplo a seguir:

```python
novo_caso = pd.DataFrame([{
    "idade_media": 62,
    "carga_sistema": 92,
    "tempo_espera": 75,
    "fc_media": 118,
    "spo2_media": 89,
    "pa_sistolica": 100,
    "temperatura": 37.5,
    "densidade_eventos": 7,
    "eventos_24h": 5,
    "disponibilidade recursos": 25
}])
```

> NOTA DA EQUIPE: no enunciado original a chave acima está escrita "disponibilidade recursos" (com espaço). No código usamos "disponibilidade_recursos" (com underscore), igual ao nome da coluna na base de treino.

A resposta do seu sistema deverá ser o risco previsto bem como os protocolos a serem seguidos, conforme o seguinte exemplo:

```
RISCO PREVISTO: 0.91

PROTOCOLOS SUGERIDOS:

- Se carga do sistema > 85% → abrir unidades temporárias

- Se SPO2 < 88% → iniciar suporte respiratório imediato

- Se disponibilidade_recursos < 30% → redistribuir insumos
```

Diretrizes técnicas da entrega:
- **Base de dados:** gerar ou utilizar a base de dados simulada para o treinamento.
- **Treinamento:** treinar um modelo supervisionado de classificação para prever a variável `pico_risco`.
- **Avaliação:** avaliar o desempenho com métricas vistas em aula (acurácia e matriz de confusão).
- **Modelo salvo:** salvar o modelo treinado para a posterior integração no sistema multiagente.

---

### PARTE 2 – SISTEMA MULTIAGENTE (OPENAI AGENTS SDK)

Nesta parte, o grupo deve construir o sistema multiagente que usa o modelo treinado.

Diretrizes técnicas:
- **Agentes especializados:** implementar, no mínimo, um Agente Analista de Risco (consulta o modelo preditivo e gera o score), um Agente Especialista em Protocolos (consulta a base de protocolos simulados), um Agente Planejador de Resposta (consolida as informações e sugere ações operacionais) e um Agente Orquestrador (coordena o fluxo entre os agentes com handoffs).
- **Fluxo do sistema:** receber os dados de um novo paciente, acionar o agente de risco, encaminhar o resultado ao agente de protocolos e gerar uma resposta final estruturada com a probabilidade prevista, a classificação de risco e os protocolos sugeridos.
- **Recursos:** usar handoffs entre agentes, tools, histórico de mensagens e validação de saída.
