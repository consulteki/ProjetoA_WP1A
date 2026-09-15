"""Avaliação — métricas MET-01..MET-12 e Entrega A5 (SPEC-007)."""

from wp1a.evaluation.metrics import CANONICAL_LABELS, compute_classification_metrics
from wp1a.evaluation.pipeline import run_evaluation_a5
from wp1a.evaluation.verify import (
    recompute_balanced_accuracy_from_per_class,
    recompute_f1_macro_from_per_class,
    verify_reported_aggregates,
)

__all__ = [
    "CANONICAL_LABELS",
    "compute_classification_metrics",
    "recompute_balanced_accuracy_from_per_class",
    "recompute_f1_macro_from_per_class",
    "run_evaluation_a5",
    "verify_reported_aggregates",
]
