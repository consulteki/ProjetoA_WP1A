# Testes de rejeição — pré-condição para o pipeline de ML (WP1A)

Estes testes existem **antes** de qualquer implementação do pipeline de ML (auditoria, EDA, split, pré-processamento, treinamento, avaliação — ver `skills/`). Eles fixam, em forma executável, seis modos de falha metodológica que o pipeline — quando implementado — DEVE ser incapaz de produzir sem que a suíte falhe.

Cada teste importa de `src/wp1a/`, um pacote de **validadores/guardas** (não o pipeline de ML em si) que implementa apenas os contratos necessários para que as rejeições sejam verificáveis agora. O pipeline real (skills `grouped-split`, `preprocessing`, `ml-training`, etc.) deverá depender destes mesmos validadores quando for implementado.

## Categorias cobertas (conforme solicitado)

| Categoria solicitada | Arquivo de teste | Validador exercido (`src/wp1a/`) | Fonte normativa |
|---|---|---|---|
| Run leakage | `test_run_leakage.py` | `run_leakage.check_run_disjoint`, `check_manifest_disjoint` | ADR-001, SPEC-000 INV-01/INV-02 |
| Uso de test durante fit | `test_test_set_isolation.py` | `isolation_guard.GuardedFitter`, `ExperimentState`, `assert_test_not_used_for_selection` | ADR-002, SPEC-000 INV-05 |
| Inconsistência de classes | `test_class_consistency.py` | `class_consistency.validate_class_consistency`, `validate_train_covers_eval_classes` | SPEC-000 DS-03 |
| Schema inválido | `test_schema_validation.py` | `schema.validate_schema` | SPEC-000 DS-01..DS-06 |
| Split não reproduzível | `test_split_reproducibility.py` | `reproducibility.assert_split_reproducible` | ADR-003, SPEC-000 REP-01/REP-02 |
| Metadata incompleta | `test_metadata_completeness.py` | `metadata_guard.validate_experiment_metadata` | ADR-003, ADR-005 |

`tests/conftest.py` fornece um dataset sintético (não são dados reais do TEP) com o schema canônico completo (52 variáveis, 21 classes, múltiplas execuções por classe), usado como base "válida" que cada teste corrompe deliberadamente para provar a rejeição.

## Como rodar

```bash
pytest
```

(configuração em `pytest.ini`: `pythonpath = src`, `testpaths = tests`).

Requer `pandas`, `numpy` e `pytest` instalados no ambiente Python usado. Estado atual: **59 testes, todos passando** (verificado nesta sessão).

## O que "passar" significa aqui

Para cada categoria, a suíte contém:

1. Um caso **válido** que não deve levantar exceção (prova de que o validador não rejeita dados corretos — evita falso positivo).
2. Um ou mais casos **inválidos**, cada um corrompendo exatamente uma condição, que devem levantar a exceção específica daquela categoria (`RunLeakageError`, `TestSetLeakageError`, `ClassConsistencyError`, `SchemaError`, `SplitReproducibilityError`, `IncompleteMetadataError` — todas em `src/wp1a/errors.py`).

Um teste que nunca falha por não conseguir provocar a condição de erro (ex.: um "leakage" que na verdade não vaza) é, por si, uma não conformidade desta suíte — cada teste de rejeição inclui, quando aplicável, uma asserção intermediária que confirma que o cenário de falha foi de fato reproduzido antes de checar a exceção.

## Próximos passos

Quando as skills `grouped-split`, `preprocessing`, `ml-training` etc. forem implementadas, seu código deve:

- chamar `run_leakage.check_run_disjoint`/`check_manifest_disjoint` logo após qualquer divisão de dados;
- envolver `fit()` de transformadores/modelos em `isolation_guard.GuardedFitter` (ou lógica equivalente) e usar `ExperimentState` para controlar o congelamento e o acesso único ao teste;
- chamar `class_consistency.validate_class_consistency` e `validate_train_covers_eval_classes` na auditoria e antes da avaliação final;
- chamar `schema.validate_schema` logo após carregar qualquer dataset;
- expor sua função de split real para ser verificada com `reproducibility.assert_split_reproducible`;
- montar os metadados de cada experimento no formato exigido por `metadata_guard.validate_experiment_metadata` antes de persistir qualquer resultado.

Nenhuma implementação de pipeline deve ser aceita (merge) sem que a suíte completa continue passando (AGENTS.md TEST-R07/TEST-R08).
