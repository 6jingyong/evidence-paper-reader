#!/usr/bin/env python3
"""Compatibility wrapper for the packaged Evidence Paper Reader validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "evidence-paper-reader" / "scripts" / "validate_audit.py"
SPEC = importlib.util.spec_from_file_location("packaged_validate_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

SECTION_HEADINGS = MODULE.SECTION_HEADINGS
CLAIM_TYPES = MODULE.CLAIM_TYPES
CONCLUSION_STRENGTHS = MODULE.CONCLUSION_STRENGTHS
SUPPORT_LEVELS = MODULE.SUPPORT_LEVELS
PROVENANCE = MODULE.PROVENANCE
DEPENDENCE = MODULE.DEPENDENCE
VALUE_LEVELS = MODULE.VALUE_LEVELS
SCOPE_STATUSES = MODULE.SCOPE_STATUSES
VALUE_FIELDS = MODULE.VALUE_FIELDS

evidence_labels = MODULE.evidence_labels
validate = MODULE.validate
main = MODULE.main

if __name__ == "__main__":
    raise SystemExit(main())
