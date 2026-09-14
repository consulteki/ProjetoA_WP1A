"""Carregamento e inventário de arquivos brutos TEP (Braatz .dat).

Este módulo NÃO aplica transformações de modelagem: apenas lê os arquivos
como estão em ``data/raw/`` e extrai metadados necessários à auditoria
(SPEC-001). Decisões de canonicidade ficam na SPEC-002.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Convenção Braatz: d00.dat / d00_te.dat … d21.dat / d21_te.dat
_DAT_PATTERN = re.compile(r"^d(?P<fault>\d{2})(?P<te>_te)?\.dat$", re.IGNORECASE)

# Contagens documentadas na fonte Braatz (Russell/Chiang/Braatz).
EXPECTED_N_FEATURES = 52
EXPECTED_TRAIN_ROWS = 480
EXPECTED_TEST_ROWS = 960


@dataclass(frozen=True)
class RawFileRecord:
    """Metadados estruturais de um arquivo bruto auditado."""

    path: Path
    name: str
    format: str
    size_bytes: int
    sha256: str
    n_rows: int
    n_cols: int
    fault_id: int
    source_split: str  # "braatz_train" | "braatz_test" (proveniência, NÃO split WP1A)
    run_id: str
    orientation: str  # "samples_x_features" | "features_x_samples" | "unknown"
    expected_shape: tuple[int, int]
    shape_matches_expected: bool


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def parse_braatz_filename(name: str) -> tuple[int, str, str]:
    """Parse ``dXX.dat`` / ``dXX_te.dat`` → (fault_id, source_split, run_id)."""
    match = _DAT_PATTERN.match(name)
    if not match:
        raise ValueError(f"filename does not match Braatz convention: {name}")
    fault_id = int(match.group("fault"))
    is_te = match.group("te") is not None
    source_split = "braatz_test" if is_te else "braatz_train"
    run_id = f"braatz_{'te' if is_te else 'tr'}_fault{fault_id:02d}"
    return fault_id, source_split, run_id


def load_raw_matrix(path: Path) -> np.ndarray:
    """Load a space-delimited Braatz ``.dat`` file as a float matrix."""
    return np.loadtxt(path, dtype=np.float64)


def infer_orientation(shape: tuple[int, int], source_split: str) -> tuple[str, tuple[int, int], bool]:
    """Infer matrix orientation relative to the documented Braatz layout.

    Returns ``(orientation, expected_shape, matches_expected)``.
    """
    expected_rows = EXPECTED_TEST_ROWS if source_split == "braatz_test" else EXPECTED_TRAIN_ROWS
    expected = (expected_rows, EXPECTED_N_FEATURES)
    n_rows, n_cols = shape

    if (n_rows, n_cols) == expected:
        return "samples_x_features", expected, True
    if (n_cols, n_rows) == expected:
        return "features_x_samples", expected, False
    # d00.dat histórico: frequentemente 52 x N (transposto) com N ≠ 480.
    if n_rows == EXPECTED_N_FEATURES and n_cols != EXPECTED_N_FEATURES:
        return "features_x_samples", expected, False
    if n_cols == EXPECTED_N_FEATURES and n_rows != expected_rows:
        return "samples_x_features", expected, False
    return "unknown", expected, False


def list_raw_dat_files(raw_dir: Path) -> list[Path]:
    if not raw_dir.is_dir():
        raise FileNotFoundError(f"raw data directory not found: {raw_dir}")
    return sorted(p for p in raw_dir.iterdir() if p.is_file() and p.suffix.lower() == ".dat")


def inventory_raw_file(path: Path) -> tuple[RawFileRecord, np.ndarray]:
    """Build an inventory record and return the loaded matrix (as-is)."""
    matrix = load_raw_matrix(path)
    if matrix.ndim != 2:
        raise ValueError(f"{path.name}: expected 2-D matrix, got shape {matrix.shape}")
    fault_id, source_split, run_id = parse_braatz_filename(path.name)
    orientation, expected_shape, matches = infer_orientation(matrix.shape, source_split)
    record = RawFileRecord(
        path=path.resolve(),
        name=path.name,
        format="text/plain; space-delimited .dat (Braatz TEP)",
        size_bytes=path.stat().st_size,
        sha256=sha256_file(path),
        n_rows=int(matrix.shape[0]),
        n_cols=int(matrix.shape[1]),
        fault_id=fault_id,
        source_split=source_split,
        run_id=run_id,
        orientation=orientation,
        expected_shape=expected_shape,
        shape_matches_expected=matches,
    )
    return record, matrix


def as_samples_by_features(matrix: np.ndarray, orientation: str) -> np.ndarray:
    """Return a view/copy oriented as (n_samples, n_features) when possible.

    Used only for integrity checks that require column-wise statistics; the
    raw file on disk is never rewritten by the audit.
    """
    if orientation == "samples_x_features":
        return matrix
    if orientation == "features_x_samples":
        return matrix.T
    # Fallback: prefer the axis that looks like 52 features.
    if matrix.shape[1] == EXPECTED_N_FEATURES:
        return matrix
    if matrix.shape[0] == EXPECTED_N_FEATURES:
        return matrix.T
    raise ValueError(f"cannot orient matrix of shape {matrix.shape} as samples×features")
