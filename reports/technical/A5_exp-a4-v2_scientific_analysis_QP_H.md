# Análise científica — experimento `exp-a4-v2` (Entrega A5)

| Campo | Valor |
|---|---|
| Papel | Scientific Analyst (somente leitura de artefatos) |
| Experimento | `exp-a4-v2` (baseline SPEC-006 / A4 + avaliação SPEC-007 / A5) |
| Data da análise | 2026-09-14 |
| Status | Análise descritiva a partir de resultados persistidos; **não** altera código nem métricas |
| Causalidade | **Proibida** interpretação causal do processo físico do TEP (SPEC-000 INV-08; AGENTS.md MET-R07) |

Toda afirmação quantitativa abaixo cita o arquivo de origem (DOC-R03).

---

## 1. Fontes utilizadas

| Artefato | Caminho |
|---|---|
| Métricas globais A5 | `results/tables/A5_exp-a4-v2__global_metrics.csv` |
| Custo computacional | `results/tables/A5_exp-a4-v2__cost_metrics.csv` |
| Métricas por classe | `results/tables/A5_exp-a4-v2__per_class_metrics.csv` |
| Classes “worst_k” agregadas | `results/tables/A5_exp-a4-v2__confused_classes.csv` |
| Pares confundidos / QP3 JSON | `results/tables/A5_exp-a4-v2__qp3_confused_faults.json` |
| Pacote A5 completo | `results/metrics/A5_exp-a4-v2__evaluation.json` |
| Configuração do experimento | `configs/experiments/exp-a4-v2.yaml` |
| Snapshot de execução | `results/metadata/exp-a4-v2__config_snapshot.json` |
| Definições QP1–QP5 e H1–H4 | `docs/specs/SPEC-000-master.md` §§3–4 |

---

## 2. Caveats metodológicos (não causais)

1. **Holdout incompleto em classes:** no teste deste split há **11** classes com `support > 0` e **10** ausentes (`0, 1, 4, 5, 7, 8, 9, 12, 16, 17`), conforme `results/tables/A5_exp-a4-v2__per_class_metrics.csv` (ex.: linhas do modelo `xgboost`).
2. **MET-02 / MET-05 usam C = 21** (SPEC-000 §9.2). Classes ausentes no teste entram com recall/F1 = 0 e **deprimem** BA e F1 macro em relação à acurácia simples.
3. **SVM** neste baseline usa apenas `kernel: linear` (`configs/experiments/exp-a4-v2.yaml`).
4. Espaços de busca são os do baseline reduzido (`exp-a4-v2`), não o tuning ampliado da SPEC-006A.
5. Rankings abaixo são **observacionais** sob o protocolo compartilhado (INV-03); não se declara um único “melhor modelo” por métrica isolada (INV-06 / ADR-007).

---

## 3. Rankings observacionais (conjunto de teste)

Fonte: `results/tables/A5_exp-a4-v2__global_metrics.csv` (`formula_checks_ok=True` nos seis modelos).

| Critério | 1º | 2º | 3º | Último |
|---|---|---|---|---|
| MET-01 acurácia | xgboost **0.6185** | random_forest **0.6165** | gradient_boosting **0.6080** | svm **0.2374** |
| MET-02 BA | random_forest **0.3326** | xgboost **0.3300** | gradient_boosting **0.3214** | svm **0.1501** |
| MET-05 F1 macro | random_forest **0.3568** | xgboost **0.3531** | gradient_boosting **0.3465** | svm **0.1633** |
| MET-07 MCC | random_forest **0.5966** | xgboost **0.5956** | gradient_boosting **0.5836** | svm **0.2152** |
| MET-10 treino (menor melhor) | decision_tree **1.36 s** | random_forest **3.09 s** | logistic_regression **3.65 s** | gradient_boosting **281.9 s** |
| MET-11 inferência (menor melhor) | decision_tree **0.0015 s** | logistic_regression **0.0031 s** | xgboost **0.052 s** | svm **3.58 s** |
| MET-12 tamanho (menor melhor) | logistic_regression **10 020 B** | decision_tree **158 662 B** | gradient_boosting **1 901 442 B** | random_forest **49 567 094 B** |

Valores de custo também em `results/tables/A5_exp-a4-v2__cost_metrics.csv`.

---

## 4. Questões de pesquisa

### QP1 — Quais algoritmos apresentam o melhor desempenho global?

Fonte: `results/tables/A5_exp-a4-v2__global_metrics.csv`.

- Por **acurácia**: xgboost > random_forest ≈ gradient_boosting ≫ decision_tree ≫ logistic_regression > svm.
- Por **F1 macro / MCC / BA**: random_forest ligeiramente à frente de xgboost, depois gradient_boosting e decision_tree; logistic_regression e svm ficam no grupo inferior.

**Resposta:** sob o protocolo deste experimento, os métodos de conjunto baseados em árvores (RF, XGB, GB) e a árvore isolada dominam as métricas globais de classificação no teste; LR e SVM linear formam o grupo inferior. Não há ranking único oficial — ver QP5 e INV-06.

### QP2 — O desempenho é consistente sob equilíbrio entre classes?

Fonte: `results/tables/A5_exp-a4-v2__global_metrics.csv`.

| Ranking | Ordem observada |
|---|---|
| Acurácia (MET-01) | XGB → RF → GB → DT → LR → SVM |
| BA / F1 macro / MCC | **RF → XGB** → GB → DT → LR → SVM |

**Resposta:** não é totalmente consistente. O líder em acurácia (xgboost, 0.6185) **não** é o líder em BA/F1/MCC (random_forest: F1 0.3568, MCC 0.5966), embora a diferença XGB–RF seja pequena. A lacuna acurácia ≫ BA/F1 é compatível com a média sobre 21 classes incluindo 10 ausentes no teste (`per_class_metrics.csv`).

### QP3 — Quais falhas são sistematicamente mais difíceis?

**Advertência sobre `confused_classes.csv`:** as classes `1, 4, 5, 7, 8` aparecem em `results/tables/A5_exp-a4-v2__confused_classes.csv` com alta frequência no “worst_k”, porém em `results/tables/A5_exp-a4-v2__per_class_metrics.csv` têm **`support = 0` no teste**. O F1 = 0 nesses casos reflete ausência no holdout, não erro de classificação observado. Não devem ser lidas como “falhas difíceis de diagnosticar” neste teste.

**Classes com `support > 0` e menor F1 médio entre os seis modelos** (agregação a partir de `A5_exp-a4-v2__per_class_metrics.csv`):

| class_label | support | mean F1 (6 modelos) |
|---|---:|---:|
| **3** | 480 | **0.184** |
| **15** | 480 | **0.252** |
| **10** | 960 | **0.283** |
| 13 | 480 | 0.415 |
| 19 | 480 | 0.521 |
| 2 (mais alto em média) | 480 | 0.970 |

**Pares de confusão mais frequentes (soma entre modelos)** — `results/tables/A5_exp-a4-v2__qp3_confused_faults.json`:

| true → pred | total_count_across_models |
|---|---:|
| 10 → 15 | 1451 |
| 3 → 15 | 1002 |
| 18 → 5 | 1001 |
| 13 → 12 | 809 |

**Resposta:** neste holdout, as falhas **3, 15 e 10** são as de menor F1 médio entre classes presentes; as confusões **10→15** e **3→15** são recorrentes. Não se interpreta mecanismo físico dessas confusões (INV-08).

### QP4 — Métodos mais complexos justificam maior custo?

Fontes: `A5_exp-a4-v2__global_metrics.csv`, `A5_exp-a4-v2__cost_metrics.csv`.

| Modelo | F1 macro | MCC | treino (s) | inferência (s) | tamanho (B) |
|---|---:|---:|---:|---:|---:|
| random_forest | 0.357 | 0.597 | 3.1 | 0.24 | 49 567 094 |
| xgboost | 0.353 | 0.596 | 22.3 | 0.052 | 4 910 294 |
| gradient_boosting | 0.347 | 0.584 | 281.9 | 0.10 | 1 901 442 |
| decision_tree | 0.314 | 0.560 | 1.4 | 0.0015 | 158 662 |
| logistic_regression | 0.184 | 0.250 | 3.6 | 0.003 | 10 020 |
| svm | 0.163 | 0.215 | 177.0 | 3.58 | 8 782 836 |

**Resposta (descritiva):**
- RF obtém o melhor F1/MCC com treino baixo, porém o maior artefato.
- XGB quase empata RF em F1/MCC, com inferência mais rápida e tamanho ~10× menor que RF.
- GB não supera RF/XGB em F1/MCC e tem o maior tempo de treino — o ganho observado não acompanha esse custo neste baseline.
- SVM linear combina custo alto e pior desempenho preditivo entre os seis.

Não se afirma que a complexidade *causa* o desempenho; apenas se cruza custo e métricas reportadas.

### QP5 — Melhor compromisso desempenho × tempo × tamanho?

**Síntese multicritério (sem vencedor absoluto):**

- Maximizar F1/MCC: **random_forest** (ligeiramente à frente), com custo de armazenamento alto.
- Compromisso observacional desempenho/custo neste baseline: **xgboost** (F1/MCC ≈ RF; inferência e tamanho mais favoráveis que RF; treino moderado vs GB).
- Extremo barato com desempenho intermediário: **decision_tree**.
- Extremo compacto/rápido em inferência com desempenho global baixo: **logistic_regression**.

Esta é uma síntese de trade-offs (ADR-007 / QP5), não uma eleição de “melhor modelo” por métrica única.

---

## 5. Avaliação das hipóteses

Critérios de suporte/refutação: `docs/specs/SPEC-000-master.md` §4.  
Evidência numérica: `results/tables/A5_exp-a4-v2__global_metrics.csv` e, para H3, `results/tables/A5_exp-a4-v2__per_class_metrics.csv`.

### H1 — Conjuntos em árvore superam regressão logística (F1 e/ou MCC)

| Modelo | F1 macro | MCC | vs LR |
|---|---:|---:|---|
| random_forest | 0.3568 | 0.5966 | supera |
| gradient_boosting | 0.3465 | 0.5836 | supera |
| xgboost | 0.3531 | 0.5956 | supera |
| logistic_regression | 0.1838 | 0.2496 | — |

**Veredito (SPEC-000 §4 / holdout):** **H1 corroborada.** Status run-level: pendente (SPEC-008).

### H2 — XGBoost e Random Forest > LR e árvore isolada (F1 e MCC)

- RF: F1/MCC > LR e > decision_tree.
- XGB: F1/MCC > LR e > decision_tree.

Fonte: `A5_exp-a4-v2__global_metrics.csv`.

**Veredito (SPEC-000 §4 / holdout):** **H2 corroborada.** Status run-level: pendente (SPEC-008).

### H3 — LR competitiva em custo; F1 reduzido nas falhas difíceis (QP3)

- **Custo** (`A5_exp-a4-v2__cost_metrics.csv`): menor tamanho (10 020 B); 2º menor tempo de inferência; 3º menor tempo de treino → está entre os de menor custo.
- **Falhas com suporte e baixo F1 médio** (classes 3, 15, 10, 13, 19 em `per_class_metrics.csv`): LR é especialmente baixa em **13** (F1 0.090) e **19** (0.126) frente a RF/XGB; na classe **3** não é a pior absoluta. A redução de F1 nas falhas difíceis **existe**, ainda que não seja uniforme em todas as classes (o critério §4 não exige uniformidade).
- **Refutação §4:** LR fora do grupo de menor custo **ou** LR igualando não lineares em *todas* as classes — nenhuma se observa.

**Veredito (SPEC-000 §4 / holdout):** **H3 corroborada.** Status run-level: pendente (SPEC-008).

### H4 — Melhor por acurácia ≠ melhor por F1 / MCC / custo de inferência

Fonte: `A5_exp-a4-v2__global_metrics.csv`.

| Critério | Líder observado |
|---|---|
| Maior acurácia | xgboost (0.6185) |
| Maior F1 macro | random_forest (0.3568) |
| Maior MCC | random_forest (0.5966) |
| Menor inferência | decision_tree (0.0015 s) |

O mesmo modelo **não** lidera todos esses critérios.

**Veredito (SPEC-000 §4 / holdout):** **H4 corroborada.** Status run-level: pendente (SPEC-008).

---

## 6. Resumo executivo

| Item | Conclusão baseada nos artefatos |
|---|---|
| QP1 | RF / XGB / GB lideram métricas globais; LR e SVM linear atrás |
| QP2 | Ranking por acurácia ≠ ranking por BA/F1/MCC (XGB vs RF) |
| QP3 | Entre classes presentes: 3, 15, 10 mais difíceis; confusões 10→15 e 3→15 recorrentes |
| QP4 | XGB/RF oferecem melhor relação desempenho/custo que GB e SVM neste baseline |
| QP5 | Trade-off: RF (F1/MCC) vs XGB (compromisso) vs DT (custo mínimo) |
| H1 | Corroborada (§4 / holdout; SPEC-008 pendente) |
| H2 | Corroborada (§4 / holdout; SPEC-008 pendente) |
| H3 | Corroborada (§4 / holdout; SPEC-008 pendente) |
| H4 | Corroborada (§4 / holdout; SPEC-008 pendente) |

---

## 7. O que esta análise deliberadamente não faz

- Não altera código, hiperparâmetros, predições nem métricas.
- Não atribui causa física às confusões entre falhas do TEP.
- Não substitui a Entrega A7/A8 completa (SPEC-009) nem a análise estatística formal (SPEC-008).
- Não usa o conjunto de teste para propor novo tuning (isso exigiria SPEC-006A com novo `experiment_id`).
