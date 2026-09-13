# SPEC-001 — Auditoria dos Dados

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §5, §7.1 |
| Skill correspondente | `.agents/skills/data-audit/SKILL.md` |
| Etapa do pipeline | Etapa 1 |
| Entrega | A1 |

Em caso de conflito, prevalece `SPEC-000-master.md`. Este documento apenas recorta e detalha, para a Etapa 1, o que já está definido na especificação mestra.

## 1. Objetivo

Verificar e documentar a integridade, a estrutura e a rastreabilidade dos dados brutos do TEP antes de qualquer uso em análise ou modelagem.

## 2. Escopo

Cobre exclusivamente a auditoria dos arquivos brutos (`data/raw/`). Não decide qual dataset é canônico (ver SPEC-002) e não realiza nenhuma transformação dos dados.

## 3. Requisitos

A auditoria DEVE verificar e reportar, individualmente:

1. Arquivos disponíveis (nome, formato, tamanho).
2. Quantidade de linhas e colunas por arquivo.
3. Nomes, tipos e significado das variáveis.
4. Distribuição das 21 classes.
5. Quantidade de execuções (`run`) por classe.
6. Valores ausentes, infinitos ou inconsistentes.
7. Possíveis duplicações (intra e entre arquivos).
8. Relação entre arquivos, classes e identificadores de execução (`run_id`).

Contagens obrigatórias a conferir contra o esperado normativo: 52 variáveis de processo (DS-02), 21 classes (DS-03).

## 4. Entradas e saídas

- **Entrada:** `data/raw/*` (arquivos de origem do TEP).
- **Saída:** Entrega A1 (relatório de auditoria, PDF/CSV) em `reports/audit/`; metadados de contagens em `results/metadata/`.

## 5. Critérios de aceite

- CA-02 da SPEC-000: dataset auditado com resultado explícito para cada um dos 8 itens do procedimento, inclusive "nenhum problema encontrado" quando aplicável.
- Toda divergência frente ao esperado (52 variáveis, 21 classes) está documentada, não omitida.

## 6. Rastreabilidade

WP1A §9.1 → `requirements.md` RD-01..06, RP-01 → `SPEC-000-master.md` §5, §7.1, DS-01..06 → esta SPEC → `.agents/skills/data-audit/SKILL.md`.
