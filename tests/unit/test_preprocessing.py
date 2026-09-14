"""Tests for SPEC-005 preprocessing — fit(TRAIN) only, never fit(all_data)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.preprocessing import StandardScaler

from wp1a.data.schema import (
    CLASS_LABEL_COLUMN,
    FEATURE_COLUMNS,
    RUN_ID_COLUMN,
    SAMPLE_INDEX_COLUMN,
    SOURCE_FILE_COLUMN,
    SOURCE_SPLIT_COLUMN,
)
from wp1a.errors import TestSetLeakageError
from wp1a.preprocessing.pipeline import (
    apply_train_only_scaling,
    refuse_fit_all_data,
    run_preprocessing,
    split_canonical_by_manifest,
)
from wp1a.preprocessing.scaler import (
    TrainOnlyStandardScaler,
    assert_params_match_train_only,
    feature_matrix,
)
from wp1a.tracking.isolation_guard import GuardedFitter


def _toy_partitions(n_train: int = 40, n_val: int = 20, n_test: int = 20, seed: int = 0):
    rng = np.random.default_rng(seed)

    def _frame(n: int, run_prefix: str, class_label: int, loc: float) -> pd.DataFrame:
        data = {c: rng.normal(loc=loc, scale=1.0, size=n) for c in FEATURE_COLUMNS}
        data[RUN_ID_COLUMN] = [f"{run_prefix}_{i // 5}" for i in range(n)]
        data[CLASS_LABEL_COLUMN] = class_label
        data[SOURCE_FILE_COLUMN] = f"{run_prefix}.dat"
        data[SOURCE_SPLIT_COLUMN] = "braatz_train"
        data[SAMPLE_INDEX_COLUMN] = np.arange(n, dtype=np.int64)
        return pd.DataFrame(data)

    # Distinct means so train-only ≠ all-data moments.
    train = _frame(n_train, "tr", 0, loc=0.0)
    val = _frame(n_val, "va", 1, loc=5.0)
    test = _frame(n_test, "te", 2, loc=-5.0)
    return {"train": train, "val": val, "test": test}


def test_fit_train_then_transform_all_partitions():
    parts = _toy_partitions()
    X_train = feature_matrix(parts["train"])
    X_val = feature_matrix(parts["val"])
    X_test = feature_matrix(parts["test"])

    scaler = TrainOnlyStandardScaler()
    scaler.fit(X_train, partition="train")
    Z_train = scaler.transform(X_train, partition="train")
    Z_val = scaler.transform(X_val, partition="validation")
    Z_test = scaler.transform(X_test, partition="test")

    assert Z_train.shape == X_train.shape
    assert Z_val.shape == X_val.shape
    assert Z_test.shape == X_test.shape
    assert_params_match_train_only(
        scaler, X_train, X_all=np.vstack([X_train, X_val, X_test])
    )


def test_never_fit_all_data_partition_tag():
    parts = _toy_partitions()
    X_all = feature_matrix(pd.concat([parts["train"], parts["val"], parts["test"]]))
    scaler = TrainOnlyStandardScaler()
    with pytest.raises(TestSetLeakageError, match="all_data|TRAIN"):
        refuse_fit_all_data(scaler, X_all)
    with pytest.raises(TestSetLeakageError, match="all_data|TRAIN"):
        scaler.fit(X_all, partition="all")
    with pytest.raises(TestSetLeakageError, match="all_data|TRAIN"):
        scaler.fit(X_all, partition="train+val+test")


def test_never_fit_on_test_partition():
    parts = _toy_partitions()
    scaler = TrainOnlyStandardScaler()
    with pytest.raises(TestSetLeakageError):
        scaler.fit(feature_matrix(parts["test"]), partition="test")


def test_params_differ_from_all_data_fit_when_distributions_differ():
    parts = _toy_partitions()
    X_train = feature_matrix(parts["train"])
    X_all = feature_matrix(pd.concat([parts["train"], parts["val"], parts["test"]]))

    ours = TrainOnlyStandardScaler()
    ours.fit(X_train, partition="train")

    leaked = StandardScaler().fit(X_all)
    assert not np.allclose(ours.mean_, leaked.mean_)
    assert_params_match_train_only(ours, X_train, X_all=X_all)


def test_apply_train_only_scaling_pipeline():
    parts = _toy_partitions()
    scaled, scaler = apply_train_only_scaling(parts)
    assert set(scaled) == {"train", "val", "test"}
    X_train = feature_matrix(parts["train"])
    assert_params_match_train_only(
        scaler,
        X_train,
        X_all=feature_matrix(pd.concat(list(parts.values()))),
    )
    # Transformed train features ~ zero mean (ddof=0).
    Z_train = feature_matrix(scaled["train"])
    assert np.allclose(Z_train.mean(axis=0), 0.0, atol=1e-9)


def test_guarded_fitter_still_rejects_test_fit():
    """SPEC-005 acceptance: methodology guard remains wired."""
    est = StandardScaler()
    guard = GuardedFitter(est)
    X = np.ones((10, 52))
    with pytest.raises(TestSetLeakageError, match="fit"):
        guard.fit(X, partition="test")
    guard.fit(X, partition="train")
    guard.transform(X, partition="test")


def test_run_preprocessing_end_to_end(tmp_path: Path):
    """Minimal canonical + A3 → preprocessed artifacts."""
    from wp1a.data.canonical import CANONICAL_TABLE_NAME, DATASET_VERSION, REGISTRY_NAME
    from wp1a.splitting.manifest import MANIFEST_FILENAME

    rng = np.random.default_rng(1)
    frames = []
    run_class = {}
    for c in range(21):
        for tag, split in (("tr", "braatz_train"), ("te", "braatz_test")):
            rid = f"braatz_{tag}_fault{c:02d}"
            run_class[rid] = c
            n = 8
            data = {col: rng.normal(size=n) for col in FEATURE_COLUMNS}
            data[RUN_ID_COLUMN] = rid
            data[CLASS_LABEL_COLUMN] = c
            data[SOURCE_FILE_COLUMN] = f"d{c:02d}.dat"
            data[SOURCE_SPLIT_COLUMN] = split
            data[SAMPLE_INDEX_COLUMN] = np.arange(n, dtype=np.int64)
            frames.append(pd.DataFrame(data))
    df = pd.concat(frames, ignore_index=True)

    # Simple A3: one run/class train, rest split val/test like production strategy.
    train_runs, val_runs, test_runs = [], [], []
    for c in range(21):
        train_runs.append(f"braatz_tr_fault{c:02d}")
        if c % 2 == 0:
            val_runs.append(f"braatz_te_fault{c:02d}")
        else:
            test_runs.append(f"braatz_te_fault{c:02d}")

    processed = tmp_path / "processed"
    processed.mkdir()
    df.to_csv(processed / CANONICAL_TABLE_NAME, index=False, compression="gzip")
    (processed / REGISTRY_NAME).write_text(
        json.dumps({"dataset_version": DATASET_VERSION, "status": "canonical"}),
        encoding="utf-8",
    )
    (processed / MANIFEST_FILENAME).write_text(
        json.dumps(
            {
                "manifest_version": "split_manifest_v1",
                "seed": 42,
                "train_runs": train_runs,
                "validation_runs": val_runs,
                "test_runs": test_runs,
                "partitions": {"train": train_runs, "val": val_runs, "test": test_runs},
                "run_class_map": run_class,
            }
        ),
        encoding="utf-8",
    )

    written = run_preprocessing(processed_dir=processed, metadata_dir=tmp_path / "meta")
    assert written["train"].is_file()
    assert written["val"].is_file()
    assert written["test"].is_file()
    params = json.loads(written["scaler_params"].read_text(encoding="utf-8"))
    assert params["scaler"]["fitted_on_partition"] == "train"
    assert "fit(all_data)" in params["transformations"][0]["forbidden"]

    # Reload and confirm mean_ == train-only.
    parts = split_canonical_by_manifest(df, json.loads((processed / MANIFEST_FILENAME).read_text()))
    X_train = feature_matrix(parts["train"])
    expected_mean = X_train.mean(axis=0)
    assert np.allclose(params["scaler"]["mean_"], expected_mean)
