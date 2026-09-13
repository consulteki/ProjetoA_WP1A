# ADR-001: Run como unidade de agrupamento experimental

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-13 |
| Decisores | Grupo A — WP1A |
| Documentos relacionados | `docs/specs/SPEC-000-master.md` §6 (UE-01 a UE-03), §12 (INV-01, INV-02); `docs/project/requirements.md` RD-03, RD-04; `AGENTS.md` MET-R01, LEAK-R01, LEAK-R04 |

## Contexto

Os dados do Tennessee Eastman Process (TEP) são organizados em **execuções (`run`)** do processo simulado, cada uma contendo múltiplas amostras (linhas/instantes) sequenciais e temporalmente correlacionadas dentro da mesma execução. O problema de pesquisa exige comparar métodos de classificação multiclasse de forma que o desempenho medido reflita a capacidade real de generalização do modelo para **novas execuções do processo**, não a capacidade de memorizar padrões locais de uma execução já vista em parte.

Se a divisão treino/validação/teste for feita por amostra individual, é altamente provável que amostras de uma mesma execução apareçam em mais de uma partição, uma vez que amostras vizinhas no tempo dentro de uma execução são estatisticamente dependentes (autocorrelação temporal, dinâmica do processo). Isso caracteriza vazamento de informação e leva a métricas de desempenho artificialmente infladas.

## Decisão

A **execução do processo (`run`) é adotada como a unidade fundamental e obrigatória de agrupamento experimental**, para todos os fins de:

1. divisão dos dados em treino, validação e teste (nenhuma `run` pode ser fracionada entre partições);
2. definição de unidade experimental em qualquer teste estatístico de comparação entre modelos;
3. contagem de "número de observações independentes" em relatórios de significância estatística.

Cada amostra individual do dataset é tratada como pertencente a exatamente uma execução, identificada por um `run_id` explícito, registrado no manifesto de divisão (Entrega A3).

## Justificativa e alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Divisão por amostra individual (linha), estratificada por classe. | Ignora a correlação temporal dentro da execução; amostras da mesma `run` podem cair em treino e teste simultaneamente, inflando artificialmente o desempenho medido (vazamento). |
| Divisão temporal dentro da mesma execução (ex.: primeiros 80% do tempo para treino, últimos 20% para teste, dentro de cada `run`). | Ainda mistura a mesma execução em treino e teste; o modelo pode se beneficiar de padrões específicos daquela execução (nível de ruído, estado inicial) não generalizáveis a outras execuções. |
| Tratar cada amostra como unidade experimental independente para fins estatísticos (testes pareados amostra a amostra). | Viola a suposição de independência exigida pelos testes estatísticos (Friedman/Wilcoxon), pois amostras da mesma execução são correlacionadas — produziria significância estatística espúria. |

A adoção da execução como unidade é a única alternativa consistente com o problema de pesquisa (generalização entre execuções) e com os requisitos de integridade estatística da SPEC-000 (§10, EST-04/EST-05).

## Consequências

### Positivas
- Elimina uma classe inteira de vazamento de dados por construção, desde que a regra seja seguida.
- Torna as métricas de desempenho representativas da capacidade de generalização entre execuções, que é o que interessa operacionalmente para diagnóstico de falhas industriais.
- Torna os testes estatísticos (Friedman/Wilcoxon) metodologicamente válidos, com unidade experimental correta.

### Negativas / trade-offs
- Reduz o "número de unidades independentes" disponíveis para inferência estatística em comparação com tratar cada amostra como independente (menor poder estatístico nominal, porém o poder anterior seria espúrio).
- Exige infraestrutura explícita de rastreamento de `run_id` em todos os artefatos de dados, aumentando a complexidade de engenharia de dados.

### Riscos e mitigação
- **Risco:** algum componente do pipeline (ex.: uma função utilitária de terceiros) realiza split ou reamostragem por padrão sobre linhas individuais. **Mitigação:** toda função de split deve receber explicitamente `run_id` como chave de agrupamento e ser coberta por teste automatizado (TEST-R01) que rejeita qualquer overlap.

## Regras derivadas

- `AGENTS.md` MET-R01, LEAK-R01, LEAK-R04, TEST-R01.
- `docs/specs/SPEC-000-master.md` INV-01, INV-02, UE-01–UE-03.

## Critério de verificação

O manifesto de divisão (Entrega A3) deve permitir a verificação automatizada de que os conjuntos de `run_id` de treino, validação e teste são par a par disjuntos. Essa verificação é pré-condição de qualquer treinamento (ver ADR-002).
