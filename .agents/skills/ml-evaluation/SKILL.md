---
name: ml-evaluation
description: Calcula o conjunto completo de métricas globais, por classe e de custo computacional para os seis modelos treinados (Etapa 6 do pipeline WP1A).
---

# Skill: ml-evaluation

**Fontes normativas:** `docs/adr/ADR-007-multi-criteria-model-evaluation.md`; `docs/specs/SPEC-000-master.md` §7.6, §9, §12 (INV-06, INV-07); `docs/project/requirements.md` RP-10..13, Seção 5; `AGENTS.md` MET-R06.

## Purpose

Calcular, para cada um dos seis modelos treinados, o conjunto completo de métricas obrigatórias (globais, por classe e de custo computacional) definidas na SPEC-000, produzindo os artefatos que fundamentam as respostas às questões de pesquisa QP1–QP5 e a avaliação das hipóteses H1–H4 — sem jamais reduzir a comparação a uma métrica única.

## Preconditions

- A skill `ml-training` foi executada para os seis modelos, com predições em teste geradas exatamente uma vez por modelo, após congelamento de configuração.
- Os artefatos de tempo de treinamento, tempo de inferência e tamanho de modelo estão disponíveis para todos os seis modelos.

## Inputs

- Predições em teste por modelo (via `ml-training`).
- Rótulos verdadeiros do conjunto de teste (via `grouped-split`/`preprocessing`).
- Tempos de treinamento/inferência e tamanho de modelo por modelo (via `ml-training`).

## Procedure

1. Para cada modelo, calcular a matriz de confusão (21×21) sobre o conjunto de teste.
2. A partir da matriz de confusão, calcular precisão, revocação e F1 por classe (21 classes).
3. Calcular F1 macro como a média aritmética simples dos F1 por classe: $F1_{macro} = \frac{1}{C}\sum_{c=1}^{C} F1_c$.
4. Calcular acurácia balanceada como $BA = \frac{1}{C}\sum_{c=1}^{C} \frac{TP_c}{TP_c + FN_c}$.
5. Calcular acurácia simples, precisão macro, revocação macro, F1 ponderada e MCC multiclasse.
6. Consolidar tempo de treinamento, tempo de inferência e tamanho do modelo salvo (e consumo de memória, quando disponível) para cada modelo.
7. Consolidar todas as métricas em uma tabela comparativa única, cobrindo os seis modelos lado a lado.
8. Identificar, a partir das matrizes de confusão e do F1 por classe, as classes de falha sistematicamente mais confundidas entre modelos (insumo para QP3).
9. Verificar numericamente que os valores de F1 macro e acurácia balanceada reportados são reprodutíveis a partir dos valores por classe/matriz de confusão (recômputo independente).
10. Não emitir nenhuma conclusão de "melhor modelo" nesta etapa baseada em uma única métrica — a síntese multicritério cabe à skill `scientific-writing`, a partir dos artefatos aqui produzidos.

## Outputs

- **Entrega A5** — Resultados completos (CSV/JSON): métricas globais, por classe, matrizes de confusão, custo computacional.
- Tabela comparativa de métricas globais (insumo 3 dos insumos do artigo).
- Tabela de métricas por classe (insumo 4).
- Matrizes de confusão (insumo 5).
- Análise preliminar das falhas mais confundidas (insumo 8), para consumo por `scientific-writing` e `scientific-figures`.

## Validation

- Todas as métricas MET-01 a MET-12 (SPEC-000 §9.3) estão presentes para os seis modelos.
- F1 macro e acurácia balanceada recomputados a partir dos dados por classe conferem com os valores reportados (verificação numérica).
- Nenhum arquivo de resultado agrega métricas sem manter também os dados por classe/matriz de confusão que as sustentam (rastreabilidade — DOC-R03).

## Failure Conditions

- Cálculo de F1 macro ou acurácia balanceada por método diferente do definido na SPEC-000 §9.2 (ex.: usar F1 ponderada no lugar de F1 macro sem distinção clara).
- Ausência de qualquer uma das métricas obrigatórias (MET-01 a MET-12) para qualquer um dos seis modelos.
- Publicação de métricas agregadas sem os arquivos de resultado bruto (matriz de confusão, métricas por classe) que as sustentam.
- Conclusão de "melhor modelo" emitida nesta skill com base em métrica única, antecipando indevidamente a síntese que cabe a `scientific-writing`.

## Definition of Done

- Entrega A5 completa e versionada para os seis modelos.
- Critério de aceite CA-05 e CA-06 (SPEC-000 §13) satisfeitos.
- Artefatos prontos para consumo por `statistical-analysis` (comparação formal entre modelos) e `scientific-figures` (visualizações).
