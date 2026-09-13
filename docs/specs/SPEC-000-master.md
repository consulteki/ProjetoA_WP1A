# SPEC-000 — Especificação Mestra do Benchmark WP1A

| Campo | Valor |
|---|---|
| ID da especificação | SPEC-000-master |
| Título | Benchmark reproduzível de métodos clássicos de aprendizado de máquina para diagnóstico de falhas no Tennessee Eastman Process |
| Subprojeto de origem | WP1A |
| Disciplina | MEI0028 – Modelagem e Simulação |
| Grupo responsável | Grupo A |
| Status | Aprovada como referência normativa para os demais documentos de especificação (SPEC-0xx) do subprojeto |
| Fontes normativas exclusivas | `MEI0028_WP1A_3.pdf` (documento WP1A); `docs/project/requirements.md` |
| Natureza deste documento | Especificação. Não contém nem prescreve implementação de código. |

Esta especificação consolida, em um único documento mestre, as decisões de escopo, método e critérios de aceite necessárias para que qualquer subespecificação ou artefato técnico derivado (dados, pipeline, modelos, avaliação, artigo) seja implementado de forma consistente com o WP1A. Onde houver conflito aparente entre esta SPEC e `requirements.md`, prevalece o texto do WP1A; `requirements.md` é usado como fonte de identificadores (RD, RMO, RP, RMT, RAE, RQ, A1–A9) para rastreabilidade.

---

## 1. Objetivo

### 1.1 Objetivo geral

Desenvolver e avaliar um benchmark reproduzível de algoritmos clássicos de aprendizado de máquina para diagnóstico multiclasse de falhas no Tennessee Eastman Process (TEP), comparando os métodos não apenas por acurácia, mas por capacidade preditiva, equilíbrio entre classes, custo computacional, robustez e interpretabilidade.

### 1.2 Objetivos específicos

| ID | Objetivo específico |
|---|---|
| OBJ-1 | Auditar e documentar a base de dados utilizada no estudo. |
| OBJ-2 | Aplicar um protocolo único de divisão entre treinamento, validação e teste, evitando vazamento entre execuções do processo. |
| OBJ-3 | Treinar Regressão Logística, Árvore de Decisão, Random Forest, Gradient Boosting, SVM e XGBoost. |
| OBJ-4 | Avaliar os modelos por métricas globais e específicas por classe. |
| OBJ-5 | Comparar tempos de treinamento, tempos de inferência e tamanho dos modelos. |
| OBJ-6 | Identificar falhas com maior grau de confusão. |
| OBJ-7 | Produzir tabelas, figuras, arquivos de resultados e documentação reproduzível. |
| OBJ-8 | Elaborar um artigo científico com os resultados do benchmark. |

O sucesso do subprojeto é condicionado ao cumprimento simultâneo de OBJ-1 a OBJ-8 (ver Seção 12, Critérios de aceite).

---

## 2. Escopo

### 2.1 Dentro do escopo

- Diagnóstico automático de falhas do TEP tratado como problema de **classificação multiclasse** (1 classe normal + 20 classes de falha = 21 classes).
- Avaliação comparativa de **exatamente 6 famílias de modelos clássicos** (Seção 8): Regressão Logística, Árvore de Decisão, Random Forest, Gradient Boosting, SVM, XGBoost.
- Protocolo experimental único e comum a todos os modelos (auditoria → EDA → divisão → pré-processamento → treinamento/seleção → avaliação final).
- Avaliação multidimensional: desempenho preditivo, equilíbrio entre classes, custo computacional, interpretabilidade.
- Produção de artefatos reproduzíveis (código numerado, dados de divisão, resultados brutos, metadados de ambiente) e de um artigo científico de base metodológica.

### 2.2 Fora do escopo

- Modelos de aprendizado profundo (redes neurais profundas), métodos orientados por física ou estratégias de detecção precoce — explicitamente reservados a estudos futuros que usarão este benchmark como referência clássica (Seção 19 do WP1A).
- Otimização exaustiva de hiperparâmetros além do necessário para uma seleção documentada e justificável (a busca deve usar apenas treino/validação — ver Seção 7.5).
- Coleta de novos dados experimentais: o estudo utiliza exclusivamente os dados do TEP já disponibilizados (52 variáveis de processo, 21 classes).
- Interpretação causal do processo físico a partir de importâncias de atributos (vedado — ver Seção 11, INV-08).
- Implementação de software: este documento e seus derivados de especificação não descrevem nem substituem código-fonte.

### 2.3 Limites do sistema em estudo

O sistema observado é o TEP simulado, descrito pelas suas 52 variáveis de processo (variáveis de estado e de operação) sob dois regimes: condição normal e condições de falha (20 tipos). Os modelos de classificação são especificados como mecanismos computacionais de diagnóstico que mapeiam vetores de variáveis de processo (por amostra/instante, dentro de uma execução) para uma das 21 classes.

---

## 3. Questões de pesquisa

| ID | Questão | Critério de resposta exigido |
|---|---|---|
| **QP1** | Quais algoritmos clássicos apresentam o melhor desempenho global na classificação das condições operacionais do TEP? | Ranking explícito dos 6 modelos por métricas globais (Seção 9). |
| **QP2** | O desempenho global é consistente quando se considera o equilíbrio entre as 21 classes? | Comparação entre ranking por acurácia simples e ranking por acurácia balanceada/F1 macro/MCC. |
| **QP3** | Quais falhas são sistematicamente mais difíceis de diagnosticar? | Identificação, a partir das matrizes de confusão e do F1 por classe, das classes com desempenho consistentemente baixo entre modelos. |
| **QP4** | Métodos mais complexos produzem ganhos suficientes para justificar maior custo computacional? | Cruzamento entre ganho de F1 macro/MCC e custo computacional (tempo de treino, tempo de inferência, tamanho do modelo). |
| **QP5** | Qual modelo apresenta o melhor compromisso entre desempenho, tempo de treinamento, tempo de inferência e tamanho do arquivo treinado? | Síntese multicritério explícita nas conclusões do relatório/artigo. |

Estas questões constituem o critério-mestre de aceite do estudo: os outputs definidos na Seção 10 devem, em conjunto, ser suficientes para respondê-las.

---

## 4. Hipóteses

| ID | Hipótese | Corroborada se | Refutada se |
|---|---|---|---|
| **H1** | Métodos de conjunto baseados em árvores têm desempenho superior aos classificadores lineares (relações não lineares entre variáveis do processo). | Random Forest e/ou Gradient Boosting e/ou XGBoost superam Regressão Logística em F1 macro e/ou MCC (teste). | Regressão Logística iguala/supera todos os métodos de conjunto baseados em árvores nessas métricas. |
| **H2** | XGBoost e Random Forest têm maior F1 macro e MCC do que Regressão Logística e Árvore de Decisão isolada. | F1 macro e MCC de XGBoost **e** de Random Forest superam os de Regressão Logística **e** de Árvore de Decisão (teste). | Qualquer uma dessas desigualdades é violada. |
| **H3** | Regressão Logística permanece competitiva em custo computacional e interpretabilidade, com menor capacidade de separar falhas com padrões sobrepostos. | Regressão Logística está entre os modelos de menor custo (tempo/tamanho) e apresenta F1 por classe reduzido nas classes de falha mais confundidas (QP3). | Regressão Logística não está entre os modelos de menor custo, ou iguala os métodos não lineares em todas as classes. |
| **H4** | O melhor modelo por acurácia não é necessariamente o melhor considerando F1 macro, MCC e custo de inferência. | O modelo de maior acurácia simples não coincide com o de melhor F1 macro, melhor MCC ou melhor relação desempenho/custo de inferência. | O mesmo modelo lidera simultaneamente todos esses critérios. |

As hipóteses DEVEM ser avaliadas exclusivamente sobre o conjunto de teste, após o congelamento de todas as configurações (ver Seção 7.5 e INV-05).

---

## 5. Dataset

| ID | Especificação | Valor normativo |
|---|---|---|
| DS-01 | Origem | Dados de simulação do Tennessee Eastman Process (TEP), em arquivos de treinamento e teste, contendo execuções sem falha e execuções com falhas induzidas. |
| DS-02 | Número de variáveis de processo | 52. |
| DS-03 | Número de classes | 21 (1 condição normal + 20 condições de falha). |
| DS-04 | Granularidade da amostra | Observação (linha) dentro de uma execução (*run*) do processo. |
| DS-05 | Integridade dos dados | Deve ser auditada quanto a valores ausentes, infinitos ou inconsistentes, e quanto a possíveis duplicações (Seção 7.1). |
| DS-06 | Rastreabilidade | Cada amostra deve ser vinculável a um arquivo de origem, a uma classe e a um identificador de execução (`run_id`). |

A auditoria completa do dataset (arquivos disponíveis, contagens de linhas/colunas, tipos e significado das variáveis, distribuição de classes, execuções por classe, ausentes/infinitos/duplicados, relação arquivo–classe–execução) é normativa e corresponde à Etapa 1 do pipeline (Seção 7.1) e à Entrega A1.

---

## 6. Unidade experimental

| ID | Definição |
|---|---|
| UE-01 | A **unidade experimental e de divisão dos dados é a execução do processo (*run*)**, não a amostra/observação individual nem o instante temporal. |
| UE-02 | Amostras pertencentes à mesma execução NÃO PODEM aparecer simultaneamente em mais de uma partição (treino, validação, teste). |
| UE-03 | Toda inferência estatística (comparação entre modelos, intervalos de confiança, testes de hipótese) DEVE declarar explicitamente a execução como unidade experimental; observações/instantes correlacionados dentro de uma mesma execução NÃO PODEM ser tratados como repetições estatisticamente independentes. |

Esta definição é vinculante para todas as demais seções desta SPEC (divisão de dados, pipeline, estatística, invariantes) e não pode ser reinterpretada por especificações derivadas.

---

## 7. Pipeline

O pipeline experimental é composto por 6 etapas sequenciais, executadas na ordem abaixo, com um único protocolo compartilhado por todos os 6 modelos (Seção 8).

### 7.1 Etapa 1 — Auditoria dos dados

Verifica e documenta: arquivos disponíveis; quantidade de linhas e colunas; nomes, tipos e significado das variáveis; distribuição das classes; quantidade de execuções por classe; valores ausentes, infinitos ou inconsistentes; possíveis duplicações; relação entre arquivos, classes e identificadores de execução.
→ Produz a Entrega A1.

### 7.2 Etapa 2 — Análise exploratória (EDA)

Inclui estatísticas descritivas, distribuição das classes, variabilidade das variáveis, correlações, projeções por PCA e inspeção de diferenças entre o regime normal e os regimes de falha.
→ Produz a Entrega A2.

### 7.3 Etapa 3 — Divisão experimental

Realizada por execução completa (UE-01/UE-02), segundo o protocolo-base:

- **Treinamento**: execuções destinadas ao ajuste dos modelos.
- **Validação**: execuções independentes, para seleção de hiperparâmetros.
- **Teste**: execuções nunca usadas durante o desenvolvimento.

A semente aleatória, a lista de execuções e o manifesto de divisão devem ser salvos para garantir repetibilidade.
→ Produz a Entrega A3.

### 7.4 Etapa 4 — Pré-processamento

Utiliza as decisões já estabelecidas na infraestrutura comum do projeto. Transformações dependentes dos dados (ex.: padronização) são ajustadas exclusivamente no conjunto de treinamento e apenas aplicadas (sem reajuste) aos conjuntos de validação e teste.

### 7.5 Etapa 5 — Treinamento e seleção

Cada algoritmo é treinado sob condições documentadas. A seleção de hiperparâmetros usa apenas o conjunto de validação ou validação cruzada interna aplicada ao conjunto de treinamento. O conjunto de teste só é consultado após o congelamento da configuração final de cada modelo.

### 7.6 Etapa 6 — Avaliação final

Calcula, por classe, precisão, revocação e F1; agrega as métricas globais (Seção 9), incluindo F1 macro, acurácia balanceada e MCC multiclasse, conforme as definições formais da Seção 9.

```
Etapa 1 (Auditoria) → Etapa 2 (EDA) → Etapa 3 (Divisão) → Etapa 4 (Pré-processamento)
      → Etapa 5 (Treinamento e seleção) → Etapa 6 (Avaliação final)
```

Nenhuma etapa posterior pode retroalimentar decisões de uma etapa anterior de forma a violar o isolamento do conjunto de teste (ver INV-05).

---

## 8. Modelos

O benchmark compreende exatamente os 6 modelos a seguir; nenhum pode ser omitido e nenhum modelo adicional descaracteriza o escopo definido na Seção 2.1 sem constituir um subprojeto distinto.

| ID | Modelo | Papel no benchmark |
|---|---|---|
| MOD-1 | Regressão Logística | Baseline linear, interpretável e de baixo custo computacional. |
| MOD-2 | Árvore de Decisão | Modelo não linear simples, com regras diretamente interpretáveis. |
| MOD-3 | Random Forest | Método de conjunto com redução de variância e boa robustez. |
| MOD-4 | Gradient Boosting | Referência de boosting sequencial com árvores rasas. |
| MOD-5 | SVM | Classificador de margem máxima; implementação inicial deve ser escalável. |
| MOD-6 | XGBoost | Baseline forte de boosting otimizado e regularizado. |

Todos os 6 modelos DEVEM ser treinados e avaliados sob o mesmo manifesto de divisão (Seção 7.3) e o mesmo pipeline de pré-processamento (Seção 7.4), de modo a preservar a comparabilidade (ver INV-03).

---

## 9. Métricas

### 9.1 Métricas por classe

Para cada classe *c*, de um total de *C* = 21 classes: precisão, revocação e F1.

### 9.2 Métricas globais e definições formais

$$F1_{macro} = \frac{1}{C}\sum_{c=1}^{C} F1_c$$

$$BA = \frac{1}{C}\sum_{c=1}^{C} \frac{TP_c}{TP_c + FN_c}$$

O coeficiente de correlação de Matthews multiclasse (MCC) é utilizado por fornecer uma avaliação mais informativa quando há erros distribuídos entre várias classes.

### 9.3 Conjunto obrigatório de métricas a reportar

| ID | Métrica |
|---|---|
| MET-01 | Acurácia |
| MET-02 | Acurácia balanceada (BA) |
| MET-03 | Precisão macro |
| MET-04 | Revocação macro |
| MET-05 | F1 macro |
| MET-06 | F1 ponderada |
| MET-07 | MCC multiclasse |
| MET-08 | Matriz de confusão |
| MET-09 | Métricas por classe (precisão, revocação, F1 — 21 classes) |
| MET-10 | Tempo de treinamento |
| MET-11 | Tempo de inferência |
| MET-12 | Tamanho do modelo salvo |
| MET-13 | Consumo de memória, quando disponível (condicional) |

Nenhuma decisão de ranking de modelos (QP1, QP5, H1–H4) pode se basear apenas em MET-01 (ver INV-06).

---

## 10. Estatística

| ID | Especificação |
|---|---|
| EST-01 | Sempre que houver resultados de múltiplas execuções independentes, sementes ou partições, devem ser reportados média, desvio-padrão e intervalo de confiança. |
| EST-02 | A comparação estatística entre modelos pode utilizar o teste de Friedman seguido de procedimento pós-hoc apropriado. |
| EST-03 | Comparações pareadas específicas podem utilizar o teste de Wilcoxon com correção para múltiplas comparações. |
| EST-04 | A unidade experimental (execução — UE-01) deve ser explicitada em toda inferência estatística. |
| EST-05 | Observações/linhas temporalmente correlacionadas não devem ser tratadas como repetições estatisticamente independentes. |

---

## 11. Outputs

### 11.1 Entregas formais (A1–A9)

| ID | Entrega | Formato |
|---|---|---|
| A1 | Relatório de auditoria da base | PDF/CSV |
| A2 | Análise exploratória | Notebook/figuras |
| A3 | Manifesto da divisão por execução | CSV/JSON |
| A4 | Implementação dos seis modelos | Python |
| A5 | Resultados completos | CSV/JSON |
| A6 | Figuras e tabelas do artigo | PNG/PDF/LaTeX |
| A7 | Relatório técnico final | PDF |
| A8 | Manuscrito científico | LaTeX/Word |
| A9 | Apresentação do projeto | PDF/PPTX |

### 11.2 Insumos mínimos para o artigo (compõem A5/A6)

1. Tabela de caracterização da base.
2. Tabela dos hiperparâmetros dos modelos.
3. Tabela comparativa das métricas globais.
4. Tabela de métricas por classe.
5. Matrizes de confusão.
6. Gráfico comparativo de F1 macro e MCC.
7. Gráfico de custo computacional.
8. Análise das falhas mais confundidas.
9. Arquivos CSV com resultados brutos.
10. Metadados do ambiente computacional.
11. Repositório com scripts numerados e instruções de execução.

### 11.3 Estrutura mínima do repositório

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

### 11.4 Estrutura obrigatória do manuscrito (A8)

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

Título provisório: *"Benchmark reproduzível de métodos clássicos de aprendizado de máquina para diagnóstico de falhas no Tennessee Eastman Process"* / *"A Reproducible Benchmark of Classical Machine Learning Methods for Fault Diagnosis in the Tennessee Eastman Process"*.

---

## 12. Invariantes

Condições que DEVEM permanecer verdadeiras em todos os momentos do subprojeto, independentemente da etapa, do modelo ou de quem executa o trabalho. A violação de qualquer invariante invalida os resultados associados.

| ID | Invariante |
|---|---|
| **INV-01** | A unidade de divisão dos dados é sempre a execução (`run`), nunca a amostra individual (UE-01). |
| **INV-02** | Nenhuma execução (`run`) pertence simultaneamente a mais de uma partição (treino/validação/teste) (UE-02). |
| **INV-03** | Todos os 6 modelos (Seção 8) usam o mesmo manifesto de divisão e o mesmo pipeline de pré-processamento — nenhuma comparação entre modelos é válida sob protocolos distintos. |
| **INV-04** | Transformações dependentes dos dados (ex.: padronização) são estimadas exclusivamente no conjunto de treinamento. |
| **INV-05** | O conjunto de teste não é consultado, direta ou indiretamente, antes do congelamento da configuração final de cada modelo (nenhum ajuste de hiperparâmetro usa o teste). |
| **INV-06** | Nenhuma conclusão sobre qual modelo é "melhor" pode se basear exclusivamente em acurácia simples (MET-01); deve considerar o conjunto de métricas da Seção 9.3. |
| **INV-07** | O custo computacional (MET-10, MET-11, MET-12) é sempre reportado e considerado nas conclusões que comparam modelos. |
| **INV-08** | Importâncias de atributos são interpretadas apenas como descritivas do comportamento do modelo, nunca como evidência causal sobre o processo físico do TEP. |
| **INV-09** | Nenhuma inferência estatística trata observações/instantes temporalmente correlacionados dentro de uma mesma execução como amostras independentes (EST-04, EST-05). |
| **INV-10** | Toda execução experimental é rastreável: semente aleatória, versões de software e manifesto de divisão são registrados e versionados. |

---

## 13. Critérios de aceite

O subprojeto WP1A é considerado **conforme** somente se todas as condições abaixo forem satisfeitas.

| ID | Critério de aceite | Verificação |
|---|---|---|
| CA-01 | Todas as entregas A1–A9 (Seção 11.1) existem, no formato especificado, com o conteúdo mínimo exigido. | Inspeção direta do repositório e dos documentos. |
| CA-02 | O dataset foi auditado conforme Seção 7.1, com resultado explícito (inclusive "nenhum encontrado") para cada item verificado. | Conteúdo de A1. |
| CA-03 | O manifesto de divisão (A3) comprova, por `run_id`, ausência de sobreposição entre treino, validação e teste. | Verificação automatizada de interseção vazia entre partições. |
| CA-04 | Os 6 modelos (MOD-1 a MOD-6) foram treinados e avaliados sob o mesmo protocolo (INV-03), com hiperparâmetros documentados. | Tabela de hiperparâmetros + A4. |
| CA-05 | Todas as métricas obrigatórias (MET-01 a MET-12) estão reportadas para cada um dos 6 modelos, globalmente e por classe. | A5 + tabelas comparativas (A6, insumos 3–4). |
| CA-06 | As definições formais de F1 macro, acurácia balanceada e MCC (Seção 9.2) foram aplicadas corretamente e são numericamente reprodutíveis a partir dos dados por classe reportados. | Recômputo a partir da matriz de confusão/valores por classe. |
| CA-07 | QP1–QP5 são respondidas de forma explícita e fundamentada em evidência quantitativa no relatório técnico (A7) e/ou manuscrito (A8). | Leitura de A7/A8. |
| CA-08 | H1–H4 são avaliadas explicitamente (corroboradas ou refutadas) com base no conjunto de teste, conforme os critérios da Seção 4. | Leitura de A7/A8. |
| CA-09 | Nenhuma das restrições metodológicas (INV-01 a INV-10) foi violada em nenhuma etapa do pipeline. | Auditoria metodológica cruzando A3–A5 com Seção 12. |
| CA-10 | O manuscrito (A8) segue a estrutura obrigatória (Seção 11.4), incluindo a seção "Ameaças à validade" (Seção 14 desta SPEC). | Sumário do manuscrito. |
| CA-11 | O repositório contém, no mínimo, a estrutura de diretórios da Seção 11.3, antes do início do treinamento dos modelos. | Inspeção do repositório. |
| CA-12 | A reprodutibilidade (Seção 15) é demonstrável: semente, versões de software e manifesto de divisão estão registrados e versionados. | Metadados de ambiente (insumo 10) + A3. |

---

## 14. Ameaças à validade

Categoria obrigatória do manuscrito (Seção 11.4, item 8); nesta SPEC, cada ameaça é associada aos mecanismos de mitigação já definidos no protocolo (Seções 6, 7 e 12), servindo de checklist normativo para a redação de A7/A8.

### 14.1 Validade interna (correção do experimento em si)

| Ameaça | Mecanismo de mitigação normativo |
|---|---|
| Vazamento de dados entre execuções, superestimando o desempenho. | Divisão por `run` (UE-01/UE-02), verificação de interseção vazia (CA-03, INV-01/INV-02). |
| Ajuste de hiperparâmetros contaminado pelo conjunto de teste. | Seleção restrita a treino/validação; teste consultado apenas após congelamento (Seção 7.5, INV-05). |
| Padronização/transformações estimadas incluindo dados de validação/teste. | Ajuste exclusivo no treino (Seção 7.4, INV-04). |
| Comparação entre modelos sob protocolos diferentes. | Protocolo único e compartilhado (INV-03). |

### 14.2 Validade estatística (correção das inferências)

| Ameaça | Mecanismo de mitigação normativo |
|---|---|
| Tratar observações temporalmente correlacionadas como independentes, inflando significância estatística. | Unidade experimental = execução (UE-03, EST-04, EST-05, INV-09). |
| Comparações múltiplas sem correção, gerando falsos positivos. | Correção para múltiplas comparações no pós-hoc de Wilcoxon (EST-03). |
| Conclusões baseadas em métrica única (acurácia) em cenário de classes desbalanceadas. | Conjunto obrigatório de métricas (Seção 9.3), INV-06. |

### 14.3 Validade de constructo (o que está de fato sendo medido)

| Ameaça | Mecanismo de mitigação normativo |
|---|---|
| Importâncias de atributos interpretadas como relações causais do processo físico do TEP. | Interpretação restrita à descrição do comportamento do modelo (INV-08). |
| Custo computacional omitido, fazendo "melhor modelo" significar apenas "modelo de maior acurácia". | Custo computacional (MET-10 a MET-12) sempre reportado e discutido (INV-07, QP4/QP5). |

### 14.4 Validade externa (generalização dos achados)

| Ameaça | Mecanismo de mitigação normativo |
|---|---|
| Resultados obtidos em dados simulados do TEP podem não generalizar diretamente para processos industriais reais. | Escopo explicitamente delimitado ao TEP como ambiente de referência simulado (Seção 2.3); generalização não é objeto deste benchmark. |
| Benchmark limitado a métodos clássicos pode não refletir o estado da arte em métodos profundos/híbridos. | Delimitação explícita de escopo (Seção 2.2) — o estudo é declaradamente uma referência clássica para comparações futuras, não uma afirmação de estado da arte absoluto. |

### 14.5 Reprodutibilidade como ameaça transversal

A ausência de registro de versões de software e sementes aleatórias compromete a reprodutibilidade e, indiretamente, a verificabilidade de todas as demais categorias de validade acima. Mitigação: Seção 15 (Reprodutibilidade) e INV-10.

---

## 15. Reprodutibilidade

| ID | Requisito de reprodutibilidade |
|---|---|
| REP-01 | A semente aleatória utilizada em cada etapa estocástica (divisão de dados, inicialização de modelos, validação cruzada) DEVE ser registrada. |
| REP-02 | A lista completa de execuções (`run_id`) por partição (treino/validação/teste) DEVE ser salva no manifesto de divisão (A3). |
| REP-03 | As versões do software e das bibliotecas utilizadas DEVEM ser registradas como metadados do ambiente computacional (insumo 10, Seção 11.2). |
| REP-04 | Os hiperparâmetros finais de cada um dos 6 modelos DEVEM ser documentados em tabela própria (insumo 2, Seção 11.2). |
| REP-05 | O repositório DEVE conter scripts numerados e instruções de execução (insumo 11, Seção 11.2), organizados conforme a estrutura mínima da Seção 11.3. |
| REP-06 | Os resultados brutos (previsões, métricas por execução/semente) DEVEM ser salvos em arquivos CSV/JSON (insumo 9, Entrega A5), permitindo o recômputo independente de qualquer métrica agregada. |

O cumprimento de REP-01 a REP-06 é condição necessária (mas não suficiente, isoladamente) para o critério de aceite CA-12.

---

## 16. Matriz de rastreabilidade desta SPEC

| Seção desta SPEC | Origem normativa (WP1A) | Origem normativa (requirements.md) |
|---|---|---|
| 1. Objetivo | Seção 6 (Objetivos) | Seção 1.5 |
| 2. Escopo | Seções 2, 3, 19, 21 (Contextualização, Problema, Resultados esperados, Considerações finais) | Seções 1.1–1.2, 13 |
| 3. Questões de pesquisa | Seção 4 (QP1–QP5) | Seção 1.3 |
| 4. Hipóteses | Seção 5 (H1–H4) | Seção 1.4 |
| 5. Dataset | Seção 7 (Base de dados) | Seção 2 |
| 6. Unidade experimental | Seções 7, 9.3, 11 | Seções 2 (RD-03/04), 6 (RAE-04/05) |
| 7. Pipeline | Seção 9 (Etapas 1–6) | Seção 4 |
| 8. Modelos | Seção 8 (Tabela 1) | Seção 3 |
| 9. Métricas | Seções 9.6, 10 | Seções 4.6, 5 |
| 10. Estatística | Seção 11 | Seção 6 |
| 11. Outputs | Seções 12, 13, 15, 20 | Seções 8, 9 |
| 12. Invariantes | Seção 18 (Riscos) | Seção 7 (RQ-01 a RQ-08) |
| 13. Critérios de aceite | Seções 15, 17, 19, 21 | Seções 8, 11, 13 |
| 14. Ameaças à validade | Seções 13 (item 8), 18 | Seção 7 |
| 15. Reprodutibilidade | Seções 9.3, 18 | Seção 2 (RD-03/04), 4.3 (RP-04) |

---

## 17. Observações finais

Esta SPEC-000 é o documento mestre do subprojeto WP1A. Qualquer especificação derivada (por exemplo, especificações de dados, de pipeline, de modelos individuais ou de avaliação) DEVE ser consistente com os objetivos (Seção 1), o escopo (Seção 2), a unidade experimental (Seção 6), os invariantes (Seção 12) e os critérios de aceite (Seção 13) aqui definidos. Este documento não implementa, não descreve arquitetura de código e não deve ser usado como especificação de software — ele define o que deve ser verdadeiro, cientificamente e metodologicamente, para que o benchmark WP1A seja considerado válido e reproduzível.
