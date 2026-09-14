"""Construção e registro do dataset canônico TEP (SPEC-002).

Lê exclusivamente ``data/raw/`` (imutável), aplica decisões de tratamento
globais documentadas a partir da Entrega A1, valida o schema canônico e
publica o registro em ``data/processed/``.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from wp1a.data.class_consistency import validate_class_consistency
from wp1a.data.raw_loader import (
    as_samples_by_features,
    inventory_raw_file,
    list_raw_dat_files,
    sha256_file,
)
from wp1a.data.schema import (
    CANONICAL_REQUIRED_COLUMNS,
    CLASS_LABEL_COLUMN,
    FEATURE_COLUMNS,
    N_EXPECTED_CLASSES,
    RUN_ID_COLUMN,
    SAMPLE_INDEX_COLUMN,
    SOURCE_FILE_COLUMN,
    SOURCE_SPLIT_COLUMN,
    validate_canonical_schema,
)
from wp1a.errors import CanonicalDatasetError

DATASET_VERSION = "tep-canonical-v1"
CANONICAL_TABLE_NAME = f"{DATASET_VERSION}.csv.gz"
REGISTRY_NAME = "canonical_dataset_registry.json"

# Decisões de tratamento global (pós-A1, pré-split). Ver ADR-004-amendment-001.
EXCLUDED_FAULT_IDS: frozenset[int] = frozenset({21})
TREATMENTS: tuple[dict[str, str], ...] = (
    {
        "id": "exclude_fault_21",
        "decision": "exclude",
        "a1_item": "4",
        "summary": (
            "Excluir d21.dat e d21_te.dat (classe 21) para alinhar ao DS-03 "
            "(21 classes = rótulos 0..20)."
        ),
    },
    {
        "id": "orient_to_samples_x_features",
        "decision": "orient_in_memory_only",
        "a1_item": "2",
        "summary": (
            "Orientar matrizes features×samples (notadamente d00.dat 52×500) para "
            "samples×features apenas na representação canônica; data/raw/ permanece "
            "inalterado. Conservar as 500 amostras de d00.dat (não truncar para 480)."
        ),
    },
    {
        "id": "retain_cross_file_duplicate_rows",
        "decision": "retain",
        "a1_item": "7",
        "summary": (
            "Manter linhas numericamente idênticas compartilhadas entre arquivos "
            "*_te.dat (trecho pré-falha em regime normal). Removê-las alteraria o "
            "comprimento e a estrutura temporal das execuções."
        ),
    },
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_a1_metadata(metadata_path: Path) -> dict[str, Any]:
    if not metadata_path.is_file():
        raise CanonicalDatasetError(
            f"A1 metadata not found at {metadata_path}; run SPEC-001 (make audit) first"
        )
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def assert_raw_immutable(raw_dir: Path, expected_sha256_by_file: dict[str, str]) -> None:
    """Verify that every audited raw file still matches its A1 checksum."""
    raw_dir = Path(raw_dir)
    errors: list[str] = []
    for name, expected in sorted(expected_sha256_by_file.items()):
        path = raw_dir / name
        if not path.is_file():
            errors.append(f"missing raw file referenced by A1: {name}")
            continue
        actual = sha256_file(path)
        if actual != expected:
            errors.append(
                f"raw file mutated since A1 (must remain immutable): {name} "
                f"(expected sha256={expected}, got={actual})"
            )
    if errors:
        raise CanonicalDatasetError("; ".join(errors))


def assert_run_class_bijection(df: pd.DataFrame) -> None:
    """Each run_id must map to exactly one class_label (DS-06 consistency)."""
    grouped = df.groupby(RUN_ID_COLUMN)[CLASS_LABEL_COLUMN].nunique()
    bad = grouped[grouped != 1]
    if len(bad) > 0:
        raise CanonicalDatasetError(
            f"run_id(s) map to multiple class labels: {bad.index.tolist()}"
        )


def _matrix_to_frame(
    matrix: np.ndarray,
    *,
    run_id: str,
    class_label: int,
    source_file: str,
    source_split: str,
) -> pd.DataFrame:
    if matrix.ndim != 2 or matrix.shape[1] != len(FEATURE_COLUMNS):
        raise CanonicalDatasetError(
            f"{source_file}: expected (*, {len(FEATURE_COLUMNS)}) after orientation, "
            f"got {matrix.shape}"
        )
    data = {col: matrix[:, i] for i, col in enumerate(FEATURE_COLUMNS)}
    data[RUN_ID_COLUMN] = run_id
    data[CLASS_LABEL_COLUMN] = np.int64(class_label)
    data[SOURCE_FILE_COLUMN] = source_file
    data[SOURCE_SPLIT_COLUMN] = source_split
    data[SAMPLE_INDEX_COLUMN] = np.arange(matrix.shape[0], dtype=np.int64)
    return pd.DataFrame(data)


def build_canonical_dataframe(
    raw_dir: Path,
    *,
    a1_metadata: dict[str, Any],
    excluded_fault_ids: frozenset[int] = EXCLUDED_FAULT_IDS,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Assemble the canonical table from audited raw files without mutating them."""
    raw_dir = Path(raw_dir)
    expected_hashes: dict[str, str] = dict(a1_metadata["sha256_by_file"])
    assert_raw_immutable(raw_dir, expected_hashes)

    paths = list_raw_dat_files(raw_dir)
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    frames: list[pd.DataFrame] = []
    orientations_applied: list[dict[str, str]] = []

    for path in paths:
        record, matrix = inventory_raw_file(path)
        # Fresh hash must still match A1 for this file.
        if expected_hashes.get(record.name) != record.sha256:
            raise CanonicalDatasetError(
                f"checksum drift for {record.name} during canonical build"
            )

        if record.fault_id in excluded_fault_ids:
            excluded.append(
                {
                    "name": record.name,
                    "fault_id": record.fault_id,
                    "run_id": record.run_id,
                    "sha256": record.sha256,
                    "reason": (
                        f"fault_id={record.fault_id} excluded to satisfy DS-03 "
                        f"({N_EXPECTED_CLASSES} classes, labels 0..20)"
                    ),
                }
            )
            continue

        oriented = as_samples_by_features(matrix, record.orientation)
        if record.orientation == "features_x_samples":
            orientations_applied.append(
                {
                    "name": record.name,
                    "raw_shape": f"{record.n_rows}x{record.n_cols}",
                    "canonical_shape": f"{oriented.shape[0]}x{oriented.shape[1]}",
                    "action": "transpose_in_memory",
                }
            )

        frame = _matrix_to_frame(
            oriented,
            run_id=record.run_id,
            class_label=record.fault_id,
            source_file=record.name,
            source_split=record.source_split,
        )
        frames.append(frame)
        included.append(
            {
                "name": record.name,
                "fault_id": record.fault_id,
                "run_id": record.run_id,
                "source_split": record.source_split,
                "raw_shape": [record.n_rows, record.n_cols],
                "oriented_shape": [int(oriented.shape[0]), int(oriented.shape[1])],
                "orientation": record.orientation,
                "sha256": record.sha256,
                "n_samples": int(oriented.shape[0]),
            }
        )

    if not frames:
        raise CanonicalDatasetError("canonical build produced zero included files")

    df = pd.concat(frames, ignore_index=True)
    # Column order: features, ids, provenance.
    df = df.loc[:, list(CANONICAL_REQUIRED_COLUMNS)]

    validate_canonical_schema(df)
    validate_class_consistency(df)
    assert_run_class_bijection(df)

    build_info = {
        "included_files": included,
        "excluded_files": excluded,
        "orientations_applied": orientations_applied,
        "n_rows": int(len(df)),
        "n_runs": int(df[RUN_ID_COLUMN].nunique()),
        "n_classes": int(df[CLASS_LABEL_COLUMN].nunique()),
        "class_labels": sorted(int(x) for x in df[CLASS_LABEL_COLUMN].unique()),
        "n_features": len(FEATURE_COLUMNS),
    }
    return df, build_info


def _dataframe_content_sha256(df: pd.DataFrame) -> str:
    """Stable content hash of the canonical table (CSV bytes, sorted columns)."""
    payload = df.to_csv(index=False).encode("utf-8")
    return _sha256_bytes(payload)


def write_canonical_artifacts(
    df: pd.DataFrame,
    build_info: dict[str, Any],
    *,
    a1_metadata: dict[str, Any],
    processed_dir: Path,
    metadata_dir: Path | None = None,
) -> dict[str, Path]:
    """Persist canonical table + registry. Never writes under data/raw/."""
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    table_path = processed_dir / CANONICAL_TABLE_NAME
    registry_path = processed_dir / REGISTRY_NAME
    non_canonical_path = processed_dir / "NON_CANONICAL.md"

    df.to_csv(table_path, index=False, compression="gzip")
    table_sha256 = sha256_file(table_path)
    content_sha256 = _dataframe_content_sha256(df)

    registry = {
        "dataset_version": DATASET_VERSION,
        "status": "canonical",
        "spec": "SPEC-002",
        "adr": ["ADR-004", "ADR-004-amendment-001"],
        "frozen_at": _utc_now(),
        "a1_reference": {
            "spec": a1_metadata.get("spec", "SPEC-001"),
            "delivery": a1_metadata.get("delivery", "A1"),
            "generated_at": a1_metadata.get("generated_at"),
            "metadata_path": "results/metadata/audit_counts.json",
            "report_paths": [
                "reports/audit/A1_audit_report.md",
                "reports/audit/A1_findings.csv",
            ],
        },
        "treatments": list(TREATMENTS),
        "source_files_included": build_info["included_files"],
        "source_files_excluded": build_info["excluded_files"],
        "orientations_applied": build_info["orientations_applied"],
        "counts": {
            "n_rows": build_info["n_rows"],
            "n_runs": build_info["n_runs"],
            "n_classes": build_info["n_classes"],
            "n_features": build_info["n_features"],
            "class_labels": build_info["class_labels"],
        },
        "artifacts": {
            "table": f"data/processed/{CANONICAL_TABLE_NAME}",
            "table_sha256": table_sha256,
            "content_sha256": content_sha256,
            "registry": f"data/processed/{REGISTRY_NAME}",
        },
        "raw_sha256_by_file": {
            item["name"]: item["sha256"] for item in build_info["included_files"]
        },
        "schema": {
            "feature_columns": list(FEATURE_COLUMNS),
            "id_columns": [RUN_ID_COLUMN, CLASS_LABEL_COLUMN],
            "provenance_columns": [
                SOURCE_FILE_COLUMN,
                SOURCE_SPLIT_COLUMN,
                SAMPLE_INDEX_COLUMN,
            ],
        },
        "non_canonical_policy": (
            "Qualquer subconjunto, amostra reduzida ou versão alternativa do TEP "
            "que não seja exatamente este dataset_version é NÃO CANÔNICA e não pode "
            "alimentar entregas A5–A9. Alterações exigem nova auditoria (SPEC-001) "
            "e emenda a ADR-004."
        ),
    }

    registry_path.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    excluded_lines = [
        f"- `{item['name']}` — {item['reason']}"
        for item in build_info["excluded_files"]
    ] or ["- (nenhum arquivo excluído além da política abaixo)"]
    non_canonical_path.write_text(
        "\n".join(
            [
                "# Material não canônico",
                "",
                f"A única versão canônica vigente é **`{DATASET_VERSION}`**, "
                f"registrada em `{REGISTRY_NAME}`.",
                "",
                "## Excluído do canônico (por decisão SPEC-002)",
                "",
                *excluded_lines,
                "",
                "## Política",
                "",
                registry["non_canonical_policy"],
                "",
                "Fixtures sintéticas em `tests/` e qualquer CSV/Parquet ad hoc "
                "em `data/interim/` são **não canônicos**.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    written = {
        "table": table_path,
        "registry": registry_path,
        "non_canonical": non_canonical_path,
    }

    if metadata_dir is not None:
        metadata_dir = Path(metadata_dir)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        meta_path = metadata_dir / "canonical_dataset.json"
        meta_path.write_text(
            json.dumps(
                {
                    "dataset_version": DATASET_VERSION,
                    "frozen_at": registry["frozen_at"],
                    "counts": registry["counts"],
                    "artifacts": registry["artifacts"],
                    "treatments": registry["treatments"],
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        written["metadata"] = meta_path

    return written


def load_canonical_dataframe(processed_dir: Path) -> pd.DataFrame:
    """Load the canonical table and validate schema + class consistency."""
    processed_dir = Path(processed_dir)
    table_path = processed_dir / CANONICAL_TABLE_NAME
    if not table_path.is_file():
        raise CanonicalDatasetError(f"canonical table not found: {table_path}")
    df = pd.read_csv(table_path, compression="gzip")
    validate_canonical_schema(df)
    validate_class_consistency(df)
    assert_run_class_bijection(df)
    return df


def load_canonical_registry(processed_dir: Path) -> dict[str, Any]:
    path = Path(processed_dir) / REGISTRY_NAME
    if not path.is_file():
        raise CanonicalDatasetError(f"canonical registry not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_registry_against_table(
    registry: dict[str, Any], df: pd.DataFrame, *, table_path: Path
) -> None:
    """Ensure registry counts/hashes match the on-disk canonical table."""
    errors: list[str] = []
    counts = registry.get("counts", {})
    if counts.get("n_rows") != len(df):
        errors.append(f"registry n_rows={counts.get('n_rows')} != table {len(df)}")
    if counts.get("n_runs") != df[RUN_ID_COLUMN].nunique():
        errors.append("registry n_runs mismatch")
    if counts.get("n_classes") != df[CLASS_LABEL_COLUMN].nunique():
        errors.append("registry n_classes mismatch")
    if counts.get("n_features") != len(FEATURE_COLUMNS):
        errors.append("registry n_features mismatch")
    expected_labels = set(counts.get("class_labels", []))
    observed = set(int(x) for x in df[CLASS_LABEL_COLUMN].unique())
    if expected_labels != observed:
        errors.append(f"registry class_labels {sorted(expected_labels)} != {sorted(observed)}")

    actual_table_sha = sha256_file(table_path)
    if registry.get("artifacts", {}).get("table_sha256") != actual_table_sha:
        errors.append("registry table_sha256 does not match file on disk")

    content_sha = _dataframe_content_sha256(df)
    if registry.get("artifacts", {}).get("content_sha256") != content_sha:
        errors.append("registry content_sha256 does not match loaded table")

    if registry.get("status") != "canonical":
        errors.append("registry status must be 'canonical'")
    if registry.get("dataset_version") != DATASET_VERSION:
        errors.append(
            f"unexpected dataset_version {registry.get('dataset_version')!r}; "
            f"expected {DATASET_VERSION!r}"
        )

    if errors:
        raise CanonicalDatasetError("; ".join(errors))


def build_and_register(
    *,
    raw_dir: Path,
    processed_dir: Path,
    a1_metadata_path: Path,
    metadata_dir: Path | None = None,
) -> dict[str, Path]:
    """End-to-end SPEC-002: verify raw immutability, build, validate, register."""
    a1_metadata = load_a1_metadata(a1_metadata_path)
    df, build_info = build_canonical_dataframe(raw_dir, a1_metadata=a1_metadata)
    written = write_canonical_artifacts(
        df,
        build_info,
        a1_metadata=a1_metadata,
        processed_dir=processed_dir,
        metadata_dir=metadata_dir,
    )
    # Post-condition: raw still unchanged; registry consistent with table.
    assert_raw_immutable(raw_dir, a1_metadata["sha256_by_file"])
    registry = load_canonical_registry(processed_dir)
    loaded = load_canonical_dataframe(processed_dir)
    validate_registry_against_table(registry, loaded, table_path=written["table"])
    return written
