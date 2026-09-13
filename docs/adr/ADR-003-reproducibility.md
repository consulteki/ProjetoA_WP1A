# ADR-003: Requisitos de reprodutibilidade

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-13 |
| Decisores | Grupo A — WP1A |
| Documentos relacionados | `docs/specs/SPEC-000-master.md` §15 (REP-01 a REP-06), §12 (INV-10), §13 (CA-12); `docs/project/requirements.md` RP-04, RQ-08; `AGENTS.md` §7 (EXP-R01 a EXP-R07) |

## Contexto

O produto principal do WP1A é declarado como um **protocolo reprodutível**, não apenas um conjunto de números de desempenho. O subprojeto será usado como referência para comparações futuras (modelos profundos, métodos orientados por física, detecção precoce), o que exige que qualquer resultado reportado possa ser auditado e, idealmente, recomputado de forma independente. Historicamente, comparações de modelos de aprendizado de máquina falham em reprodutibilidade por: sementes aleatórias não registradas, versões de bibliotecas não documentadas, manifestos de divisão não versionados, e resultados agregados reportados sem os dados brutos que os sustentam.

## Decisão

Toda execução experimental do benchmark DEVE registrar e versionar, como condição de validade do resultado:

1. **Semente aleatória** de cada etapa estocástica (divisão de dados, inicialização de modelo, validação cruzada).
2. **Lista completa de `run_id`** por partição (treino/validação/teste), no manifesto de divisão (Entrega A3).
3. **Versões de software e bibliotecas** utilizadas (linguagem, frameworks de ML, dependências), como metadados do ambiente computacional.
4. **Hiperparâmetros finais** de cada um dos 6 modelos, em tabela própria e versionada.
5. **Resultados brutos** (predições por amostra, métricas por execução/semente), em arquivos CSV/JSON versionados em `results/`, permitindo recômputo independente de qualquer métrica agregada reportada em tabelas ou no manuscrito.
6. **Identificador único de experimento**, associando de forma inequívoca uma configuração (dataset canônico + split + pré-processamento + hiperparâmetros + semente) a um conjunto de resultados.

Nenhum número (tabela, figura, métrica) pode ser citado em documentação (A6, A7, A8) sem que exista um artefato de resultado versionado do qual ele foi derivado.

## Justificativa e alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Reprodutibilidade garantida apenas por descrição narrativa no relatório ("usamos Random Forest com parâmetros padrão"). | Não é verificável nem recomputável; descrições narrativas divergem facilmente da implementação real ao longo do tempo. |
| Não fixar sementes aleatórias, aceitando variação natural entre execuções. | Impede comparação direta entre reexecuções, dificulta depuração de divergências e quebra o critério de aceite CA-12. |
| Reportar apenas métricas agregadas finais, descartando predições e resultados brutos por execução. | Impede auditoria e recômputo independente (por exemplo, para verificar a fórmula de F1 macro/MCC), e impede a aplicação de testes estatísticos que exigem os valores por unidade experimental (ver ADR-001). |
| Deixar hiperparâmetros "no código", sem tabela documentada separada. | Dificulta auditoria comparativa entre os 6 modelos e a rastreabilidade exigida por DOC-R03; diverge facilmente do que foi realmente usado no experimento reportado. |

## Consequências

### Positivas
- Qualquer resultado reportado é auditável e, em princípio, recomputável por terceiros — condição necessária para o artigo servir como referência clássica (Seção 19 do WP1A / §13 da SPEC-000).
- Facilita a depuração: divergências entre execuções podem ser rastreadas a mudanças de versão, semente ou configuração.

### Negativas / trade-offs
- Overhead de engenharia para capturar e versionar metadados em toda execução (não apenas nas execuções "finais").
- Aumenta o volume de artefatos a gerenciar (resultados brutos, metadados, tabelas de hiperparâmetros), exigindo política de armazenamento (ver ADR-005 e GIT-R03).

### Riscos e mitigação
- **Risco:** membros do grupo (ou agentes) executam experimentos exploratórios sem registrar semente/versões, e esses resultados acabam citados por engano em tabelas finais. **Mitigação:** convenção de identificador único de experimento (ADR-005) e regra de que nenhum número entra em documentação sem artefato de resultado rastreável (DOC-R03).

## Regras derivadas

- `AGENTS.md` EXP-R01 a EXP-R07, DOC-R03.
- `docs/specs/SPEC-000-master.md` REP-01 a REP-06, INV-10, CA-12.

## Critério de verificação

Para qualquer tabela ou figura do relatório técnico (A7) ou manuscrito (A8), é possível localizar: o identificador de experimento, o manifesto de divisão usado, a semente, as versões de ambiente e o arquivo de resultado bruto correspondente em `results/`.
