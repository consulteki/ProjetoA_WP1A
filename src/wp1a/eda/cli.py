"""CLI da Etapa 2 — análise exploratória (SPEC-003 / Entrega A2).

Uso::

    python -m wp1a.eda.cli
    make eda
"""

from __future__ import annotations

import argparse
from pathlib import Path

from wp1a.eda.report import run_eda


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        description="WP1A SPEC-003 — EDA do dataset canônico (Entrega A2)."
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=root / "data" / "processed",
        help="Diretório do dataset canônico (default: data/processed).",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=root / "results" / "figures",
        help="Destino das figuras A2 (default: results/figures).",
    )
    parser.add_argument(
        "--tables-dir",
        type=Path,
        default=root / "results" / "tables",
        help="Destino das tabelas A2 (default: results/tables).",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=root / "reports" / "eda",
        help="Destino do relatório A2 (default: reports/eda).",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=root / "results" / "metadata",
        help="Metadados da execução EDA (default: results/metadata).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    artifacts = run_eda(
        processed_dir=args.processed_dir,
        figures_dir=args.figures_dir,
        tables_dir=args.tables_dir,
        reports_dir=args.reports_dir,
        metadata_dir=args.metadata_dir,
    )
    print("Entrega A2 gerada (EDA descritiva — sem alteração de protocolo).")
    print(f"  report: {artifacts.report}")
    print(f"  observations: {artifacts.observations}")
    print(f"  metadata: {artifacts.metadata}")
    print(f"  figures ({len(artifacts.figures)}):")
    for key, path in sorted(artifacts.figures.items()):
        print(f"    - {key}: {path}")
    print(f"  tables ({len(artifacts.tables)}):")
    for key, path in sorted(artifacts.tables.items()):
        print(f"    - {key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
