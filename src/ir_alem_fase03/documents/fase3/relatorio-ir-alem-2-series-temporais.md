# Relatório — IR ALÉM 2: Inteligência Artificial em séries temporais de saúde

## 1. Objetivo

O objetivo deste módulo é aplicar técnicas de Inteligência Artificial para análise de séries temporais de sinais vitais, com foco em batimentos cardíacos. A proposta é comparar uma abordagem tradicional, baseada em Regressão Logística, com uma abordagem neuromórfica simples inspirada no modelo LIF, ou seja, neurônios do tipo Leaky Integrate-and-Fire.

A comparação é importante porque sistemas de saúde digital e dispositivos vestíveis frequentemente precisam processar dados temporais com baixo consumo computacional. Portanto, além de avaliar desempenho, também é relevante discutir interpretabilidade, simplicidade, custo e possibilidade de uso em Edge Computing.

## 2. Dataset sintético

Como esta fase tem caráter de prova de conceito, foi criado um dataset sintético de séries temporais de BPM. Cada amostra representa uma janela de 60 leituras de batimentos cardíacos. Foram simuladas três classes:

- `NORMAL`: frequência cardíaca em faixa regular.
- `TAQUICARDIA`: batimentos elevados e sustentados.
- `IRREGULAR`: série com variações abruptas e picos.

A vantagem do dataset sintético é permitir controle sobre os padrões de cada classe e facilitar a reprodução do experimento. Em uma evolução do projeto, a mesma estrutura poderia ser aplicada a bases reais de ECG, PPG ou dados coletados por sensores vestíveis.

## 3. Método tradicional: Regressão Logística

No classificador tradicional, cada janela temporal foi convertida em features estatísticas, como:

- média;
- desvio padrão;
- mínimo;
- máximo;
- mediana;
- quartis;
- amplitude;
- inclinação da série.

Essas features foram usadas para treinar uma Regressão Logística. A principal vantagem dessa abordagem é a simplicidade. O modelo é leve, rápido de treinar, fácil de explicar e adequado para uma primeira versão de triagem em saúde digital. A limitação é que parte da dinâmica temporal do sinal pode se perder quando a janela é resumida em estatísticas agregadas.

## 4. Método neuromórfico simples: LIF

O segundo método utiliza uma codificação inspirada em neurônios LIF. Nesse modelo, cada série de BPM é interpretada como uma corrente de entrada. A tensão simulada do neurônio acumula ao longo do tempo, sofre decaimento e dispara um spike quando ultrapassa determinado limiar.

Foram usados neurônios com diferentes limiares. Para cada janela, o sistema extrai informações como:

- quantidade de spikes;
- primeiro spike;
- último spike;
- intervalo médio entre spikes;
- tensão média simulada.

Essas características formam uma representação orientada a eventos. Em seguida, um classificador de leitura é usado para separar as classes. Essa abordagem é chamada aqui de neuromórfica simples porque não implementa um hardware neuromórfico real, mas demonstra o princípio de transformar sinais contínuos em eventos discretos.

## 5. Comparação dos modelos

A Regressão Logística tradicional tende a funcionar muito bem quando as classes são separáveis por estatísticas simples, como média e máximo. Por exemplo, a taquicardia é facilmente identificável quando o BPM médio da janela é alto.

O modelo LIF pode capturar aspectos diferentes da série temporal, como frequência de eventos, intensidade dos picos e momentos de disparo. Isso é interessante para sinais de saúde porque nem sempre o valor médio é suficiente. Em casos de arritmia ou irregularidade, o padrão temporal pode ser tão importante quanto a média.

Por outro lado, o modelo LIF depende de hiperparâmetros como limiar, decaimento e ganho de entrada. Se esses valores forem mal escolhidos, a codificação pode perder informação. Já a Regressão Logística com features estatísticas é mais direta e mais fácil de ajustar.

## 6. Vantagens e limitações

### Regressão Logística

Vantagens:

- simples;
- interpretável;
- rápida;
- fácil de documentar;
- adequada para baseline acadêmico.

Limitações:

- depende de boas features manuais;
- pode perder dinâmica temporal;
- não é naturalmente orientada a eventos.

### Modelo LIF

Vantagens:

- representa séries por eventos discretos;
- aproxima o conceito de computação neuromórfica;
- pode ser interessante para Edge Computing de baixo consumo;
- captura padrões de disparo ao longo do tempo.

Limitações:

- depende de parâmetros sensíveis;
- é mais difícil de explicar que o baseline;
- a versão implementada é didática, não uma rede neuromórfica completa.

## 7. Conclusão

O experimento mostra que a Regressão Logística é uma excelente linha de base para o CardioIA, especialmente por sua simplicidade e interpretabilidade. O modelo LIF, por sua vez, amplia a discussão técnica ao introduzir uma forma de processamento temporal baseada em spikes.

Para uma próxima etapa, recomenda-se utilizar dados reais de séries temporais de saúde, aplicar validação cruzada, medir latência de inferência e avaliar a viabilidade de execução em dispositivos de borda. Dessa forma, o projeto se aproximaria ainda mais de aplicações reais de monitoramento cardíaco contínuo.
