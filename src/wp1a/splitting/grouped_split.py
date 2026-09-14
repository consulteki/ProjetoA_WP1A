"""Divisão treino/validação/teste agrupada por ``run_id`` (SPEC-004).

Contrato compatível com ``assert_split_reproducible``:

    split_fn(run_ids, classes, seed=<int>) -> {"train": [...], "val": [...], "test": [...]}

Estratégia (dataset Braatz canônico com 2 runs/classe):
  1. Para cada classe, embaralhar os ``run_id`` com a semente e reservar
     exatamente um run para treino (garante as 21 classes no treino).
  2. Os runs restantes são embaralhados e repartidos entre validação e
     teste (~50/50). Com apenas 2 runs/classe, validação e teste NÃO
     podem cobrir as 21 classes simultaneamente — limitação documentada
     no manifesto A3.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import numpy as np

from wp1a.data.schema import N_EXPECTED_CLASSES
from wp1a.errors import CanonicalDatasetError
from wp1a.splitting.run_leakage import check_manifest_disjoint

SplitManifest = dict[str, list[str]]


def _as_run_class_map(
    run_ids: Iterable[Any],
    classes: Mapping[Any, Any] | Sequence[Any],
) -> dict[str, int]:
    run_list = [str(r) for r in run_ids]
    if isinstance(classes, Mapping):
        try:
            return {rid: int(classes[rid]) for rid in run_list}
        except KeyError:
            # Allow keys that were not stringified the same way.
            return {rid: int(classes[r]) for rid, r in zip(run_list, run_ids)}
    class_list = list(classes)
    if len(class_list) != len(run_list):
        raise ValueError(
            f"classes length ({len(class_list)}) must match run_ids ({len(run_list)})"
        )
    return {rid: int(c) for rid, c in zip(run_list, class_list)}


def grouped_split(
    run_ids: Iterable[Any],
    classes: Mapping[Any, Any] | Sequence[Any],
    *,
    seed: int,
) -> SplitManifest:
    """Particiona ``run_id`` em train/val/test de forma estratificada e reprodutível.

    Parameters
    ----------
    run_ids
        Identificadores de execução a particionar.
    classes
        Mapa ``run_id -> class_label`` **ou** sequência paralela a ``run_ids``.
    seed
        Semente aleatória explícita (configs/seeds.yaml → per_stage.split).
    """
    run_class_map = _as_run_class_map(run_ids, classes)
    if not run_class_map:
        raise ValueError("grouped_split requires at least one run_id")

    by_class: dict[int, list[str]] = defaultdict(list)
    for rid in sorted(run_class_map):
        by_class[run_class_map[rid]].append(rid)

    rng = np.random.default_rng(seed)
    train: list[str] = []
    leftovers: list[str] = []

    for class_label in sorted(by_class):
        runs = by_class[class_label]
        order = rng.permutation(len(runs))
        shuffled = [runs[i] for i in order]
        train.append(shuffled[0])
        leftovers.extend(shuffled[1:])

    val: list[str] = []
    test: list[str] = []
    if leftovers:
        order = rng.permutation(len(leftovers))
        leftovers = [leftovers[i] for i in order]
        mid = len(leftovers) // 2
        val = leftovers[:mid]
        test = leftovers[mid:]

    manifest: SplitManifest = {"train": train, "val": val, "test": test}

    # Integrity: full coverage, no duplicates within partition, disjoint.
    all_assigned = train + val + test
    if len(all_assigned) != len(set(all_assigned)):
        raise CanonicalDatasetError("grouped_split produced duplicate run_id assignments")
    if set(all_assigned) != set(run_class_map):
        missing = sorted(set(run_class_map) - set(all_assigned))
        extra = sorted(set(all_assigned) - set(run_class_map))
        raise CanonicalDatasetError(
            f"grouped_split coverage error: missing={missing} extra={extra}"
        )
    check_manifest_disjoint(manifest)
    return manifest


def class_coverage(manifest: SplitManifest, run_class_map: Mapping[str, int]) -> dict[str, Any]:
    """Report which classes appear in each partition (and gaps)."""
    coverage: dict[str, Any] = {}
    for partition, key in (("train", "train"), ("validation", "val"), ("test", "test")):
        runs = manifest[key]
        classes = sorted({int(run_class_map[r]) for r in runs})
        coverage[partition] = {
            "n_runs": len(runs),
            "n_classes": len(classes),
            "classes": classes,
            "missing_classes": sorted(set(range(N_EXPECTED_CLASSES)) - set(classes)),
        }
    return coverage
