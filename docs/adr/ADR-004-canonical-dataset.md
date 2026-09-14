# ADR-004: Dataset canônico

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-13 |
| Decisores | Grupo A — WP1A |
| Documentos relacionados | `docs/specs/SPEC-000-master.md` §5 (DS-01 a DS-06), §7.1 (Etapa 1 — Auditoria); `docs/project/requirements.md` Seção 2, Entrega A1; `AGENTS.md` GIT-R03, DOC-R03 |

## Contexto

O TEP possui diferentes versões e derivações amplamente utilizadas na literatura (diferentes simuladores, diferentes números de execuções, diferentes convenções de rotulação de falhas). O WP1A especifica uma versão de referência com **52 variáveis de processo e 21 classes** (condição normal + 20 condições de falha), disponibilizada em arquivos de treinamento e teste contendo execuções sem falha e execuções com falhas induzidas. Sem uma definição única e explícita de qual conjunto de arquivos constitui "o dataset do benchmark", há risco de que diferentes membros do grupo (ou diferentes agentes automatizados) usem versões, subconjuntos ou cópias ligeiramente distintas do TEP, invalidando a comparabilidade entre os 6 modelos e comprometendo a reprodutibilidade (ADR-003).

## Decisão

1. É definida uma **fonte canônica única** de dados para todo o benchmark: os arquivos de origem do TEP identificados, descritos e auditados no relatório de auditoria da base (Entrega A1), com exatamente 52 variáveis de processo e 21 classes.
2. O relatório de auditoria (A1) é o **documento de registro oficial** da identidade do dataset canônico: arquivos disponíveis, contagem de linhas/colunas, nomes/tipos/significado das variáveis, distribuição de classes, execuções por classe, tratamento de valores ausentes/infinitos/inconsistentes e duplicações, e relação entre arquivos, classes e `run_id`.
3. Qualquer subconjunto, amostra reduzida ou versão alternativa do TEP usada para fins exploratórios (prototipagem rápida, testes de código) é explicitamente marcada como **não canônica** e **não pode alimentar** resultados reportados em A5–A9.
4. Alterações ao dataset canônico (ex.: correção de um erro de rotulação descoberto na auditoria, adição de execuções) exigem: (a) nova auditoria documentada, (b) atualização explícita desta ADR ou de uma ADR de emenda, e (c) reexecução completa do pipeline para os 6 modelos, preservando a comparabilidade (INV-03).

## Justificativa e alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Cada membro do grupo (ou agente) obtém sua própria cópia dos dados do TEP de fontes públicas, sem registro central. | Risco alto de divergência silenciosa entre cópias (diferentes versões/convenções do TEP), invalidando comparações entre modelos treinados por pessoas/agentes diferentes. |
| Usar subconjuntos de dados diferentes por modelo para acelerar experimentação (ex.: menos execuções para SVM por custo computacional). | Viola diretamente INV-03 (protocolo único e comparável entre os 6 modelos) e compromete a validade de QP1/QP2/H1–H4. |
| Tratar a definição do dataset como implícita no código de carregamento, sem documento de auditoria formal. | Não atende à Entrega A1 exigida pelo WP1A e dificulta a auditoria de conformidade (integridade, duplicidade, valores ausentes) exigida pela Etapa 1 do pipeline. |

## Consequências

### Positivas
- Elimina ambiguidade sobre "qual dataset" fundamenta os resultados reportados.
- Torna a Etapa 1 (auditoria) o ponto único de verdade sobre a integridade e a estrutura dos dados, evitando descobertas tardias de inconsistências.
- Facilita a rastreabilidade exigida por DOC-R03: toda métrica reportada remonta, em última instância, ao mesmo dataset canônico.

### Negativas / trade-offs
- Reduz a flexibilidade de experimentação individual com variações de dados sem processo formal de emenda.
- Exige disciplina de versionamento de dados (ou ao menos de metadados/checksums), mesmo quando os arquivos brutos não são versionados diretamente no Git (ver GIT-R03).

### Riscos e mitigação
- **Risco:** divergência silenciosa entre a cópia local de dados de um contribuinte e o dataset canônico documentado em A1. **Mitigação:** a auditoria (A1) deve registrar informação suficiente (contagens, hashes/checksums quando viável, contagem de execuções por classe) para permitir verificação de integridade antes de qualquer treinamento.

## Regras derivadas

- `AGENTS.md` GIT-R03, DOC-R03, DOC-R04.
- `docs/specs/SPEC-000-master.md` DS-01 a DS-06, CA-02.

## Critério de verificação

Qualquer artefato de resultado (A5 em diante) é rastreável ao relatório de auditoria (A1) do dataset canônico; uma verificação de integridade (contagem de linhas/colunas, número de classes, número de execuções) confirma correspondência entre os dados efetivamente usados no treinamento e o que está documentado em A1.

## Emendas

- [ADR-004-amendment-001](./ADR-004-amendment-001-canonical-freeze.md) — congelamento de `tep-canonical-v1` (exclusão da classe 21, orientação em memória de `d00.dat`, retenção de duplicatas pré-falha).
