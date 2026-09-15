"""Tests for A6 scientific figures — results/ only, never data/raw."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from wp1a.visualization.pipeline import run_a6
from wp1a.visualization.sources import ResultsOnlyError, assert_under_results, require_file


def test_assert_under_results_accepts_results_file(tmp_path: Path):
    results = tmp_path / "results"
    results.mkdir()
    f = results / "tables" / "x.csv"
    f.parent.mkdir(parents=True)
    f.write_text("a\n1\n", encoding="utf-8")
    assert require_file(f, results_root=results) == f.resolve()


def test_assert_under_results_rejects_data_raw(tmp_path: Path):
    results = tmp_path / "results"
    results.mkdir()
    raw = tmp_path / "data" / "raw" / "d00.dat"
    raw.parent.mkdir(parents=True)
    raw.write_text("x", encoding="utf-8")
    with pytest.raises(ResultsOnlyError):
        assert_under_results(raw, results_root=results)


def test_assert_under_results_rejects_outside_tree(tmp_path: Path):
    results = tmp_path / "results"
    results.mkdir()
    other = tmp_path / "elsewhere" / "x.csv"
    other.parent.mkdir()
    other.write_text("a\n", encoding="utf-8")
    with pytest.raises(ResultsOnlyError):
        assert_under_results(other, results_root=results)


def _seed_min_results(root: Path, experiment_id: str = "exp-fake") -> None:
    results = root / "results"
    for sub in ("tables", "metrics", "metadata", "figures"):
        (results / sub).mkdir(parents=True)
    # A1 characterization
    char = pd.DataFrame(
        {
            "class_label": list(range(22)),
            "meaning": ["m"] * 22,
            "in_normative_set_0_20": [True] * 21 + [False],
            "n_samples": [100] * 22,
            "n_runs": [2] * 22,
            "n_features": [52] * 22,
        }
    )
    char.to_csv(results / "tables" / "A1_dataset_characterization.csv", index=False)
    # hyperparams
    models = [
        "logistic_regression",
        "decision_tree",
        "random_forest",
        "gradient_boosting",
        "svm",
        "xgboost",
    ]
    pd.DataFrame(
        {"model_id": models, "mod_code": [f"MOD-{i}" for i in range(1, 7)], "experiment_id": [experiment_id] * 6}
    ).to_csv(results / "tables" / f"{experiment_id}__hyperparameters.csv", index=False)
    # global + cost
    g = pd.DataFrame(
        {
            "model_id": models,
            "MET-01_accuracy": [0.2] * 6,
            "MET-02_balanced_accuracy": [0.1] * 6,
            "MET-05_f1_macro": [0.15, 0.2, 0.3, 0.25, 0.1, 0.28],
            "MET-07_mcc": [0.2, 0.3, 0.4, 0.35, 0.15, 0.38],
            "MET-10_train_time_s": [1, 2, 3, 4, 5, 6],
            "MET-11_inference_time_s": [0.1] * 6,
            "MET-12_model_size_bytes": [1000] * 6,
        }
    )
    g.to_csv(results / "tables" / f"A5_{experiment_id}__global_metrics.csv", index=False)
    g[["model_id", "MET-10_train_time_s", "MET-11_inference_time_s", "MET-12_model_size_bytes"]].to_csv(
        results / "tables" / f"A5_{experiment_id}__cost_metrics.csv", index=False
    )
    # per-class
    rows = []
    for mid in models:
        for c in range(21):
            rows.append(
                {
                    "model_id": mid,
                    "class_label": c,
                    "f1": 0.5 if c < 5 else 0.0,
                    "support": 10 if c < 5 else 0,
                    "precision": 0.5,
                    "recall": 0.5,
                }
            )
    pd.DataFrame(rows).to_csv(
        results / "tables" / f"A5_{experiment_id}__per_class_metrics.csv", index=False
    )
    # confusion matrices 21x21
    import numpy as np

    for mid in models:
        cm = pd.DataFrame(
            np.eye(21, dtype=int),
            index=[f"true_{i}" for i in range(21)],
            columns=[f"pred_{i}" for i in range(21)],
        )
        cm.to_csv(results / "tables" / f"A5_{experiment_id}__{mid}__confusion_matrix.csv")
    qp3 = {
        "systematic_confused_pairs": [
            {"true_class": 3, "pred_class": 15, "total_count_across_models": 10}
        ]
    }
    (results / "tables" / f"A5_{experiment_id}__qp3_confused_faults.json").write_text(
        json.dumps(qp3), encoding="utf-8"
    )
    (results / "metadata" / "audit_counts.json").write_text(
        json.dumps({"counts": {"n_files": 44, "n_classes_observed": 22}}), encoding="utf-8"
    )
    (results / "metadata" / "canonical_dataset.json").write_text(
        json.dumps(
            {
                "dataset_version": "tep-canonical-v1",
                "counts": {"n_features": 52, "n_classes": 21, "n_runs": 42, "n_rows": 100},
            }
        ),
        encoding="utf-8",
    )


def test_run_a6_smoke_and_never_needs_raw(tmp_path: Path):
    _seed_min_results(tmp_path)
    # Ensure data/raw does not even need to exist
    assert not (tmp_path / "data" / "raw").exists()
    out = run_a6(repo_root=tmp_path, experiment_id="exp-fake")
    assert out["results_only"] is True
    assert out["n_models"] == 6
    meta = json.loads(Path(out["traceability_path"]).read_text(encoding="utf-8"))
    for row in meta["traceability"]:
        for src in row["sources"].split(","):
            assert src.startswith("results/"), src
            assert "data/raw" not in src
    # key figures exist
    assert Path(out["artifacts"]["06_f1_mcc"]).is_file()
    assert Path(out["artifacts"]["07_computational_cost"]).is_file()
