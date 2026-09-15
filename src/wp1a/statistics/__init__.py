"""WP1A SPEC-008 — formal statistical comparison (Friedman / Wilcoxon)."""

from wp1a.statistics.pipeline import run_statistics_a8
from wp1a.statistics.tests import (
    friedman_test,
    per_run_metric_table,
    wilcoxon_pairwise,
)

__all__ = [
    "run_statistics_a8",
    "friedman_test",
    "per_run_metric_table",
    "wilcoxon_pairwise",
]
