import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader" / "SKILL.md"
EVIDENCE_TYPES = ROOT / "evidence-paper-reader" / "references" / "evidence-types.md"
FOLLOW_UP = ROOT / "evidence-paper-reader" / "references" / "follow-up-boundaries.md"
RESNET_FIXTURE = ROOT / "tests" / "fixtures" / "resnet-smoke-audit.md"
FIXTURES = sorted((ROOT / "tests" / "fixtures").glob("*-audit.md"))
POLLUTION = ROOT / "evidence-paper-reader" / "references" / "pollution-patterns.md"

spec = importlib.util.spec_from_file_location("validate_audit", ROOT / "tests" / "validate_audit.py")
validate_audit = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_audit)


class SkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.evidence = EVIDENCE_TYPES.read_text(encoding="utf-8")
        cls.follow_up = FOLLOW_UP.read_text(encoding="utf-8")
        cls.pollution = POLLUTION.read_text(encoding="utf-8")
        cls.allowed = validate_audit.evidence_labels(cls.evidence)

    def test_fixed_output_sections_are_unique_and_ordered(self):
        positions = []
        for heading in validate_audit.SECTION_HEADINGS:
            self.assertEqual(self.skill.count(heading), 1, heading)
            positions.append(self.skill.index(heading))
        self.assertEqual(positions, sorted(positions))

    def test_scope_gate_and_out_of_scope_behavior_are_explicit(self):
        for status in ["`in scope`", "`partially in scope`", "`out of scope`"]:
            self.assertIn(status, self.skill)
        self.assertIn("do not force 3 to 5 artificial claims", self.skill)
        self.assertIn("preserve the seven-section output skeleton", self.skill)

    def test_benchmark_evidence_has_its_own_controlled_label(self):
        self.assertIn("computational benchmark", self.allowed)
        self.assertIn("Do not collapse computational benchmark into direct experiment.", self.evidence)
        self.assertIn("Do not collapse computational benchmark into numerical simulation.", self.evidence)

    def test_citation_dependency_cannot_masquerade_as_local_evidence(self):
        self.assertIn("A literature citation is not paper-local evidence.", self.skill)
        self.assertIn("paper-local", self.follow_up)
        self.assertIn("external citation", self.follow_up)
        self.assertIn("mixed", self.follow_up)
        self.assertIn("Do not guess a DOI from memory.", self.follow_up)

    def test_all_real_paper_fixtures_satisfy_contract(self):
        self.assertGreaterEqual(len(FIXTURES), 6)
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture.name):
                errors = validate_audit.validate(fixture.read_text(encoding="utf-8"), self.allowed)
                self.assertEqual(errors, [])

    def test_cross_section_consistency_rule_is_explicit(self):
        self.assertIn("cross-section consistency scan", self.skill)
        self.assertIn("internal inconsistency", self.pollution)
        self.assertIn("Do not let summary prose override", self.skill)

    def test_validation_independence_rule_is_explicit(self):
        self.assertIn("Check whether validation is independent", self.skill)
        self.assertIn("non-independent validation", self.pollution)
        self.assertIn("fit to target", self.skill)

    def test_validator_rejects_unknown_evidence_label(self):
        text = RESNET_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence type: computational benchmark",
            "- evidence type: benchmark experiment",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("unknown evidence label" in error for error in errors), errors)

    def test_validator_rejects_external_provenance_without_dependency(self):
        text = FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence provenance: paper-local",
            "- evidence provenance: external citation",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("requires a named external dependency" in error for error in errors), errors)

    def test_validator_rejects_literature_citation_as_paper_local(self):
        text = FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence type: computational benchmark",
            "- evidence type: literature citation",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("cannot be labeled paper-local" in error for error in errors), errors)

    def test_validator_rejects_section_reordering(self):
        text = FIXTURE.read_text(encoding="utf-8")
        a = text.index("## 4. what is usable")
        b = text.index("## 5. what to downweight")
        c = text.index("## 6. value breakdown")
        broken = text[:a] + text[b:c] + text[a:b] + text[c:]
        errors = validate_audit.validate(broken, self.allowed)
        self.assertTrue(any("out of order" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
