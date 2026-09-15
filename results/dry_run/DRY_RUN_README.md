# DRY-RUN

Artifacts in this directory are **pipeline smoke tests only**.

They are produced from a controlled fraction of `run_id`s, use lightweight
hyperparameters, and are **not scientifically valid** (`scientific_validity: false`).

Do **not** cite these numbers in A4/A7/A8, tables, figures, or model comparisons.

A random run-fraction may yield ~0 test accuracy when train/test classes are
disjoint — that still confirms the pipeline, not model quality.

Regenerate with:

```bash
make dry-run
```
