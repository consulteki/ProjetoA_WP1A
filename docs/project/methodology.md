# Metodologia — WP1A

**Fonte:** `WP1A_SOURCE.pdf` (Seções 7–11, 18); versão verificável completa em `docs/project/requirements.md` §2–§7; operacionalização normativa em `docs/specs/SPEC-000-master.md` §5–§10, §12.

Este documento é um resumo narrativo da metodologia, para leitura rápida. Para os requisitos verificáveis item a item, ver `requirements.md`; para a especificação vinculante completa (incluindo invariantes e critérios de aceite), ver `docs/specs/SPEC-000-master.md`.

## 1. Dataset

O estudo utiliza dados de simulação do Tennessee Eastman Process (TEP): 52 variáveis de processo, 21 classes (1 condição normal + 20 condições de falha), em arquivos de treinamento e teste contendo execuções sem falha e execuções com falhas induzidas.

→ Skill: `.agents/skills/data-audit/SKILL.md`, `.agents/skills/canonical-dataset/SKILL.md`
→ Decisão estrutural: `docs/adr/ADR-004-canonical-dataset.md`

## 2. Unidade experimental

A unidade de divisão dos dados e de inferência estatística é a **execução do processo (`run`)**, nunca a amostra/observação individual. Amostras da mesma execução não podem aparecer em mais de uma partição (treino/validação/teste).

→ Decisão estrutural: `docs/adr/ADR-001-run-as-group-unit.md`
→ Skill: `.agents/skills/grouped-split/SKILL.md`

## 3. Modelos avaliados

| Modelo | Papel no benchmark |
|---|---|
| Regressão Logística | Baseline linear, interpretável, baixo custo computacional. |
| Árvore de Decisão | Modelo não linear simples, com regras diretamente interpretáveis. |
| Random Forest | Conjunto por *bagging*, redução de variância, boa robustez. |
| Gradient Boosting | Conjunto por *boosting* sequencial com árvores rasas. |
| SVM | Classificador de margem máxima. |
| XGBoost | Boosting otimizado e regularizado — baseline forte. |

→ Decisão estrutural: `docs/adr/ADR-006-model-family-selection.md`
→ Skill: `.agents/skills/ml-training/SKILL.md`

## 4. Protocolo experimental (pipeline)

```
Etapa 1: Auditoria dos dados        → .agents/skills/data-audit/
Etapa 2: Análise exploratória (EDA) → .agents/skills/exploratory-analysis/
Etapa 3: Divisão experimental       → .agents/skills/grouped-split/
Etapa 4: Pré-processamento          → .agents/skills/preprocessing/
Etapa 5: Treinamento e seleção      → .agents/skills/ml-training/
Etapa 6: Avaliação final            → .agents/skills/ml-evaluation/
```

Regras centrais do protocolo:

- Transformações dependentes dos dados são ajustadas exclusivamente no treino.
- Seleção de hiperparâmetros usa apenas treino/validação.
- O conjunto de teste é consultado uma única vez, após o congelamento da configuração final de cada modelo.

→ Decisão estrutural: `docs/adr/ADR-002-test-set-isolation.md`, `docs/adr/ADR-005-experiment-configuration.md`

## 5. Métricas

Acurácia, acurácia balanceada, precisão/revocação/F1 macro, F1 ponderada, MCC multiclasse, métricas por classe, matriz de confusão, tempo de treinamento, tempo de inferência, tamanho do modelo salvo, consumo de memória (quando disponível).

$$F1_{macro} = \frac{1}{C}\sum_{c=1}^{C} F1_c \qquad BA = \frac{1}{C}\sum_{c=1}^{C} \frac{TP_c}{TP_c + FN_c}$$

Nenhuma conclusão de "melhor modelo" pode se basear em métrica única.

→ Decisão estrutural: `docs/adr/ADR-007-multi-criteria-model-evaluation.md`
→ Skill: `.agents/skills/ml-evaluation/SKILL.md`

## 6. Análise estatística

Teste de Friedman (comparação global) seguido de procedimento pós-hoc; teste de Wilcoxon com correção para múltiplas comparações (comparações pareadas); unidade experimental sempre declarada (a execução); nenhuma observação temporalmente correlacionada é tratada como independente.

→ Decisão estrutural: `docs/adr/ADR-008-statistical-comparison-methodology.md`
→ Skill: `.agents/skills/statistical-analysis/SKILL.md`

## 7. Riscos e restrições metodológicas

Vazamento de dados entre execuções; ajuste de hiperparâmetros com base no teste; comparação injusta entre modelos; uso exclusivo de acurácia; omissão de custo computacional; inferência estatística sobre amostras correlacionadas; interpretação causal indevida de importâncias de atributos; falta de registro de versões/sementes.

→ Regras operacionais vinculantes: `AGENTS.md` §1–§2, §8 (Proibições)
→ Guardas executáveis e testes de rejeição: `src/wp1a/` e `tests/methodology/`

## Rastreabilidade

- Requisitos verificáveis completos: `docs/project/requirements.md` §2–§7.
- Especificação vinculante completa: `docs/specs/SPEC-000-master.md`.
