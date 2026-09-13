"""WP1A validation/guard utilities.

This package does NOT implement the ML pipeline (audit, EDA, split,
preprocessing, training, evaluation — see skills/*/SKILL.md). It implements
only the methodological guardrails that the future pipeline implementation
must satisfy, as fixed by:

- docs/specs/SPEC-000-master.md
- docs/adr/ADR-001-run-as-experimental-grouping-unit.md
- docs/adr/ADR-002-test-set-isolation.md
- docs/adr/ADR-003-reproducibility-requirements.md
- AGENTS.md

These guardrails exist so that the test suite in tests/ can reject, by
construction, the six methodological failure modes requested before any
pipeline code is written: run leakage, use of the test set during fit,
class inconsistency, invalid schema, non-reproducible splits, and
incomplete experiment metadata.
"""

__version__ = "0.1.0"
