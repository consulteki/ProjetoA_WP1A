# SPEC-002 — Dataset Canônico

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §5; `docs/adr/ADR-004-canonical-dataset.md` |
| Skill correspondente | `.agents/skills/canonical-dataset/SKILL.md` |
| Etapa do pipeline | Pré-condição transversal (pós Etapa 1) |
| Entrega | Registro do dataset canônico (insumo de A3–A9) |

Em caso de conflito, prevalece `SPEC-000-master.md` e `ADR-004-canonical-dataset.md`.

## 1. Objetivo

Estabelecer, a partir do relatório de auditoria (A1), uma fonte única e versionada de dados para todo o benchmark, impedindo que subconjuntos ou versões divergentes alimentem resultados finais.

## 2. Escopo

Cobre a seleção e o registro formal do dataset canônico. Não cobre a divisão em treino/validação/teste (ver SPEC-004).

## 3. Requisitos

1. O dataset canônico é definido exclusivamente a partir de arquivos já cobertos pelo relatório de auditoria (A1) — sem pendências de verificação.
2. Um identificador de versão do dataset canônico DEVE ser registrado (data de congelamento e/ou checksum dos arquivos de origem).
3. Qualquer subconjunto/amostra usada para fins exploratórios é marcada como **não canônica** e não pode alimentar as Entregas A5–A9.
4. Alteração do dataset canônico exige nova auditoria (SPEC-001) e emenda formal a `ADR-004-canonical-dataset.md`.

## 4. Entradas e saídas

- **Entrada:** Entrega A1 (relatório de auditoria).
- **Saída:** registro do dataset canônico (identificador de versão, lista de arquivos, decisões de tratamento global) em `data/processed/`.

## 5. Critérios de aceite

- Todo dado usado da SPEC-004 em diante é rastreável ao registro do dataset canônico.
- CA-02 (SPEC-000) reforçado por referência única e não ambígua.

## 6. Rastreabilidade

`ADR-004-canonical-dataset.md` → `SPEC-000-master.md` §5, DS-01..06 → esta SPEC → `.agents/skills/canonical-dataset/SKILL.md`.
