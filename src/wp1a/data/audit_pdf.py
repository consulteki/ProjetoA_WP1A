"""Gera um PDF textual da Entrega A1 a partir do relatório Markdown/CSV."""

from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt


def write_audit_pdf(markdown_path: Path, pdf_path: Path, *, max_chars_per_line: int = 95) -> Path:
    """Render a simple multipage PDF from the A1 markdown report."""
    text = Path(markdown_path).read_text(encoding="utf-8")
    wrapped: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            wrapped.append("")
            continue
        while len(line) > max_chars_per_line:
            split_at = line.rfind(" ", 0, max_chars_per_line)
            if split_at < 40:
                split_at = max_chars_per_line
            wrapped.append(line[:split_at])
            line = line[split_at:].lstrip()
        wrapped.append(line)

    lines_per_page = 52
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    with PdfPages(pdf_path) as pdf:
        for start in range(0, max(len(wrapped), 1), lines_per_page):
            chunk = wrapped[start : start + lines_per_page]
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis("off")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            y = 0.98
            for line in chunk:
                ax.text(
                    0.02,
                    y,
                    line,
                    family="monospace",
                    fontsize=8,
                    va="top",
                    ha="left",
                    transform=ax.transAxes,
                )
                y -= 0.018
            pdf.savefig(fig)
            plt.close(fig)

    return pdf_path
