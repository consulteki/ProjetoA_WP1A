# results/

Saídas versionadas do benchmark (Entrega A5 e insumos de A6), uma subpasta por tipo de artefato:

- `raw/` — resultados brutos por execução/experimento, antes de qualquer agregação.
- `metrics/` — métricas globais e por classe, por modelo (`docs/specs/SPEC-007-evaluation.md`).
- `predictions/` — predições em teste, por modelo/experimento.
- `tables/` — tabelas geradas (A2 EDA, hiperparâmetros, comparativas, estatísticas — `docs/specs/SPEC-003-eda.md`, `SPEC-008`).
- `figures/` — figuras geradas (A2 EDA; depois F1 macro/MCC, custo computacional, matrizes de confusão).
- `metadata/` — metadados de reprodutibilidade por experimento (`docs/protocols/reproducibility_protocol.md`), validados por `src/wp1a/tracking/metadata_guard.py`; inclui `eda_run.json` (SPEC-003).

Toda tabela/figura citada em `reports/` ou `article/` deve ser rastreável a um arquivo aqui (`AGENTS.md` DOC-R03).
