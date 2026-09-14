"""Tests for SPEC-004 grouped split (Entrega A3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wp1a.errors import RunLeakageError
from wp1a.splitting.grouped_split import class_coverage, grouped_split
from wp1a.splitting.reproducibility import assert_split_reproducible
from wp1a.splitting.run_leakage import check_manifest_disjoint, check_run_disjoint


@pytest.fixture
def two_runs_per_class_map() -> dict[str, int]:
    """Mirrors the canonical Braatz layout: 2 runs × 21 classes."""
    mapping: dict[str, int] = {}
    for c in range(21):
        mapping[f"braatz_tr_fault{c:02d}"] = c
        mapping[f"braatz_te_fault{c:02d}"] = c
    return mapping


def test_grouped_split_is_reproducible_and_disjoint(two_runs_per_class_map):
    run_ids = sorted(two_runs_per_class_map)
    classes = [two_runs_per_class_map[r] for r in run_ids]
    manifest = assert_split_reproducible(grouped_split, run_ids, classes, seed=42)
    check_manifest_disjoint(manifest)
    check_run_disjoint(manifest["train"], manifest["val"], manifest["test"])
    covered = set(manifest["train"]) | set(manifest["val"]) | set(manifest["test"])
    assert covered == set(run_ids)


def test_grouped_split_puts_all_classes_in_train(two_runs_per_class_map):
    run_ids = sorted(two_runs_per_class_map)
    classes = [two_runs_per_class_map[r] for r in run_ids]
    manifest = grouped_split(run_ids, classes, seed=42)
    coverage = class_coverage(manifest, two_runs_per_class_map)
    assert coverage["train"]["n_classes"] == 21
    assert coverage["train"]["missing_classes"] == []
    # With 2 runs/class, val and test cannot both have 21 classes.
    assert coverage["validation"]["n_classes"] + coverage["test"]["n_classes"] == 21
    assert coverage["train"]["n_runs"] == 21
    assert coverage["validation"]["n_runs"] + coverage["test"]["n_runs"] == 21


def test_grouped_split_differs_across_seeds(two_runs_per_class_map):
    run_ids = sorted(two_runs_per_class_map)
    classes = [two_runs_per_class_map[r] for r in run_ids]
    a = grouped_split(run_ids, classes, seed=1)
    b = grouped_split(run_ids, classes, seed=2)
    assert a != b


def test_grouped_split_accepts_mapping_classes(two_runs_per_class_map):
    run_ids = sorted(two_runs_per_class_map)
    manifest = grouped_split(run_ids, two_runs_per_class_map, seed=7)
    check_manifest_disjoint(manifest)
