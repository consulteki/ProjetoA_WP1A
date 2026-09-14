"""CLI da Etapa 3 — divisão por run (SPEC-004 / Entrega A3).

Gera apenas ``train_runs``, ``validation_runs`` e ``test_runs`` (mais o
manifesto JSON). Não treina modelos.

Após gerar o manifesto, executa ``tests/methodology/`` e interrompe
(exit ≠ 0) se qualquer teste de leakage/metodologia falhar.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from wp1a.splitting.manifest import (
    build_split_manifest,
    run_methodology_suite_or_abort,
    verify_manifest_leakage_or_raise,
    write_split_artifacts,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        description="WP1A SPEC-004 — manifesto de divisão por run (Entrega A3)."
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=root / "data" / "processed",
        help="Dataset canônico + destino do manifesto (default: data/processed).",
    )
    parser.add_argument(
        "--seeds-path",
        type=Path,
        default=root / "configs" / "seeds.yaml",
        help="Arquivo de sementes (default: configs/seeds.yaml).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Sobrescreve a semente de split (default: seeds.yaml#per_stage.split).",
    )
    parser.add_argument(
        "--skip-methodology-tests",
        action="store_true",
        help="Não executar tests/methodology/ (apenas para debug; não use em CI).",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=root / "results" / "metadata",
        help="Cópia enxuta do manifesto (default: results/metadata).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = build_split_manifest(
        processed_dir=args.processed_dir,
        seed=args.seed,
        seeds_path=args.seeds_path,
    )
    verify_manifest_leakage_or_raise(payload)
    written = write_split_artifacts(payload, args.processed_dir)

    args.metadata_dir.mkdir(parents=True, exist_ok=True)
    meta_path = args.metadata_dir / "split_manifest.json"
    meta_path.write_text(
        json.dumps(
            {
                "manifest_version": payload["manifest_version"],
                "seed": payload["seed"],
                "dataset_version": payload["dataset_version"],
                "n_train_runs": len(payload["train_runs"]),
                "n_validation_runs": len(payload["validation_runs"]),
                "n_test_runs": len(payload["test_runs"]),
                "class_coverage": payload["class_coverage"],
                "limitations": payload["limitations"],
                "artifacts": {k: str(v) for k, v in written.items()},
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    print("Entrega A3 gerada (apenas split — sem treinamento).", flush=True)
    print(f"  seed={payload['seed']} dataset={payload['dataset_version']}", flush=True)
    print(f"  train_runs:      {len(payload['train_runs'])}", flush=True)
    print(f"  validation_runs: {len(payload['validation_runs'])}", flush=True)
    print(f"  test_runs:       {len(payload['test_runs'])}", flush=True)
    for key, path in written.items():
        print(f"  - {key}: {path}", flush=True)
    print(f"  - metadata: {meta_path}", flush=True)
    if payload["limitations"]:
        print("Limitações documentadas:", flush=True)
        for line in payload["limitations"]:
            print(f"  * {line}", flush=True)

    if args.skip_methodology_tests:
        print("WARNING: methodology suite skipped by flag.", flush=True)
        return 0

    return run_methodology_suite_or_abort(repo_root=_repo_root())


if __name__ == "__main__":
    raise SystemExit(main())
