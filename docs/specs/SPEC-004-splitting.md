# SPEC-004 — Divisão Experimental (Splitting)

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §6, §7.3; `docs/adr/ADR-001-run-as-group-unit.md` |
| Skill correspondente | `.agents/skills/grouped-split/SKILL.md` |
| Etapa do pipeline | Etapa 3 |
| Entrega | A3 |
| Guardas executáveis | `src/wp1a/splitting/run_leakage.py`, `src/wp1a/splitting/reproducibility.py` |
| Testes de rejeição | `tests/methodology/test_run_leakage.py`, `tests/methodology/test_split_reproducibility.py` |

Em caso de conflito, prevalece `SPEC-000-master.md` e `ADR-001-run-as-group-unit.md`.

## 1. Objetivo

Produzir a divisão oficial e única dos dados em treino, validação e teste, agrupada pela execução (`run`), com verificação automatizada de disjunção e reprodutibilidade.

## 2. Escopo

Cobre exclusivamente a divisão dos dados. Não cobre pré-processamento (SPEC-005) nem treinamento (SPEC-006).

## 3. Requisitos

1. A unidade de divisão é a execução (`run_id`), nunca a amostra individual (INV-01).
2. Nenhum `run_id` pode aparecer em mais de uma partição (INV-02) — verificado automaticamente por `check_run_disjoint`/`check_manifest_disjoint`.
3. Semente aleatória explícita, registrada.
4. A divisão é determinística: chamadas repetidas com a mesma semente produzem o mesmo manifesto (verificado por `assert_split_reproducible`).
5. Representação das 21 classes em cada partição, na medida do possível.

## 4. Entradas e saídas

- **Entrada:** dataset canônico (SPEC-002).
- **Saída:** Entrega A3 — manifesto de divisão (CSV/JSON) em `data/processed/`, referenciando o identificador de versão do dataset canônico.

## 5. Critérios de aceite

- CA-03 (SPEC-000): interseção vazia entre `run_id` de treino/validação/teste, verificada automaticamente.
- Toda a suíte `tests/methodology/test_run_leakage.py` e `test_split_reproducibility.py` passa contra o manifesto gerado.

## 6. Rastreabilidade

`ADR-001-run-as-group-unit.md` → `SPEC-000-master.md` §6, §7.3, INV-01/INV-02 → esta SPEC → `.agents/skills/grouped-split/SKILL.md` → guardas em `src/wp1a/splitting/`.
