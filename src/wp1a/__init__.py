"""WP1A utilities: methodological guards plus pipeline stage modules.

Guardrails (must keep passing ``tests/``) live under ``data/``, ``splitting/``
and ``tracking/``. Pipeline stages are added incrementally per SPEC-001..009;
currently implemented:

- ``wp1a.data.audit`` / ``wp1a.data.audit_cli`` — Etapa 1 (Entrega A1)
- ``wp1a.data.canonical`` / ``wp1a.data.canonical_cli`` — SPEC-002 (dataset canônico)
- ``wp1a.eda`` / ``wp1a.eda.cli`` — Etapa 2 / SPEC-003 (Entrega A2)
- ``wp1a.splitting.grouped_split`` / ``wp1a.splitting.cli`` — Etapa 3 / SPEC-004 (Entrega A3)
- ``wp1a.preprocessing`` / ``wp1a.preprocessing.cli`` — Etapa 4 / SPEC-005 (fit só no treino)
- ``wp1a.experiment.ExperimentRunner`` — framework único de execução (pré–SPEC-006); todos os classificadores passam pelo mesmo runner
- ``wp1a.experiment.dry_run_cli`` — smoke ponta a ponta em fração de runs (**DRY-RUN**, não científico)
- ``wp1a.training.cli`` — Entrega A4 / SPEC-006 (6 modelos + proveniência completa)
- ``wp1a.evaluation.metrics`` — MET-01..MET-09 (fórmulas SPEC-000 §9.2)

Normative references:

- docs/specs/SPEC-000-master.md
- docs/adr/ADR-001-run-as-experimental-grouping-unit.md
- docs/adr/ADR-002-test-set-isolation.md
- docs/adr/ADR-003-reproducibility-requirements.md
- AGENTS.md
"""

__version__ = "0.1.0"
