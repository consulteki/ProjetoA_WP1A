# SPEC-003 — Análise Exploratória (EDA)

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §7.2 |
| Skill correspondente | `.agents/skills/exploratory-analysis/SKILL.md` |
| Etapa do pipeline | Etapa 2 |
| Entrega | A2 |

Em caso de conflito, prevalece `SPEC-000-master.md`.

## 1. Objetivo

Caracterizar estatística e visualmente o dataset canônico, orientando decisões de pré-processamento subsequentes, sem influenciar hiperparâmetros de modelo nem tocar o conjunto de teste para fins de decisão.

## 2. Escopo

Cobre estatísticas descritivas, distribuição de classes, variabilidade, correlações, PCA e comparação normal/falha. Não decide pipeline de pré-processamento (ver SPEC-005) nem treina modelos.

## 3. Requisitos

A análise DEVE incluir, individualmente identificáveis:

1. Estatísticas descritivas por variável (global e por classe).
2. Distribuição das 21 classes (amostras e execuções por classe).
3. Variabilidade das variáveis (variância, coeficiente de variação).
4. Matriz de correlação entre variáveis.
5. Projeção por PCA (ou técnica equivalente).
6. Comparação de comportamento entre regime normal e regimes de falha.

Qualquer inspeção do conjunto de teste nesta etapa é estritamente descritiva — nenhuma conclusão aqui determina hiperparâmetros (ver `ADR-002-test-set-isolation.md`).

## 4. Entradas e saídas

- **Entrada:** dataset canônico (SPEC-002).
- **Saída:** Entrega A2 (notebook/figuras) em `notebooks/02_eda.ipynb` e `results/figures/`.

## 5. Critérios de aceite

- Os 6 elementos do procedimento estão presentes e individualmente identificáveis em A2.
- Nenhuma decisão de modelagem foi tomada com base nesta análise.

## 6. Rastreabilidade

WP1A §9.2 → `requirements.md` RP-02 → `SPEC-000-master.md` §7.2 → esta SPEC → `.agents/skills/exploratory-analysis/SKILL.md`.
