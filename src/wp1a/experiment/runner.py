"""ExperimentRunner — caminho único de execução para todos os classificadores.

Referência: SPEC-006, ADR-002, ADR-005, INV-03/INV-05, MET-R03.

Uso conceitual::

    runner = ExperimentRunner(model=..., dataset=..., split=..., config=...)
    result = runner.run()

Nenhum classificador do benchmark pode ser treinado fora deste runner.
"""

from __future__ import annotations

import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np

from wp1a.errors import TestSetLeakageError
from wp1a.experiment.types import ExperimentConfig, ExperimentDataset, SplitRef
from wp1a.models.protocol import ClassifierProtocol
from wp1a.tracking.isolation_guard import (
    TEST,
    TRAIN,
    VAL,
    ExperimentState,
    assert_test_not_used_for_selection,
)
from wp1a.tracking.metadata_guard import validate_experiment_metadata

# Callable that scores a candidate model on (X, y) → float (higher is better).
ScoreFn = Callable[[ClassifierProtocol, np.ndarray, np.ndarray], float]
# Callable that, given train/val arrays + seed, returns best hyperparameter dict.
# Must NOT receive or use the test partition.
SelectFn = Callable[..., dict[str, Any]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _manifest_paths_equivalent(a: str, b: str) -> bool:
    pa, pb = Path(a), Path(b)
    return pa.name == pb.name or pa.as_posix() == pb.as_posix()


@dataclass
class ExperimentResult:
    experiment_id: str
    model_id: str
    frozen_hyperparameters: dict[str, Any]
    y_test_pred: np.ndarray | None
    train_time_s: float | None
    inference_time_s: float | None
    selection_scores: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    frozen_at: str | None = None
    test_accessed_at: str | None = None


class ExperimentRunner:
    """Single execution framework shared by all WP1A classifiers.

    Lifecycle (ADR-002):
      1. ``select_hyperparameters`` — train/val only
      2. ``freeze`` — lock configuration
      3. ``fit_final`` — fit on train (never test)
      4. ``predict_test`` — exactly once after freeze
    """

    def __init__(
        self,
        *,
        model: ClassifierProtocol,
        dataset: ExperimentDataset,
        split: SplitRef,
        config: ExperimentConfig,
    ) -> None:
        if not isinstance(model, ClassifierProtocol):
            # runtime_checkable Protocol — structural check
            missing = [
                name
                for name in ("fit", "predict", "get_params", "set_params")
                if not callable(getattr(model, name, None))
            ]
            if missing:
                raise TypeError(
                    f"model missing ClassifierProtocol methods: {missing}; "
                    "all classifiers must be runner-compatible"
                )
        self._validate_shared_protocol(dataset, split, config)

        self.model = model
        self.dataset = dataset
        self.split = split
        self.config = config
        self.state = ExperimentState()
        self._selection_partitions_used: set[str] = set()
        self._selection_scores: list[dict[str, Any]] = []
        self._frozen_hyperparameters: dict[str, Any] | None = None
        self._frozen_at: str | None = None
        self._fitted = False
        self._train_time_s: float | None = None
        self._inference_time_s: float | None = None
        self._y_test_pred: np.ndarray | None = None
        self._test_accessed_at: str | None = None

    @staticmethod
    def _validate_shared_protocol(
        dataset: ExperimentDataset,
        split: SplitRef,
        config: ExperimentConfig,
    ) -> None:
        """INV-03: config/split/preprocess references must be consistent."""
        if not _manifest_paths_equivalent(config.split_manifest_path, split.path):
            raise ValueError(
                "config.split_manifest_path does not match split.path — "
                "all models must share the same A3 manifesto (INV-03)"
            )
        if config.dataset_version != dataset.dataset_version:
            raise ValueError(
                "config.dataset_version != dataset.dataset_version (INV-03)"
            )
        if config.preprocessor_version != dataset.preprocessor_version:
            raise ValueError(
                "config.preprocessor_version != dataset.preprocessor_version (INV-03)"
            )

    def select_hyperparameters(
        self,
        select_fn: SelectFn | None = None,
        *,
        score_fn: ScoreFn | None = None,
        candidates: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Hyperparameter selection using ONLY train and/or validation.

        If ``select_fn`` is provided, it is called with keyword-only train/val
        arrays (never test). If ``candidates`` is provided, a simple grid
        search on validation accuracy is performed.
        """
        if self.state.frozen:
            raise TestSetLeakageError(
                "cannot select hyperparameters after freeze; open a new "
                "experiment_id (LEAK-R06)"
            )

        self._selection_partitions_used = {TRAIN, VAL}
        assert_test_not_used_for_selection(self._selection_partitions_used)

        X_train, y_train = self.dataset.partition_xy(TRAIN)
        X_val, y_val = self.dataset.partition_xy(VAL)

        if select_fn is not None:
            best = select_fn(
                model=self.model,
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                seed=self.config.seed,
            )
            if not isinstance(best, dict):
                raise TypeError("select_fn must return a hyperparameters dict")
            self._frozen_hyperparameters = dict(best)
            return self._frozen_hyperparameters

        # Default: evaluate candidate list on validation (or use config as-is).
        grid = candidates if candidates is not None else [dict(self.config.hyperparameters)]
        scorer = score_fn or _default_accuracy
        best_params = dict(grid[0])
        best_score = float("-inf")
        self._selection_scores = []

        for params in grid:
            assert_test_not_used_for_selection(self._selection_partitions_used)
            candidate = deepcopy(self.model)
            candidate.set_params(**params)
            candidate.fit(X_train, y_train)
            score = float(scorer(candidate, X_val, y_val))
            self._selection_scores.append({"params": dict(params), "val_score": score})
            if score > best_score:
                best_score = score
                best_params = dict(params)

        self._frozen_hyperparameters = best_params
        return best_params

    def freeze(self) -> ExperimentConfig:
        """Freeze hyperparameters and experiment metadata before any test access."""
        if self._frozen_hyperparameters is None:
            # No search performed — freeze declared config hyperparameters.
            self._frozen_hyperparameters = dict(self.config.hyperparameters)

        assert_test_not_used_for_selection(self._selection_partitions_used or {TRAIN, VAL})
        self._frozen_at = _utc_now()
        self.state.freeze()
        self.config = ExperimentConfig(
            experiment_id=self.config.experiment_id,
            model_id=self.config.model_id,
            seed=self.config.seed,
            dataset_version=self.config.dataset_version,
            split_manifest_path=self.config.split_manifest_path,
            preprocessor_version=self.config.preprocessor_version,
            hyperparameters=dict(self._frozen_hyperparameters),
            software_versions=dict(self.config.software_versions),
            timestamp=self._frozen_at,
            frozen=True,
        )
        validate_experiment_metadata(self.config.as_metadata())
        return self.config

    def fit_final(self) -> ClassifierProtocol:
        """Fit the frozen configuration on TRAIN only (never test)."""
        if not self.state.frozen:
            raise TestSetLeakageError(
                "fit_final() requires freeze() first (ADR-002 order)"
            )
        assert self._frozen_hyperparameters is not None
        self.model.set_params(**self._frozen_hyperparameters)
        X_train, y_train = self.dataset.partition_xy(TRAIN)
        t0 = time.perf_counter()
        self.model.fit(X_train, y_train)
        self._train_time_s = time.perf_counter() - t0
        self._fitted = True
        return self.model

    def predict_test(self) -> np.ndarray:
        """Consult the test partition exactly once after freeze."""
        if not self._fitted:
            raise RuntimeError("predict_test() requires fit_final() first")
        self.state.access_test()
        self._test_accessed_at = _utc_now()
        X_test, _ = self.dataset.partition_xy(TEST)
        t0 = time.perf_counter()
        pred = np.asarray(self.model.predict(X_test))
        self._inference_time_s = time.perf_counter() - t0
        self._y_test_pred = pred
        return pred

    def run(
        self,
        *,
        select_fn: SelectFn | None = None,
        score_fn: ScoreFn | None = None,
        candidates: list[dict[str, Any]] | None = None,
    ) -> ExperimentResult:
        """Full lifecycle for one classifier through this shared runner."""
        self.select_hyperparameters(select_fn, score_fn=score_fn, candidates=candidates)
        self.freeze()
        self.fit_final()
        self.predict_test()
        return ExperimentResult(
            experiment_id=self.config.experiment_id,
            model_id=self.config.model_id,
            frozen_hyperparameters=dict(self._frozen_hyperparameters or {}),
            y_test_pred=self._y_test_pred,
            train_time_s=self._train_time_s,
            inference_time_s=self._inference_time_s,
            selection_scores=list(self._selection_scores),
            metadata=self.config.as_metadata(),
            frozen_at=self._frozen_at,
            test_accessed_at=self._test_accessed_at,
        )


def run_all_models(
    *,
    models: dict[str, ClassifierProtocol],
    dataset: ExperimentDataset,
    split: SplitRef,
    base_config: ExperimentConfig,
    candidates_by_model: dict[str, list[dict[str, Any]]] | None = None,
) -> list[ExperimentResult]:
    """Execute every classifier through the *same* ExperimentRunner protocol.

    ``models`` keys must be the six MODEL_IDS (or a subset during scaffolding).
    Shared ``dataset`` and ``split`` enforce INV-03.
    """
    results: list[ExperimentResult] = []
    for model_id, model in models.items():
        cfg = ExperimentConfig(
            experiment_id=f"{base_config.experiment_id}__{model_id}",
            model_id=model_id,
            seed=base_config.seed,
            dataset_version=base_config.dataset_version,
            split_manifest_path=base_config.split_manifest_path,
            preprocessor_version=base_config.preprocessor_version,
            hyperparameters=dict(base_config.hyperparameters),
            software_versions=dict(base_config.software_versions),
        )
        runner = ExperimentRunner(model=model, dataset=dataset, split=split, config=cfg)
        cand = None if candidates_by_model is None else candidates_by_model.get(model_id)
        results.append(runner.run(candidates=cand))
    return results


def _default_accuracy(model: ClassifierProtocol, X: np.ndarray, y: np.ndarray) -> float:
    pred = np.asarray(model.predict(X))
    return float(np.mean(pred == np.asarray(y)))
