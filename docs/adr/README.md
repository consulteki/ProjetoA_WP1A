# Registro de Decisões Arquiteturais/Metodológicas (ADRs) — WP1A

Cada ADR é derivada exclusivamente de `docs/specs/SPEC-000-master.md`, de `docs/project/requirements.md` e do documento WP1A (`docs/project/WP1A_SOURCE.pdf`). As regras operacionais decorrentes destas decisões são vinculantes e estão consolidadas em `AGENTS.md` (raiz do repositório).

## Índice

| ADR | Título | Decisão em uma frase |
|---|---|---|
| [ADR-001](./ADR-001-run-as-group-unit.md) | Run como unidade de agrupamento experimental | A execução do processo (`run`), não a amostra individual, é a unidade de divisão de dados e de inferência estatística. |
| [ADR-002](./ADR-002-test-set-isolation.md) | Isolamento do conjunto de teste | O teste só é consultado uma vez, após o congelamento da configuração; nenhuma transformação ou seleção de hiperparâmetro pode usá-lo. |
| [ADR-003](./ADR-003-reproducibility.md) | Requisitos de reprodutibilidade | Semente, manifesto de divisão, versões de software, hiperparâmetros e resultados brutos são sempre registrados e versionados. |
| [ADR-004](./ADR-004-canonical-dataset.md) | Dataset canônico | Existe uma única fonte de dados oficial (documentada em A1); versões/subconjuntos alternativos não alimentam resultados finais. |
| [ADR-004-amendment-001](./ADR-004-amendment-001-canonical-freeze.md) | Congelamento `tep-canonical-v1` | Exclui classe 21, orienta `d00.dat` em memória, mantém duplicatas pré-falha; registro em `data/processed/`. |
| [ADR-005](./ADR-005-experiment-configuration.md) | Configuração de experimentos | Toda execução é definida por uma configuração explícita e versionada em `configs/`, com identificador único de experimento. |
| [ADR-006](./ADR-006-model-family-selection.md) | Seleção da família de modelos do benchmark | O benchmark compreende exatamente 6 modelos clássicos fixos, sob o mesmo protocolo. |
| [ADR-007](./ADR-007-multi-criteria-model-evaluation.md) | Avaliação multicritério dos modelos | Nenhum "melhor modelo" é declarado com base apenas em acurácia; custo computacional é sempre considerado. |
| [ADR-008](./ADR-008-statistical-comparison-methodology.md) | Metodologia de comparação estatística entre modelos | Friedman + pós-hoc e Wilcoxon + correção, sempre com a execução como unidade experimental. |

## Relação entre as ADRs

```
ADR-004 (dataset canônico)
   │
   ▼
ADR-001 (run como unidade) ──► ADR-002 (isolamento do teste)
   │                                  │
   ▼                                  ▼
ADR-005 (configuração de experimento) ──► ADR-003 (reprodutibilidade)
   │
   ▼
ADR-006 (seleção de modelos) ──► ADR-007 (avaliação multicritério) ──► ADR-008 (comparação estatística)
```

Ver também `docs/protocols/experimental_protocol.md` (síntese operacional de ADR-001/ADR-002) e `docs/protocols/reproducibility_protocol.md` (síntese operacional de ADR-003/ADR-005).
