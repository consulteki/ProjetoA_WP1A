# Scientific review — A7/A8 for experiment `exp-a4-v2`

| Field | Value |
|---|---|
| Role | Scientific Reviewer Agent (read-only; no metric/code/retrain changes) |
| Date | 2026-09-14 |
| Scope | Entregas A7 + A8 (+ análise A5 de apoio); experimento oficial `exp-a4-v2` |
| Normative basis | `AGENTS.md`; `docs/specs/SPEC-000-master.md` §§3–4, §11.4, §12–14; SPEC-009; `.agents/prompts/reviewer.md`; skill `scientific-writing` |
| Artifacts reviewed | `reports/technical/A7_technical_report.md`; `article/manuscript/manuscript.tex`; `reports/technical/A5_exp-a4-v2_scientific_analysis_QP_H.md` |
| Traceability spot-check | A5 CSVs/JSON; A6 tables/figures; `configs/experiments/exp-a4-v2.yaml`; `data/processed/split_manifest_v1.json`; `results/metadata/exp-a4-v2__config_snapshot.json` |

---

## Verdict

**Approve with revisions.**

A7 and A8 largely meet the *textual* acceptance surface for CA-07, CA-08, and CA-10 (QP1–QP5 answered; H1–H4 individually judged; manuscript has the 10 required sections; threats cover the four SPEC-000 §14 categories; multicriteria wording respects INV-06/07; no causal feature interpretation — INV-08). Cited headline numbers match versioned A5/A6 artifacts (DOC-R03 spot-check pass).

Unconditional approval is blocked by methodological closures still open for a final scientific deliverable under SPEC-009 / scientific-writing preconditions: **SPEC-008 not executed**, **H3 uses a non-SPEC ternary verdict**, and several **structural protocol threats** (val∩test class disjointness; accuracy selection scorer; unequal search budgets; sample-level H without run-level inference) remain material even though they are disclosed.

Severity tally: **2 BLOCKER · 5 MAJOR · 4 MINOR · 3 INFO**.

---

## Explicit acceptance checks

| Check | Result | Evidence / notes |
|---|---|---|
| **QP1–QP5 answered?** | **PASS** | A7 §6.3; A8 §§ QP1–QP5 under Results. Each QP has an explicit answer grounded in A5/A6 paths. |
| **H1–H4 individually judged?** | **PARTIAL** | A7 §7; A8 “Avaliação de H1–H4”. H1/H2/H4 judged; H3 uses **“parcialmente suportada”**, which is **not** a SPEC-000 §4 outcome (only corroborada/refutada). |
| **Threats cover 4 categories?** | **PASS** | A7 §9.1–9.4; A8 § Ameaças (interna, estatística, constructo, externa) + reproducibility transversal. |
| **Multicriteria (no single-metric “best”)?** | **PASS** | INV-06/07 respected: QP5 trade-off table; H4; cost discussed; no accuracy-only winner. |
| **No causal feature interpretation?** | **PASS** | INV-08 / MET-R07: both texts forbid physical causality from importances/confusions. |
| **Numbers match CSVs?** | **PASS** (with 1 MINOR rounding) | Global Acc/BA/F1/MCC/cost/size match `A5_exp-a4-v2__global_metrics.csv` / cost CSV at reported precision; QP3 means and pair counts match recomputation / `qp3_confused_faults.json`. A8 DT inference **0,002** vs CSV **0.00146** (should be 0,0015 or 0,001). |
| **CA-07** | **Met** (pending wording polish under revisions) | Explicit QP answers with quantitative evidence. |
| **CA-08** | **Not fully met** until H3 binary + H language closure | See BLOCKER-02; MAJOR-01. |
| **CA-10** | **Met** | A8 has §§ Introdução…Referências per SPEC-000 §11.4; threats section present with 4 categories. |
| **SPEC-008 executed?** | **NO** | Declared in A7/A8; must remain flagged — see BLOCKER-01. |
| **DOC-R03** | **Mostly met** | Artifact indices present; residual gaps below. |

---

## Severity-ranked findings

### BLOCKER

#### BLOCKER-01 — SPEC-008 absent while H1–H4 are presented as “suportada”
- **Rules:** SPEC-000 §10, UE-03, INV-09; SPEC-009 §4 inputs; scientific-writing skill *Preconditions* / *Procedure* step 5; EXP-R06.
- **Evidence:** No SPEC-008 artifacts under `results/tables/` for Friedman/Wilcoxon. A7 §7 and A8 Results label H1/H2/H4 **suportada** from **sample-level** holdout aggregates, with a caveat that SPEC-008 is pending.
- **Why blocker:** For final A7/A8 under SPEC-009, statistical comparison is a declared input. Leaving H as “supported” in abstract/conclusions risks readers treating sample-pseudo-replication as confirmed model superiority (INV-09). Disclosure helps but does not close the skill/SPEC-009 precondition.
- **Required action (authors):** Either (A) execute SPEC-008 on run-level metrics and update H veredicts from those tests, **or** (B) rewrite all H labels in abstract, results, and conclusions to a non-inferential formulation, e.g. *“descritivamente consistente com os critérios de SPEC-000 §4 sobre estimativas pontuais do holdout; não confirmada estatisticamente em nível de `run`”*, and remove unqualified “suportada” from high-visibility sections.

#### BLOCKER-02 — H3 verdict “parcialmente suportada” violates SPEC-000 §4 binary outcomes
- **Rules:** SPEC-000 §4 (H3); CA-08.
- **Evidence:** A7 §7 H3; A8 H3; A5 analysis §5 H3 — all say **parcialmente suportada**.
- **Why blocker:** SPEC-000 defines only **corroborada** / **refutada** with explicit criteria. A third state fails CA-08’s “avaliadas explicitamente (corroboradas ou refutadas)”.
- **Required action:** Map evidence to one binary outcome. Suggested: if LR is among lowest-cost models **and** shows reduced F1 on at least some QP3 hard classes present in test → **corroborada**, with a sentence that the second clause is not uniform across all hard classes; else **refutada** with the violated clause named. Do not use “parcial”.

---

### MAJOR

#### MAJOR-01 — H1–H4 from sample-level point estimates without run-level stats (prior finding: **confirmed**)
- **Rules:** UE-01/UE-03, INV-09, MET-R01, EST-04/05.
- **Evidence:** Rankings and H use `A5_exp-a4-v2__global_metrics.csv` (sample-aggregated). Caveat present in A7 §7 / A8 footnote; still used as primary H language.
- **Status:** Confirmed threat; partially mitigated by disclosure; closure tied to BLOCKER-01.

#### MAJOR-02 — Validation ∩ test class sets empty (prior finding: **confirmed**)
- **Rules:** Construct validity of selection (SPEC-000 §7.5, §14.1); limits interpretation of “final hyperparameters”.
- **Evidence:** `split_manifest_v1.json` `class_coverage`: val `{0,1,4,5,7,8,9,12,16,17}` vs test `{2,3,6,10,11,13,14,15,18,19,20}` — intersection empty; `leakage_check.status=passed` for **run_id** only. Documented in A7 §4.3 / §9.1 and A8 methods/threats.
- **Status:** Confirmed; correctly disclosed. Remains an open structural threat for any claim that validation selected configs for the faults evaluated at test.

#### MAJOR-03 — Selection scorer = sample accuracy vs F1/BA targets (prior finding: **confirmed**)
- **Rules:** Misalignment with MET-R06 / INV-06 intent for model *comparison* (selection still allowed on val); weakens link between selection objective and reported ranking metrics.
- **Evidence:** `src/wp1a/experiment/runner.py` default `_default_accuracy` / “grid search on validation accuracy”; A7 §4.6 and A8 threats acknowledge accuracy scorer.
- **Status:** Confirmed; disclosed. Future `experiment_id` should align scorer with F1/BA if class coverage allows.

#### MAJOR-04 — Unequal search budgets (GB vs XGB; SVM linear only) (prior finding: **confirmed**)
- **Rules:** Fairness of family comparison; SPEC-000 INV-03 covers shared split/preprocess, **not** equal search cardinality; still a statistical/construct threat for “family superiority”.
- **Evidence:** `exp-a4-v2.yaml`: GB 2 candidates; XGB 8; SVM `kernel: ["linear"]` only; RF 4; DT 6; LR 3. Disclosed in A7/A8.
- **Status:** Confirmed. Authors must not imply equal optimization effort across families (mostly already avoided — keep/strengthen).

#### MAJOR-05 — Macro metrics over C=21 with ~10 absent test classes (prior finding: **confirmed**)
- **Rules:** SPEC-000 §9.2 (C=21); construct validity (§14.3).
- **Evidence:** Test has 11 classes with support>0 and 10 absent (`per_class_metrics.csv`); BA/F1 depressed vs accuracy. A7/A8 document this; heatmap uses NaN for support=0.
- **Status:** Confirmed; correctly disclosed. Keep prominent in abstract if BA/F1 are lead metrics.

---

### MINOR

#### MINOR-01 — `git_dirty: true` on A4 snapshot (prior finding: **confirmed**)
- **Rules:** INV-10, REP-*, GIT hygiene.
- **Evidence:** A7 header / A8 protocol; `exp-a4-v2__config_snapshot.json` → `"git_dirty": true`.
- **Action:** Record residual reproducibility risk; prefer clean-tree re-snapshot on next official experiment_id (do not rewrite past snapshot silently).

#### MINOR-02 — Single seed (prior finding: **confirmed**)
- **Evidence:** seed 42 only; no `replication_seeds`. Disclosed in A7 §9.2 / A8 threats.
- **Action:** Keep as limitation; optional multi-seed campaign = new experiment_ids.

#### MINOR-03 — A8 Decision Tree inference rounded to 0,002
- **Rules:** DOC-R03.
- **Evidence:** CSV MET-11 = 0.0014557…; A7 correctly ~0.0015; A8 Table global shows **0,002**.
- **Action:** Fix A8 table to 0,0015 (or 0,001) and rebuild PDF.

#### MINOR-04 — MET-03 / MET-04 / MET-06 under-emphasized in A7/A8 narrative tables
- **Evidence:** Present in `A5_…__global_metrics.csv` and A6 global table CSV; A7/A8 display tables omit precision/recall macro and weighted F1.
- **Action:** Optionally add columns or a footnote that full MET-01–07 live in A6/A5 paths (MET-08/09 covered via CM + per-class).

---

### INFO

#### INFO-01 — QP3 support=0 misread (prior finding: **mitigated in A7/A8 text**)
- **Evidence:** `qp3_confused_faults.json` still lists support=0 classes under `systematic_low_f1_faults` / per-model lowest F1. A5 analysis warned; **A7 §6.2 / QP3 and A8 QP3 explicitly filter `support>0`** and refuse to call absent classes “hard”.
- **Residual:** Artifact JSON remains misleading if consumed alone — consider a future evaluation-pipeline note (out of scope for this text-only revision unless authors regenerate A5 with a filter).

#### INFO-02 — A6 package completeness for SPEC-009 §3.1
- Figures/tables `A6_exp-a4-v2__01`…`08` present under `article/`; aligned with A5 sources spot-checked.

#### INFO-03 — Title / structure
- Provisional title matches SPEC-000 §11.4; A8 section order matches the 10 mandatory sections.

---

## Prior adversarial findings — re-verification summary

| Prior finding | Status | Notes |
|---|---|---|
| Val ∩ test class sets empty | **Confirmed** | Manifest `class_coverage`; disclosed in A7/A8. |
| Selection scorer = sample accuracy | **Confirmed** | Runner default accuracy; disclosed. |
| H1–H4 from sample-level estimates without run-level stats | **Confirmed** | Disclosed caveat; still primary H language → BLOCKER-01 / MAJOR-01. |
| Unequal search budgets (GB vs XGB; SVM linear) | **Confirmed** | YAML candidate counts; disclosed. |
| Macro metrics C=21 with ~10 absent test classes | **Confirmed** | Disclosed; construct caveat OK. |
| QP3 support=0 classes misread as hard | **Mitigated in A7/A8** | Text filters support>0; JSON artifact still noisy (INFO-01). |
| `git_dirty: true` | **Confirmed** | Disclosed (MINOR-01). |
| Single seed | **Confirmed** | Disclosed (MINOR-02). |

---

## Traceability gaps (DOC-R03)

| Item | Status |
|---|---|
| Headline Acc / BA / F1_macro / MCC / train / size | Match A5 global CSV at 3 d.p. |
| Confused pairs 10→15 (1451), 3→15 (1002), 18→5 (1001), 13→12 (809) | Match `qp3_confused_faults.json` |
| Mean F1 hard classes 3 / 15 / 10 ≈ 0.184 / 0.252 / 0.283 | Match recomputation from `per_class_metrics.csv` |
| Hyperparameters cited | Match A6 `…__02_hyperparameters.csv` / YAML freeze narrative |
| Dataset 52 / 21 / 42 / 30260 | Match A6 dataset summary |
| A8 DT inference 0,002 | **Gap** (MINOR-03) |
| MET-03/04/06 in prose tables | Present in CSV, not in A7/A8 display tables (MINOR-04) |
| SPEC-008 statistical tables | **Missing** (expected; flagged) |
| Feature-importance tables | Absent (good — no INV-08 risk) |

---

## Methodological threats still open

1. **Internal / construct:** Val and test class supports are disjoint → validation cannot score the faults that define test performance; accuracy scorer further misaligns selection with F1/BA.
2. **Statistical:** No Friedman/Wilcoxon at `run` level; single seed; H currently descriptive only.
3. **Comparability:** Unequal grids and SVM-linear-only baseline limit family-level causal claims about algorithms.
4. **Construct (metrics):** BA/F1 macro average over 21 labels including 10 structural zeros.
5. **Reproducibility residual:** `git_dirty: true` on frozen A4 snapshot.
6. **External:** Unchanged and correctly scoped (simulated TEP; classical methods only).

These are appropriately *named* in A7/A8 threats sections; they are **not resolved**.

---

## Concrete revision requests for A7/A8 authors

1. **Resolve BLOCKER-01:** Run SPEC-008 **or** demote all H “suportada” language in abstract, results, and conclusions to explicitly non-inferential wording; keep a dedicated “pendência SPEC-008” box.
2. **Resolve BLOCKER-02:** Replace H3 “parcialmente suportada” with **corroborada** or **refutada** per SPEC-000 §4, naming which clause drives the decision.
3. **Strengthen H caveats in the abstract** so a skimming reader cannot miss that veredicts are holdout point estimates pending run-level tests (unless SPEC-008 is added).
4. **Keep (do not soften)** disclosures of val/test class disjointness, accuracy selection scorer, unequal budgets, and C=21 absent-class effect.
5. **Fix A8** Decision Tree inference cell (0,0015) and rebuild `manuscript.pdf`.
6. **Optional:** Add MET-03/04/06 to the global metrics display or cite A6 table path for the full MET-01–07 set.
7. **Do not** invent run-level significance, equalize budgets retrospectively, or retune using test (LEAK-R03 / LEAK-R06). New claims require a **new** `experiment_id`.
8. **Do not** interpret confused pairs 10→15 / 3→15 as physical TEP mechanisms (already OK — preserve).

---

## Reviewer checklist (`.agents/prompts/reviewer.md`)

- [x] Experimental unit (`run`) acknowledged where applicable — **yes in text**; statistical tests still sample-level — **open**.
- [x] Evidence test unused for development decisions — **yes** (INV-05 claimed; no post-test retune described).
- [x] Mandatory metrics coverage (MET-01–12) — **artifacts yes**; narrative tables partial (MINOR-04); MET-08/09 via CM/per-class.
- [x] Numbers traceable to versioned results — **yes** (MINOR-03 exception).
- [ ] Related automated tests executed in this review — **not re-run** (out of scope: read-only scientific review of documents).
- [ ] Commit/PR GIT-R05 — **N/A** (document review only).
- [x] AGENTS.md §8 prohibitions in the *writing* — **no violation found** in A7/A8 prose (multicriteria, cost, no causality, no sample-split advocacy).

---

## Bottom line for parent agent

| Item | Value |
|---|---|
| Review file | `reports/technical/A8_scientific_review_exp-a4-v2.md` |
| Verdict | **Approve with revisions** |
| Counts | **2 BLOCKER / 5 MAJOR / 4 MINOR** (+ 3 INFO) |
| Top 5 issues | (1) SPEC-008 missing vs “H suportada”; (2) H3 “parcialmente” non-SPEC; (3) sample-level H / INV-09; (4) val∩test class empty + accuracy scorer; (5) unequal search budgets (GB/XGB/SVM linear) |

*End of scientific review.*

---

## Addendum — resolução dos BLOCKERS (2026-09-14)

Autores aplicaram a opção **(B)** do BLOCKER-01 e a correção binária do BLOCKER-02 em A5 (análise), A7 e A8; PDFs regenerados.

| ID | Resolução |
|---|---|
| **BLOCKER-01** | Removido “suportada” não qualificado. H1–H4 usam **corroborada/refutada** (SPEC-000 §4) com box explícito: *descritivo do holdout; não confirmação run-level; SPEC-008 pendente* (abstract, § hipóteses, conclusões). |
| **BLOCKER-02** | H3 → **corroborada** (ambas cláusulas §4 satisfeitas; refutação não observada). Uniformidade em todas as classes difíceis **não** é exigida por §4. |
| MINOR-03 (extra) | A8 inferência DT corrigida para **0,0015**. |

**Status pós-correção (texto):** BLOCKER-01 e BLOCKER-02 **fechados no plano documental**. SPEC-008 continua **não executada** (MAJOR-01 permanece aberto metodologicamente até análise run-level). Re-review formal recomendado para confirmar checklist.
