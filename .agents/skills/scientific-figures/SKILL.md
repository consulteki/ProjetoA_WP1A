---
name: scientific-figures
description: Produz as tabelas e figuras obrigatórias do artigo/relatório WP1A a partir dos resultados versionados de avaliação e análise estatística.
---

# Skill: scientific-figures

**Fontes normativas:** `docs/specs/SPEC-000-master.md` §11.2; `docs/project/requirements.md` Seção 8 (Entregas), item A6; `AGENTS.md` DOC-R03.

## Purpose

Gerar o conjunto mínimo obrigatório de tabelas e figuras exigido pelo WP1A para compor o artigo científico e o relatório técnico, garantindo que cada elemento visual seja rastreável a um artefato de resultado versionado (não recriado manualmente a partir de números soltos).

## Preconditions

- As skills `data-audit`, `ml-training`, `ml-evaluation` e `statistical-analysis` foram executadas e seus artefatos de saída estão versionados e acessíveis.

## Inputs

- Relatório de auditoria (A1) para a tabela de caracterização da base.
- Tabela de hiperparâmetros (via `ml-training`).
- Resultados completos (A5) — métricas globais, por classe, matrizes de confusão, custo computacional (via `ml-evaluation`).
- Resultados estatísticos (via `statistical-analysis`).

## Procedure

1. Gerar a tabela de caracterização da base (a partir de A1): número de variáveis, número de classes, distribuição de classes/execuções.
2. Gerar a tabela dos hiperparâmetros dos modelos (a partir de `ml-training`), um conjunto de hiperparâmetros por um dos seis modelos.
3. Gerar a tabela comparativa das métricas globais (a partir de A5), cobrindo todas as métricas MET-01 a MET-12 para os seis modelos.
4. Gerar a tabela de métricas por classe (a partir de A5), cobrindo as 21 classes para os seis modelos.
5. Gerar as matrizes de confusão (uma por modelo, ou consolidadas), a partir de A5.
6. Gerar o gráfico comparativo de F1 macro e MCC entre os seis modelos.
7. Gerar o gráfico de custo computacional (tempo de treinamento, tempo de inferência, tamanho do modelo) entre os seis modelos.
8. Gerar a análise visual das falhas mais confundidas (a partir das matrizes de confusão e do F1 por classe), destacando as classes identificadas em `ml-evaluation`.
9. Para cada tabela/figura gerada, registrar explicitamente de qual arquivo de resultado versionado ela foi derivada.
10. Exportar as figuras em formato adequado à publicação (PNG/PDF) e as tabelas em formato compatível com LaTeX, conforme a estrutura do manuscrito.

## Outputs

- **Parte da Entrega A6** — Figuras e tabelas do artigo (PNG/PDF/LaTeX), cobrindo os 8 itens do procedimento (insumos 1–8 do artigo, SPEC-000 §11.2).
- Registro de rastreabilidade tabela/figura → arquivo de resultado de origem, para consumo por `scientific-writing` e para auditoria (DOC-R03).

## Validation

- Cada uma das 8 tabelas/figuras obrigatórias existe e está associada a um arquivo de resultado versionado em `results/`.
- Os números apresentados nas tabelas conferem exatamente com os valores nos arquivos de resultado de origem (sem transcrição manual divergente).
- Gráficos de F1 macro/MCC e de custo computacional cobrem os seis modelos, sem omissão.

## Failure Conditions

- Qualquer tabela/figura cujo número não seja rastreável a um arquivo de resultado versionado (viola DOC-R03).
- Omissão de qualquer um dos 8 itens obrigatórios de insumo do artigo.
- Divergência entre o valor apresentado na figura/tabela e o valor no arquivo de resultado de origem.
- Geração de figuras a partir de resultados não canônicos ou de execuções não congeladas (ver `ml-training`).

## Definition of Done

- Os 8 insumos obrigatórios (tabelas e figuras) produzidos, versionados em `results/figures/` e `results/tables/`, e rastreáveis às fontes.
- Parte da Entrega A6 concluída e pronta para incorporação ao manuscrito por `scientific-writing`.
