"""Canonical schema definition and validation for the TEP dataset.

Reference: docs/specs/SPEC-000-master.md §5 (DS-01..DS-06) — 52 process
variables, 21 classes (1 normal + 20 faults), run_id traceability.
Reference: docs/adr/ADR-004-canonical-dataset.md; SPEC-002.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from wp1a.errors import SchemaError

# 41 measured process variables (XMEAS) + 11 manipulated variables (XMV) = 52,
# matching SPEC-000 DS-02 ("52 variáveis de processo").
FEATURE_COLUMNS: tuple[str, ...] = tuple(
    [f"xmeas_{i}" for i in range(1, 42)] + [f"xmv_{i}" for i in range(1, 12)]
)

RUN_ID_COLUMN = "run_id"
CLASS_LABEL_COLUMN = "class_label"
SOURCE_FILE_COLUMN = "source_file"
SOURCE_SPLIT_COLUMN = "source_split"
SAMPLE_INDEX_COLUMN = "sample_index"

ID_COLUMNS: tuple[str, ...] = (RUN_ID_COLUMN, CLASS_LABEL_COLUMN)
PROVENANCE_COLUMNS: tuple[str, ...] = (
    SOURCE_FILE_COLUMN,
    SOURCE_SPLIT_COLUMN,
    SAMPLE_INDEX_COLUMN,
)
REQUIRED_COLUMNS: tuple[str, ...] = FEATURE_COLUMNS + ID_COLUMNS
CANONICAL_REQUIRED_COLUMNS: tuple[str, ...] = REQUIRED_COLUMNS + PROVENANCE_COLUMNS

N_EXPECTED_FEATURES = 52
N_EXPECTED_CLASSES = 21
# class_label 0 = normal condition, 1..20 = the 20 fault conditions (DS-03).
VALID_CLASS_LABELS: frozenset[int] = frozenset(range(0, N_EXPECTED_CLASSES))

assert len(FEATURE_COLUMNS) == N_EXPECTED_FEATURES, "FEATURE_COLUMNS must define exactly 52 columns"


def validate_schema(df: pd.DataFrame) -> None:
    """Validate that ``df`` conforms to the core WP1A/TEP schema (DS-02..DS-04).

    Raises
    ------
    SchemaError
        Listing every violation found (not only the first one), so a
        single failing call is informative on its own.
    """
    if not isinstance(df, pd.DataFrame):
        raise SchemaError(f"expected a pandas.DataFrame, got {type(df).__name__}")

    errors: list[str] = []
    columns = set(df.columns)

    missing = sorted(c for c in REQUIRED_COLUMNS if c not in columns)
    if missing:
        errors.append(f"missing required columns: {missing}")

    present_features = [c for c in FEATURE_COLUMNS if c in columns]
    if len(present_features) != N_EXPECTED_FEATURES:
        errors.append(
            f"expected {N_EXPECTED_FEATURES} process-variable columns (DS-02), "
            f"found {len(present_features)}"
        )

    for col in present_features:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"feature column '{col}' is not numeric (dtype={df[col].dtype})")
        else:
            values = df[col].to_numpy(dtype="float64", copy=False)
            if np.isnan(values).any():
                errors.append(f"feature column '{col}' contains NaN values")
            elif np.isinf(values).any():
                errors.append(f"feature column '{col}' contains infinite values")

    if RUN_ID_COLUMN in columns:
        if df[RUN_ID_COLUMN].isna().any():
            errors.append(f"column '{RUN_ID_COLUMN}' contains null values")

    if CLASS_LABEL_COLUMN in columns:
        if df[CLASS_LABEL_COLUMN].isna().any():
            errors.append(f"column '{CLASS_LABEL_COLUMN}' contains null values")
        else:
            observed: Iterable = df[CLASS_LABEL_COLUMN].unique().tolist()
            bad = sorted(v for v in observed if v not in VALID_CLASS_LABELS)
            if bad:
                errors.append(f"column '{CLASS_LABEL_COLUMN}' contains values outside 0..20: {bad}")

    if len(df) == 0:
        errors.append("dataframe has zero rows")

    if errors:
        raise SchemaError("; ".join(errors))


def validate_canonical_schema(df: pd.DataFrame) -> None:
    """Validate core schema plus DS-06 provenance columns required of the canonical table."""
    validate_schema(df)
    errors: list[str] = []
    columns = set(df.columns)
    missing = sorted(c for c in PROVENANCE_COLUMNS if c not in columns)
    if missing:
        errors.append(f"missing canonical provenance columns (DS-06): {missing}")
    else:
        if df[SOURCE_FILE_COLUMN].isna().any():
            errors.append(f"column '{SOURCE_FILE_COLUMN}' contains null values")
        if df[SOURCE_SPLIT_COLUMN].isna().any():
            errors.append(f"column '{SOURCE_SPLIT_COLUMN}' contains null values")
        if df[SAMPLE_INDEX_COLUMN].isna().any():
            errors.append(f"column '{SAMPLE_INDEX_COLUMN}' contains null values")
        elif not pd.api.types.is_integer_dtype(df[SAMPLE_INDEX_COLUMN]):
            if not pd.api.types.is_numeric_dtype(df[SAMPLE_INDEX_COLUMN]):
                errors.append(f"column '{SAMPLE_INDEX_COLUMN}' must be integer-like")
    if errors:
        raise SchemaError("; ".join(errors))
