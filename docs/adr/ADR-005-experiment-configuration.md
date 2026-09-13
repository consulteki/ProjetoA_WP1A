# ADR-005: Configuração de experimentos

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-13 |
| Decisores | Grupo A — WP1A |
| Documentos relacionados | `docs/specs/SPEC-000-master.md` §7.5, §11.3 (`configs/`), §15 (REP-04); `docs/project/requirements.md` RP-07; `AGENTS.md` §7 (EXP-R01, EXP-R02, EXP-R04) |

## Contexto

O benchmark envolve 6 modelos, cada um com seus próprios hiperparâmetros, além de decisões compartilhadas (dataset canônico — ADR-004, manifesto de divisão — ADR-001, semente aleatória — ADR-003). Sem uma forma padronizada e versionada de declarar "o que foi executado", cada execução corre o risco de depender de valores implícitos, hardcoded em scripts, ou passados informalmente por linha de comando e não registrados — tornando impossível reconstruir, depois, exatamente qual configuração gerou qual resultado (violando ADR-003).

## Decisão

1. Cada execução experimental (treinamento + avaliação de um modelo, ou de um conjunto de modelos sob o mesmo protocolo) DEVE ser definida por uma **configuração explícita e versionada**, armazenada no diretório `configs/` (estrutura mínima definida em SPEC-000 §11.3).
2. A configuração de um experimento DEVE referenciar, de forma explícita e não ambígua:
   - o **dataset canônico** utilizado (ADR-004);
   - o **manifesto de divisão** (`run_id` por partição — ADR-001, Entrega A3);
   - a **semente aleatória**;
   - os **hiperparâmetros** do(s) modelo(s), incluindo valores padrão explicitamente declarados (nunca implícitos);
   - a etapa de pré-processamento aplicada (referenciando a infraestrutura comum do pipeline, Seção 7.4 da SPEC-000).
3. Cada configuração possui um **identificador único de experimento**, associado de forma rastreável aos resultados que produz (`results/tables/`, `results/predictions/`, `results/metadata/`).
4. Alterar um hiperparâmetro ou qualquer componente da configuração gera uma **nova configuração versionada** (novo arquivo ou nova versão identificável), nunca a edição silenciosa de uma configuração já usada para gerar resultados publicados/citados.
5. Reexecuções para correção de erro seguem a mesma regra: gera-se um novo identificador de experimento (EXP-R04), preservando o histórico da execução anterior para auditoria.

## Justificativa e alternativas consideradas

| Alternativa | Motivo de rejeição |
|---|---|
| Hiperparâmetros definidos diretamente no código de treinamento (valores hardcoded). | Dificulta diff/auditoria entre experimentos, aumenta risco de divergência silenciosa entre o que está documentado (tabela de hiperparâmetros) e o que foi de fato executado. |
| Passar hiperparâmetros apenas via argumentos de linha de comando, sem persistir a configuração usada. | Não reprodutível a posteriori: uma vez encerrado o processo, a configuração exata pode se perder, violando REP-04. |
| Uma única configuração global "mutável", atualizada a cada nova tentativa. | Impede rastrear qual configuração gerou quais resultados já reportados; um ajuste posterior pode invalidar silenciosamente números já citados em documentação (viola DOC-R03). |
| Configuração implícita na ordem de chamadas de um notebook interativo, sem arquivo de configuração dedicado. | Não versionável de forma confiável, alto risco de execução fora de ordem ou com estado residual de célula anterior — incompatível com REP-01 a REP-06. |

## Consequências

### Positivas
- Cada resultado reportado é rastreável a exatamente uma configuração versionada, viabilizando auditoria e recômputo (reforça ADR-003).
- Facilita comparação entre modelos sob o mesmo protocolo (INV-03), pois a configuração explicita e compartilha os componentes comuns (dataset, split, pré-processamento).
- Reduz risco de "corrupção" retroativa de resultados já publicados por edição não rastreada de configuração.

### Negativas / trade-offs
- Exige disciplina adicional de nomeação e versionamento de arquivos de configuração.
- Aumenta o número de artefatos armazenados (uma configuração por experimento/execução relevante).

### Riscos e mitigação
- **Risco:** proliferação descontrolada de arquivos de configuração sem convenção clara, dificultando localizar a configuração "oficial" de cada entrega. **Mitigação:** convenção de nomenclatura e tabela de rastreamento (experimento → configuração → resultado) mantida na documentação de resultados (Entrega A5/A7), como exigido por DOC-R03.

## Regras derivadas

- `AGENTS.md` EXP-R01, EXP-R02, EXP-R04, REP-04.
- `docs/specs/SPEC-000-master.md` estrutura `configs/` (§11.3).

## Critério de verificação

Para qualquer entrada da tabela de hiperparâmetros dos modelos (insumo obrigatório do artigo) ou de qualquer linha de resultado em `results/`, existe um arquivo de configuração versionado em `configs/` que a produziu, e esse arquivo referencia explicitamente o dataset canônico (ADR-004) e o manifesto de divisão (ADR-001) utilizados.
