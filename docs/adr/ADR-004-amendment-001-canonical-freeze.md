# ADR-004-amendment-001: Congelamento do dataset canônico `tep-canonical-v1`

| Campo | Valor |
|---|---|
| Status | Aceita |
| Data | 2026-09-14 |
| Emenda a | [ADR-004-canonical-dataset.md](./ADR-004-canonical-dataset.md) |
| Documentos relacionados | `docs/specs/SPEC-002-canonical-dataset.md`; Entrega A1 (`reports/audit/`); `results/metadata/audit_counts.json` |

## Contexto

A Entrega A1 (SPEC-001) auditou os 44 arquivos Braatz em `data/raw/` e registrou três divergências relevantes para a definição do dataset canônico:

1. **Forma de `d00.dat`:** 52×500 (`features_x_samples`), divergente do layout documentado 480×52.
2. **Classe 21:** arquivos `d21.dat` / `d21_te.dat` excedem DS-03 (21 classes = rótulos 0..20).
3. **Duplicatas entre arquivos `*_te.dat`:** 160 grupos de linhas idênticas no trecho pré-falha.

## Decisões de tratamento global (pré-divisão)

| ID | Decisão | Justificativa |
|---|---|---|
| `exclude_fault_21` | **Excluir** `d21.dat` e `d21_te.dat` do canônico | Alinha o dataset a DS-03 / ADR-004 (exatamente 21 classes). |
| `orient_to_samples_x_features` | **Orientar em memória** (transpor `d00.dat` → 500×52); **não** reescrever `data/raw/`; **não** truncar para 480 | Corrige a orientação sem mutar os brutos; as 500 amostras são o conteúdo real do arquivo auditado. |
| `retain_cross_file_duplicate_rows` | **Manter** linhas numericamente iguais entre runs `*_te` | São trechos iniciais em regime normal de execuções distintas; removê-las alteraria comprimento e estrutura temporal dos `run_id`. |

## Representação canônica

- Identificador: **`tep-canonical-v1`**
- Tabela: `data/processed/tep-canonical-v1.csv.gz`
- Registro: `data/processed/canonical_dataset_registry.json`
- Schema: 52 features (`xmeas_1..41`, `xmv_1..11`) + `run_id` + `class_label` + proveniência (`source_file`, `source_split`, `sample_index`)
- `data/raw/` permanece **imutável**; checksums SHA-256 de A1 são revalidados na construção

## Política de não-canônico

Qualquer subconjunto ou versão alternativa (incluindo os arquivos excluídos e fixtures de teste) é **não canônica** e não pode alimentar A5–A9. Alterações futuras exigem nova auditoria (SPEC-001) e nova emenda a ADR-004.

## Critério de verificação

`make canonical-dataset` produz o registro com `status=canonical`, 21 classes (0..20), 52 features, e a suíte de testes de schema/canônico passa sem mutar checksums em `data/raw/`.
