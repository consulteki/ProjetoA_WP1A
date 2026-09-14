"""Package EDA — SPEC-003 / Entrega A2."""

from wp1a.eda.analysis import PROTOCOL_DISCLAIMER, compute_eda_tables, load_canonical_for_eda
from wp1a.eda.report import run_eda

__all__ = [
    "PROTOCOL_DISCLAIMER",
    "compute_eda_tables",
    "load_canonical_for_eda",
    "run_eda",
]
