"""Tests that reject use of the test partition during fit or during
hyperparameter/model selection.

Reference: docs/adr/ADR-002-test-set-isolation.md;
docs/specs/SPEC-000-master.md INV-05;
skill ml-training (skills/ml-training/SKILL.md).
"""

from __future__ import annotations

import pytest

from wp1a.errors import TestSetLeakageError
from wp1a.tracking.isolation_guard import (
    ExperimentState,
    GuardedFitter,
    assert_test_not_used_for_selection,
)


class _DummyEstimator:
    """Minimal stand-in for a scaler/model exposing fit/transform, used only
    to exercise GuardedFitter. Not part of the (not yet implemented) ML
    pipeline.
    """

    def __init__(self) -> None:
        self.fitted_on_n_: int | None = None

    def fit(self, X):
        self.fitted_on_n_ = len(X)
        return self

    def transform(self, X):
        return X


def test_fit_on_train_is_allowed(valid_dataset):
    fitter = GuardedFitter(_DummyEstimator())
    fitter.fit(valid_dataset, partition="train")  # must not raise


def test_fit_on_validation_is_allowed(valid_dataset):
    fitter = GuardedFitter(_DummyEstimator())
    fitter.fit(valid_dataset, partition="val")  # must not raise


def test_rejects_fit_on_test_partition(valid_dataset):
    fitter = GuardedFitter(_DummyEstimator())
    with pytest.raises(TestSetLeakageError, match="fit"):
        fitter.fit(valid_dataset, partition="test")


def test_transform_on_test_partition_is_allowed(valid_dataset):
    fitter = GuardedFitter(_DummyEstimator())
    fitter.fit(valid_dataset, partition="train")
    fitter.transform(valid_dataset, partition="test")  # must not raise: transform != fit


def test_rejects_unknown_partition_tag(valid_dataset):
    fitter = GuardedFitter(_DummyEstimator())
    with pytest.raises(ValueError, match="unknown partition"):
        fitter.fit(valid_dataset, partition="holdout")


def test_rejects_test_used_for_hyperparameter_selection():
    with pytest.raises(TestSetLeakageError, match="selection"):
        assert_test_not_used_for_selection({"train", "val", "test"})


def test_allows_selection_using_only_train_and_val():
    assert_test_not_used_for_selection({"train", "val"})  # must not raise


def test_rejects_test_access_before_freeze():
    state = ExperimentState()
    with pytest.raises(TestSetLeakageError, match="frozen"):
        state.access_test()


def test_allows_single_test_access_after_freeze():
    state = ExperimentState()
    state.freeze()
    state.access_test()  # must not raise
    assert state.frozen is True


def test_rejects_second_test_access_after_freeze():
    """LEAK-R06: once the test set has been consulted for a frozen
    configuration, iterating on that same configuration using test
    feedback is rejected — a new experiment id is required instead.
    """
    state = ExperimentState()
    state.freeze()
    state.access_test()
    with pytest.raises(TestSetLeakageError, match="already been consulted"):
        state.access_test()
