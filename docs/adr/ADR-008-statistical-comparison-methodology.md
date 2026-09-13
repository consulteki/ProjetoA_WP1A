# ADR-008: Metodologia de comparação estatística entre modelos

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-13 |
| Decisores | Grupo A — WP1A |
| Documentos relacionados | `docs/specs/SPEC-000-master.md` §10 (EST-01 a EST-05), §12 (INV-09); `docs/project/requirements.md` Seção 6 (RAE-01 a RAE-05); `AGENTS.md` EXP-R06 |

## Contexto

Comparar 6 modelos exige uma metodologia estatística que respeite a unidade experimental definida em ADR-001 (a execução, `run`, não a amostra individual) e que seja adequada a comparações múltiplas (6 modelos, potencialmente múltiplas sementes/partições). Uma prática comum e metodologicamente incorreta é aplicar testes de hipótese diretamente sobre predições por amostra, tratando observações temporalmente correlacionadas de uma mesma execução como se fossem independentes — o que infla artificialmente a significância estatística encontrada.

## Decisão

1. Sempre que houver resultados de múltiplas execuções independentes, sementes ou partições, são reportados **média, desvio-padrão e intervalo de confiança**.
2. A comparação estatística global entre os 6 modelos pode utilizar o **teste de Friedman**, seguido de procedimento pós-hoc apropriado quando a hipótese nula de igualdade entre modelos for rejeitada.
3. Comparações pareadas específicas entre dois modelos podem utilizar o **teste de Wilcoxon**, com correção para múltiplas comparações (ex.: Holm ou Bonferroni) quando várias comparações pareadas forem realizadas a partir do mesmo conjunto de resultados.
4. Toda análise estatística DEVE declarar explicitamente qual é a **unidade experimental** utilizada (a execução — ADR-001) e o número de unidades que entraram no teste.
5. É proibido tratar amostras/linhas temporalmente correlacionadas dentro de uma mesma execução como repetições estatisticamente independentes em qualquer teste de hipótese.

## Justificativa e alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Teste t pareado (ou equivalente) diretamente sobre as predições de cada amostra individual dos 6 modelos. | Viola a suposição de independência: amostras da mesma execução são correlacionadas (INV-09), o que infla artificialmente a significância estatística encontrada. |
| Comparar apenas os valores pontuais de métricas agregadas (uma tabela de números, sem teste de hipótese). | Insuficiente para o critério de avaliação acadêmica "Análise dos resultados" (peso 20% — SPEC-000 §11) e para responder QP1/QP2 com rigor estatístico, especialmente diante de diferenças pequenas entre modelos. |
| Aplicar correção de múltiplas comparações apenas quando "conveniente", sem regra fixa. | Introduz arbitrariedade e risco de inflação da taxa de falsos positivos ao reportar múltiplas comparações pareadas sem controle formal. |
| Comparar modelos usando apenas uma única partição treino/teste, sem qualquer replicação (semente/partição). | Impede o cálculo de média/desvio-padrão/IC (EST-01) e restringe a aplicabilidade dos testes de Friedman/Wilcoxon a comparações de amostra única; quando isso ocorrer por restrição de tempo/recursos, deve ser declarado explicitamente como limitação metodológica (ameaça à validade estatística), não tratado como equivalente a uma comparação com múltiplas repetições. |

## Consequências

### Positivas
- Garante que qualquer alegação de significância estatística entre modelos seja metodologicamente válida, com a unidade experimental correta.
- Fornece um procedimento padronizado (Friedman + pós-hoc; Wilcoxon + correção) aplicável de forma consistente entre todas as comparações do benchmark.

### Negativas / trade-offs
- Exige múltiplas execuções independentes (sementes e/ou partições) para que os testes tenham poder estatístico adequado; uma única rodada por modelo limita a inferência a comparação descritiva, devendo essa limitação ser declarada na seção de ameaças à validade (ver SPEC-000 §14).
- Aumenta a complexidade analítica do relatório/artigo em comparação com uma simples tabela de métricas pontuais.

### Riscos e mitigação
- **Risco:** restrições de tempo levam à execução de uma única partição/semente por modelo, impossibilitando testes estatísticos formais robustos. **Mitigação:** essa limitação deve ser reportada explicitamente como ameaça à validade estatística (SPEC-000 §14.2), e não deve ser disfarçada como comparação estatisticamente validada.

## Regras derivadas

- `AGENTS.md` EXP-R06.
- `docs/specs/SPEC-000-master.md` EST-01 a EST-05, INV-09.

## Critério de verificação

O relatório técnico (A7) e/ou manuscrito (A8) declaram explicitamente: a unidade experimental usada em cada teste estatístico, o número de unidades, o teste aplicado (Friedman/Wilcoxon) e, quando aplicável, o método de correção para múltiplas comparações.
