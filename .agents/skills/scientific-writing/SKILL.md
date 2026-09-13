---
name: scientific-writing
description: Redige o relatório técnico final e o manuscrito científico do WP1A, respondendo QP1–QP5 e avaliando H1–H4 com base nos artefatos versionados do benchmark.
---

# Skill: scientific-writing

**Fontes normativas:** `docs/specs/SPEC-000-master.md` §1, §3, §4, §11.4, §14; `docs/project/requirements.md` Seções 1, 9, 13; `docs/adr/ADR-007-multi-criteria-model-evaluation.md`; `AGENTS.md` MET-R06, MET-R07, DOC-R03, DOC-R05.

## Purpose

Consolidar os artefatos produzidos por todas as demais skills em dois documentos finais — o relatório técnico (A7) e o manuscrito científico (A8) — respondendo de forma explícita e fundamentada às questões de pesquisa (QP1–QP5), avaliando as hipóteses (H1–H4), e discutindo as ameaças à validade do estudo, sem introduzir nenhuma conclusão não rastreável aos resultados versionados.

## Preconditions

- As skills `ml-evaluation`, `statistical-analysis` e `scientific-figures` foram executadas e seus artefatos estão versionados e completos.
- Nenhuma pendência de verificação (checagem de leakage, recômputo de métricas) está em aberto para os resultados a serem citados.

## Inputs

- Resultados completos (A5), estatísticas de comparação (`statistical-analysis`), tabelas/figuras (A6, via `scientific-figures`).
- Registro de dataset canônico, manifesto de divisão e configurações de experimento (para as seções de método e reprodutibilidade).
- Estrutura obrigatória do manuscrito (SPEC-000 §11.4) e do relatório técnico.

## Procedure

1. Redigir a introdução e a fundamentação teórica sobre diagnóstico de falhas e o TEP, situando o problema de pesquisa (SPEC-000 §1.2).
2. Redigir a seção de trabalhos relacionados.
3. Redigir "materiais e métodos", descrevendo dataset canônico, unidade experimental, protocolo de divisão, pré-processamento e os seis modelos, com referência explícita às skills/ADRs que fundamentam cada decisão.
4. Redigir "protocolo reprodutível", detalhando sementes, versões, manifesto de divisão e configurações de experimento (ADR-003, ADR-005).
5. Redigir "resultados", incorporando as tabelas/figuras de `scientific-figures` e os testes estatísticos de `statistical-analysis`, respondendo explicitamente QP1–QP5.
6. Avaliar cada hipótese (H1–H4) individualmente, declarando corroborada ou refutada com base nos critérios definidos na SPEC-000 §4, citando os números exatos que sustentam a conclusão.
7. Redigir "discussão", interpretando os resultados sem atribuir causalidade física a importâncias de atributos (MET-R07) e sem basear conclusões de "melhor modelo" em métrica única (MET-R06).
8. Redigir "ameaças à validade", cobrindo validade interna, estatística, de constructo e externa, conforme SPEC-000 §14, referenciando explicitamente os mecanismos de mitigação já aplicados (ou as limitações não mitigadas, como poder estatístico reduzido).
9. Redigir "conclusões", sintetizando a resposta ao problema de pesquisa (SPEC-000 §1.2) e apontando o benchmark como referência para trabalhos futuros (modelos profundos, orientados por física, detecção precoce).
10. Compilar as referências bibliográficas.
11. Revisar o manuscrito quanto à aderência à estrutura obrigatória de 10 seções (SPEC-000 §11.4) e ao título provisório definido.
12. Consolidar o relatório técnico final (A7), cobrindo metodologia, protocolo e resultados de forma mais extensa/operacional que o manuscrito.

## Outputs

- **Entrega A7** — Relatório técnico final (PDF).
- **Entrega A8** — Manuscrito científico (LaTeX/Word), seguindo a estrutura de 10 seções da SPEC-000 §11.4.

## Validation

- Cada número citado no texto (A7/A8) é rastreável a um arquivo de resultado versionado (via `scientific-figures`/`ml-evaluation`), nunca reescrito "de memória".
- QP1–QP5 são respondidas de forma explícita e individualizada no texto.
- H1–H4 são avaliadas individualmente, com declaração explícita de corroboração ou refutação.
- A seção "Ameaças à validade" cobre as quatro categorias (interna, estatística, de constructo, externa).
- Nenhuma afirmação de causalidade física é feita a partir de importâncias de atributos.

## Failure Conditions

- Qualquer conclusão de "melhor modelo" baseada apenas em acurácia simples.
- QP1–QP5 ou H1–H4 não respondidas de forma explícita e individualizada.
- Ausência da seção "Ameaças à validade" ou cobertura incompleta das quatro categorias.
- Números no texto divergentes dos arquivos de resultado versionados.
- Interpretação causal de importâncias de atributos sobre o processo físico do TEP.
- Manuscrito que não segue a estrutura obrigatória de 10 seções (SPEC-000 §11.4).

## Definition of Done

- Entregas A7 e A8 produzidas, revisáveis e versionadas.
- Critérios de aceite CA-07, CA-08 e CA-10 (SPEC-000 §13) satisfeitos.
- Toda tabela, figura e afirmação quantitativa do texto é rastreável aos artefatos produzidos pelas demais skills.
- O documento está pronto para a Entrega A9 (apresentação), que sintetiza este conteúdo.
