# SPEC-006 — Benchmark de Modelos (Treinamento e Seleção)

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §7.5, §8; `docs/adr/ADR-002`, `ADR-005`, `ADR-006` |
| Skill correspondente | `.agents/skills/ml-training/SKILL.md` |
| Etapa do pipeline | Etapa 5 |
| Entrega | A4 |
| Guardas executáveis | `src/wp1a/tracking/isolation_guard.py` (`ExperimentState`, `assert_test_not_used_for_selection`) |
| Testes de rejeição | `tests/methodology/test_test_set_isolation.py` |

Em caso de conflito, prevalece `SPEC-000-master.md` e as ADRs citadas.

## 1. Objetivo

Treinar os 6 modelos obrigatórios do benchmark sob configurações explícitas e versionadas, selecionando hiperparâmetros exclusivamente a partir de treino/validação, consultando o teste apenas após o congelamento.

## 2. Escopo

Cobre o treinamento e a seleção de hiperparâmetros dos 6 modelos. Não cobre o cálculo de métricas de avaliação (ver SPEC-007).

## 3. Requisitos

1. Exatamente 6 modelos: Regressão Logística, Árvore de Decisão, Random Forest, Gradient Boosting, SVM, XGBoost (`ADR-006-model-family-selection.md`).
2. Todos os 6 modelos usam o mesmo manifesto de divisão (SPEC-004) e o mesmo pipeline de pré-processamento (SPEC-005) — INV-03.
3. Seleção de hiperparâmetros usa apenas treino/validação — verificado por `assert_test_not_used_for_selection`.
4. Configuração congelada antes de qualquer consulta ao teste — controlado por `ExperimentState.freeze()`/`access_test()`.
5. O teste é consultado exatamente uma vez por configuração final; reajuste pós-teste exige novo identificador de experimento.
6. Cada execução referencia uma configuração explícita e versionada em `configs/` (`ADR-005-experiment-configuration.md`).
7. Tempo de treinamento, tempo de inferência e tamanho do modelo são coletados no mesmo ambiente/execução.

## 4. Entradas e saídas

- **Entrada:** conjuntos pré-processados (SPEC-005), configuração de experimento (`configs/experiment.yaml`, `configs/models.yaml`, `configs/seeds.yaml`).
- **Saída:** Entrega A4 — modelos treinados em `models/`, tabela de hiperparâmetros em `results/tables/`, predições de teste em `results/predictions/`.

## 5. Critérios de aceite

- CA-04 (SPEC-000): 6 modelos treinados sob o mesmo protocolo, com hiperparâmetros documentados.
- `tests/methodology/test_test_set_isolation.py` passa integralmente contra a implementação real de treinamento.

## 6. Rastreabilidade

`ADR-002`, `ADR-005`, `ADR-006` → `SPEC-000-master.md` §7.5, §8, INV-03/INV-05 → esta SPEC → `.agents/skills/ml-training/SKILL.md`.
