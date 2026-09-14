"""Pipeline de treinamento A4 — seis modelos via ExperimentRunner (SPEC-006).

Registra por modelo: seed, git SHA, environment, parameters, time,
metrics (teste uma vez), model size (EXP-R01, EXP-R05, MET-10..12).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import yaml

from wp1a.data.class_consistency import validate_train_covers_eval_classes
from wp1a.data.schema import CLASS_LABEL_COLUMN, RUN_ID_COLUMN
from wp1a.evaluation.metrics import compute_classification_metrics
from wp1a.experiment.provenance import (
    environment_snapshot,
    git_provenance,
    software_versions_for_config,
)
from wp1a.experiment.runner import ExperimentResult, ExperimentRunner
from wp1a.experiment.types import ExperimentConfig, ExperimentDataset, SplitRef
from wp1a.models.adapters import build_adapter
from wp1a.models.defaults import DEFAULT_HYPERPARAMETERS
from wp1a.models.protocol import MODEL_IDS, MODEL_ID_TO_MOD
from wp1a.preprocessing.pipeline import PREPROCESSOR_VERSION
from wp1a.training.search import expand_search_space

DEFAULT_DATASET_VERSION = "tep-canonical-v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_experiment_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"experiment config must be a mapping: {path}")
    return payload


def load_seed(seeds_path: Path) -> int:
    payload = yaml.safe_load(Path(seeds_path).read_text(encoding="utf-8"))
    seed = payload.get("per_stage", {}).get("model_init", payload.get("global_seed"))
    if seed is None:
        raise ValueError(f"model seed not found in {seeds_path}")
    return int(seed)


@dataclass
class TrainedModelRecord:
    experiment_id: str
    model_id: str
    record: dict[str, Any]
    result: ExperimentResult
    model_path: Path


def _model_size_bytes(path: Path) -> int:
    return int(path.stat().st_size)


def _assert_class_coverage(dataset: ExperimentDataset) -> None:
    train_df = pd.DataFrame({CLASS_LABEL_COLUMN: dataset.y_train})
    for name, y in (("validation", dataset.y_val), ("test", dataset.y_test)):
        eval_df = pd.DataFrame({CLASS_LABEL_COLUMN: y})
        validate_train_covers_eval_classes(train_df, eval_df, partition_name=name)


def train_one_model(
    *,
    model_id: str,
    dataset: ExperimentDataset,
    split: SplitRef,
    experiment_id: str,
    seed: int,
    candidates: list[dict[str, Any]],
    models_dir: Path,
    predictions_dir: Path,
    git_info: dict[str, Any],
    environment: dict[str, Any],
) -> TrainedModelRecord:
    """Select (train/val) → freeze → fit → predict_test once; persist artifacts."""
    if model_id not in MODEL_IDS:
        raise ValueError(f"unknown model_id={model_id}")
    if not candidates:
        candidates = [dict(DEFAULT_HYPERPARAMETERS[model_id])]

    adapter = build_adapter(model_id, seed=seed)
    cfg = ExperimentConfig(
        experiment_id=f"{experiment_id}__{model_id}",
        model_id=model_id,
        seed=seed,
        dataset_version=dataset.dataset_version,
        split_manifest_path=split.path,
        preprocessor_version=dataset.preprocessor_version,
        hyperparameters=dict(candidates[0]),
        software_versions=software_versions_for_config(),
    )
    runner = ExperimentRunner(
        model=adapter, dataset=dataset, split=split, config=cfg
    )

    t_sel0 = time.perf_counter()
    best = runner.select_hyperparameters(candidates=candidates)
    selection_time_s = time.perf_counter() - t_sel0
    runner.freeze()
    fitted = runner.fit_final()
    y_pred = runner.predict_test()
    result = ExperimentResult(
        experiment_id=runner.config.experiment_id,
        model_id=model_id,
        frozen_hyperparameters=dict(best),
        y_test_pred=y_pred,
        train_time_s=runner._train_time_s,
        inference_time_s=runner._inference_time_s,
        selection_scores=list(runner._selection_scores),
        metadata=runner.config.as_metadata(),
        frozen_at=runner._frozen_at,
        test_accessed_at=runner._test_accessed_at,
    )

    models_dir.mkdir(parents=True, exist_ok=True)
    predictions_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / f"{experiment_id}__{model_id}.joblib"
    joblib.dump(fitted, model_path)
    size_bytes = _model_size_bytes(model_path)

    metrics = compute_classification_metrics(dataset.y_test, y_pred)

    pred_path = predictions_dir / f"{experiment_id}__{model_id}__test_pred.csv"
    pd.DataFrame(
        {
            RUN_ID_COLUMN: dataset.run_id_test,
            "y_true": dataset.y_test,
            "y_pred": y_pred,
            "model_id": model_id,
            "experiment_id": result.experiment_id,
        }
    ).to_csv(pred_path, index=False)

    record = {
        "experiment_id": result.experiment_id,
        "parent_experiment_id": experiment_id,
        "model_id": model_id,
        "mod_code": MODEL_ID_TO_MOD[model_id],
        "seed": seed,
        "git_sha": git_info.get("git_sha"),
        "git_sha_short": git_info.get("git_sha_short"),
        "git_dirty": git_info.get("git_dirty"),
        "git_branch": git_info.get("git_branch"),
        "environment": environment,
        "parameters": dict(best),
        "selection": {
            "n_candidates": len(candidates),
            "selection_time_s": selection_time_s,
            "selection_scores": result.selection_scores,
            "partitions_used": ["train", "validation"],
            "test_used_for_selection": False,
        },
        "time": {
            "selection_s": selection_time_s,
            "train_s": result.train_time_s,
            "inference_s": result.inference_time_s,
            "MET-10_train_time_s": result.train_time_s,
            "MET-11_inference_time_s": result.inference_time_s,
        },
        "metrics": {
            k: v
            for k, v in metrics.items()
            if k != "MET-08_confusion_matrix"
        },
        "confusion_matrix": metrics["MET-08_confusion_matrix"],
        "model_size": {
            "path": str(model_path),
            "bytes": size_bytes,
            "MET-12_model_size_bytes": size_bytes,
        },
        "artifacts": {
            "model_path": str(model_path),
            "predictions_path": str(pred_path),
        },
        "dataset_version": dataset.dataset_version,
        "preprocessor_version": dataset.preprocessor_version,
        "split_manifest_path": split.path,
        "frozen_at": result.frozen_at,
        "test_accessed_at": result.test_accessed_at,
        "timestamp": _utc_now(),
        "scientific_validity": True,
        "status": "A4",
    }
    return TrainedModelRecord(
        experiment_id=result.experiment_id,
        model_id=model_id,
        record=record,
        result=result,
        model_path=model_path,
    )


def run_training_benchmark(
    *,
    dataset: ExperimentDataset,
    split: SplitRef,
    experiment_cfg: dict[str, Any],
    seed: int,
    output_root: Path,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Train all six models under one shared protocol; write A4 artifacts."""
    _assert_class_coverage(dataset)

    experiment_id = str(experiment_cfg["experiment_id"])
    search_spaces: dict[str, dict[str, list[Any]]] = experiment_cfg.get(
        "search_spaces", {}
    )
    model_ids = tuple(experiment_cfg.get("model_ids", list(MODEL_IDS)))
    for mid in model_ids:
        if mid not in MODEL_IDS:
            raise ValueError(f"model_id {mid!r} not in mandatory set")

    git_info = git_provenance(repo_root)
    environment = environment_snapshot()

    models_dir = output_root / "models"
    predictions_dir = output_root / "results" / "predictions"
    metrics_dir = output_root / "results" / "metrics"
    tables_dir = output_root / "results" / "tables"
    meta_dir = output_root / "results" / "metadata"
    for d in (models_dir, predictions_dir, metrics_dir, tables_dir, meta_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Persist the exact config used for this run (ADR-005 / EXP-R04).
    run_cfg_path = meta_dir / f"{experiment_id}__config_snapshot.json"
    snapshot = {
        "experiment_id": experiment_id,
        "seed": seed,
        "git": git_info,
        "environment": environment,
        "dataset_version": dataset.dataset_version,
        "preprocessor_version": dataset.preprocessor_version,
        "split_manifest_path": split.path,
        "search_spaces": search_spaces,
        "model_ids": list(model_ids),
        "config_source": experiment_cfg.get("config_source"),
        "created_at": _utc_now(),
        "scientific_validity": True,
        "status": "A4",
    }
    run_cfg_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    records: list[dict[str, Any]] = []
    # Merge with any prior per-model records for this experiment_id (resume-safe).
    for model_id in MODEL_IDS:
        existing = metrics_dir / f"{experiment_id}__{model_id}__record.json"
        if model_id not in model_ids and existing.is_file():
            records.append(json.loads(existing.read_text(encoding="utf-8")))

    for model_id in model_ids:
        space = search_spaces.get(model_id) or {
            k: [v] for k, v in DEFAULT_HYPERPARAMETERS[model_id].items()
        }
        candidates = expand_search_space(space)
        print(
            f"[A4] {model_id}: selecting among {len(candidates)} candidates "
            f"(train/val only)...",
            flush=True,
        )
        trained = train_one_model(
            model_id=model_id,
            dataset=dataset,
            split=split,
            experiment_id=experiment_id,
            seed=seed,
            candidates=candidates,
            models_dir=models_dir,
            predictions_dir=predictions_dir,
            git_info=git_info,
            environment=environment,
        )
        rec_path = metrics_dir / f"{experiment_id}__{model_id}__record.json"
        rec_path.write_text(
            json.dumps(trained.record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        # Confusion matrix as separate table artifact (DOC-R03).
        cm_path = tables_dir / f"{experiment_id}__{model_id}__confusion_matrix.csv"
        pd.DataFrame(
            trained.record["confusion_matrix"],
            index=[f"true_{c}" for c in range(len(trained.record["confusion_matrix"]))],
            columns=[f"pred_{c}" for c in range(len(trained.record["confusion_matrix"]))],
        ).to_csv(cm_path)
        per_class = pd.DataFrame(trained.record["metrics"]["MET-09_per_class"])
        per_class.to_csv(
            tables_dir / f"{experiment_id}__{model_id}__per_class_metrics.csv",
            index=False,
        )
        records = [r for r in records if r["model_id"] != model_id]
        records.append(trained.record)
        m = trained.record["metrics"]
        print(
            f"[A4] {model_id}: done | "
            f"F1_macro={m['MET-05_f1_macro']:.4f} "
            f"BA={m['MET-02_balanced_accuracy']:.4f} "
            f"MCC={m['MET-07_mcc']:.4f} | "
            f"train={trained.record['time']['train_s']:.2f}s "
            f"infer={trained.record['time']['inference_s']:.2f}s "
            f"size={trained.record['model_size']['bytes']}B",
            flush=True,
        )

    # Stable order MOD-1..MOD-6
    order = {mid: i for i, mid in enumerate(MODEL_IDS)}
    records.sort(key=lambda r: order.get(r["model_id"], 99))

    summary_rows = []
    for rec in records:
        summary_rows.append(
            {
                "experiment_id": rec["experiment_id"],
                "model_id": rec["model_id"],
                "mod_code": rec["mod_code"],
                "seed": rec["seed"],
                "git_sha": rec["git_sha"],
                "accuracy": rec["metrics"]["MET-01_accuracy"],
                "balanced_accuracy": rec["metrics"]["MET-02_balanced_accuracy"],
                "precision_macro": rec["metrics"]["MET-03_precision_macro"],
                "recall_macro": rec["metrics"]["MET-04_recall_macro"],
                "f1_macro": rec["metrics"]["MET-05_f1_macro"],
                "f1_weighted": rec["metrics"]["MET-06_f1_weighted"],
                "mcc": rec["metrics"]["MET-07_mcc"],
                "train_time_s": rec["time"]["train_s"],
                "inference_time_s": rec["time"]["inference_s"],
                "selection_time_s": rec["time"]["selection_s"],
                "model_size_bytes": rec["model_size"]["bytes"],
                "parameters_json": json.dumps(rec["parameters"], sort_keys=True),
            }
        )
    summary_df = pd.DataFrame(summary_rows)
    summary_csv = tables_dir / f"{experiment_id}__metrics_summary.csv"
    summary_json = metrics_dir / f"{experiment_id}__metrics_summary.json"
    hp_csv = tables_dir / f"{experiment_id}__hyperparameters.csv"
    summary_df.to_csv(summary_csv, index=False)
    summary_json.write_text(
        json.dumps(
            {
                "experiment_id": experiment_id,
                "seed": seed,
                "git": git_info,
                "environment": environment,
                "scientific_validity": True,
                "status": "A4",
                "disclaimer": (
                    "Multi-metric report (MET-01..MET-12). Do not rank models by "
                    "accuracy alone (INV-06)."
                ),
                "models": records,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "model_id": r["model_id"],
                "mod_code": r["mod_code"],
                "experiment_id": r["experiment_id"],
                **{f"param__{k}": v for k, v in r["parameters"].items()},
            }
            for r in records
        ]
    ).to_csv(hp_csv, index=False)

    return {
        "experiment_id": experiment_id,
        "n_models": len(records),
        "summary_csv": str(summary_csv),
        "summary_json": str(summary_json),
        "hyperparameters_csv": str(hp_csv),
        "config_snapshot": str(run_cfg_path),
        "records": records,
    }
