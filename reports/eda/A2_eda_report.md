# Entrega A2 — Análise Exploratória (TEP)

- Gerado em: `2026-09-14T00:54:53+00:00`
- Dataset canônico: `tep-canonical-v1`
- Spec: SPEC-003 / skill `exploratory-analysis`

## Disclaimer

Esta EDA é estritamente descritiva. Nenhuma interpretação abaixo modifica o protocolo experimental (unidade = run, isolamento do teste, os 6 modelos obrigatórios, o conjunto de métricas, nem a ordem do pipeline). Sugestões de pré-processamento, se houver, são hipóteses a avaliar em SPEC-005 e não decisões congeladas nesta etapa.

## Elementos obrigatórios (RP-02)

### 1. Estatísticas descritivas

- Global: `/home/alanancy/metodosEsimulacao/results/tables/A2_descriptive_global.csv`
- Por classe: `/home/alanancy/metodosEsimulacao/results/tables/A2_descriptive_by_class.csv`
- Cobertura: 52 variáveis × 21 classes.

### 2. Distribuição das 21 classes

- Tabela: `/home/alanancy/metodosEsimulacao/results/tables/A2_class_distribution.csv`
- Figuras: `/home/alanancy/metodosEsimulacao/results/figures/A2_class_distribution_samples.png`, `/home/alanancy/metodosEsimulacao/results/figures/A2_class_distribution_runs.png`
- Amostras totais: 30260; runs totais: 42.

### 3. Variabilidade das variáveis

- Tabela: `/home/alanancy/metodosEsimulacao/results/tables/A2_variability.csv`
- Figura: `/home/alanancy/metodosEsimulacao/results/figures/A2_variable_variability.png`

### 4. Matriz de correlação

- Tabela completa: `/home/alanancy/metodosEsimulacao/results/tables/A2_correlation.csv`
- Top pares: `/home/alanancy/metodosEsimulacao/results/tables/A2_correlation_top_pairs.csv`
- Figura: `/home/alanancy/metodosEsimulacao/results/figures/A2_correlation_heatmap.png`

### 5. Projeção PCA

- Variância: `/home/alanancy/metodosEsimulacao/results/tables/A2_pca_variance.csv`
- Projeção: `/home/alanancy/metodosEsimulacao/results/tables/A2_pca_projection.csv.gz`
- Figuras: `/home/alanancy/metodosEsimulacao/results/figures/A2_pca_normal_vs_fault.png`, `/home/alanancy/metodosEsimulacao/results/figures/A2_pca_by_class.png`, `/home/alanancy/metodosEsimulacao/results/figures/A2_pca_explained_variance.png`

### 6. Comparação normal vs falha

- Tabela: `/home/alanancy/metodosEsimulacao/results/tables/A2_normal_vs_fault.csv`
- Figura: `/home/alanancy/metodosEsimulacao/results/figures/A2_normal_vs_fault_mean_shift.png`

## Rastreabilidade

- Entrada exclusiva: dataset canônico registrado (SPEC-002).
- Figuras geradas programaticamente por `wp1a.eda.figures`.
- Observações qualitativas: `reports/eda/A2_observations.md` (não alteram o protocolo).
