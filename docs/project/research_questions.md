# Questões de Pesquisa — WP1A

**Fonte:** `WP1A_SOURCE.pdf` (Seção 4); operacionalizadas em `docs/project/requirements.md` §1.3 e `docs/specs/SPEC-000-master.md` §3.

## Problema de pesquisa

> Dado um conjunto de dados multivariado proveniente da simulação do Tennessee Eastman Process, qual método clássico de aprendizado de máquina apresenta o melhor compromisso entre capacidade de classificação, equilíbrio entre classes, custo computacional, estabilidade e interpretabilidade no diagnóstico de falhas industriais?

## Questões de pesquisa

| ID | Questão | Evidência exigida para resposta |
|---|---|---|
| **QP1** | Quais algoritmos clássicos apresentam o melhor desempenho global na classificação das condições operacionais do TEP? | Tabela comparativa de métricas globais para os 6 modelos, com ranking explícito. |
| **QP2** | O desempenho global é consistente quando se considera o equilíbrio entre as 21 classes? | Comparação entre ranking por acurácia simples e ranking por acurácia balanceada/F1 macro/MCC. |
| **QP3** | Quais falhas são sistematicamente mais difíceis de diagnosticar? | Matrizes de confusão e análise das falhas mais confundidas, identificando classes com F1 por classe consistentemente baixo entre modelos. |
| **QP4** | Métodos mais complexos produzem ganhos suficientes para justificar maior custo computacional? | Cruzamento entre ganho de desempenho (F1 macro/MCC) e custo computacional (tempo de treinamento, tempo de inferência, tamanho do modelo). |
| **QP5** | Qual modelo apresenta o melhor compromisso entre desempenho, tempo de treinamento, tempo de inferência e tamanho do arquivo treinado? | Síntese multicritério cruzando desempenho e custo, reportada explicitamente nas conclusões. |

Estas questões são o critério-mestre de aceite do estudo: os artefatos definidos em `docs/specs/SPEC-000-master.md` §11 (Outputs) devem, em conjunto, ser suficientes para respondê-las com evidência quantitativa rastreável.

## Rastreabilidade

- Versão detalhada/verificável: `docs/project/requirements.md` §1.3.
- Operacionalização normativa: `docs/specs/SPEC-000-master.md` §3.
- Skill responsável pela resposta final: `.agents/skills/scientific-writing/SKILL.md`.
