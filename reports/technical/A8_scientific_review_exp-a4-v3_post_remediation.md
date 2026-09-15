# Scientific review (post-remediation) — A7/A8 for experiment `exp-a4-v2`

| Field | Value |
|---|---|
| Role | Scientific Reviewer Agent (**adversarial**; document/artifact review only) |
| Date | 2026-09-14 |
| Scope | Re-review after authors’ remediation of post-SPEC-008 findings |
| Prior review (baseline) | `reports/technical/A8_scientific_review_exp-a4-v2_post_spec008.md` |
| Remediation report | `reports/technical/A8_review_remediation_exp-a4-v2.md` |
| Normative basis | `AGENTS.md`; SPEC-000 INV-06/07/08/09, DOC-R03, CA-07/08/10, EST-01..05, §14; SPEC-008/009; `.agents/prompts/reviewer.md` |
| Documents re-reviewed | `reports/technical/A7_technical_report.md`; `article/manuscript/manuscript.tex` |
| SPEC-008 spot-check | `results/tables/A8_exp-a4-v2__{friedman,wilcoxon_H1_family,wilcoxon_H2_family}.*`; A5 `global_metrics.csv` (unchanged; **not** re-run) |

---

## Verdict

**APPROVE WITH ACCEPTED RISKS**

All corrective findings from the prior review (MAJOR-01, MINOR-01, MINOR-02) are **CLOSED**. Structural findings (MAJOR-02..04, MINOR-03..04) are **TREATED AS ACCEPTED RISK** (AR-1..AR-5) with mitigation, residual, and impact stated in Threats, Discussion, and Conclusions of both A7 and A8. Prior BLOCKER-01/02 remain **CLOSED** (no regression). Experimental freeze for `exp-a4-v2` is untouched: no new metrics, splits, seeds, or re-tuned claims.

Severity tally of **remaining untreated** issues: **0 BLOCKER · 0 MAJOR · 0 MINOR**.

Accepted risks AR-1..AR-5 remain **on the books** (documented, not untreated).

---

## Finding disposition vs prior review

| Prior ID | Prior severity | Authors’ class | Reviewer disposition | Evidence |
|---|---|---|---|---|
| BLOCKER-01 | BLOCKER | (closed prior) | **CLOSED** — no reopen | SPEC-008 present; dual-plane H; no unqualified “suportada”; no “parcialmente” |
| BLOCKER-02 | BLOCKER | (closed prior) | **CLOSED** — no reopen | H3 = **corroborada** (§4); no “parcialmente suportada” |
| MAJOR-01 | MAJOR | ALREADY FIXED | **CLOSED** | A8 Conclusões (ii) = multi-semente / poder Wilcoxon (H2); **not** “fazer Friedman/Wilcoxon” |
| MAJOR-02 | MAJOR | ACCEPTED RISK → AR-1 | **TREATED AS ACCEPTED RISK** | A7 §9.1/9.6 + §8 + §10.5; A8 ameaças + AR block + discussão + conclusões; residual explicit |
| MAJOR-03 | MAJOR | ACCEPTED RISK → AR-2 | **TREATED AS ACCEPTED RISK** | Scorer = accuracy disclosed; AR-2 mitigation (INV-06/07) + residual; not softened |
| MAJOR-04 | MAJOR | ACCEPTED RISK → AR-3 | **TREATED AS ACCEPTED RISK** | Unequal budgets / SVM linear; no equal-effort claim; AR-3 residual |
| MINOR-01 | MINOR | ALREADY FIXED | **CLOSED** | Apêndice A lists Friedman JSON, Wilcoxon H1/H2 paths, `statistics.json` |
| MINOR-02 | MINOR | FIX → corrected | **CLOSED** | A8: “nem nos testes de hipótese (INV-09…)”; A7 §2: “toda inferência estatística (incluindo SPEC-008)” — present tense |
| MINOR-03 | MINOR | ACCEPTED RISK → AR-4 | **TREATED AS ACCEPTED RISK** | C=21 / absent classes in construct threats + AR-4 + Discussion |
| MINOR-04 | MINOR | ACCEPTED RISK → AR-5 | **TREATED AS ACCEPTED RISK** | Single seed / n=11; linked to H2 non-corroboration; AR-5 residual |
| INFO-02 (polish) | INFO | applied | **CLOSED** (not a corrective gate) | H2 family = **all 4 pairs** fail Holm; A7 §7 H2 + A8 SPEC-008 / box explícitos |

**No STILL OPEN / REGRESSED findings.**

---

## ACCEPTED RISKS still on the books (AR-1..AR-5)

These are **not** untreated issues. They are formalized risks for frozen `exp-a4-v2`.

| ID | Origin | Summary | Residual (authors) | Softened / hidden? |
|---|---|---|---|---|
| **AR-1** | MAJOR-02 | Val ∩ test class sets empty | HPs not optimized on test faults | **No** — “não mitigada estruturalmente” |
| **AR-2** | MAJOR-03 | Selection scorer = sample accuracy | Selection ↔ F1/BA misalignment | **No** |
| **AR-3** | MAJOR-04 | Unequal search budgets / SVM linear | Family diffs mix algorithm + budget | **No** |
| **AR-4** | MINOR-03 | Macro C=21 with ~10 absent classes | Macro ≠ industrial coverage of 21 faults | **No** |
| **AR-5** | MINOR-04 | Single seed / n=11 | Low power; seed sensitivity unmeasured | **No** |

Formalization check (adversarial):

| Requirement | A7 | A8 |
|---|---|---|
| AR-1..AR-5 named | §9.6 table | § Ameaças subsection “Riscos metodológicos aceitos” |
| Impact in Discussion | §8 items 2–5 + closing sentence | Discussão paragraph on AR-1–AR-5 |
| Impact in Conclusions | §10 item 5 | Conclusões paragraph conditioning rankings/H on AR-1–AR-5 |
| Residual stated | Yes (table column) | Yes (emph Residual per AR) |
| Threats not hidden | §9.1–9.4 keep structural wording | Internal/statistical/construct unchanged in substance |
| Freeze not altered to “fix” risks | Explicit: new `experiment_id` required | Explicit: none “resolvido” by changing frozen protocol |

---

## FIX-item verification (prior corrective asks)

| Item | Required | Status |
|---|---|---|
| No stale “Friedman as future work” | Rewrite A8 future-work (ii) | **PASS** — (ii) multi-seed / Wilcoxon power for H2 |
| Appendix SPEC-008 paths | DOC-R03 for manuscript consumers | **PASS** — Friedman, Wilcoxon H\*, `statistics.json` |
| Present-tense INV-09 | No “análises/inferência futuras” | **PASS** — A7 §2 + A8 fundamentação |
| H2 Holm family clarity (all 4 pairs) | Optional polish / INFO-02 | **PASS** — “nenhum dos quatro pares” in A7/A8 |

---

## Experimental freeze

| Check | Result |
|---|---|
| Experiment ID still `exp-a4-v2` | **Yes** |
| New metrics / re-tuned H claims | **None found** |
| New seeds / splits claimed | **None** (still seed 42; n_units=11) |
| SPEC-008 numbers vs artifacts | **Match** (spot-check): Friedman χ²≈14.079, p≈0.0151, reject; H1 3/3 `significant_holm=True`; H2 4/4 `False` |
| A5 headline numbers | **Unchanged** (e.g. XGB Acc ≈0.618; RF F1≈0.357 / MCC≈0.597; DT inf ≈0.0015) |
| Authors claim of doc-only remediation | **Consistent** with re-review (no demand to re-run experiments) |

---

## Explicit acceptance checklist

| Check | Result | Notes |
|---|---|---|
| **QP1–QP5 answered?** | **PASS** | A7 §6.3; A8 Results |
| **H1–H4 (§4 plane)?** | **PASS** | Binary corroborada only |
| **H1–H4 (run-level)?** | **PASS** | H1 corroborada; H2 não; H3/H4 N/A as primary Wilcoxon |
| **Threats — 4 categories?** | **PASS** | + reproducibility transversal + AR block |
| **SPEC-008 executed?** | **YES** (prior; unchanged) | Artifacts versioned |
| **Numbers match?** | **PASS** | Spot-check OK |
| **Metric = `run_accuracy`?** | **PASS** | Disclosed |
| **Single seed/split?** | **PASS** | AR-5 |
| **INV-06/07 multicriteria?** | **PASS** | |
| **INV-08 no causality?** | **PASS** | |
| **INV-09 / EST-04/05?** | **PASS** | Present-tense prose + run-level tests |
| **CA-07 / CA-08 / CA-10** | **Met** | |
| **DOC-R03** | **PASS** | Prior appendix gap closed |
| **AR formalization complete?** | **PASS** | AR-1..AR-5 in A7 and A8 |
| **Prior MAJOR/MINOR all treated?** | **YES** | Closed or accepted risk |

---

## Severity tally (remaining *untreated*)

| Severity | Count |
|---|---|
| BLOCKER | **0** |
| MAJOR (untreated) | **0** |
| MINOR (untreated) | **0** |
| INFO (optional polish left open) | **0** material |

On the books but **not** untreated: **AR-1, AR-2, AR-3, AR-4, AR-5**.

---

## Reviewer checklist (`.agents/prompts/reviewer.md`)

- [x] Experimental unit = run where applicable (INV-09)
- [x] Test unused for development decisions (claimed; freeze preserved)
- [x] Mandatory metrics narrative respects multicriteria + cost (INV-06/07)
- [x] Numbers traceable to versioned `results/` (DOC-R03; appendix complete)
- [ ] Related automated tests re-run in this review — **not re-run** (scientific doc review only; per mandate)
- [ ] Commit/PR GIT-R05 — **N/A**
- [x] AGENTS.md §8 prohibitions in writing — **no violation**; threats not hidden

---

## Bottom line for parent agent

| Item | Value |
|---|---|
| Review file | `reports/technical/A8_scientific_review_exp-a4-v3_post_remediation.md` |
| Verdict | **APPROVE WITH ACCEPTED RISKS** |
| Untreated counts | **0 BLOCKER / 0 MAJOR / 0 MINOR** |
| Prior MAJOR/MINOR all treated? | **YES** (CLOSED or TREATED AS ACCEPTED RISK) |
| ACCEPTED RISKS on books | **AR-1..AR-5** |
| Prior BLOCKER-01/02 | **CLOSED** (no regression) |

*End of post-remediation scientific review (adversarial).*
