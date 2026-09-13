---
name: data-audit
description: Audita e documenta a base de dados do Tennessee Eastman Process antes de qualquer uso em modelagem, conforme a Etapa 1 do pipeline WP1A.
---

# Skill: data-audit

**Fontes normativas:** `docs/specs/SPEC-000-master.md` §5, §7.1; `docs/project/requirements.md` RD-01..06, RP-01; `docs/adr/ADR-004-canonical-dataset.md`; `AGENTS.md` §1, §2.

## Purpose

Verificar e documentar de forma sistemática a integridade, a estrutura e a rastreabilidade dos dados brutos do TEP antes de qualquer etapa de análise ou modelagem, produzindo o registro oficial (Entrega A1) que outras skills (especialmente `canonical-dataset`) usarão como base de verdade.

Esta skill não decide qual dataset é canônico (isso é responsabilidade de `canonical-dataset`); ela produz a evidência factual sobre os dados disponíveis a partir da qual essa decisão pode ser tomada.

## Preconditions

- Os arquivos brutos do TEP (treinamento e teste, execuções normais e com falha) estão acessíveis no ambiente de trabalho, em `data/raw/`.
- Nenhuma etapa de pré-processamento, divisão ou modelagem foi ainda realizada sobre esses arquivos.
- O executor tem acesso de leitura a todos os arquivos de origem citados na documentação do WP1A.

## Inputs

- Arquivos brutos de treinamento e teste do TEP (`data/raw/`).
- Documentação de referência do dataset (Seção 7 do WP1A; SPEC-000 §5).
- Convenção esperada de 52 variáveis de processo e 21 classes (1 normal + 20 falhas).

## Procedure

1. Listar todos os arquivos disponíveis em `data/raw/` e registrar nome, formato e tamanho de cada um.
2. Determinar a quantidade de linhas e colunas de cada arquivo.
3. Identificar nomes, tipos de dado e significado (quando documentado na fonte) de cada variável de processo.
4. Calcular a distribuição das classes (contagem de amostras por classe, das 21 classes esperadas).
5. Calcular a quantidade de execuções (`run`) distintas por classe.
6. Verificar a presença de valores ausentes, infinitos (`inf`/`-inf`) ou inconsistentes (ex.: fora de faixas fisicamente plausíveis), registrando contagem e localização.
7. Verificar a existência de linhas duplicadas, tanto dentro de um mesmo arquivo quanto entre arquivos de treino/teste.
8. Verificar a relação entre arquivos, classes e identificadores de execução (`run_id`): cada `run_id` deve mapear de forma consistente e não ambígua a uma única classe e a um único arquivo de origem.
9. Consolidar os achados dos passos 1–8 em um relatório de auditoria estruturado (Entrega A1), incluindo, para cada item, um resultado explícito — inclusive "nenhum problema encontrado", quando for o caso.
10. Sinalizar explicitamente qualquer divergência frente ao esperado pela SPEC-000 (52 variáveis, 21 classes) como um achado de auditoria, não como um erro silencioso a corrigir sem registro.

## Outputs

- **Entrega A1** — Relatório de auditoria da base (PDF/CSV), contendo os oito itens do procedimento acima.
- Tabela de caracterização da base (insumo 1 dos insumos do artigo — SPEC-000 §11.2), reaproveitável por `scientific-figures`.
- Registro estruturado (ex.: CSV/JSON de metadados) com contagens de linhas, colunas, classes e execuções, para uso por `canonical-dataset`.

## Validation

- O relatório A1 cobre individualmente cada um dos oito itens do procedimento, com resultado explícito.
- A contagem de variáveis e de classes reportada é comparada explicitamente ao valor normativo (52 variáveis, 21 classes — DS-02, DS-03); qualquer divergência é destacada, não omitida.
- A relação arquivo–classe–`run_id` é verificada de forma automatizada (não apenas por inspeção visual), com evidência de que a verificação foi executada.

## Failure Conditions

- Ausência de verificação para qualquer um dos oito itens do procedimento.
- Relatório A1 que declara "dados íntegros" sem evidência de checagem de valores ausentes/infinitos/duplicados.
- Progresso para as skills seguintes (`canonical-dataset`, `exploratory-analysis`) sem que o relatório A1 exista ou esteja completo.
- Uso de estatísticas agregadas (médias, distribuições) calculadas sobre dados cuja integridade ainda não foi auditada, para qualquer finalidade além da própria auditoria.

## Definition of Done

- Entrega A1 produzida, versionada e revisável, cobrindo os oito itens do procedimento.
- Toda divergência frente ao esperado normativo (52 variáveis, 21 classes) está documentada, mesmo que não resolvida nesta skill.
- Critério de aceite CA-02 (SPEC-000 §13) satisfeito: dataset auditado com resultado explícito para cada item verificado.
- Artefato de metadados de contagens disponível para consumo pela skill `canonical-dataset`.
