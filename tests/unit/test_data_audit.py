"""Unit tests for SPEC-001 data audit (happy path + edge cases).

Uses small deterministic Braatz-like fixtures under a temporary directory
(TEST-R06) — never the full production dataset.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from wp1a.data.audit import run_audit, write_audit_artifacts
from wp1a.data.raw_loader import parse_braatz_filename


def _write_dat(path: Path, matrix: np.ndarray) -> None:
    np.savetxt(path, matrix, fmt="%.6e")


@pytest.fixture
def braatz_fixture_dir(tmp_path: Path) -> Path:
    """Minimal Braatz-shaped set: classes 0 and 1, train+test, 52 features."""
    rng = np.random.default_rng(0)
    for fault in (0, 1):
        train = rng.normal(size=(8, 52))
        test = rng.normal(size=(12, 52))
        _write_dat(tmp_path / f"d{fault:02d}.dat", train)
        _write_dat(tmp_path / f"d{fault:02d}_te.dat", test)
    return tmp_path


def test_parse_braatz_filename() -> None:
    fault, split, run_id = parse_braatz_filename("d07_te.dat")
    assert fault == 7
    assert split == "braatz_test"
    assert run_id == "braatz_te_fault07"


def test_audit_happy_path_covers_eight_items(braatz_fixture_dir: Path) -> None:
    result = run_audit(braatz_fixture_dir)
    assert [f.item for f in result.findings] == list(range(1, 9))
    assert all(f.summary for f in result.findings)
    # Fixture has only classes 0 and 1 → divergence vs DS-03 must be explicit.
    assert result.finding_by_item(4).status == "divergence"
    assert result.normative_check["DS-03_status"] == "divergence"
    assert result.finding_by_item(8).status == "ok"
    assert result.finding_by_item(8).details["automated_check"] is True


def test_audit_detects_transposed_file(tmp_path: Path) -> None:
    rng = np.random.default_rng(1)
    # Transposed train file: 52 x N instead of samples x 52.
    _write_dat(tmp_path / "d00.dat", rng.normal(size=(52, 8)))
    # Test file with correct orientation but wrong row count still flagged;
    # focus assertion on the transposed train file.
    _write_dat(tmp_path / "d00_te.dat", rng.normal(size=(960, 52)))
    result = run_audit(tmp_path)
    assert result.finding_by_item(2).status == "anomaly"
    assert "d00.dat" in result.finding_by_item(2).details["anomalies"]
    assert "d00.dat" in result.metadata["shape_anomalies"]


def test_audit_detects_class_21_extra(tmp_path: Path) -> None:
    rng = np.random.default_rng(2)
    for fault in range(0, 22):
        _write_dat(tmp_path / f"d{fault:02d}.dat", rng.normal(size=(4, 52)))
        _write_dat(tmp_path / f"d{fault:02d}_te.dat", rng.normal(size=(4, 52)))
    result = run_audit(tmp_path)
    assert result.finding_by_item(4).status == "divergence"
    assert 21 in result.normative_check["DS-03_observed_classes"]
    assert result.metadata["extra_classes_beyond_ds03"] == [21]


def test_write_audit_artifacts(braatz_fixture_dir: Path, tmp_path: Path) -> None:
    result = run_audit(braatz_fixture_dir)
    reports = tmp_path / "reports"
    metadata = tmp_path / "metadata"
    tables = tmp_path / "tables"
    written = write_audit_artifacts(
        result, reports_dir=reports, metadata_dir=metadata, tables_dir=tables
    )
    assert (reports / "A1_audit_report.md").is_file()
    assert (reports / "A1_audit_report.pdf").is_file()
    assert (reports / "A1_findings.csv").is_file()
    assert (reports / "A1_08_file_class_run.csv").is_file()
    assert (metadata / "audit_counts.json").is_file()
    assert (tables / "A1_dataset_characterization.csv").is_file()
    assert set(written) >= {"report_md", "report_pdf", "metadata", "characterization"}


def test_audit_rejects_empty_dir(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        run_audit(tmp_path)
