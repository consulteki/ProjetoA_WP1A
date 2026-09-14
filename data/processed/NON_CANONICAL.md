# Material não canônico

A única versão canônica vigente é **`tep-canonical-v1`**, registrada em `canonical_dataset_registry.json`.

## Excluído do canônico (por decisão SPEC-002)

- `d21.dat` — fault_id=21 excluded to satisfy DS-03 (21 classes, labels 0..20)
- `d21_te.dat` — fault_id=21 excluded to satisfy DS-03 (21 classes, labels 0..20)

## Política

Qualquer subconjunto, amostra reduzida ou versão alternativa do TEP que não seja exatamente este dataset_version é NÃO CANÔNICA e não pode alimentar entregas A5–A9. Alterações exigem nova auditoria (SPEC-001) e emenda a ADR-004.

Fixtures sintéticas em `tests/` e qualquer CSV/Parquet ad hoc em `data/interim/` são **não canônicos**.
