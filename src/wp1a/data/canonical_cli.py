"""CLI da SPEC-002 — dataset canônico.

Uso::

    python -m wp1a.data.canonical_cli
    make canonical-dataset
"""

from __future__ import annotations

import argparse
from pathlib import Path

from wp1a.data.canonical import (
    DATASET_VERSION,
    build_and_register,
    load_canonical_registry,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        description="WP1A SPEC-002 — construir e registrar o dataset canônico."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=root / "data" / "raw",
        help="Arquivos brutos imutáveis (default: data/raw).",
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=root / "data" / "processed",
        help="Destino da tabela e do registro canônicos (default: data/processed).",
    )
    parser.add_argument(
        "--a1-metadata",
        type=Path,
        default=root / "results" / "metadata" / "audit_counts.json",
        help="Metadados A1 (default: results/metadata/audit_counts.json).",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=root / "results" / "metadata",
        help="Cópia enxuta do registro para results/metadata/.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written = build_and_register(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        a1_metadata_path=args.a1_metadata,
        metadata_dir=args.metadata_dir,
    )
    registry = load_canonical_registry(args.processed_dir)
    counts = registry["counts"]
    print(f"Dataset canônico registrado: {DATASET_VERSION}")
    print(
        f"  rows={counts['n_rows']} runs={counts['n_runs']} "
        f"classes={counts['n_classes']} features={counts['n_features']}"
    )
    print(f"  excluded files: {len(registry['source_files_excluded'])}")
    print(f"  orientations applied: {len(registry['orientations_applied'])}")
    print("Artefatos:")
    for key, path in written.items():
        print(f"  - {key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
