"""Unit tests for MOD-1..MOD-6 model adapters."""

from __future__ import annotations

import numpy as np
import pytest

from wp1a.experiment import (
    ExperimentConfig,
    ExperimentDataset,
    ExperimentRunner,
    SplitRef,
    run_all_models,
)
from wp1a.models import (
    MODEL_IDS,
    MODEL_ID_TO_MOD,
    REQUIRED_MODEL_COUNT,
    ClassifierProtocol,
    ModelAdapter,
    build_adapter,
    build_all_adapters,
)
from wp1a.models.defaults import DEFAULT_HYPERPARAMETERS


def _toy_xy(n=40, n_features=6, n_classes=3, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, n_features))
    y = rng.integers(0, n_classes, size=n)
    return X, y


def _toy_dataset(n_train=48, n_val=24, n_test=24, seed=0) -> ExperimentDataset:
    rng = np.random.default_rng(seed)
    n_features, n_classes = 6, 3
    return ExperimentDataset(
        X_train=rng.normal(size=(n_train, n_features)),
        y_train=rng.integers(0, n_classes, size=n_train),
        X_val=rng.normal(size=(n_val, n_features)),
        y_val=rng.integers(0, n_classes, size=n_val),
        X_test=rng.normal(size=(n_test, n_features)),
        y_test=rng.integers(0, n_classes, size=n_test),
        run_id_train=np.array([f"tr{i}" for i in range(n_train)]),
        run_id_val=np.array([f"va{i}" for i in range(n_val)]),
        run_id_test=np.array([f"te{i}" for i in range(n_test)]),
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


def _config(model_id: str) -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id=f"exp-adapter-{model_id}",
        model_id=model_id,
        seed=42,
        dataset_version="tep-canonical-v1",
        split_manifest_path="data/processed/split_manifest_v1.json",
        preprocessor_version="preprocessor_v1",
        hyperparameters=dict(DEFAULT_HYPERPARAMETERS[model_id]),
        software_versions={"python": "3.12", "scikit-learn": "1.x", "xgboost": "2.x"},
    )


def test_exactly_six_adapters_and_defaults():
    assert len(MODEL_IDS) == REQUIRED_MODEL_COUNT == 6
    assert set(DEFAULT_HYPERPARAMETERS) == set(MODEL_IDS)
    adapters = build_all_adapters(seed=0)
    assert set(adapters) == set(MODEL_IDS)
    for model_id, adapter in adapters.items():
        assert isinstance(adapter, ModelAdapter)
        assert isinstance(adapter, ClassifierProtocol)
        assert adapter.model_id == model_id
        assert adapter.mod_code == MODEL_ID_TO_MOD[model_id]


@pytest.mark.parametrize("model_id", MODEL_IDS)
def test_adapter_fit_predict_roundtrip(model_id: str):
    X, y = _toy_xy()
    adapter = build_adapter(model_id, seed=0)
    adapter.fit(X, y)
    pred = adapter.predict(X)
    assert pred.shape == y.shape
    assert set(np.unique(pred)).issubset(set(np.unique(y)))


@pytest.mark.parametrize("model_id", MODEL_IDS)
def test_adapter_get_set_params(model_id: str):
    adapter = build_adapter(model_id, seed=1)
    params = adapter.get_params(deep=False)
    assert isinstance(params, dict)
    # Apply a known default key back via set_params (protocol contract).
    key = next(iter(DEFAULT_HYPERPARAMETERS[model_id]))
    value = DEFAULT_HYPERPARAMETERS[model_id][key]
    adapter.set_params(**{key: value})
    assert adapter.get_params()[key] == value


def test_unknown_model_id_rejected():
    with pytest.raises(ValueError, match="not in"):
        build_adapter("not_a_model")


@pytest.mark.parametrize("model_id", MODEL_IDS)
def test_each_adapter_through_experiment_runner(model_id: str):
    ds = _toy_dataset()
    adapter = build_adapter(model_id, seed=42)
    runner = ExperimentRunner(
        model=adapter,
        dataset=ds,
        split=_split(),
        config=_config(model_id),
    )
    result = runner.run()
    assert result.model_id == model_id
    assert result.y_test_pred is not None
    assert len(result.y_test_pred) == len(ds.y_test)
    assert result.train_time_s is not None
    assert result.inference_time_s is not None
    assert result.frozen_hyperparameters


def test_run_all_models_with_six_adapters():
    ds = _toy_dataset()
    models = build_all_adapters(seed=42)
    # Shared base config (INV-03); per-model defaults via candidates so set_params
    # never applies LR keys to SVM, etc.
    base = ExperimentConfig(
        experiment_id="exp-adapter-all",
        model_id="logistic_regression",
        seed=42,
        dataset_version="tep-canonical-v1",
        split_manifest_path="data/processed/split_manifest_v1.json",
        preprocessor_version="preprocessor_v1",
        hyperparameters={"C": 1.0},
        software_versions={"python": "3.12", "scikit-learn": "1.x", "xgboost": "2.x"},
    )
    candidates = {mid: [dict(DEFAULT_HYPERPARAMETERS[mid])] for mid in MODEL_IDS}
    results = run_all_models(
        models=models,
        dataset=ds,
        split=_split(),
        base_config=base,
        candidates_by_model=candidates,
    )
    assert len(results) == 6
    assert {r.model_id for r in results} == set(MODEL_IDS)
