"""Pipeline A5 — avaliação final multicritério (SPEC-007).

Recalcula MET-01..MET-09 a partir das predições de teste do A4, anexa
MET-10..MET-12 dos records de treino, verifica F1 macro/BA (CA-06) e
produz tabelas comparativas sem eleger um único “melhor” modelo (INV-06).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from wp1a.data.class_consistency import validate_train_covers_eval_classes
from wp1a.data.schema import CLASS_LABEL_COLUMN
from wp1a.evaluation.confused_classes import systematically_confused_classes
from wp1a.evaluation.metrics import compute_classification_metrics
from wp1a.evaluation.verify import verify_reported_aggregates
from wp1a.models.protocol import MODEL_IDS, MODEL_ID_TO_MOD

A5_DISCLAIMER = (
    "A5 multi-criteria evaluation (MET-01..MET-12). Do NOT rank models by "
    "accuracy alone (INV-06); computational cost is part of the comparison (INV-07). "
    "No single “best model” is declared in this stage."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_required_metrics(metrics: dict[str, Any], cost: dict[str, Any]) -> None:
    required_cls = [
        "MET-01_accuracy",
        "MET-02_balanced_accuracy",
        "MET-03_precision_macro",
        "MET-04_recall_macro",
        "MET-05_f1_macro",
        "MET-06_f1_weighted",
        "MET-07_mcc",
        "MET-08_confusion_matrix",
        "MET-09_per_class",
    ]
    missing = [k for k in required_cls if k not in metrics]
    if missing:
        raise ValueError(f"missing classification metrics: {missing}")
    for k in ("MET-10_train_time_s", "MET-11_inference_time_s", "MET-12_model_size_bytes"):
        if k not in cost or cost[k] is None:
            raise ValueError(f"missing cost metric {k}")


def evaluate_model_from_artifacts(
    *,
    model_id: str,
    predictions_path: Path,
    record_path: Path,
    train_labels: pd.Series | None = None,
) -> dict[str, Any]:
    """Recompute metrics from test predictions; attach cost from A4 record."""
    pred = pd.read_csv(predictions_path)
    required_cols = {"y_true", "y_pred"}
    if not required_cols.issubset(pred.columns):
        raise ValueError(f"{predictions_path} missing columns {required_cols}")

    if train_labels is not None:
        eval_df = pd.DataFrame({CLASS_LABEL_COLUMN: pred["y_true"]})
        train_df = pd.DataFrame({CLASS_LABEL_COLUMN: train_labels})
        validate_train_covers_eval_classes(train_df, eval_df, partition_name="test")

    metrics = compute_classification_metrics(
        pred["y_true"].to_numpy(),
        pred["y_pred"].to_numpy(),
    )
    record = _load_json(record_path)
    cost = {
        "MET-10_train_time_s": record.get("time", {}).get("MET-10_train_time_s")
        or record.get("time", {}).get("train_s"),
        "MET-11_inference_time_s": record.get("time", {}).get("MET-11_inference_time_s")
        or record.get("time", {}).get("inference_s"),
        "MET-12_model_size_bytes": record.get("model_size", {}).get(
            "MET-12_model_size_bytes"
        )
        or record.get("model_size", {}).get("bytes"),
        "selection_time_s": record.get("time", {}).get("selection_s"),
    }
    _assert_required_metrics(metrics, cost)
    checks = verify_reported_aggregates(metrics)
    if not checks["all_ok"]:
        raise AssertionError(
            f"CA-06 failed for {model_id}: F1/BA recomputation mismatch: {checks}"
        )

    return {
        "model_id": model_id,
        "mod_code": MODEL_ID_TO_MOD[model_id],
        "experiment_id": record.get("experiment_id"),
        "parent_experiment_id": record.get("parent_experiment_id"),
        "seed": record.get("seed"),
        "git_sha": record.get("git_sha"),
        "parameters": record.get("parameters"),
        "metrics": metrics,
        "cost": cost,
        "formula_checks": checks,
        "artifacts": {
            "predictions_path": str(predictions_path),
            "record_path": str(record_path),
        },
        "n_test_rows": int(len(pred)),
    }


def run_evaluation_a5(
    *,
    experiment_id: str,
    repo_root: Path,
    model_ids: tuple[str, ...] = MODEL_IDS,
    train_labels_path: Path | None = None,
) -> dict[str, Any]:
    """Build Entrega A5 for a completed A4 experiment_id."""
    root = Path(repo_root)
    pred_dir = root / "results" / "predictions"
    metrics_dir = root / "results" / "metrics"
    tables_dir = root / "results" / "tables"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    train_labels = None
    if train_labels_path is not None and Path(train_labels_path).is_file():
        train_df = pd.read_csv(train_labels_path, compression="gzip")
        train_labels = train_df[CLASS_LABEL_COLUMN]

    evaluated: list[dict[str, Any]] = []
    for model_id in model_ids:
        pred_path = pred_dir / f"{experiment_id}__{model_id}__test_pred.csv"
        rec_path = metrics_dir / f"{experiment_id}__{model_id}__record.json"
        if not pred_path.is_file():
            raise FileNotFoundError(f"missing predictions: {pred_path}")
        if not rec_path.is_file():
            raise FileNotFoundError(f"missing A4 record: {rec_path}")
        evaluated.append(
            evaluate_model_from_artifacts(
                model_id=model_id,
                predictions_path=pred_path,
                record_path=rec_path,
                train_labels=train_labels,
            )
        )

    if len(evaluated) != len(MODEL_IDS):
        raise ValueError(
            f"A5 requires all {len(MODEL_IDS)} models; got {len(evaluated)}"
        )

    confusion = systematically_confused_classes(evaluated)

    # --- write tables ---
    global_rows = []
    per_class_rows = []
    cost_rows = []
    for item in evaluated:
        m = item["metrics"]
        c = item["cost"]
        global_rows.append(
            {
                "experiment_id": experiment_id,
                "model_id": item["model_id"],
                "mod_code": item["mod_code"],
                "seed": item["seed"],
                "git_sha": item["git_sha"],
                "MET-01_accuracy": m["MET-01_accuracy"],
                "MET-02_balanced_accuracy": m["MET-02_balanced_accuracy"],
                "MET-03_precision_macro": m["MET-03_precision_macro"],
                "MET-04_recall_macro": m["MET-04_recall_macro"],
                "MET-05_f1_macro": m["MET-05_f1_macro"],
                "MET-06_f1_weighted": m["MET-06_f1_weighted"],
                "MET-07_mcc": m["MET-07_mcc"],
                "MET-10_train_time_s": c["MET-10_train_time_s"],
                "MET-11_inference_time_s": c["MET-11_inference_time_s"],
                "MET-12_model_size_bytes": c["MET-12_model_size_bytes"],
                "formula_checks_ok": item["formula_checks"]["all_ok"],
            }
        )
        cost_rows.append(
            {
                "experiment_id": experiment_id,
                "model_id": item["model_id"],
                "mod_code": item["mod_code"],
                "MET-10_train_time_s": c["MET-10_train_time_s"],
                "MET-11_inference_time_s": c["MET-11_inference_time_s"],
                "MET-12_model_size_bytes": c["MET-12_model_size_bytes"],
                "selection_time_s": c.get("selection_time_s"),
            }
        )
        for row in m["MET-09_per_class"]:
            per_class_rows.append(
                {
                    "experiment_id": experiment_id,
                    "model_id": item["model_id"],
                    "mod_code": item["mod_code"],
                    **row,
                }
            )
        cm_path = tables_dir / f"A5_{experiment_id}__{item['model_id']}__confusion_matrix.csv"
        pd.DataFrame(
            m["MET-08_confusion_matrix"],
            index=[f"true_{c}" for c in m["labels"]],
            columns=[f"pred_{c}" for c in m["labels"]],
        ).to_csv(cm_path)

    global_csv = tables_dir / f"A5_{experiment_id}__global_metrics.csv"
    per_class_csv = tables_dir / f"A5_{experiment_id}__per_class_metrics.csv"
    cost_csv = tables_dir / f"A5_{experiment_id}__cost_metrics.csv"
    confused_csv = tables_dir / f"A5_{experiment_id}__confused_classes.csv"
    pd.DataFrame(global_rows).to_csv(global_csv, index=False)
    pd.DataFrame(per_class_rows).to_csv(per_class_csv, index=False)
    pd.DataFrame(cost_rows).to_csv(cost_csv, index=False)
    pd.DataFrame(confusion["systematic_low_f1_faults"]).to_csv(confused_csv, index=False)

    payload = {
        "delivery": "A5",
        "spec": "SPEC-007",
        "experiment_id": experiment_id,
        "status": "A5",
        "scientific_validity": True,
        "disclaimer": A5_DISCLAIMER,
        "created_at": _utc_now(),
        "n_models": len(evaluated),
        "models": evaluated,
        "confused_classes": confusion,
        "artifacts": {
            "global_metrics_csv": str(global_csv),
            "per_class_metrics_csv": str(per_class_csv),
            "cost_metrics_csv": str(cost_csv),
            "confused_classes_csv": str(confused_csv),
        },
        "acceptance": {
            "CA-05_all_metrics_present": True,
            "CA-06_f1_ba_recomputed": all(e["formula_checks"]["all_ok"] for e in evaluated),
            "INV-06_no_single_metric_winner": True,
        },
    }
    out_json = metrics_dir / f"A5_{experiment_id}__evaluation.json"
    # Drop bulky nested checks duplication for readability? Keep full for audit.
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["artifacts"]["evaluation_json"] = str(out_json)

    # Compact QP3 note
    qp3_path = tables_dir / f"A5_{experiment_id}__qp3_confused_faults.json"
    qp3_path.write_text(
        json.dumps(confusion, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    payload["artifacts"]["qp3_json"] = str(qp3_path)
    return payload
