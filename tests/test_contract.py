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
TOPOLOGY = ROOT / "evidence-paper-reader" / "references" / "evidence-topology.md"
DEPENDENCE_REF = ROOT / "evidence-paper-reader" / "references" / "evidence-dependence.md"
ECHINACEA_FIXTURE = ROOT / "tests" / "fixtures" / "historical-echinacea-2010-audit.md"
AKT_FIXTURE = ROOT / "tests" / "fixtures" / "historical-akt-inos-2010-audit.md"
BMD_REPLICATION_FIXTURE = ROOT / "tests" / "fixtures" / "historical-bmd-gwas-replication-2010-audit.md"

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
        cls.topology = TOPOLOGY.read_text(encoding="utf-8")
        cls.dependence_ref = DEPENDENCE_REF.read_text(encoding="utf-8")
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
        self.assertGreaterEqual(len(FIXTURES), 15)
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


    def test_historical_topology_rules_are_explicit(self):
        for label in [
            "mechanical coupling",
            "null-result overreach",
            "proxy reification",
            "selection-conditioned evidence",
        ]:
            self.assertIn(label, self.pollution)
        for heading in [
            "## 1. Mechanical coupling",
            "## 3. Selection-conditioned evidence",
            "## 4. Null-result boundary",
            "## 5. Proxy-to-construct boundary",
        ]:
            self.assertIn(heading, self.topology)

    def test_finance_medicine_and_empirical_arts_are_covered(self):
        self.assertIn("administrative or transactional record", self.allowed)
        self.assertIn("intervention", validate_audit.CLAIM_TYPES)
        self.assertIn("### Finance, econometrics, and market-microstructure papers", self.skill)
        self.assertIn("### Clinical and biomedical empirical papers", self.skill)
        self.assertIn("### Empirical aesthetics and human-subject arts research", self.skill)
        self.assertIn("Do not translate `not statistically significant`", self.skill)
        self.assertIn("operational proxy", self.skill)

    def test_evidence_dependence_and_triangulation_are_explicit(self):
        for label in [
            "single-source",
            "shared-source convergence",
            "partially independent convergence",
            "independent convergence",
            "unclear",
        ]:
            self.assertIn(label, validate_audit.DEPENDENCE)
            self.assertIn(label, self.dependence_ref)
        self.assertIn("pseudo-triangulation", self.pollution)
        self.assertIn("evidence dependence:", self.skill)

    def test_real_fixtures_distinguish_shared_partial_and_independent_convergence(self):
        echinacea = ECHINACEA_FIXTURE.read_text(encoding="utf-8")
        akt = AKT_FIXTURE.read_text(encoding="utf-8")
        bmd = BMD_REPLICATION_FIXTURE.read_text(encoding="utf-8")
        self.assertIn("- evidence dependence: shared-source convergence", echinacea)
        self.assertIn("- evidence dependence: partially independent convergence", akt)
        self.assertIn("- evidence dependence: independent convergence", bmd)

    def test_validator_rejects_unknown_evidence_dependence(self):
        text = RESNET_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence dependence: single-source",
            "- evidence dependence: many confirmations",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("invalid evidence dependence" in error for error in errors), errors)

    def test_validator_rejects_unknown_evidence_label(self):
        text = RESNET_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence type: computational benchmark",
            "- evidence type: benchmark experiment",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("unknown evidence label" in error for error in errors), errors)

    def test_validator_rejects_external_provenance_without_dependency(self):
        text = RESNET_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence provenance: paper-local",
            "- evidence provenance: external citation",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("requires a named external dependency" in error for error in errors), errors)

    def test_validator_rejects_literature_citation_as_paper_local(self):
        text = RESNET_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence type: computational benchmark",
            "- evidence type: literature citation",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("cannot be labeled paper-local" in error for error in errors), errors)

    def test_validator_rejects_section_reordering(self):
        text = RESNET_FIXTURE.read_text(encoding="utf-8")
        a = text.index("## 4. what is usable")
        b = text.index("## 5. what to downweight")
        c = text.index("## 6. value breakdown")
        broken = text[:a] + text[b:c] + text[a:b] + text[c:]
        errors = validate_audit.validate(broken, self.allowed)
        self.assertTrue(any("out of order" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
