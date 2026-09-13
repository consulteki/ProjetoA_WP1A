# Hipóteses de Pesquisa — WP1A

**Fonte:** `WP1A_SOURCE.pdf` (Seção 5); operacionalizadas em `docs/project/requirements.md` §1.4 e `docs/specs/SPEC-000-master.md` §4.

Todas as hipóteses DEVEM ser avaliadas exclusivamente sobre o conjunto de teste, após o congelamento de todas as configurações dos 6 modelos (ver `docs/adr/ADR-002-test-set-isolation.md`).

| ID | Hipótese | Corroborada se | Refutada se |
|---|---|---|---|
| **H1** | Métodos de conjunto baseados em árvores apresentam desempenho superior aos classificadores lineares em razão das relações não lineares entre as variáveis do processo. | Random Forest, Gradient Boosting e/ou XGBoost superam Regressão Logística em F1 macro e/ou MCC no conjunto de teste. | Regressão Logística iguala ou supera todos os métodos de conjunto baseados em árvores nessas métricas. |
| **H2** | XGBoost e Random Forest apresentam maior F1 macro e MCC do que Regressão Logística e Árvore de Decisão isolada. | F1 macro e MCC de XGBoost **e** de Random Forest superam os de Regressão Logística **e** de Árvore de Decisão. | Qualquer uma dessas desigualdades é violada no conjunto de teste. |
| **H3** | A Regressão Logística permanece competitiva em custo computacional e interpretabilidade, embora apresente menor capacidade de separar falhas com padrões sobrepostos. | Regressão Logística está entre os modelos de menor tempo de treinamento/inferência e menor tamanho de modelo, e apresenta F1 por classe reduzido nas classes de falha mais confundidas (ver QP3). | Regressão Logística não figura entre os métodos de menor custo computacional, ou apresenta desempenho equivalente aos métodos não lineares em todas as classes. |
| **H4** | O melhor modelo segundo acurácia não necessariamente será o melhor quando considerados F1 macro, MCC e custo de inferência. | O modelo com maior acurácia simples não coincide com o modelo com melhor F1 macro, melhor MCC, ou melhor relação desempenho/custo de inferência. | O mesmo modelo lidera simultaneamente acurácia, F1 macro, MCC e custo de inferência. |

## Rastreabilidade

- Versão detalhada/verificável: `docs/project/requirements.md` §1.4.
- Operacionalização normativa: `docs/specs/SPEC-000-master.md` §4.
- Decisão estrutural que fundamenta a comparação multicritério: `docs/adr/ADR-007-multi-criteria-model-evaluation.md`.
- Metodologia estatística usada para corroborar/refutar: `docs/adr/ADR-008-statistical-comparison-methodology.md`.
- Skill responsável pela avaliação final: `.agents/skills/scientific-writing/SKILL.md`.
