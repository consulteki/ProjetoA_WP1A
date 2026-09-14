"""CLI — Entrega A5 / SPEC-007 (avaliação final multicritério).

Exemplo::

    PYTHONPATH=src python -m wp1a.evaluation.cli --experiment-id exp-a4-v2
"""

from __future__ import annotations

import argparse
from pathlib import Path

from wp1a.evaluation.pipeline import run_evaluation_a5
from wp1a.models.protocol import MODEL_IDS
from wp1a.preprocessing.pipeline import PREPROCESSOR_VERSION


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    root = _repo_root()
    p = argparse.ArgumentParser(
        description="WP1A SPEC-007 — Entrega A5 (métricas MET-01..MET-12, sem ranking único)."
    )
    p.add_argument(
        "--experiment-id",
        default="exp-a4-v2",
        help="Parent A4 experiment id (predictions + records)",
    )
    p.add_argument(
        "--repo-root",
        type=Path,
        default=root,
    )
    p.add_argument(
        "--train-labels",
        type=Path,
        default=root / "data" / "processed" / f"{PREPROCESSOR_VERSION}_train.csv.gz",
        help="Train partition for class-coverage check (SPEC-007 req. 10)",
    )
    p.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Optional subset (default: all six MODEL_IDS)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    model_ids = tuple(args.models) if args.models else MODEL_IDS
    print("=" * 72)
    print(f" A5 / SPEC-007  experiment_id={args.experiment_id}")
    print(" Recompute MET-01..09 from predictions; attach MET-10..12 from A4 records")
    print(" No single-metric “best model” (INV-06)")
    print("=" * 72)

    result = run_evaluation_a5(
        experiment_id=args.experiment_id,
        repo_root=args.repo_root,
        model_ids=model_ids,
        train_labels_path=args.train_labels,
    )
    print(f"\nCA-05 metrics present: {result['acceptance']['CA-05_all_metrics_present']}")
    print(f"CA-06 F1/BA recomputed: {result['acceptance']['CA-06_f1_ba_recomputed']}")
    print(f"Models evaluated: {result['n_models']}")
    print("\nGlobal metrics (excerpt):")
    for m in result["models"]:
        met = m["metrics"]
        cost = m["cost"]
        print(
            f"  {m['model_id']}: F1={met['MET-05_f1_macro']:.4f} "
            f"BA={met['MET-02_balanced_accuracy']:.4f} "
            f"MCC={met['MET-07_mcc']:.4f} "
            f"train={cost['MET-10_train_time_s']:.2f}s "
            f"size={cost['MET-12_model_size_bytes']}B"
        )
    print(f"\n{result['disclaimer']}")
    print("Artifacts:")
    for k, v in result["artifacts"].items():
        print(f"  - {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
