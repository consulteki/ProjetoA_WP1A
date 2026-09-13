---
name: canonical-dataset
description: Define e registra a versão canônica única do dataset TEP a partir do relatório de auditoria, servindo de referência obrigatória para todas as demais skills.
---

# Skill: canonical-dataset

**Fontes normativas:** `docs/adr/ADR-004-canonical-dataset.md`; `docs/specs/SPEC-000-master.md` §5, §12 (INV-10); `docs/project/requirements.md` Seção 2; `AGENTS.md` GIT-R03, DOC-R03, DOC-R04.

## Purpose

Estabelecer, a partir do relatório de auditoria (Entrega A1), uma **fonte canônica única** de dados para todo o benchmark WP1A, registrando-a de forma explícita e versionada, de modo que nenhuma skill subsequente (`exploratory-analysis`, `grouped-split`, `preprocessing`, `ml-training`, `ml-evaluation`) possa operar sobre uma versão divergente dos dados.

## Preconditions

- A skill `data-audit` foi executada e produziu a Entrega A1 completa, sem itens de verificação pendentes.
- Todas as divergências identificadas na auditoria (valores ausentes, duplicados, inconsistências) foram avaliadas e uma decisão de tratamento foi tomada e documentada (mesmo que a decisão seja "manter como está, com justificativa").

## Inputs

- Entrega A1 (relatório de auditoria) e seus metadados de contagens.
- Arquivos brutos de origem referenciados em A1 (`data/raw/`).
- ADR-004 (decisão estrutural que esta skill operacionaliza).

## Procedure

1. Revisar o relatório A1 e confirmar que a contagem de variáveis (52) e de classes (21) está de acordo com o esperado, ou documentar explicitamente por que difere.
2. Selecionar, entre os arquivos auditados, o conjunto exato de arquivos que compõe o dataset canônico (nenhuma seleção parcial "temporária" sem registro).
3. Definir e registrar um identificador de versão do dataset canônico (ex.: data de congelamento, hash/checksum dos arquivos de origem, quando viável).
4. Registrar, para o dataset canônico, quaisquer decisões de tratamento de dados aplicadas globalmente antes da divisão (ex.: remoção de duplicatas exatas identificadas em A1) — decisões de pré-processamento dependentes de partição (padronização, etc.) NÃO pertencem a esta skill (ver `preprocessing`).
5. Publicar o registro do dataset canônico em local versionado e referenciável por outras skills (ex.: `data/processed/canonical_dataset_registry`).
6. Marcar explicitamente qualquer outro subconjunto, amostra reduzida ou versão alternativa dos dados usada para fins exploratórios como **não canônica**, impedindo que seus resultados alimentem entregas finais (A5–A9).
7. Comunicar (via documentação) que qualquer alteração futura ao dataset canônico exige nova auditoria (`data-audit`) e uma emenda formal a ADR-004.

## Outputs

- Registro do dataset canônico (identificador de versão, lista de arquivos de origem, decisões de tratamento global aplicadas), versionado em `data/processed/` ou equivalente.
- Referência explícita ao dataset canônico, a ser citada por toda configuração de experimento (skill `ml-training`, ADR-005).

## Validation

- O registro do dataset canônico é rastreável, item a item, ao relatório de auditoria A1.
- Nenhum dado usado nas skills seguintes (`grouped-split` em diante) é proveniente de fonte não referenciada no registro canônico.
- A contagem de variáveis/classes do dataset canônico confere com o que foi reportado em A1.

## Failure Conditions

- Definição do dataset canônico sem relatório de auditoria (A1) completo e revisado.
- Existência de mais de uma versão "canônica" simultânea, sem registro de qual é a vigente.
- Uso, em qualquer entrega final (A5–A9), de dados provenientes de um subconjunto não registrado como canônico.
- Alteração do dataset canônico sem nova auditoria e sem atualização/emenda de ADR-004.

## Definition of Done

- Registro do dataset canônico publicado, versionado e referenciável por identificador único.
- Toda divergência entre os dados brutos e o esperado normativo (52 variáveis, 21 classes) está resolvida ou explicitamente justificada no registro.
- Critério de aceite CA-02 reforçado com uma referência única e não ambígua ao dataset usado em todas as etapas seguintes.
- Skills subsequentes podem citar o identificador do dataset canônico em seus próprios artefatos de saída.
