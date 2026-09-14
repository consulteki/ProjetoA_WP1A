"""Exception hierarchy for WP1A methodological validation guards.

Each exception corresponds to one of the failure modes the pipeline must
reject, per the request "crie testes que rejeitem: run leakage, uso de
test durante fit, inconsistência de classes, schema inválido, split não
reproduzível, metadata incompleta". Using a dedicated exception type per
failure mode (instead of a generic AssertionError/ValueError) lets tests,
and later the real pipeline code, distinguish *which* invariant was
violated.
"""

from __future__ import annotations


class WP1AValidationError(Exception):
    """Base class for all WP1A methodological validation errors."""


class SchemaError(WP1AValidationError):
    """Dataset does not conform to the canonical TEP schema.

    See docs/specs/SPEC-000-master.md §5 (DS-01..DS-06).
    """


class RunLeakageError(WP1AValidationError):
    """A run (execution) appears in more than one data partition.

    See docs/adr/ADR-001-run-as-experimental-grouping-unit.md,
    docs/specs/SPEC-000-master.md INV-01/INV-02.
    """


class TestSetLeakageError(WP1AValidationError):
    """The test partition was used during fit or model/hyperparameter selection.

    See docs/adr/ADR-002-test-set-isolation.md,
    docs/specs/SPEC-000-master.md INV-05.
    """


class ClassConsistencyError(WP1AValidationError):
    """The set of classes is inconsistent with the canonical 21-class
    definition, or diverges in a way that breaks evaluation validity
    (e.g. a class evaluated but never seen in training).

    See docs/specs/SPEC-000-master.md DS-03.
    """


class SplitReproducibilityError(WP1AValidationError):
    """A data split is not reproducible from its declared seed.

    See docs/adr/ADR-003-reproducibility-requirements.md, REP-01/REP-02.
    """


class IncompleteMetadataError(WP1AValidationError):
    """Experiment metadata is missing required reproducibility fields.

    See docs/adr/ADR-003-reproducibility-requirements.md, REP-01..REP-06.
    """


class CanonicalDatasetError(WP1AValidationError):
    """Canonical dataset registry or table is inconsistent with SPEC-002 / ADR-004.

    See docs/specs/SPEC-002-canonical-dataset.md,
    docs/adr/ADR-004-canonical-dataset.md.
    """
