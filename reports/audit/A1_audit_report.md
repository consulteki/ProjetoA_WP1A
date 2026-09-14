# Entrega A1 — Relatório de Auditoria da Base (TEP)

- Gerado em: `2026-09-14T00:40:20+00:00`
- Diretório auditado: `/home/alanancy/metodosEsimulacao/data/raw`
- Fonte: Tennessee Eastman Process (TEP) — Russell/Chiang/Braatz reference files
- URL de origem: https://github.com/jkitchin/tennessee-eastman-profbraatz/tree/master/data

## Escopo

Auditoria exclusiva dos arquivos brutos (`data/raw/`), conforme `docs/specs/SPEC-001-data-audit.md` e `.agents/skills/data-audit/SKILL.md`. Nenhuma transformação de modelagem foi aplicada; a definição do dataset canônico permanece sob SPEC-002.

## Checagem normativa (DS-02 / DS-03)

- **DS-02** (52 variáveis): `ok` (esperado=52, observado=52)
- **DS-03** (21 classes 0..20): `divergence` (observado=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])

> Nota: O pacote Braatz inclui d21/d21_te (classe 21), excedendo as 21 classes normativas (0..20). A decisão de inclusão/exclusão cabe à SPEC-002.

## Itens obrigatórios (RP-01 / CA-02)

### Item 1 — Arquivos disponíveis

- **Status:** `ok`
- **Resultado:** 44 arquivo(s) .dat encontrados em /home/alanancy/metodosEsimulacao/data/raw; nome, formato, tamanho e sha256 registrados.

### Item 2 — Quantidade de linhas e colunas por arquivo

- **Status:** `anomaly`
- **Resultado:** 1 arquivo(s) com forma divergente do esperado (treino 480×52, teste 960×52): d00.dat=52x500 (features_x_samples)

### Item 3 — Nomes, tipos e significado das variáveis

- **Status:** `ok`
- **Resultado:** Catálogo de 52 variáveis canônicas (xmeas_1..41 + xmv_1..11) documentado; dtype observado nos .dat = float64.

### Item 4 — Distribuição das 21 classes

- **Status:** `divergence`
- **Resultado:** Divergência frente a DS-03 (21 classes = 0..20). classes além do normativo DS-03 (0..20): [21] (arquivos d21* presentes no pacote Braatz). Classes observadas: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21].

### Item 5 — Quantidade de execuções (run) por classe

- **Status:** `ok`
- **Resultado:** 44 run_id distintos (1 arquivo = 1 execução Braatz); contagem por classe registrada. Nota: os rótulos braatz_train/braatz_test são proveniência do pacote original, NÃO a divisão experimental WP1A (SPEC-004).

### Item 6 — Valores ausentes, infinitos ou inconsistentes

- **Status:** `ok`
- **Resultado:** nenhum problema encontrado — zero NaN, zero Inf; todas as matrizes orientadas têm 52 colunas de processo.

### Item 7 — Possíveis duplicações (intra e entre arquivos)

- **Status:** `anomaly`
- **Resultado:** grupos de linhas idênticas presentes em ≥2 arquivos: 160; nota: no pacote Braatz, arquivos *_te.dat tipicamente compartilham o trecho inicial em operação normal (pré-introdução da falha); isso é um achado de auditoria a decidir em SPEC-002, não uma correção silenciosa nesta etapa

### Item 8 — Relação entre arquivos, classes e identificadores de execução (run_id)

- **Status:** `ok`
- **Resultado:** nenhum problema encontrado — cada run_id mapeia a exatamente uma classe e a exatamente um arquivo de origem; verificação automatizada executada.

## Artefatos tabulares

- `A1_01_files.csv` — inventário de arquivos
- `A1_02_shapes.csv` — linhas/colunas por arquivo
- `A1_03_variables.csv` — catálogo de variáveis
- `A1_04_class_distribution.csv` — amostras por classe
- `A1_05_runs_per_class.csv` — execuções por classe
- `A1_06_integrity.csv` — NaN/Inf/inconsistências por arquivo
- `A1_07_duplicates_summary.csv` — resumo de duplicações
- `A1_08_file_class_run.csv` — mapeamento arquivo–classe–run_id
- `A1_findings.csv` — status dos 8 itens
- `../tables/A1_dataset_characterization.csv` — tabela de caracterização (insumo 1)

## Metadados para SPEC-002

Contagens e checksums em `results/metadata/audit_counts.json`.
