"""Treinamento A4 (SPEC-006) — seleção + fit via ExperimentRunner."""

from wp1a.training.pipeline import run_training_benchmark
from wp1a.training.search import expand_search_space

__all__ = ["expand_search_space", "run_training_benchmark"]
