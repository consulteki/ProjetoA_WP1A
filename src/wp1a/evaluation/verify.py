"""Recômputo e verificação das fórmulas SPEC-000 §9.2 (CA-06)."""

from __future__ import annotations

from typing import Any

import numpy as np


def recompute_f1_macro_from_per_class(per_class: list[dict[str, Any]]) -> float:
    """F1_macro = (1/C) * sum F1_c  (média aritmética simples)."""
    if not per_class:
        raise ValueError("per_class metrics list is empty")
    return float(np.mean([float(row["f1"]) for row in per_class]))


def recompute_balanced_accuracy_from_per_class(per_class: list[dict[str, Any]]) -> float:
    """BA = (1/C) * sum TP_c / (TP_c + FN_c)  (== média dos recalls)."""
    if not per_class:
        raise ValueError("per_class metrics list is empty")
    recalls: list[float] = []
    for row in per_class:
        tp = float(row["tp"])
        fn = float(row["fn"])
        denom = tp + fn
        recalls.append(tp / denom if denom > 0 else 0.0)
    return float(np.mean(recalls))


def verify_reported_aggregates(
    metrics: dict[str, Any],
    *,
    atol: float = 1e-12,
) -> dict[str, Any]:
    """Verify MET-05 / MET-02 against independent recomputation from MET-09."""
    per_class = metrics["MET-09_per_class"]
    f1_re = recompute_f1_macro_from_per_class(per_class)
    ba_re = recompute_balanced_accuracy_from_per_class(per_class)
    f1_ok = abs(float(metrics["MET-05_f1_macro"]) - f1_re) <= atol
    ba_ok = abs(float(metrics["MET-02_balanced_accuracy"]) - ba_re) <= atol
    return {
        "f1_macro_reported": float(metrics["MET-05_f1_macro"]),
        "f1_macro_recomputed": f1_re,
        "f1_macro_ok": f1_ok,
        "balanced_accuracy_reported": float(metrics["MET-02_balanced_accuracy"]),
        "balanced_accuracy_recomputed": ba_re,
        "balanced_accuracy_ok": ba_ok,
        "all_ok": f1_ok and ba_ok,
    }
