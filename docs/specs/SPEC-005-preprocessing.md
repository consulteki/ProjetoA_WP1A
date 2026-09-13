# SPEC-005 — Pré-processamento

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §7.4; `docs/adr/ADR-002-test-set-isolation.md` |
| Skill correspondente | `.agents/skills/preprocessing/SKILL.md` |
| Etapa do pipeline | Etapa 4 |
| Guardas executáveis | `src/wp1a/tracking/isolation_guard.py` (`GuardedFitter`) |
| Testes de rejeição | `tests/methodology/test_test_set_isolation.py` (parte de fit) |

Em caso de conflito, prevalece `SPEC-000-master.md` e `ADR-002-test-set-isolation.md`.

## 1. Objetivo

Aplicar transformações dependentes dos dados (padronização, normalização, codificação) sem vazamento, garantindo que todo parâmetro de transformação seja estimado exclusivamente a partir do treino.

## 2. Escopo

Cobre exclusivamente transformações de dados aplicadas após a divisão (SPEC-004) e antes do treinamento (SPEC-006).

## 3. Requisitos

1. Objetos de transformação são ajustados (`fit`) exclusivamente sobre o conjunto de treinamento (INV-04).
2. Os mesmos objetos são aplicados (`transform`, sem reajuste) à validação e ao teste.
3. Nenhum `fit` pode ser chamado com dados marcados como partição de teste — verificado por `GuardedFitter.fit(X, partition=...)`, que rejeita `partition="test"`.
4. Transformações e seus parâmetros são versionados, associados ao manifesto de divisão (SPEC-004) e ao dataset canônico (SPEC-002).

## 4. Entradas e saídas

- **Entrada:** manifesto de divisão (A3, SPEC-004), dataset canônico (SPEC-002).
- **Saída:** conjuntos pré-processados de treino/validação/teste em `data/processed/`; objetos/parâmetros de transformação versionados.

## 5. Critérios de aceite

- Teste automatizado confirma que os parâmetros de transformação provêm exclusivamente do treino.
- `tests/methodology/test_test_set_isolation.py::test_rejects_fit_on_test_partition` passa contra a implementação real.

## 6. Rastreabilidade

`ADR-002-test-set-isolation.md` → `SPEC-000-master.md` §7.4, INV-04 → esta SPEC → `.agents/skills/preprocessing/SKILL.md` → `src/wp1a/tracking/isolation_guard.py`.
