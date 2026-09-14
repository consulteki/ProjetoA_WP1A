.PHONY: setup test test-unit test-methodology lint audit canonical-dataset eda split preprocess dry-run train evaluate statistics figures report clean help

PYTHON ?= python3
PIP ?= pip

help:
	@echo "WP1A — alvos disponiveis:"
	@echo "  setup              instala dependencias (requirements.txt)"
	@echo "  test               roda toda a suite de testes (pytest)"
	@echo "  test-unit          roda apenas tests/unit"
	@echo "  test-methodology   roda apenas tests/methodology (anti-leakage etc.)"
	@echo "  audit              Etapa 1 - auditoria dos dados (.agents/skills/data-audit)"
	@echo "  canonical-dataset  registra o dataset canonico (.agents/skills/canonical-dataset)"
	@echo "  eda                Etapa 2 - analise exploratoria (.agents/skills/exploratory-analysis)"
	@echo "  split              Etapa 3 - divisao por run (.agents/skills/grouped-split)"
	@echo "  preprocess         Etapa 4 - pre-processamento (.agents/skills/preprocessing)"
	@echo "  dry-run            smoke ponta a ponta em fracao de runs (DRY-RUN; NAO cientifico)"
	@echo "  train              Etapa 5 - treinamento dos 6 modelos (.agents/skills/ml-training)"
	@echo "  evaluate           Etapa 6 - avaliacao final (.agents/skills/ml-evaluation)"
	@echo "  statistics         analise estatistica formal (.agents/skills/statistical-analysis)"
	@echo "  figures            tabelas/figuras do artigo (.agents/skills/scientific-figures)"
	@echo "  report             relatorio tecnico + manuscrito (.agents/skills/scientific-writing)"
	@echo "  clean              remove artefatos de cache (__pycache__, .pytest_cache)"

setup:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m pytest

test-unit:
	$(PYTHON) -m pytest tests/unit

test-methodology:
	$(PYTHON) -m pytest tests/methodology

# --- Etapas do pipeline -------------------------------------------------
# Cada alvo aponta para a skill/SPEC correspondente. SPEC-001..005 já
# estão implementadas; as demais permanecem conforme SPEC-006..009.
audit:
	$(PYTHON) -m wp1a.data.audit_cli

canonical-dataset:
	$(PYTHON) -m wp1a.data.canonical_cli

eda:
	$(PYTHON) -m wp1a.eda.cli

split:
	$(PYTHON) -m wp1a.splitting.cli

preprocess:
	$(PYTHON) -m wp1a.preprocessing.cli

# Smoke end-to-end on a controlled fraction of run_ids. Outputs are explicitly
# marked DRY-RUN and MUST NOT be treated as scientifically valid (not A4).
dry-run:
	$(PYTHON) -m wp1a.experiment.dry_run_cli \
		--run-fraction 0.2 \
		--max-runs-per-partition 3 \
		--output-dir results/dry_run

train:
	$(PYTHON) -m wp1a.training.cli \
		--experiment-config configs/experiments/exp-a4-v2.yaml

evaluate:
	@echo "TODO: nao implementado ainda."
	@echo "Siga docs/specs/SPEC-007-evaluation.md e .agents/skills/ml-evaluation/SKILL.md"

statistics:
	@echo "TODO: nao implementado ainda."
	@echo "Siga docs/specs/SPEC-008-statistics.md e .agents/skills/statistical-analysis/SKILL.md"

figures:
	@echo "TODO: nao implementado ainda."
	@echo "Siga docs/specs/SPEC-009-publication.md e .agents/skills/scientific-figures/SKILL.md"

report:
	@echo "TODO: nao implementado ainda."
	@echo "Siga docs/specs/SPEC-009-publication.md e .agents/skills/scientific-writing/SKILL.md"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
