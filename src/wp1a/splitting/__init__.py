"""Splitting package — SPEC-004 guards + grouped split."""

from wp1a.splitting.grouped_split import grouped_split
from wp1a.splitting.reproducibility import assert_split_reproducible
from wp1a.splitting.run_leakage import check_manifest_disjoint, check_run_disjoint

__all__ = [
    "assert_split_reproducible",
    "check_manifest_disjoint",
    "check_run_disjoint",
    "grouped_split",
]
