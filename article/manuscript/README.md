# Manuscrito A8 — instruções de compilação

**Entrega editável (preferencial):** `A8_manuscript_exp-a4-v2.docx`  
**Fonte Markdown:** `A8_manuscript_exp-a4-v2.md`  
**LaTeX legado:** `manuscript.tex` + `references.bib`  
**Figuras:** `../figures/A6_exp-a4-v2__*.png`  
**Tabelas-fonte:** `../tables/A6_exp-a4-v2__*`

## Estrutura obrigatória (SPEC-000 §11.4)

1. Introdução  
2. Fundamentação sobre diagnóstico de falhas e TEP  
3. Trabalhos relacionados  
4. Materiais e métodos  
5. Protocolo reprodutível  
6. Resultados (QP1–QP5 + H1–H4)  
7. Discussão  
8. Ameaças à validade (interna, estatística, constructo, externa)  
9. Conclusões  
10. Referências  

## Gerar DOCX (editável)

```bash
cd article/manuscript
pandoc A8_manuscript_exp-a4-v2.md \
  -o A8_manuscript_exp-a4-v2.docx \
  --resource-path=.:../figures \
  -f markdown -t docx
```

## Compilar PDF (LaTeX legado)

```bash
cd article/manuscript
xelatex manuscript.tex
biber manuscript
xelatex manuscript.tex
xelatex manuscript.tex
```

Requer: Pandoc (DOCX) ou XeLaTeX + Biber + fontes DejaVu (PDF).

Experimento oficial: `exp-a4-v2`. Relatório técnico expandido: `reports/technical/A7_technical_report.md`.
