# ADR-002: Isolamento do conjunto de teste

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-13 |
| Decisores | Grupo A — WP1A |
| Documentos relacionados | `docs/specs/SPEC-000-master.md` §7.3, §7.5, §12 (INV-04, INV-05); `docs/project/requirements.md` RP-06, RP-08, RP-09; `AGENTS.md` §2 (LEAK-R02, LEAK-R03, LEAK-R05, LEAK-R06) |

## Contexto

O benchmark compara 6 famílias de modelos e depende de um processo de seleção de hiperparâmetros para cada uma. Existe risco metodológico relevante de que, direta ou indiretamente, informação do conjunto de teste influencie decisões de desenvolvimento (escolha de features, hiperparâmetros, critério de parada, limiares de decisão, ou mesmo reajuste após observar o resultado em teste). Esse fenômeno — "test set leakage" por reuso iterativo — produz estimativas de desempenho otimistas e não confiáveis, comprometendo diretamente a resposta às questões de pesquisa QP1–QP5 e a avaliação das hipóteses H1–H4.

Adicionalmente, transformações dependentes dos dados (padronização, normalização, codificação) podem vazar informação estatística do teste para o treino se forem ajustadas (`fit`) sobre a união de todas as partições.

## Decisão

1. O conjunto de teste é consultado **exatamente uma vez por configuração final de modelo**, e somente **após o congelamento** de todos os hiperparâmetros e decisões de pré-processamento daquele modelo.
2. A seleção de hiperparâmetros usa exclusivamente o conjunto de treinamento e/ou o conjunto de validação (incluindo validação cruzada interna aplicada ao treino) — nunca o teste.
3. Toda transformação dependente dos dados é ajustada (`fit`) exclusivamente no conjunto de treinamento e apenas aplicada (`transform`, sem reajuste) aos conjuntos de validação e teste.
4. Caso seja necessário revisar uma configuração após observar métricas de teste, isso constitui um **novo experimento** (novo identificador — ver ADR-005), nunca um ajuste silencioso da mesma configuração já avaliada em teste.
5. Qualquer agente (humano ou de IA) que identifique um caminho de código ou de processo que exponha o teste antes do congelamento deve interromper a tarefa e reportar o risco (ver `AGENTS.md`, LEAK-R07).

## Justificativa e alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Validação cruzada k-fold usando os mesmos dados de teste em algumas dobras ("teste" e "validação" intercambiáveis). | Borra a fronteira entre validação e teste, permitindo que informação de teste influencie indiretamente a seleção de modelo em alguma dobra. |
| Refinamento iterativo guiado pelo resultado em teste ("rodei no teste, ajusto, rodo de novo"). | É a forma mais direta de overfitting ao conjunto de teste; o teste deixa de medir generalização e passa a medir adequação a um conjunto específico já observado. Viola diretamente RP-09 e LEAK-R06. |
| Validação cruzada aninhada (*nested CV*) sem um conjunto de teste holdout explicitamente separado por execução. | O WP1A exige explicitamente um manifesto de divisão com partições nomeadas treino/validação/teste (Entrega A3); a ausência de um teste holdout fixo dificultaria a auditoria e a comparação direta entre os 6 modelos sob o mesmo teste. |
| Reajuste de scaler/encoder separadamente em cada partição (um `fit` por partição). | Introduz vazamento estatístico (a distribuição do teste influenciaria os parâmetros usados para transformar o próprio teste) e quebra a premissa de que o modelo "não viu" o teste antes da avaliação final. |

## Consequências

### Positivas
- Garante que as métricas finais reportadas (Seção 9 da SPEC-000) sejam estimativas não enviesadas do desempenho de generalização.
- Torna comparável e auditável o momento exato em que cada modelo "toca" o teste, permitindo checagem de conformidade por revisão de logs/experiment tracking.

### Negativas / trade-offs
- Reduz a flexibilidade de iteração rápida: um erro de configuração descoberto somente após consulta ao teste exige nova rodada completa registrada como novo experimento, não apenas um ajuste pontual.
- Exige disciplina de processo (checkpoint de congelamento) que deve ser reforçada por automação, não apenas por acordo entre os membros do grupo.

### Riscos e mitigação
- **Risco:** pipelines de biblioteca (ex.: buscas de hiperparâmetro automatizadas) que, por configuração padrão, recebem acidentalmente o conjunto de teste como entrada de validação. **Mitigação:** testes automatizados (TEST-R02) que verificam que os objetos de transformação e seleção de hiperparâmetros nunca recebem dados de teste como argumento de ajuste.

## Regras derivadas

- `AGENTS.md` MET-R05, LEAK-R02, LEAK-R03, LEAK-R05, LEAK-R06, LEAK-R07.
- `docs/specs/SPEC-000-master.md` INV-04, INV-05.

## Critério de verificação

Registro/log de execução do experimento demonstra, em ordem cronológica auditável: (1) ajuste de transformação apenas no treino; (2) seleção de hiperparâmetros restrita a treino/validação; (3) congelamento explícito da configuração; (4) consulta única e posterior ao teste. Qualquer inversão dessa ordem é não conformidade (ver `AGENTS.md`, Proibição 2).
