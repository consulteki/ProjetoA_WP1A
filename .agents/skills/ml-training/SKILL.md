---
name: ml-training
description: Treina e seleciona hiperparâmetros para os seis modelos clássicos do benchmark WP1A, isolando o conjunto de teste (Etapa 5 do pipeline).
---

# Skill: ml-training

**Fontes normativas:** `docs/adr/ADR-002-test-set-isolation.md`; `docs/adr/ADR-005-experiment-configuration.md`; `docs/adr/ADR-006-model-family-selection.md`; `docs/specs/SPEC-000-master.md` §7.5, §8, §12 (INV-03, INV-05); `docs/project/requirements.md` RP-07, RP-08, RP-09, RMO-01..06; `AGENTS.md` LEAK-R03, LEAK-R06, LEAK-R07, EXP-R01..R07.

## Purpose

Treinar os seis modelos obrigatórios do benchmark (Regressão Logística, Árvore de Decisão, Random Forest, Gradient Boosting, SVM, XGBoost) sob configurações explícitas e versionadas, selecionando hiperparâmetros exclusivamente a partir de treino/validação, e consultando o conjunto de teste apenas após o congelamento de cada configuração final.

## Preconditions

- As skills `grouped-split` e `preprocessing` foram executadas; conjuntos de treino, validação e teste pré-processados estão disponíveis e rastreáveis.
- Uma configuração de experimento (ADR-005) foi definida para cada rodada de treinamento, referenciando dataset canônico, manifesto de divisão e semente.

## Inputs

- Conjuntos de treino e validação pré-processados (via `preprocessing`).
- Configuração de experimento versionada (`configs/`), incluindo espaço de busca de hiperparâmetros por modelo.
- Lista dos seis modelos obrigatórios (MOD-1 a MOD-6).

## Procedure

1. Para cada um dos seis modelos obrigatórios, instanciar o algoritmo conforme a configuração de experimento vigente.
2. Realizar a seleção de hiperparâmetros usando exclusivamente o conjunto de validação ou validação cruzada interna aplicada ao conjunto de treinamento — nunca o conjunto de teste.
3. Registrar, para cada tentativa de hiperparâmetro avaliada, o resultado na partição de validação (para rastreabilidade do processo de seleção).
4. Ao identificar a configuração de melhor desempenho em validação, **congelar** essa configuração: registrar explicitamente hiperparâmetros finais, semente e timestamp de congelamento.
5. Somente após o congelamento, treinar o modelo final com a configuração congelada sobre o conjunto de treinamento (mantendo a possibilidade de incluir a validação no treino final apenas se essa for uma decisão explícita e documentada da configuração, nunca implícita).
6. Consultar o conjunto de teste **uma única vez** por modelo, gerando as predições finais.
7. Medir e registrar o tempo de treinamento, o tempo de inferência e o tamanho do artefato de modelo salvo, no mesmo ambiente de execução.
8. Persistir o modelo treinado (`models/`) e a tabela de hiperparâmetros finais, associados ao identificador de experimento (ADR-005).
9. Caso um problema seja identificado após a consulta ao teste, **não reajustar** a configuração já congelada: abrir um novo identificador de experimento e repetir o processo desde o passo 1, preservando o histórico do experimento anterior.

## Outputs

- **Entrega A4** — Implementação/artefatos dos seis modelos treinados.
- Tabela de hiperparâmetros dos modelos (insumo 2 dos insumos do artigo).
- Predições em teste por modelo, tempos de treinamento/inferência e tamanho de modelo, para consumo por `ml-evaluation`.
- Registro do momento de congelamento de cada configuração, para auditoria de isolamento do teste.

## Validation

- Log/registro de execução demonstra ordem cronológica: seleção de hiperparâmetros (treino/validação) → congelamento → consulta única ao teste.
- Os seis modelos foram treinados sob o mesmo manifesto de divisão e o mesmo pipeline de pré-processamento (INV-03).
- Tempo de treinamento, tempo de inferência e tamanho do modelo foram coletados no mesmo ambiente/execução das métricas de desempenho (EXP-R05).

## Failure Conditions

- Qualquer consulta ao conjunto de teste antes do congelamento da configuração (viola LEAK-R03, INV-05).
- Reajuste de uma configuração já avaliada em teste, sem abertura de novo identificador de experimento (viola LEAK-R06).
- Omissão de qualquer um dos seis modelos obrigatórios.
- Uso de manifesto de divisão ou pipeline de pré-processamento diferente entre modelos (viola INV-03).
- Ausência de registro de hiperparâmetros finais, semente ou tempos de treino/inferência.

## Definition of Done

- Entrega A4 produzida para os seis modelos, com tabela de hiperparâmetros documentada.
- Critério de aceite CA-04 (SPEC-000 §13) satisfeito.
- Cada modelo tem um identificador de experimento rastreável (ADR-005), com evidência de isolamento do teste (ADR-002).
- Artefatos prontos para consumo por `ml-evaluation`.
