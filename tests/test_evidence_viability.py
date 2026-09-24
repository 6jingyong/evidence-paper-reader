import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
VALIDATOR = SKILL / "scripts" / "validate_audit.py"
RENDERER = SKILL / "scripts" / "render_audit.py"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"
VIABILITY_REF = SKILL / "references" / "evidence-viability.md"
FIXTURES = ROOT / "tests" / "viability-fixtures"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_module("viability_validator", VALIDATOR)
renderer = load_module("viability_renderer", RENDERER)


class EvidenceViabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.allowed = validator.evidence_labels(EVIDENCE_TYPES.read_text(encoding="utf-8"))
        cls.ref = VIABILITY_REF.read_text(encoding="utf-8")

    def test_reference_covers_evidence_shaped_non_auditable_content(self):
        for phrase in [
            "Critical method omission",
            "Critical result omission",
            "Self-referential construct",
            "Circular validation",
            "Demo-only evidence",
            "Proprietary black box",
            "Promotional asymmetry",
            "New terminology is not a problem by itself.",
            "Commercial or proprietary work is not automatically non-auditable.",
        ]:
            self.assertIn(phrase, self.ref)

    def test_all_viability_fixtures_validate(self):
        files = sorted(FIXTURES.glob("*-audit.md"))
        self.assertEqual(len(files), 3)
        for file in files:
            with self.subTest(file=file.name):
                errors = validator.validate(file.read_text(encoding="utf-8"), self.allowed)
                self.assertEqual(errors, [])

    def test_non_auditable_fixture_does_not_manufacture_claims(self):
        text = (FIXTURES / "synthetic-promotional-brief-audit.md").read_text(encoding="utf-8")
        self.assertIn("- evidence viability: non-auditable", text)
        self.assertNotIn("### claim 1", text)
        self.assertIn("promotional-asymmetry", text)
        self.assertIn("not applicable", text.lower())

    def test_self_referential_construct_is_separate_from_new_terminology(self):
        text = (FIXTURES / "synthetic-self-referential-framework-audit.md").read_text(encoding="utf-8")
        self.assertIn("self-referential-construct", text)
        self.assertIn("circular-validation", text)
        self.assertIn("independent", text.lower())

    def test_partially_auditable_fixture_may_have_fewer_than_three_claims(self):
        text = (FIXTURES / "synthetic-partially-auditable-tech-note-audit.md").read_text(encoding="utf-8")
        self.assertIn("- evidence viability: partially auditable", text)
        self.assertEqual(text.count("### claim 1"), 2)
        self.assertEqual(text.count("### claim 2"), 2)
        self.assertNotIn("### claim 3", text)
        self.assertEqual(validator.validate(text, self.allowed), [])

    def test_renderer_rejects_non_auditable_claim_manufacturing(self):
        ledger = dict(renderer.TEMPLATE)
        ledger["evidence_viability"] = "non-auditable"
        ledger["viability_flags"] = ["critical-method-omission"]
        ledger["not_applicable_reason"] = "No reconstructable evidence chain."
        errors = renderer.validate_ledger(ledger)
        self.assertTrue(any("empty claims list" in error for error in errors), errors)

    def test_renderer_requires_flags_for_partial_or_non_auditable(self):
        partial = dict(renderer.TEMPLATE)
        partial["evidence_viability"] = "partially auditable"
        partial["viability_flags"] = []
        errors = renderer.validate_ledger(partial)
        self.assertTrue(any("requires at least one viability flag" in error for error in errors), errors)

    def test_renderer_accepts_two_claim_partial_ledger(self):
        ledger = dict(renderer.TEMPLATE)
        ledger["evidence_viability"] = "partially auditable"
        ledger["viability_flags"] = ["proprietary-black-box"]
        ledger["claims"] = renderer.TEMPLATE["claims"][:2]
        # Fill the template placeholders sufficiently to isolate claim-count behavior.
        ledger["paper_type"] = "technical note"
        ledger["reader_conclusion"] = "Only part of the evidence chain is reconstructable."
        ledger["usable"] = {
            "results": "A bounded result is usable.",
            "methods_or_design": "Only part of the method is documented.",
            "materials_or_documentation": "Some operating documentation is usable.",
        }
        ledger["downweight"] = {
            "worth_noticing": "The local result remains useful.",
            "cautious_or_ignore": "The proprietary mechanism is unresolved.",
        }
        ledger["uncertainty_and_follow_up"] = "The proprietary component is unavailable."
        for i, claim in enumerate(ledger["claims"], start=1):
            claim["content"] = f"Reconstructable claim {i}."
            claim["support"]["evidence_type"] = ["author interpretation"]
            claim["support"]["source_location"] = f"section {i}"
            claim["support"]["reason"] = "The disclosed material supports only this bounded claim."
        self.assertEqual(renderer.validate_ledger(ledger), [])


if __name__ == "__main__":
    unittest.main()
