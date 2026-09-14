"""Figuras programáticas da Entrega A2 (SPEC-003).

Todas as figuras são geradas em código (matplotlib); nenhum arquivo de
figura externo é importado como artefato de análise.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from wp1a.data.schema import FEATURE_COLUMNS

sns.set_theme(style="whitegrid", context="talk")


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return path


def plot_class_distribution(dist: pd.DataFrame, figures_dir: Path) -> dict[str, Path]:
    figures_dir = Path(figures_dir)
    out: dict[str, Path] = {}

    fig, ax = plt.subplots(figsize=(12, 5))
    colors = ["#2a9d8f" if r == "normal" else "#264653" for r in dist["regime"]]
    ax.bar(dist["class_label"].astype(str), dist["n_samples"], color=colors)
    ax.set_xlabel("class_label")
    ax.set_ylabel("n_samples")
    ax.set_title("A2 — Distribuição de amostras por classe")
    out["class_samples"] = _save(fig, figures_dir / "A2_class_distribution_samples.png")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(dist["class_label"].astype(str), dist["n_runs"], color=colors)
    ax.set_xlabel("class_label")
    ax.set_ylabel("n_runs")
    ax.set_title("A2 — Distribuição de execuções (run) por classe")
    out["class_runs"] = _save(fig, figures_dir / "A2_class_distribution_runs.png")
    return out


def plot_variability(variability: pd.DataFrame, figures_dir: Path) -> dict[str, Path]:
    figures_dir = Path(figures_dir)
    # Show lowest and highest variance variables for readability.
    low = variability.nsmallest(15, "variance")
    high = variability.nlargest(15, "variance").sort_values("variance")

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), sharey=False)
    axes[0].barh(low["variable"], low["variance"], color="#457b9d")
    axes[0].set_title("15 menores variâncias")
    axes[0].set_xlabel("variance")
    axes[1].barh(high["variable"], high["variance"], color="#e76f51")
    axes[1].set_title("15 maiores variâncias")
    axes[1].set_xlabel("variance")
    fig.suptitle("A2 — Variabilidade das variáveis de processo")
    fig.tight_layout()
    path = _save(fig, figures_dir / "A2_variable_variability.png")
    return {"variability": path}


def plot_correlation_heatmap(corr: pd.DataFrame, figures_dir: Path) -> dict[str, Path]:
    figures_dir = Path(figures_dir)
    mat = corr.set_index("variable").loc[list(FEATURE_COLUMNS), list(FEATURE_COLUMNS)]
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        mat,
        ax=ax,
        cmap="vlag",
        center=0.0,
        xticklabels=False,
        yticklabels=False,
        cbar_kws={"label": "Pearson r"},
    )
    ax.set_title("A2 — Matriz de correlação (52 variáveis)")
    path = _save(fig, figures_dir / "A2_correlation_heatmap.png")
    return {"correlation": path}


def plot_pca(proj: pd.DataFrame, variance: pd.DataFrame, figures_dir: Path) -> dict[str, Path]:
    figures_dir = Path(figures_dir)
    out: dict[str, Path] = {}

    # Subsample for readability while remaining deterministic.
    rng = np.random.default_rng(0)
    if len(proj) > 8000:
        idx = rng.choice(len(proj), size=8000, replace=False)
        plot_df = proj.iloc[idx]
    else:
        plot_df = proj

    fig, ax = plt.subplots(figsize=(9, 7))
    for regime, color in (("normal", "#2a9d8f"), ("fault", "#264653")):
        part = plot_df.loc[plot_df["regime"] == regime]
        ax.scatter(
            part["PC1"],
            part["PC2"],
            s=8,
            alpha=0.35,
            c=color,
            label=regime,
            linewidths=0,
        )
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("A2 — PCA (PC1 × PC2) por regime normal/falha")
    ax.legend(markerscale=2)
    out["pca_regime"] = _save(fig, figures_dir / "A2_pca_normal_vs_fault.png")

    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(
        plot_df["PC1"],
        plot_df["PC2"],
        c=plot_df["class_label"],
        s=8,
        alpha=0.4,
        cmap="tab20",
        linewidths=0,
    )
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("class_label")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("A2 — PCA (PC1 × PC2) colorido por classe")
    out["pca_class"] = _save(fig, figures_dir / "A2_pca_by_class.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(variance["component"], variance["explained_variance_ratio"], color="#1d3557")
    ax.plot(
        variance["component"],
        variance["cumulative_explained_variance_ratio"],
        color="#e63946",
        marker="o",
        label="acumulado",
    )
    ax.set_ylabel("explained variance ratio")
    ax.set_title("A2 — Variância explicada por componente PCA")
    ax.legend()
    ax.tick_params(axis="x", rotation=45)
    out["pca_variance"] = _save(fig, figures_dir / "A2_pca_explained_variance.png")
    return out


def plot_normal_vs_fault(nvf: pd.DataFrame, figures_dir: Path) -> dict[str, Path]:
    figures_dir = Path(figures_dir)
    top = nvf.head(20).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#e76f51" if v >= 0 else "#457b9d" for v in top["standardized_mean_diff_vs_normal"]]
    ax.barh(top["variable"], top["standardized_mean_diff_vs_normal"], color=colors)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel("standardized mean diff (fault − normal) / std_normal")
    ax.set_title("A2 — Deslocamento de média: falha agregada vs normal (top 20 |SMD|)")
    path = _save(fig, figures_dir / "A2_normal_vs_fault_mean_shift.png")
    return {"normal_vs_fault": path}


def generate_all_figures(tables: dict[str, pd.DataFrame], figures_dir: Path) -> dict[str, Path]:
    figures_dir = Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}
    out.update(plot_class_distribution(tables["class_distribution"], figures_dir))
    out.update(plot_variability(tables["variability"], figures_dir))
    out.update(plot_correlation_heatmap(tables["correlation"], figures_dir))
    out.update(plot_pca(tables["pca_projection"], tables["pca_variance"], figures_dir))
    out.update(plot_normal_vs_fault(tables["normal_vs_fault"], figures_dir))
    return out
