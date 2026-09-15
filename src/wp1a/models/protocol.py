"""Contrato comum dos classificadores do benchmark WP1A (SPEC-006).

Os seis modelos (MOD-1..MOD-6) DEVEM implementar este protocolo e ser
executados exclusivamente via :class:`wp1a.experiment.ExperimentRunner`
— nunca por caminhos de treino ad hoc (INV-03, MET-R03).
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import numpy as np

# Identificadores canônicos (ADR-006 / configs/models.yaml).
MODEL_IDS: tuple[str, ...] = (
    "logistic_regression",  # MOD-1
    "decision_tree",        # MOD-2
    "random_forest",        # MOD-3
    "gradient_boosting",    # MOD-4
    "svm",                  # MOD-5
    "xgboost",              # MOD-6
)

MODEL_ID_TO_MOD: dict[str, str] = {
    "logistic_regression": "MOD-1",
    "decision_tree": "MOD-2",
    "random_forest": "MOD-3",
    "gradient_boosting": "MOD-4",
    "svm": "MOD-5",
    "xgboost": "MOD-6",
}


@runtime_checkable
class ClassifierProtocol(Protocol):
    """Minimal sklearn-like estimator interface required by ExperimentRunner."""

    def get_params(self, deep: bool = True) -> dict[str, Any]: ...

    def set_params(self, **params: Any) -> Any: ...

    def fit(self, X: Any, y: Any) -> Any: ...

    def predict(self, X: Any) -> np.ndarray: ...


REQUIRED_MODEL_COUNT = 6

assert len(MODEL_IDS) == REQUIRED_MODEL_COUNT
