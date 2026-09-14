"""Adapters dos seis classificadores obrigatórios (MOD-1..MOD-6).

Cada adapter encapsula o estimador sklearn/xgboost e expõe
``ClassifierProtocol`` para o ``ExperimentRunner``. Nenhum treino
ad hoc fora do runner (INV-03, MET-R03).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from wp1a.models.defaults import DEFAULT_HYPERPARAMETERS
from wp1a.models.protocol import (
    MODEL_ID_TO_MOD,
    MODEL_IDS,
    REQUIRED_MODEL_COUNT,
    ClassifierProtocol,
)

try:
    from xgboost import XGBClassifier
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "xgboost is required for MOD-6; install with: pip install 'xgboost>=2.0'"
    ) from exc

from sklearn.preprocessing import LabelEncoder


def _merge_params(model_id: str, overrides: dict[str, Any]) -> dict[str, Any]:
    params = dict(DEFAULT_HYPERPARAMETERS[model_id])
    params.update(overrides)
    return params


class LabelEncodedClassifier:
    """Wraps an estimator so non-contiguous integer labels (e.g. {9,13,19}) work.

    Required for XGBoost when a run-subsample does not include every class id.
    """

    def __init__(self, estimator: Any) -> None:
        self.estimator = estimator
        self._le: LabelEncoder | None = None

    def get_params(self, deep: bool = True) -> dict[str, Any]:
        return self.estimator.get_params(deep=deep)

    def set_params(self, **params: Any) -> "LabelEncodedClassifier":
        self.estimator.set_params(**params)
        return self

    def fit(self, X: Any, y: Any) -> "LabelEncodedClassifier":
        self._le = LabelEncoder()
        y_enc = self._le.fit_transform(np.asarray(y))
        self.estimator.fit(X, y_enc)
        return self

    def predict(self, X: Any) -> np.ndarray:
        if self._le is None:
            raise RuntimeError("LabelEncodedClassifier must be fit before predict")
        pred = np.asarray(self.estimator.predict(X))
        return self._le.inverse_transform(pred)

    def predict_proba(self, X: Any) -> np.ndarray:
        return np.asarray(self.estimator.predict_proba(X))

    def __sklearn_clone__(self) -> "LabelEncodedClassifier":
        from sklearn.base import clone

        return LabelEncodedClassifier(clone(self.estimator))


@dataclass
class ModelAdapter:
    """Wrapper uniforme: identidade MOD-* + estimador sklearn-like."""

    model_id: str
    estimator: Any
    mod_code: str = field(init=False)

    def __post_init__(self) -> None:
        if self.model_id not in MODEL_IDS:
            raise ValueError(f"unknown model_id={self.model_id!r}; expected one of {MODEL_IDS}")
        self.mod_code = MODEL_ID_TO_MOD[self.model_id]

    def __deepcopy__(self, memo: dict[int, Any]) -> "ModelAdapter":
        # sklearn.clone is safer than copy.deepcopy for estimators (esp. XGBoost).
        from sklearn.base import clone

        est = clone(self.estimator)
        copied = ModelAdapter(model_id=self.model_id, estimator=est)
        memo[id(self)] = copied
        return copied

    # --- ClassifierProtocol -------------------------------------------------

    def get_params(self, deep: bool = True) -> dict[str, Any]:
        return self.estimator.get_params(deep=deep)

    def set_params(self, **params: Any) -> "ModelAdapter":
        self.estimator.set_params(**params)
        return self

    def fit(self, X: Any, y: Any) -> "ModelAdapter":
        self.estimator.fit(X, y)
        return self

    def predict(self, X: Any) -> np.ndarray:
        return np.asarray(self.estimator.predict(X))

    def predict_proba(self, X: Any) -> np.ndarray:
        if not hasattr(self.estimator, "predict_proba"):
            raise AttributeError(f"{self.model_id} estimator has no predict_proba")
        return np.asarray(self.estimator.predict_proba(X))


def make_logistic_regression(seed: int = 42, **overrides: Any) -> ModelAdapter:
    params = _merge_params("logistic_regression", overrides)
    est = LogisticRegression(**params, random_state=seed)
    return ModelAdapter(model_id="logistic_regression", estimator=est)


def make_decision_tree(seed: int = 42, **overrides: Any) -> ModelAdapter:
    params = _merge_params("decision_tree", overrides)
    est = DecisionTreeClassifier(**params, random_state=seed)
    return ModelAdapter(model_id="decision_tree", estimator=est)


def make_random_forest(seed: int = 42, **overrides: Any) -> ModelAdapter:
    params = _merge_params("random_forest", overrides)
    est = RandomForestClassifier(**params, random_state=seed)
    return ModelAdapter(model_id="random_forest", estimator=est)


def make_gradient_boosting(seed: int = 42, **overrides: Any) -> ModelAdapter:
    params = _merge_params("gradient_boosting", overrides)
    est = GradientBoostingClassifier(**params, random_state=seed)
    return ModelAdapter(model_id="gradient_boosting", estimator=est)


def make_svm(seed: int = 42, **overrides: Any) -> ModelAdapter:
    params = _merge_params("svm", overrides)
    est = SVC(**params, random_state=seed)
    return ModelAdapter(model_id="svm", estimator=est)


def make_xgboost(seed: int = 42, **overrides: Any) -> ModelAdapter:
    params = _merge_params("xgboost", overrides)
    # Force CPU — avoids CUDA driver errors on hosts without a usable GPU.
    params.setdefault("device", "cpu")
    params.setdefault("tree_method", "hist")
    # Label encoding keeps MOD-6 usable when a subsample omits some class ids.
    est = LabelEncodedClassifier(
        XGBClassifier(**params, random_state=seed, verbosity=0)
    )
    return ModelAdapter(model_id="xgboost", estimator=est)


ADAPTER_FACTORY: dict[str, Any] = {
    "logistic_regression": make_logistic_regression,
    "decision_tree": make_decision_tree,
    "random_forest": make_random_forest,
    "gradient_boosting": make_gradient_boosting,
    "svm": make_svm,
    "xgboost": make_xgboost,
}

assert set(ADAPTER_FACTORY) == set(MODEL_IDS)
assert len(ADAPTER_FACTORY) == REQUIRED_MODEL_COUNT


def build_adapter(model_id: str, *, seed: int = 42, **overrides: Any) -> ModelAdapter:
    """Build one of the six mandatory adapters by ``model_id``."""
    if model_id not in ADAPTER_FACTORY:
        raise ValueError(f"model_id={model_id!r} not in {MODEL_IDS}")
    adapter = ADAPTER_FACTORY[model_id](seed=seed, **overrides)
    # Structural check against the shared protocol.
    assert isinstance(adapter, ClassifierProtocol)
    return adapter


def build_all_adapters(*, seed: int = 42) -> dict[str, ModelAdapter]:
    """Instantiate all six adapters (same seed / shared protocol)."""
    return {model_id: build_adapter(model_id, seed=seed) for model_id in MODEL_IDS}
