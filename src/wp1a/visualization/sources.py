"""Guarda: artefatos A6 só podem ler caminhos sob ``results/``.

Nunca ``data/raw`` (nem interim/processed como fonte de figuras A6).
"""

from __future__ import annotations

from pathlib import Path


class ResultsOnlyError(ValueError):
    """Raised when a figure/table source is outside ``results/``."""


FORBIDDEN_SUBSTRINGS = (
    "/data/raw/",
    "/data/interim/",
    "\\data\\raw\\",
    "\\data\\interim\\",
)


def assert_under_results(path: Path, *, results_root: Path) -> Path:
    """Resolve ``path`` and ensure it lives under ``results_root``."""
    results_root = Path(results_root).resolve()
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(results_root)
    except ValueError as exc:
        raise ResultsOnlyError(
            f"A6 sources must be under {results_root}; refused: {resolved}"
        ) from exc
    text = str(resolved)
    for bad in FORBIDDEN_SUBSTRINGS:
        if bad in text.replace("//", "/"):
            raise ResultsOnlyError(
                f"A6 must never read data/raw (or interim); refused: {resolved}"
            )
    if not resolved.is_file() and not resolved.is_dir():
        # Allow missing check by caller; still path-safe.
        pass
    return resolved


def require_file(path: Path, *, results_root: Path) -> Path:
    resolved = assert_under_results(path, results_root=results_root)
    if not resolved.is_file():
        raise FileNotFoundError(f"required results artifact missing: {resolved}")
    return resolved
