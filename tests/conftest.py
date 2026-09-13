"""Shared fixtures for the WP1A validation-guard test suite.

These fixtures build a small, fully synthetic TEP-shaped dataset (not real
TEP data) with the exact canonical schema (SPEC-000 §5): 52 numeric
process-variable columns, a `run_id` column, and a `class_label` column
covering all 21 canonical classes across multiple runs per class. Tests
mutate copies of this fixture to construct the specific violation each
test is meant to reject.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from wp1a.data.schema import FEATURE_COLUMNS, N_EXPECTED_CLASSES

RUNS_PER_CLASS = 2
ROWS_PER_RUN = 10


def _make_run(run_id: str, class_label: int, n_rows: int, rng: np.random.Generator) -> pd.DataFrame:
    data = {col: rng.normal(loc=0.0, scale=1.0, size=n_rows) for col in FEATURE_COLUMNS}
    data["run_id"] = run_id
    data["class_label"] = class_label
    return pd.DataFrame(data)


@pytest.fixture
def rng() -> np.random.Generator:
    return np.random.default_rng(42)


@pytest.fixture
def valid_dataset(rng: np.random.Generator) -> pd.DataFrame:
    """A synthetic dataset fully compliant with the canonical schema:
    52 numeric feature columns, run_id, class_label in 0..20, all 21
    classes represented, each by RUNS_PER_CLASS distinct runs.
    """
    frames = []
    run_counter = 0
    for class_label in range(N_EXPECTED_CLASSES):
        for _rep in range(RUNS_PER_CLASS):
            run_counter += 1
            frames.append(
                _make_run(f"run_{run_counter:03d}", class_label, n_rows=ROWS_PER_RUN, rng=rng)
            )
    return pd.concat(frames, ignore_index=True)


@pytest.fixture
def run_class_map(valid_dataset: pd.DataFrame) -> dict[str, int]:
    """Mapping run_id -> class_label, one entry per distinct run in
    `valid_dataset`. Used by split/leakage tests that operate at the
    run level rather than the row level.
    """
    return (
        valid_dataset[["run_id", "class_label"]]
        .drop_duplicates()
        .set_index("run_id")["class_label"]
        .to_dict()
    )
