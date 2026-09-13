---
name: grouped-split
description: Realiza a divisão treino/validação/teste do dataset canônico do TEP agrupada por execução (run), produzindo o manifesto de divisão (Etapa 3 do pipeline WP1A).
---

# Skill: grouped-split

**Fontes normativas:** `docs/adr/ADR-001-run-as-group-unit.md`; `docs/specs/SPEC-000-master.md` §6, §7.3, §12 (INV-01, INV-02); `docs/project/requirements.md` RD-03, RD-04, RP-03, RP-04; `AGENTS.md` LEAK-R01, LEAK-R04, TEST-R01.

## Purpose

Produzir a divisão oficial e única dos dados em treino, validação e teste, agrupada pela unidade experimental (execução/`run`), garantindo que nenhuma execução apareça em mais de uma partição, e registrando o manifesto de divisão que será usado por todas as demais skills de modelagem.

## Preconditions

- A skill `canonical-dataset` foi executada; o dataset canônico está registrado.
- A lista de `run_id` associada a cada amostra do dataset canônico está disponível e íntegra (verificada em `data-audit`).

## Inputs

- Dataset canônico e sua lista de `run_id` por amostra/classe.
- Critério de proporção/composição desejada de treino/validação/teste (a ser documentado nesta execução, ex.: número ou proporção de execuções por partição e por classe).

## Procedure

1. Listar todas as execuções (`run_id`) distintas do dataset canônico, com sua classe associada.
2. Definir uma semente aleatória explícita para o processo de divisão e registrá-la.
3. Particionar o conjunto de `run_id` em três grupos disjuntos — treino, validação, teste — respeitando: (a) nenhuma execução em mais de uma partição; (b) representação de todas as 21 classes em cada partição, na medida do possível, dado o desenho de execuções disponível.
4. Verificar de forma automatizada que a interseção entre os conjuntos de `run_id` de treino, validação e teste é vazia, par a par.
5. Verificar que a partição de teste não foi consultada por nenhuma etapa anterior (`exploratory-analysis`) para decisões de modelagem.
6. Registrar o manifesto de divisão: lista completa de `run_id` por partição, semente utilizada, e referência ao identificador de versão do dataset canônico (produzido por `canonical-dataset`).
7. Versionar o manifesto de divisão como artefato imutável — qualquer necessidade de nova divisão gera um novo manifesto versionado, não uma edição do existente.

## Outputs

- **Entrega A3** — Manifesto da divisão por execução (CSV/JSON), contendo `run_id` por partição e semente aleatória.

## Validation

- Teste automatizado (TEST-R01) confirma disjunção par a par entre os conjuntos de `run_id` de treino, validação e teste.
- Todas as 21 classes estão representadas nas partições de treino e teste (ou a ausência de alguma classe em alguma partição está explicitamente documentada como limitação).
- O manifesto referencia de forma explícita o identificador de versão do dataset canônico usado.

## Failure Conditions

- Qualquer `run_id` presente em mais de uma partição (violação direta de INV-01/INV-02).
- Divisão realizada por amostra individual em vez de por execução completa.
- Ausência de registro de semente aleatória ou do manifesto de divisão versionado.
- Geração de uma nova divisão sem versionamento explícito, sobrescrevendo silenciosamente um manifesto já usado em resultados publicados.
- Uso do manifesto de teste por qualquer skill de modelagem antes do congelamento de configuração (ver `ml-training`).

## Definition of Done

- Entrega A3 produzida, versionada, com verificação automatizada de disjunção documentada e aprovada.
- Critério de aceite CA-03 (SPEC-000 §13) satisfeito.
- Manifesto disponível e referenciável por `preprocessing`, `ml-training` e `statistical-analysis`.
