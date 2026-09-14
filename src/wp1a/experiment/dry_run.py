"""Dry-run do pipeline de experimento (NÃO cientificamente válido).

Usa uma fração controlada das *execuções* (``run_id``) dentro de cada
partição já definida pelo manifesto A3 — nunca remistura runs entre
treino/val/teste (LEAK-R01 / LEAK-R04).

Todo artefato produzido DEVE carregar o marcador ``DRY-RUN`` e
``scientific_validity: false``.
"""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.base import clone

from wp1a.experiment.runner import ExperimentResult, ExperimentRunner
from wp1a.experiment.types import ExperimentConfig, ExperimentDataset, SplitRef
from wp1a.models.adapters import build_adapter
from wp1a.models.protocol import MODEL_IDS, MODEL_ID_TO_MOD

DRY_RUN_MARKER = "DRY-RUN"
DRY_RUN_DISCLAIMER = (
    "DRY-RUN only: controlled fraction of runs; results are NOT scientifically "
    "valid and MUST NOT feed A4/A7/A8 tables, figures, or conclusions."
)

# Hiperparâmetros deliberadamente leves — só para validar o caminho select→freeze→test.
DRY_RUN_HYPERPARAMETERS: dict[str, dict[str, Any]] = {
    "logistic_regression": {"C": 1.0, "max_iter": 200, "solver": "lbfgs"},
    "decision_tree": {"max_depth": 3, "min_samples_leaf": 5, "criterion": "gini"},
    "random_forest": {
        "n_estimators": 8,
        "max_depth": 4,
        "min_samples_leaf": 5,
        "n_jobs": 1,
    },
    "gradient_boosting": {
        "n_estimators": 8,
        "learning_rate": 0.1,
        "max_depth": 2,
    },
    "svm": {"C": 1.0, "kernel": "linear", "cache_size": 200},
    "xgboost": {
        "n_estimators": 8,
        "learning_rate": 0.1,
        "max_depth": 2,
        "reg_lambda": 1.0,
        "tree_method": "hist",
        "n_jobs": 1,
    },
}


@dataclass(frozen=True)
class DryRunSubsamplePlan:
    """Which run_ids were kept per partition after the controlled fraction."""

    run_fraction: float
    seed: int
    max_runs_per_partition: int | None
    train_runs: tuple[str, ...]
    validation_runs: tuple[str, ...]
    test_runs: tuple[str, ...]
    n_rows_train: int
    n_rows_validation: int
    n_rows_test: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _select_run_ids(
    run_ids: np.ndarray,
    *,
    fraction: float,
    seed: int,
    salt: str,
    max_runs: int | None,
) -> tuple[str, ...]:
    if not (0.0 < fraction <= 1.0):
        raise ValueError(f"run_fraction must be in (0, 1], got {fraction}")
    unique = sorted({str(r) for r in run_ids.tolist()})
    if not unique:
        raise ValueError("partition has no run_ids to subsample")
    n_keep = max(1, int(np.ceil(len(unique) * fraction)))
    if max_runs is not None:
        if max_runs < 1:
            raise ValueError("max_runs_per_partition must be >= 1 when set")
        n_keep = min(n_keep, max_runs)
    n_keep = min(n_keep, len(unique))
    digest = hashlib.sha256(f"{seed}:{salt}".encode()).hexdigest()
    rng = np.random.default_rng(int(digest[:8], 16))
    chosen = rng.choice(np.array(unique, dtype=object), size=n_keep, replace=False)
    return tuple(sorted(str(x) for x in chosen.tolist()))


def _mask_rows(run_ids: np.ndarray, keep: tuple[str, ...]) -> np.ndarray:
    keep_set = set(keep)
    return np.array([str(r) in keep_set for r in run_ids], dtype=bool)


def subsample_dataset_by_runs(
    dataset: ExperimentDataset,
    *,
    run_fraction: float = 0.2,
    seed: int = 42,
    max_runs_per_partition: int | None = 3,
) -> tuple[ExperimentDataset, DryRunSubsamplePlan]:
    """Keep a fraction of ``run_id``s *within* each partition (no cross-moves).

    Disjunction of run_ids across train/val/test is preserved because runs are
    only dropped, never reassigned (LEAK-R01).
    """
    train_keep = _select_run_ids(
        dataset.run_id_train,
        fraction=run_fraction,
        seed=seed,
        salt="train",
        max_runs=max_runs_per_partition,
    )
    val_keep = _select_run_ids(
        dataset.run_id_val,
        fraction=run_fraction,
        seed=seed,
        salt="validation",
        max_runs=max_runs_per_partition,
    )
    test_keep = _select_run_ids(
        dataset.run_id_test,
        fraction=run_fraction,
        seed=seed,
        salt="test",
        max_runs=max_runs_per_partition,
    )

    # Hard guard: never invent overlap.
    if set(train_keep) & set(val_keep) or set(train_keep) & set(test_keep) or set(val_keep) & set(test_keep):
        raise RuntimeError("dry-run subsample produced overlapping run_ids across partitions")

    mt = _mask_rows(dataset.run_id_train, train_keep)
    mv = _mask_rows(dataset.run_id_val, val_keep)
    ms = _mask_rows(dataset.run_id_test, test_keep)

    sub = ExperimentDataset(
        X_train=dataset.X_train[mt],
        y_train=dataset.y_train[mt],
        X_val=dataset.X_val[mv],
        y_val=dataset.y_val[mv],
        X_test=dataset.X_test[ms],
        y_test=dataset.y_test[ms],
        run_id_train=dataset.run_id_train[mt],
        run_id_val=dataset.run_id_val[mv],
        run_id_test=dataset.run_id_test[ms],
        dataset_version=f"{dataset.dataset_version}+{DRY_RUN_MARKER}",
        preprocessor_version=dataset.preprocessor_version,
    )
    plan = DryRunSubsamplePlan(
        run_fraction=run_fraction,
        seed=seed,
        max_runs_per_partition=max_runs_per_partition,
        train_runs=train_keep,
        validation_runs=val_keep,
        test_runs=test_keep,
        n_rows_train=int(mt.sum()),
        n_rows_validation=int(mv.sum()),
        n_rows_test=int(ms.sum()),
    )
    return sub, plan


def _software_versions() -> dict[str, str]:
    versions = {
        "python": platform.python_version(),
        "scikit-learn": sklearn.__version__,
        "numpy": np.__version__,
    }
    try:
        import xgboost

        versions["xgboost"] = xgboost.__version__
    except ImportError:  # pragma: no cover
        versions["xgboost"] = "missing"
    return versions


def _accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.asarray(y_pred) == np.asarray(y_true)))


def run_dry_pipeline(
    *,
    dataset: ExperimentDataset,
    split: SplitRef,
    run_fraction: float = 0.2,
    seed: int = 42,
    max_runs_per_partition: int | None = 3,
    experiment_prefix: str = "DRY-RUN",
    model_ids: tuple[str, ...] = MODEL_IDS,
) -> tuple[list[ExperimentResult], DryRunSubsamplePlan, dict[str, Any], ExperimentDataset]:
    """Execute all adapters on a run-fraction of the shared preprocessed split.

    Returns ``(results, plan, summary, subsampled_dataset)``.
    """
    if experiment_prefix != DRY_RUN_MARKER and DRY_RUN_MARKER not in experiment_prefix:
        raise ValueError(
            f"dry-run experiment_prefix must include {DRY_RUN_MARKER!r}; "
            "refusing to emit unmarked results"
        )

    sub, plan = subsample_dataset_by_runs(
        dataset,
        run_fraction=run_fraction,
        seed=seed,
        max_runs_per_partition=max_runs_per_partition,
    )

    # SplitRef for the dry-run keeps the *same* manifesto path (INV-03) but
    # records which runs were actually used in this non-scientific smoke.
    dry_split = SplitRef(
        manifest_version=f"{split.manifest_version}+{DRY_RUN_MARKER}",
        path=split.path,
        train_runs=plan.train_runs,
        validation_runs=plan.validation_runs,
        test_runs=plan.test_runs,
        seed=seed,
    )

    results: list[ExperimentResult] = []
    for model_id in model_ids:
        if model_id not in DRY_RUN_HYPERPARAMETERS:
            raise ValueError(f"no dry-run hyperparameters for {model_id}")
        adapter = build_adapter(model_id, seed=seed)
        # Fresh estimator copy so successive models do not share state.
        adapter.estimator = clone(adapter.estimator)
        cfg = ExperimentConfig(
            experiment_id=f"{experiment_prefix}__{model_id}",
            model_id=model_id,
            seed=seed,
            dataset_version=sub.dataset_version,
            split_manifest_path=dry_split.path,
            preprocessor_version=sub.preprocessor_version,
            hyperparameters=dict(DRY_RUN_HYPERPARAMETERS[model_id]),
            software_versions=_software_versions(),
        )
        runner = ExperimentRunner(
            model=adapter, dataset=sub, split=dry_split, config=cfg
        )
        results.append(runner.run())

    summary = {
        "status": DRY_RUN_MARKER,
        "scientific_validity": False,
        "disclaimer": DRY_RUN_DISCLAIMER,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "subsample": plan.as_dict(),
        "models": [],
    }
    for res in results:
        assert res.y_test_pred is not None
        y_test = sub.y_test
        summary["models"].append(
            {
                "status": DRY_RUN_MARKER,
                "scientific_validity": False,
                "experiment_id": res.experiment_id,
                "model_id": res.model_id,
                "mod_code": MODEL_ID_TO_MOD[res.model_id],
                "frozen_hyperparameters": res.frozen_hyperparameters,
                "train_time_s": res.train_time_s,
                "inference_time_s": res.inference_time_s,
                "n_test_predictions": int(len(res.y_test_pred)),
                "test_accuracy_dry_run_only": _accuracy(y_test, res.y_test_pred),
                "frozen_at": res.frozen_at,
                "test_accessed_at": res.test_accessed_at,
            }
        )
    return results, plan, summary, sub


def write_dry_run_artifacts(
    *,
    output_dir: Path,
    results: list[ExperimentResult],
    plan: DryRunSubsamplePlan,
    summary: dict[str, Any],
    dataset: ExperimentDataset,
) -> Path:
    """Persist dry-run outputs under ``results/dry_run/`` with explicit banners."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pred_dir = output_dir / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)

    readme = output_dir / "DRY_RUN_README.md"
    readme.write_text(
        "\n".join(
            [
                f"# {DRY_RUN_MARKER}",
                "",
                DRY_RUN_DISCLAIMER,
                "",
                "These files validate that adapters + ExperimentRunner execute",
                "end-to-end on a controlled fraction of runs. Do **not** cite,",
                "compare models, or promote numbers into SPEC-006/A4 results.",
                "",
                "Note: a random run-fraction may put disjoint classes in train vs",
                "test (TEP has ~2 runs/class), so dry-run accuracy may be ~0.",
                "That still validates the pipeline path — not model quality.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    manifest = {
        "status": DRY_RUN_MARKER,
        "scientific_validity": False,
        "disclaimer": DRY_RUN_DISCLAIMER,
        "subsample": plan.as_dict(),
        "dataset_version": dataset.dataset_version,
        "preprocessor_version": dataset.preprocessor_version,
    }
    (output_dir / "dry_run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "metrics_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    for res in results:
        assert res.y_test_pred is not None
        path = pred_dir / f"{DRY_RUN_MARKER}__{res.model_id}__test_pred.csv"
        # Include run_id for auditability of the dry-run subsample.
        lines = ["run_id,y_true,y_pred,status,scientific_validity"]
        for run_id, y_t, y_p in zip(
            dataset.run_id_test.tolist(),
            dataset.y_test.tolist(),
            res.y_test_pred.tolist(),
            strict=True,
        ):
            lines.append(
                f"{run_id},{y_t},{y_p},{DRY_RUN_MARKER},false"
            )
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return output_dir
