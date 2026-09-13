"""Experiment metadata completeness checks.

Reference: docs/adr/ADR-003-reproducibility-requirements.md (REP-01..06);
docs/adr/ADR-005-experiment-configuration.md;
docs/project/requirements.md RQ-08.
"""

from __future__ import annotations

from typing import Any

from wp1a.errors import IncompleteMetadataError

# Minimum metadata required to consider an experiment run reproducible and
# auditable, per REP-01..REP-06 and ADR-005.
REQUIRED_METADATA_FIELDS: tuple[str, ...] = (
    "experiment_id",
    "seed",
    "dataset_version",        # canonical dataset identifier (ADR-004)
    "split_manifest_path",    # reference to the Entrega A3 manifest (ADR-001)
    "software_versions",      # dict: library/language versions (REP-03)
    "hyperparameters",        # dict: final, frozen hyperparameters (REP-04)
    "timestamp",               # when the run/freeze happened
)

def validate_experiment_metadata(metadata: Any) -> None:
    """Validate that ``metadata`` declares every field required for the
    experiment to be reproducible and auditable.

    Raises
    ------
    IncompleteMetadataError
        If ``metadata`` is not a mapping, if any required field is
        missing, or if any required field is present but empty.
    """
    if not isinstance(metadata, dict):
        raise IncompleteMetadataError(f"metadata must be a dict, got {type(metadata).__name__}")

    missing = [f for f in REQUIRED_METADATA_FIELDS if f not in metadata]
    empty = [
        f
        for f in REQUIRED_METADATA_FIELDS
        if f in metadata and _is_empty(metadata[f])
    ]

    problems: list[str] = []
    if missing:
        problems.append(f"missing required metadata fields: {missing}")
    if empty:
        problems.append(f"metadata fields present but empty: {empty}")

    if problems:
        raise IncompleteMetadataError("; ".join(problems))


def _is_empty(value: Any) -> bool:
    if isinstance(value, (str, dict, list, tuple)):
        return len(value) == 0
    return value is None
