"""Default hyperparameters for MOD-1..MOD-6 (starting points from configs/models.yaml).

These are scaffolding defaults for adapters — final frozen values are chosen
by ExperimentRunner selection (train/val only) and recorded per experiment
(ADR-005). Not a silent protocol change.
"""

from __future__ import annotations

from typing import Any

DEFAULT_HYPERPARAMETERS: dict[str, dict[str, Any]] = {
    "logistic_regression": {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
    },
    "decision_tree": {
        "max_depth": 10,
        "min_samples_leaf": 1,
        "criterion": "gini",
    },
    "random_forest": {
        "n_estimators": 200,
        "max_depth": 20,
        "min_samples_leaf": 1,
        "n_jobs": -1,
    },
    "gradient_boosting": {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 3,
    },
    "svm": {
        "C": 1.0,
        "kernel": "rbf",
        # Dual=False path not used for rbf; cache for speed on TEP-sized data.
        "cache_size": 500,
    },
    "xgboost": {
        "n_estimators": 200,
        "learning_rate": 0.1,
        "max_depth": 3,
        "reg_lambda": 1.0,
        "tree_method": "hist",
        "device": "cpu",
        "n_jobs": -1,
    },
}
