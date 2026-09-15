"""CLI — Entrega A6 (figuras/tabelas) lendo somente ``results/``.

Exemplo::

    PYTHONPATH=src python -m wp1a.visualization.cli --experiment-id exp-a4-v2
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from wp1a.visualization.pipeline import run_a6


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="WP1A A6 — scientific figures/tables from results/ only (never data/raw)."
    )
    p.add_argument("--experiment-id", default="exp-a4-v2")
    p.add_argument("--repo-root", type=Path, default=_repo_root())
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print("=" * 72)
    print(f" A6 / scientific-figures  experiment_id={args.experiment_id}")
    print(" Rule: read ONLY results/ — never data/raw")
    print("=" * 72)
    out = run_a6(repo_root=args.repo_root, experiment_id=args.experiment_id)
    print(json.dumps({k: out[k] for k in ("delivery", "n_models", "traceability_path", "disclaimer")}, indent=2))
    print(f"\nArtifacts: {len(out['artifacts'])} registered")
    for k, v in sorted(out["artifacts"].items()):
        print(f"  - {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
