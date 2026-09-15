"""Entrega A6 — tabelas/figuras do artigo a partir exclusivamente de ``results/``.

Regra dura: nenhuma leitura de ``data/raw`` (nem interim). Fontes = A1/A2/A4/A5
já materializados sob ``results/``.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from wp1a.models.protocol import MODEL_IDS
from wp1a.visualization.a6_figures import (
    fig_computational_cost,
    fig_confused_pairs,
    fig_confusion_matrix,
    fig_dataset_characterization,
    fig_f1_mcc,
    fig_per_class_f1_heatmap,
)
from wp1a.visualization.sources import require_file

DISCLAIMER = (
    "A6 figures/tables are derived only from versioned files under results/. "
    "No data/raw access. Multicriteria view (INV-06/INV-07); no single-metric winner."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _copy_table(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def _df_to_latex(df: pd.DataFrame, path: Path, caption: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    # escape minimal; pandas to_latex handles most
    tex = df.to_latex(index=False, escape=True, caption=caption, label=f"tab:{path.stem}")
    path.write_text(tex, encoding="utf-8")
    return path


def run_a6(
    *,
    repo_root: Path,
    experiment_id: str = "exp-a4-v2",
) -> dict[str, Any]:
    root = Path(repo_root)
    results = root / "results"
    tables_in = results / "tables"
    metrics_in = results / "metrics"
    meta_in = results / "metadata"

    figures_out = results / "figures"
    tables_out = results / "tables"
    article_fig = root / "article" / "figures"
    article_tab = root / "article" / "tables"
    for d in (figures_out, tables_out, article_fig, article_tab):
        d.mkdir(parents=True, exist_ok=True)

    # --- resolve sources (results/ only) ---
    src_char = require_file(
        tables_in / "A1_dataset_characterization.csv", results_root=results
    )
    src_hp = require_file(
        tables_in / f"{experiment_id}__hyperparameters.csv", results_root=results
    )
    src_global = require_file(
        tables_in / f"A5_{experiment_id}__global_metrics.csv", results_root=results
    )
    src_per_class = require_file(
        tables_in / f"A5_{experiment_id}__per_class_metrics.csv", results_root=results
    )
    src_cost = require_file(
        tables_in / f"A5_{experiment_id}__cost_metrics.csv", results_root=results
    )
    src_qp3 = require_file(
        tables_in / f"A5_{experiment_id}__qp3_confused_faults.json", results_root=results
    )
    src_audit = require_file(meta_in / "audit_counts.json", results_root=results)
    src_canonical = require_file(meta_in / "canonical_dataset.json", results_root=results)

    char_df = pd.read_csv(src_char)
    hp_df = pd.read_csv(src_hp)
    global_df = pd.read_csv(src_global)
    per_class_df = pd.read_csv(src_per_class)
    cost_df = pd.read_csv(src_cost)
    qp3 = json.loads(src_qp3.read_text(encoding="utf-8"))
    audit = json.loads(src_audit.read_text(encoding="utf-8"))
    canonical = json.loads(src_canonical.read_text(encoding="utf-8"))

    if set(global_df["model_id"]) != set(MODEL_IDS):
        raise ValueError(
            f"A6 expects all six MODEL_IDS in global metrics; got {sorted(global_df['model_id'])}"
        )

    # --- publication tables (insumos 1–5, 8 tabular) ---
    summary_char = pd.DataFrame(
        [
            {
                "n_features": canonical["counts"]["n_features"],
                "n_classes_canonical": canonical["counts"]["n_classes"],
                "n_runs_canonical": canonical["counts"]["n_runs"],
                "n_rows_canonical": canonical["counts"]["n_rows"],
                "audit_n_files_raw_pack": audit["counts"]["n_files"],
                "audit_n_classes_observed_raw_pack": audit["counts"]["n_classes_observed"],
                "dataset_version": canonical["dataset_version"],
            }
        ]
    )

    outs: dict[str, str] = {}
    trace: list[dict[str, str]] = []

    def register(item: str, artifact: Path, sources: list[Path]) -> None:
        outs[item] = str(artifact)
        trace.append(
            {
                "item": item,
                "artifact": str(artifact.relative_to(root)),
                "sources": ",".join(str(s.relative_to(root)) for s in sources),
            }
        )

    # 1 — characterization
    t1 = tables_out / f"A6_{experiment_id}__01_dataset_characterization.csv"
    _copy_table(src_char, t1)
    _copy_table(t1, article_tab / t1.name)
    summary_path = tables_out / f"A6_{experiment_id}__01_dataset_summary.csv"
    summary_char.to_csv(summary_path, index=False)
    _copy_table(summary_path, article_tab / summary_path.name)
    _df_to_latex(summary_char, article_tab / f"A6_{experiment_id}__01_dataset_summary.tex", "Dataset characterization summary")
    register("01_characterization_table", t1, [src_char, src_canonical, src_audit])
    f1 = fig_dataset_characterization(
        char_df, figures_out / f"A6_{experiment_id}__01_dataset_characterization.png"
    )
    shutil.copy2(f1, article_fig / f1.name)
    register("01_characterization_figure", f1, [src_char])

    # 2 — hyperparameters
    t2 = tables_out / f"A6_{experiment_id}__02_hyperparameters.csv"
    _copy_table(src_hp, t2)
    _copy_table(t2, article_tab / t2.name)
    _df_to_latex(hp_df.fillna(""), article_tab / f"A6_{experiment_id}__02_hyperparameters.tex", "Frozen hyperparameters")
    register("02_hyperparameters", t2, [src_hp])

    # 3 — global metrics
    t3 = tables_out / f"A6_{experiment_id}__03_global_metrics.csv"
    _copy_table(src_global, t3)
    _copy_table(t3, article_tab / t3.name)
    cols = [
        "model_id",
        "MET-01_accuracy",
        "MET-02_balanced_accuracy",
        "MET-05_f1_macro",
        "MET-07_mcc",
        "MET-10_train_time_s",
        "MET-11_inference_time_s",
        "MET-12_model_size_bytes",
    ]
    _df_to_latex(
        global_df[cols],
        article_tab / f"A6_{experiment_id}__03_global_metrics.tex",
        "Global metrics MET-01..12 (excerpt)",
    )
    register("03_global_metrics", t3, [src_global])

    # 4 — per-class
    t4 = tables_out / f"A6_{experiment_id}__04_per_class_metrics.csv"
    _copy_table(src_per_class, t4)
    _copy_table(t4, article_tab / t4.name)
    register("04_per_class_metrics", t4, [src_per_class])

    # 5 — confusion matrices (copy + heatmaps)
    cm_sources: list[Path] = []
    for model_id in MODEL_IDS:
        src_cm = require_file(
            tables_in / f"A5_{experiment_id}__{model_id}__confusion_matrix.csv",
            results_root=results,
        )
        cm_sources.append(src_cm)
        dest = tables_out / f"A6_{experiment_id}__05_cm__{model_id}.csv"
        _copy_table(src_cm, dest)
        _copy_table(dest, article_tab / dest.name)
        cm_df = pd.read_csv(src_cm, index_col=0)
        fig_path = figures_out / f"A6_{experiment_id}__05_cm__{model_id}.png"
        fig_confusion_matrix(cm_df, model_id, fig_path)
        shutil.copy2(fig_path, article_fig / fig_path.name)
        register(f"05_cm_{model_id}", fig_path, [src_cm])

    # 6 — F1 / MCC figure
    f6 = fig_f1_mcc(global_df, figures_out / f"A6_{experiment_id}__06_f1_mcc.png")
    shutil.copy2(f6, article_fig / f6.name)
    register("06_f1_mcc", f6, [src_global])

    # 7 — cost figure
    f7 = fig_computational_cost(
        cost_df, figures_out / f"A6_{experiment_id}__07_computational_cost.png"
    )
    shutil.copy2(f7, article_fig / f7.name)
    t7 = tables_out / f"A6_{experiment_id}__07_computational_cost.csv"
    _copy_table(src_cost, t7)
    _copy_table(t7, article_tab / t7.name)
    register("07_computational_cost", f7, [src_cost])

    # 8 — confused faults
    f8a = fig_per_class_f1_heatmap(
        per_class_df, figures_out / f"A6_{experiment_id}__08_per_class_f1_heatmap.png"
    )
    shutil.copy2(f8a, article_fig / f8a.name)
    f8b = fig_confused_pairs(
        qp3, figures_out / f"A6_{experiment_id}__08_confused_pairs.png"
    )
    shutil.copy2(f8b, article_fig / f8b.name)
    t8 = tables_out / f"A6_{experiment_id}__08_confused_pairs.csv"
    pd.DataFrame(qp3.get("systematic_confused_pairs", [])).to_csv(t8, index=False)
    _copy_table(t8, article_tab / t8.name)
    register("08_confused_faults", f8a, [src_per_class, src_qp3])
    register("08_confused_pairs", f8b, [src_qp3])

    payload = {
        "delivery": "A6",
        "spec": "SPEC-009 §3.1 / scientific-figures",
        "experiment_id": experiment_id,
        "created_at": _utc_now(),
        "disclaimer": DISCLAIMER,
        "results_only": True,
        "forbidden": ["data/raw", "data/interim"],
        "artifacts": outs,
        "traceability": trace,
        "n_models": int(global_df["model_id"].nunique()),
    }
    meta_path = meta_in / f"A6_{experiment_id}__traceability.json"
    meta_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["traceability_path"] = str(meta_path)
    return payload
