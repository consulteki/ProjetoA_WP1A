# SPEC-008 — Análise Estatística

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §10; `docs/adr/ADR-008-statistical-comparison-methodology.md` |
| Skill correspondente | `.agents/skills/statistical-analysis/SKILL.md` |
| Etapa do pipeline | Transversal (pós Etapa 6) |
| Guardas executáveis | `src/wp1a/splitting/run_leakage.py` (para checagem cruzada da unidade experimental) |

Em caso de conflito, prevalece `SPEC-000-master.md` e `ADR-008-statistical-comparison-methodology.md`.

## 1. Objetivo

Aplicar testes estatísticos formais para sustentar ou refutar diferenças de desempenho entre os 6 modelos, com a execução (`run`) como unidade experimental.

## 2. Escopo

Cobre exclusivamente a comparação estatística formal. Não recalcula métricas de desempenho (ver SPEC-007).

## 3. Requisitos

1. Média, desvio-padrão e intervalo de confiança sempre que houver múltiplas repetições (sementes/partições).
2. Teste de Friedman para comparação global entre os 6 modelos.
3. Procedimento pós-hoc quando a hipótese nula for rejeitada.
4. Teste de Wilcoxon para comparações pareadas específicas, com correção para múltiplas comparações.
5. Unidade experimental (execução) e número de unidades declarados explicitamente em todo teste (INV-09).
6. Nenhuma observação/instante temporalmente correlacionado tratado como amostra independente.
7. Limitação de poder estatístico (ex.: partição única, sem repetição) declarada explicitamente, nunca disfarçada de comparação validada.

## 4. Entradas e saídas

- **Entrada:** métricas por modelo/repetição (SPEC-007, A5).
- **Saída:** relatório/tabela de resultados estatísticos em `results/tables/`.

## 5. Critérios de aceite

- Todo teste estatístico reportado declara unidade experimental e número de unidades.
- Nenhuma comparação pareada múltipla sem correção.

## 6. Rastreabilidade

`ADR-008-statistical-comparison-methodology.md` → `SPEC-000-master.md` §10, INV-09 → esta SPEC → `.agents/skills/statistical-analysis/SKILL.md`.
