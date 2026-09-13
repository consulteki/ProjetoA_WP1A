"""Tests that reject incomplete experiment metadata.

Reference: docs/adr/ADR-003-reproducibility-requirements.md (REP-01..06);
docs/adr/ADR-005-experiment-configuration.md;
skill ml-training (skills/ml-training/SKILL.md).
"""

from __future__ import annotations

import copy

import pytest

from wp1a.errors import IncompleteMetadataError
from wp1a.tracking.metadata_guard import REQUIRED_METADATA_FIELDS, validate_experiment_metadata


@pytest.fixture
def complete_metadata() -> dict:
    return {
        "experiment_id": "exp-2026-09-13-001",
        "seed": 123,
        "dataset_version": "tep-canonical-v1",
        "split_manifest_path": "data/processed/split_manifest_v1.json",
        "software_versions": {"python": "3.11.15", "scikit-learn": "1.5.0"},
        "hyperparameters": {"model": "random_forest", "n_estimators": 300},
        "timestamp": "2026-09-13T12:00:00Z",
    }


def test_complete_metadata_passes(complete_metadata):
    validate_experiment_metadata(complete_metadata)  # must not raise


def test_rejects_non_dict_metadata():
    with pytest.raises(IncompleteMetadataError, match="must be a dict"):
        validate_experiment_metadata(["not", "a", "dict"])


@pytest.mark.parametrize("field", REQUIRED_METADATA_FIELDS)
def test_rejects_metadata_missing_each_required_field(complete_metadata, field):
    broken = copy.deepcopy(complete_metadata)
    del broken[field]
    with pytest.raises(IncompleteMetadataError, match=field):
        validate_experiment_metadata(broken)


@pytest.mark.parametrize(
    "field,empty_value",
    [
        ("seed", None),
        ("dataset_version", ""),
        ("software_versions", {}),
        ("hyperparameters", {}),
        ("split_manifest_path", ""),
    ],
)
def test_rejects_metadata_with_empty_required_field(complete_metadata, field, empty_value):
    broken = copy.deepcopy(complete_metadata)
    broken[field] = empty_value
    with pytest.raises(IncompleteMetadataError, match="empty"):
        validate_experiment_metadata(broken)


def test_reports_all_missing_fields_at_once(complete_metadata):
    broken = {"experiment_id": complete_metadata["experiment_id"]}
    with pytest.raises(IncompleteMetadataError) as exc_info:
        validate_experiment_metadata(broken)
    message = str(exc_info.value)
    for field in REQUIRED_METADATA_FIELDS:
        if field != "experiment_id":
            assert field in message
