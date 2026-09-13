"""Tests that reject an invalid dataset schema.

Reference: docs/specs/SPEC-000-master.md §5 (DS-01..DS-06);
skill data-audit (skills/data-audit/SKILL.md).
"""

from __future__ import annotations

import numpy as np
import pytest

from wp1a.errors import SchemaError
from wp1a.data.schema import validate_schema


def test_valid_dataset_passes_schema_validation(valid_dataset):
    validate_schema(valid_dataset)  # must not raise


def test_rejects_non_dataframe_input():
    with pytest.raises(SchemaError, match="DataFrame"):
        validate_schema({"not": "a dataframe"})


def test_rejects_missing_feature_columns(valid_dataset):
    broken = valid_dataset.drop(columns=["xmeas_1", "xmv_1"])
    with pytest.raises(SchemaError, match="missing required columns"):
        validate_schema(broken)


def test_rejects_wrong_feature_count(valid_dataset):
    broken = valid_dataset.drop(columns=["xmeas_1"])
    with pytest.raises(SchemaError, match="52 process-variable columns"):
        validate_schema(broken)


def test_rejects_missing_run_id_column(valid_dataset):
    broken = valid_dataset.drop(columns=["run_id"])
    with pytest.raises(SchemaError, match="missing required columns"):
        validate_schema(broken)


def test_rejects_missing_class_label_column(valid_dataset):
    broken = valid_dataset.drop(columns=["class_label"])
    with pytest.raises(SchemaError, match="missing required columns"):
        validate_schema(broken)


def test_rejects_non_numeric_feature_column(valid_dataset):
    broken = valid_dataset.copy()
    broken["xmeas_1"] = broken["xmeas_1"].astype(str)
    with pytest.raises(SchemaError, match="not numeric"):
        validate_schema(broken)


def test_rejects_class_label_out_of_canonical_range(valid_dataset):
    broken = valid_dataset.copy()
    broken.loc[broken.index[0], "class_label"] = 99
    with pytest.raises(SchemaError, match="outside 0..20"):
        validate_schema(broken)


def test_rejects_infinite_feature_values(valid_dataset):
    broken = valid_dataset.copy()
    broken.loc[broken.index[0], "xmeas_5"] = np.inf
    with pytest.raises(SchemaError, match="infinite"):
        validate_schema(broken)


def test_rejects_null_run_id(valid_dataset):
    broken = valid_dataset.copy()
    broken.loc[broken.index[0], "run_id"] = None
    with pytest.raises(SchemaError, match="null"):
        validate_schema(broken)


def test_rejects_null_class_label(valid_dataset):
    broken = valid_dataset.copy()
    broken.loc[broken.index[0], "class_label"] = None
    with pytest.raises(SchemaError, match="null"):
        validate_schema(broken)


def test_rejects_empty_dataframe(valid_dataset):
    broken = valid_dataset.iloc[0:0]
    with pytest.raises(SchemaError, match="zero rows"):
        validate_schema(broken)
