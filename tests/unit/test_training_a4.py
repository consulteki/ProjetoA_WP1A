"""Unit tests for A4 metrics, search expansion, and training smoke."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from wp1a.evaluation.metrics import CANONICAL_LABELS, compute_classification_metrics
from wp1a.experiment.provenance import environment_snapshot, git_provenance
from wp1a.experiment.types import ExperimentDataset, SplitRef
from wp1a.training.pipeline import run_training_benchmark
from wp1a.training.search import expand_search_space


def test_expand_search_space_cartesian():
    grid = expand_search_space({"C": [0.1, 1.0], "kernel": ["linear"]})
    assert len(grid) == 2
    assert {"C": 0.1, "kernel": "linear"} in grid


def test_f1_macro_and_ba_formulas():
    # 3-class toy with known confusion; pad to canonical 21 via labels arg.
    y_true = np.array([0, 0, 1, 1, 2, 2])
    y_pred = np.array([0, 1, 1, 1, 2, 0])
    labels = (0, 1, 2)
    m = compute_classification_metrics(y_true, y_pred, labels=labels)
    # class0: tp1 fp1 fn1 → p=0.5 r=0.5 f1=0.5
    # class1: tp2 fp1 fn0 → p=2/3 r=1 f1=0.8
    # class2: tp1 fp0 fn1 → p=1 r=0.5 f1=2/3
    f1s = [row["f1"] for row in m["MET-09_per_class"]]
    assert m["MET-05_f1_macro"] == pytest.approx(sum(f1s) / 3)
    recalls = [row["recall"] for row in m["MET-09_per_class"]]
    assert m["MET-02_balanced_accuracy"] == pytest.approx(sum(recalls) / 3)
    assert m["_checks"]["f1_macro_matches_sklearn"]


def test_canonical_label_count():
    assert len(CANONICAL_LABELS) == 21


def test_provenance_keys():
    env = environment_snapshot()
    assert "python" in env and "scikit-learn" in env
    git = git_provenance()
    assert "git_sha" in git


def _toy_full_classes(n_per=8, n_features=10, seed=0) -> ExperimentDataset:
    """One small block per canonical class in each partition (coverage OK)."""
    rng = np.random.default_rng(seed)
    labels = list(range(21))

    def block(prefix: str):
        Xs, ys, rs = [], [], []
        for c in labels:
            Xs.append(rng.normal(size=(n_per, n_features)) + c * 0.1)
            ys.append(np.full(n_per, c))
            rs.append(np.full(n_per, f"{prefix}_c{c}", dtype=object))
        return np.vstack(Xs), np.concatenate(ys), np.concatenate(rs)

    Xt, yt, rt = block("tr")
    Xv, yv, rv = block("va")
    Xs, ys, rs = block("te")
    return ExperimentDataset(
        X_train=Xt,
        y_train=yt,
        X_val=Xv,
        y_val=yv,
        X_test=Xs,
        y_test=ys,
        run_id_train=rt,
        run_id_val=rv,
        run_id_test=rs,
        dataset_version="tep-canonical-v1",
        preprocessor_version="preprocessor_v1",
    )


def test_training_benchmark_smoke_logs_required_fields(tmp_path: Path):
    ds = _toy_full_classes()
    split = SplitRef(
        manifest_version="split_manifest_v1",
        path="data/processed/split_manifest_v1.json",
        train_runs=("a",),
        validation_runs=("b",),
        test_runs=("c",),
        seed=42,
    )
    # Tiny search spaces — smoke only.
    cfg = {
        "experiment_id": "exp-smoke-a4",
        "config_source": "test",
        "model_ids": [
            "logistic_regression",
            "decision_tree",
            "random_forest",
            "gradient_boosting",
            "svm",
            "xgboost",
        ],
        "search_spaces": {
            "logistic_regression": {"C": [1.0], "max_iter": [200], "solver": ["lbfgs"]},
            "decision_tree": {"max_depth": [3], "min_samples_leaf": [1]},
            "random_forest": {
                "n_estimators": [5],
                "max_depth": [3],
                "min_samples_leaf": [1],
                "n_jobs": [1],
            },
            "gradient_boosting": {
                "n_estimators": [5],
                "learning_rate": [0.1],
                "max_depth": [2],
            },
            "svm": {"C": [1.0], "kernel": ["linear"]},
            "xgboost": {
                "n_estimators": [5],
                "learning_rate": [0.1],
                "max_depth": [2],
                "n_jobs": [1],
            },
        },
    }
    out = run_training_benchmark(
        dataset=ds,
        split=split,
        experiment_cfg=cfg,
        seed=42,
        output_root=tmp_path,
    )
    assert out["n_models"] == 6
    summary = json.loads(Path(out["summary_json"]).read_text(encoding="utf-8"))
    assert summary["scientific_validity"] is True
    for rec in summary["models"]:
        assert rec["seed"] == 42
        assert "git_sha" in rec
        assert "environment" in rec and "python" in rec["environment"]
        assert isinstance(rec["parameters"], dict) and rec["parameters"]
        assert rec["time"]["train_s"] is not None
        assert rec["time"]["inference_s"] is not None
        assert "MET-05_f1_macro" in rec["metrics"]
        assert rec["model_size"]["bytes"] > 0
        assert Path(rec["artifacts"]["model_path"]).is_file()
        assert Path(rec["artifacts"]["predictions_path"]).is_file()
