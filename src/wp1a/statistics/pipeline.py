"""Pipeline SPEC-008 — artefatos estatísticos versionados em ``results/``."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from wp1a.models.protocol import MODEL_IDS
from wp1a.statistics.tests import (
    A8_DISCLAIMER,
    PRIMARY_METRIC,
    friedman_test,
    hypothesis_pairs,
    interpret_hypotheses_from_tests,
    per_run_metric_table,
    summarize_per_run,
    wilcoxon_pairwise,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_predictions(
    *,
    experiment_id: str,
    repo_root: Path,
    model_ids: Sequence[str],
) -> dict[str, pd.DataFrame]:
    pred_dir = repo_root / "results" / "predictions"
    out: dict[str, pd.DataFrame] = {}
    for mid in model_ids:
        path = pred_dir / f"{experiment_id}__{mid}__test_pred.csv"
        if not path.is_file():
            raise FileNotFoundError(f"missing predictions: {path}")
        out[mid] = pd.read_csv(path)
    return out


def run_statistics_a8(
    *,
    experiment_id: str,
    repo_root: Path,
    model_ids: Sequence[str] = MODEL_IDS,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Execute SPEC-008 for one frozen A4/A5 experiment; write tables + JSON."""
    model_ids = tuple(model_ids)
    preds = _load_predictions(
        experiment_id=experiment_id, repo_root=repo_root, model_ids=model_ids
    )
    wide = per_run_metric_table(preds, metric=PRIMARY_METRIC)
    summary = summarize_per_run(wide)
    friedman = friedman_test(wide)
    wilcoxon_all = wilcoxon_pairwise(wide, alpha=alpha)
    wilcoxon_h = wilcoxon_pairwise(wide, pairs=hypothesis_pairs(), alpha=alpha)

    global_path = (
        repo_root / "results" / "tables" / f"A5_{experiment_id}__global_metrics.csv"
    )
    global_metrics = pd.read_csv(global_path) if global_path.is_file() else None
    hyp = interpret_hypotheses_from_tests(
        friedman=friedman,
        wide=wide,
        alpha=alpha,
        global_metrics=global_metrics,
    )

    # Planned-contrast tables (Holm within each H) for DOC-R03.
    h1_pairs_df = wilcoxon_pairwise(
        wide,
        pairs=[
            ("random_forest", "logistic_regression"),
            ("gradient_boosting", "logistic_regression"),
            ("xgboost", "logistic_regression"),
        ],
        alpha=alpha,
    )
    h2_pairs_df = wilcoxon_pairwise(
        wide,
        pairs=[
            ("random_forest", "logistic_regression"),
            ("random_forest", "decision_tree"),
            ("xgboost", "logistic_regression"),
            ("xgboost", "decision_tree"),
        ],
        alpha=alpha,
    )

    limitations = [
        (
            "Single seed and single train/val/test split "
            f"({experiment_id}): EST-01 mean/SD/CI across seeds/partitions "
            "are not available; summaries are over test run_id units only."
        ),
        (
            f"Primary paired metric is {PRIMARY_METRIC} (within-run accuracy). "
            "Each test run has a single true class; macro-F1/MCC over C=21 are "
            "not well-defined per run and are not used as Friedman blocks."
        ),
        (
            "H3/H4 remain primarily SPEC-000 §4 criterion evaluations on global "
            "holdout metrics/cost; Wilcoxon on run accuracy is primary for H1/H2."
        ),
        (
            f"Statistical power is limited by n_units={len(wide)} test runs."
        ),
    ]

    tables_dir = repo_root / "results" / "tables"
    metrics_dir = repo_root / "results" / "metrics"
    tables_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)

    wide_path = tables_dir / f"A8_{experiment_id}__per_run_{PRIMARY_METRIC}.csv"
    summary_path = tables_dir / f"A8_{experiment_id}__run_metric_summary.csv"
    friedman_path = tables_dir / f"A8_{experiment_id}__friedman.json"
    wilcoxon_all_path = tables_dir / f"A8_{experiment_id}__wilcoxon_all_pairs.csv"
    wilcoxon_h_path = tables_dir / f"A8_{experiment_id}__wilcoxon_hypothesis_pairs.csv"
    wilcoxon_h1_path = tables_dir / f"A8_{experiment_id}__wilcoxon_H1_family.csv"
    wilcoxon_h2_path = tables_dir / f"A8_{experiment_id}__wilcoxon_H2_family.csv"
    hyp_path = tables_dir / f"A8_{experiment_id}__hypothesis_from_stats.json"
    lim_path = tables_dir / f"A8_{experiment_id}__limitations.json"
    report_path = metrics_dir / f"A8_{experiment_id}__statistics.json"

    wide.to_csv(wide_path)
    summary.to_csv(summary_path, index=False)
    wilcoxon_all.to_csv(wilcoxon_all_path, index=False)
    wilcoxon_h.to_csv(wilcoxon_h_path, index=False)
    h1_pairs_df.to_csv(wilcoxon_h1_path, index=False)
    h2_pairs_df.to_csv(wilcoxon_h2_path, index=False)
    friedman_path.write_text(json.dumps(friedman, indent=2), encoding="utf-8")
    hyp_path.write_text(json.dumps(hyp, indent=2, default=str), encoding="utf-8")
    lim_path.write_text(json.dumps(limitations, indent=2), encoding="utf-8")

    payload: dict[str, Any] = {
        "delivery": "SPEC-008",
        "experiment_id": experiment_id,
        "created_at": _utc_now(),
        "disclaimer": A8_DISCLAIMER,
        "experimental_unit": "run_id",
        "n_units": int(len(wide)),
        "n_models": int(wide.shape[1]),
        "metric": PRIMARY_METRIC,
        "alpha": alpha,
        "friedman": friedman,
        "hypothesis_interpretation": hyp,
        "limitations": limitations,
        "artifacts": {
            "per_run_metric": str(wide_path.relative_to(repo_root)),
            "run_metric_summary": str(summary_path.relative_to(repo_root)),
            "friedman": str(friedman_path.relative_to(repo_root)),
            "wilcoxon_all_pairs": str(wilcoxon_all_path.relative_to(repo_root)),
            "wilcoxon_hypothesis_pairs": str(wilcoxon_h_path.relative_to(repo_root)),
            "wilcoxon_H1_family": str(wilcoxon_h1_path.relative_to(repo_root)),
            "wilcoxon_H2_family": str(wilcoxon_h2_path.relative_to(repo_root)),
            "hypothesis_from_stats": str(hyp_path.relative_to(repo_root)),
            "limitations": str(lim_path.relative_to(repo_root)),
            "statistics_bundle": str(report_path.relative_to(repo_root)),
        },
    }
    report_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return payload
