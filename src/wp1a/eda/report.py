"""Persistência da Entrega A2 (tabelas, figuras, relatório)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from wp1a.eda.analysis import (
    PROTOCOL_DISCLAIMER,
    EdaArtifacts,
    build_observations,
    compute_eda_tables,
    load_canonical_for_eda,
    _utc_now,
)
from wp1a.eda.figures import generate_all_figures

TABLE_NAMES = (
    "descriptive_global",
    "descriptive_by_class",
    "class_distribution",
    "variability",
    "correlation",
    "correlation_top_pairs",
    "pca_variance",
    "pca_projection",
    "normal_vs_fault",
)


def _write_tables(tables: dict[str, pd.DataFrame], tables_dir: Path) -> dict[str, Path]:
    tables_dir = Path(tables_dir)
    tables_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for name in TABLE_NAMES:
        # Large projection table is compressed; others stay plain CSV.
        if name == "pca_projection":
            path = tables_dir / f"A2_{name}.csv.gz"
            tables[name].to_csv(path, index=False, compression="gzip")
        else:
            path = tables_dir / f"A2_{name}.csv"
            tables[name].to_csv(path, index=False)
        written[name] = path
    return written


def render_a2_report(
    *,
    registry: dict[str, Any],
    tables: dict[str, pd.DataFrame],
    figure_paths: dict[str, Path],
    table_paths: dict[str, Path],
) -> str:
    dist = tables["class_distribution"]
    lines = [
        "# Entrega A2 — Análise Exploratória (TEP)",
        "",
        f"- Gerado em: `{_utc_now()}`",
        f"- Dataset canônico: `{registry.get('dataset_version')}`",
        f"- Spec: SPEC-003 / skill `exploratory-analysis`",
        "",
        "## Disclaimer",
        "",
        PROTOCOL_DISCLAIMER,
        "",
        "## Elementos obrigatórios (RP-02)",
        "",
        "### 1. Estatísticas descritivas",
        "",
        f"- Global: `{table_paths['descriptive_global']}`",
        f"- Por classe: `{table_paths['descriptive_by_class']}`",
        f"- Cobertura: {len(tables['descriptive_global'])} variáveis × "
        f"{tables['class_distribution']['class_label'].nunique()} classes.",
        "",
        "### 2. Distribuição das 21 classes",
        "",
        f"- Tabela: `{table_paths['class_distribution']}`",
        f"- Figuras: `{figure_paths['class_samples']}`, `{figure_paths['class_runs']}`",
        f"- Amostras totais: {int(dist['n_samples'].sum())}; "
        f"runs totais: {int(dist['n_runs'].sum())}.",
        "",
        "### 3. Variabilidade das variáveis",
        "",
        f"- Tabela: `{table_paths['variability']}`",
        f"- Figura: `{figure_paths['variability']}`",
        "",
        "### 4. Matriz de correlação",
        "",
        f"- Tabela completa: `{table_paths['correlation']}`",
        f"- Top pares: `{table_paths['correlation_top_pairs']}`",
        f"- Figura: `{figure_paths['correlation']}`",
        "",
        "### 5. Projeção PCA",
        "",
        f"- Variância: `{table_paths['pca_variance']}`",
        f"- Projeção: `{table_paths['pca_projection']}`",
        f"- Figuras: `{figure_paths['pca_regime']}`, `{figure_paths['pca_class']}`, "
        f"`{figure_paths['pca_variance']}`",
        "",
        "### 6. Comparação normal vs falha",
        "",
        f"- Tabela: `{table_paths['normal_vs_fault']}`",
        f"- Figura: `{figure_paths['normal_vs_fault']}`",
        "",
        "## Rastreabilidade",
        "",
        "- Entrada exclusiva: dataset canônico registrado (SPEC-002).",
        "- Figuras geradas programaticamente por `wp1a.eda.figures`.",
        "- Observações qualitativas: `reports/eda/A2_observations.md` "
        "(não alteram o protocolo).",
        "",
    ]
    return "\n".join(lines)


def run_eda(
    *,
    processed_dir: Path,
    figures_dir: Path,
    tables_dir: Path,
    reports_dir: Path,
    metadata_dir: Path,
) -> EdaArtifacts:
    df, registry = load_canonical_for_eda(processed_dir)
    tables = compute_eda_tables(df)
    table_paths = _write_tables(tables, tables_dir)
    figure_paths = generate_all_figures(tables, figures_dir)

    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    observations_text = build_observations(tables, registry)
    observations_path = reports_dir / "A2_observations.md"
    observations_path.write_text(observations_text, encoding="utf-8")

    report_text = render_a2_report(
        registry=registry,
        tables=tables,
        figure_paths=figure_paths,
        table_paths=table_paths,
    )
    report_path = reports_dir / "A2_eda_report.md"
    report_path.write_text(report_text, encoding="utf-8")

    metadata_dir = Path(metadata_dir)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_dir / "eda_run.json"
    metadata = {
        "spec": "SPEC-003",
        "delivery": "A2",
        "generated_at": _utc_now(),
        "dataset_version": registry.get("dataset_version"),
        "n_rows": int(len(df)),
        "n_features": 52,
        "n_classes": int(df["class_label"].nunique()),
        "protocol_disclaimer": PROTOCOL_DISCLAIMER,
        "tables": {k: str(v) for k, v in table_paths.items()},
        "figures": {k: str(v) for k, v in figure_paths.items()},
        "report": str(report_path),
        "observations": str(observations_path),
        "elements_covered": [
            "descriptive_stats",
            "class_distribution",
            "variability",
            "correlation",
            "pca",
            "normal_vs_fault",
        ],
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    return EdaArtifacts(
        tables=table_paths,
        figures=figure_paths,
        report=report_path,
        observations=observations_path,
        metadata=metadata_path,
    )
