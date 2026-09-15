"""Identificação de classes de falha sistematicamente confundidas (insumo QP3)."""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from wp1a.evaluation.metrics import CANONICAL_LABELS


def confused_pairs_from_cm(
    cm: list[list[int]] | np.ndarray,
    *,
    labels: tuple[int, ...] = CANONICAL_LABELS,
    top_k: int = 15,
) -> list[dict[str, Any]]:
    """Rank off-diagonal confusion counts (true_c → pred_k), excluding normal-only noise optionally."""
    mat = np.asarray(cm, dtype=int)
    pairs: list[dict[str, Any]] = []
    for i, true_c in enumerate(labels):
        for j, pred_c in enumerate(labels):
            if i == j:
                continue
            count = int(mat[i, j])
            if count <= 0:
                continue
            pairs.append(
                {
                    "true_class": int(true_c),
                    "pred_class": int(pred_c),
                    "count": count,
                    "true_support": int(mat[i, :].sum()),
                }
            )
    pairs.sort(key=lambda r: (-r["count"], r["true_class"], r["pred_class"]))
    return pairs[:top_k]


def lowest_f1_classes(
    per_class: list[dict[str, Any]],
    *,
    top_k: int = 5,
    exclude_normal: bool = True,
) -> list[dict[str, Any]]:
    rows = [
        r
        for r in per_class
        if not (exclude_normal and int(r["class_label"]) == 0)
    ]
    rows = sorted(rows, key=lambda r: (float(r["f1"]), int(r["class_label"])))
    return [
        {
            "class_label": int(r["class_label"]),
            "f1": float(r["f1"]),
            "precision": float(r["precision"]),
            "recall": float(r["recall"]),
            "support": int(r["support"]),
        }
        for r in rows[:top_k]
    ]


def systematically_confused_classes(
    models_payload: list[dict[str, Any]],
    *,
    worst_k: int = 5,
    pair_top_k: int = 10,
) -> dict[str, Any]:
    """Aggregate across models: faults that repeatedly have low F1 / high off-diag mass."""
    worst_counter: Counter[int] = Counter()
    pair_counter: Counter[tuple[int, int]] = Counter()
    per_model_worst: dict[str, list[dict[str, Any]]] = {}
    per_model_pairs: dict[str, list[dict[str, Any]]] = {}

    for item in models_payload:
        model_id = str(item["model_id"])
        metrics = item["metrics"]
        worst = lowest_f1_classes(metrics["MET-09_per_class"], top_k=worst_k)
        pairs = confused_pairs_from_cm(
            metrics["MET-08_confusion_matrix"], top_k=pair_top_k
        )
        per_model_worst[model_id] = worst
        per_model_pairs[model_id] = pairs
        for row in worst:
            worst_counter[int(row["class_label"])] += 1
        for row in pairs:
            pair_counter[(int(row["true_class"]), int(row["pred_class"]))] += row["count"]

    systematic_low_f1 = [
        {"class_label": c, "n_models_in_worst_k": n}
        for c, n in worst_counter.most_common()
        if n >= 2  # appears among worst for ≥2 models
    ]
    systematic_pairs = [
        {
            "true_class": a,
            "pred_class": b,
            "total_count_across_models": tot,
        }
        for (a, b), tot in pair_counter.most_common(pair_top_k)
    ]

    return {
        "disclaimer": (
            "Preliminary QP3 input only — lists systematically difficult/confused "
            "fault classes; does NOT declare a best model (INV-06)."
        ),
        "worst_k": worst_k,
        "per_model_lowest_f1_faults": per_model_worst,
        "per_model_top_confused_pairs": per_model_pairs,
        "systematic_low_f1_faults": systematic_low_f1,
        "systematic_confused_pairs": systematic_pairs,
    }
