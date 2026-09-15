# Prompt de Agente: Figures (A6)

**Papel:** gerar tabelas e figuras da Entrega A6 a partir de artefatos versionados.

## Restrição absoluta

1. **Nunca** ler `data/raw` (nem `data/interim`) para produzir A6.
2. Fontes permitidas: **somente** arquivos sob `results/` (e cópias derivadas para `article/`).
3. Cada figura/tabela DEVE registrar rastreabilidade → arquivo(s) de origem (DOC-R03).
4. Não declarar “melhor modelo” por métrica única (INV-06); incluir custo quando comparar (INV-07).

## Contexto

1. `.agents/skills/scientific-figures/SKILL.md`
2. `docs/specs/SPEC-009-publication.md` §3.1
3. A5 em `results/tables/A5_*` e `results/metrics/A5_*`

## Comando

```bash
make figures
# ou: PYTHONPATH=src python -m wp1a.visualization.cli --experiment-id exp-a4-v2
```

## Não fazer

- Não recalcular métricas a partir de dados brutos.
- Não editar números manualmente nas figuras.
- Não misturar DRY-RUN com A6 científico.
