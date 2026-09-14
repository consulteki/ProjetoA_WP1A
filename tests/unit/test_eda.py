"""Unit tests for SPEC-003 exploratory analysis (Entrega A2)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from wp1a.data.canonical import (
    CANONICAL_TABLE_NAME,
    DATASET_VERSION,
    REGISTRY_NAME,
)
from wp1a.data.schema import (
    CLASS_LABEL_COLUMN,
    FEATURE_COLUMNS,
    RUN_ID_COLUMN,
    SAMPLE_INDEX_COLUMN,
    SOURCE_FILE_COLUMN,
    SOURCE_SPLIT_COLUMN,
)
from wp1a.eda.analysis import (
    PROTOCOL_DISCLAIMER,
    class_distribution,
    compute_eda_tables,
    descriptive_global,
)
from wp1a.eda.figures import generate_all_figures
from wp1a.eda.report import run_eda


def _synthetic_canonical(n_per_class: int = 12) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    frames = []
    for class_label in range(21):
        for run_i in range(2):
            n = n_per_class
            data = {col: rng.normal(loc=class_label * 0.01, size=n) for col in FEATURE_COLUMNS}
            data[RUN_ID_COLUMN] = f"run_c{class_label:02d}_r{run_i}"
            data[CLASS_LABEL_COLUMN] = class_label
            data[SOURCE_FILE_COLUMN] = f"d{class_label:02d}.dat"
            data[SOURCE_SPLIT_COLUMN] = "braatz_train" if run_i == 0 else "braatz_test"
            data[SAMPLE_INDEX_COLUMN] = np.arange(n, dtype=np.int64)
            frames.append(pd.DataFrame(data))
    return pd.concat(frames, ignore_index=True)


@pytest.fixture
def synthetic_df() -> pd.DataFrame:
    return _synthetic_canonical()


def test_descriptive_and_distribution_cover_21_classes(synthetic_df: pd.DataFrame):
    desc = descriptive_global(synthetic_df)
    assert len(desc) == 52
    dist = class_distribution(synthetic_df)
    assert list(dist["class_label"]) == list(range(21))
    assert dist["n_runs"].min() >= 1


def test_compute_eda_tables_six_elements(synthetic_df: pd.DataFrame):
    tables = compute_eda_tables(synthetic_df)
    required = {
        "descriptive_global",
        "descriptive_by_class",
        "class_distribution",
        "variability",
        "correlation",
        "pca_variance",
        "pca_projection",
        "normal_vs_fault",
    }
    assert required.issubset(tables)
    assert len(tables["pca_variance"]) >= 2
    assert set(tables["class_distribution"]["class_label"]) == set(range(21))


def test_figures_generated_programmatically(synthetic_df: pd.DataFrame, tmp_path: Path):
    tables = compute_eda_tables(synthetic_df)
    figures = generate_all_figures(tables, tmp_path / "figures")
    assert len(figures) >= 6
    for path in figures.values():
        assert path.is_file()
        assert path.stat().st_size > 0
        assert path.suffix == ".png"


def test_run_eda_writes_a2_and_keeps_protocol_disclaimer(tmp_path: Path):
    df = _synthetic_canonical(n_per_class=8)
    processed = tmp_path / "processed"
    processed.mkdir()
    table_path = processed / CANONICAL_TABLE_NAME
    df.to_csv(table_path, index=False, compression="gzip")
    registry = {
        "dataset_version": DATASET_VERSION,
        "status": "canonical",
        "counts": {
            "n_rows": len(df),
            "n_runs": int(df[RUN_ID_COLUMN].nunique()),
            "n_classes": 21,
            "n_features": 52,
            "class_labels": list(range(21)),
        },
        "artifacts": {
            "table": str(table_path),
            "table_sha256": "unused-in-eda-load",
            "content_sha256": "unused-in-eda-load",
        },
    }
    # load_canonical_dataframe validates schema/classes; registry hash checks are
    # not re-run by EDA load path beyond version/status.
    (processed / REGISTRY_NAME).write_text(json.dumps(registry), encoding="utf-8")

    artifacts = run_eda(
        processed_dir=processed,
        figures_dir=tmp_path / "figures",
        tables_dir=tmp_path / "tables",
        reports_dir=tmp_path / "reports",
        metadata_dir=tmp_path / "metadata",
    )
    obs = artifacts.observations.read_text(encoding="utf-8")
    assert PROTOCOL_DISCLAIMER[:40] in obs
    assert "NÃO faz" in obs or "explicitamente NÃO" in obs
    meta = json.loads(artifacts.metadata.read_text(encoding="utf-8"))
    assert meta["elements_covered"] == [
        "descriptive_stats",
        "class_distribution",
        "variability",
        "correlation",
        "pca",
        "normal_vs_fault",
    ]
    assert artifacts.report.is_file()
    assert len(artifacts.figures) >= 6
