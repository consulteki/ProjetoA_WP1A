# Scientific review (post SPEC-008) — A7/A8 for experiment `exp-a4-v2`

| Field | Value |
|---|---|
| Role | Scientific Reviewer Agent (read-only; no A7/A8/code changes) |
| Date | 2026-09-14 |
| Scope | Re-review after SPEC-008 execution + A7/A8 incorporation of run-level stats |
| Prior review | `reports/technical/A8_scientific_review_exp-a4-v2.md` (+ addendum closing text BLOCKERs) |
| Normative basis | `AGENTS.md`; SPEC-000 §§3–4, §10 (EST-01..05), §12 (INV-06/07/08/09), §13 (CA-07/08/10), §14; SPEC-008/009; `.agents/prompts/reviewer.md`; skill `statistical-analysis` |
| Documents | `reports/technical/A7_technical_report.md`; `article/manuscript/manuscript.tex` |
| SPEC-008 spot-check | `results/metrics/A8_exp-a4-v2__statistics.json`; `results/tables/A8_exp-a4-v2__{friedman,run_metric_summary,wilcoxon_H1_family,wilcoxon_H2_family,hypothesis_from_stats,limitations}.*`; code `src/wp1a/statistics/` |
| A5 spot-check | `results/tables/A5_exp-a4-v2__global_metrics.csv`; QP3 JSON |

---

## Verdict

**Approve with revisions.**

SPEC-008 is **executed and versioned**. A7 §6.4 / §7 and A8 Results correctly report a **two-plane** hypothesis evaluation: SPEC-000 §4 binary holdout criteria **and** run-level Friedman/Wilcoxon+Holm on `run_accuracy` (n=11). Prior **BLOCKER-01** (SPEC-008 absent / unqualified “suportada”) and **BLOCKER-02** (H3 “parcialmente suportada”) are **closed**. Headline A5 numbers and SPEC-008 statistics match artifacts (DOC-R03). INV-06/07/08 respected in prose; INV-09 respected in code and reported tests (unit = `run_id`, no sample-level independence).

Unconditional approval is withheld for **one factual inconsistency in A8 conclusions** (future-work still lists Friedman/Wilcoxon as if not done) plus residual **structural threats** that remain correctly disclosed but scientifically material. No new BLOCKERs.

Severity tally: **0 BLOCKER · 4 MAJOR · 4 MINOR · 3 INFO**.

---

## Explicit acceptance checklist

| Check | Result | Evidence / notes |
|---|---|---|
| **QP1–QP5 answered?** | **PASS** | A7 §6.3; A8 §§ QP1–QP5. Grounded in A5/A6 paths; QP3 filters `support>0`. |
| **H1–H4 (§4 plane)?** | **PASS** | Binary **corroborada** only (no “parcialmente suportada”). H3 binary **corroborada** with both §4 clauses argued. |
| **H1–H4 (run-level plane)?** | **PASS** | H1 Wilcoxon family Holm: all 3 pairs significant → **corroborada**. H2 family: **no** pair significant after Holm → **não corroborada**. H3/H4: N/A as primary Wilcoxon (stated). |
| **Threats — 4 categories?** | **PASS** | A7 §9.1–9.4; A8 Ameaças (interna, estatística, constructo, externa) + reproducibility transversal. |
| **SPEC-008 executed?** | **YES** | Artifacts under `results/tables/A8_*` + `results/metrics/A8_*__statistics.json`; A7 §6.4; A8 subsection “Análise estatística (SPEC-008)”. |
| **Numbers match?** | **PASS** | Friedman χ²≈14.079, p≈0.0151, n_units=11, reject H0; H1/H2 family tables; run_accuracy means; A5 Acc/BA/F1/MCC/cost (incl. DT inf. **0,0015**). |
| **Metric disclosed as `run_accuracy`?** | **PASS** | Explicit in A7 table + A8 SPEC-008 subsection; limitations JSON states F1/MCC not used as Friedman blocks. |
| **Single seed/split declared?** | **PASS** | A7 §6.4 / §9.2; A8 SPEC-008 + ameaças; `limitations.json`. |
| **Multicriteria (INV-06/07)?** | **PASS** | QP5 trade-offs; H4; cost always present; no accuracy-only winner. |
| **No causality (INV-08)?** | **PASS** | Confused pairs framed as classifier behavior; no feature→physics claims. |
| **INV-09 / EST-04/05?** | **PASS** | Code aggregates by `run_id` before Friedman/Wilcoxon; Holm within H families; prose forbids sample-as-unit. |
| **CA-07** | **Met** | Explicit QP answers with quantitative evidence. |
| **CA-08** | **Met** | Each H judged corroborada/refutada on §4; run-level plane reported separately where applicable. |
| **CA-10** | **Met** | A8 has 10 mandatory sections + threats with 4 categories. |
| **DOC-R03** | **Mostly met** | Indices in A7 include A8 paths; A8 appendix still omits SPEC-008 files (MINOR). |
| **Prior BLOCKER-01 closed?** | **YES** | SPEC-008 present; H language uses corroborada/refutada with dual-plane box; no unqualified “suportada”. |
| **Prior BLOCKER-02 closed?** | **YES** | No “parcialmente suportada”; H3 = **corroborada** (§4). |

---

## SPEC-008 code & artifact spot-check

### Code (`src/wp1a/statistics/`)

| Requirement | Status |
|---|---|
| Experimental unit = `run_id` | **OK** — `per_run_metric_table` groups by `run_id`; Friedman/Wilcoxon operate on wide run×model table |
| Primary metric = `run_accuracy` | **OK** — `PRIMARY_METRIC`; F1/MCC per run not used as blocks |
| Holm correction | **OK** — `holm_adjust` + within-H families in `interpret_hypotheses_from_tests` |
| No sample-level tests | **OK** — aggregation before tests; `assert_not_sample_level` guard; disclaimer forbids sample-level |
| EST-04 declaration | **OK** — every test payload includes `experimental_unit` + `n_units` |

### Numbers (prose ↔ artifacts)

| Claim | Artifact | Match |
|---|---|---|
| n_units=11, metric=`run_accuracy` | `statistics.json` / `friedman.json` | Yes |
| Friedman χ²=14,079; p≈0,015; reject H0 | `friedman.json` (14.0789…, 0.015115…) | Yes (A7 reports 0,0151; A8 0,015) |
| H1: 3/3 significant Holm | `wilcoxon_H1_family.csv` (all `significant_holm=True`) | Yes |
| H2: not all / none significant Holm | `wilcoxon_H2_family.csv` (all `False`) | Yes (“nenhum par”) |
| Means RF/XGB/GB/DT/LR/SVM ≈ 0.635/0.630/0.614/0.579/0.313/0.287 | `run_metric_summary.csv` | Yes |
| Single seed/split + run_accuracy disclosure | `limitations.json` | Yes |
| A5 XGB Acc 0.618; RF F1 0.357 / MCC 0.597; DT inf 0.0015 | `A5_…__global_metrics.csv` | Yes (A7 + A8 tables) |
| QP3 pairs 10→15 (1451), 3→15 (1002), … | `qp3_confused_faults.json` | Yes |

---

## Severity-ranked findings

### BLOCKER

*None.* Prior BLOCKER-01 and BLOCKER-02 are closed.

---

### MAJOR

#### MAJOR-01 — A8 conclusions still list Friedman/Wilcoxon as *future work*
- **Rules:** DOC consistency with executed SPEC-008; risk of readers treating §Resultados as incomplete.
- **Evidence:** `manuscript.tex` Conclusões: “Trabalhos futuros incluem: … (ii) comparações Friedman/Wilcoxon em nível de execução” while the same manuscript already reports Friedman p=0,015 and Wilcoxon+Holm families.
- **Required action:** Rewrite future-work (ii) to what is *still* open — e.g. multi-seed / multi-split replication, larger `n_units`, or power for H2 contrasts — not “perform run-level Friedman/Wilcoxon” as if absent.

#### MAJOR-02 — Val ∩ test class sets empty (prior; **confirmed, disclosed**)
- **Rules:** Construct/internal validity of selection (SPEC-000 §7.5, §14).
- **Evidence:** Manifest class coverage disjoint; A7 §4.3 / §9.1; A8 methods/threats.
- **Status:** Open structural threat; correctly disclosed. Do not soften.

#### MAJOR-03 — Selection scorer = sample accuracy (prior; **confirmed, disclosed**)
- **Rules:** Misalignment with F1/BA targets under imbalance / class mismatch.
- **Evidence:** A7 §4.6 / §9.1; A8 ameaças internas.
- **Status:** Open; disclosed. Future `experiment_id` may realign scorer.

#### MAJOR-04 — Unequal search budgets (prior; **confirmed, disclosed**)
- **Evidence:** GB 2 vs XGB 8 candidates; SVM linear-only; discussed in A7/A8.
- **Status:** Open fairness/comparability threat; keep wording that avoids equal-effort family claims.

---

### MINOR

#### MINOR-01 — A8 appendix omits SPEC-008 artifact paths
- **Rules:** DOC-R03 completeness for manuscript consumers.
- **Evidence:** Apêndice A lists A5/A6/A7 but not `A8_exp-a4-v2__friedman.json`, Wilcoxon H1/H2 CSVs, or `statistics.json` (A7 index already includes them).
- **Action:** Add SPEC-008 rows to the appendix table.

#### MINOR-02 — Stale “análises futuras” / “inferência futura” phrasing
- **Evidence:** A8 fundamentação: “nem (em análises futuras) em testes de hipótese”; A7 §2: “qualquer inferência estatística futura”.
- **Action:** Rephrase to present tense (tests *must* respect `run_id`), now that SPEC-008 is executed.

#### MINOR-03 — Macro metrics C=21 with ~10 absent test classes (prior; **confirmed, disclosed**)
- Keep prominent when BA/F1 are lead metrics; already OK in QP2/threats.

#### MINOR-04 — Single seed / n=11 power (prior; **confirmed, disclosed**)
- Correctly linked to H2 non-corroboration at run level; keep as limitation, not as excuse to invent significance.

---

### INFO

#### INFO-01 — QP3 JSON still lists support=0 under systematic/low-F1 helpers
- A7/A8 prose correctly filters `support>0`. Residual artifact noise if JSON consumed alone.

#### INFO-02 — H2 family: *all* four pairs fail Holm (not only vs DT)
- Prose says “nenhum par” (correct) and “sobretudo vs DT” (interpretive emphasis on small mean diffs vs DT). Optional clarity: note that Holm over 4 pairs also drops RF/XGB vs LR in the H2 family, unlike the 3-pair H1 family.

#### INFO-03 — A6 package / structure
- Figures/tables and A8 10-section structure remain adequate for CA-10 / SPEC-009 surface.

---

## Prior BLOCKER / MAJOR disposition

| Prior ID | Status post SPEC-008 |
|---|---|
| BLOCKER-01 (SPEC-008 absent / “suportada”) | **Closed** — SPEC-008 executed; dual-plane H language |
| BLOCKER-02 (H3 “parcialmente”) | **Closed** — H3 **corroborada** (§4 binary) |
| MAJOR sample-level H without run stats | **Closed as blocker threat** for final deliverable; §4 plane remains descriptive; run-level plane now present for H1/H2 |
| MAJOR val∩test / accuracy scorer / unequal budgets / C=21 zeros | **Still open** (disclosed) → MAJOR-02..04 + MINOR-03 |
| MINOR DT inference 0,002 | **Closed** — A8 table shows 0,0015 |
| MINOR single seed / git_dirty | **Still open** (disclosed) |

---

## Concrete revision requests (authors)

1. **Fix A8 Conclusões future-work (ii)** so it does not imply Friedman/Wilcoxon are still pending (MAJOR-01). Rebuild `manuscript.pdf`.
2. **Add SPEC-008 paths** to A8 Apêndice A (MINOR-01).
3. **Optional wording polish:** present-tense INV-09 sentences (MINOR-02); one sentence clarifying H2 Holm family size vs H1 (INFO-02).
4. **Keep (do not soften)** disclosures of val/test class disjointness, accuracy selection scorer, unequal budgets, C=21 absent-class effect, single seed, and `run_accuracy` ≠ F1/MCC for run-level tests.
5. **Do not** re-tune on test, invent multi-seed significance, or claim H2 run-level corroboration (LEAK-R03/R06; INV-09). New claims → new `experiment_id`.

---

## Reviewer checklist (`.agents/prompts/reviewer.md`)

- [x] Experimental unit (`run`) where applicable — **yes** in tests and prose (INV-09).
- [x] Test unused for development decisions — **yes** (claimed; no post-test retune described).
- [x] Mandatory metrics MET-01–12 — artifacts yes; narrative tables emphasize Acc/BA/F1/MCC/cost (MET-03/04/06 still mainly in CSV).
- [x] Numbers traceable to versioned results — **yes** (appendix gap MINOR-01).
- [ ] Related automated tests re-run in this review — **not re-run** (document/artifact scientific review only).
- [ ] Commit/PR GIT-R05 — **N/A**.
- [x] AGENTS.md §8 prohibitions in writing — **no violation** found (multicriteria, cost, no causality, no sample-level inference advocacy).

---

## Bottom line for parent agent

| Item | Value |
|---|---|
| Review file | `reports/technical/A8_scientific_review_exp-a4-v2_post_spec008.md` |
| Verdict | **Approve with revisions** |
| Counts | **0 BLOCKER / 4 MAJOR / 4 MINOR** (+ 3 INFO) |
| Prior BLOCKER-01/02 | **Closed** |
| Top issues | (1) A8 future-work still lists Friedman/Wilcoxon; (2) val∩test class empty; (3) accuracy selection scorer; (4) unequal search budgets; (5) A8 appendix missing SPEC-008 paths |

*End of post-SPEC-008 scientific review.*
