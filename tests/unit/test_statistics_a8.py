"""Unit tests for SPEC-008 statistical analysis (run-level units)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from wp1a.statistics.pipeline import run_statistics_a8
from wp1a.statistics.tests import (
    friedman_test,
    holm_adjust,
    per_run_metric_table,
    run_level_accuracy,
    wilcoxon_pairwise,
)


def test_run_level_accuracy():
    assert run_level_accuracy(np.array([1, 1, 1]), np.array([1, 0, 1])) == pytest.approx(
        2 / 3
    )


def test_holm_monotonic_and_bounds():
    adj = holm_adjust([0.01, 0.04, 0.03])
    assert all(0.0 <= p <= 1.0 for p in adj)
    # Sorted raw 0.01, 0.03, 0.04 → adjusted non-decreasing in that order
    order = np.argsort([0.01, 0.04, 0.03])
    ordered_adj = [adj[i] for i in order]
    assert ordered_adj == sorted(ordered_adj)


def test_per_run_table_and_friedman_rejects_identical():
    rng = np.random.default_rng(0)
    runs = [f"r{i}" for i in range(8)]
    frames = {}
    # Model A perfect, B chance-level → Friedman should see differences
    for mid, p_correct in [("a", 1.0), ("b", 0.2), ("c", 0.5)]:
        rows = []
        for r in runs:
            y_true = np.full(20, 1)
            mask = rng.random(20) < p_correct
            y_pred = np.where(mask, 1, 0)
            for yt, yp in zip(y_true, y_pred):
                rows.append({"run_id": r, "y_true": int(yt), "y_pred": int(yp)})
        frames[mid] = pd.DataFrame(rows)
    wide = per_run_metric_table(frames)
    assert wide.shape == (8, 3)
    fr = friedman_test(wide)
    assert fr["experimental_unit"] == "run_id"
    assert fr["n_units"] == 8
    assert fr["reject_h0"] is True


def test_wilcoxon_holm_marks_strong_pair():
    runs = [f"r{i}" for i in range(10)]
    strong = pd.DataFrame(
        {
            "run_id": runs,
            "y_true": [1] * 10,
            "y_pred": [1] * 10,
        }
    )
    # Expand to multiple samples per run for realism
    strong = strong.loc[strong.index.repeat(5)].reset_index(drop=True)
    weak_rows = []
    for r in runs:
        for _ in range(5):
            weak_rows.append({"run_id": r, "y_true": 1, "y_pred": 0})
    weak = pd.DataFrame(weak_rows)
    wide = per_run_metric_table({"strong": strong, "weak": weak})
    w = wilcoxon_pairwise(wide, pairs=[("strong", "weak")])
    assert bool(w.iloc[0]["significant_holm"])
    assert float(w.iloc[0]["mean_diff_a_minus_b"]) > 0
    assert w.iloc[0]["correction"] == "holm"


def test_rejects_incomplete_model_coverage():
    df_a = pd.DataFrame(
        {"run_id": ["r1", "r2"], "y_true": [0, 1], "y_pred": [0, 1]}
    )
    df_b = pd.DataFrame(
        {"run_id": ["r1"], "y_true": [0], "y_pred": [1]}
    )
    with pytest.raises(ValueError, match="incomplete"):
        per_run_metric_table({"a": df_a, "b": df_b})


def test_pipeline_exp_a4_v2_if_artifacts_present():
    root = Path(__file__).resolve().parents[2]
    pred = root / "results" / "predictions" / "exp-a4-v2__xgboost__test_pred.csv"
    if not pred.is_file():
        pytest.skip("exp-a4-v2 predictions not present")
    out = run_statistics_a8(experiment_id="exp-a4-v2", repo_root=root)
    assert out["experimental_unit"] == "run_id"
    assert out["n_units"] == 11
    assert out["n_models"] == 6
    assert out["friedman"]["n_units"] == 11
    assert Path(root / out["artifacts"]["statistics_bundle"]).is_file()
