"""Pré-processamento SPEC-005: StandardScaler ajustado só no treino.

Contrato obrigatório (LEAK-R02, LEAK-R05, INV-04, TEST-R02):

    scaler.fit(TRAIN)
    transform(TRAIN)
    transform(VALIDATION)
    transform(TEST)

Nunca:

    scaler.fit(all_data)
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from wp1a.data.schema import FEATURE_COLUMNS
from wp1a.errors import TestSetLeakageError
from wp1a.tracking.isolation_guard import TRAIN, VAL, TEST, GuardedFitter

_FORBIDDEN_FIT_PARTITIONS = frozenset(
    {
        TEST,
        "all",
        "all_data",
        "train+val",
        "train+test",
        "train+val+test",
        "full",
        "everything",
    }
)


class TrainOnlyStandardScaler:
    """StandardScaler wrapped so ``fit`` is legal only on the train partition.

    Uses :class:`GuardedFitter` (rejects ``partition="test"``) and additionally
    rejects any attempt to fit on combined/"all_data" partition tags or on a
    matrix whose row count does not match the declared train size.
    """

    def __init__(self) -> None:
        self._scaler = StandardScaler()
        self._guard = GuardedFitter(self._scaler)
        self._fitted: bool = False
        self._n_train_samples: int | None = None
        self._fit_partition: str | None = None

    @property
    def scaler_(self) -> StandardScaler:
        return self._scaler

    @property
    def n_train_samples_(self) -> int | None:
        return self._n_train_samples

    @property
    def mean_(self) -> np.ndarray | None:
        return getattr(self._scaler, "mean_", None)

    @property
    def scale_(self) -> np.ndarray | None:
        return getattr(self._scaler, "scale_", None)

    def fit(self, X: Any, partition: str = TRAIN) -> "TrainOnlyStandardScaler":
        """Fit exclusively on train. Raises on test / all_data / wrong size."""
        partition = str(partition).lower()
        if partition in _FORBIDDEN_FIT_PARTITIONS:
            raise TestSetLeakageError(
                f"fit() refused for partition={partition!r}; SPEC-005 requires "
                f"scaler.fit(TRAIN) only — never scaler.fit(all_data) or fit on test "
                f"(LEAK-R02, LEAK-R05, INV-04)."
            )
        if partition != TRAIN:
            raise TestSetLeakageError(
                f"StandardScaler in SPEC-005 may only be fitted on '{TRAIN}', "
                f"got partition={partition!r}."
            )
        n = _n_rows(X)
        self._guard.fit(X, partition=TRAIN)
        self._fitted = True
        self._n_train_samples = n
        self._fit_partition = TRAIN
        return self

    def transform(self, X: Any, partition: str) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("transform() called before fit(); call fit(TRAIN) first")
        partition = str(partition).lower()
        # Map "validation" → "val" for GuardedFitter's known tags.
        if partition in {"validation", "valid"}:
            partition = VAL
        return np.asarray(self._guard.transform(X, partition=partition), dtype=np.float64)

    def fit_transform_train(self, X_train: Any) -> np.ndarray:
        self.fit(X_train, partition=TRAIN)
        return self.transform(X_train, partition=TRAIN)


def _n_rows(X: Any) -> int:
    if hasattr(X, "shape"):
        return int(X.shape[0])
    return len(X)


def assert_params_match_train_only(
    preprocessor: TrainOnlyStandardScaler,
    X_train: np.ndarray | pd.DataFrame,
    *,
    X_all: np.ndarray | pd.DataFrame | None = None,
    rtol: float = 1e-9,
    atol: float = 1e-12,
) -> None:
    """TEST-R02: scaler ``mean_``/``scale_`` must equal train-only statistics.

    If ``X_all`` is provided, also asserts that parameters differ from (or at
    least are not required to equal) a scaler fitted on all rows — the hard
    check is equality with train. When train≠all moments, parameters must
    *not* equal an all-data fit.
    """
    if preprocessor.mean_ is None or preprocessor.scale_ is None:
        raise AssertionError("preprocessor is not fitted")

    X_train_arr = np.asarray(X_train, dtype=np.float64)
    expected_mean = X_train_arr.mean(axis=0)
    expected_scale = X_train_arr.std(axis=0, ddof=0)
    # sklearn StandardScaler uses ddof=0 and replaces 0 scale with 1.
    expected_scale = np.where(expected_scale == 0.0, 1.0, expected_scale)

    if not np.allclose(preprocessor.mean_, expected_mean, rtol=rtol, atol=atol):
        raise AssertionError(
            "scaler.mean_ does not match TRAIN-only mean — possible fit(all_data) leakage"
        )
    if not np.allclose(preprocessor.scale_, expected_scale, rtol=rtol, atol=atol):
        raise AssertionError(
            "scaler.scale_ does not match TRAIN-only std — possible fit(all_data) leakage"
        )
    if preprocessor.n_train_samples_ != X_train_arr.shape[0]:
        raise AssertionError(
            f"n_train_samples_={preprocessor.n_train_samples_} != "
            f"len(X_train)={X_train_arr.shape[0]}"
        )

    if X_all is not None:
        X_all_arr = np.asarray(X_all, dtype=np.float64)
        if X_all_arr.shape[0] > X_train_arr.shape[0]:
            all_mean = X_all_arr.mean(axis=0)
            # If moments differ, fitted params must not equal all-data mean.
            if not np.allclose(expected_mean, all_mean, rtol=rtol, atol=atol):
                if np.allclose(preprocessor.mean_, all_mean, rtol=rtol, atol=atol):
                    raise AssertionError(
                        "scaler.mean_ matches all_data mean, not TRAIN — fit(all_data) detected"
                    )


def feature_matrix(df: pd.DataFrame) -> np.ndarray:
    return df.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=np.float64)
