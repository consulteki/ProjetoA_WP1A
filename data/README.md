# data/

- `raw/` — arquivos de origem do TEP, exatamente como auditados em `reports/audit/` (Entrega A1). Nunca editados manualmente.
- `interim/` — saídas intermediárias de transformação que ainda não são o dataset canônico nem um conjunto pronto para treino (ex.: extrações parciais, formatos convertidos).
- `processed/` — dataset canônico registrado (`docs/specs/SPEC-002-canonical-dataset.md`), manifestos de divisão (`docs/specs/SPEC-004-splitting.md`, Entrega A3) e conjuntos pré-processados (`docs/specs/SPEC-005-preprocessing.md`).

Nenhum arquivo grande aqui é versionado por padrão (ver `.gitignore`); os `.gitkeep` mantêm a estrutura de pastas no controle de versão.
