# SPEC-009 — Publicação (Figuras, Relatório e Manuscrito)

| Campo | Valor |
|---|---|
| Deriva de | `docs/specs/SPEC-000-master.md` §11.2, §11.4, §14 |
| Skills correspondentes | `.agents/skills/scientific-figures/SKILL.md`, `.agents/skills/scientific-writing/SKILL.md` |
| Etapa do pipeline | Consolidação final |
| Entregas | A6, A7, A8, A9 |

Em caso de conflito, prevalece `SPEC-000-master.md`.

## 1. Objetivo

Consolidar os artefatos de todas as etapas anteriores em tabelas, figuras, relatório técnico e manuscrito científico, respondendo QP1–QP5 e avaliando H1–H4 com rastreabilidade total a resultados versionados.

## 2. Escopo

Cobre a produção de figuras/tabelas (A6), relatório técnico (A7), manuscrito (A8) e apresentação (A9). Não recalcula métricas nem testes estatísticos (SPEC-007/SPEC-008 são as fontes).

## 3. Requisitos

### 3.1 Figuras e tabelas (A6)

1. Tabela de caracterização da base.
2. Tabela de hiperparâmetros dos modelos.
3. Tabela comparativa das métricas globais.
4. Tabela de métricas por classe.
5. Matrizes de confusão.
6. Gráfico comparativo de F1 macro e MCC.
7. Gráfico de custo computacional.
8. Análise das falhas mais confundidas.

Cada item DEVE ser rastreável a um arquivo de resultado versionado em `results/`.

### 3.2 Relatório técnico (A7) e manuscrito (A8)

Estrutura obrigatória do manuscrito: Introdução; Fundamentação; Trabalhos relacionados; Materiais e métodos; Protocolo reprodutível; Resultados; Discussão; Ameaças à validade; Conclusões; Referências.

QP1–QP5 respondidas explicitamente; H1–H4 avaliadas individualmente (corroborada/refutada); nenhuma conclusão de "melhor modelo" baseada em métrica única; nenhuma interpretação causal de importâncias de atributos.

### 3.3 Apresentação (A9)

Síntese do relatório/manuscrito, cobrindo problema, hipóteses, protocolo, resultados e conclusões.

## 4. Entradas e saídas

- **Entrada:** resultados (SPEC-007, A5), estatísticas (SPEC-008), registros de dataset/split/config (SPEC-002/004/006).
- **Saída:** A6 em `article/figures/` e `article/tables/`; A7 em `reports/technical/`; A8 em `article/manuscript/`; A9 em `presentation/`.

## 5. Critérios de aceite

- CA-07, CA-08, CA-10 (SPEC-000): QP/H respondidas, estrutura do manuscrito seguida, ameaças à validade cobertas nas 4 categorias.

## 6. Rastreabilidade

`SPEC-000-master.md` §11, §14 → esta SPEC → `.agents/skills/scientific-figures/SKILL.md`, `.agents/skills/scientific-writing/SKILL.md`.
