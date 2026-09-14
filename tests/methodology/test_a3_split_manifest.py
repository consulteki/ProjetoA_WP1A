"""Methodology checks against the generated A3 split manifesto (SPEC-004).

These tests bind the Entrega A3 artifact on disk to LEAK-R01 / TEST-R01.
If the manifesto is absent (pipeline not yet run), they skip — the CLI
``make split`` always regenerates A3 and then re-runs this suite.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wp1a.splitting.grouped_split import grouped_split
from wp1a.splitting.reproducibility import assert_split_reproducible
from wp1a.splitting.run_leakage import check_manifest_disjoint, check_run_disjoint

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "data" / "processed" / "split_manifest_v1.json"


@pytest.fixture(scope="module")
def a3_manifest():
    if not MANIFEST_PATH.is_file():
        pytest.skip("A3 manifesto not found — run `make split` / SPEC-004 first")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_a3_train_val_test_runs_are_pairwise_disjoint(a3_manifest):
    check_run_disjoint(
        a3_manifest["train_runs"],
        a3_manifest["validation_runs"],
        a3_manifest["test_runs"],
    )


def test_a3_partitions_alias_is_disjoint(a3_manifest):
    check_manifest_disjoint(a3_manifest["partitions"])


def test_a3_lists_match_partition_aliases(a3_manifest):
    assert a3_manifest["train_runs"] == a3_manifest["partitions"]["train"]
    assert a3_manifest["validation_runs"] == a3_manifest["partitions"]["val"]
    assert a3_manifest["test_runs"] == a3_manifest["partitions"]["test"]


def test_a3_covers_all_runs_exactly_once(a3_manifest):
    train = set(a3_manifest["train_runs"])
    val = set(a3_manifest["validation_runs"])
    test = set(a3_manifest["test_runs"])
    assert len(train) == len(a3_manifest["train_runs"])
    assert len(val) == len(a3_manifest["validation_runs"])
    assert len(test) == len(a3_manifest["test_runs"])
    union = train | val | test
    assert union == set(a3_manifest["run_class_map"])
    assert len(union) == len(train) + len(val) + len(test)


def test_a3_is_reproducible_from_recorded_seed(a3_manifest):
    run_class_map = {str(k): int(v) for k, v in a3_manifest["run_class_map"].items()}
    run_ids = sorted(run_class_map)
    classes = [run_class_map[r] for r in run_ids]
    reproduced = assert_split_reproducible(
        grouped_split, run_ids, classes, seed=int(a3_manifest["seed"])
    )
    assert reproduced["train"] == a3_manifest["train_runs"]
    assert reproduced["val"] == a3_manifest["validation_runs"]
    assert reproduced["test"] == a3_manifest["test_runs"]


def test_a3_train_covers_all_21_classes(a3_manifest):
    coverage = a3_manifest["class_coverage"]["train"]
    assert coverage["n_classes"] == 21
    assert coverage["missing_classes"] == []
