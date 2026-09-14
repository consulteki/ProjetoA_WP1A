"""Unit tests for DRY-RUN subsample + pipeline scaffolding."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from wp1a.experiment.dry_run import (
    DRY_RUN_DISCLAIMER,
    DRY_RUN_MARKER,
    run_dry_pipeline,
    subsample_dataset_by_runs,
    write_dry_run_artifacts,
)
from wp1a.experiment.types import ExperimentDataset, SplitRef
from wp1a.models.protocol import MODEL_IDS


def _dataset_with_runs(
    *,
    train_runs: list[str],
    val_runs: list[str],
    test_runs: list[str],
    rows_per_run: int = 4,
    n_features: int = 5,
    n_classes: int = 3,
    seed: int = 0,
) -> ExperimentDataset:
    rng = np.random.default_rng(seed)

    def block(runs: list[str]):
        X, y, r = [], [], []
        for i, run in enumerate(runs):
            X.append(rng.normal(size=(rows_per_run, n_features)))
            y.append(np.full(rows_per_run, i % n_classes))
            r.append(np.full(rows_per_run, run, dtype=object))
        return (
            np.vstack(X),
            np.concatenate(y),
            np.concatenate(r),
        )

    Xt, yt, rt = block(train_runs)
    Xv, yv, rv = block(val_runs)
    Xs, ys, rs = block(test_runs)
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


def _split() -> SplitRef:
    return SplitRef(
        manifest_version="split_manifest_v1",
        path="data/processed/split_manifest_v1.json",
        train_runs=("a",),
        validation_runs=("b",),
        test_runs=("c",),
        seed=42,
    )


def test_subsample_preserves_partition_disjunction():
    ds = _dataset_with_runs(
        train_runs=[f"tr{i}" for i in range(10)],
        val_runs=[f"va{i}" for i in range(6)],
        test_runs=[f"te{i}" for i in range(6)],
    )
    sub, plan = subsample_dataset_by_runs(
        ds, run_fraction=0.5, seed=7, max_runs_per_partition=3
    )
    tr, va, te = set(plan.train_runs), set(plan.validation_runs), set(plan.test_runs)
    assert not (tr & va) and not (tr & te) and not (va & te)
    assert tr.issubset({f"tr{i}" for i in range(10)})
    assert va.issubset({f"va{i}" for i in range(6)})
    assert te.issubset({f"te{i}" for i in range(6)})
    assert len(plan.train_runs) <= 3
    assert DRY_RUN_MARKER in sub.dataset_version
    assert set(sub.run_id_train.tolist()) == tr


def test_subsample_reproducible():
    ds = _dataset_with_runs(
        train_runs=[f"tr{i}" for i in range(8)],
        val_runs=[f"va{i}" for i in range(4)],
        test_runs=[f"te{i}" for i in range(4)],
    )
    _, p1 = subsample_dataset_by_runs(ds, run_fraction=0.4, seed=42, max_runs_per_partition=2)
    _, p2 = subsample_dataset_by_runs(ds, run_fraction=0.4, seed=42, max_runs_per_partition=2)
    assert p1 == p2


def test_rejects_unmarked_experiment_prefix():
    ds = _dataset_with_runs(
        train_runs=["tr0", "tr1"],
        val_runs=["va0"],
        test_runs=["te0"],
    )
    with pytest.raises(ValueError, match="DRY-RUN"):
        run_dry_pipeline(
            dataset=ds,
            split=_split(),
            experiment_prefix="prod",
            model_ids=("decision_tree",),
        )


def test_dry_pipeline_and_artifacts_are_marked(tmp_path: Path):
    ds = _dataset_with_runs(
        train_runs=[f"tr{i}" for i in range(4)],
        val_runs=[f"va{i}" for i in range(2)],
        test_runs=[f"te{i}" for i in range(2)],
        rows_per_run=6,
        n_features=8,
        n_classes=3,
    )
    results, plan, summary, sub = run_dry_pipeline(
        dataset=ds,
        split=_split(),
        run_fraction=1.0,
        seed=0,
        max_runs_per_partition=2,
        model_ids=MODEL_IDS,
    )
    assert summary["status"] == DRY_RUN_MARKER
    assert summary["scientific_validity"] is False
    assert DRY_RUN_DISCLAIMER in summary["disclaimer"]
    assert len(results) == 6
    assert all(r.experiment_id.startswith(DRY_RUN_MARKER) for r in results)

    out = write_dry_run_artifacts(
        output_dir=tmp_path / "dry_run",
        results=results,
        plan=plan,
        summary=summary,
        dataset=sub,
    )
    readme = (out / "DRY_RUN_README.md").read_text(encoding="utf-8")
    assert DRY_RUN_MARKER in readme
    assert "NOT scientifically" in readme or "not scientifically" in readme.lower()
    manifest = json.loads((out / "dry_run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["scientific_validity"] is False
    assert manifest["status"] == DRY_RUN_MARKER
    metrics = json.loads((out / "metrics_summary.json").read_text(encoding="utf-8"))
    assert metrics["scientific_validity"] is False
    preds = list((out / "predictions").glob("DRY-RUN__*__test_pred.csv"))
    assert len(preds) == 6
