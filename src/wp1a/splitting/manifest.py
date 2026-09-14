"""Construção e persistência da Entrega A3 (manifesto de divisão)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from wp1a.data.canonical import DATASET_VERSION, load_canonical_dataframe, load_canonical_registry
from wp1a.data.schema import CLASS_LABEL_COLUMN, RUN_ID_COLUMN
from wp1a.errors import CanonicalDatasetError, RunLeakageError
from wp1a.splitting.grouped_split import class_coverage, grouped_split
from wp1a.splitting.reproducibility import assert_split_reproducible
from wp1a.splitting.run_leakage import check_manifest_disjoint, check_run_disjoint

MANIFEST_VERSION = "split_manifest_v1"
MANIFEST_FILENAME = f"{MANIFEST_VERSION}.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_split_seed(seeds_path: Path | None = None) -> int:
    path = seeds_path or (_repo_root() / "configs" / "seeds.yaml")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    seed = payload.get("per_stage", {}).get("split", payload.get("global_seed"))
    if seed is None:
        raise CanonicalDatasetError(f"split seed not found in {path}")
    return int(seed)


def build_run_class_map(df: pd.DataFrame) -> dict[str, int]:
    pairs = (
        df[[RUN_ID_COLUMN, CLASS_LABEL_COLUMN]]
        .drop_duplicates()
        .sort_values(RUN_ID_COLUMN)
    )
    # Detect ambiguous run→class mappings.
    nunique = pairs.groupby(RUN_ID_COLUMN)[CLASS_LABEL_COLUMN].nunique()
    bad = nunique[nunique != 1]
    if len(bad) > 0:
        raise CanonicalDatasetError(
            f"run_id(s) map to multiple classes: {bad.index.tolist()}"
        )
    return {str(r): int(c) for r, c in pairs.itertuples(index=False)}


def build_split_manifest(
    *,
    processed_dir: Path,
    seed: int | None = None,
    seeds_path: Path | None = None,
) -> dict[str, Any]:
    """Create the A3 payload (no model training)."""
    processed_dir = Path(processed_dir)
    registry = load_canonical_registry(processed_dir)
    if registry.get("dataset_version") != DATASET_VERSION:
        raise CanonicalDatasetError(
            f"split requires dataset_version={DATASET_VERSION!r}, "
            f"got {registry.get('dataset_version')!r}"
        )
    df = load_canonical_dataframe(processed_dir)
    run_class_map = build_run_class_map(df)
    seed = load_split_seed(seeds_path) if seed is None else int(seed)

    run_ids = sorted(run_class_map.keys())
    classes = [run_class_map[r] for r in run_ids]

    # Reproducibility guard (two identical calls) + leakage guard.
    partitions = assert_split_reproducible(
        grouped_split, run_ids, classes, seed=seed
    )
    check_manifest_disjoint(partitions)
    check_run_disjoint(partitions["train"], partitions["val"], partitions["test"])

    coverage = class_coverage(partitions, run_class_map)
    limitations: list[str] = []
    for part in ("validation", "test"):
        missing = coverage[part]["missing_classes"]
        if missing:
            limitations.append(
                f"{part} lacks class_label(s) {missing} because the canonical "
                f"dataset has only two runs per class; one run/class is reserved "
                f"for train, so val/test cannot simultaneously cover all "
                f"{len(run_ids) // 2} classes."
            )

    payload = {
        "manifest_version": MANIFEST_VERSION,
        "spec": "SPEC-004",
        "delivery": "A3",
        "created_at": _utc_now(),
        "seed": seed,
        "seed_source": "configs/seeds.yaml#per_stage.split",
        "dataset_version": registry.get("dataset_version"),
        "canonical_registry_path": "data/processed/canonical_dataset_registry.json",
        "strategy": {
            "name": "stratified_one_train_per_class_remaining_split_val_test",
            "unit": "run_id",
            "description": (
                "For each class, shuffle runs with the seed and assign one run "
                "to train; shuffle remaining runs and split ~50/50 into "
                "validation and test. Ignores Braatz provenance labels "
                "(braatz_train/braatz_test) as WP1A partition names."
            ),
        },
        # Primary outputs requested for SPEC-004:
        "train_runs": list(partitions["train"]),
        "validation_runs": list(partitions["val"]),
        "test_runs": list(partitions["test"]),
        # Guard-compatible aliases (check_manifest_disjoint):
        "partitions": {
            "train": list(partitions["train"]),
            "val": list(partitions["val"]),
            "test": list(partitions["test"]),
        },
        "run_class_map": run_class_map,
        "class_coverage": coverage,
        "limitations": limitations,
        "leakage_check": {
            "function": "check_run_disjoint / check_manifest_disjoint",
            "status": "passed",
        },
        "reproducibility_check": {
            "function": "assert_split_reproducible(grouped_split, ...)",
            "status": "passed",
            "seed": seed,
        },
    }
    return payload


def write_split_artifacts(payload: dict[str, Any], processed_dir: Path) -> dict[str, Path]:
    """Persist A3 JSON + CSV lists for train/validation/test runs."""
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = processed_dir / MANIFEST_FILENAME
    manifest_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    written = {"manifest": manifest_path}
    for name, key in (
        ("train_runs", "train_runs"),
        ("validation_runs", "validation_runs"),
        ("test_runs", "test_runs"),
    ):
        path = processed_dir / f"{name}.csv"
        pd.DataFrame({"run_id": payload[key]}).to_csv(path, index=False)
        written[name] = path

    return written


def load_split_manifest(processed_dir: Path) -> dict[str, Any]:
    path = Path(processed_dir) / MANIFEST_FILENAME
    if not path.is_file():
        raise FileNotFoundError(f"split manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_manifest_leakage_or_raise(payload: dict[str, Any]) -> None:
    """Hard stop if the generated A3 lists are not pairwise disjoint."""
    try:
        check_run_disjoint(
            payload["train_runs"],
            payload["validation_runs"],
            payload["test_runs"],
        )
        check_manifest_disjoint(payload["partitions"])
    except RunLeakageError:
        raise


def run_methodology_suite_or_abort(*, repo_root: Path | None = None) -> int:
    """Execute ``tests/methodology/``; abort (non-zero) on any failure."""
    root = repo_root or _repo_root()
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(root / "tests" / "methodology"),
        "-q",
    ]
    print(
        "Running methodology suite (leakage/isolation/reproducibility/metadata)...",
        flush=True,
    )
    completed = subprocess.run(cmd, cwd=root, check=False)
    if completed.returncode != 0:
        print(
            "ABORT: methodology suite failed — possible leakage or related "
            "invariant violation. Split artifacts were written but must not "
            "be used until tests pass.",
            file=sys.stderr,
            flush=True,
        )
    return int(completed.returncode)
