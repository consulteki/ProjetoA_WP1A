# Protocolo Experimental — WP1A

Síntese operacional (checklist) de `docs/adr/ADR-001-run-as-group-unit.md` e `docs/adr/ADR-002-test-set-isolation.md`. Em caso de conflito, as ADRs e `docs/specs/SPEC-000-master.md` prevalecem sobre este checklist.

## Antes de dividir os dados

- [ ] O dataset canônico está registrado (`docs/specs/SPEC-002-canonical-dataset.md`).
- [ ] A lista de `run_id` por amostra está íntegra (confirmada em `reports/audit/`).

## Ao dividir os dados (SPEC-004)

- [ ] A divisão agrupa por `run_id`, nunca por amostra/linha individual.
- [ ] Semente aleatória registrada.
- [ ] `check_run_disjoint` / `check_manifest_disjoint` executado e aprovado — interseção vazia entre treino/validação/teste.
- [ ] `assert_split_reproducible` executado contra a função de split real — duas chamadas com a mesma semente produzem o mesmo manifesto.
- [ ] Manifesto de divisão (A3) versionado em `data/processed/`.

## Ao pré-processar (SPEC-005)

- [ ] Todo `fit()` de transformação é chamado apenas com `partition="train"`.
- [ ] Nenhum objeto de transformação é reajustado (`re-fit`) para validação/teste.
- [ ] Os mesmos parâmetros de transformação são aplicados às três partições.

## Ao treinar e selecionar hiperparâmetros (SPEC-006)

- [ ] Seleção de hiperparâmetros usa apenas treino/validação — `assert_test_not_used_for_selection` aprovado.
- [ ] Configuração final é explicitamente congelada (`ExperimentState.freeze()`) antes de qualquer acesso ao teste.
- [ ] O teste é consultado exatamente uma vez (`ExperimentState.access_test()`) por configuração congelada.
- [ ] Se um problema for identificado após consultar o teste, um **novo** identificador de experimento é aberto — a configuração já avaliada não é reajustada.
- [ ] Os 6 modelos usam o mesmo manifesto de divisão e o mesmo pipeline de pré-processamento.

## Ao avaliar (SPEC-007)

- [ ] Toda classe avaliada apareceu no treino (`validate_train_covers_eval_classes` aprovado).
- [ ] Todas as métricas obrigatórias (MET-01 a MET-12) foram calculadas para os 6 modelos.
- [ ] Nenhuma conclusão de "melhor modelo" se baseia em métrica única.

## Antes de qualquer merge/entrega

- [ ] `pytest` (toda a suíte, incluindo `tests/methodology/`) passa sem falhas.
- [ ] Nenhuma das proibições de `AGENTS.md` §8 foi violada.
