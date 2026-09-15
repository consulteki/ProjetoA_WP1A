"""CLI — SPEC-008 análise estatística (unidade = run_id).

Exemplo::

    PYTHONPATH=src python -m wp1a.statistics.cli --experiment-id exp-a4-v2
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from wp1a.models.protocol import MODEL_IDS
from wp1a.statistics.pipeline import run_statistics_a8


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="WP1A SPEC-008 — Friedman/Wilcoxon with run_id as experimental unit."
    )
    p.add_argument("--experiment-id", default="exp-a4-v2")
    p.add_argument("--repo-root", type=Path, default=_repo_root())
    p.add_argument("--alpha", type=float, default=0.05)
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
    print(f" SPEC-008 / statistics  experiment_id={args.experiment_id}")
    print(" Experimental unit = run_id (INV-09); no sample-level tests")
    print("=" * 72)
    result = run_statistics_a8(
        experiment_id=args.experiment_id,
        repo_root=args.repo_root,
        model_ids=model_ids,
        alpha=args.alpha,
    )
    fr = result["friedman"]
    print(
        f"\nFriedman on run_accuracy: "
        f"n_units={fr['n_units']}  chi2={fr['statistic']:.4f}  "
        f"p={fr['pvalue']:.6g}  reject_H0={fr['reject_h0']}"
    )
    print("\nHypothesis interpretation (run-level):")
    for h in result["hypothesis_interpretation"]:
        print(f"  {h['hypothesis']}: {h.get('verdict_run_level')} — {h.get('run_accuracy_wilcoxon') or h.get('note')}")
    print("\nLimitations:")
    for lim in result["limitations"]:
        print(f"  - {lim}")
    print(f"\n{result['disclaimer']}")
    print("Artifacts:")
    for k, v in result["artifacts"].items():
        print(f"  - {k}: {v}")
    # compact JSON pointer
    print("\nBundle:", result["artifacts"]["statistics_bundle"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
