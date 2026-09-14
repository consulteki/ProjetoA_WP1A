# A2 — Observações da análise exploratória

- Dataset: `tep-canonical-v1`
- Gerado em: `2026-09-14T00:54:53+00:00`

## Disclaimer de protocolo

Esta EDA é estritamente descritiva. Nenhuma interpretação abaixo modifica o protocolo experimental (unidade = run, isolamento do teste, os 6 modelos obrigatórios, o conjunto de métricas, nem a ordem do pipeline). Sugestões de pré-processamento, se houver, são hipóteses a avaliar em SPEC-005 e não decisões congeladas nesta etapa.

## Achados descritivos (não prescritivos)

### Distribuição de classes

- Total: 30260 amostras em 42 execuções (`run_id`), 21 classes.
- Amplitude de amostras/classe: 1440–1460.
- Classes com mais amostras: 0 (1460), 11 (1440), 19 (1440).
- Desbalanceamento existe e deve ser considerado nas **métricas** já exigidas pelo protocolo (F1 macro, balanced accuracy, MCC) — sem alterar o conjunto de modelos ou a unidade experimental.

### Variabilidade

- Variáveis com variância ~0: nenhuma.
- Maiores |CV| (escalas heterogêneas entre variáveis): xmv_3=0.662, xmeas_37=0.564, xmeas_1=0.55, xmv_11=0.525, xmv_9=0.341.
- Escalas distintas entre variáveis são um **indício** a ser tratado, se necessário, apenas em SPEC-005 (padronização ajustada no treino), não uma mudança de protocolo nesta etapa.

### Correlações

- Pares com maior |r| de Pearson:
  - `xmeas_15` × `xmv_8`: r=1.000
  - `xmeas_12` × `xmv_7`: r=1.000
  - `xmeas_7` × `xmeas_13`: r=0.998
  - `xmeas_25` × `xmeas_31`: r=0.985
  - `xmeas_23` × `xmeas_29`: r=0.985
- Correlações altas são descritivas da redundância linear; não autorizam seleção de features com base em teste nem alteração dos 6 modelos obrigatórios.

### PCA

- Variância explicada por PC1–PC2: 28.4% + 21.3% (acumulado PC1–PC2 = 49.8%).
- A projeção é inspeção visual de separabilidade; sobreposições entre classes, se existirem, serão avaliadas quantitativamente em SPEC-007 (QP3), não resolvidas aqui por mudança de protocolo.

### Normal vs falha

- Variáveis com maior |diferença padronizada de média| (falha agregada vs normal):
  - `xmeas_16`: SMD=3.620
  - `xmeas_7`: SMD=3.139
  - `xmeas_13`: SMD=2.910
  - `xmv_10`: SMD=2.697
  - `xmv_4`: SMD=2.210

## O que esta etapa explicitamente NÃO faz

- Não escolhe hiperparâmetros.
- Não define o manifesto de divisão (SPEC-004).
- Não congela o pipeline de pré-processamento (SPEC-005).
- Não remove classes, variáveis ou modelos do benchmark.
- Não consulta um holdout de teste WP1A (ainda inexistente nesta etapa).
