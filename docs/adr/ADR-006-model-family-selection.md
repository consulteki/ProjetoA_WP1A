# ADR-006: Seleção da família de modelos do benchmark

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-13 |
| Decisores | Grupo A — WP1A |
| Documentos relacionados | `docs/specs/SPEC-000-master.md` §8 (MOD-1 a MOD-6), §2.2 (fora de escopo), §12 (INV-03); `docs/project/requirements.md` Seção 3 (RMO-01 a RMO-06), OBJ-3; `AGENTS.md` MET-R03 |

## Contexto

O WP1A é explicitamente um estudo de referência com **métodos clássicos** de aprendizado de máquina, destinado a servir de baseline para comparações futuras com modelos profundos, métodos orientados por física e estratégias de detecção precoce (fora do escopo deste subprojeto). É necessário decidir qual conjunto de algoritmos compõe o benchmark de forma que ele represente, de maneira equilibrada, diferentes paradigmas de aprendizado supervisionado clássico relevantes para diagnóstico de falhas multiclasse.

## Decisão

O benchmark compreende **exatamente 6 famílias de modelos**, fixas e obrigatórias, cada uma representando um paradigma distinto:

| Modelo | Paradigma representado |
|---|---|
| Regressão Logística | Baseline linear, interpretável, baixo custo computacional. |
| Árvore de Decisão | Modelo não linear simples, com regras diretamente interpretáveis. |
| Random Forest | Conjunto por *bagging*, redução de variância, boa robustez. |
| Gradient Boosting | Conjunto por *boosting* sequencial com árvores rasas. |
| SVM | Classificador de margem máxima (não baseado em árvores). |
| XGBoost | Boosting otimizado e regularizado — baseline forte. |

Nenhum modelo adicional é incorporado ao escopo deste benchmark sem uma emenda formal a esta ADR (e a consequente reexecução do protocolo completo, por força de INV-03); nenhum dos 6 pode ser omitido sem comprometer o cumprimento de OBJ-3 e das entregas A4/A5.

## Justificativa e alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Incluir também modelos de aprendizado profundo (ex.: MLP, redes recorrentes) no mesmo benchmark. | Fora do escopo definido pelo WP1A (SPEC-000 §2.2); esses métodos são reservados para subprojetos futuros que usarão este benchmark clássico como referência. |
| Reduzir o conjunto a apenas modelos de árvore (Random Forest, Gradient Boosting, XGBoost), eliminando os baselines lineares/de margem. | Compromete diretamente a avaliação de H1 e H3, que dependem explicitamente da comparação entre métodos de conjunto baseados em árvores e a Regressão Logística. |
| Selecionar apenas um representante "vencedor" por paradigma após uma rodada exploratória prévia. | Contradiz o objetivo do benchmark (comparação sistemática dos 6 métodos) e inviabiliza responder QP1/QP2/QP5 com a granularidade exigida. |
| Permitir que cada subgrupo escolha livremente variações/implementações alternativas de cada modelo. | Compromete a comparabilidade entre execuções e a reprodutibilidade (ADR-003); a variação de implementação deve ser documentada como hiperparâmetro/configuração (ADR-005), não como substituição do modelo. |

## Consequências

### Positivas
- Cobertura balanceada de paradigmas (linear, árvore única, dois tipos de conjunto de árvores, margem máxima), suficiente para testar H1–H4 de forma direta.
- Escopo fixo evita "scope creep" experimental que comprometeria prazos e comparabilidade.

### Negativas / trade-offs
- Exclui, por decisão de escopo, comparações com métodos mais recentes (deep learning, métodos híbridos), que ficam para trabalhos futuros.
- SVM pode ter custo computacional elevado em bases grandes; a decisão de usar uma implementação escalável é tratada como detalhe de configuração (ADR-005), não como substituição do paradigma.

### Riscos e mitigação
- **Risco:** pressão de prazo leva a "simplificar" o benchmark reduzindo o número de modelos. **Mitigação:** este ADR, referenciado por MET-R03 e pelas Proibições do `AGENTS.md`, torna explícito que os 6 modelos são requisito de aceite (CA-04), não uma meta aspiracional.

## Regras derivadas

- `AGENTS.md` MET-R03, Proibição 8.
- `docs/specs/SPEC-000-master.md` MOD-1 a MOD-6, CA-04.

## Critério de verificação

A Entrega A4 (implementação) e a Entrega A5 (resultados) contêm artefatos para os 6 modelos listados, todos avaliados sob o mesmo manifesto de divisão (ADR-001) e a mesma configuração de pipeline (ADR-002/ADR-005).
