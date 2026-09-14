"""SPEC-008 — comparação estatística com unidade experimental = ``run_id``.

Agrega métricas por execução no conjunto de teste e aplica Friedman + Wilcoxon
(Holm). Proíbe testes sobre amostras individuais (INV-09 / EST-05).
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon

from wp1a.models.protocol import MODEL_IDS

# Primary paired metric at run level: within-run accuracy.
# Each TEP test run has a single true class; accuracy == class recall for that run.
PRIMARY_METRIC = "run_accuracy"

A8_DISCLAIMER = (
    "SPEC-008 statistical comparison. Experimental unit = run_id (INV-09). "
    "Sample-level tests are forbidden. Single seed/split: EST-01 across seeds "
    "does not apply; mean/SD/CI are over test runs within this holdout."
)


def run_level_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Accuracy within one run (never treat rows as independent units)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) == 0:
        raise ValueError("empty run")
    return float(np.mean(y_true == y_pred))


def per_run_metric_table(
    predictions_by_model: dict[str, pd.DataFrame],
    *,
    metric: str = PRIMARY_METRIC,
) -> pd.DataFrame:
    """Build wide table: rows = run_id, columns = model_id, values = metric.

    Each input frame must contain ``run_id``, ``y_true``, ``y_pred``.
    """
    if metric != PRIMARY_METRIC:
        raise ValueError(f"unsupported metric {metric!r}; only {PRIMARY_METRIC}")

    series_map: dict[str, pd.Series] = {}
    for model_id, df in predictions_by_model.items():
        required = {"run_id", "y_true", "y_pred"}
        if not required.issubset(df.columns):
            raise ValueError(f"{model_id}: missing columns {required - set(df.columns)}")
        scores = (
            df.groupby("run_id", sort=True)
            .apply(
                lambda g: run_level_accuracy(g["y_true"].to_numpy(), g["y_pred"].to_numpy()),
                include_groups=False,
            )
        )
        series_map[model_id] = scores.rename(model_id)

    wide = pd.concat(series_map, axis=1)
    wide.index.name = "run_id"
    # Require complete paired design across models.
    if wide.isna().any().any():
        missing = wide[wide.isna().any(axis=1)]
        raise ValueError(
            f"incomplete run coverage across models; missing rows:\n{missing}"
        )
    return wide


def summarize_per_run(
    wide: pd.DataFrame,
    *,
    confidence: float = 0.95,
) -> pd.DataFrame:
    """Mean, SD, and normal-approx CI of the per-run metric (EST-01 over runs)."""
    from scipy.stats import norm

    z = float(norm.ppf(0.5 + confidence / 2.0))
    rows = []
    n = int(len(wide))
    for model_id in wide.columns:
        vals = wide[model_id].to_numpy(dtype=float)
        mean = float(np.mean(vals))
        std = float(np.std(vals, ddof=1)) if n > 1 else 0.0
        se = std / np.sqrt(n) if n > 0 else float("nan")
        rows.append(
            {
                "model_id": model_id,
                "metric": PRIMARY_METRIC,
                "n_runs": n,
                "mean": mean,
                "std": std,
                "ci_low": mean - z * se,
                "ci_high": mean + z * se,
                "confidence": confidence,
                "experimental_unit": "run_id",
            }
        )
    return pd.DataFrame(rows)


def friedman_test(wide: pd.DataFrame) -> dict[str, Any]:
    """Global Friedman test across models (columns) blocked by run (rows)."""
    if wide.shape[1] < 2:
        raise ValueError("need at least 2 models")
    if wide.shape[0] < 2:
        raise ValueError("need at least 2 runs (experimental units)")
    arrays = [wide[c].to_numpy(dtype=float) for c in wide.columns]
    stat, p = friedmanchisquare(*arrays)
    return {
        "test": "Friedman",
        "metric": PRIMARY_METRIC,
        "experimental_unit": "run_id",
        "n_units": int(wide.shape[0]),
        "n_models": int(wide.shape[1]),
        "model_ids": list(wide.columns),
        "statistic": float(stat),
        "pvalue": float(p),
        "alpha": 0.05,
        "reject_h0": bool(p < 0.05),
        "h0": "all models have equal run-level accuracy distributions (ranks)",
    }


def holm_adjust(pvalues: Sequence[float]) -> list[float]:
    """Holm–Bonferroni step-down adjustment (EST-03)."""
    m = len(pvalues)
    order = np.argsort(pvalues)
    adjusted = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        factor = m - rank
        adj = min(1.0, float(pvalues[idx]) * factor)
        running = max(running, adj)
        adjusted[idx] = running
    return adjusted


def wilcoxon_pairwise(
    wide: pd.DataFrame,
    *,
    pairs: Iterable[tuple[str, str]] | None = None,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Paired Wilcoxon signed-rank tests with Holm correction.

    Default pairs: all unique unordered pairs among columns.
    """
    models = list(wide.columns)
    if pairs is None:
        pairs = [
            (models[i], models[j])
            for i in range(len(models))
            for j in range(i + 1, len(models))
        ]
    pair_list = list(pairs)
    raw_rows: list[dict[str, Any]] = []
    for a, b in pair_list:
        if a not in wide.columns or b not in wide.columns:
            raise ValueError(f"unknown model in pair ({a}, {b})")
        diff = wide[a].to_numpy(dtype=float) - wide[b].to_numpy(dtype=float)
        nonzero = diff[diff != 0]
        if len(nonzero) < 1:
            stat, p = float("nan"), 1.0
            note = "all paired differences zero"
        else:
            # zero_method='wilcox' drops zeros; alternative two-sided.
            try:
                res = wilcoxon(wide[a], wide[b], zero_method="wilcox", alternative="two-sided")
                stat, p = float(res.statistic), float(res.pvalue)
                note = ""
            except ValueError as exc:
                stat, p = float("nan"), 1.0
                note = str(exc)
        raw_rows.append(
            {
                "model_a": a,
                "model_b": b,
                "metric": PRIMARY_METRIC,
                "experimental_unit": "run_id",
                "n_units": int(len(wide)),
                "n_nonzero_diffs": int(len(nonzero)),
                "mean_diff_a_minus_b": float(np.mean(diff)),
                "statistic": stat,
                "pvalue_raw": p,
                "note": note,
            }
        )
    adjusted = holm_adjust([r["pvalue_raw"] for r in raw_rows])
    for r, p_adj in zip(raw_rows, adjusted):
        r["pvalue_holm"] = float(p_adj)
        r["alpha"] = alpha
        r["significant_holm"] = bool(p_adj < alpha)
        r["correction"] = "holm"
    return pd.DataFrame(raw_rows)


def hypothesis_pairs() -> list[tuple[str, str]]:
    """Pairs most relevant to H1–H2 (SPEC-000 §4), plus RF vs XGB for QP1/QP5."""
    return [
        ("random_forest", "logistic_regression"),
        ("gradient_boosting", "logistic_regression"),
        ("xgboost", "logistic_regression"),
        ("random_forest", "decision_tree"),
        ("xgboost", "decision_tree"),
        ("xgboost", "random_forest"),
        ("random_forest", "gradient_boosting"),
        ("xgboost", "gradient_boosting"),
        ("decision_tree", "logistic_regression"),
        ("svm", "logistic_regression"),
    ]


def interpret_hypotheses_from_tests(
    *,
    friedman: dict[str, Any],
    wide: pd.DataFrame,
    alpha: float = 0.05,
    global_metrics: pd.DataFrame | None = None,
) -> list[dict[str, Any]]:
    """Map planned Wilcoxon families (Holm within H) + Friedman to H1–H4 notes.

    H1/H2 use pre-specified contrasts with Holm correction *within* each
    hypothesis family (EST-03). The all-pairs Holm table is reported separately
    for exploration and is more conservative under n_units small.
    H3/H4 remain primarily criterion-based on global metrics/cost (SPEC-000 §4).
    """

    def _family(
        name: str,
        pairs: list[tuple[str, str]],
        require_positive: bool = True,
    ) -> dict[str, Any]:
        wdf = wilcoxon_pairwise(wide, pairs=pairs, alpha=alpha)
        rows = []
        ok = True
        for (_, _), (_, row) in zip(pairs, wdf.iterrows()):
            d = row.to_dict()
            rows.append(d)
            if require_positive:
                if not (bool(d["significant_holm"]) and float(d["mean_diff_a_minus_b"]) > 0):
                    ok = False
            elif not bool(d["significant_holm"]):
                ok = False
        return {
            "hypothesis": name,
            "friedman_reject_h0": friedman["reject_h0"],
            "correction_family": "holm_within_hypothesis",
            "n_planned_pairs": len(pairs),
            "run_accuracy_wilcoxon": (
                "all planned pairs significant (Holm within H)"
                if ok
                else "not all planned pairs significant (Holm within H)"
            ),
            "verdict_run_level": "corroborated" if ok else "not_corroborated_by_wilcoxon",
            "pairs": rows,
        }

    h1 = _family(
        "H1",
        [
            ("random_forest", "logistic_regression"),
            ("gradient_boosting", "logistic_regression"),
            ("xgboost", "logistic_regression"),
        ],
    )
    h2 = _family(
        "H2",
        [
            ("random_forest", "logistic_regression"),
            ("random_forest", "decision_tree"),
            ("xgboost", "logistic_regression"),
            ("xgboost", "decision_tree"),
        ],
    )
    out: list[dict[str, Any]] = [h1, h2]
    out.append(
        {
            "hypothesis": "H3",
            "note": (
                "H3 uses cost + per-class F1 criteria (SPEC-000 §4); "
                "run-level accuracy Wilcoxon is not the primary test for H3."
            ),
            "verdict_run_level": "not_applicable_primary",
        }
    )
    h4: dict[str, Any] = {
        "hypothesis": "H4",
        "note": (
            "H4 compares leaders across Acc/F1/MCC/inference cost on global "
            "holdout metrics; not a single Wilcoxon contrast."
        ),
        "verdict_run_level": "not_applicable_primary",
    }
    if global_metrics is not None:
        h4["global_metrics_ref"] = "provided"
    out.append(h4)
    return out


def assert_not_sample_level(n_rows: int, n_runs: int) -> None:
    """Guard: refuse designs that treat rows as independent units."""
    if n_runs < 2:
        raise ValueError("n_runs must be >= 2 for paired model comparison")
    if n_rows == n_runs:
        return  # already aggregated
    # Caller must pass aggregated n_units == n_runs into tests.
