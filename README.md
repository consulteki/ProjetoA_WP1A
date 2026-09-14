# WP1A — Benchmark Reproduzível de Métodos Clássicos de ML para Diagnóstico de Falhas (TEP)

Subprojeto **WP1A** da disciplina **MEI0028 — Modelagem e Simulação** (Programa de Pós-Graduação, Pontifícia Universidade Católica de Goiás), Grupo A, professor responsável Clarimar José Coelho.

> Dado um conjunto de dados multivariado proveniente da simulação do Tennessee Eastman Process (TEP), qual método clássico de aprendizado de máquina apresenta o melhor compromisso entre capacidade de classificação, equilíbrio entre classes, custo computacional, estabilidade e interpretabilidade no diagnóstico de falhas industriais?

Este repositório contém a especificação, os guardas metodológicos executáveis, os testes de rejeição e a estrutura de artefatos do benchmark. **Nenhum pipeline de ML foi implementado ainda** — o que existe hoje é a governança (specs, ADRs, skills, regras de agente) e a suíte de testes que qualquer implementação futura precisa satisfazer.

## Comece por aqui

1. Leia `AGENTS.md` — é a constituição obrigatória para qualquer pessoa ou agente que for trabalhar neste repositório (regras metodológicas, anti-vazamento, workflow, testes, Git, documentação, experimentos, proibições).
2. Leia `docs/specs/SPEC-000-master.md` — especificação mestra (objetivo, escopo, questões de pesquisa, hipóteses, dataset, unidade experimental, pipeline, modelos, métricas, estatística, outputs, invariantes, critérios de aceite, reprodutibilidade, ameaças à validade).
3. Consulte `docs/adr/` para entender *por que* cada decisão estrutural foi tomada (unidade experimental, isolamento do teste, reprodutibilidade, dataset canônico, configuração de experimento, seleção de modelos, avaliação multicritério, metodologia estatística).
4. Consulte `.agents/skills/` para o procedimento operacional de cada etapa do pipeline.
5. Rode `make test` — a suíte de testes de rejeição (`tests/unit/`, `tests/methodology/`) já existe e deve continuar passando à medida que o pipeline for implementado.

## Origem

Todo o conteúdo normativo deste repositório deriva, em cadeia de autoridade, de:

```
docs/project/WP1A_SOURCE.pdf  (documento original do subprojeto)
        │
        ▼
docs/project/requirements.md  (requisitos verificáveis)
        │
        ▼
docs/specs/SPEC-000-master.md (especificação mestra)
        │
        ▼
docs/specs/SPEC-001..009.md   (especificações por etapa)
docs/adr/ADR-001..008.md      (decisões estruturantes)
        │
        ▼
AGENTS.md                     (regras operacionais para agentes)
.agents/skills/*/SKILL.md     (procedimento por etapa)
```

Em caso de conflito entre documentos, o documento mais próximo do topo desta cadeia prevalece (ver `AGENTS.md` §0).

## Estrutura do repositório

```
wp1a-tep-benchmark/
│
├── README.md                 este arquivo
├── LICENSE                   placeholder — decisão de licenciamento pendente
├── .gitignore
├── pyproject.toml            metadados do projeto + configuração do pytest
├── requirements.txt
├── Makefile                  atalhos (make test, make audit, ...)
│
├── AGENTS.md                 constituição obrigatória para agentes
│
├── docs/
│   ├── project/               conteúdo de origem (WP1A_SOURCE.pdf, questões, hipóteses, metodologia, requisitos verificáveis)
│   ├── specs/                 SPEC-000 (mestra) + SPEC-001..009 (por etapa)
│   ├── adr/                   decisões estruturantes (ADR-001..008)
│   └── protocols/              checklists operacionais (experimental, reprodutibilidade)
│
├── .agents/
│   ├── skills/                 procedimento operacional de cada etapa (10 skills)
│   └── prompts/                perfis de agente (auditor, reviewer, experimenter)
│
├── configs/                   templates de configuração (experiment, models, paths, seeds)
├── data/{raw,interim,processed}/
├── notebooks/                 esqueletos (01_data_audit, 02_eda, 03_results_analysis)
│
├── src/wp1a/                  guardas metodológicos executáveis (NÃO é o pipeline de ML)
│   ├── errors.py               hierarquia de exceções de validação
│   ├── data/                   schema.py, class_consistency.py
│   ├── splitting/               run_leakage.py, reproducibility.py
│   ├── tracking/                isolation_guard.py, metadata_guard.py
│   └── preprocessing/ models/ evaluation/ statistics/ visualization/   (stubs — a implementar)
│
├── tests/
│   ├── unit/                   schema, consistência de classes
│   ├── methodology/             run leakage, isolamento de teste, reprodutibilidade de split, metadata
│   └── integration/             (a preencher quando o pipeline existir)
│
├── models/                    modelos treinados (gerado — não versionado)
├── results/{raw,metrics,predictions,tables,figures,metadata}/  (gerado — não versionado em parte)
├── reports/{audit,technical}/
├── article/{manuscript,figures,tables}/
└── presentation/
```

## Estado atual

| Área | Estado |
|---|---|
| Governança (specs, ADRs, skills, AGENTS.md) | ✅ Completa |
| Guardas de validação (`src/wp1a/`) | ✅ Implementados (schema, run leakage, isolamento de teste, consistência de classes, reprodutibilidade de split, completude de metadados) |
| Testes de rejeição (`tests/unit/`, `tests/methodology/`) | ✅ Implementados e passando |
| Etapa 1 — Auditoria (SPEC-001 / Entrega A1) | ✅ Implementada (`make audit` → `reports/audit/`, `results/metadata/audit_counts.json`) |
| Dataset canônico (SPEC-002) | ✅ Implementado (`make canonical-dataset` → `data/processed/canonical_dataset_registry.json`, `tep-canonical-v1.csv.gz`) |
| Etapa 2 — EDA (SPEC-003 / Entrega A2) | ✅ Implementada (`make eda` → `reports/eda/`, `results/figures/A2_*.png`, `results/tables/A2_*.csv`) |
| Etapa 3 — Divisão por run (SPEC-004 / Entrega A3) | ✅ Implementada (`make split` → `data/processed/split_manifest_v1.json`, `train_runs.csv`, `validation_runs.csv`, `test_runs.csv`) |
| Etapa 4 — Pré-processamento (SPEC-005) | ✅ Implementada (`make preprocess` → `preprocessor_v1_*.csv.gz`, `preprocessor_v1_scaler_params.json`; fit só no treino) |
| Pipeline restante (treino → avaliação) | ⛔ Não implementado — ver `.agents/skills/` e `docs/specs/SPEC-006..007.md` |
| Análise estatística, figuras, manuscrito | ⛔ Não implementado — ver `docs/specs/SPEC-008.md`, `SPEC-009.md` |

## Como rodar os testes

```bash
pip install -r requirements.txt
make test              # toda a suite
make test-unit         # apenas tests/unit
make test-methodology  # apenas tests/methodology (anti-leakage, isolamento de teste, reprodutibilidade, metadata)
```

## Regras não negociáveis (resumo — ver AGENTS.md para o texto completo)

- A unidade de divisão dos dados é a **execução (`run`)**, nunca a amostra individual.
- O conjunto de teste é consultado **uma única vez**, após o congelamento da configuração de cada modelo.
- Os 6 modelos obrigatórios (Regressão Logística, Árvore de Decisão, Random Forest, Gradient Boosting, SVM, XGBoost) usam **o mesmo protocolo**.
- Nenhuma conclusão de "melhor modelo" pode se basear em métrica única.
- Toda execução experimental é rastreável (semente, versões, hiperparâmetros, manifesto de divisão).
