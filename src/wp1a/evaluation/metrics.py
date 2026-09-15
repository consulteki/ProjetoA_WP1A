"""Métricas obrigatórias MET-01..MET-09 (SPEC-000 §9).

F1 macro e BA seguem as fórmulas explícitas da SPEC (média simples sobre
C classes canônicas), não atalhos implícitos de bibliotecas.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
)

from wp1a.data.schema import N_EXPECTED_CLASSES, VALID_CLASS_LABELS

CANONICAL_LABELS: tuple[int, ...] = tuple(sorted(VALID_CLASS_LABELS))
assert len(CANONICAL_LABELS) == N_EXPECTED_CLASSES


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    labels: tuple[int, ...] = CANONICAL_LABELS,
) -> dict[str, Any]:
    """Compute global + per-class metrics on a single test prediction pass."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    label_list = list(labels)
    C = len(label_list)

    cm = confusion_matrix(y_true, y_pred, labels=label_list)
    per_class: list[dict[str, Any]] = []
    f1_list: list[float] = []
    recall_list: list[float] = []
    precision_list: list[float] = []

    for i, cls in enumerate(label_list):
        tp = float(cm[i, i])
        fp = float(cm[:, i].sum() - tp)
        fn = float(cm[i, :].sum() - tp)
        support = float(cm[i, :].sum())
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            (2.0 * precision * recall / (precision + recall))
            if (precision + recall) > 0
            else 0.0
        )
        per_class.append(
            {
                "class_label": int(cls),
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": int(support),
                "tp": int(tp),
                "fp": int(fp),
                "fn": int(fn),
            }
        )
        f1_list.append(f1)
        recall_list.append(recall)
        precision_list.append(precision)

    # SPEC-000 §9.2 — simple means over C canonical classes.
    f1_macro = float(np.mean(f1_list))
    balanced_accuracy = float(np.mean(recall_list))
    precision_macro = float(np.mean(precision_list))
    recall_macro = float(np.mean(recall_list))

    # Cross-check against sklearn with labels fixed to the canonical set.
    sk_f1_macro = float(
        f1_score(y_true, y_pred, labels=label_list, average="macro", zero_division=0)
    )
    sk_ba = float(
        np.mean(
            [
                (
                    cm[i, i] / cm[i, :].sum()
                    if cm[i, :].sum() > 0
                    else 0.0
                )
                for i in range(C)
            ]
        )
    )

    return {
        "MET-01_accuracy": float(accuracy_score(y_true, y_pred)),
        "MET-02_balanced_accuracy": balanced_accuracy,
        "MET-03_precision_macro": precision_macro,
        "MET-04_recall_macro": recall_macro,
        "MET-05_f1_macro": f1_macro,
        "MET-06_f1_weighted": float(
            f1_score(y_true, y_pred, labels=label_list, average="weighted", zero_division=0)
        ),
        "MET-07_mcc": float(matthews_corrcoef(y_true, y_pred)),
        "MET-08_confusion_matrix": cm.astype(int).tolist(),
        "MET-09_per_class": per_class,
        "n_classes_canonical": C,
        "labels": label_list,
        "_checks": {
            "f1_macro_matches_sklearn": abs(f1_macro - sk_f1_macro) < 1e-12,
            "ba_recomputed": abs(balanced_accuracy - sk_ba) < 1e-12,
            "sklearn_f1_macro": sk_f1_macro,
            "sklearn_precision_macro": float(
                precision_score(
                    y_true, y_pred, labels=label_list, average="macro", zero_division=0
                )
            ),
            "sklearn_recall_macro": float(
                recall_score(
                    y_true, y_pred, labels=label_list, average="macro", zero_division=0
                )
            ),
        },
    }
