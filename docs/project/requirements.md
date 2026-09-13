# Requisitos do Subprojeto WP1A

**Benchmark Reproduzível de Métodos Clássicos de Aprendizado de Máquina para Diagnóstico de Falhas Industriais**

| Campo | Valor |
|---|---|
| Disciplina | MEI0028 – Modelagem e Simulação |
| Programa | Pós-Graduação, Pontifícia Universidade Católica de Goiás |
| Código do subprojeto | WP1A |
| Grupo responsável | Grupo A |
| Professor responsável | Clarimar José Coelho |
| Base experimental | Tennessee Eastman Process (TEP) |
| Produto científico previsto | Artigo para periódico técnico-científico |
| Documento de origem | `MEI0028_WP1A_3.pdf` |
| Natureza | Projeto aplicado de modelagem, simulação, análise de dados e inteligência artificial |

Este documento traduz o conteúdo do WP1A em requisitos verificáveis (científicos, metodológicos e técnicos), sem prescrever ou conter implementação de código. Cada requisito possui um identificador único, uma descrição normativa (DEVE/DEVERÁ = obrigatório; PODERÁ/poderá = opcional condicional) e um critério objetivo de verificação, de modo a permitir auditoria de conformidade ao final do subprojeto.

---

## 1. Contexto e problema de pesquisa

### 1.1 Contextualização

Sistemas industriais modernos são compostos por variáveis fortemente acopladas, com comportamento dinâmico, perturbações operacionais e múltiplos modos de falha. O diagnóstico automático de falhas é tratado como tarefa de classificação multiclasse que distingue a condição normal de diferentes anomalias de processo. O Tennessee Eastman Process (TEP) é adotado como ambiente de referência por representar, de forma simulada, um processo químico multivariado, não linear e sujeito a falhas de diferentes naturezas.

O subprojeto propõe a construção de um benchmark reproduzível de métodos clássicos de aprendizado de máquina. O foco não é apenas identificar o algoritmo de maior acurácia, mas comparar desempenho preditivo, equilíbrio entre classes, custo computacional, robustez, interpretabilidade e viabilidade de aplicação em sistemas industriais. O estudo trata o processo industrial como um sistema dinâmico observado por variáveis de estado e de operação, e os modelos de classificação são avaliados como mecanismos computacionais de diagnóstico construídos a partir das respostas simuladas do sistema sob condições normais e de falha.

### 1.2 Problema de pesquisa

> Dado um conjunto de dados multivariado proveniente da simulação do Tennessee Eastman Process, qual método clássico de aprendizado de máquina apresenta o melhor compromisso entre capacidade de classificação, equilíbrio entre classes, custo computacional, estabilidade e interpretabilidade no diagnóstico de falhas industriais?

Este problema é o critério-mestre de aceitação do subprojeto: o conjunto de entregas e análises produzidas (Seção 6) deve, em conjunto, ser suficiente para respondê-lo de forma fundamentada em evidência quantitativa.

### 1.3 Questões de pesquisa (QP)

| ID | Questão | Evidência exigida para resposta |
|---|---|---|
| **QP1** | Quais algoritmos clássicos apresentam o melhor desempenho global na classificação das condições operacionais do TEP? | Tabela comparativa de métricas globais (Seção 5) para os 6 modelos da Tabela de modelos (Seção 3), com ranking explícito. |
| **QP2** | O desempenho global é consistente quando se considera o equilíbrio entre as 21 classes? | Comparação entre acurácia simples/acurácia balanceada/F1 macro e métricas por classe; discussão de divergências entre ranking por acurácia e ranking por métricas balanceadas. |
| **QP3** | Quais falhas são sistematicamente mais difíceis de diagnosticar? | Matrizes de confusão e análise das falhas mais confundidas (Seção 6, item A6/insumo 8), identificando classes com F1 por classe consistentemente baixo entre modelos. |
| **QP4** | Métodos mais complexos produzem ganhos suficientes para justificar maior custo computacional? | Cruzamento entre ganho de desempenho (F1 macro/MCC) e custo computacional (tempo de treinamento, tempo de inferência, tamanho do modelo) — gráfico de custo computacional (Seção 6, insumo 7). |
| **QP5** | Qual modelo apresenta o melhor compromisso entre desempenho, tempo de treinamento, tempo de inferência e tamanho do arquivo treinado? | Síntese multicritério cruzando as métricas de desempenho (Seção 5) com as métricas de custo (Seção 5), reportada de forma explícita nas conclusões do artigo/relatório. |

### 1.4 Hipóteses de pesquisa

| ID | Hipótese | Condição de corroboração (verificável) | Condição de refutação |
|---|---|---|---|
| **H1** | Métodos de conjunto baseados em árvores apresentam desempenho superior aos classificadores lineares em razão das relações não lineares entre as variáveis do processo. | Random Forest, Gradient Boosting e/ou XGBoost superam Regressão Logística em F1 macro e/ou MCC no conjunto de teste. | Regressão Logística iguala ou supera todos os métodos de conjunto baseados em árvores nas métricas citadas. |
| **H2** | XGBoost e Random Forest apresentam maior F1 macro e MCC do que Regressão Logística e Árvore de Decisão isolada. | F1 macro(XGBoost) > F1 macro(Regressão Logística, Árvore de Decisão) **e** F1 macro(Random Forest) > F1 macro(Regressão Logística, Árvore de Decisão); mesma relação para MCC. | Qualquer uma das quatro desigualdades acima é violada no conjunto de teste. |
| **H3** | A Regressão Logística permanece competitiva em custo computacional e interpretabilidade, embora apresente menor capacidade de separar falhas com padrões sobrepostos. | Regressão Logística está entre os modelos de menor tempo de treinamento/inferência e menor tamanho de modelo, e apresenta F1 por classe reduzido nas classes de falha com maior sobreposição identificadas em QP3. | Regressão Logística não figura entre os métodos de menor custo computacional, ou apresenta desempenho equivalente aos métodos não lineares em todas as classes. |
| **H4** | O melhor modelo segundo acurácia não necessariamente será o melhor quando considerados F1 macro, MCC e custo de inferência. | O modelo com maior acurácia simples não coincide com o modelo com melhor F1 macro, melhor MCC, ou melhor relação desempenho/custo de inferência. | O mesmo modelo lidera simultaneamente acurácia, F1 macro, MCC e custo de inferência. |

### 1.5 Objetivos

**Objetivo geral:** desenvolver e avaliar um benchmark reproduzível de algoritmos clássicos de aprendizado de máquina para diagnóstico multiclasse de falhas no Tennessee Eastman Process.

**Objetivos específicos** (rastreados aos requisitos das Seções 2–6):

1. Auditar e documentar a base de dados utilizada no estudo → Seção 4.1, Entrega A1.
2. Aplicar um protocolo único de divisão entre treinamento, validação e teste, evitando vazamento entre execuções do processo → Seção 4.3, Entrega A3.
3. Treinar Regressão Logística, Árvore de Decisão, Random Forest, Gradient Boosting, SVM e XGBoost → Seção 3, Entrega A4.
4. Avaliar os modelos por métricas globais e específicas por classe → Seção 5, Entrega A5.
5. Comparar tempos de treinamento, tempos de inferência e tamanho dos modelos → Seção 5, Entrega A5.
6. Identificar falhas com maior grau de confusão → QP3, Entrega A6.
7. Produzir tabelas, figuras, arquivos de resultados e documentação reproduzível → Seção 6, Entregas A5–A7.
8. Elaborar um artigo científico com os resultados do benchmark → Entrega A8.

---

## 2. Requisitos de dados

| ID | Requisito | Critério de verificação |
|---|---|---|
| **RD-01** | O experimento DEVE utilizar os dados do Tennessee Eastman Process disponibilizados em arquivos de treinamento e teste, contendo execuções sem falha e execuções com falhas induzidas. | Arquivos de origem identificados e documentados no relatório de auditoria (A1), com indicação de execuções normais e de falha presentes. |
| **RD-02** | A base de dados utilizada DEVE conter 52 variáveis de processo e 21 classes (condição normal + 20 condições de falha). | Contagem de colunas de variáveis = 52 e contagem de classes distintas = 21, reportada no relatório de auditoria (A1). |
| **RD-03** | A unidade independente de divisão dos dados DEVE ser a execução do processo (*run*). | Manifesto de divisão (A3) referencia identificadores de execução (`run_id` ou equivalente), não índices de amostra individual. |
| **RD-04** | Amostras pertencentes à mesma execução NÃO PODEM aparecer simultaneamente nos conjuntos de treinamento e teste. | Verificação automatizada de interseção vazia entre o conjunto de `run_id` de treino e o conjunto de `run_id` de teste, registrada no manifesto de divisão (A3). |
| **RD-05** | Nenhuma linha temporal correlacionada pode ser tratada como repetição estatisticamente independente. | Descrição explícita, no relatório técnico, da unidade experimental adotada (execução, não amostra/instante) e de como essa distinção foi respeitada na análise estatística (Seção 5.6). |

---

## 3. Requisitos de modelos avaliados

O benchmark DEVE incluir, no mínimo, os seis modelos a seguir, cada qual desempenhando o papel indicado:

| ID | Modelo | Papel no benchmark |
|---|---|---|
| **RMO-01** | Regressão Logística | Baseline linear, interpretável e de baixo custo computacional. |
| **RMO-02** | Árvore de Decisão | Modelo não linear simples, com regras diretamente interpretáveis. |
| **RMO-03** | Random Forest | Método de conjunto com redução de variância e boa robustez. |
| **RMO-04** | Gradient Boosting | Referência de boosting sequencial com árvores rasas. |
| **RMO-05** | SVM | Classificador de margem máxima; implementação inicial deve ser escalável. |
| **RMO-06** | XGBoost | Baseline forte de boosting otimizado e regularizado. |

**Critério de verificação (conjunto):** o repositório de resultados (A4/A5) contém, para cada um dos 6 modelos acima, artefato treinado, hiperparâmetros documentados e métricas completas (Seção 5); a ausência de qualquer um dos seis constitui não conformidade.

---

## 4. Requisitos de protocolo experimental

O protocolo experimental é composto por seis etapas sequenciais e obrigatórias, cada uma com critérios de conclusão verificáveis.

### 4.1 Etapa 1 — Auditoria dos dados

| ID | Requisito | Critério de verificação |
|---|---|---|
| **RP-01** | A auditoria DEVE verificar e documentar: arquivos disponíveis; quantidade de linhas e colunas; nomes, tipos e significado das variáveis; distribuição das classes; quantidade de execuções por classe; valores ausentes, infinitos ou inconsistentes; possíveis duplicações; e relação entre arquivos, classes e identificadores de execução. | Relatório de auditoria (A1) contém uma seção/tabela para cada um dos oito itens listados, com resultado explícito (inclusive "nenhum encontrado", quando aplicável). |

### 4.2 Etapa 2 — Análise exploratória

| ID | Requisito | Critério de verificação |
|---|---|---|
| **RP-02** | A análise exploratória DEVE incluir estatísticas descritivas, distribuição das classes, variabilidade das variáveis, correlações, projeções por PCA e inspeção de diferenças entre o regime normal e os regimes de falha. | Entrega A2 (notebook/figuras) contém, individualmente identificáveis, cada um dos seis elementos citados. |

### 4.3 Etapa 3 — Divisão experimental

| ID | Requisito | Critério de verificação |
|---|---|---|
| **RP-03** | A divisão dos dados DEVE ser realizada por execução completa (não por amostra individual), segundo o protocolo-base: treinamento (ajuste dos modelos), validação (seleção de hiperparâmetros, com execuções independentes do treino) e teste (execuções nunca usadas durante o desenvolvimento). | Manifesto de divisão (A3) lista, para cada partição (treino/validação/teste), o conjunto de `run_id` associado, sem sobreposição entre partições. |
| **RP-04** | A semente aleatória, a lista de execuções e o manifesto de divisão DEVEM ser salvos para garantir repetibilidade. | Arquivo(s) de manifesto (A3, formato CSV/JSON) contendo semente(s) utilizada(s) e lista completa de execuções por partição, versionado no repositório. |

### 4.4 Etapa 4 — Pré-processamento

| ID | Requisito | Critério de verificação |
|---|---|---|
| **RP-05** | O pipeline principal DEVE utilizar as decisões já estabelecidas na infraestrutura comum do projeto. | Documentação técnica referencia explicitamente a infraestrutura/pipeline comum adotada. |
| **RP-06** | Transformações dependentes dos dados (ex.: padronização) DEVEM ser ajustadas exclusivamente no conjunto de treinamento e apenas aplicadas (transform) aos conjuntos de validação e teste. | Inspeção do pipeline documentado/registro de execução confirma que os parâmetros de transformação (médias, desvios-padrão, etc.) são estimados somente a partir do conjunto de treinamento. |

### 4.5 Etapa 5 — Treinamento e seleção

| ID | Requisito | Critério de verificação |
|---|---|---|
| **RP-07** | Cada algoritmo DEVE ser treinado sob condições documentadas. | Tabela de hiperparâmetros dos modelos (insumo obrigatório do artigo, Seção 6) documenta as condições de treinamento de cada um dos 6 modelos. |
| **RP-08** | A seleção de hiperparâmetros DEVE usar apenas o conjunto de validação ou validação cruzada interna aplicada ao conjunto de treinamento. | Registro de seleção de hiperparâmetros não referencia, em nenhum momento, o conjunto de teste. |
| **RP-09** | O conjunto de teste SÓ PODE ser consultado após o congelamento da configuração final de cada modelo. | Log/registro de execução demonstra ordem cronológica: (1) congelamento de hiperparâmetros → (2) avaliação única em teste, sem reajuste posterior. |

### 4.6 Etapa 6 — Avaliação final

| ID | Requisito | Critério de verificação |
|---|---|---|
| **RP-10** | Para cada classe *c* (de um total de *C* classes), DEVEM ser calculadas precisão, revocação e F1. | Tabela de métricas por classe (A5/insumo 4) contém precisão, revocação e F1 para cada uma das 21 classes e para cada um dos 6 modelos. |
| **RP-11** | A F1 macro DEVE ser calculada como $F1_{macro} = \frac{1}{C}\sum_{c=1}^{C} F1_c$. | Valor de F1 macro reportado é reprodutível a partir da média aritmética simples dos F1 por classe reportados (verificação numérica). |
| **RP-12** | A acurácia balanceada DEVE ser calculada como $BA = \frac{1}{C}\sum_{c=1}^{C} \frac{TP_c}{TP_c + FN_c}$. | Valor de acurácia balanceada reportado é reprodutível a partir dos TP e FN por classe da matriz de confusão (verificação numérica). |
| **RP-13** | O coeficiente de correlação de Matthews multiclasse (MCC) DEVE ser reportado como métrica adicional, por fornecer avaliação mais informativa quando há erros distribuídos entre várias classes. | Valor de MCC multiclasse presente na tabela comparativa de métricas globais (A5) para cada um dos 6 modelos. |

---

## 5. Requisitos de métricas obrigatórias

O conjunto de resultados DEVE reportar, para cada um dos 6 modelos, todas as métricas a seguir (RMT-01 a RMT-12):

| ID | Métrica |
|---|---|
| **RMT-01** | Acurácia |
| **RMT-02** | Acurácia balanceada |
| **RMT-03** | Precisão macro |
| **RMT-04** | Revocação macro |
| **RMT-05** | F1 macro |
| **RMT-06** | F1 ponderada |
| **RMT-07** | MCC multiclasse |
| **RMT-08** | Matriz de confusão |
| **RMT-09** | Métricas por classe (precisão, revocação, F1 — 21 classes) |
| **RMT-10** | Tempo de treinamento |
| **RMT-11** | Tempo de inferência |
| **RMT-12** | Tamanho do modelo salvo |
| **RMT-13** | Consumo de memória, quando disponível (opcional/condicional) |

**Critério de verificação:** tabela comparativa de métricas globais (A5, insumo 3) e tabela de métricas por classe (insumo 4) contêm colunas/valores para RMT-01 a RMT-12 para cada um dos 6 modelos; ausência de RMT-13 é aceitável somente se justificada por indisponibilidade técnica.

---

## 6. Requisitos de análise estatística

| ID | Requisito | Critério de verificação |
|---|---|---|
| **RAE-01** | Sempre que houver resultados provenientes de múltiplas execuções independentes, sementes ou partições, DEVEM ser reportados média, desvio-padrão e intervalo de confiança. | Tabelas de resultados agregados apresentam explicitamente média ± desvio-padrão (ou IC) sempre que há repetições. |
| **RAE-02** | A comparação estatística entre modelos PODERÁ utilizar o teste de Friedman seguido por procedimento pós-hoc apropriado. | Se aplicado, relatório/artigo documenta estatística do teste de Friedman e o procedimento pós-hoc utilizado. |
| **RAE-03** | Comparações pareadas específicas PODERÃO utilizar o teste de Wilcoxon com correção para múltiplas comparações. | Se aplicado, relatório/artigo documenta o método de correção (ex.: Bonferroni, Holm) utilizado nas comparações pareadas. |
| **RAE-04** | A unidade experimental DEVE ser explicitada em toda inferência estatística. | Texto do relatório/artigo declara explicitamente qual é a unidade experimental (execução do processo) em cada teste estatístico aplicado. |
| **RAE-05** | Amostras/linhas temporalmente correlacionadas NÃO PODEM ser tratadas como repetições estatisticamente independentes. | Nenhum teste estatístico do relatório trata observações individuais (instantes) dentro de uma mesma execução como amostras i.i.d.; a granularidade declarada é a execução. |

---

## 7. Restrições metodológicas e riscos a mitigar

Os itens a seguir constituem restrições de conformidade — sua ocorrência representa falha do protocolo e DEVE ser ativamente evitada e auditável:

| ID | Restrição (o que NÃO pode ocorrer) | Como verificar a ausência |
|---|---|---|
| **RQ-01** | Vazamento de dados entre execuções (mesma `run` em treino e teste). | Interseção vazia de `run_id` entre partições (ver RD-04). |
| **RQ-02** | Ajuste de hiperparâmetros com base no conjunto de teste. | Registro de tuning referencia apenas treino/validação (ver RP-08). |
| **RQ-03** | Comparação injusta entre modelos (ex.: protocolos, splits ou pré-processamento diferentes por modelo). | Todos os 6 modelos utilizam o mesmo manifesto de divisão (A3) e o mesmo pipeline de pré-processamento (RP-05/RP-06). |
| **RQ-04** | Uso exclusivo de acurácia como métrica de decisão. | Conclusões do artigo/relatório fundamentam-se em conjunto de métricas (Seção 5), não apenas em RMT-01. |
| **RQ-05** | Omissão do custo computacional na comparação entre modelos. | RMT-10, RMT-11 e RMT-12 reportados e discutidos nas conclusões (QP4/QP5). |
| **RQ-06** | Inferência estatística baseada em amostras temporalmente correlacionadas tratadas como independentes. | Ver RAE-04/RAE-05. |
| **RQ-07** | Interpretação causal indevida de importâncias de atributos. | Texto do artigo/relatório qualifica importâncias de atributos como associativas/descritivas do modelo, não como evidência causal do processo físico. |
| **RQ-08** | Falta de registro das versões de software e sementes aleatórias. | Metadados do ambiente computacional (Entrega, insumo 10) documentam versões de bibliotecas/linguagem e sementes utilizadas. |

---

## 8. Entregas do grupo (A1–A9)

Cada entrega abaixo constitui um requisito de produto verificável por presença, formato e conteúdo mínimo.

| ID | Entrega | Formato exigido | Conteúdo mínimo verificável |
|---|---|---|---|
| **A1** | Relatório de auditoria da base | PDF/CSV | Cobre todos os itens de RP-01. |
| **A2** | Análise exploratória | Notebook/figuras | Cobre todos os itens de RP-02. |
| **A3** | Manifesto da divisão por execução | CSV/JSON | Cobre RD-03, RD-04, RP-03, RP-04 (lista de `run_id` por partição e semente). |
| **A4** | Implementação dos seis modelos | Python | Presença e treinamento documentado dos 6 modelos da Seção 3 (RMO-01 a RMO-06). Observação: esta entrega refere-se à existência/documentação da implementação prevista pelo WP1A — este documento de requisitos não prescreve nem contém código. |
| **A5** | Resultados completos | CSV/JSON | Todas as métricas RMT-01 a RMT-12 (Seção 5), para cada um dos 6 modelos. |
| **A6** | Figuras e tabelas do artigo | PNG/PDF/LaTeX | Ao menos: tabela de caracterização da base, tabela de hiperparâmetros, tabela comparativa de métricas globais, tabela de métricas por classe, matrizes de confusão, gráfico comparativo de F1 macro e MCC, gráfico de custo computacional, análise das falhas mais confundidas (itens 1–8 da Seção 12 do WP1A). |
| **A7** | Relatório técnico final | PDF | Consolida metodologia, protocolo, resultados e conclusões conforme Seções 1–7 deste documento. |
| **A8** | Manuscrito científico | LaTeX/Word | Segue a estrutura sugerida (Seção 9 deste documento) e título provisório (Seção 10). |
| **A9** | Apresentação do projeto | PDF/PPTX | Sintetiza problema, hipóteses, protocolo, resultados e conclusões. |

Insumos mínimos adicionais exigidos para o artigo (não numerados como entregas formais, mas obrigatórios como conteúdo de A5/A6):

9. Arquivos CSV com resultados brutos.
10. Metadados do ambiente computacional (versões de software, sementes — cobre RQ-08).
11. Repositório com scripts numerados e instruções de execução (estrutura mínima descrita na Seção 9 deste documento).

---

## 9. Estrutura sugerida do artigo científico

O manuscrito (Entrega A8) DEVE seguir a seguinte estrutura, na ordem indicada:

1. Introdução
2. Fundamentação sobre diagnóstico de falhas e TEP
3. Trabalhos relacionados
4. Materiais e métodos
5. Protocolo reprodutível
6. Resultados
7. Discussão
8. Ameaças à validade
9. Conclusões
10. Referências

**Critério de verificação:** sumário do manuscrito contém as 10 seções acima, nesta ordem ou ordem funcionalmente equivalente justificada.

### 9.1 Título provisório

- Português: *"Benchmark reproduzível de métodos clássicos de aprendizado de máquina para diagnóstico de falhas no Tennessee Eastman Process"*
- Inglês: *"A Reproducible Benchmark of Classical Machine Learning Methods for Fault Diagnosis in the Tennessee Eastman Process"*

---

## 10. Cronograma sugerido (referência de acompanhamento)

| Atividade | Semanas |
|---|---|
| Revisão e auditoria | 1–2 |
| EDA e preparação | 2–3 |
| Treinamento dos modelos | 3–5 |
| Avaliação e estatística | 5–6 |
| Geração de figuras e tabelas | 6–7 |
| Redação do artigo | 4–8 |
| Apresentação final | 8 |

Este cronograma é referencial; não constitui critério de aceitação técnica, mas pode ser usado para verificação de andamento.

---

## 11. Critérios de avaliação acadêmica

A avaliação do subprojeto pelo professor responsável segue os pesos abaixo, aplicáveis ao conjunto das entregas (Seção 8):

| Critério | Peso | Requisitos associados |
|---|---|---|
| Correção metodológica e prevenção de vazamento | 20% | RD-03, RD-04, RP-03, RP-04, RP-08, RP-09, RQ-01, RQ-02, RQ-03 |
| Qualidade da implementação e reprodutibilidade | 20% | RMO-01–06, RP-05–RP-07, RQ-08, Seção 12 (estrutura do repositório) |
| Análise dos resultados | 20% | RMT-01–13, RAE-01–05, QP1–QP5, H1–H4 |
| Qualidade das figuras, tabelas e documentação | 15% | A1, A2, A6, insumos 9–11 |
| Relatório e manuscrito científico | 15% | A7, A8, Seção 9 (estrutura do artigo) |
| Apresentação e domínio do tema | 10% | A9 |
| **Total** | **100%** | — |

---

## 12. Estrutura mínima do repositório

O repositório do projeto DEVE conter, no mínimo, a seguinte estrutura de diretórios e arquivos:

```
ProjetoA_WP1A/
|-- data/
|   |-- raw/
|   |-- processed/
|-- src/
|-- configs/
|-- models/
|-- results/
|   |-- tables/
|   |-- figures/
|   |-- predictions/
|   |-- metadata/
|-- reports/
|-- article/
|-- README.md
|-- requirements.txt
```

**Critério de verificação:** inspeção direta do repositório confirma a presença de todos os diretórios/arquivos listados, ainda que inicialmente vazios (com placeholder), antes do início do treinamento dos modelos.

---

## 13. Resultados esperados (critério de sucesso global do subprojeto)

O subprojeto é considerado bem-sucedido se, ao final, forem produzidos, de forma auditável:

1. Um panorama confiável do comportamento das seis famílias clássicas de aprendizado de máquina (Seção 3) no diagnóstico de falhas do TEP.
2. A identificação explícita do melhor modelo global (resposta a QP1).
3. A identificação explícita dos melhores modelos sob restrições de custo computacional e de interpretabilidade (resposta a QP4/QP5, H3).
4. A identificação explícita das classes de falha que permanecem difíceis de separar (resposta a QP3).
5. Um artigo científico (A8) apto a servir de referência clássica para comparações futuras com modelos profundos, métodos orientados pela física e estratégias de detecção precoce.

---

## 14. Matriz de rastreabilidade (síntese)

| Elemento de origem (WP1A) | Seção deste documento |
|---|---|
| Problema de pesquisa | 1.2 |
| QP1–QP5 | 1.3 |
| H1–H4 | 1.4 |
| Objetivo geral e específicos | 1.5 |
| Base de dados | 2 |
| Modelos avaliados | 3 |
| Protocolo experimental (Etapas 1–6) | 4 |
| Métricas | 5 |
| Análise estatística | 6 |
| Riscos e cuidados metodológicos | 7 |
| Entregas A1–A9 | 8 |
| Estrutura do artigo / título provisório | 9 |
| Cronograma | 10 |
| Critérios de avaliação acadêmica | 11 |
| Estrutura mínima do repositório | 12 |
| Resultados esperados | 13 |

---

## 15. Observações finais

O WP1A deve ser conduzido como um benchmark científico, e não apenas como uma atividade de treinamento de classificadores. Todas as decisões (auditoria, divisão de dados, pré-processamento, seleção de hiperparâmetros, métricas e testes estatísticos) DEVEM ser rastreáveis e justificadas nos artefatos correspondentes (Seção 8). O produto principal do grupo é um protocolo reprodutível capaz de sustentar a comparação entre modelos clássicos e servir de referência para os demais subprojetos da linha de pesquisa "Diagnóstico Inteligente de Falhas em Sistemas Dinâmicos Industriais".

Este documento de requisitos não implementa nenhum código e não deve ser interpretado como especificação de arquitetura de software; ele define o que deve ser verdadeiro ao final do subprojeto para que este seja considerado conforme ao WP1A.

### Referências citadas no WP1A

1. DOWNS, J. J.; VOGEL, E. F. A plant-wide industrial process control problem. *Computers & Chemical Engineering*, v. 17, n. 3, p. 245–255, 1993.
2. CHIANG, L. H.; RUSSELL, E. L.; BRAATZ, R. D. *Fault Detection and Diagnosis in Industrial Systems*. London: Springer, 2001.
3. BREIMAN, L. Random forests. *Machine Learning*, v. 45, p. 5–32, 2001.
4. FRIEDMAN, J. H. Greedy function approximation: a gradient boosting machine. *The Annals of Statistics*, v. 29, n. 5, p. 1189–1232, 2001.
5. CHEN, T.; GUESTRIN, C. XGBoost: a scalable tree boosting system. In: *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*. 2016. p. 785–794.
