# SPEC-007 — Avaliação Final

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §7.6, §9; `docs/adr/ADR-007-multi-criteria-model-evaluation.md` |
| Skill correspondente | `.agents/skills/ml-evaluation/SKILL.md` |
| Etapa do pipeline | Etapa 6 |
| Entrega | A5 |
| Guardas executáveis | `src/wp1a/data/class_consistency.py`, `src/wp1a/evaluation/verify.py` |
| Implementação | `src/wp1a/evaluation/` (`cli`, `pipeline`, `metrics`, `confused_classes`) |
| Testes de rejeição | `tests/unit/test_class_consistency.py`, `tests/unit/test_schema_validation.py`, `tests/unit/test_evaluation_a5.py` |

Em caso de conflito, prevalece `SPEC-000-master.md` e `ADR-007-multi-criteria-model-evaluation.md`.

## 1. Objetivo

Calcular o conjunto completo de métricas globais, por classe e de custo computacional para os 6 modelos treinados, sem jamais reduzir a comparação a uma métrica única.

## 2. Escopo

Cobre o cálculo e a consolidação de métricas. Não cobre testes estatísticos formais entre modelos (ver SPEC-008).

## 3. Requisitos

1. Matriz de confusão (21×21) por modelo.
2. Precisão, revocação e F1 por classe.
3. F1 macro: $F1_{macro} = \frac{1}{C}\sum_{c=1}^{C} F1_c$.
4. Acurácia balanceada: $BA = \frac{1}{C}\sum_{c=1}^{C} \frac{TP_c}{TP_c+FN_c}$.
5. Acurácia, precisão macro, revocação macro, F1 ponderada, MCC multiclasse.
6. Tempo de treinamento, tempo de inferência, tamanho do modelo (e memória, quando disponível).
7. Recômputo numérico de F1 macro/BA a partir dos dados por classe, para verificação.
8. Identificação das classes de falha sistematicamente mais confundidas (insumo para QP3).
9. Nenhuma conclusão de "melhor modelo" nesta etapa baseada em métrica única (INV-06/INV-07).
10. Todo rótulo de classe avaliado deve ter aparecido no treino — verificado por `validate_train_covers_eval_classes`.

## 4. Entradas e saídas

- **Entrada:** predições de teste e artefatos de custo (SPEC-006, A4).
- **Saída:** Entrega A5 — métricas completas (CSV/JSON) em `results/metrics/`, matrizes de confusão em `results/tables/`.

## 5. Critérios de aceite

- CA-05, CA-06 (SPEC-000): todas as métricas presentes para os 6 modelos; F1 macro/BA recomputados conferem.
- `tests/unit/test_class_consistency.py` e `test_schema_validation.py` passam contra os dados de entrada desta etapa.

## 6. Rastreabilidade

`ADR-007-multi-criteria-model-evaluation.md` → `SPEC-000-master.md` §7.6, §9, INV-06/INV-07 → esta SPEC → `.agents/skills/ml-evaluation/SKILL.md` → `src/wp1a/evaluation/`.
