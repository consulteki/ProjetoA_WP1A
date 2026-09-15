# SPEC-006A — Busca de Hiperparâmetros (pós-baseline)

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §2.2, §7.5, §8, §12 (INV-03, INV-05), §15; `docs/specs/SPEC-006-benchmark.md`; `docs/adr/ADR-002`, `ADR-005`, `ADR-006` |
| Autoridade superior | `SPEC-000-master.md` e `SPEC-006-benchmark.md` (esta SPEC **não** amplia o escopo da SPEC-000 além do já permitido na §7.5) |
| Skill correspondente | `.agents/skills/ml-training/SKILL.md` (procedimento de seleção; não substitui a skill) |
| Etapa do pipeline | Etapa 5 (extensão da seleção documentada — **após** o baseline A4) |
| Entrega relacionada | A4 (tabela de hiperparâmetros atualizada sob **novo** `experiment_id`) |
| Guardas executáveis | `src/wp1a/tracking/isolation_guard.py` (`ExperimentState`, `assert_test_not_used_for_selection`); `src/wp1a/experiment/runner.py` |
| Testes de rejeição | `tests/methodology/test_test_set_isolation.py` |

Em caso de conflito, prevalecem `SPEC-000-master.md`, as ADRs citadas e, em seguida, `SPEC-006-benchmark.md`. Esta SPEC nunca afrouxa INV-05, LEAK-R03 nem LEAK-R06.

---

## 1. Objetivo

Especificar a **busca formal e ampliada de hiperparâmetros** para os seis modelos obrigatórios (MOD-1..MOD-6), a ser executada **somente depois** de um baseline A4 congelado e versionado, usando exclusivamente treino/validação e produzindo um novo experimento rastreável (ADR-005 / EXP-R04).

O baseline estabelece a referência metodológica e de custo; a busca desta SPEC refina hiperparâmetros **sem** reutilizar o resultado de teste do baseline para guiar a grade (LEAK-R06).

---

## 2. Escopo

### 2.1 Dentro do escopo

1. Definição de espaços de busca versionados por modelo (além do grid reduzido do baseline).
2. Estratégia de busca (grade, amostragem documentada ou equivalente) restrita a treino e/ou validação.
3. Critério de seleção em validação (métrica primária de *seleção*, distinta da síntese multicritério final).
4. Congelamento da configuração escolhida e consulta **única** ao teste sob novo `experiment_id`.
5. Registro completo: seed, git SHA, environment, parâmetros candidatos avaliados, tempos, métricas, tamanho de modelo.
6. Comparação documental baseline vs. configuração tunada (mesmo split A3 e mesmo pré-processamento — INV-03).

### 2.2 Fora do escopo

1. Executar tuning **antes** ou **em substituição** ao baseline A4.
2. Otimização exaustiva / AutoML sem orçamento e justificativa documentados (SPEC-000 §2.2).
3. Uso do conjunto de teste para escolher hiperparâmetros, early stopping, limiares ou features (INV-05, LEAK-R03).
4. Reajuste silencioso de uma configuração já avaliada em teste (LEAK-R06).
5. Avaliação estatística formal entre modelos (SPEC-008) e redação do manuscrito (SPEC-009).
6. Alteração do manifesto de divisão (SPEC-004) ou do pipeline de pré-processamento (SPEC-005).

---

## 3. Pré-condição obrigatória — baseline primeiro

A implementação e a execução desta SPEC **só podem começar** quando **todas** as condições abaixo forem verdadeiras:

| ID | Pré-condição |
|---|---|
| BL-01 | Existe um experimento baseline A4 completo dos 6 modelos sob SPEC-006 (ex.: `exp-a4-v2`), com artefatos em `results/metrics/`, `results/tables/` e `models/`. |
| BL-02 | O baseline referencia o mesmo dataset canônico (SPEC-002), manifesto A3 (SPEC-004) e preprocessor (SPEC-005) que serão reutilizados no tuning. |
| BL-03 | O baseline está congelado: hiperparâmetros finais e métricas de teste do baseline **não** entram como sinais de otimização da nova busca (podem ser citados apenas como referência pós-hoc na documentação). |
| BL-04 | Foi aberto um **novo** `experiment_id` (ex.: `exp-a4-tune-v1`) em `configs/experiments/` — nunca sobrescrever o baseline (EXP-R04, ADR-005). |

Se qualquer pré-condição falhar, o agente **interrompe** e não inicia a busca (LEAK-R07 / workflow AGENTS.md §3).

---

## 4. Requisitos

### 4.1 Protocolo compartilhado (INV-03)

1. Os 6 modelos usam o **mesmo** manifesto de divisão e o **mesmo** pipeline de pré-processamento do baseline.
2. Todos passam pelo `ExperimentRunner` (select → freeze → fit_final → predict_test).
3. É proibido criar caminho de dados ou split “só para o modelo X”.

### 4.2 Isolamento do teste (INV-05)

1. A busca usa **apenas** treino e/ou validação (ou CV interna ao treino).
2. O teste é consultado **uma única vez** por modelo, **após** `freeze()` da configuração escolhida.
3. Observar métricas de teste do baseline **não** autoriza estreitar a grade ou repetir a busca na mesma configuração; isso exige novo experimento e justificativa explícita de que a grade foi definida *a priori* (sem realimentação do teste).

### 4.3 Espaço de busca e orçamento

1. O espaço de busca por modelo DEVE estar versionado em `configs/experiments/<experiment_id>.yaml` (e pode derivar de `configs/models.yaml`).
2. O orçamento (nº máximo de candidatos, tempo wall-clock, ou nº de trials) DEVE ser declarado no mesmo arquivo de configuração.
3. A busca NÃO precisa ser exaustiva sobre `models.yaml`; deve ser **documentada e justificável** (SPEC-000 §2.2).
4. Ampliações em relação ao baseline (ex.: incluir `kernel: rbf` no SVM, grids maiores de RF/XGB) DEVEM ser listadas explicitamente no config do experimento de tuning.

### 4.4 Critério de seleção (validação)

1. A métrica usada para **escolher** o candidato em validação DEVE ser declarada no config (recomendado: F1 macro ou acurácia balanceada — nunca usar só acurácia simples como único critério de seleção sem justificar).
2. Empates: regra determinística documentada (ex.: maior F1 macro; em empate, menor tempo de treino; em novo empate, menor `model_id` lexicográfico).
3. A seleção em validação **não** substitui o relatório multicritério no teste (INV-06, INV-07, SPEC-007).

### 4.5 Reprodutibilidade e proveniência (EXP-R01)

Cada trial e a configuração final DEVEM registrar:

| Campo | Obrigatório |
|---|---|
| `experiment_id` / `model_id` | sim |
| `seed` | sim |
| `git_sha` (+ dirty flag) | sim |
| `environment` (python, sklearn, xgboost, etc.) | sim |
| `parameters` (candidato e congelados) | sim |
| scores de validação por candidato | sim |
| `time` (seleção, treino, inferência — MET-10/11) | sim |
| métricas de teste (MET-01..MET-09) após freeze | sim |
| `model_size` (MET-12) | sim |
| referência ao baseline (`baseline_experiment_id`) | sim |

### 4.6 Relação com o baseline

1. O relatório/tabela de hiperparâmetros do tuning DEVE citar `baseline_experiment_id`.
2. É permitido publicar lado a lado métricas baseline vs. tunado **no teste**, desde que ambos tenham sido obtidos com consulta única pós-freeze em seus respectivos experimentos.
3. É **proibido** concluir que o tuning “melhorou” o modelo usando apenas acurácia simples (INV-06).

---

## 5. Procedimento (ordem fixa)

1. Verificar BL-01..BL-04.
2. Criar `configs/experiments/<novo_experiment_id>.yaml` com `search_spaces`, orçamento, métrica de seleção e `baseline_experiment_id`.
3. Para cada MOD-1..MOD-6:
   1. Expandir candidatos (treino/val apenas).
   2. Avaliar candidatos via `ExperimentRunner.select_hyperparameters`.
   3. `freeze` → `fit_final` → `predict_test` (uma vez).
   4. Persistir modelo, predições, record JSON e tabelas.
4. Gerar tabela comparativa baseline × tunado (insumo de hiperparâmetros / A4 atualizado).
5. Não reabrir o teste do experimento tunado para nova busca.

---

## 6. Entradas e saídas

### Entradas

- Baseline A4 completo (SPEC-006), ex.: `exp-a4-v2`.
- Conjuntos pré-processados (SPEC-005) e manifesto A3 (SPEC-004).
- Configuração do experimento de tuning em `configs/experiments/`.
- Semente em `configs/seeds.yaml` (`per_stage.model_init` / `cross_validation`).

### Saídas

- Novo `experiment_id` com:
  - `models/<experiment_id>__<model_id>.joblib`
  - `results/predictions/<experiment_id>__<model_id>__test_pred.csv`
  - `results/metrics/<experiment_id>__<model_id>__record.json`
  - `results/tables/<experiment_id>__metrics_summary.csv`
  - `results/tables/<experiment_id>__hyperparameters.csv`
  - `results/metadata/<experiment_id>__config_snapshot.json`
- Tabela explícita baseline vs. tunado (mesmo protocolo de split/preprocess).

---

## 7. Critérios de aceite

| ID | Critério | Evidência |
|---|---|---|
| CA-006A-01 | Baseline A4 existente e referenciado (`baseline_experiment_id`). | Config snapshot + artefatos do baseline. |
| CA-006A-02 | Novo `experiment_id` distinto do baseline (EXP-R04). | `configs/experiments/` + `results/`. |
| CA-006A-03 | Busca sem acesso ao teste; freeze antes de `predict_test` (INV-05). | Logs do runner + `tests/methodology/test_test_set_isolation.py`. |
| CA-006A-04 | Seis modelos sob o mesmo split e preprocessor (INV-03). | Metadata idêntica de manifesto/preprocessor. |
| CA-006A-05 | Espaço de busca, orçamento e métrica de seleção documentados *a priori*. | YAML do experimento. |
| CA-006A-06 | Records com seed, git SHA, environment, parameters, time, metrics, model size. | `results/metrics/*__record.json`. |
| CA-006A-07 | Nenhuma conclusão de “melhor” baseada só em acurácia (INV-06); custo reportado (INV-07). | Tabela comparativa multicritério. |

---

## 8. Proibições específicas desta SPEC

1. **PROIBIDO** iniciar SPEC-006A sem baseline A4 completo (BL-01).
2. **PROIBIDO** usar métricas de teste do baseline (ou de trials anteriores em teste) para definir ou reduzir a grade da busca atual.
3. **PROIBIDO** sobrescrever artefatos do baseline.
4. **PROIBIDO** early stopping / selection com base no teste.
5. **PROIBIDO** declarar o tuning como “resultado oficial” do artigo sem atualizar a tabela de hiperparâmetros e sem novo `experiment_id` auditável.

---

## 9. Rastreabilidade

| Elemento desta SPEC | Origem de autoridade |
|---|---|
| Pré-condição baseline-first; novo `experiment_id` | SPEC-006; ADR-005; AGENTS.md EXP-R04 |
| Seleção só em treino/val; freeze antes do teste | SPEC-000 §7.5, INV-05; ADR-002; AGENTS.md MET-R05, LEAK-R03, LEAK-R06 |
| Protocolo único nos 6 modelos | SPEC-000 INV-03; ADR-006; SPEC-006 |
| Busca documentada, não exaustiva obrigatória | SPEC-000 §2.2 |
| Métricas e custo no mesmo run | SPEC-000 §9.3 (MET-01..MET-12); INV-06, INV-07; SPEC-007 |
| Reprodutibilidade (seed, versões, SHA) | SPEC-000 §15; ADR-003; AGENTS.md EXP-R01 |
| Entrega / insumos de hiperparâmetros | SPEC-000 §11.1–11.2 (A4, insumo 2); SPEC-009 |

Cadeia resumida:

`WP1A` → `requirements.md` → `SPEC-000-master.md` §7.5 / INV-03 / INV-05 → `SPEC-006-benchmark.md` (baseline A4) → **esta SPEC-006A** (tuning pós-baseline) → `.agents/skills/ml-training/SKILL.md` → `src/wp1a/experiment/` + `src/wp1a/training/`.
