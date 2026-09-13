# Skills do Pipeline WP1A

Este diretório contém as 10 skills independentes que operacionalizam o pipeline experimental do benchmark WP1A. Cada skill é um procedimento padronizado, com pré-condições, entradas, procedimento, saídas, critérios de validação, condições de falha e definição de pronto — derivado exclusivamente de `docs/specs/SPEC-000-master.md`, `docs/project/requirements.md`, das ADRs em `docs/adr/` e das regras de `AGENTS.md`.

Nenhuma skill contém ou prescreve implementação de código; cada uma descreve o que deve ser feito, sob quais condições, e como verificar que foi feito corretamente.

## Índice e ordem de execução

| # | Skill | Etapa do pipeline (SPEC-000 §7) | Entrega principal |
|---|---|---|---|
| 1 | [data-audit](./data-audit/SKILL.md) | Etapa 1 — Auditoria dos dados | A1 |
| 2 | [canonical-dataset](./canonical-dataset/SKILL.md) | Pré-condição transversal (ADR-004) | Registro do dataset canônico |
| 3 | [exploratory-analysis](./exploratory-analysis/SKILL.md) | Etapa 2 — Análise exploratória | A2 |
| 4 | [grouped-split](./grouped-split/SKILL.md) | Etapa 3 — Divisão experimental | A3 |
| 5 | [preprocessing](./preprocessing/SKILL.md) | Etapa 4 — Pré-processamento | Conjuntos pré-processados |
| 6 | [ml-training](./ml-training/SKILL.md) | Etapa 5 — Treinamento e seleção | A4 |
| 7 | [ml-evaluation](./ml-evaluation/SKILL.md) | Etapa 6 — Avaliação final | A5 |
| 8 | [statistical-analysis](./statistical-analysis/SKILL.md) | Transversal (após Etapa 6) | Resultados estatísticos |
| 9 | [scientific-figures](./scientific-figures/SKILL.md) | Pós-avaliação | Parte de A6 |
| 10 | [scientific-writing](./scientific-writing/SKILL.md) | Consolidação final | A7, A8 |

## Dependências entre skills

```
data-audit ──► canonical-dataset ──► exploratory-analysis
                     │
                     ▼
               grouped-split ──► preprocessing ──► ml-training ──► ml-evaluation
                                                                        │
                                                          ┌─────────────┼─────────────┐
                                                          ▼                            ▼
                                              statistical-analysis          scientific-figures
                                                          │                            │
                                                          └─────────────┬──────────────┘
                                                                        ▼
                                                              scientific-writing
```

Nenhuma skill pode ser executada antes de suas pré-condições estarem satisfeitas pelas skills anteriores na cadeia. Em particular:

- `canonical-dataset` exige `data-audit` completa (Entrega A1 sem pendências).
- `grouped-split` exige `canonical-dataset` registrado.
- `preprocessing` exige `grouped-split` validado (partições disjuntas confirmadas).
- `ml-training` exige `preprocessing` concluído para treino/validação/teste.
- `ml-evaluation` exige `ml-training` concluído, com predições de teste geradas exatamente uma vez por modelo, após congelamento.
- `statistical-analysis` e `scientific-figures` exigem `ml-evaluation` concluído; podem ser executadas em qualquer ordem entre si.
- `scientific-writing` exige `statistical-analysis` e `scientific-figures` concluídas.

## Relação com os demais documentos normativos

| Documento | Papel em relação às skills |
|---|---|
| `MEI0028_WP1A_3.pdf` (WP1A) | Fonte original de todos os requisitos operacionalizados pelas skills. |
| `docs/project/requirements.md` | Requisitos verificáveis referenciados em "Fontes normativas" de cada skill. |
| `docs/specs/SPEC-000-master.md` | Especificação mestra; cada skill implementa uma ou mais seções dela. |
| `docs/adr/` | Decisões estruturantes que cada skill deve respeitar (ex.: `grouped-split` implementa ADR-001; `ml-training` implementa ADR-002/ADR-005/ADR-006). |
| `AGENTS.md` | Regras operacionais obrigatórias (workflow, testes, Git, proibições) que se aplicam à execução de qualquer skill. |

Qualquer agente que execute uma destas skills DEVE, antes de iniciar, reler a seção "Fontes normativas" da skill correspondente e confirmar que as pré-condições estão satisfeitas.
