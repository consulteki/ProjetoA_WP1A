"""Tests for the shared ExperimentRunner framework (pre–six-model wiring)."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.dummy import DummyClassifier
from sklearn.tree import DecisionTreeClassifier

from wp1a.errors import TestSetLeakageError
from wp1a.experiment import (
    ExperimentConfig,
    ExperimentDataset,
    ExperimentRunner,
    SplitRef,
    run_all_models,
)
from wp1a.models.protocol import MODEL_IDS, REQUIRED_MODEL_COUNT
from wp1a.tracking.isolation_guard import TEST


def _toy_dataset(n_train=60, n_val=30, n_test=30, seed=0) -> ExperimentDataset:
    rng = np.random.default_rng(seed)
    X_train = rng.normal(size=(n_train, 8))
    y_train = rng.integers(0, 3, size=n_train)
    X_val = rng.normal(size=(n_val, 8))
    y_val = rng.integers(0, 3, size=n_val)
    X_test = rng.normal(size=(n_test, 8))
    y_test = rng.integers(0, 3, size=n_test)
    return ExperimentDataset(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        X_test=X_test,
        y_test=y_test,
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


def _config(model_id: str = "decision_tree", **kwargs) -> ExperimentConfig:
    base = dict(
        experiment_id="exp-framework-test",
        model_id=model_id,
        seed=42,
        dataset_version="tep-canonical-v1",
        split_manifest_path="data/processed/split_manifest_v1.json",
        preprocessor_version="preprocessor_v1",
        hyperparameters={"max_depth": 2},
        software_versions={"python": "3.12", "scikit-learn": "1.9"},
    )
    base.update(kwargs)
    return ExperimentConfig(**base)


def test_model_ids_are_exactly_six():
    assert len(MODEL_IDS) == REQUIRED_MODEL_COUNT == 6


def test_runner_lifecycle_select_freeze_fit_predict():
    ds = _toy_dataset()
    model = DecisionTreeClassifier(random_state=0)
    runner = ExperimentRunner(
        model=model, dataset=ds, split=_split(), config=_config()
    )
    result = runner.run(candidates=[{"max_depth": 1}, {"max_depth": 3}])
    assert result.y_test_pred is not None
    assert len(result.y_test_pred) == len(ds.y_test)
    assert result.frozen_hyperparameters in ({"max_depth": 1}, {"max_depth": 3})
    assert result.train_time_s is not None
    assert result.inference_time_s is not None
    assert runner.state.frozen is True


def test_runner_rejects_predict_test_before_freeze():
    ds = _toy_dataset()
    runner = ExperimentRunner(
        model=DummyClassifier(strategy="most_frequent"),
        dataset=ds,
        split=_split(),
        config=_config(
            model_id="logistic_regression",
            hyperparameters={"strategy": "most_frequent"},
        ),
    )
    with pytest.raises(TestSetLeakageError):
        runner.state.access_test()


def test_runner_rejects_second_test_access():
    ds = _toy_dataset()
    runner = ExperimentRunner(
        model=DummyClassifier(strategy="most_frequent"),
        dataset=ds,
        split=_split(),
        config=_config(
            model_id="logistic_regression",
            hyperparameters={"strategy": "most_frequent"},
        ),
    )
    runner.run()
    with pytest.raises(TestSetLeakageError, match="already been consulted"):
        runner.predict_test()


def test_select_fn_cannot_legally_include_test_in_selection_set():
    ds = _toy_dataset()
    runner = ExperimentRunner(
        model=DummyClassifier(strategy="most_frequent"),
        dataset=ds,
        split=_split(),
        config=_config(model_id="svm", hyperparameters={"strategy": "most_frequent"}),
    )

    def bad_select(**kwargs):
        # Simulate a buggy search that claims to have used test.
        from wp1a.tracking.isolation_guard import assert_test_not_used_for_selection

        assert_test_not_used_for_selection({TEST, "train"})
        return {}

    with pytest.raises(TestSetLeakageError):
        runner.select_hyperparameters(bad_select)


def test_all_models_go_through_same_runner():
    """INV-03 scaffolding: every model_id is executed via ExperimentRunner."""
    ds = _toy_dataset()
    split = _split()
    base = _config(
        model_id="logistic_regression",
        hyperparameters={"strategy": "most_frequent"},
    )
    models = {
        mid: DummyClassifier(strategy="most_frequent") for mid in MODEL_IDS
    }
    results = run_all_models(models=models, dataset=ds, split=split, base_config=base)
    assert len(results) == 6
    assert {r.model_id for r in results} == set(MODEL_IDS)
    # Shared protocol artifacts
    assert all(r.metadata["dataset_version"] == ds.dataset_version for r in results)
    assert all(
        r.metadata["split_manifest_path"].endswith("split_manifest_v1.json")
        for r in results
    )
    assert all(
        r.metadata["preprocessor_version"] == ds.preprocessor_version for r in results
    )


def test_rejects_mismatched_dataset_version():
    ds = _toy_dataset()
    with pytest.raises(ValueError, match="dataset_version"):
        ExperimentRunner(
            model=DummyClassifier(strategy="most_frequent"),
            dataset=ds,
            split=_split(),
            config=_config(
                model_id="xgboost",
                hyperparameters={},
                dataset_version="other-dataset",
            ),
        )


def test_rejects_unknown_model_id():
    with pytest.raises(ValueError, match="model_id"):
        _config(model_id="neural_net")
