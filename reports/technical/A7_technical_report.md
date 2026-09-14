# Relatório técnico final (Entrega A7)

**Título:** Benchmark reproduzível de métodos clássicos de aprendizado de máquina para diagnóstico de falhas no Tennessee Eastman Process

| Campo | Valor |
|---|---|
| Entrega | A7 — Relatório técnico final (SPEC-000 §11.1; SPEC-009 §3.2) |
| Subprojeto | WP1A / MEI0028 – Modelagem e Simulação |
| Experimento oficial | `exp-a4-v2` (baseline SPEC-006 / A4 + avaliação SPEC-007 / A5) |
| Dataset canônico | `tep-canonical-v1` |
| Manifesto de divisão | `data/processed/split_manifest_v1.json` (A3) |
| Pré-processamento | `preprocessor_v1` (fit exclusivo no treino) |
| Semente | 42 (`configs/seeds.yaml`) |
| SHA de execução A4 | `40c6c6026f39c6e356ed8e3e57950a7a89dddb5e` (`git_dirty: true` no snapshot) |
| Data do relatório | 2026-09-14 |
| Fontes normativas | `docs/specs/SPEC-000-master.md`, `AGENTS.md`, SPEC-001…009 |

**Escopo deste documento.** Consolida metodologia, protocolo reprodutível, resultados e respostas a QP1–QP5 / H1–H4 com rastreabilidade a artefatos em `results/` e `article/` (DOC-R03). Inclui a análise estatística formal SPEC-008 (Friedman/Wilcoxon com unidade = `run_id`). Não interpreta importâncias de atributos como causalidade física do TEP (INV-08 / MET-R07).

---

## Sumário executivo

Sob o protocolo compartilhado do experimento `exp-a4-v2`, os conjuntos baseados em árvores (Random Forest, XGBoost, Gradient Boosting) lideram as métricas globais de classificação no conjunto de teste; Regressão Logística e SVM linear formam o grupo inferior. O líder em acurácia simples (XGBoost) **não** coincide com o líder em F1 macro / MCC (Random Forest). Entre classes presentes no teste, as falhas **3, 15 e 10** apresentam os menores F1 médios; as confusões **10→15** e **3→15** são as mais frequentes. Multicritério: RF maximiza F1/MCC; XGBoost oferece compromisso desempenho/custo; Decision Tree é o extremo de custo baixo. Pelos critérios binários de SPEC-000 §4 (estimativas pontuais do holdout), H1–H4 são **corroboradas**. Em nível de `run` (SPEC-008, acurácia dentro da execução, n=11): Friedman rejeita igualdade global (p=0,015); Wilcoxon+Holm na família H1 **corrobora** ensembles > LR; a família H2 **não** corrobora RF/XGB > DT (poder limitado). Ameaças críticas: cobertura disjunta val/teste de classes; semente/split únicos; orçamentos de busca desiguais.

---

## 1. Introdução

### 1.1 Problema

O diagnóstico automático de falhas em processos químicos industriais exige classificadores capazes de distinguir a condição normal de múltiplos modos de falha a partir de variáveis de processo. O Tennessee Eastman Process (TEP) é um ambiente simulado de referência com 52 variáveis e 21 classes (1 normal + 20 falhas). Comparações entre algoritmos frequentemente sofrem de vazamento temporal entre partições, protocolos inconsistentes entre modelos e conclusões baseadas apenas em acurácia simples.

### 1.2 Objetivos do WP1A

Conforme SPEC-000 §1, o subprojeto desenvolve um **benchmark reproduzível** de seis famílias clássicas de aprendizado de máquina, avaliando desempenho preditivo, equilíbrio entre classes, custo computacional e interpretabilidade descritiva — sem pretender estado da arte em modelos profundos ou física-orientada (SPEC-000 §2.2).

Objetivos específicos OBJ-1 a OBJ-8 (auditoria → artigo) estruturam as entregas A1–A9. Este relatório (A7) responde às questões de pesquisa QP1–QP5 e avalia as hipóteses H1–H4 com evidência do conjunto de teste do experimento congelado `exp-a4-v2`.

### 1.3 Questões de pesquisa e hipóteses

| ID | Conteúdo (SPEC-000 §§3–4) |
|---|---|
| QP1 | Melhor desempenho global entre os 6 algoritmos |
| QP2 | Consistência sob equilíbrio entre classes (acurácia vs BA/F1/MCC) |
| QP3 | Falhas sistematicamente mais difíceis |
| QP4 | Complexidade vs justificativa de custo |
| QP5 | Melhor compromisso desempenho × tempo × tamanho |
| H1–H4 | Ver Seção 7 deste relatório |

---

## 2. Fundamentação: diagnóstico de falhas e TEP

O TEP simula uma planta química com reciclo, reator, condensador, separador e stripper. Cada execução (*run*) induz (ou não) uma falha e produz uma série temporal de observações. No WP1A, o problema é formulado como **classificação multiclasse** de vetores de 52 variáveis para um rótulo em {0,…,20}.

A **unidade experimental** é a execução (`run_id`), não a linha/amostra (UE-01). Observações dentro de um mesmo run são temporalmente correlacionadas; tratá-las como independentes viola INV-09. A divisão treino/validação/teste e **toda** inferência estatística (incluindo SPEC-008) devem respeitar essa unidade (UE-02, UE-03).

---

## 3. Trabalhos relacionados (posicionamento)

Este relatório não reproduz uma revisão bibliográfica exaustiva (reservada ao manuscrito A8). Em síntese, o posicionamento do WP1A é:

1. **Protocolo único** para seis classificadores clássicos (INV-03), em contraste com estudos que misturam splits ou pré-processamentos por modelo.
2. **Anti-vazamento por run** como invariante operacional (INV-01/INV-02), com checagem automatizada no manifesto A3.
3. **Avaliação multicritério** obrigatória (INV-06, INV-07; ADR-007), incluindo custo (MET-10–12).
4. **Delimitação explícita** frente a redes profundas e métodos físico-informados, que usam este benchmark como referência clássica futura (SPEC-000 §2.2).

---

## 4. Materiais e métodos

### 4.1 Dataset canônico

| Item | Valor | Fonte |
|---|---|---|
| Versão | `tep-canonical-v1` | `article/tables/A6_exp-a4-v2__01_dataset_summary.csv` |
| Features | 52 | idem |
| Classes canônicas | 21 | idem |
| Runs canônicos | 42 | idem |
| Linhas | 30 260 | idem |
| Pacote bruto auditado | 44 arquivos; 22 classes observadas no pack | A1 / sumário A6 |

A auditoria (Etapa 1 / A1) e o registro canônico (SPEC-002) precedem qualquer modelagem. Detalhes operacionais: `reports/audit/`, `data/processed/canonical_dataset_registry.json`.

### 4.2 Análise exploratória (Etapa 2 / A2)

A EDA documenta distribuições e correlações **sem** decidir hiperparâmetros nem o manifesto de divisão científica. Artefatos: `reports/eda/`, `results/figures/A2_*.png`, `results/tables/A2_*.csv`.

### 4.3 Divisão agrupada por execução (Etapa 3 / A3)

- **Manifesto:** `data/processed/split_manifest_v1.json`
- **Estratégia:** `stratified_one_train_per_class_remaining_split_val_test` — um run por classe no treino; restante ~50/50 validação/teste (semente 42).
- **Partições:** treino 21 runs; validação 10; teste 11.
- **Checagem de leakage:** `leakage_check.status = passed` (interseção vazia de `run_id` par a par).

**Limitação estrutural documentada no manifesto:** com apenas dois runs por classe no canônico, reservar um run/classe ao treino implica que validação e teste **não cobrem simultaneamente as 21 classes**. Em `exp-a4-v2`:

| Partição | Classes presentes | Classes ausentes |
|---|---|---|
| Validação | 0, 1, 4, 5, 7, 8, 9, 12, 16, 17 | 2, 3, 6, 10, 11, 13, 14, 15, 18, 19, 20 |
| Teste | 2, 3, 6, 10, 11, 13, 14, 15, 18, 19, 20 | 0, 1, 4, 5, 7, 8, 9, 12, 16, 17 |

Os conjuntos de classes de validação e teste são **disjuntos**. Isso afeta a validade de constructo da seleção por validação (ver Seção 8).

### 4.4 Pré-processamento (Etapa 4)

Versão `preprocessor_v1`: padronização (e demais transformações dependentes dos dados) **ajustadas exclusivamente no treino** e aplicadas a validação/teste (INV-04 / LEAK-R02 / LEAK-R05). Artefatos: `preprocessor_v1_*.csv.gz`, `preprocessor_v1_scaler_params.json`, metadados em `results/metadata/preprocessing.json`.

### 4.5 Modelos (MOD-1 a MOD-6)

| Código | Modelo | Adapter |
|---|---|---|
| MOD-1 | Regressão logística | `logistic_regression` |
| MOD-2 | Árvore de decisão | `decision_tree` |
| MOD-3 | Random Forest | `random_forest` |
| MOD-4 | Gradient Boosting (sklearn) | `gradient_boosting` |
| MOD-5 | SVM | `svm` |
| MOD-6 | XGBoost | `xgboost` |

Todos passam pelo mesmo `ExperimentRunner` (`src/wp1a/experiment/`), mesmo manifesto A3 e mesmo `preprocessor_v1` (INV-03 / MET-R03).

### 4.6 Seleção de hiperparâmetros (Etapa 5 / A4)

- Configuração: `configs/experiments/exp-a4-v2.yaml`
- Seleção **somente** em treino/validação; teste consultado após congelamento (INV-05).
- Espaços de busca do **baseline reduzido** (não SPEC-006A):
  - GB: 2 candidatos (`n_estimators=50`, `max_depth ∈ {2,3}`)
  - SVM: apenas `kernel: linear`
  - XGBoost: 8 candidatos; RF: 4; etc. (orçamentos **desiguais** — ameaça de validade estatística/comparabilidade)
- Scorer de seleção nesta rodada: acurácia na validação (limitação discutida na Seção 8, dado o descompasso de classes val↔teste).

**Hiperparâmetros finais selecionados** (`article/tables/A6_exp-a4-v2__02_hyperparameters.csv`):

| Modelo | Principais parâmetros |
|---|---|
| logistic_regression | C=10.0, max_iter=1000, solver=lbfgs |
| decision_tree | max_depth=20, min_samples_leaf=5, criterion=gini |
| random_forest | n_estimators=200, max_depth=20, min_samples_leaf=1 |
| gradient_boosting | n_estimators=50, learning_rate=0.1, max_depth=3 |
| svm | C=10.0, kernel=linear, cache_size=500 |
| xgboost | n_estimators=100, learning_rate=0.1, max_depth=6, tree_method=hist |

### 4.7 Avaliação (Etapa 6 / A5)

Métricas MET-01 a MET-12 conforme SPEC-000 §9; F1 macro e acurácia balanceada com **C = 21** (classes ausentes no teste entram com contribuição nula e deprimem BA/F1 em relação à acurácia). Verificação CA-06: `formula_checks_ok=True` nos seis modelos (`results/tables/A5_exp-a4-v2__global_metrics.csv`).

Figuras/tabelas A6 geradas **somente** a partir de `results/` (proibido `data/raw`): `make figures` → `article/figures|tables/A6_exp-a4-v2__*`.

### 4.8 Ambiente computacional

Fonte: `results/metadata/exp-a4-v2__config_snapshot.json`.

| Item | Valor |
|---|---|
| Python | 3.12.7 (CPython) |
| scikit-learn | 1.9.1 |
| xgboost | 2.1.4 |
| numpy / pandas / joblib | 1.26.4 / 2.2.3 / 1.4.2 |
| Plataforma | Linux x86_64, 16 CPUs |
| Branch / SHA | `feat/experiment-runner` / `40c6c6026f39…` (`git_dirty: true`) |

---

## 5. Protocolo reprodutível

| Requisito | Cumprimento neste experimento |
|---|---|
| REP-01 semente | 42 registrada no manifesto e no snapshot |
| REP-02 `run_id`s por partição | `split_manifest_v1.json` + CSVs `train/validation/test_runs.csv` |
| REP-03 versões de software | snapshot `environment` |
| REP-04 hiperparâmetros finais | A6 tabela 02 / `results/tables/` |
| REP-05 scripts e README | `make train`, `make evaluate`, `make figures`; `README.md` |
| REP-06 resultados brutos | `results/predictions/`, `results/tables/A5_*`, `results/metrics/A5_*` |

**Ordem fixa do pipeline (MET-R02):** Auditoria → EDA → Divisão → Pré-processamento → Treinamento/Seleção → Avaliação final. O dry-run (`make dry-run`, `scientific_validity: false`) **não** alimenta este relatório.

**Identidade do experimento:** `exp-a4-v2` substitui `exp-a4-v1` (abortado no GB); novo `experiment_id` conforme EXP-R04. Tuning ampliado (SPEC-006A) **não** foi executado e não altera esta baseline.

Comandos de referência:

```bash
make audit && make canonical-dataset && make eda && make split && make preprocess
make train EXPERIMENT=exp-a4-v2   # ou configs/experiments/exp-a4-v2.yaml
make evaluate EXPERIMENT=exp-a4-v2
make figures EXPERIMENT=exp-a4-v2
```

---

## 6. Resultados

Todas as afirmações quantitativas citam arquivos versionados.

### 6.1 Métricas globais e custo (teste)

Fonte: `results/tables/A5_exp-a4-v2__global_metrics.csv` e `…__cost_metrics.csv`. Visualizações: `article/figures/A6_exp-a4-v2__06_f1_mcc.png`, `…__07_computational_cost.png`; tabelas `article/tables/A6_exp-a4-v2__03_global_metrics.*`, `…__07_computational_cost.csv`.

| Modelo | Acc (MET-01) | BA (MET-02) | F1 macro (MET-05) | MCC (MET-07) | Treino s (MET-10) | Inferência s (MET-11) | Tamanho B (MET-12) |
|---|---:|---:|---:|---:|---:|---:|---:|
| logistic_regression | 0.275 | 0.164 | 0.184 | 0.250 | 3.65 | 0.0031 | 10 020 |
| decision_tree | 0.564 | 0.303 | 0.314 | 0.560 | 1.36 | 0.0015 | 158 662 |
| random_forest | 0.617 | **0.333** | **0.357** | **0.597** | 3.09 | 0.243 | 49 567 094 |
| gradient_boosting | 0.608 | 0.321 | 0.347 | 0.584 | 281.89 | 0.101 | 1 901 442 |
| svm | 0.237 | 0.150 | 0.163 | 0.215 | 177.03 | 3.575 | 8 782 836 |
| xgboost | **0.618** | 0.330 | 0.353 | 0.596 | 22.28 | 0.052 | 4 910 294 |

Valores arredondados; precisão completa nos CSVs citados. `formula_checks_ok=True` para todos.

### 6.2 Métricas por classe e confusões

- Por classe: `results/tables/A5_exp-a4-v2__per_class_metrics.csv` / `article/tables/A6_exp-a4-v2__04_per_class_metrics.csv`
- Matrizes: `article/figures/A6_exp-a4-v2__05_cm__*.png`
- Heatmap F1 (NaN onde support=0): `article/figures/A6_exp-a4-v2__08_per_class_f1_heatmap.png`
- Pares confundidos: `article/tables/A6_exp-a4-v2__08_confused_pairs.csv`, `…__08_confused_pairs.png`, `results/tables/A5_exp-a4-v2__qp3_confused_faults.json`

**Classes com support > 0 e menor F1 médio (6 modelos):** 3 (0.184), 15 (0.252), 10 (0.283).  
**Pares mais frequentes (soma entre modelos):** 10→15 (1451), 3→15 (1002), 18→5 (1001), 13→12 (809).

Classes com `support = 0` no teste **não** são interpretadas como “falhas difíceis observadas” neste holdout (F1=0 por ausência).

### 6.3 Respostas explícitas a QP1–QP5

#### QP1 — Quais algoritmos apresentam o melhor desempenho global?

**Resposta.** No teste de `exp-a4-v2`, o grupo superior em métricas globais é formado por **Random Forest, XGBoost e Gradient Boosting**, seguidos de Decision Tree; **Regressão Logística e SVM linear** ficam no grupo inferior (`A5_exp-a4-v2__global_metrics.csv`). Não há “melhor modelo” oficial por métrica única (INV-06): por acurácia lidera XGBoost (0.618); por F1 macro e MCC lidera Random Forest (0.357 / 0.597).

#### QP2 — O desempenho é consistente sob equilíbrio entre classes?

**Resposta.** **Não totalmente.** Ranking por acurácia: XGB → RF → GB → DT → LR → SVM. Ranking por BA / F1 macro / MCC: **RF → XGB** → GB → DT → LR → SVM. A lacuna acurácia ≫ BA/F1 é compatível com a média sobre C=21 incluindo 10 classes ausentes no teste (`per_class_metrics.csv`).

#### QP3 — Quais falhas são sistematicamente mais difíceis?

**Resposta.** Entre classes **presentes** no teste, **3, 15 e 10** têm os menores F1 médios entre os seis modelos; confusões recorrentes **10→15** e **3→15** (`qp3_confused_faults.json`, A6 pares). Não se atribui mecanismo físico a essas confusões (INV-08).

#### QP4 — Métodos mais complexos justificam maior custo?

**Resposta (descritiva).** RF obtém o melhor F1/MCC com treino baixo, porém o maior artefato. XGB quase empata RF com inferência mais rápida e tamanho ~10× menor que RF. GB **não** supera RF/XGB em F1/MCC e tem o maior tempo de treino (≈282 s) — o ganho observado **não** acompanha esse custo neste baseline. SVM linear combina custo alto e pior desempenho preditivo. Fonte: `global_metrics.csv` + `cost_metrics.csv`.

#### QP5 — Melhor compromisso desempenho × tempo × tamanho?

**Resposta multicritério (ADR-007; sem vencedor absoluto).**

| Objetivo | Escolha observacional neste baseline |
|---|---|
| Maximizar F1/MCC | **random_forest** (ligeira frente) |
| Compromisso desempenho/custo | **xgboost** |
| Extremo barato com desempenho intermediário | **decision_tree** |
| Extremo compacto/rápido com desempenho global baixo | **logistic_regression** |

---

## 6.4 Análise estatística formal (SPEC-008)

Fontes: `results/tables/A8_exp-a4-v2__*.csv|json`, `results/metrics/A8_exp-a4-v2__statistics.json`.

| Declaração obrigatória | Valor |
|---|---|
| Unidade experimental | `run_id` (INV-09 / EST-04) |
| Número de unidades | **11** runs de teste |
| Métrica pareada | `run_accuracy` (acurácia *dentro* de cada run; cada run tem uma única classe verdadeira) |
| α | 0,05 |
| Sementes/splits | 1 (limitação EST-01 entre sementes) |

**Friedman** (6 modelos × 11 runs): χ² = 14,079; **p = 0,0151**; rejeita H₀ de igualdade de ranks (`A8_…__friedman.json`).

**Resumo por modelo** (média ± DP da acurácia por run; IC 95% normal-approx) — `A8_…__run_metric_summary.csv`:

| Modelo | Média run_acc | DP | IC95% |
|---|---:|---:|---|
| random_forest | 0,635 | 0,267 | [0,478; 0,793] |
| xgboost | 0,630 | 0,288 | [0,460; 0,800] |
| gradient_boosting | 0,614 | 0,278 | [0,449; 0,778] |
| decision_tree | 0,579 | 0,342 | [0,376; 0,781] |
| logistic_regression | 0,313 | 0,315 | [0,127; 0,499] |
| svm | 0,287 | 0,306 | [0,106; 0,467] |

**Wilcoxon + Holm**
- Família planejada **H1** (3 pares ensemble vs LR): todos significativos após Holm (`A8_…__wilcoxon_H1_family.csv`) → run-level **corrobora** H1 na métrica `run_accuracy`.
- Família planejada **H2** (4 pares RF/XGB vs LR/DT): **nenhum** par permanece significativo após Holm (`A8_…__wilcoxon_H2_family.csv`) → run-level **não corrobora** H2 (diferenças vs DT pequenas; n=11).
- Tabela exploratória all-pairs com Holm global: `A8_…__wilcoxon_all_pairs.csv` (mais conservadora).

Macro-F1/MCC com C=21 **não** entram como blocos do Friedman (mal definidos por run monoclasse); H3/H4 permanecem critérios §4 sobre métricas/custo globais.

---

## 7. Avaliação das hipóteses (H1–H4)

Critérios binários de SPEC-000 §4 (**corroborada** / **refutada**) sobre métricas globais/custo do holdout, **mais** evidência run-level SPEC-008 onde aplicável.

> **Dois planos de evidência.** (1) §4 sobre F1/MCC/custo globais (`A5_…`). (2) Friedman/Wilcoxon sobre `run_accuracy` com n=11 (`A8_…`). Concordância entre planos não é automática.

### H1 — Conjuntos em árvore superam regressão logística (F1 e/ou MCC)

RF, GB e XGB superam LR em F1 macro e em MCC (`global_metrics.csv`). Critério de refutação (§4) **não** se observa.

**Veredito (SPEC-000 §4 / holdout):** **H1 corroborada.**  
**Veredito run-level (Wilcoxon+Holm, família H1, `run_accuracy`):** **corroborada** (`A8_…__wilcoxon_H1_family.csv`; Friedman global p=0,015).

### H2 — XGBoost e Random Forest > LR e árvore isolada (F1 e MCC)

RF e XGB superam LR e Decision Tree em F1 macro e MCC globais. Nenhuma desigualdade §4 é violada.

**Veredito (SPEC-000 §4 / holdout):** **H2 corroborada.**  
**Veredito run-level (Wilcoxon+Holm, família H2, `run_accuracy`):** **não corroborada** — **nenhum** dos quatro pares planejados (RF/XGB vs LR e vs DT) permanece significativo após Holm (`A8_…__wilcoxon_H2_family.csv`). Nota: RF/XGB vs LR *são* significativos na família H1 (3 pares), mas deixam de sê-lo sob Holm quando a família cresce para 4 pares em H2; as diferenças médias vs DT são as menores. A superioridade §4 em F1/MCC **não** se traduz em corroboração Wilcoxon de `run_accuracy` para H2 com n=11.

### H3 — LR competitiva em custo; F1 reduzido nas falhas difíceis (QP3)

- **Cláusula de custo (§4):** menor tamanho (10 020 B); 2º menor inferência; 3º menor treino → **está entre os modelos de menor custo** (`cost_metrics.csv`).
- **Cláusula de falhas difíceis (§4):** nas classes de QP3 com `support > 0`, LR apresenta F1 por classe **reduzido** frente aos ensembles em várias falhas (p.ex. 13 e 19); a redução **não** é uniforme em todas as classes difíceis (na classe 3 LR não é a pior absoluta) (`per_class_metrics.csv`).
- **Refutação (§4):** exigiria (i) LR fora do grupo de menor custo **ou** (ii) LR igualar os métodos não lineares em *todas* as classes. Nenhuma das duas se observa.

**Veredito (SPEC-000 §4 / holdout):** **H3 corroborada.**  
**Veredito run-level:** não aplicável como teste primário (H3 não é contraste único de acurácia por run).

### H4 — Melhor por acurácia ≠ melhor por F1 / MCC / custo de inferência

| Critério | Líder observado |
|---|---|
| Maior acurácia | xgboost (0.618) |
| Maior F1 macro | random_forest (0.357) |
| Maior MCC | random_forest (0.597) |
| Menor inferência | decision_tree (0.0015 s) |

O mesmo modelo **não** lidera todos esses critérios.

**Veredito (SPEC-000 §4 / holdout):** **H4 corroborada.**  
**Veredito run-level:** não aplicável como contraste Wilcoxon único (H4 é multicritério).

---

## 8. Discussão

1. **Multicritério é necessário.** Usar só acurácia elegeria XGBoost; F1/MCC elegem RF; custo de inferência elege DT — consistente com H4 (§4) e INV-06/INV-07.
2. **Friedman vs Wilcoxon.** Há evidência global de diferenças entre os seis modelos (Friedman p=0,015), mas o poder pareado com n=11 é baixo: H1 (família de 3 pares vs LR) passa Holm; H2 (família de 4 pares, incluindo vs DT) não — nenhum dos quatro pares permanece significativo (**AR-5**).
3. **Macro métricas e classes ausentes (AR-4).** BA e F1 macro com C=21 incluem zeros por ausência — comparáveis entre modelos no mesmo teste, não “média sobre todas as falhas industriais”.
4. **Seleção vs avaliação (AR-1, AR-2).** Classes de val e teste disjuntas e scorer de acurácia limitam a interpretação dos hiperparâmetros escolhidos na validação.
5. **Orçamentos de busca desiguais (AR-3).** GB (2 candidatos) vs XGB (8); SVM só linear — sem claim de esforço de otimização igual entre famílias.
6. **Sem causalidade física.** Confusões 10→15 / 3→15 descrevem comportamento dos classificadores (INV-08).

Os riscos AR-1–AR-5 são **aceitos** para este `experiment_id` (Seção 9.6); não foram removidos por alteração do protocolo congelado.

---

## 9. Ameaças à validade

Cobertura das quatro categorias (SPEC-000 §14) e ameaça transversal de reprodutibilidade.

### 9.1 Validade interna

| Ameaça | Situação neste estudo |
|---|---|
| Vazamento por `run` | **Mitigada:** divisão por `run_id`; `leakage_check.status=passed` no manifesto A3. |
| Contaminação do teste na seleção | **Mitigada operacionalmente:** seleção só em treino/val; teste após freeze (INV-05). **Não** houve retreino pós-teste. |
| Fit de transformações fora do treino | **Mitigada:** `preprocessor_v1` fit(train) only. |
| Protocolos distintos entre modelos | **Mitigada:** mesmo manifesto e preprocessor (INV-03). |
| Alinhamento val↔teste de classes | **Não mitigada estruturalmente:** classes de val e teste disjuntas (limitação do canônico com 2 runs/classe). A seleção por validação não observa as falhas do teste. |
| Scorer de seleção = acurácia amostral | **Parcialmente mitigada em relatório:** reconhecida; desalinhada com F1/BA sob desbalanceamento e sob descompasso de classes. |

### 9.2 Validade estatística

| Ameaça | Situação |
|---|---|
| Pseudo-replicação (amostras vs runs) | **Mitigada nos testes SPEC-008:** agregação por `run_id` antes de Friedman/Wilcoxon (INV-09). Residual: n=11 e uma semente limitam poder. |
| Comparações múltiplas | **Mitigada:** Holm dentro de famílias H1/H2 e tabela all-pairs com Holm (`A8_…`). |
| Métrica única | **Mitigada na redação:** INV-06; custo sempre discutido (INV-07). |
| Uma semente | Apenas seed 42; sem `replication_seeds` nesta rodada — sensibilidade a seed não quantificada. |
| Orçamentos de busca desiguais | Limitam comparabilidade entre famílias (especialmente GB vs XGB; SVM linear vs RBF futuro). |

### 9.3 Validade de constructo

| Ameaça | Situação |
|---|---|
| Causalidade via importâncias | **Mitigada:** este relatório **não** interpreta importância de atributos como física do TEP (INV-08). |
| “Melhor modelo” = só acurácia | **Mitigada:** QP5 multicritério; H4 explícita. |
| F1/BA com C=21 e classes ausentes | Constructo de “desempenho macro sobre 21 classes” inclui zeros por ausência — documentado; heatmap A6 usa NaN para support=0. |
| Artefato `confused_classes` / worst_k | Pode listar classes com support=0; interpretação correta exige filtro por support (feito em QP3). |

### 9.4 Validade externa

| Ameaça | Situação |
|---|---|
| Dados simulados TEP ≠ planta real | Escopo delimitado (SPEC-000 §2.3); generalização industrial **não** é reivindicada. |
| Só métodos clássicos | Deliberado (§2.2); referência para estudos futuros profundos/híbridos. |
| Baseline ≠ tuning SPEC-006A | Resultados não representam o máximo de cada família sob busca ampliada. |

### 9.5 Reprodutibilidade (transversal)

Mitigações: manifesto, seed, snapshot de ambiente, predições e métricas versionadas (REP-01–06). Residual: `git_dirty: true` no snapshot A4; artefatos A5/A6/análise posteriores ao SHA congelado devem ser commitados em branch dedicada para auditoria completa (GIT-R01–R05). O dry-run permanece marcado `scientific_validity: false`.

### 9.6 Riscos metodológicos aceitos (ACCEPTED RISK)

Riscos **estruturais** que exigiriam novo desenho experimental para eliminação e que, para `exp-a4-v2`, são **aceitos** com mitigação documental (não ocultados):

| ID | Finding origem | Mitigação neste estudo | Risco residual |
|---|---|---|---|
| **AR-1** | MAJOR-02 — val∩teste classes vazias | Limitação no manifesto A3; INV-05 (teste isolado); discussão explícita | Hiperparâmetros não otimizados nas falhas do teste |
| **AR-2** | MAJOR-03 — scorer = acurácia amostral | Publicação multicritério (INV-06/07); ameaça nomeada | Desalinhamento seleção ↔ F1/BA |
| **AR-3** | MAJOR-04 — grids desiguais / SVM linear | Sem claim de esforço igual; YAML versionado | Diferenças misturam família e budget |
| **AR-4** | MINOR-03 — macro C=21 com ausentes | Zeros documentados; heatmap NaN; comparação intra-holdout | Macro ≠ cobertura das 21 falhas |
| **AR-5** | MINOR-04 — semente única / n=11 | SPEC-008 declara unidade e n; H2 run-level não corroborada | Baixo poder; sensibilidade a seed não medida |

---

## 10. Conclusões

1. O benchmark WP1A executou ponta a ponta o protocolo Auditoria→…→Avaliação(+SPEC-008) para os seis modelos sob `exp-a4-v2`, com disjunção de `run_id` e pré-processamento fit-no-treino verificáveis.
2. **QP1–QP5** foram respondidas com evidência em `results/` / `article/` (Seção 6.3).
3. **H1–H4 corroboradas** pelos critérios §4 no holdout; em run-level, **H1 corroborada** (Wilcoxon+Holm, família 3) e **H2 não corroborada** (família 4; nenhum par após Holm) na métrica `run_accuracy` (n=11).
4. Não existe um único “melhor modelo”: RF (F1/MCC), XGB (compromisso), DT (custo mínimo) respondem a objetivos distintos (QP5).
5. Conclusões ficam condicionadas aos **riscos aceitos AR-1–AR-5** (Seção 9.6): cobertura disjunta val/teste, scorer de acurácia, grids desiguais, macro com classes ausentes e poder limitado. Remoção desses riscos exige **novo** `experiment_id` / dataset — não alteração silenciosa de `exp-a4-v2`.
6. Este relatório (A7) alimenta o manuscrito (A8) e a apresentação (A9); números aqui citados não devem ser reescritos sem o CSV correspondente.

---

## 11. Índice de artefatos (rastreabilidade DOC-R03)

| Conteúdo | Caminho |
|---|---|
| Config experimento | `configs/experiments/exp-a4-v2.yaml` |
| Snapshot A4 | `results/metadata/exp-a4-v2__config_snapshot.json` |
| Manifesto A3 | `data/processed/split_manifest_v1.json` |
| Métricas globais A5 | `results/tables/A5_exp-a4-v2__global_metrics.csv` |
| Custo A5 | `results/tables/A5_exp-a4-v2__cost_metrics.csv` |
| Por classe A5 | `results/tables/A5_exp-a4-v2__per_class_metrics.csv` |
| QP3 JSON | `results/tables/A5_exp-a4-v2__qp3_confused_faults.json` |
| Friedman SPEC-008 | `results/tables/A8_exp-a4-v2__friedman.json` |
| Wilcoxon H1/H2 | `results/tables/A8_exp-a4-v2__wilcoxon_H1_family.csv`, `…__wilcoxon_H2_family.csv` |
| Bundle estatístico | `results/metrics/A8_exp-a4-v2__statistics.json` |
| Análise prévia QP/H | `reports/technical/A5_exp-a4-v2_scientific_analysis_QP_H.md` |
| Tabelas/figuras A6 | `article/tables/A6_exp-a4-v2__*`, `article/figures/A6_exp-a4-v2__*` |
| Traceability A6 | `results/metadata/A6_exp-a4-v2__traceability.json` |

---

## 12. Referências normativas e bibliográficas mínimas

1. Documento WP1A — *MEI0028_WP1A_3.pdf* (autoridade máxima do subprojeto).
2. `docs/project/requirements.md`.
3. `docs/specs/SPEC-000-master.md` (e SPEC-001 a SPEC-009).
4. `AGENTS.md` — regras operacionais (MET-*, LEAK-*, DOC-*, EXP-*).
5. `docs/adr/ADR-007-multi-criteria-model-evaluation.md`.
6. Downs, J. J., & Vogel, E. F. (1993). A plant-wide industrial process control problem. *Computers & Chemical Engineering*, 17(3), 245–255. (TEP — referência clássica do processo.)
7. Bibliotecas: Pedregosa et al., scikit-learn; Chen & Guestrin, XGBoost — versões no snapshot de ambiente.

Referências bibliográficas amplas de diagnóstico de falhas / TEP serão expandidas no manuscrito A8.

---

## Apêndice A — Checklist de aceite tocado por A7

| Critério | Status neste documento |
|---|---|
| CA-07 QP1–QP5 explícitas | Cumprido (Seção 6.3) |
| CA-08 H1–H4 avaliadas | Cumprido (Seção 7): cada H com veredito binário corroborada/refutada + box SPEC-008 |
| CA-10 ameaças (4 categorias) | Cumprido em A7 (Seção 9); estrutura completa de 10 seções aplica-se a A8 |
| DOC-R03 rastreabilidade | Cumprido (Seção 11) |
| INV-06 / INV-07 / INV-08 | Respeitados na redação |

---

*Fim do Relatório Técnico A7 — experimento `exp-a4-v2`.*
