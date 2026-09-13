"""Generic reproducibility checker for data-split functions.

Reference: docs/adr/ADR-003-reproducibility-requirements.md;
docs/specs/SPEC-000-master.md §15 (REP-01, REP-02).

This module does not implement the pipeline's actual split algorithm
(skill `grouped-split`, ADR-001). It provides a black-box checker that can
wrap *any* callable claiming to produce a deterministic, seeded split, and
rejects it if it fails to reproduce identical output across two calls
with the same seed and inputs.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from wp1a.errors import SplitReproducibilityError

# The contract every split function under test must satisfy:
#   split_fn(run_ids, classes, seed=<int>, **kwargs) -> {"train": [...], "val": [...], "test": [...]}
SplitManifest = Mapping[str, list]
SplitFn = Callable[..., SplitManifest]


def assert_split_reproducible(
    split_fn: SplitFn,
    *args: Any,
    seed: int,
    **kwargs: Any,
) -> SplitManifest:
    """Call ``split_fn`` twice with identical arguments (including
    ``seed``) and reject it if the two calls disagree.

    Parameters
    ----------
    split_fn
        A callable following the ``SplitFn`` contract above.
    *args, **kwargs
        Forwarded verbatim to both calls of ``split_fn``; ``seed`` is
        always passed as a keyword argument to make the reproducibility
        contract explicit at the call site.

    Returns
    -------
    SplitManifest
        The (agreeing) manifest produced by the first call, for reuse by
        the caller.

    Raises
    ------
    SplitReproducibilityError
        If any partition differs between the two calls, or if the set of
        partition keys differs.
    """
    result_a = split_fn(*args, seed=seed, **kwargs)
    result_b = split_fn(*args, seed=seed, **kwargs)

    if set(result_a.keys()) != set(result_b.keys()):
        raise SplitReproducibilityError(
            f"split_fn is not reproducible for seed={seed}: partition keys "
            f"differ between two calls ({sorted(result_a.keys())} vs "
            f"{sorted(result_b.keys())})"
        )

    disagreements = {
        partition: (sorted(result_a[partition]), sorted(result_b[partition]))
        for partition in result_a
        if sorted(result_a[partition]) != sorted(result_b[partition])
    }
    if disagreements:
        raise SplitReproducibilityError(
            f"split_fn is not reproducible for seed={seed}: partition(s) "
            f"differ between two calls with the same seed: {disagreements}"
        )

    return result_a
