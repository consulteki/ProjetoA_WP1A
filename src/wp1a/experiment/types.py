"""Objetos de configuração, dados e split injetados no ExperimentRunner."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from wp1a.data.schema import CLASS_LABEL_COLUMN, FEATURE_COLUMNS, RUN_ID_COLUMN
from wp1a.errors import CanonicalDatasetError
from wp1a.models.protocol import MODEL_IDS, MODEL_ID_TO_MOD
from wp1a.preprocessing.pipeline import PREPROCESSOR_VERSION
from wp1a.splitting.manifest import MANIFEST_VERSION
from wp1a.tracking.isolation_guard import TEST, TRAIN, VAL


@dataclass(frozen=True)
class ExperimentConfig:
    """Configuração explícita de um experimento (ADR-005)."""

    experiment_id: str
    model_id: str
    seed: int
    dataset_version: str
    split_manifest_path: str
    preprocessor_version: str
    hyperparameters: dict[str, Any]
    software_versions: dict[str, str] = field(default_factory=dict)
    timestamp: str | None = None
    frozen: bool = False

    def __post_init__(self) -> None:
        if self.model_id not in MODEL_IDS:
            raise ValueError(
                f"model_id={self.model_id!r} not in mandatory set {MODEL_IDS}"
            )
        if not self.experiment_id:
            raise ValueError("experiment_id must be non-empty")
        if not isinstance(self.hyperparameters, dict):
            raise ValueError("hyperparameters must be a dict")

    @property
    def mod_code(self) -> str:
        return MODEL_ID_TO_MOD[self.model_id]

    def with_hyperparameters(self, hyperparameters: dict[str, Any]) -> "ExperimentConfig":
        return ExperimentConfig(
            experiment_id=self.experiment_id,
            model_id=self.model_id,
            seed=self.seed,
            dataset_version=self.dataset_version,
            split_manifest_path=self.split_manifest_path,
            preprocessor_version=self.preprocessor_version,
            hyperparameters=dict(hyperparameters),
            software_versions=dict(self.software_versions),
            timestamp=self.timestamp,
            frozen=self.frozen,
        )

    def as_metadata(self) -> dict[str, Any]:
        """Payload compatible with ``validate_experiment_metadata``."""
        return {
            "experiment_id": self.experiment_id,
            "seed": self.seed,
            "dataset_version": self.dataset_version,
            "split_manifest_path": self.split_manifest_path,
            "software_versions": self.software_versions
            or {"python": "unspecified", "note": "fill before published run"},
            "hyperparameters": self.hyperparameters,
            "timestamp": self.timestamp or "pending",
            "model_id": self.model_id,
            "mod_code": self.mod_code,
            "preprocessor_version": self.preprocessor_version,
            "frozen": self.frozen,
        }


@dataclass(frozen=True)
class SplitRef:
    """Referência imutável ao manifesto A3 compartilhado por todos os modelos."""

    manifest_version: str
    path: str
    train_runs: tuple[str, ...]
    validation_runs: tuple[str, ...]
    test_runs: tuple[str, ...]
    seed: int

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any], *, path: str) -> "SplitRef":
        return cls(
            manifest_version=str(manifest.get("manifest_version", MANIFEST_VERSION)),
            path=path,
            train_runs=tuple(manifest["train_runs"]),
            validation_runs=tuple(manifest["validation_runs"]),
            test_runs=tuple(manifest["test_runs"]),
            seed=int(manifest["seed"]),
        )


@dataclass
class ExperimentDataset:
    """Partições pré-processadas (SPEC-005) usadas pelo runner.

    Todos os classificadores recebem a *mesma* instância (ou cópias com o
    mesmo conteúdo) — INV-03.
    """

    X_train: np.ndarray
    y_train: np.ndarray
    X_val: np.ndarray
    y_val: np.ndarray
    X_test: np.ndarray
    y_test: np.ndarray
    run_id_train: np.ndarray
    run_id_val: np.ndarray
    run_id_test: np.ndarray
    dataset_version: str
    preprocessor_version: str

    def partition_xy(self, partition: str) -> tuple[np.ndarray, np.ndarray]:
        if partition == TRAIN:
            return self.X_train, self.y_train
        if partition == VAL:
            return self.X_val, self.y_val
        if partition == TEST:
            return self.X_test, self.y_test
        raise ValueError(f"unknown partition {partition!r}")


def _xy_from_frame(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    X = df.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=np.float64)
    y = df[CLASS_LABEL_COLUMN].to_numpy()
    runs = df[RUN_ID_COLUMN].to_numpy()
    return X, y, runs


def load_experiment_dataset(
    processed_dir: Path,
    *,
    dataset_version: str,
    preprocessor_version: str = PREPROCESSOR_VERSION,
) -> ExperimentDataset:
    """Load the three preprocessed partition tables produced by SPEC-005."""
    processed_dir = Path(processed_dir)
    paths = {
        TRAIN: processed_dir / f"{preprocessor_version}_train.csv.gz",
        VAL: processed_dir / f"{preprocessor_version}_validation.csv.gz",
        TEST: processed_dir / f"{preprocessor_version}_test.csv.gz",
    }
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        raise CanonicalDatasetError(
            f"preprocessed partitions missing (run make preprocess): {missing}"
        )
    frames = {k: pd.read_csv(p, compression="gzip") for k, p in paths.items()}
    Xt, yt, rt = _xy_from_frame(frames[TRAIN])
    Xv, yv, rv = _xy_from_frame(frames[VAL])
    Xs, ys, rs = _xy_from_frame(frames[TEST])
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
        dataset_version=dataset_version,
        preprocessor_version=preprocessor_version,
    )
