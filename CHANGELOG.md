# Changelog

## [1.0.0] — 2026-09-14

Primeira release científica do benchmark WP1A (Tennessee Eastman Process).

### Escopo
- Experimento oficial congelado: **`exp-a4-v2`**
- Dataset: `tep-canonical-v1` · manifesto A3 · `preprocessor_v1`
- Entregas **A1–A9** cobertas (auditoria → apresentação)
- Review final: **APPROVE WITH ACCEPTED RISKS** (AR-1–AR-5)

### Pipeline
- SPEC-001…005: auditoria, canônico, EDA, split por `run`, pré-processamento
- SPEC-006 / A4: treino dos 6 modelos (`ExperimentRunner`)
- SPEC-007 / A5: métricas MET-01…12 + QP3
- SPEC-008: Friedman + Wilcoxon (unidade = `run_id`, n=11)
- SPEC-009 / A6–A9: figuras, relatório técnico, manuscrito, slides

### Como verificar
```bash
make reproduce   # pytest + evaluate + statistics + figures (sem retreino)
```

### Não incluído nesta tag
- Binários em `models/` (gitignored; regenerar com `make train`)
- Tuning ampliado SPEC-006A (não executado)
- Predições de experimentos parciais (`exp-a4-v1`, dry-run)

### Riscos aceitos (documentados em A7/A8)
AR-1 val∩teste classes disjuntas · AR-2 scorer=acurácia · AR-3 grids desiguais · AR-4 macro C=21 · AR-5 semente única / n=11
