"""Model layer — ClassifierProtocol and MOD-1..MOD-6 adapters.

Implementações concretas dos seis modelos (SPEC-006 / A4 scaffolding).
Todo classificador experimental DEVE respeitar ``ClassifierProtocol`` e
passar por ``ExperimentRunner`` (INV-03, MET-R03).
"""

from wp1a.models.adapters import (
    ADAPTER_FACTORY,
    ModelAdapter,
    build_adapter,
    build_all_adapters,
    make_decision_tree,
    make_gradient_boosting,
    make_logistic_regression,
    make_random_forest,
    make_svm,
    make_xgboost,
)
from wp1a.models.defaults import DEFAULT_HYPERPARAMETERS
from wp1a.models.protocol import (
    MODEL_IDS,
    MODEL_ID_TO_MOD,
    REQUIRED_MODEL_COUNT,
    ClassifierProtocol,
)

__all__ = [
    "ADAPTER_FACTORY",
    "ClassifierProtocol",
    "DEFAULT_HYPERPARAMETERS",
    "MODEL_IDS",
    "MODEL_ID_TO_MOD",
    "ModelAdapter",
    "REQUIRED_MODEL_COUNT",
    "build_adapter",
    "build_all_adapters",
    "make_decision_tree",
    "make_gradient_boosting",
    "make_logistic_regression",
    "make_random_forest",
    "make_svm",
    "make_xgboost",
]
