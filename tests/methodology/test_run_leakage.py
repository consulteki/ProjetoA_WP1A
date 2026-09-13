"""Tests that reject run-level (execution-level) leakage between
train/validation/test partitions.

Reference: docs/adr/ADR-001-run-as-experimental-grouping-unit.md;
docs/specs/SPEC-000-master.md INV-01/INV-02;
skill grouped-split (skills/grouped-split/SKILL.md).
"""

from __future__ import annotations

import pytest

from wp1a.errors import RunLeakageError
from wp1a.splitting.run_leakage import check_manifest_disjoint, check_run_disjoint


def test_disjoint_partitions_pass(run_class_map):
    runs = sorted(run_class_map.keys())
    third = len(runs) // 3
    train, val, test = runs[:third], runs[third : 2 * third], runs[2 * third :]
    check_run_disjoint(train, val, test)  # must not raise


def test_rejects_run_shared_between_train_and_test(run_class_map):
    runs = sorted(run_class_map.keys())
    train = runs[:10] + [runs[-1]]  # deliberately leaks the last test run into train
    val = runs[10:15]
    test = runs[15:]
    with pytest.raises(RunLeakageError, match="train/test"):
        check_run_disjoint(train, val, test)


def test_rejects_run_shared_between_train_and_val(run_class_map):
    runs = sorted(run_class_map.keys())
    train = runs[:10]
    val = runs[5:15]  # overlaps train on runs[5:10]
    test = runs[15:]
    with pytest.raises(RunLeakageError, match="train/val"):
        check_run_disjoint(train, val, test)


def test_rejects_run_shared_between_val_and_test(run_class_map):
    runs = sorted(run_class_map.keys())
    train = runs[:10]
    val = runs[10:20]
    test = runs[15:]  # overlaps val on runs[15:20]
    with pytest.raises(RunLeakageError, match="val/test"):
        check_run_disjoint(train, val, test)


def test_reports_multiple_simultaneous_overlaps(run_class_map):
    runs = sorted(run_class_map.keys())
    shared = runs[0]
    train = [shared] + runs[1:10]
    val = [shared] + runs[10:15]
    test = [shared] + runs[15:20]
    with pytest.raises(RunLeakageError) as exc_info:
        check_run_disjoint(train, val, test)
    message = str(exc_info.value)
    assert "train/val" in message
    assert "train/test" in message
    assert "val/test" in message


def test_rejects_split_by_row_instead_of_by_run(valid_dataset):
    """Regression guard for MET-R01/LEAK-R04: splitting a dataframe by row
    index instead of grouping by run_id causes the same run to land in
    more than one partition, because each run spans multiple consecutive
    rows in the fixture.
    """
    n = len(valid_dataset)
    # Offset the cut so it deliberately falls inside a run's row block
    # (runs are stored as contiguous blocks of ROWS_PER_RUN rows in the
    # fixture); a cut aligned exactly on a run boundary would not
    # reproduce the leakage this test exists to catch.
    cut = n // 2 + 5
    train_df = valid_dataset.iloc[:cut]
    test_df = valid_dataset.iloc[cut:]
    train_runs = set(train_df["run_id"])
    test_runs = set(test_df["run_id"])

    assert train_runs & test_runs, "fixture must reproduce the row-split leakage scenario"

    with pytest.raises(RunLeakageError):
        check_run_disjoint(train_runs, set(), test_runs)


def test_check_manifest_disjoint_accepts_valid_manifest(run_class_map):
    runs = sorted(run_class_map.keys())
    third = len(runs) // 3
    manifest = {
        "train": runs[:third],
        "val": runs[third : 2 * third],
        "test": runs[2 * third :],
    }
    check_manifest_disjoint(manifest)  # must not raise


def test_check_manifest_disjoint_rejects_leaking_manifest(run_class_map):
    runs = sorted(run_class_map.keys())
    manifest = {
        "train": runs[:10] + [runs[-1]],
        "val": runs[10:15],
        "test": runs[15:],
    }
    with pytest.raises(RunLeakageError):
        check_manifest_disjoint(manifest)


def test_check_manifest_disjoint_rejects_incomplete_manifest(run_class_map):
    runs = sorted(run_class_map.keys())
    manifest = {"train": runs[:10], "test": runs[10:]}  # missing "val"
    with pytest.raises(ValueError, match="missing partition"):
        check_manifest_disjoint(manifest)
