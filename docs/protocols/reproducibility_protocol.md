# Protocolo de Reprodutibilidade — WP1A

Síntese operacional (checklist) de `docs/adr/ADR-003-reproducibility.md` e `docs/adr/ADR-005-experiment-configuration.md`. Em caso de conflito, as ADRs e `docs/specs/SPEC-000-master.md` prevalecem sobre este checklist.

## Para cada experimento registrado

Os metadados abaixo são obrigatórios (verificados por `src/wp1a/tracking/metadata_guard.py::validate_experiment_metadata`):

- [ ] `experiment_id` — identificador único.
- [ ] `seed` — semente aleatória usada em toda etapa estocástica.
- [ ] `dataset_version` — identificador do dataset canônico (SPEC-002).
- [ ] `split_manifest_path` — referência ao manifesto de divisão (A3, SPEC-004).
- [ ] `software_versions` — versões de linguagem e bibliotecas.
- [ ] `hyperparameters` — hiperparâmetros finais, congelados.
- [ ] `timestamp` — momento do congelamento/execução.

## Antes de publicar qualquer número (tabela, figura, texto)

- [ ] O número é rastreável a um arquivo de resultado versionado em `results/`.
- [ ] O arquivo de resultado é rastreável a um `experiment_id` com metadados completos.
- [ ] O `experiment_id` referencia um `dataset_version` (SPEC-002) e um `split_manifest_path` (SPEC-004) válidos.

## Ao reexecutar um experimento

- [ ] Um novo `experiment_id` é aberto — nenhum resultado anterior já citado em documentação é sobrescrito silenciosamente.
- [ ] A configuração (`configs/experiment.yaml`, `configs/models.yaml`, `configs/seeds.yaml`) usada é versionada junto ao novo `experiment_id`.

## Verificação de reprodutibilidade

- [ ] `pytest tests/methodology/test_split_reproducibility.py` passa contra a função de split real.
- [ ] `pytest tests/methodology/test_metadata_completeness.py` passa contra os metadados de todo experimento registrado.
- [ ] Recômputo independente de F1 macro / acurácia balanceada a partir dos dados por classe confere com o valor reportado.

## Estrutura mínima de metadados por experimento

```
results/metadata/<experiment_id>.json
{
  "experiment_id": "...",
  "seed": 123,
  "dataset_version": "...",
  "split_manifest_path": "data/processed/split_manifest_<version>.json",
  "software_versions": {"python": "...", "scikit-learn": "...", "xgboost": "..."},
  "hyperparameters": {...},
  "timestamp": "..."
}
```
