---
name: statistical-analysis
description: Aplica testes estatísticos formais (Friedman, Wilcoxon) para comparar os seis modelos, respeitando a execução como unidade experimental.
---

# Skill: statistical-analysis

**Fontes normativas:** `docs/adr/ADR-008-statistical-comparison-methodology.md`; `docs/specs/SPEC-000-master.md` §10, §12 (INV-09); `docs/project/requirements.md` RAE-01..05; `AGENTS.md` EXP-R06.

## Purpose

Aplicar procedimentos estatísticos formais para sustentar (ou refutar) diferenças de desempenho entre os seis modelos, garantindo que a unidade experimental usada em qualquer teste seja a execução do processo (`run`), e nunca a amostra individual, evitando inflação artificial de significância estatística.

## Preconditions

- A skill `ml-evaluation` foi executada e produziu métricas por modelo.
- Existem múltiplas execuções independentes, sementes ou partições disponíveis para comparação (caso contrário, ver Failure Conditions quanto à limitação a ser declarada).

## Inputs

- Métricas por modelo, idealmente replicadas por múltiplas sementes/partições (via `ml-evaluation`, repetido sob diferentes configurações de `grouped-split`/`ml-training` quando aplicável).
- Definição da unidade experimental (execução — ADR-001).

## Procedure

1. Consolidar, para cada modelo, os valores de métrica relevante (ex.: F1 macro, MCC) obtidos em cada repetição independente (semente/partição), preservando a granularidade por unidade experimental.
2. Quando houver múltiplas repetições, calcular média, desvio-padrão e intervalo de confiança para cada modelo e métrica.
3. Aplicar o teste de Friedman para comparação global entre os seis modelos.
4. Se a hipótese nula de igualdade entre modelos for rejeitada, aplicar procedimento pós-hoc apropriado para identificar quais pares de modelos diferem significativamente.
5. Para comparações pareadas específicas de interesse direto das hipóteses H1–H4 (ex.: XGBoost vs. Regressão Logística), aplicar o teste de Wilcoxon, com correção para múltiplas comparações (ex.: Holm ou Bonferroni).
6. Declarar explicitamente, em todo teste realizado, a unidade experimental (execução) e o número de unidades que entraram no teste.
7. Registrar os resultados de cada teste (estatística, valor-p, tamanho de efeito quando aplicável) de forma versionada e rastreável às métricas de origem.
8. Caso apenas uma única partição/semente esteja disponível, não aplicar testes de significância como se houvesse replicação — reportar a limitação explicitamente como ameaça à validade estatística, a ser incorporada por `scientific-writing`.

## Outputs

- Relatório/tabela de resultados estatísticos (estatística de Friedman, resultados pós-hoc, estatísticas de Wilcoxon com correção), versionado em `results/tables/`.
- Declaração explícita da unidade experimental e do número de unidades usadas em cada teste, para consumo por `scientific-writing`.
- Registro de limitação estatística (quando aplicável) para a seção de ameaças à validade.

## Validation

- Todo teste estatístico reportado indica explicitamente a unidade experimental e o número de unidades.
- Nenhum teste trata observações/instantes correlacionados dentro de uma mesma execução como unidades independentes (verificação cruzada com o manifesto de divisão — `grouped-split`).
- Comparações pareadas múltiplas apresentam método de correção explícito.

## Failure Conditions

- Aplicação de teste estatístico diretamente sobre predições por amostra individual, sem agregação por execução.
- Comparações pareadas múltiplas sem correção para múltiplas comparações.
- Ausência de declaração da unidade experimental em qualquer teste reportado.
- Apresentação de resultado de uma única partição/semente como se fosse estatisticamente validado por teste formal com repetições.

## Definition of Done

- Resultados estatísticos versionados e rastreáveis às métricas de origem (`ml-evaluation`).
- Toda limitação de poder estatístico (ex.: ausência de múltiplas repetições) está documentada explicitamente.
- Artefatos prontos para consumo por `scientific-writing` (seções "Resultados" e "Ameaças à validade").
