---
name: exploratory-analysis
description: Realiza a análise exploratória do dataset canônico do TEP (Etapa 2 do pipeline WP1A), sem influenciar decisões de treino/teste.
---

# Skill: exploratory-analysis

**Fontes normativas:** `docs/specs/SPEC-000-master.md` §7.2; `docs/project/requirements.md` RP-02; Entrega A2.

## Purpose

Produzir uma caracterização estatística e visual do dataset canônico — estatísticas descritivas, distribuição das classes, variabilidade das variáveis, correlações, projeções por PCA e diferenças entre regime normal e regimes de falha — para orientar decisões metodológicas subsequentes (ex.: necessidade de padronização, presença de variáveis pouco informativas) sem, em nenhum momento, decidir hiperparâmetros ou tocar o conjunto de teste.

## Preconditions

- A skill `canonical-dataset` foi executada e o dataset canônico está registrado e referenciável.
- A skill `grouped-split` **ainda não precisa** ter sido executada para esta análise inicial de caracterização geral, mas qualquer inspeção que compare "treino vs. teste" só pode ocorrer **depois** de `grouped-split`, e mesmo assim sem usar essa inspeção para ajustar o treino (ver Failure Conditions).

## Inputs

- Dataset canônico (registro produzido por `canonical-dataset`).
- Relatório de auditoria A1, para contexto sobre qualidade dos dados.

## Procedure

1. Calcular estatísticas descritivas (média, desvio-padrão, mínimo, máximo, quartis) para cada uma das 52 variáveis de processo, globalmente e por classe.
2. Descrever a distribuição das 21 classes (contagem de amostras e de execuções por classe), evidenciando desbalanceamento.
3. Analisar a variabilidade das variáveis (variância, coeficiente de variação) para identificar variáveis quase constantes ou de alta dispersão.
4. Calcular a matriz de correlação entre variáveis de processo e identificar pares fortemente correlacionados.
5. Projetar os dados por PCA (ou técnica equivalente de redução de dimensionalidade) para inspeção visual da separabilidade entre classes.
6. Inspecionar diferenças de comportamento entre o regime normal e os regimes de falha (ex.: deslocamento de médias, mudança de variância, mudança de correlação entre variáveis).
7. Registrar observações qualitativas relevantes para as etapas seguintes (ex.: "falhas X e Y apresentam projeções PCA sobrepostas"), sem prescrever ainda uma resposta a QP3 (isso é responsabilidade de `ml-evaluation`).
8. Consolidar os resultados em notebook/relatório com figuras (Entrega A2).

## Outputs

- **Entrega A2** — Análise exploratória (notebook/figuras).
- Observações qualitativas documentadas, reaproveitáveis por `preprocessing` (ex.: necessidade de padronização) e por `scientific-writing` (Seção "Materiais e métodos"/"Discussão").

## Validation

- Os seis elementos do procedimento (estatísticas descritivas, distribuição de classes, variabilidade, correlações, PCA, comparação normal/falha) estão individualmente identificáveis no notebook/relatório A2.
- Nenhuma figura ou estatística usa dados fora do dataset canônico registrado.
- Caso a análise utilize a divisão treino/teste (produzida por `grouped-split`), ela é executada e descrita como análise **descritiva** — nenhuma conclusão desta etapa determina hiperparâmetros de modelo.

## Failure Conditions

- Uso desta análise para escolher, ainda que informalmente, hiperparâmetros de modelos ou features "vencedoras" a partir de inspeção do conjunto de teste.
- Cálculo de estatísticas/PCA sobre dados não canônicos (bypassa `canonical-dataset`).
- Ausência de qualquer um dos seis elementos obrigatórios do procedimento no artefato final.
- Conclusões de EDA apresentadas como decisão de pipeline definitiva sem passar pela skill `preprocessing`/`ml-training` correspondente.

## Definition of Done

- Entrega A2 produzida e revisável, cobrindo os seis elementos exigidos.
- Observações relevantes para pré-processamento e para a discussão do artigo estão documentadas e rastreáveis a esta skill.
- Nenhuma decisão de modelagem foi tomada nesta etapa com base no conjunto de teste.
