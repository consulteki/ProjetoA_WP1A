"""Orquestração do pré-processamento SPEC-005 sobre o dataset canônico + A3."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from wp1a.data.canonical import DATASET_VERSION, load_canonical_dataframe, load_canonical_registry
from wp1a.data.schema import (
    CLASS_LABEL_COLUMN,
    FEATURE_COLUMNS,
    RUN_ID_COLUMN,
    SAMPLE_INDEX_COLUMN,
    SOURCE_FILE_COLUMN,
    SOURCE_SPLIT_COLUMN,
)
from wp1a.errors import CanonicalDatasetError, TestSetLeakageError
from wp1a.preprocessing.scaler import (
    TrainOnlyStandardScaler,
    assert_params_match_train_only,
    feature_matrix,
)
from wp1a.splitting.manifest import MANIFEST_FILENAME, load_split_manifest
from wp1a.splitting.run_leakage import check_run_disjoint
from wp1a.tracking.isolation_guard import TEST, TRAIN, VAL

PREPROCESSOR_VERSION = "preprocessor_v1"
META_COLUMNS = (
    RUN_ID_COLUMN,
    CLASS_LABEL_COLUMN,
    SOURCE_FILE_COLUMN,
    SOURCE_SPLIT_COLUMN,
    SAMPLE_INDEX_COLUMN,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def split_canonical_by_manifest(
    df: pd.DataFrame, manifest: dict[str, Any]
) -> dict[str, pd.DataFrame]:
    """Slice canonical rows by A3 run lists (unit = run_id)."""
    check_run_disjoint(
        manifest["train_runs"],
        manifest["validation_runs"],
        manifest["test_runs"],
    )
    frames = {
        TRAIN: df[df[RUN_ID_COLUMN].isin(manifest["train_runs"])].copy(),
        VAL: df[df[RUN_ID_COLUMN].isin(manifest["validation_runs"])].copy(),
        TEST: df[df[RUN_ID_COLUMN].isin(manifest["test_runs"])].copy(),
    }
    for name, part in frames.items():
        if part.empty:
            raise CanonicalDatasetError(f"partition {name!r} has zero rows after split")
    n_total = sum(len(p) for p in frames.values())
    if n_total != len(df):
        raise CanonicalDatasetError(
            f"partition row count {n_total} != canonical rows {len(df)} "
            "(runs missing from manifesto or overlap)"
        )
    return frames


def apply_train_only_scaling(
    partitions: dict[str, pd.DataFrame],
) -> tuple[dict[str, pd.DataFrame], TrainOnlyStandardScaler]:
    """fit(TRAIN) then transform(TRAIN), transform(VAL), transform(TEST)."""
    X_train = feature_matrix(partitions[TRAIN])
    X_val = feature_matrix(partitions[VAL])
    X_test = feature_matrix(partitions[TEST])
    X_all = np.vstack([X_train, X_val, X_test])

    scaler = TrainOnlyStandardScaler()
    # Required sequence:
    scaler.fit(X_train, partition=TRAIN)
    Z_train = scaler.transform(X_train, partition=TRAIN)
    Z_val = scaler.transform(X_val, partition=VAL)
    Z_test = scaler.transform(X_test, partition=TEST)

    # Automated leakage check (TEST-R02).
    assert_params_match_train_only(scaler, X_train, X_all=X_all)

    out = {
        TRAIN: _replace_features(partitions[TRAIN], Z_train),
        VAL: _replace_features(partitions[VAL], Z_val),
        TEST: _replace_features(partitions[TEST], Z_test),
    }
    return out, scaler


def _replace_features(df: pd.DataFrame, Z: np.ndarray) -> pd.DataFrame:
    out = df.copy()
    out.loc[:, list(FEATURE_COLUMNS)] = Z
    return out


def scaler_params_dict(scaler: TrainOnlyStandardScaler) -> dict[str, Any]:
    if scaler.mean_ is None or scaler.scale_ is None:
        raise RuntimeError("scaler not fitted")
    return {
        "type": "StandardScaler",
        "fitted_on_partition": TRAIN,
        "n_train_samples": scaler.n_train_samples_,
        "n_features": int(len(FEATURE_COLUMNS)),
        "feature_columns": list(FEATURE_COLUMNS),
        "mean_": scaler.mean_.tolist(),
        "scale_": scaler.scale_.tolist(),
        "with_mean": True,
        "with_std": True,
    }


def run_preprocessing(
    *,
    processed_dir: Path,
    metadata_dir: Path | None = None,
) -> dict[str, Path]:
    """End-to-end SPEC-005: load canonical+A3, fit train-only scaler, persist."""
    processed_dir = Path(processed_dir)
    registry = load_canonical_registry(processed_dir)
    if registry.get("dataset_version") != DATASET_VERSION:
        raise CanonicalDatasetError(
            f"preprocessing requires dataset_version={DATASET_VERSION!r}"
        )
    manifest = load_split_manifest(processed_dir)
    df = load_canonical_dataframe(processed_dir)
    partitions = split_canonical_by_manifest(df, manifest)
    scaled, scaler = apply_train_only_scaling(partitions)

    written: dict[str, Path] = {}
    file_map = {
        TRAIN: f"{PREPROCESSOR_VERSION}_train.csv.gz",
        VAL: f"{PREPROCESSOR_VERSION}_validation.csv.gz",
        TEST: f"{PREPROCESSOR_VERSION}_test.csv.gz",
    }
    for key, filename in file_map.items():
        path = processed_dir / filename
        scaled[key].to_csv(path, index=False, compression="gzip")
        written[key] = path

    params_path = processed_dir / f"{PREPROCESSOR_VERSION}_scaler_params.json"
    params_payload = {
        "preprocessor_version": PREPROCESSOR_VERSION,
        "spec": "SPEC-005",
        "created_at": _utc_now(),
        "dataset_version": registry.get("dataset_version"),
        "split_manifest_version": manifest.get("manifest_version"),
        "split_seed": manifest.get("seed"),
        "transformations": [
            {
                "order": 1,
                "name": "standard_scaler",
                "fit": "train_only",
                "transform": ["train", "validation", "test"],
                "forbidden": ["fit(all_data)", "fit(test)", "refit on val/test"],
            }
        ],
        "scaler": scaler_params_dict(scaler),
        "partition_row_counts": {
            "train": int(len(scaled[TRAIN])),
            "validation": int(len(scaled[VAL])),
            "test": int(len(scaled[TEST])),
        },
        "artifacts": {
            "train": f"data/processed/{file_map[TRAIN]}",
            "validation": f"data/processed/{file_map[VAL]}",
            "test": f"data/processed/{file_map[TEST]}",
            "scaler_params": f"data/processed/{params_path.name}",
        },
    }
    params_path.write_text(
        json.dumps(params_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    written["scaler_params"] = params_path

    registry_path = processed_dir / "preprocessing_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "status": "ready_for_training",
                "preprocessor_version": PREPROCESSOR_VERSION,
                "dataset_version": registry.get("dataset_version"),
                "split_manifest": MANIFEST_FILENAME,
                "created_at": params_payload["created_at"],
                "fit_policy": "scaler.fit(TRAIN) only; transform(TRAIN|VAL|TEST); never fit(all_data)",
                "artifacts": params_payload["artifacts"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    written["registry"] = registry_path

    if metadata_dir is not None:
        metadata_dir = Path(metadata_dir)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        meta = metadata_dir / "preprocessing.json"
        meta.write_text(
            json.dumps(
                {
                    "preprocessor_version": PREPROCESSOR_VERSION,
                    "created_at": params_payload["created_at"],
                    "n_train": params_payload["partition_row_counts"]["train"],
                    "n_validation": params_payload["partition_row_counts"]["validation"],
                    "n_test": params_payload["partition_row_counts"]["test"],
                    "fit_partition": TRAIN,
                    "artifacts": params_payload["artifacts"],
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        written["metadata"] = meta

    return written


def refuse_fit_all_data(scaler: TrainOnlyStandardScaler, X_all: Any) -> None:
    """Helper used by tests: attempting fit(all_data) must raise."""
    scaler.fit(X_all, partition="all_data")
