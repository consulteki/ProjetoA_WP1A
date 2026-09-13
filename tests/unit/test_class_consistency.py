"""Tests that reject class-label inconsistency.

Reference: docs/specs/SPEC-000-master.md DS-03 (21 classes: 1 normal + 20
faults); docs/project/requirements.md Seção 2;
skills data-audit / ml-evaluation.
"""

from __future__ import annotations

import pytest

from wp1a.data.class_consistency import (
    validate_class_consistency,
    validate_train_covers_eval_classes,
)
from wp1a.errors import ClassConsistencyError


def test_valid_dataset_has_21_consistent_classes(valid_dataset):
    validate_class_consistency(valid_dataset)  # must not raise


def test_rejects_missing_class(valid_dataset):
    broken = valid_dataset[valid_dataset["class_label"] != 7]
    with pytest.raises(ClassConsistencyError, match="missing"):
        validate_class_consistency(broken)


def test_rejects_unexpected_class_label(valid_dataset):
    broken = valid_dataset.copy()
    broken.loc[broken.index[0], "class_label"] = 21  # outside canonical 0..20
    with pytest.raises(ClassConsistencyError, match="unexpected"):
        validate_class_consistency(broken)


def test_rejects_wrong_total_number_of_classes(valid_dataset):
    broken = valid_dataset[valid_dataset["class_label"].isin(range(10))]
    with pytest.raises(ClassConsistencyError, match="expected 21 distinct classes"):
        validate_class_consistency(broken)


def test_rejects_dataframe_without_class_label_column(valid_dataset):
    broken = valid_dataset.drop(columns=["class_label"])
    with pytest.raises(ClassConsistencyError, match="class_label"):
        validate_class_consistency(broken)


def test_rejects_eval_class_absent_from_train(valid_dataset):
    """A class evaluated but never seen during training is a class
    inconsistency: the model had no opportunity to learn it.
    """
    train = valid_dataset[valid_dataset["class_label"] != 3]
    test = valid_dataset[valid_dataset["class_label"] == 3]
    with pytest.raises(ClassConsistencyError, match="absent from the training partition"):
        validate_train_covers_eval_classes(train, test, partition_name="test")


def test_allows_eval_classes_that_are_a_subset_of_train_classes(valid_dataset):
    train = valid_dataset
    test = valid_dataset[valid_dataset["class_label"].isin([0, 1, 2])]
    validate_train_covers_eval_classes(train, test, partition_name="test")  # must not raise


def test_allows_eval_classes_identical_to_train_classes(valid_dataset):
    validate_train_covers_eval_classes(valid_dataset, valid_dataset, partition_name="test")
