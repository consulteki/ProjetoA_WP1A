"""CLI da Etapa 4 — pré-processamento (SPEC-005).

Não treina modelos. Ajusta StandardScaler apenas no treino e aplica
transform em train/validation/test.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from wp1a.preprocessing.pipeline import PREPROCESSOR_VERSION, run_preprocessing


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        description="WP1A SPEC-005 — pré-processamento (fit só no treino)."
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=root / "data" / "processed",
        help="Canônico + A3 + destino dos conjuntos pré-processados.",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=root / "results" / "metadata",
        help="Metadados enxutos (default: results/metadata).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written = run_preprocessing(
        processed_dir=args.processed_dir,
        metadata_dir=args.metadata_dir,
    )
    print(f"SPEC-005 ok — {PREPROCESSOR_VERSION}")
    print("  policy: scaler.fit(TRAIN); transform(TRAIN|VAL|TEST); never fit(all_data)")
    for key, path in written.items():
        print(f"  - {key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
