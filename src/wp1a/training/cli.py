"""CLI — treino dos seis modelos (Entrega A4 / SPEC-006).

Exemplo::

    PYTHONPATH=src python -m wp1a.training.cli \\
        --experiment-config configs/experiments/exp-a4-v1.yaml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from wp1a.experiment.types import SplitRef, load_experiment_dataset
from wp1a.preprocessing.pipeline import PREPROCESSOR_VERSION
from wp1a.splitting.manifest import load_split_manifest
from wp1a.training.pipeline import (
    DEFAULT_DATASET_VERSION,
    load_experiment_yaml,
    load_seed,
    run_training_benchmark,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    root = _repo_root()
    p = argparse.ArgumentParser(
        description="WP1A SPEC-006 — train MOD-1..MOD-6 (A4) with full provenance logging."
    )
    p.add_argument(
        "--experiment-config",
        type=Path,
        default=root / "configs" / "experiments" / "exp-a4-v1.yaml",
        help="Versioned experiment config (ADR-005)",
    )
    p.add_argument(
        "--processed-dir",
        type=Path,
        default=root / "data" / "processed",
    )
    p.add_argument(
        "--seeds",
        type=Path,
        default=root / "configs" / "seeds.yaml",
    )
    p.add_argument(
        "--output-root",
        type=Path,
        default=root,
        help="Repo root (writes models/ and results/)",
    )
    p.add_argument(
        "--dataset-version",
        default=DEFAULT_DATASET_VERSION,
    )
    p.add_argument(
        "--preprocessor-version",
        default=PREPROCESSOR_VERSION,
    )
    p.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Optional subset of model_ids (default: all from experiment config)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _repo_root()
    cfg = load_experiment_yaml(args.experiment_config)
    cfg["config_source"] = str(args.experiment_config)
    if args.models:
        cfg["model_ids"] = list(args.models)
    seed = load_seed(args.seeds)

    dataset = load_experiment_dataset(
        args.processed_dir,
        dataset_version=args.dataset_version,
        preprocessor_version=args.preprocessor_version,
    )
    manifest = load_split_manifest(args.processed_dir)
    split_path = cfg.get("split", {}).get(
        "manifest_path", str(args.processed_dir / "split_manifest_v1.json")
    )
    split = SplitRef.from_manifest(manifest, path=split_path)

    print("=" * 72)
    print(f" A4 / SPEC-006  experiment_id={cfg['experiment_id']}  seed={seed}")
    print(" Protocol: select(train/val) → freeze → fit_final → predict_test (once)")
    print(" Logging: seed | git SHA | environment | parameters | time | metrics | size")
    print("=" * 72)

    summary = run_training_benchmark(
        dataset=dataset,
        split=split,
        experiment_cfg=cfg,
        seed=seed,
        output_root=args.output_root,
        repo_root=root,
    )
    print("\nA4 complete.")
    print(json.dumps({k: v for k, v in summary.items() if k != "records"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
