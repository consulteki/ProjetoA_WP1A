---
name: preprocessing
description: Aplica transformações dependentes dos dados (padronização e equivalentes) ajustadas exclusivamente no treino, conforme a Etapa 4 do pipeline WP1A.
---

# Skill: preprocessing

**Fontes normativas:** `docs/adr/ADR-002-test-set-isolation.md`; `docs/specs/SPEC-000-master.md` §7.4, §12 (INV-04); `docs/project/requirements.md` RP-05, RP-06; `AGENTS.md` LEAK-R02, LEAK-R05, TEST-R02.

## Purpose

Aplicar, de forma consistente e sem vazamento, as transformações de dados dependentes de distribuição (padronização, normalização, codificação, tratamento de valores ausentes remanescentes) necessárias antes do treinamento, garantindo que todo parâmetro de transformação seja estimado exclusivamente a partir do conjunto de treinamento.

## Preconditions

- A skill `grouped-split` foi executada; o manifesto de divisão (Entrega A3) está disponível e validado (partições disjuntas confirmadas).
- As decisões de pré-processamento a aplicar seguem a infraestrutura comum do projeto já estabelecida (não são reinventadas por modelo).

## Inputs

- Dataset canônico (via `canonical-dataset`).
- Manifesto de divisão (Entrega A3, via `grouped-split`).
- Observações relevantes da análise exploratória (`exploratory-analysis`), quando indicarem necessidade de tratamento específico (ex.: variáveis de alta dispersão).

## Procedure

1. Selecionar, a partir do conjunto de treinamento (e somente dele), os parâmetros de qualquer transformação dependente dos dados (ex.: médias e desvios-padrão para padronização, categorias para codificação, valores de imputação).
2. Ajustar (`fit`) os objetos de transformação exclusivamente sobre o conjunto de treinamento.
3. Aplicar (`transform`, sem reajuste) os mesmos objetos de transformação aos conjuntos de validação e de teste.
4. Verificar, de forma automatizada, que nenhum parâmetro de transformação foi recomputado a partir de dados de validação ou teste.
5. Documentar explicitamente cada transformação aplicada (tipo, parâmetros de alto nível, ordem de aplicação) para reprodutibilidade.
6. Persistir os objetos de transformação ajustados (ou seus parâmetros) de forma versionada, associados ao manifesto de divisão e ao dataset canônico usados.
7. Gerar os conjuntos de dados pré-processados (treino, validação, teste) prontos para consumo por `ml-training`.

## Outputs

- Conjuntos de dados pré-processados por partição (`data/processed/`), rastreáveis ao manifesto de divisão (A3) e ao dataset canônico.
- Objetos/parâmetros de transformação versionados, para reuso determinístico em inferência futura.
- Documentação das transformações aplicadas, para a tabela de "materiais e métodos" do relatório/artigo.

## Validation

- Teste automatizado (TEST-R02) confirma que os parâmetros de transformação (ex.: médias/desvios de um scaler) provêm exclusivamente do conjunto de treinamento.
- Os conjuntos de validação e teste, após transformação, não influenciaram em nenhum momento o ajuste dos objetos de transformação.
- A documentação das transformações é suficiente para reproduzir exatamente o mesmo resultado a partir dos dados brutos e do manifesto de divisão.

## Failure Conditions

- Ajuste (`fit`) de qualquer transformação usando dados de validação ou teste, isolados ou combinados com o treino.
- Reajuste (`re-fit`) de um objeto de transformação já ajustado, para qualquer partição.
- Aplicação de transformações diferentes (ou com parâmetros diferentes) a modelos diferentes dentro do mesmo benchmark, quebrando a comparabilidade exigida por INV-03.
- Ausência de versionamento dos objetos/parâmetros de transformação, impedindo reprodutibilidade (REP-01 a REP-06).

## Definition of Done

- Conjuntos pré-processados de treino, validação e teste disponíveis e rastreáveis ao manifesto de divisão e ao dataset canônico.
- Verificação automatizada de ausência de vazamento estatístico documentada e aprovada.
- Transformações aplicadas documentadas de forma suficiente para a Entrega A7 (materiais e métodos) e para reprodutibilidade (ADR-003).
