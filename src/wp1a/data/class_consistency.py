"""Class-label consistency checks for the TEP dataset.

Reference: docs/specs/SPEC-000-master.md DS-03 (21 classes: 1 normal +
20 faults); docs/project/requirements.md Seção 2.
"""

from __future__ import annotations

import pandas as pd

from wp1a.errors import ClassConsistencyError
from wp1a.data.schema import CLASS_LABEL_COLUMN, N_EXPECTED_CLASSES, VALID_CLASS_LABELS


def validate_class_consistency(
    df: pd.DataFrame,
    *,
    expected_n_classes: int = N_EXPECTED_CLASSES,
    expected_labels: frozenset[int] = VALID_CLASS_LABELS,
) -> None:
    """Validate that ``df`` contains exactly the canonical set of classes.

    Raises
    ------
    ClassConsistencyError
        If any class label falls outside the canonical set, or if the
        dataframe does not contain all ``expected_n_classes`` classes.
    """
    if CLASS_LABEL_COLUMN not in df.columns:
        raise ClassConsistencyError(f"dataframe has no '{CLASS_LABEL_COLUMN}' column")

    labels = set(df[CLASS_LABEL_COLUMN].unique().tolist())
    unexpected = sorted(labels - expected_labels)
    missing = sorted(expected_labels - labels)

    problems: list[str] = []
    if unexpected:
        problems.append(f"unexpected class labels present: {unexpected}")
    if len(labels) != expected_n_classes:
        problems.append(
            f"expected {expected_n_classes} distinct classes, found {len(labels)} "
            f"(missing: {missing if missing else 'none'})"
        )
    if problems:
        raise ClassConsistencyError("; ".join(problems))


def validate_train_covers_eval_classes(
    train_df: pd.DataFrame,
    eval_df: pd.DataFrame,
    *,
    partition_name: str = "eval",
) -> None:
    """Validate that every class present in ``eval_df`` was also present in
    ``train_df``.

    A classifier cannot be legitimately evaluated on a class it never had
    the opportunity to learn during training; a class appearing only in
    validation/test is a class-inconsistency failure distinct from, but as
    serious as, a wrong global class count.

    Raises
    ------
    ClassConsistencyError
        If ``eval_df`` contains one or more classes absent from ``train_df``.
    """
    train_labels = set(train_df[CLASS_LABEL_COLUMN].unique().tolist())
    eval_labels = set(eval_df[CLASS_LABEL_COLUMN].unique().tolist())
    unseen = sorted(eval_labels - train_labels)
    if unseen:
        raise ClassConsistencyError(
            f"partition '{partition_name}' contains class label(s) {unseen} "
            f"that are absent from the training partition"
        )
