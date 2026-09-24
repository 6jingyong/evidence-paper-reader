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
CLAIM_LINKS_REF = ROOT / "evidence-paper-reader" / "references" / "claim-evidence-links.md"
CLAIM_DEPENDENCIES_REF = ROOT / "evidence-paper-reader" / "references" / "claim-dependencies.md"
FIGURE_TRAPS_REF = ROOT / "evidence-paper-reader" / "references" / "figure-and-table-traps.md"
STATISTICAL_TRAPS_REF = ROOT / "evidence-paper-reader" / "references" / "statistical-traps.md"
MEASUREMENT_TRAPS_REF = ROOT / "evidence-paper-reader" / "references" / "measurement-traps.md"
STUDY_DESIGN_TRAPS_REF = ROOT / "evidence-paper-reader" / "references" / "study-design-traps.md"
ECHINACEA_FIXTURE = ROOT / "tests" / "fixtures" / "historical-echinacea-2010-audit.md"
AKT_FIXTURE = ROOT / "tests" / "fixtures" / "historical-akt-inos-2010-audit.md"
BMD_REPLICATION_FIXTURE = ROOT / "tests" / "fixtures" / "historical-bmd-gwas-replication-2010-audit.md"
BEAUTY_FIXTURE = ROOT / "tests" / "fixtures" / "historical-brain-beauty-2011-audit.md"
ADVERSARIAL_SUBGROUP = ROOT / "tests" / "fixtures" / "adversarial-subgroup-aneurysm-2008-audit.md"
ADVERSARIAL_ORGANIC = ROOT / "tests" / "fixtures" / "adversarial-organic-diet-biomarkers-2019-audit.md"
ADVERSARIAL_BEFORE_AFTER = ROOT / "tests" / "fixtures" / "adversarial-care-coordination-before-after-2009-audit.md"
ADVERSARIAL_LEAKAGE = ROOT / "tests" / "fixtures" / "adversarial-train-test-leakage-2022-audit.md"
ADVERSARIAL_DIC = ROOT / "tests" / "fixtures" / "adversarial-collagen-dic-2021-audit.md"

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
        cls.claim_links_ref = CLAIM_LINKS_REF.read_text(encoding="utf-8")
        cls.claim_dependencies_ref = CLAIM_DEPENDENCIES_REF.read_text(encoding="utf-8")
        cls.figure_traps_ref = FIGURE_TRAPS_REF.read_text(encoding="utf-8")
        cls.statistical_traps_ref = STATISTICAL_TRAPS_REF.read_text(encoding="utf-8")
        cls.measurement_traps_ref = MEASUREMENT_TRAPS_REF.read_text(encoding="utf-8")
        cls.study_design_traps_ref = STUDY_DESIGN_TRAPS_REF.read_text(encoding="utf-8")
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
        self.assertGreaterEqual(len(FIXTURES), 20)
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

    def test_claim_evidence_links_and_reuse_are_explicit(self):
        self.assertIn("Stable identity rule", self.claim_links_ref)
        self.assertIn("Claim stacking", self.claim_links_ref)
        self.assertIn("claim stacking / evidence double-spending", self.pollution)
        self.assertIn("evidence nodes:", self.skill)

    def test_brain_beauty_fixture_exposes_evidence_reuse_across_claims(self):
        text = BEAUTY_FIXTURE.read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("- evidence nodes: E1 + E2"), 4)
        self.assertIn("- support level: sufficient", text)
        self.assertIn("- support level: partial", text)
        self.assertIn("- support level: insufficient", text)

    def test_claim_dependencies_and_uncertainty_propagation_are_explicit(self):
        self.assertIn("Uncertainty propagation", self.claim_dependencies_ref)
        self.assertIn("inference-chain laundering", self.claim_dependencies_ref)
        self.assertIn("upstream claims:", self.skill)
        self.assertIn("inference-chain laundering", self.pollution)

    def test_validator_rejects_forward_claim_dependency(self):
        text = BEAUTY_FIXTURE.read_text(encoding="utf-8").replace(
            "- upstream claims: none",
            "- upstream claims: C2",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("must reference earlier claims only" in error for error in errors), errors)

    def test_validator_propagates_uncertainty_without_new_evidence(self):
        text = BEAUTY_FIXTURE.read_text(encoding="utf-8").replace(
            "- support level: insufficient",
            "- support level: sufficient",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(
            any("downstream claim cannot be sufficient" in error for error in errors),
            errors,
        )

    def test_figure_and_table_world_knowledge_is_bounded_and_explicit(self):
        for phrase in [
            "Truncated baseline",
            "Dual y-axes",
            "Denominator drift",
            "Simpson's paradox",
            "Error-bar identity",
            "Representative image",
            "Adjusted versus unadjusted estimates",
        ]:
            self.assertIn(phrase, self.figure_traps_ref)
        self.assertIn("Treat figures and tables as evidence objects", self.skill)
        self.assertIn("visual impression overreach", self.pollution)

    def test_methodological_world_knowledge_is_modular_and_bounded(self):
        self.assertIn("Methodological knowledge boundary", self.skill)
        self.assertIn("Do not run every methodological trap on every paper.", self.skill)
        self.assertIn("Do not use generic field knowledge to overwrite a paper-local result.", self.skill)
        for ref in [
            "references/statistical-traps.md",
            "references/measurement-traps.md",
            "references/study-design-traps.md",
        ]:
            self.assertIn(ref, self.skill)

    def test_statistical_traps_cover_high_value_inference_failures(self):
        for phrase in [
            "Effect size before significance",
            "Multiple testing and selection",
            "Optional stopping and repeated looks",
            "Regression to the mean",
            "Significant in one group, not significant in another",
            "Collider conditioning",
            "Dependence and standard errors",
            "Missing data",
        ]:
            self.assertIn(phrase, self.statistical_traps_ref)

    def test_measurement_traps_cover_validity_and_instrument_failures(self):
        for phrase in [
            "Reliability versus validity",
            "Calibration and drift",
            "Limit of detection and quantification",
            "Saturation, ceiling, and floor effects",
            "Batch, lot, and operator effects",
            "Specificity and cross-reactivity",
            "Surrogate endpoints",
            "Preprocessing dependence",
        ]:
            self.assertIn(phrase, self.measurement_traps_ref)

    def test_study_design_traps_cover_identification_failures(self):
        for phrase in [
            "Unit of assignment versus unit of analysis",
            "Before-after without a concurrent control",
            "Attrition and informative censoring",
            "Immortal-time and time-alignment bias",
            "Difference-in-differences and interrupted time series",
            "Instrumental-variable and natural-experiment designs",
            "Benchmark and ML design",
            "Temporal leakage",
        ]:
            self.assertIn(phrase, self.study_design_traps_ref)

    def test_adversarial_suite_triggers_distinct_method_modules(self):
        subgroup = ADVERSARIAL_SUBGROUP.read_text(encoding="utf-8")
        organic = ADVERSARIAL_ORGANIC.read_text(encoding="utf-8")
        before_after = ADVERSARIAL_BEFORE_AFTER.read_text(encoding="utf-8")
        leakage = ADVERSARIAL_LEAKAGE.read_text(encoding="utf-8")
        dic = ADVERSARIAL_DIC.read_text(encoding="utf-8")

        self.assertIn("interaction", subgroup.lower())
        self.assertIn("subgroup", subgroup.lower())
        self.assertIn("below detection", organic.lower())
        self.assertIn("benjamini-hochberg", organic.lower())
        self.assertIn("regression to the mean", before_after.lower())
        self.assertIn("concurrent control", before_after.lower())
        self.assertIn("train-test leakage", leakage.lower())
        self.assertIn("ranking", leakage.lower())
        self.assertIn("technical repeats", dic.lower())
        self.assertIn("independent fibrils", dic.lower())

    def test_measurement_reference_handles_threshold_coding_and_fit_error(self):
        self.assertIn("Thresholded or detectability outcomes", self.measurement_traps_ref)
        self.assertIn("reference category", self.measurement_traps_ref)
        self.assertIn("not independent validation", self.measurement_traps_ref)
        self.assertIn("fit error", self.measurement_traps_ref)

    def test_validator_rejects_malformed_evidence_nodes(self):
        text = RESNET_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence nodes: E1",
            "- evidence nodes: Figure4",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("invalid evidence nodes" in error for error in errors), errors)

    def test_validator_requires_two_nodes_for_convergence(self):
        text = BMD_REPLICATION_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence nodes: E1 + E2",
            "- evidence nodes: E1",
            1,
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(
            any("convergence dependence requires at least two evidence nodes" in error for error in errors),
            errors,
        )

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
