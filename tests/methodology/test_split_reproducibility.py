"""Tests that reject a non-reproducible train/val/test split.

Reference: docs/adr/ADR-003-reproducibility-requirements.md (REP-01, REP-02);
docs/specs/SPEC-000-master.md §15;
skill grouped-split (skills/grouped-split/SKILL.md).

`assert_split_reproducible` is a generic, black-box checker: it does not
assume any particular splitting algorithm. The two split functions used
here (`_seeded_split`, `_unseeded_split`) are local test doubles that
illustrate a compliant and a non-compliant implementation respectively —
they are not the pipeline's actual split algorithm (not yet implemented).
"""

from __future__ import annotations

import random

import pytest

from wp1a.errors import SplitReproducibilityError
from wp1a.splitting.reproducibility import assert_split_reproducible
from wp1a.splitting.run_leakage import check_run_disjoint


def _seeded_split(run_ids, seed, ratios=(0.6, 0.2, 0.2)):
    """Compliant test double: deterministic given `seed`, via a seeded RNG."""
    import numpy as np

    ids = sorted(run_ids)  # sort first so the only source of order is the seeded RNG
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(ids))
    shuffled = [ids[i] for i in order]

    n = len(shuffled)
    n_train = int(round(n * ratios[0]))
    n_val = int(round(n * ratios[1]))
    return {
        "train": shuffled[:n_train],
        "val": shuffled[n_train : n_train + n_val],
        "test": shuffled[n_train + n_val :],
    }


def _unseeded_split(run_ids, seed, ratios=(0.6, 0.2, 0.2)):
    """Non-compliant test double: ignores `seed` and relies on the global,
    unseeded `random` module, so consecutive calls disagree. Used only to
    prove that `assert_split_reproducible` correctly rejects it.
    """
    ids = list(run_ids)
    random.shuffle(ids)  # not seeded by the `seed` argument -> non-deterministic
    n = len(ids)
    n_train = int(round(n * ratios[0]))
    n_val = int(round(n * ratios[1]))
    return {
        "train": ids[:n_train],
        "val": ids[n_train : n_train + n_val],
        "test": ids[n_train + n_val :],
    }


def test_seeded_split_is_reproducible_for_same_seed(run_class_map):
    run_ids = list(run_class_map.keys())
    result = assert_split_reproducible(_seeded_split, run_ids, seed=123)
    covered = set(result["train"]) | set(result["val"]) | set(result["test"])
    assert covered == set(run_ids)


def test_seeded_split_result_is_run_disjoint(run_class_map):
    run_ids = list(run_class_map.keys())
    result = assert_split_reproducible(_seeded_split, run_ids, seed=123)
    check_run_disjoint(result["train"], result["val"], result["test"])  # must not raise


def test_seeded_split_may_differ_across_seeds(run_class_map):
    """Sanity check on the reference test double: different seeds are
    expected (not required) to produce different splits. This is not a
    methodological requirement of the checker itself.
    """
    run_ids = list(run_class_map.keys())
    result_a = _seeded_split(run_ids, seed=1)
    result_b = _seeded_split(run_ids, seed=2)
    assert result_a != result_b


def test_rejects_non_reproducible_split_function(run_class_map):
    run_ids = list(run_class_map.keys())
    with pytest.raises(SplitReproducibilityError, match="not reproducible"):
        assert_split_reproducible(_unseeded_split, run_ids, seed=123)


def test_rejects_split_function_with_inconsistent_partition_keys(run_class_map):
    run_ids = list(run_class_map.keys())
    call_count = {"n": 0}

    def _flaky_keys_split(run_ids, seed):
        call_count["n"] += 1
        base = _seeded_split(run_ids, seed=seed)
        if call_count["n"] == 1:
            return base
        # second call drops the "val" key entirely -> reproducibility must be rejected
        return {"train": base["train"], "test": base["test"]}

    with pytest.raises(SplitReproducibilityError, match="partition keys"):
        assert_split_reproducible(_flaky_keys_split, run_ids, seed=123)
