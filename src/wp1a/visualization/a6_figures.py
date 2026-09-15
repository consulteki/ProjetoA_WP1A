"""Figuras A6 — apenas a partir de DataFrames já carregados de ``results/``."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Paleta deliberada (evitar defaults “AI purple”).
C_TEAL = "#1b7f7a"
C_SLATE = "#2f3e46"
C_AMBER = "#c47b2b"
C_ROSE = "#a33b3b"
C_BLUE = "#3d5a80"

sns.set_theme(style="whitegrid", context="notebook")


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=160)
    plt.close(fig)
    return path


def fig_dataset_characterization(char_df: pd.DataFrame, out: Path) -> Path:
    """Insumo 1 (visual): amostras e runs por classe a partir da tabela A1 em results/."""
    df = char_df[char_df["in_normative_set_0_20"] == True].copy()  # noqa: E712
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].bar(df["class_label"].astype(str), df["n_samples"], color=C_SLATE)
    axes[0].set_ylabel("n_samples")
    axes[0].set_title("A6 — Caracterização da base (classes normativas 0–20)")
    axes[1].bar(df["class_label"].astype(str), df["n_runs"], color=C_TEAL)
    axes[1].set_xlabel("class_label")
    axes[1].set_ylabel("n_runs")
    return _save(fig, out)


def fig_f1_mcc(global_df: pd.DataFrame, out: Path) -> Path:
    """Insumo 6: F1 macro e MCC lado a lado (INV-06: não só acurácia)."""
    df = global_df.sort_values("model_id")
    x = np.arange(len(df))
    w = 0.38
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w / 2, df["MET-05_f1_macro"], width=w, label="F1 macro (MET-05)", color=C_TEAL)
    ax.bar(x + w / 2, df["MET-07_mcc"], width=w, label="MCC (MET-07)", color=C_SLATE)
    ax.set_xticks(x)
    ax.set_xticklabels(df["model_id"], rotation=25, ha="right")
    ax.set_ylabel("score")
    ax.set_ylim(0, 1)
    ax.set_title("A6 — F1 macro e MCC (teste; exp-a4-v2)")
    ax.legend(frameon=False)
    ax.axhline(0, color="0.5", lw=0.5)
    return _save(fig, out)


def fig_computational_cost(cost_df: pd.DataFrame, out: Path) -> Path:
    """Insumo 7: treino, inferência e tamanho (MET-10..12)."""
    df = cost_df.sort_values("model_id")
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    axes[0].barh(df["model_id"], df["MET-10_train_time_s"], color=C_TEAL)
    axes[0].set_xlabel("train time (s)")
    axes[0].set_title("MET-10")
    axes[1].barh(df["model_id"], df["MET-11_inference_time_s"], color=C_AMBER)
    axes[1].set_xlabel("inference time (s)")
    axes[1].set_title("MET-11")
    size_mb = df["MET-12_model_size_bytes"] / (1024 * 1024)
    axes[2].barh(df["model_id"], size_mb, color=C_SLATE)
    axes[2].set_xlabel("model size (MiB)")
    axes[2].set_title("MET-12")
    fig.suptitle("A6 — Custo computacional (INV-07)", y=1.02)
    fig.tight_layout()
    return _save(fig, out)


def fig_per_class_f1_heatmap(per_class: pd.DataFrame, out: Path) -> Path:
    """Insumo 8a: F1 por classe×modelo; classes com support==0 ficam NaN (não fingir dificuldade)."""
    # Use max support across models per class to mask absents.
    support = (
        per_class.groupby("class_label")["support"].max().rename("max_support")
    )
    pivot = per_class.pivot_table(
        index="class_label", columns="model_id", values="f1", aggfunc="mean"
    )
    for c in pivot.index:
        if int(support.loc[c]) == 0:
            pivot.loc[c, :] = np.nan
    fig, ax = plt.subplots(figsize=(11, 8))
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="mako",
        vmin=0,
        vmax=1,
        linewidths=0.3,
        linecolor="white",
        cbar_kws={"label": "F1"},
    )
    ax.set_title(
        "A6 — F1 por classe (NaN = support 0 no teste; não interpretar como falha difícil)"
    )
    ax.set_xlabel("model")
    ax.set_ylabel("class_label")
    return _save(fig, out)


def fig_confused_pairs(qp3: dict, out: Path, *, top_n: int = 10) -> Path:
    """Insumo 8b: pares true→pred mais frequentes (agregado A5)."""
    pairs = list(qp3.get("systematic_confused_pairs", []))[:top_n]
    if not pairs:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.text(0.5, 0.5, "no confused pairs in source", ha="center")
        ax.axis("off")
        return _save(fig, out)
    labels = [f"{p['true_class']}→{p['pred_class']}" for p in pairs]
    vals = [p["total_count_across_models"] for p in pairs]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(labels[::-1], vals[::-1], color=C_ROSE)
    ax.set_xlabel("count (sum across 6 models)")
    ax.set_title("A6 — Pares de confusão mais frequentes (insumo QP3)")
    return _save(fig, out)


def fig_confusion_matrix(cm_df: pd.DataFrame, model_id: str, out: Path) -> Path:
    """Insumo 5: heatmap de uma matriz de confusão A5."""
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(cm_df, ax=ax, cmap="Blues", cbar_kws={"label": "count"})
    ax.set_title(f"A6 — Confusion matrix — {model_id}")
    ax.set_xlabel("predicted")
    ax.set_ylabel("true")
    return _save(fig, out)
