# Fase 2 — IA Simbólica e Classificação Textual

Esta fase concentra os artefatos de IA simbólica e classificação textual do CardioAI.

## Conteúdo da fase

- `diagnostico_ontologia.py`: script para leitura de frases e sugestão de diagnóstico com base em mapa de conhecimento
- `classificacao_risco.ipynb`: notebook de classificação textual de risco
- dados e saídas compartilhadas na raiz do projeto:
  - `../../data/`
  - `../../docs/`
  - `../../referencias.md`

## Objetivos

- mapear sintomas para doenças cardiovasculares
- classificar frases médicas em níveis de risco
- demonstrar abordagem explicável e acadêmica com Python e Scikit-learn

## Como executar o script simbólico

Na raiz do repositório:

```bash
python phases/fase02_ia_simbolica_classificacao/diagnostico_ontologia.py
```

## Como abrir o notebook

```bash
jupyter notebook phases/fase02_ia_simbolica_classificacao/classificacao_risco.ipynb
```

## Dependências sugeridas

```bash
pip install pandas scikit-learn jupyter
```

## Observações

- O script utiliza caminhos relativos à raiz do repositório.
- Caso o arquivo `mapa_conhecimento.csv` ainda não esteja presente, ele deve ser colocado em `data/samples/` ou outro local documentado e o caminho deve ser mantido consistente.
- Os resultados gerados podem ser salvos em `data/processed/`.
