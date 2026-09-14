"""Análise exploratória do dataset canônico (SPEC-003 / Entrega A2).

Caracterização descritiva apenas. Nenhuma saída desta etapa altera o
protocolo experimental (splits, modelos, métricas, hiperparâmetros).
Estatísticas aqui NÃO podem ser reutilizadas como parâmetros de
``fit`` de pré-processamento (isso é SPEC-005, apenas no treino).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from wp1a.data.canonical import (
    DATASET_VERSION,
    load_canonical_dataframe,
    load_canonical_registry,
)
from wp1a.data.schema import (
    CLASS_LABEL_COLUMN,
    FEATURE_COLUMNS,
    RUN_ID_COLUMN,
    validate_canonical_schema,
)
from wp1a.errors import CanonicalDatasetError

PROTOCOL_DISCLAIMER = (
    "Esta EDA é estritamente descritiva. Nenhuma interpretação abaixo "
    "modifica o protocolo experimental (unidade = run, isolamento do teste, "
    "os 6 modelos obrigatórios, o conjunto de métricas, nem a ordem do pipeline). "
    "Sugestões de pré-processamento, se houver, são hipóteses a avaliar em "
    "SPEC-005 e não decisões congeladas nesta etapa."
)


@dataclass(frozen=True)
class EdaArtifacts:
    tables: dict[str, Path]
    figures: dict[str, Path]
    report: Path
    observations: Path
    metadata: Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_canonical_for_eda(processed_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load and validate the registered canonical dataset only."""
    processed_dir = Path(processed_dir)
    registry = load_canonical_registry(processed_dir)
    if registry.get("dataset_version") != DATASET_VERSION:
        raise CanonicalDatasetError(
            f"EDA requires dataset_version={DATASET_VERSION!r}, "
            f"got {registry.get('dataset_version')!r}"
        )
    if registry.get("status") != "canonical":
        raise CanonicalDatasetError("registry status must be 'canonical'")
    df = load_canonical_dataframe(processed_dir)
    validate_canonical_schema(df)
    return df, registry


def descriptive_global(df: pd.DataFrame) -> pd.DataFrame:
    x = df.loc[:, list(FEATURE_COLUMNS)]
    desc = x.describe(percentiles=[0.25, 0.5, 0.75]).T
    desc = desc.rename(
        columns={
            "mean": "mean",
            "std": "std",
            "min": "min",
            "25%": "q25",
            "50%": "q50",
            "75%": "q75",
            "max": "max",
            "count": "count",
        }
    )
    desc.index.name = "variable"
    return desc.reset_index()


def descriptive_by_class(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for class_label, group in df.groupby(CLASS_LABEL_COLUMN, sort=True):
        x = group.loc[:, list(FEATURE_COLUMNS)]
        means = x.mean()
        stds = x.std(ddof=1)
        mins = x.min()
        maxs = x.max()
        for var in FEATURE_COLUMNS:
            rows.append(
                {
                    "class_label": int(class_label),
                    "variable": var,
                    "n_samples": int(len(group)),
                    "mean": float(means[var]),
                    "std": float(stds[var]) if pd.notna(stds[var]) else 0.0,
                    "min": float(mins[var]),
                    "max": float(maxs[var]),
                }
            )
    return pd.DataFrame(rows)


def class_distribution(df: pd.DataFrame) -> pd.DataFrame:
    sample_counts = df.groupby(CLASS_LABEL_COLUMN).size().rename("n_samples")
    run_counts = (
        df.groupby(CLASS_LABEL_COLUMN)[RUN_ID_COLUMN].nunique().rename("n_runs")
    )
    out = pd.concat([sample_counts, run_counts], axis=1).reset_index()
    out["class_label"] = out["class_label"].astype(int)
    out["regime"] = np.where(out["class_label"] == 0, "normal", "fault")
    out["sample_fraction"] = out["n_samples"] / out["n_samples"].sum()
    return out.sort_values("class_label").reset_index(drop=True)


def variability_table(df: pd.DataFrame) -> pd.DataFrame:
    x = df.loc[:, list(FEATURE_COLUMNS)]
    mean = x.mean()
    std = x.std(ddof=1)
    var = x.var(ddof=1)
    # CV undefined/unstable near zero mean — report abs(mean) guard.
    cv = std / mean.replace(0.0, np.nan).abs()
    out = pd.DataFrame(
        {
            "variable": list(FEATURE_COLUMNS),
            "variance": var.to_numpy(),
            "std": std.to_numpy(),
            "mean": mean.to_numpy(),
            "cv_abs": cv.to_numpy(),
        }
    )
    out["nearly_constant"] = out["variance"] < 1e-12
    return out.sort_values("variance", ascending=True).reset_index(drop=True)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    corr = df.loc[:, list(FEATURE_COLUMNS)].corr(method="pearson")
    corr.index.name = "variable"
    return corr.reset_index()


def top_correlated_pairs(corr: pd.DataFrame, *, top_n: int = 30) -> pd.DataFrame:
    mat = corr.set_index("variable")
    pairs: list[dict[str, Any]] = []
    cols = list(mat.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            pairs.append({"variable_a": a, "variable_b": b, "pearson_r": float(mat.loc[a, b])})
    out = pd.DataFrame(pairs)
    out["abs_r"] = out["pearson_r"].abs()
    return out.sort_values("abs_r", ascending=False).head(top_n).reset_index(drop=True)


def pca_analysis(
    df: pd.DataFrame, *, n_components: int = 10, random_state: int = 0
) -> tuple[pd.DataFrame, pd.DataFrame, PCA, StandardScaler]:
    """PCA on standardized features (exploratory only; scaler not for SPEC-005)."""
    x = df.loc[:, list(FEATURE_COLUMNS)].to_numpy(dtype=np.float64)
    scaler = StandardScaler()
    x_std = scaler.fit_transform(x)
    n_components = min(n_components, x_std.shape[1], x_std.shape[0])
    pca = PCA(n_components=n_components, random_state=random_state)
    scores = pca.fit_transform(x_std)

    variance = pd.DataFrame(
        {
            "component": [f"PC{i+1}" for i in range(n_components)],
            "explained_variance_ratio": pca.explained_variance_ratio_,
            "cumulative_explained_variance_ratio": np.cumsum(pca.explained_variance_ratio_),
        }
    )
    proj = pd.DataFrame(
        {
            "PC1": scores[:, 0],
            "PC2": scores[:, 1] if n_components > 1 else 0.0,
            CLASS_LABEL_COLUMN: df[CLASS_LABEL_COLUMN].to_numpy(),
            RUN_ID_COLUMN: df[RUN_ID_COLUMN].to_numpy(),
            "regime": np.where(df[CLASS_LABEL_COLUMN].to_numpy() == 0, "normal", "fault"),
        }
    )
    return variance, proj, pca, scaler


def normal_vs_fault_comparison(df: pd.DataFrame) -> pd.DataFrame:
    normal = df.loc[df[CLASS_LABEL_COLUMN] == 0, list(FEATURE_COLUMNS)]
    fault = df.loc[df[CLASS_LABEL_COLUMN] != 0, list(FEATURE_COLUMNS)]
    if normal.empty or fault.empty:
        raise CanonicalDatasetError("EDA requires both normal (0) and fault classes")

    n_mean, n_std = normal.mean(), normal.std(ddof=1)
    f_mean, f_std = fault.mean(), fault.std(ddof=1)
    # Standardized mean difference using pooled-ish normal std as reference scale.
    denom = n_std.replace(0.0, np.nan)
    smd = (f_mean - n_mean) / denom
    var_ratio = (f_std**2) / (n_std**2).replace(0.0, np.nan)

    return pd.DataFrame(
        {
            "variable": list(FEATURE_COLUMNS),
            "mean_normal": n_mean.to_numpy(),
            "mean_fault": f_mean.to_numpy(),
            "std_normal": n_std.to_numpy(),
            "std_fault": f_std.to_numpy(),
            "mean_diff": (f_mean - n_mean).to_numpy(),
            "standardized_mean_diff_vs_normal": smd.to_numpy(),
            "variance_ratio_fault_over_normal": var_ratio.to_numpy(),
        }
    ).sort_values(
        "standardized_mean_diff_vs_normal",
        key=lambda s: s.abs(),
        ascending=False,
    ).reset_index(drop=True)


def compute_eda_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    corr = correlation_matrix(df)
    variance, proj, _, _ = pca_analysis(df)
    return {
        "descriptive_global": descriptive_global(df),
        "descriptive_by_class": descriptive_by_class(df),
        "class_distribution": class_distribution(df),
        "variability": variability_table(df),
        "correlation": corr,
        "correlation_top_pairs": top_correlated_pairs(corr),
        "pca_variance": variance,
        "pca_projection": proj,
        "normal_vs_fault": normal_vs_fault_comparison(df),
    }


def build_observations(tables: dict[str, pd.DataFrame], registry: dict[str, Any]) -> str:
    """Qualitative notes that must not alter the experimental protocol."""
    dist = tables["class_distribution"]
    var = tables["variability"]
    top = tables["correlation_top_pairs"].head(5)
    pca = tables["pca_variance"]
    nvf = tables["normal_vs_fault"].head(5)

    n_samples = int(dist["n_samples"].sum())
    n_runs = int(dist["n_runs"].sum())
    imbalance = dist.sort_values("n_samples", ascending=False)

    nearly_const = var.loc[var["nearly_constant"], "variable"].tolist()
    high_cv = var.sort_values("cv_abs", ascending=False).head(5)

    lines = [
        "# A2 — Observações da análise exploratória",
        "",
        f"- Dataset: `{registry.get('dataset_version')}`",
        f"- Gerado em: `{_utc_now()}`",
        "",
        "## Disclaimer de protocolo",
        "",
        PROTOCOL_DISCLAIMER,
        "",
        "## Achados descritivos (não prescritivos)",
        "",
        "### Distribuição de classes",
        "",
        f"- Total: {n_samples} amostras em {n_runs} execuções (`run_id`), 21 classes.",
        f"- Amplitude de amostras/classe: {int(dist['n_samples'].min())}–{int(dist['n_samples'].max())}.",
        f"- Classes com mais amostras: "
        + ", ".join(
            f"{int(r.class_label)} ({int(r.n_samples)})"
            for r in imbalance.head(3).itertuples()
        )
        + ".",
        "- Desbalanceamento existe e deve ser considerado nas **métricas** já "
        "exigidas pelo protocolo (F1 macro, balanced accuracy, MCC) — sem "
        "alterar o conjunto de modelos ou a unidade experimental.",
        "",
        "### Variabilidade",
        "",
        (
            f"- Variáveis com variância ~0: {nearly_const if nearly_const else 'nenhuma'}."
        ),
        "- Maiores |CV| (escalas heterogêneas entre variáveis): "
        + ", ".join(f"{r.variable}={r.cv_abs:.3g}" for r in high_cv.itertuples())
        + ".",
        "- Escalas distintas entre variáveis são um **indício** a ser tratado, "
        "se necessário, apenas em SPEC-005 (padronização ajustada no treino), "
        "não uma mudança de protocolo nesta etapa.",
        "",
        "### Correlações",
        "",
        "- Pares com maior |r| de Pearson:",
    ]
    for r in top.itertuples():
        lines.append(
            f"  - `{r.variable_a}` × `{r.variable_b}`: r={r.pearson_r:.3f}"
        )
    lines += [
        "- Correlações altas são descritivas da redundância linear; "
        "não autorizam seleção de features com base em teste nem alteração "
        "dos 6 modelos obrigatórios.",
        "",
        "### PCA",
        "",
        f"- Variância explicada por PC1–PC2: "
        f"{100 * float(pca.loc[0, 'explained_variance_ratio']):.1f}% + "
        f"{100 * float(pca.loc[1, 'explained_variance_ratio']):.1f}% "
        f"(acumulado PC1–PC2 = "
        f"{100 * float(pca.loc[1, 'cumulative_explained_variance_ratio']):.1f}%).",
        "- A projeção é inspeção visual de separabilidade; sobreposições entre "
        "classes, se existirem, serão avaliadas quantitativamente em SPEC-007 "
        "(QP3), não resolvidas aqui por mudança de protocolo.",
        "",
        "### Normal vs falha",
        "",
        "- Variáveis com maior |diferença padronizada de média| (falha agregada vs normal):",
    ]
    for r in nvf.itertuples():
        lines.append(
            f"  - `{r.variable}`: SMD={r.standardized_mean_diff_vs_normal:.3f}"
        )
    lines += [
        "",
        "## O que esta etapa explicitamente NÃO faz",
        "",
        "- Não escolhe hiperparâmetros.",
        "- Não define o manifesto de divisão (SPEC-004).",
        "- Não congela o pipeline de pré-processamento (SPEC-005).",
        "- Não remove classes, variáveis ou modelos do benchmark.",
        "- Não consulta um holdout de teste WP1A (ainda inexistente nesta etapa).",
        "",
    ]
    return "\n".join(lines)
