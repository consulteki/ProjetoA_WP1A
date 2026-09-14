"""Visualização A6 — figuras/tabelas a partir de ``results/`` apenas."""

from wp1a.visualization.pipeline import run_a6
from wp1a.visualization.sources import ResultsOnlyError, assert_under_results

__all__ = ["ResultsOnlyError", "assert_under_results", "run_a6"]
