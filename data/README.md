# data/

- `raw/` — arquivos de origem do TEP, exatamente como auditados em `reports/audit/` (Entrega A1). Nunca editados manualmente.
  - Proveniência e URL de download: `data/raw/SOURCE.txt`.
  - Os `.dat` Braatz (`d00.dat`…`d21_te.dat`) não são versionados; repô-los antes de `make audit`.
  - **Imutáveis** após a auditoria: `make canonical-dataset` revalida os SHA-256 de A1 e falha se algum arquivo bruto tiver sido alterado.
- `interim/` — saídas intermediárias de transformação que ainda não são o dataset canônico nem um conjunto pronto para treino (ex.: extrações parciais, formatos convertidos). **Não canônico.**
- `processed/` — dataset canônico registrado (`docs/specs/SPEC-002-canonical-dataset.md`):
  - `tep-canonical-v1.csv.gz` — tabela canônica (gerada; não versionada por volume).
  - `canonical_dataset_registry.json` — registro versionado (identificador, arquivos, tratamentos, checksums).
  - `NON_CANONICAL.md` — política do que não pode alimentar A5–A9.
  - Também receberá conjuntos pré-processados (`SPEC-005`).
  - Entrega A3: `split_manifest_v1.json`, `train_runs.csv`, `validation_runs.csv`, `test_runs.csv`.

Nenhum arquivo grande aqui é versionado por padrão (ver `.gitignore`); os `.gitkeep` mantêm a estrutura de pastas no controle de versão. Exceções versionáveis: registro canônico, `NON_CANONICAL.md` e manifesto A3 (`split_manifest_v1.json` + CSVs de runs).
