# Relatório Curto — Fase 4 CNN aplicada a ECG

## Objetivo

Avaliar a viabilidade de uma CNN simples para classificação de imagens de ECG em contexto acadêmico.

## Base escolhida

Preencher após definição da base:

- PTB-XL
- ECG Images derivadas do MIT-BIH
- outra base documentada

## Estratégia experimental

- carregamento de imagens por classe
- divisão treino/validação
- CNN 2D simples
- avaliação com matriz de confusão
- métricas: accuracy, precision, recall e F1-score

## Resultados esperados

Preencher após execução:

- accuracy:
- precision:
- recall:
- F1-score:

## Matriz de confusão

Salvar figura em:

```text
phases/fase04_cnn_ecg/outputs/figures/confusion_matrix.png
```

## Discussão crítica

Pontos obrigatórios para discussão:

- risco de overfitting com poucas imagens
- limitação clínica de bases públicas
- ausência de validação médica real
- necessidade de interpretabilidade e uso responsável de IA em saúde
- impossibilidade de uso diagnóstico real sem validação robusta

## Próximos passos

- testar aumento de dados
- comparar arquiteturas simples e mais profundas
- revisar balanceamento entre classes
- documentar limitações e vieses da base
