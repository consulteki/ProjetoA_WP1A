"""CLI da Etapa 1 — auditoria dos dados brutos (SPEC-001 / Entrega A1).

Uso::

    python -m wp1a.data.audit_cli
    python -m wp1a.data.audit_cli --raw-dir data/raw --reports-dir reports/audit
"""

from __future__ import annotations

import argparse
from pathlib import Path

from wp1a.data.audit import run_audit, write_audit_artifacts


def _repo_root() -> Path:
    # src/wp1a/data/audit_cli.py → parents[3] = repo root
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    root = _repo_root()
    parser = argparse.ArgumentParser(
        description="WP1A SPEC-001 — auditoria dos dados brutos do TEP (Entrega A1)."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=root / "data" / "raw",
        help="Diretório com os arquivos .dat brutos (default: data/raw).",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=root / "reports" / "audit",
        help="Destino da Entrega A1 (default: reports/audit).",
    )
    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=root / "results" / "metadata",
        help="Destino dos metadados de contagens (default: results/metadata).",
    )
    parser.add_argument(
        "--tables-dir",
        type=Path,
        default=root / "results" / "tables",
        help="Destino da tabela de caracterização (default: results/tables).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_audit(args.raw_dir)
    written = write_audit_artifacts(
        result,
        reports_dir=args.reports_dir,
        metadata_dir=args.metadata_dir,
        tables_dir=args.tables_dir,
    )

    print(f"A1 gerada em {args.reports_dir}")
    for finding in result.findings:
        print(f"  [{finding.status:10s}] item {finding.item}: {finding.title}")
    print("Artefatos:")
    for key, path in written.items():
        print(f"  - {key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
