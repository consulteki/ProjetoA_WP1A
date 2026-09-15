"""Unit tests for SPEC-007 / A5 evaluation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from wp1a.evaluation.confused_classes import systematically_confused_classes
from wp1a.evaluation.metrics import compute_classification_metrics
from wp1a.evaluation.pipeline import evaluate_model_from_artifacts, run_evaluation_a5
from wp1a.evaluation.verify import (
    recompute_balanced_accuracy_from_per_class,
    recompute_f1_macro_from_per_class,
    verify_reported_aggregates,
)
from wp1a.models.protocol import MODEL_IDS


def test_recompute_f1_and_ba_match_spec_formulas():
    y_true = np.array([0, 0, 1, 1, 2, 2])
    y_pred = np.array([0, 1, 1, 1, 2, 0])
    m = compute_classification_metrics(y_true, y_pred, labels=(0, 1, 2))
    assert recompute_f1_macro_from_per_class(m["MET-09_per_class"]) == pytest.approx(
        m["MET-05_f1_macro"]
    )
    assert recompute_balanced_accuracy_from_per_class(
        m["MET-09_per_class"]
    ) == pytest.approx(m["MET-02_balanced_accuracy"])
    assert verify_reported_aggregates(m)["all_ok"]


def test_verify_detects_tampered_f1():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 0, 1, 0])
    m = compute_classification_metrics(y_true, y_pred, labels=(0, 1))
    m["MET-05_f1_macro"] = 0.99
    assert verify_reported_aggregates(m)["all_ok"] is False


def _write_fake_a4(tmp: Path, experiment_id: str = "exp-fake-a4") -> None:
    rng = np.random.default_rng(0)
    (tmp / "results" / "predictions").mkdir(parents=True)
    (tmp / "results" / "metrics").mkdir(parents=True)
    (tmp / "results" / "tables").mkdir(parents=True)
    (tmp / "models").mkdir(parents=True)
    # Train labels cover 0..20
    train = pd.DataFrame({"class_label": list(range(21)) * 3})
    train_path = tmp / "train.csv.gz"
    train.to_csv(train_path, index=False, compression="gzip")

    for i, model_id in enumerate(MODEL_IDS):
        n = 21 * 4
        y_true = np.tile(np.arange(21), 4)
        # Mostly correct with some noise
        y_pred = y_true.copy()
        flip = rng.choice(n, size=8, replace=False)
        y_pred[flip] = (y_pred[flip] + 1) % 21
        pred = pd.DataFrame(
            {
                "run_id": [f"r{j}" for j in range(n)],
                "y_true": y_true,
                "y_pred": y_pred,
                "model_id": model_id,
                "experiment_id": f"{experiment_id}__{model_id}",
            }
        )
        pred.to_csv(
            tmp / "results" / "predictions" / f"{experiment_id}__{model_id}__test_pred.csv",
            index=False,
        )
        record = {
            "experiment_id": f"{experiment_id}__{model_id}",
            "parent_experiment_id": experiment_id,
            "model_id": model_id,
            "seed": 42,
            "git_sha": "deadbeef",
            "parameters": {"x": i},
            "time": {"train_s": 1.0 + i, "inference_s": 0.1, "selection_s": 2.0},
            "model_size": {"bytes": 1000 * (i + 1)},
        }
        (tmp / "results" / "metrics" / f"{experiment_id}__{model_id}__record.json").write_text(
            json.dumps(record), encoding="utf-8"
        )
    (tmp / "train_path.txt").write_text(str(train_path), encoding="utf-8")


def test_a5_pipeline_smoke(tmp_path: Path):
    _write_fake_a4(tmp_path)
    train_path = Path((tmp_path / "train_path.txt").read_text(encoding="utf-8").strip())
    out = run_evaluation_a5(
        experiment_id="exp-fake-a4",
        repo_root=tmp_path,
        train_labels_path=train_path,
    )
    assert out["n_models"] == 6
    assert out["acceptance"]["CA-05_all_metrics_present"]
    assert out["acceptance"]["CA-06_f1_ba_recomputed"]
    assert "best" not in out["disclaimer"].lower() or "NOT" in out["disclaimer"] or "Do NOT" in out["disclaimer"]
    assert Path(out["artifacts"]["global_metrics_csv"]).is_file()
    assert Path(out["artifacts"]["per_class_metrics_csv"]).is_file()
    assert Path(out["artifacts"]["cost_metrics_csv"]).is_file()
    assert Path(out["artifacts"]["evaluation_json"]).is_file()
    # All MET keys present in global table
    g = pd.read_csv(out["artifacts"]["global_metrics_csv"])
    for col in [
        "MET-01_accuracy",
        "MET-05_f1_macro",
        "MET-07_mcc",
        "MET-10_train_time_s",
        "MET-12_model_size_bytes",
    ]:
        assert col in g.columns
    assert systematically_confused_classes(out["models"])["systematic_low_f1_faults"] is not None
