"""Expansão do espaço de busca de hiperparâmetros (treino/val apenas)."""

from __future__ import annotations

import itertools
from typing import Any


def expand_search_space(search_space: dict[str, list[Any]]) -> list[dict[str, Any]]:
    """Cartesian product of a per-model search_space mapping."""
    if not search_space:
        return [{}]
    keys = list(search_space.keys())
    values = [list(search_space[k]) for k in keys]
    for vals in values:
        if len(vals) == 0:
            raise ValueError("search_space values must be non-empty lists")
    return [dict(zip(keys, combo, strict=True)) for combo in itertools.product(*values)]
