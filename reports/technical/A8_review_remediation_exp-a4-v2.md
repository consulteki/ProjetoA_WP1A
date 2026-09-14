# Remediação metodológica — revisão A8 (pós SPEC-008)

| Campo | Valor |
|---|---|
| Papel | Responsável pela remediação metodológica |
| Data | 2026-09-14 |
| Revisão de entrada | `reports/technical/A8_scientific_review_exp-a4-v2_post_spec008.md` |
| Decisão de entrada | Approve with revisions (0 BLOCKER · 4 MAJOR · 4 MINOR) |
| Experimento congelado | `exp-a4-v2` (**não** alterado: dados, split, seeds, predições, métricas, stats, configs) |
| Revisão de saída (adversarial) | `reports/technical/A8_scientific_review_exp-a4-v3_post_remediation.md` |

**Regra:** BLOCKER-01 e BLOCKER-02 permanecem **CLOSED** (sem evidência de regressão).  
**Ações possíveis por finding:** `FIX REQUIRED` | `ACCEPTED RISK` | `ALREADY FIXED`.

---

## Resumo executivo

| Finding | Severidade | Classificação | Status final |
|---|---|---|---|
| MAJOR-01 | MAJOR | **ALREADY FIXED** | CLOSED |
| MAJOR-02 | MAJOR | **ACCEPTED RISK** (AR-1) | TREATED (accepted) |
| MAJOR-03 | MAJOR | **ACCEPTED RISK** (AR-2) | TREATED (accepted) |
| MAJOR-04 | MAJOR | **ACCEPTED RISK** (AR-3) | TREATED (accepted) |
| MINOR-01 | MINOR | **ALREADY FIXED** | CLOSED |
| MINOR-02 | MINOR | **FIX REQUIRED** → corrigido | CLOSED |
| MINOR-03 | MINOR | **ACCEPTED RISK** (AR-4) | TREATED (accepted) |
| MINOR-04 | MINOR | **ACCEPTED RISK** (AR-5) | TREATED (accepted) |

Extras (INFO-02 da revisão anterior): clareza da família Holm H2 (4 pares) aplicada em A7/A8 como polish científico — **CLOSED**.

**Critério de saída pretendido:** 0 BLOCKER; 0 MAJOR não tratados; 0 MINOR não tratados; estruturais só como ACCEPTED RISK documentados.

---

## Finding-by-finding

### MAJOR-01 — A8 conclusões listavam Friedman/Wilcoxon como trabalho futuro

| Campo | Conteúdo |
|---|---|
| **ID** | MAJOR-01 |
| **Severidade** | MAJOR |
| **Descrição** | `manuscript.tex` Conclusões item (ii) ainda pedia “comparações Friedman/Wilcoxon em nível de execução” apesar de SPEC-008 já executada. |
| **Classificação** | **ALREADY FIXED** (antes desta remediação formal; confirmado no texto atual) |
| **Arquivos afetados** | `article/manuscript/manuscript.tex` (+ PDF) |
| **Correção / justificativa** | Item (ii) reescrito para multi-semente / poder Wilcoxon (H2); Friedman não aparece como pendente. |
| **Evidência** | Grep: conclusões citam “replicação multi-semente… H2 permanece não significativa”; corpo já reporta Friedman p=0,015. |
| **Risco residual** | Nenhum para este finding. |
| **Status final** | **CLOSED** |

---

### MAJOR-02 — Val ∩ test class sets empty

| Campo | Conteúdo |
|---|---|
| **ID** | MAJOR-02 → **AR-1** |
| **Severidade** | MAJOR (estrutural) |
| **Descrição** | Com 2 runs/classe no canônico, val e teste têm conjuntos de classes disjuntos; seleção não observa falhas do teste. |
| **Classificação** | **ACCEPTED RISK** |
| **Arquivos afetados** | Documentação: A7 §9.6 / §8 / §10; A8 ameaças + discussão + conclusões. **Não** alterados: `split_manifest_v1.json`, dados, treino. |
| **Correção / justificativa** | Eliminação exigiria novo canônico/split → novo `experiment_id`. Formalizado como AR-1 com mitigação (manifesto, INV-05, discussão) e residual explícito. Confirmado nas seções Threats, Discussão e Conclusões. |
| **Evidência** | Tabelas AR em A7 §9.6; bloco “Riscos metodológicos aceitos” em A8; conclusões condicionam rankings a AR-1–AR-5. |
| **Risco residual** | Hiperparâmetros não otimizados nas falhas avaliadas no teste. |
| **Status final** | **TREATED (ACCEPTED RISK)** |

---

### MAJOR-03 — Selection scorer = sample accuracy

| Campo | Conteúdo |
|---|---|
| **ID** | MAJOR-03 → **AR-2** |
| **Severidade** | MAJOR (estrutural / constructo da seleção) |
| **Descrição** | Grid search usa acurácia na validação; desalinhado de F1/BA sob desbalanceamento e sob AR-1. |
| **Classificação** | **ACCEPTED RISK** |
| **Arquivos afetados** | Só documentação (A7/A8). Código/config de seleção **congelados**. |
| **Correção / justificativa** | Realinhar scorer exigiria novo experimento. AR-2: mitigação por publicação multicritério (INV-06/07) + ameaça nomeada. |
| **Evidência** | A7 §9.1 + §9.6 AR-2; A8 ameaças internas + AR-2; discussão referencia AR-2. |
| **Risco residual** | Seleção não otimiza diretamente as métricas de ranking publicadas. |
| **Status final** | **TREATED (ACCEPTED RISK)** |

---

### MAJOR-04 — Unequal search budgets / SVM linear-only

| Campo | Conteúdo |
|---|---|
| **ID** | MAJOR-04 → **AR-3** |
| **Severidade** | MAJOR (comparabilidade) |
| **Descrição** | GB 2 candidatos vs XGB 8; SVM só linear nesta baseline. |
| **Classificação** | **ACCEPTED RISK** |
| **Arquivos afetados** | Só documentação. `configs/experiments/exp-a4-v2.yaml` **não** alterado. |
| **Correção / justificativa** | Equalizar grids = novo `experiment_id`. AR-3: sem claim de esforço igual; YAML versionado como baseline. |
| **Evidência** | A7 §4.6 / §8 / §9.6; A8 métodos + AR-3 + discussão. |
| **Risco residual** | Diferenças entre famílias misturam algoritmo e budget. |
| **Status final** | **TREATED (ACCEPTED RISK)** |

---

### MINOR-01 — A8 appendix omitia paths SPEC-008

| Campo | Conteúdo |
|---|---|
| **ID** | MINOR-01 |
| **Severidade** | MINOR |
| **Descrição** | Apêndice A sem `friedman.json` / Wilcoxon H1/H2 / `statistics.json`. |
| **Classificação** | **ALREADY FIXED** |
| **Arquivos afetados** | `article/manuscript/manuscript.tex` Apêndice A |
| **Correção / justificativa** | Linhas adicionadas para Friedman, Wilcoxon H1/H2 e bundle estatístico. |
| **Evidência** | Apêndice A contém `\path{results/tables/A8_exp-a4-v2__friedman.json}` e correlatos. |
| **Risco residual** | Nenhum. |
| **Status final** | **CLOSED** |

---

### MINOR-02 — Frases “análises/inferência futuras” (tempo verbal)

| Campo | Conteúdo |
|---|---|
| **ID** | MINOR-02 |
| **Severidade** | MINOR |
| **Descrição** | Texto sugeria que testes de hipótese ainda eram futuros, pós SPEC-008. |
| **Classificação** | **FIX REQUIRED** → **corrigido nesta remediação** |
| **Arquivos afetados** | `article/manuscript/manuscript.tex` (fundamentação TEP); `reports/technical/A7_technical_report.md` §2 |
| **Correção / justificativa** | Presente: testes **devem** / **toda** inferência (incl. SPEC-008) respeita `run_id` (INV-09). |
| **Evidência** | A8: “nem nos testes de hipótese (INV-09; UE-03)”; A7: “toda inferência estatística (incluindo SPEC-008)”. |
| **Risco residual** | Nenhum. |
| **Status final** | **CLOSED** |

---

### MINOR-03 — Macro C=21 com ~10 classes ausentes

| Campo | Conteúdo |
|---|---|
| **ID** | MINOR-03 → **AR-4** |
| **Severidade** | MINOR (constructo; estrutural ao split) |
| **Descrição** | BA/F1 macro deprimidos por zeros de classes ausentes no teste. |
| **Classificação** | **ACCEPTED RISK** |
| **Arquivos afetados** | Documentação AR-4; métricas **não** recalculadas. |
| **Correção / justificativa** | Já divulgado; formalizado como AR-4 com mitigação (NaN no heatmap; comparação intra-holdout). |
| **Evidência** | A7 §9.3 / §9.6; A8 constructo + AR-4; QP2. |
| **Risco residual** | Macro ≠ desempenho médio sobre 21 falhas industriais neste holdout. |
| **Status final** | **TREATED (ACCEPTED RISK)** |

---

### MINOR-04 — Single seed / n=11 power

| Campo | Conteúdo |
|---|---|
| **ID** | MINOR-04 → **AR-5** |
| **Severidade** | MINOR (poder estatístico) |
| **Descrição** | Uma semente; 11 runs; H2 run-level não corroborada. |
| **Classificação** | **ACCEPTED RISK** |
| **Arquivos afetados** | Documentação AR-5; stats **não** reexecutadas com novas seeds. |
| **Correção / justificativa** | Multi-seed exigiria novo experimento. AR-5 liga H2 não-corroborada ao poder limitado. |
| **Evidência** | A7 §6.4 / §9.6; A8 SPEC-008 + AR-5; conclusões. |
| **Risco residual** | Baixo poder; sensibilidade a seed não quantificada. |
| **Status final** | **TREATED (ACCEPTED RISK)** |

---

## BLOCAÇÕES anteriores (não reabertas)

| ID | Status | Nota |
|---|---|---|
| BLOCKER-01 | **CLOSED** | SPEC-008 presente; dual-plane H; sem “suportada” não qualificada. Sem regressão. |
| BLOCKER-02 | **CLOSED** | H3 binária **corroborada** (§4). Sem “parcialmente”. Sem regressão. |

---

## Inventário do que **não** foi alterado (congelado)

- `data/raw`, `data/processed` (split/canônico)
- Seeds / `configs/seeds.yaml` / `configs/experiments/exp-a4-v2.yaml`
- Predições `results/predictions/exp-a4-v2__*`
- Métricas A5 e artefatos SPEC-008 numéricos
- Modelos `models/exp-a4-v2__*`

Alterações desta remediação: **somente** texto A7/A8 (+ rebuild PDF) e este relatório.

---

## Mapa ACCEPTED RISK ↔ seções

| AR | Threats | Discussão | Conclusões |
|---|---|---|---|
| AR-1 | A7 §9.1/9.6; A8 ameaças + AR | A7 §8.4; A8 discussão | A7 §10.5; A8 parágrafo AR |
| AR-2 | A7 §9.1/9.6; A8 | A7 §8.4; A8 | idem |
| AR-3 | A7 §9.2/9.6; A8 | A7 §8.5; A8 | idem |
| AR-4 | A7 §9.3/9.6; A8 | A7 §8.3; A8 | idem |
| AR-5 | A7 §9.2/9.6; A8 | A7 §8.2; A8 | idem |

---

## Próximo passo

Executar Scientific Reviewer **adversarial** comparando esta remediação à revisão `…_post_spec008.md`, produzindo:

`reports/technical/A8_scientific_review_exp-a4-v3_post_remediation.md`

Decisão esperada (se checklist OK): **APPROVE WITH ACCEPTED RISKS**.

*Fim do relatório de remediação.*
