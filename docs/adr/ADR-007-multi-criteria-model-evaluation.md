# ADR-007: Avaliação multicritério dos modelos (proibição de ranking por métrica única)

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-13 |
| Decisores | Grupo A — WP1A |
| Documentos relacionados | `docs/specs/SPEC-000-master.md` §9 (MET-01 a MET-13), §12 (INV-06, INV-07); `docs/project/requirements.md` Seção 5, RQ-04, RQ-05; `AGENTS.md` MET-R06 |

## Contexto

O TEP apresenta 21 classes com distribuição desbalanceada entre condição normal e diferentes falhas. Nesse cenário, a acurácia simples pode mascarar desempenho ruim em classes minoritárias, favorecendo modelos que apenas acertam bem as classes majoritárias. Além disso, o problema de pesquisa e as questões QP4/QP5 exigem explicitamente considerar o custo computacional (tempo de treino, tempo de inferência, tamanho do modelo) como parte da comparação entre modelos, não apenas seu desempenho preditivo.

## Decisão

1. Nenhuma afirmação de que um modelo é "o melhor" pode se basear exclusivamente na acurácia simples (MET-01).
2. Toda comparação e conclusão sobre desempenho entre os 6 modelos DEVE considerar, em conjunto, o conjunto completo de métricas definido na SPEC-000 (§9.3): acurácia, acurácia balanceada, precisão/revocação/F1 macro, F1 ponderada, MCC multiclasse, métricas por classe, matriz de confusão, tempo de treinamento, tempo de inferência e tamanho do modelo.
3. O relatório técnico (A7) e o manuscrito (A8) DEVEM apresentar explicitamente os casos em que o ranking por diferentes critérios diverge (ex.: melhor por acurácia ≠ melhor por F1 macro ≠ melhor por custo de inferência), como parte da resposta a QP4/QP5/H4.
4. Custo computacional é reportado e discutido para todo modelo comparado — nunca omitido, mesmo quando o foco da discussão é desempenho preditivo.

## Justificativa e alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Ranquear os modelos principalmente por acurácia, com as demais métricas como anexo secundário. | Viola diretamente INV-06 e a QP2 (equilíbrio entre classes); mascara desempenho ruim em classes minoritárias de falha, que são justamente o objeto de interesse prático do diagnóstico. |
| Usar apenas F1 macro como métrica única de decisão. | Embora mais robusta que acurácia a desbalanceamento, ainda ignora custo computacional, explicitamente exigido pelas QP4/QP5 e por H4. |
| Reportar custo computacional apenas informativamente, sem influenciar as conclusões sobre "melhor modelo". | Contradiz o objetivo específico OBJ-5 e a proibição explícita de omissão de custo computacional (RQ-05); H4 exige exatamente o cruzamento entre desempenho e custo. |
| Reportar uma métrica composta única (ex.: score ponderado arbitrário combinando F1 e custo) como critério oficial de decisão. | O WP1A não define tal métrica composta; combinar métricas heterogêneas em um único número exige pesos arbitrários não especificados no protocolo, o que introduziria um critério não rastreável à fonte normativa. A decisão apresenta o panorama multicritério explicitamente, sem colapsar em um único índice. |

## Consequências

### Positivas
- Reduz o risco de conclusões enganosas em um cenário de 21 classes desbalanceadas.
- Torna H4 (desacordo entre "melhor por acurácia" e "melhor por outras métricas/custo") diretamente testável e central na discussão dos resultados, em vez de um efeito colateral não discutido.
- Aumenta a utilidade prática do benchmark para quem for escolher um modelo sob restrições reais de custo computacional (QP5).

### Negativas / trade-offs
- Exige apresentação de resultados mais elaborada (múltiplas tabelas/figuras por critério) em vez de um único ranking simples.
- Pode não produzir uma resposta única e definitiva a "qual é o melhor modelo" — o resultado esperado é um panorama de trade-offs, não um vencedor absoluto.

### Riscos e mitigação
- **Risco:** pressão editorial (ao escrever o artigo) para simplificar a narrativa em torno de um único "modelo vencedor". **Mitigação:** este ADR, junto com INV-06/INV-07 e a Proibição 5 do `AGENTS.md`, torna a discussão multicritério um critério de aceite (CA-07), não uma escolha estilística de redação.

## Regras derivadas

- `AGENTS.md` MET-R06, Proibições 4 e 5.
- `docs/specs/SPEC-000-master.md` INV-06, INV-07, CA-05, CA-07.

## Critério de verificação

O relatório técnico (A7) e/ou manuscrito (A8) apresentam, lado a lado, ao menos: ranking por F1 macro, ranking por MCC e ranking por custo computacional (tempo de treino/inferência, tamanho do modelo) para os 6 modelos, com discussão explícita de eventuais divergências entre rankings.
