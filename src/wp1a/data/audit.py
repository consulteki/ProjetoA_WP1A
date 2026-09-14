"""Auditoria dos dados brutos do TEP (SPEC-001 / Entrega A1).

Implementa os 8 itens obrigatórios de ``docs/specs/SPEC-001-data-audit.md``
e ``.agents/skills/data-audit/SKILL.md``. Não decide o dataset canônico
(SPEC-002) e não treina modelos.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from wp1a.data.raw_loader import (
    EXPECTED_N_FEATURES,
    RawFileRecord,
    as_samples_by_features,
    inventory_raw_file,
    list_raw_dat_files,
)
from wp1a.data.schema import N_EXPECTED_CLASSES, N_EXPECTED_FEATURES, VALID_CLASS_LABELS
from wp1a.data.audit_pdf import write_audit_pdf
from wp1a.data.variables import FAULT_MEANINGS, variable_catalog

NORMATIVE_CLASSES = frozenset(range(N_EXPECTED_CLASSES))  # 0..20
PROVENANCE = {
    "dataset_family": "Tennessee Eastman Process (TEP) — Russell/Chiang/Braatz reference files",
    "source_url": "https://github.com/jkitchin/tennessee-eastman-profbraatz/tree/master/data",
    "literature": [
        "Downs, J.J. & Vogel, E.F. (1993). A plant-wide industrial process control problem.",
        "Russell, E.L.; Chiang, L.H.; Braatz, R.D. (2000). Data-driven Techniques for Fault Detection and Diagnosis in Chemical Processes.",
    ],
}


@dataclass
class AuditFinding:
    item: int
    title: str
    status: str  # "ok" | "divergence" | "anomaly" | "info"
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditResult:
    generated_at: str
    raw_dir: str
    findings: list[AuditFinding]
    files: list[dict[str, Any]]
    variables: list[dict[str, str]]
    class_distribution: list[dict[str, Any]]
    runs_per_class: list[dict[str, Any]]
    integrity: dict[str, Any]
    duplicates: dict[str, Any]
    file_class_run: list[dict[str, Any]]
    normative_check: dict[str, Any]
    metadata: dict[str, Any]

    def finding_by_item(self, item: int) -> AuditFinding:
        for finding in self.findings:
            if finding.item == item:
                return finding
        raise KeyError(item)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _row_hash(row: np.ndarray) -> bytes:
    return np.ascontiguousarray(row, dtype=np.float64).tobytes()


def run_audit(raw_dir: Path) -> AuditResult:
    """Execute the eight mandatory audit checks over ``raw_dir``."""
    raw_dir = Path(raw_dir)
    paths = list_raw_dat_files(raw_dir)
    if not paths:
        raise FileNotFoundError(f"no .dat files found under {raw_dir}")

    records: list[RawFileRecord] = []
    matrices: dict[str, np.ndarray] = {}
    oriented: dict[str, np.ndarray] = {}

    for path in paths:
        record, matrix = inventory_raw_file(path)
        records.append(record)
        matrices[record.name] = matrix
        oriented[record.name] = as_samples_by_features(matrix, record.orientation)

    findings: list[AuditFinding] = []

    # --- Item 1: arquivos disponíveis ---
    files_table = [
        {
            "name": r.name,
            "format": r.format,
            "size_bytes": r.size_bytes,
            "sha256": r.sha256,
            "n_rows": r.n_rows,
            "n_cols": r.n_cols,
            "orientation": r.orientation,
            "expected_shape": f"{r.expected_shape[0]}x{r.expected_shape[1]}",
            "shape_matches_expected": r.shape_matches_expected,
            "fault_id": r.fault_id,
            "source_split": r.source_split,
            "run_id": r.run_id,
        }
        for r in records
    ]
    findings.append(
        AuditFinding(
            item=1,
            title="Arquivos disponíveis",
            status="ok",
            summary=(
                f"{len(records)} arquivo(s) .dat encontrados em {raw_dir.as_posix()}; "
                "nome, formato, tamanho e sha256 registrados."
            ),
            details={"n_files": len(records)},
        )
    )

    # --- Item 2: linhas e colunas ---
    shape_anomalies = [r for r in records if not r.shape_matches_expected]
    findings.append(
        AuditFinding(
            item=2,
            title="Quantidade de linhas e colunas por arquivo",
            status="anomaly" if shape_anomalies else "ok",
            summary=(
                "nenhum problema encontrado — todas as formas conferem com o layout Braatz esperado."
                if not shape_anomalies
                else (
                    f"{len(shape_anomalies)} arquivo(s) com forma divergente do esperado "
                    f"(treino {480}×{52}, teste {960}×{52}): "
                    + ", ".join(
                        f"{r.name}={r.n_rows}x{r.n_cols} ({r.orientation})" for r in shape_anomalies
                    )
                )
            ),
            details={"anomalies": [r.name for r in shape_anomalies]},
        )
    )

    # --- Item 3: nomes, tipos e significado ---
    variables = variable_catalog()
    # Tipagem observada: matrizes float64 carregadas via np.loadtxt.
    observed_dtype = "float64"
    findings.append(
        AuditFinding(
            item=3,
            title="Nomes, tipos e significado das variáveis",
            status="ok",
            summary=(
                f"Catálogo de {len(variables)} variáveis canônicas (xmeas_1..41 + xmv_1..11) "
                f"documentado; dtype observado nos .dat = {observed_dtype}."
            ),
            details={"n_variables_catalog": len(variables), "observed_dtype": observed_dtype},
        )
    )

    # --- Item 4: distribuição das classes ---
    # Contagem por amostra (após orientação samples×features).
    class_sample_counts: dict[int, int] = {}
    for r in records:
        class_sample_counts[r.fault_id] = class_sample_counts.get(r.fault_id, 0) + oriented[
            r.name
        ].shape[0]
    observed_classes = frozenset(class_sample_counts)
    class_distribution = [
        {
            "class_label": c,
            "n_samples": class_sample_counts.get(c, 0),
            "meaning": FAULT_MEANINGS.get(c, "não documentado na fonte local"),
            "in_normative_set_0_20": c in NORMATIVE_CLASSES,
        }
        for c in sorted(class_sample_counts)
    ]
    missing_normative = sorted(NORMATIVE_CLASSES - observed_classes)
    extra_classes = sorted(observed_classes - NORMATIVE_CLASSES)
    class_status = "ok"
    class_parts: list[str] = []
    if missing_normative:
        class_status = "divergence"
        class_parts.append(f"classes normativas ausentes: {missing_normative}")
    if extra_classes:
        class_status = "divergence"
        class_parts.append(
            f"classes além do normativo DS-03 (0..20): {extra_classes} "
            "(arquivos d21* presentes no pacote Braatz)"
        )
    if class_status == "ok":
        class_summary = (
            f"21 classes normativas (0..20) presentes; distribuição de amostras registrada. "
            f"Total de amostras (após orientação): {sum(class_sample_counts.values())}."
        )
    else:
        class_summary = (
            f"Divergência frente a DS-03 (21 classes = 0..20). "
            + "; ".join(class_parts)
            + f". Classes observadas: {sorted(observed_classes)}."
        )
    findings.append(
        AuditFinding(
            item=4,
            title="Distribuição das 21 classes",
            status=class_status,
            summary=class_summary,
            details={
                "n_observed_classes": len(observed_classes),
                "n_normative_classes": N_EXPECTED_CLASSES,
                "missing_normative": missing_normative,
                "extra_classes": extra_classes,
            },
        )
    )

    # --- Item 5: execuções (run) por classe ---
    runs_by_class: dict[int, list[str]] = {}
    for r in records:
        runs_by_class.setdefault(r.fault_id, []).append(r.run_id)
    runs_per_class = [
        {
            "class_label": c,
            "n_runs": len(runs_by_class[c]),
            "run_ids": sorted(runs_by_class[c]),
        }
        for c in sorted(runs_by_class)
    ]
    findings.append(
        AuditFinding(
            item=5,
            title="Quantidade de execuções (run) por classe",
            status="ok",
            summary=(
                f"{len(records)} run_id distintos (1 arquivo = 1 execução Braatz); "
                "contagem por classe registrada. "
                "Nota: os rótulos braatz_train/braatz_test são proveniência do pacote "
                "original, NÃO a divisão experimental WP1A (SPEC-004)."
            ),
            details={"n_runs_total": len(records)},
        )
    )

    # --- Item 6: ausentes / infinitos / inconsistentes ---
    missing_total = 0
    inf_total = 0
    per_file_integrity: list[dict[str, Any]] = []
    for r in records:
        mat = oriented[r.name]
        n_nan = int(np.isnan(mat).sum())
        n_inf = int(np.isinf(mat).sum())
        missing_total += n_nan
        inf_total += n_inf
        # Inconsistência estrutural: número de features ≠ 52 após orientação.
        n_features = int(mat.shape[1]) if mat.ndim == 2 else -1
        feature_ok = n_features == EXPECTED_N_FEATURES
        per_file_integrity.append(
            {
                "name": r.name,
                "n_nan": n_nan,
                "n_inf": n_inf,
                "n_features_after_orient": n_features,
                "features_eq_52": feature_ok,
                "shape_anomaly": not r.shape_matches_expected,
            }
        )
    integrity_problems = missing_total + inf_total
    feature_mismatches = [x for x in per_file_integrity if not x["features_eq_52"]]
    integrity_status = "ok"
    integrity_bits: list[str] = []
    if integrity_problems == 0 and not feature_mismatches:
        integrity_summary = (
            "nenhum problema encontrado — zero NaN, zero Inf; "
            "todas as matrizes orientadas têm 52 colunas de processo."
        )
    else:
        integrity_status = "anomaly"
        if missing_total:
            integrity_bits.append(f"NaN={missing_total}")
        if inf_total:
            integrity_bits.append(f"Inf={inf_total}")
        if feature_mismatches:
            integrity_bits.append(
                "features≠52 após orientação: "
                + ", ".join(x["name"] for x in feature_mismatches)
            )
        # Formas anômalas já reportadas no item 2; reforço aqui como inconsistência.
        shape_flags = [x["name"] for x in per_file_integrity if x["shape_anomaly"]]
        if shape_flags:
            integrity_bits.append(f"forma inconsistente com layout Braatz: {shape_flags}")
        integrity_summary = "; ".join(integrity_bits)
    integrity = {
        "n_nan_total": missing_total,
        "n_inf_total": inf_total,
        "per_file": per_file_integrity,
    }
    findings.append(
        AuditFinding(
            item=6,
            title="Valores ausentes, infinitos ou inconsistentes",
            status=integrity_status,
            summary=integrity_summary,
            details=integrity,
        )
    )

    # --- Item 7: duplicações ---
    intra_dup_rows = 0
    intra_details: list[dict[str, Any]] = []
    global_hashes: dict[bytes, list[tuple[str, int]]] = {}
    for r in records:
        mat = oriented[r.name]
        seen: dict[bytes, int] = {}
        file_dups = 0
        for i in range(mat.shape[0]):
            h = _row_hash(mat[i])
            if h in seen:
                file_dups += 1
            else:
                seen[h] = i
            global_hashes.setdefault(h, []).append((r.name, i))
        intra_dup_rows += file_dups
        if file_dups:
            intra_details.append({"name": r.name, "n_duplicate_rows": file_dups})

    cross_file_dup_groups = [
        {
            "n_occurrences": len(locs),
            "locations": [{"file": f, "row_index": i} for f, i in locs],
        }
        for locs in global_hashes.values()
        if len({f for f, _ in locs}) > 1
    ]
    # Contar apenas grupos com a mesma linha em arquivos distintos.
    n_cross_groups = len(cross_file_dup_groups)
    dup_status = "ok"
    if intra_dup_rows == 0 and n_cross_groups == 0:
        dup_summary = (
            "nenhum problema encontrado — sem linhas duplicadas intra-arquivo "
            "nem grupos de linhas idênticas compartilhados entre arquivos."
        )
    else:
        dup_status = "anomaly"
        parts = []
        if intra_dup_rows:
            parts.append(f"duplicatas intra-arquivo (linhas extras): {intra_dup_rows}")
        if n_cross_groups:
            parts.append(
                f"grupos de linhas idênticas presentes em ≥2 arquivos: {n_cross_groups}"
            )
            parts.append(
                "nota: no pacote Braatz, arquivos *_te.dat tipicamente compartilham "
                "o trecho inicial em operação normal (pré-introdução da falha); "
                "isso é um achado de auditoria a decidir em SPEC-002, não uma "
                "correção silenciosa nesta etapa"
            )
        dup_summary = "; ".join(parts)
    duplicates = {
        "intra_file_duplicate_row_count": intra_dup_rows,
        "intra_file_details": intra_details,
        "cross_file_duplicate_group_count": n_cross_groups,
        # Limitar detalhe no relatório principal para não inflar o artefato.
        "cross_file_duplicate_groups_sample": cross_file_dup_groups[:20],
    }
    findings.append(
        AuditFinding(
            item=7,
            title="Possíveis duplicações (intra e entre arquivos)",
            status=dup_status,
            summary=dup_summary,
            details={
                "intra_file_duplicate_row_count": intra_dup_rows,
                "cross_file_duplicate_group_count": n_cross_groups,
            },
        )
    )

    # --- Item 8: relação arquivo–classe–run_id ---
    file_class_run = [
        {
            "file": r.name,
            "class_label": r.fault_id,
            "run_id": r.run_id,
            "source_split": r.source_split,
        }
        for r in records
    ]
    # Verificações automatizadas de consistência.
    run_to_class: dict[str, set[int]] = {}
    run_to_files: dict[str, set[str]] = {}
    for r in records:
        run_to_class.setdefault(r.run_id, set()).add(r.fault_id)
        run_to_files.setdefault(r.run_id, set()).add(r.name)
    ambiguous_runs = {rid: sorted(classes) for rid, classes in run_to_class.items() if len(classes) > 1}
    multi_file_runs = {rid: sorted(files) for rid, files in run_to_files.items() if len(files) > 1}
    relation_ok = not ambiguous_runs and not multi_file_runs
    findings.append(
        AuditFinding(
            item=8,
            title="Relação entre arquivos, classes e identificadores de execução (run_id)",
            status="ok" if relation_ok else "anomaly",
            summary=(
                "nenhum problema encontrado — cada run_id mapeia a exatamente uma classe "
                "e a exatamente um arquivo de origem; verificação automatizada executada."
                if relation_ok
                else (
                    f"ambiguidade detectada: run_id→classes={ambiguous_runs}; "
                    f"run_id→arquivos={multi_file_runs}"
                )
            ),
            details={
                "n_mappings": len(file_class_run),
                "ambiguous_run_to_class": ambiguous_runs,
                "multi_file_runs": multi_file_runs,
                "automated_check": True,
            },
        )
    )

    # --- Checagem normativa DS-02 / DS-03 ---
    # DS-02: 52 variáveis — conferido via orientação + catálogo.
    feature_ok_global = all(x["features_eq_52"] for x in per_file_integrity)
    normative_check = {
        "DS-02_expected_features": N_EXPECTED_FEATURES,
        "DS-02_observed_features_after_orient": EXPECTED_N_FEATURES if feature_ok_global else "mixed",
        "DS-02_status": "ok" if feature_ok_global else "divergence",
        "DS-03_expected_classes": N_EXPECTED_CLASSES,
        "DS-03_expected_labels": sorted(VALID_CLASS_LABELS),
        "DS-03_observed_classes": sorted(observed_classes),
        "DS-03_status": class_status,
        "notes": (
            "O pacote Braatz inclui d21/d21_te (classe 21), excedendo as 21 classes "
            "normativas (0..20). A decisão de inclusão/exclusão cabe à SPEC-002."
            if extra_classes
            else ""
        ),
    }

    metadata = {
        "provenance": PROVENANCE,
        "n_files": len(records),
        "n_runs": len(records),
        "n_samples_oriented": int(sum(m.shape[0] for m in oriented.values())),
        "n_features_expected": N_EXPECTED_FEATURES,
        "n_classes_observed": len(observed_classes),
        "n_classes_normative": N_EXPECTED_CLASSES,
        "sha256_by_file": {r.name: r.sha256 for r in records},
        "shape_anomalies": [r.name for r in shape_anomalies],
        "extra_classes_beyond_ds03": extra_classes,
        "missing_normative_classes": missing_normative,
    }

    return AuditResult(
        generated_at=_utc_now(),
        raw_dir=str(raw_dir.resolve()),
        findings=findings,
        files=files_table,
        variables=variables,
        class_distribution=class_distribution,
        runs_per_class=runs_per_class,
        integrity=integrity,
        duplicates=duplicates,
        file_class_run=file_class_run,
        normative_check=normative_check,
        metadata=metadata,
    )


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def _findings_dataframe(result: AuditResult) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "item": f.item,
                "title": f.title,
                "status": f.status,
                "summary": f.summary,
            }
            for f in result.findings
        ]
    )


def render_markdown_report(result: AuditResult) -> str:
    lines: list[str] = [
        "# Entrega A1 — Relatório de Auditoria da Base (TEP)",
        "",
        f"- Gerado em: `{result.generated_at}`",
        f"- Diretório auditado: `{result.raw_dir}`",
        f"- Fonte: {PROVENANCE['dataset_family']}",
        f"- URL de origem: {PROVENANCE['source_url']}",
        "",
        "## Escopo",
        "",
        "Auditoria exclusiva dos arquivos brutos (`data/raw/`), conforme "
        "`docs/specs/SPEC-001-data-audit.md` e `.agents/skills/data-audit/SKILL.md`. "
        "Nenhuma transformação de modelagem foi aplicada; a definição do dataset "
        "canônico permanece sob SPEC-002.",
        "",
        "## Checagem normativa (DS-02 / DS-03)",
        "",
        f"- **DS-02** (52 variáveis): `{result.normative_check['DS-02_status']}` "
        f"(esperado={result.normative_check['DS-02_expected_features']}, "
        f"observado={result.normative_check['DS-02_observed_features_after_orient']})",
        f"- **DS-03** (21 classes 0..20): `{result.normative_check['DS-03_status']}` "
        f"(observado={result.normative_check['DS-03_observed_classes']})",
    ]
    if result.normative_check.get("notes"):
        lines += ["", f"> Nota: {result.normative_check['notes']}"]
    lines += ["", "## Itens obrigatórios (RP-01 / CA-02)", ""]
    for finding in result.findings:
        lines += [
            f"### Item {finding.item} — {finding.title}",
            "",
            f"- **Status:** `{finding.status}`",
            f"- **Resultado:** {finding.summary}",
            "",
        ]
    lines += [
        "## Artefatos tabulares",
        "",
        "- `A1_01_files.csv` — inventário de arquivos",
        "- `A1_02_shapes.csv` — linhas/colunas por arquivo",
        "- `A1_03_variables.csv` — catálogo de variáveis",
        "- `A1_04_class_distribution.csv` — amostras por classe",
        "- `A1_05_runs_per_class.csv` — execuções por classe",
        "- `A1_06_integrity.csv` — NaN/Inf/inconsistências por arquivo",
        "- `A1_07_duplicates_summary.csv` — resumo de duplicações",
        "- `A1_08_file_class_run.csv` — mapeamento arquivo–classe–run_id",
        "- `A1_findings.csv` — status dos 8 itens",
        "- `../tables/A1_dataset_characterization.csv` — tabela de caracterização (insumo 1)",
        "",
        "## Metadados para SPEC-002",
        "",
        "Contagens e checksums em `results/metadata/audit_counts.json`.",
        "",
    ]
    return "\n".join(lines)


def write_characterization_table(result: AuditResult) -> pd.DataFrame:
    """Insumo 1 — tabela de caracterização da base (SPEC-000 §11.2)."""
    rows = []
    for c in result.class_distribution:
        runs = next(r for r in result.runs_per_class if r["class_label"] == c["class_label"])
        rows.append(
            {
                "class_label": c["class_label"],
                "meaning": c["meaning"],
                "in_normative_set_0_20": c["in_normative_set_0_20"],
                "n_samples": c["n_samples"],
                "n_runs": runs["n_runs"],
                "n_features": N_EXPECTED_FEATURES,
            }
        )
    return pd.DataFrame(rows)


def write_audit_artifacts(
    result: AuditResult,
    *,
    reports_dir: Path,
    metadata_dir: Path,
    tables_dir: Path,
) -> dict[str, Path]:
    """Persist Entrega A1 (CSV + Markdown) and metadata for SPEC-002."""
    reports_dir = Path(reports_dir)
    metadata_dir = Path(metadata_dir)
    tables_dir = Path(tables_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    written: dict[str, Path] = {}

    findings_df = _findings_dataframe(result)
    path = reports_dir / "A1_findings.csv"
    _write_csv(findings_df, path)
    written["findings"] = path

    path = reports_dir / "A1_01_files.csv"
    _write_csv(
        pd.DataFrame(result.files)[
            [
                "name",
                "format",
                "size_bytes",
                "sha256",
                "fault_id",
                "source_split",
                "run_id",
            ]
        ],
        path,
    )
    written["files"] = path

    path = reports_dir / "A1_02_shapes.csv"
    _write_csv(
        pd.DataFrame(result.files)[
            [
                "name",
                "n_rows",
                "n_cols",
                "orientation",
                "expected_shape",
                "shape_matches_expected",
            ]
        ],
        path,
    )
    written["shapes"] = path

    path = reports_dir / "A1_03_variables.csv"
    _write_csv(pd.DataFrame(result.variables), path)
    written["variables"] = path

    path = reports_dir / "A1_04_class_distribution.csv"
    _write_csv(pd.DataFrame(result.class_distribution), path)
    written["class_distribution"] = path

    path = reports_dir / "A1_05_runs_per_class.csv"
    runs_flat = []
    for row in result.runs_per_class:
        runs_flat.append(
            {
                "class_label": row["class_label"],
                "n_runs": row["n_runs"],
                "run_ids": "|".join(row["run_ids"]),
            }
        )
    _write_csv(pd.DataFrame(runs_flat), path)
    written["runs_per_class"] = path

    path = reports_dir / "A1_06_integrity.csv"
    _write_csv(pd.DataFrame(result.integrity["per_file"]), path)
    written["integrity"] = path

    path = reports_dir / "A1_07_duplicates_summary.csv"
    _write_csv(
        pd.DataFrame(
            [
                {
                    "intra_file_duplicate_row_count": result.duplicates[
                        "intra_file_duplicate_row_count"
                    ],
                    "cross_file_duplicate_group_count": result.duplicates[
                        "cross_file_duplicate_group_count"
                    ],
                    "summary": result.finding_by_item(7).summary,
                }
            ]
        ),
        path,
    )
    written["duplicates"] = path

    path = reports_dir / "A1_08_file_class_run.csv"
    _write_csv(pd.DataFrame(result.file_class_run), path)
    written["file_class_run"] = path

    char_df = write_characterization_table(result)
    path = tables_dir / "A1_dataset_characterization.csv"
    _write_csv(char_df, path)
    written["characterization"] = path

    md_path = reports_dir / "A1_audit_report.md"
    md_path.write_text(render_markdown_report(result), encoding="utf-8")
    written["report_md"] = md_path

    pdf_path = reports_dir / "A1_audit_report.pdf"
    write_audit_pdf(md_path, pdf_path)
    written["report_pdf"] = pdf_path

    # JSON completo + metadados enxutos para SPEC-002
    full_path = reports_dir / "A1_audit_report.json"
    payload = {
        "generated_at": result.generated_at,
        "raw_dir": result.raw_dir,
        "provenance": PROVENANCE,
        "findings": [asdict(f) for f in result.findings],
        "files": result.files,
        "variables": result.variables,
        "class_distribution": result.class_distribution,
        "runs_per_class": result.runs_per_class,
        "integrity": result.integrity,
        "duplicates": {
            "intra_file_duplicate_row_count": result.duplicates["intra_file_duplicate_row_count"],
            "intra_file_details": result.duplicates["intra_file_details"],
            "cross_file_duplicate_group_count": result.duplicates[
                "cross_file_duplicate_group_count"
            ],
            "cross_file_duplicate_groups_sample": result.duplicates[
                "cross_file_duplicate_groups_sample"
            ],
        },
        "file_class_run": result.file_class_run,
        "normative_check": result.normative_check,
        "metadata": result.metadata,
    }
    full_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written["report_json"] = full_path

    meta_path = metadata_dir / "audit_counts.json"
    meta_path.write_text(
        json.dumps(
            {
                "generated_at": result.generated_at,
                "spec": "SPEC-001",
                "delivery": "A1",
                "raw_dir": result.raw_dir,
                "counts": {
                    "n_files": result.metadata["n_files"],
                    "n_runs": result.metadata["n_runs"],
                    "n_samples_oriented": result.metadata["n_samples_oriented"],
                    "n_features_expected": result.metadata["n_features_expected"],
                    "n_classes_observed": result.metadata["n_classes_observed"],
                    "n_classes_normative": result.metadata["n_classes_normative"],
                },
                "normative_check": result.normative_check,
                "sha256_by_file": result.metadata["sha256_by_file"],
                "shape_anomalies": result.metadata["shape_anomalies"],
                "extra_classes_beyond_ds03": result.metadata["extra_classes_beyond_ds03"],
                "missing_normative_classes": result.metadata["missing_normative_classes"],
                "files": result.files,
                "class_distribution": result.class_distribution,
                "runs_per_class": result.runs_per_class,
                "file_class_run": result.file_class_run,
                "findings_status": {str(f.item): f.status for f in result.findings},
                "provenance": PROVENANCE,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    written["metadata"] = meta_path

    # A1_02_shapes — reconstruct from integrity + files if n_rows present
    # Will be fixed after enriching files table
    return written
