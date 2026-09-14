"""CLI: dry-run ponta a ponta do ExperimentRunner + adapters (NÃO científico).

Exemplo::

    PYTHONPATH=src python -m wp1a.experiment.dry_run_cli \\
        --run-fraction 0.2 --max-runs-per-partition 3

Saídas em ``results/dry_run/`` com marcador explícito DRY-RUN.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from wp1a.experiment.dry_run import (
    DRY_RUN_DISCLAIMER,
    DRY_RUN_MARKER,
    run_dry_pipeline,
    write_dry_run_artifacts,
)
from wp1a.experiment.types import SplitRef, load_experiment_dataset
from wp1a.preprocessing.pipeline import PREPROCESSOR_VERSION
from wp1a.splitting.manifest import load_split_manifest

DEFAULT_PROCESSED = Path("data/processed")
DEFAULT_MANIFEST = DEFAULT_PROCESSED / "split_manifest_v1.json"
DEFAULT_OUT = Path("results/dry_run")
DEFAULT_DATASET_VERSION = "tep-canonical-v1"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            f"{DRY_RUN_MARKER}: end-to-end smoke on a controlled fraction of runs. "
            "Results are NOT scientifically valid."
        )
    )
    p.add_argument(
        "--processed-dir",
        type=Path,
        default=DEFAULT_PROCESSED,
        help="Directory with SPEC-005 preprocessed partitions",
    )
    p.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="A3 split manifesto (shared protocol reference)",
    )
    p.add_argument(
        "--dataset-version",
        default=DEFAULT_DATASET_VERSION,
        help="Canonical dataset version id (before DRY-RUN suffix)",
    )
    p.add_argument(
        "--preprocessor-version",
        default=PREPROCESSOR_VERSION,
        help="Preprocessor version prefix for partition files",
    )
    p.add_argument(
        "--run-fraction",
        type=float,
        default=0.2,
        help="Fraction of run_ids kept inside each partition (default: 0.2)",
    )
    p.add_argument(
        "--max-runs-per-partition",
        type=int,
        default=3,
        help="Hard cap on runs kept per partition (default: 3; use 0 to disable)",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed for run subsample + model init (dry-run only)",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="Where to write DRY-RUN artifacts",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    max_runs = None if args.max_runs_per_partition <= 0 else args.max_runs_per_partition

    print("=" * 72)
    print(f" {DRY_RUN_MARKER}")
    print(f" {DRY_RUN_DISCLAIMER}")
    print("=" * 72)

    dataset = load_experiment_dataset(
        args.processed_dir,
        dataset_version=args.dataset_version,
        preprocessor_version=args.preprocessor_version,
    )
    if args.manifest.is_file():
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        manifest_path = str(args.manifest)
    else:
        manifest = load_split_manifest(args.processed_dir)
        manifest_path = str(args.processed_dir / "split_manifest_v1.json")
    split = SplitRef.from_manifest(manifest, path=manifest_path)

    results, plan, summary, sub = run_dry_pipeline(
        dataset=dataset,
        split=split,
        run_fraction=args.run_fraction,
        seed=args.seed,
        max_runs_per_partition=max_runs,
    )

    out = write_dry_run_artifacts(
        output_dir=args.output_dir,
        results=results,
        plan=plan,
        summary=summary,
        dataset=sub,
    )

    print(f"\n{DRY_RUN_MARKER} subsample plan:")
    print(json.dumps(plan.as_dict(), indent=2))
    print(f"\n{DRY_RUN_MARKER} model timings / dry accuracies:")
    for row in summary["models"]:
        print(
            f"  - {row['model_id']}: train={row['train_time_s']:.3f}s "
            f"infer={row['inference_time_s']:.3f}s "
            f"acc_DRY={row['test_accuracy_dry_run_only']:.4f}"
        )
    print(f"\nArtifacts written under: {out.resolve()}")
    print(f"scientific_validity=false  status={DRY_RUN_MARKER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
