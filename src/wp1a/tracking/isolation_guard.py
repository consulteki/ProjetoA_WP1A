"""Test-set isolation guards.

Reference: docs/adr/ADR-002-test-set-isolation.md;
docs/specs/SPEC-000-master.md §7.5, INV-05;
AGENTS.md LEAK-R02, LEAK-R03, LEAK-R05, LEAK-R06.

These guards do not implement preprocessing or model training; they wrap
*any* estimator/search routine (present or future) and enforce, by
construction, that:

1. ``fit`` is never called with data tagged as the 'test' partition.
2. Hyperparameter/model selection never references the 'test' partition.
3. The test partition is only accessed after the experiment configuration
   has been frozen, and only once per experiment.
"""

from __future__ import annotations

from typing import Any, Protocol

from wp1a.errors import TestSetLeakageError

TRAIN = "train"
VAL = "val"
TEST = "test"
_KNOWN_PARTITIONS = frozenset({TRAIN, VAL, TEST})


class _FitTransformable(Protocol):
    def fit(self, X: Any) -> Any: ...
    def transform(self, X: Any) -> Any: ...


class GuardedFitter:
    """Wraps an estimator/transformer exposing ``fit``/``transform`` and
    blocks any ``fit`` call made against data tagged as the test partition
    (RP-06, LEAK-R02, LEAK-R05).

    ``transform`` is always allowed on any partition: only *fitting*
    (parameter estimation) is restricted to train/validation, per ADR-002.
    """

    def __init__(self, estimator: _FitTransformable):
        self._estimator = estimator

    def fit(self, X: Any, partition: str) -> "GuardedFitter":
        _require_known_partition(partition)
        if partition == TEST:
            raise TestSetLeakageError(
                "fit() was called with data tagged as the 'test' partition; "
                "transformations and models may only be fitted on 'train' "
                "(or 'val' for hyperparameter search), never on 'test' "
                "(ADR-002, INV-05, LEAK-R02/LEAK-R05)."
            )
        self._estimator.fit(X)
        return self

    def transform(self, X: Any, partition: str) -> Any:
        _require_known_partition(partition)
        return self._estimator.transform(X)


def assert_test_not_used_for_selection(partitions_used_for_selection: set[str]) -> None:
    """Validate that hyperparameter/model selection referenced only
    'train' and/or 'val'.

    Raises
    ------
    TestSetLeakageError
        If 'test' is present in ``partitions_used_for_selection``.
    """
    used = {p.lower() for p in partitions_used_for_selection}
    _require_known_partition(*used)
    if TEST in used:
        raise TestSetLeakageError(
            "the 'test' partition was referenced during hyperparameter/model "
            "selection; selection must use only 'train' and/or 'val' "
            "(RP-08, LEAK-R03)."
        )


class ExperimentState:
    """Tracks whether a model configuration has been frozen for one
    experiment, and gates access to the test partition accordingly
    (ADR-002 steps 4-6; LEAK-R06).

    Usage contract for the future training pipeline:
        state = ExperimentState()
        ... select hyperparameters using train/val only ...
        state.freeze()
        state.access_test()   # exactly once, after freeze
    """

    def __init__(self) -> None:
        self._frozen = False
        self._test_accessed = False

    @property
    def frozen(self) -> bool:
        return self._frozen

    def freeze(self) -> None:
        self._frozen = True

    def access_test(self) -> None:
        if not self._frozen:
            raise TestSetLeakageError(
                "attempted to access the 'test' partition before the model "
                "configuration was frozen (ADR-002: hyperparameter selection "
                "must be complete before the test set may be consulted)."
            )
        if self._test_accessed:
            raise TestSetLeakageError(
                "the 'test' partition has already been consulted once for "
                "this experiment; re-evaluating after inspecting test "
                "results requires opening a new experiment id (LEAK-R06)."
            )
        self._test_accessed = True


def _require_known_partition(*partitions: str) -> None:
    for p in partitions:
        if p not in _KNOWN_PARTITIONS:
            raise ValueError(f"unknown partition tag {p!r}; expected one of {sorted(_KNOWN_PARTITIONS)}")
