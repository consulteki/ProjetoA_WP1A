"""Tests for SPEC-002 canonical dataset build and schema validation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from wp1a.data.canonical import (
    DATASET_VERSION,
    assert_raw_immutable,
    build_and_register,
    build_canonical_dataframe,
    load_canonical_dataframe,
    load_canonical_registry,
    validate_registry_against_table,
)
from wp1a.data.raw_loader import sha256_file
from wp1a.data.schema import validate_canonical_schema, validate_schema
from wp1a.errors import CanonicalDatasetError, SchemaError


def _write_dat(path: Path, matrix: np.ndarray) -> None:
    np.savetxt(path, matrix, fmt="%.6e")


def _a1_metadata_for(raw_dir: Path) -> dict:
    files = sorted(p.name for p in raw_dir.glob("*.dat"))
    return {
        "spec": "SPEC-001",
        "delivery": "A1",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "sha256_by_file": {name: sha256_file(raw_dir / name) for name in files},
    }


@pytest.fixture
def raw_fixture(tmp_path: Path) -> Path:
    """Braatz-like raw set with class 21 and a transposed d00.dat."""
    rng = np.random.default_rng(7)
    raw = tmp_path / "raw"
    raw.mkdir()
    # Transposed normal train (features x samples).
    _write_dat(raw / "d00.dat", rng.normal(size=(52, 6)))
    _write_dat(raw / "d00_te.dat", rng.normal(size=(10, 52)))
    for fault in range(1, 21):
        _write_dat(raw / f"d{fault:02d}.dat", rng.normal(size=(5, 52)))
        _write_dat(raw / f"d{fault:02d}_te.dat", rng.normal(size=(7, 52)))
    # Extra class 21 (must be excluded by canonical build).
    _write_dat(raw / "d21.dat", rng.normal(size=(5, 52)))
    _write_dat(raw / "d21_te.dat", rng.normal(size=(7, 52)))
    return raw


def test_validate_schema_rejects_nan_feature(valid_dataset):
    broken = valid_dataset.copy()
    broken.loc[broken.index[0], "xmeas_2"] = np.nan
    with pytest.raises(SchemaError, match="NaN"):
        validate_schema(broken)


def test_validate_canonical_schema_requires_provenance(valid_dataset):
    with pytest.raises(SchemaError, match="provenance"):
        validate_canonical_schema(valid_dataset)
    ok = valid_dataset.copy()
    ok["source_file"] = "d00.dat"
    ok["source_split"] = "braatz_train"
    ok["sample_index"] = np.arange(len(ok), dtype=np.int64)
    validate_canonical_schema(ok)


def test_build_excludes_fault_21_and_orients_d00(raw_fixture: Path):
    a1 = _a1_metadata_for(raw_fixture)
    df, info = build_canonical_dataframe(raw_fixture, a1_metadata=a1)
    assert set(info["class_labels"]) == set(range(21))
    assert {e["name"] for e in info["excluded_files"]} == {"d21.dat", "d21_te.dat"}
    assert any(o["name"] == "d00.dat" for o in info["orientations_applied"])
    d00_rows = df.loc[df["source_file"] == "d00.dat"]
    assert len(d00_rows) == 6  # transposed 52x6 → 6 samples
    validate_canonical_schema(df)


def test_raw_immutable_detection(raw_fixture: Path):
    a1 = _a1_metadata_for(raw_fixture)
    assert_raw_immutable(raw_fixture, a1["sha256_by_file"])
    target = raw_fixture / "d01.dat"
    target.write_bytes(target.read_bytes() + b"\n")
    with pytest.raises(CanonicalDatasetError, match="mutated"):
        assert_raw_immutable(raw_fixture, a1["sha256_by_file"])


def test_build_and_register_roundtrip(raw_fixture: Path, tmp_path: Path):
    a1_path = tmp_path / "audit_counts.json"
    a1 = _a1_metadata_for(raw_fixture)
    a1_path.write_text(json.dumps(a1), encoding="utf-8")
    processed = tmp_path / "processed"
    meta = tmp_path / "metadata"
    written = build_and_register(
        raw_dir=raw_fixture,
        processed_dir=processed,
        a1_metadata_path=a1_path,
        metadata_dir=meta,
    )
    registry = load_canonical_registry(processed)
    assert registry["dataset_version"] == DATASET_VERSION
    assert registry["status"] == "canonical"
    assert registry["counts"]["n_classes"] == 21
    df = load_canonical_dataframe(processed)
    validate_registry_against_table(registry, df, table_path=written["table"])
    # Raw checksums unchanged after build.
    assert_raw_immutable(raw_fixture, a1["sha256_by_file"])
    assert (meta / "canonical_dataset.json").is_file()
    assert (processed / "NON_CANONICAL.md").is_file()


def test_build_requires_a1_metadata(tmp_path: Path, raw_fixture: Path):
    with pytest.raises(CanonicalDatasetError, match="A1 metadata"):
        build_and_register(
            raw_dir=raw_fixture,
            processed_dir=tmp_path / "processed",
            a1_metadata_path=tmp_path / "missing.json",
        )
