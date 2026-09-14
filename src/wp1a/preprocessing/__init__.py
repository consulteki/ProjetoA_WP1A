"""Pré-processamento WP1A (SPEC-005)."""

from wp1a.preprocessing.pipeline import apply_train_only_scaling, run_preprocessing
from wp1a.preprocessing.scaler import TrainOnlyStandardScaler, assert_params_match_train_only

__all__ = [
    "TrainOnlyStandardScaler",
    "apply_train_only_scaling",
    "assert_params_match_train_only",
    "run_preprocessing",
]
