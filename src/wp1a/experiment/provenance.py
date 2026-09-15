"""Proveniência de experimentos: seed, git SHA, environment (EXP-R01 / REP-*)."""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import sklearn


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_provenance(repo_root: Path | None = None) -> dict[str, Any]:
    """Return git SHA and dirty flag; never raises on non-git trees."""
    root = repo_root or _repo_root()
    out: dict[str, Any] = {
        "git_sha": None,
        "git_sha_short": None,
        "git_dirty": None,
        "git_branch": None,
    }
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        dirty = (
            subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=root,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            != ""
        )
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=root,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except subprocess.CalledProcessError:
            branch = None
        out.update(
            {
                "git_sha": sha,
                "git_sha_short": sha[:12],
                "git_dirty": dirty,
                "git_branch": branch,
            }
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass
    return out


def environment_snapshot() -> dict[str, Any]:
    """Software / platform snapshot for experiment metadata."""
    env: dict[str, Any] = {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "scikit-learn": sklearn.__version__,
        "numpy": np.__version__,
        "executable": sys.executable,
    }
    try:
        import pandas as pd

        env["pandas"] = pd.__version__
    except ImportError:  # pragma: no cover
        env["pandas"] = None
    try:
        import xgboost

        env["xgboost"] = xgboost.__version__
    except ImportError:  # pragma: no cover
        env["xgboost"] = None
    try:
        import joblib

        env["joblib"] = joblib.__version__
    except ImportError:  # pragma: no cover
        env["joblib"] = None
    return env


def software_versions_for_config() -> dict[str, str]:
    """Compact version map for ExperimentConfig.software_versions."""
    snap = environment_snapshot()
    versions = {
        "python": str(snap["python"]),
        "scikit-learn": str(snap["scikit-learn"]),
        "numpy": str(snap["numpy"]),
    }
    if snap.get("xgboost"):
        versions["xgboost"] = str(snap["xgboost"])
    if snap.get("pandas"):
        versions["pandas"] = str(snap["pandas"])
    return versions
