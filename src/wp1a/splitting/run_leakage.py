"""Run-level (execution-level) leakage checks.

Reference: docs/adr/ADR-001-run-as-experimental-grouping-unit.md;
docs/specs/SPEC-000-master.md §6, INV-01/INV-02;
AGENTS.md LEAK-R01, LEAK-R04.

The unit of division of the TEP dataset is the *execution* (`run_id`),
never the individual sample/row. This module rejects any partitioning in
which a run_id appears in more than one of train/validation/test.
"""

from __future__ import annotations

from collections.abc import Iterable

from wp1a.errors import RunLeakageError


def check_run_disjoint(
    train_runs: Iterable,
    val_runs: Iterable,
    test_runs: Iterable,
) -> None:
    """Validate that the three partitions of run_id are pairwise disjoint.

    Parameters
    ----------
    train_runs, val_runs, test_runs
        Any iterable of run identifiers (list, set, pandas Series, ...).
        An empty iterable is valid (e.g. when checking only two of the
        three partitions).

    Raises
    ------
    RunLeakageError
        Listing every pair of partitions that share at least one run_id,
        and the offending run_ids, so the violation is fully diagnosable
        from the exception message alone.
    """
    train_set, val_set, test_set = set(train_runs), set(val_runs), set(test_runs)

    overlaps = {
        "train/val": sorted(train_set & val_set),
        "train/test": sorted(train_set & test_set),
        "val/test": sorted(val_set & test_set),
    }
    offending = {pair: runs for pair, runs in overlaps.items() if runs}

    if offending:
        raise RunLeakageError(
            "run_id leakage detected: the same execution(s) appear in more "
            f"than one partition: {offending}"
        )


def check_manifest_disjoint(manifest: dict[str, Iterable]) -> None:
    """Convenience wrapper over :func:`check_run_disjoint` for a split
    manifest shaped like ``{"train": [...], "val": [...], "test": [...]}``
    (the structure of Entrega A3).

    Raises
    ------
    RunLeakageError
        Same as :func:`check_run_disjoint`.
    ValueError
        If the manifest is missing one of the three required partitions.
    """
    required_keys = {"train", "val", "test"}
    missing_keys = required_keys - set(manifest.keys())
    if missing_keys:
        raise ValueError(f"split manifest is missing partition(s): {sorted(missing_keys)}")

    check_run_disjoint(manifest["train"], manifest["val"], manifest["test"])
