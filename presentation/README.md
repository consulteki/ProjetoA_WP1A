# presentation/ — Entrega A9

Síntese do relatório técnico (A7) e do manuscrito (A8): problema, hipóteses, protocolo, resultados, ameaças/riscos aceitos e conclusões.

Conforme `docs/specs/SPEC-009-publication.md` §3.3 e SPEC-000 §11.1 (A9 = PDF/PPTX).

## Arquivos

| Arquivo | Descrição |
|---|---|
| `A9_presentation.tex` | Fonte Beamer (16:9) |
| `A9_presentation.pdf` | PDF compilado |

Experimento oficial: `exp-a4-v2`. Figuras: `../article/figures/A6_exp-a4-v2__*`.

## Compilar

```bash
cd presentation
xelatex A9_presentation.tex
xelatex A9_presentation.tex
```

Requer XeLaTeX, Beamer e fontes DejaVu.
