import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL_DIR = ROOT / "evidence-paper-reader"
REFS = SKILL_DIR / "references"
SCRIPTS = SKILL_DIR / "scripts"
SKILL = SKILL_DIR / "SKILL.md"
EVIDENCE_TYPES = REFS / "evidence-types.md"
CORE_CONTRACT = REFS / "core-contract.md"
EVIDENCE_VIABILITY = REFS / "evidence-viability.md"
OUTPUT_CONTRACT = REFS / "output-contract.md"
AUDIT_LEDGER_FORMAT = REFS / "audit-ledger-format.md"
METHOD_ROUTER = REFS / "method-router.md"
DOMAIN_PROFILES = REFS / "domain-profiles.md"
FOLLOW_UP = REFS / "follow-up-boundaries.md"
POLLUTION = REFS / "pollution-patterns.md"
TOPOLOGY = REFS / "evidence-topology.md"
DEPENDENCE_REF = REFS / "evidence-dependence.md"
CLAIM_LINKS_REF = REFS / "claim-evidence-links.md"
CLAIM_DEPENDENCIES_REF = REFS / "claim-dependencies.md"
FIGURE_TRAPS_REF = REFS / "figure-and-table-traps.md"
STATISTICAL_TRAPS_REF = REFS / "statistical-traps.md"
MEASUREMENT_TRAPS_REF = REFS / "measurement-traps.md"
STUDY_DESIGN_TRAPS_REF = REFS / "study-design-traps.md"
FALSE_POSITIVE_GUARDS_REF = REFS / "false-positive-guards.md"
ROUTER_SCRIPT = SCRIPTS / "suggest_modules.py"
RENDERER_SCRIPT = SCRIPTS / "render_audit.py"
PACKAGED_VALIDATOR_SCRIPT = SCRIPTS / "validate_audit.py"

FIXTURES = sorted((ROOT / "tests" / "fixtures").glob("*-audit.md"))
RESNET_FIXTURE = ROOT / "tests" / "fixtures" / "resnet-smoke-audit.md"
ECHINACEA_FIXTURE = ROOT / "tests" / "fixtures" / "historical-echinacea-2010-audit.md"
AKT_FIXTURE = ROOT / "tests" / "fixtures" / "historical-akt-inos-2010-audit.md"
BMD_REPLICATION_FIXTURE = ROOT / "tests" / "fixtures" / "historical-bmd-gwas-replication-2010-audit.md"
BEAUTY_FIXTURE = ROOT / "tests" / "fixtures" / "historical-brain-beauty-2011-audit.md"
ADVERSARIAL_SUBGROUP = ROOT / "tests" / "fixtures" / "adversarial-subgroup-aneurysm-2008-audit.md"
ADVERSARIAL_ORGANIC = ROOT / "tests" / "fixtures" / "adversarial-organic-diet-biomarkers-2019-audit.md"
ADVERSARIAL_BEFORE_AFTER = ROOT / "tests" / "fixtures" / "adversarial-care-coordination-before-after-2009-audit.md"
ADVERSARIAL_LEAKAGE = ROOT / "tests" / "fixtures" / "adversarial-train-test-leakage-2022-audit.md"
ADVERSARIAL_DIC = ROOT / "tests" / "fixtures" / "adversarial-collagen-dic-2021-audit.md"
ANTI_SPRINT = ROOT / "tests" / "fixtures" / "anti-trigger-sprint-2015-audit.md"
ANTI_LOD = ROOT / "tests" / "fixtures" / "anti-trigger-lod-multiple-imputation-2011-audit.md"
ANTI_DID = ROOT / "tests" / "fixtures" / "anti-trigger-difference-in-differences-2014-audit.md"
ANTI_HIERARCHY = ROOT / "tests" / "fixtures" / "anti-trigger-multisite-imaging-2023-audit.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_audit = load_module("validate_audit", PACKAGED_VALIDATOR_SCRIPT)
suggest_modules = load_module("suggest_modules", ROUTER_SCRIPT)
render_audit = load_module("render_audit", RENDERER_SCRIPT)


class SkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.evidence = EVIDENCE_TYPES.read_text(encoding="utf-8")
        cls.core = CORE_CONTRACT.read_text(encoding="utf-8")
        cls.viability_ref = EVIDENCE_VIABILITY.read_text(encoding="utf-8")
        cls.output = OUTPUT_CONTRACT.read_text(encoding="utf-8")
        cls.ledger_format = AUDIT_LEDGER_FORMAT.read_text(encoding="utf-8")
        cls.router = METHOD_ROUTER.read_text(encoding="utf-8")
        cls.domains = DOMAIN_PROFILES.read_text(encoding="utf-8")
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
        cls.false_positive_guards_ref = FALSE_POSITIVE_GUARDS_REF.read_text(encoding="utf-8")
        cls.allowed = validate_audit.evidence_labels(cls.evidence)

    def test_skill_is_thin_orchestrator(self):
        self.assertLessEqual(len(self.skill.splitlines()), 180)
        for ref in [
            "references/core-contract.md",
            "references/evidence-viability.md",
            "references/output-contract.md",
            "references/audit-ledger-format.md",
            "references/evidence-types.md",
            "references/method-router.md",
        ]:
            self.assertIn(ref, self.skill)
        self.assertIn("Flash path", self.skill)
        self.assertIn("Full path", self.skill)
        self.assertNotIn("Weak-model", self.skill)
        self.assertIn("Do not load every optional reference by default.", self.skill)
        self.assertIn("Flash means less irrelevant context, not less work.", self.skill)

    def test_skill_is_logic_audit_not_scientific_policing(self):
        for phrase in [
            "general claim–evidence–reasoning audit",
            "Do not adjudicate ultimate scientific truth",
            "investigate misconduct",
            "infer author intent",
        ]:
            self.assertIn(phrase, self.skill)

        for phrase in [
            "Audit target: claim → evidence → reasoning",
            "audits logical reach, not scientific authority",
            "a fraud, fabrication, falsification, or misconduct investigation",
            "do not infer blame",
        ]:
            self.assertIn(phrase, self.core)

        for phrase in [
            "evidence usability, not culpability",
            "does not independently determine fabrication, falsification, misconduct, deception, or author intent",
            "what happens to the claim-evidence chain",
        ]:
            self.assertIn(phrase, self.viability_ref)

    def test_author_acknowledged_boundaries_are_explicit_and_support_neutral(self):
        for phrase in [
            "Author-acknowledged boundaries",
            "Author acknowledgment is not evidence for the claim",
            "Absence of acknowledgment does not imply deception",
        ]:
            self.assertIn(phrase, self.core)

        for phrase in [
            "author boundary: explicit | partial | absent | unclear | not-applicable",
            "author acknowledgment:",
            "author-boundary source:",
            "the authors themselves also limit this point",
        ]:
            self.assertIn(phrase, self.output)

        self.assertIn(
            "check whether the source authors explicitly acknowledge the same boundary",
            self.skill,
        )

    def test_fixed_output_sections_are_unique_and_ordered_in_output_contract(self):
        positions = []
        for heading in validate_audit.SECTION_HEADINGS:
            self.assertEqual(self.output.count(heading), 1, heading)
            positions.append(self.output.index(heading))
        self.assertEqual(positions, sorted(positions))

    def test_core_contract_has_scope_graph_and_support_semantics(self):
        for status in ["in scope", "partially in scope", "out of scope"]:
            self.assertIn(status, self.core)
        for phrase in [
            "Evidence viability before claims",
            "Evidence nodes",
            "Claim dependencies",
            "Evidence provenance",
            "Evidence dependence",
            "Support level",
            "Direct evidence wins over narrative summary",
            "Methodological risk is not a verdict",
            "Domain knowledge boundary",
        ]:
            self.assertIn(phrase, self.core)

    def test_core_claims_are_source_facing_not_auditor_diagnostics(self):
        for phrase in [
            "Core claims must be source-facing",
            "Do not use auditor diagnostics",
            "belong in support reasoning/downweighting",
            "A methodological claim may be selected when the paper itself claims",
        ]:
            self.assertIn(phrase, self.core)

    def test_evidence_viability_gate_is_explicit_and_non_prestige_based(self):
        for phrase in [
            "auditable",
            "partially auditable",
            "non-auditable",
            "self-referential-construct",
            "promotional-asymmetry",
            "New terminology is not a problem by itself.",
            "Commercial or proprietary work is not automatically non-auditable.",
            "The gate is about whether the evidence chain can be reconstructed",
        ]:
            self.assertIn(phrase, self.viability_ref)
        self.assertIn("evidence viability:", self.output)
        self.assertIn("viability flags:", self.output)
        self.assertIn("evidence-viability.md", self.skill)
        self.assertIn("evidence-viability.md", self.router)

    def test_router_separates_mandatory_and_optional_context(self):
        for ref in ["core-contract.md", "evidence-viability.md", "evidence-types.md", "audit-ledger-format.md", "output-contract.md"]:
            self.assertIn(ref, self.router)
        for ref in [
            "figure-and-table-traps.md",
            "statistical-traps.md",
            "measurement-traps.md",
            "study-design-traps.md",
            "evidence-topology.md",
            "evidence-dependence.md",
            "claim-evidence-links.md",
            "claim-dependencies.md",
            "follow-up-boundaries.md",
            "false-positive-guards.md",
        ]:
            self.assertIn(ref, self.router)
        self.assertIn("Do not keep all optional references in context", self.router)

    def test_router_script_is_advisory_selective_and_guarded(self):
        complex_result = suggest_modules.suggest_modules(
            "Randomized trial with subgroup interaction, hazard ratio, "
            "biomarker assay below the limit of detection and a calibration curve."
        )
        names = {item["module"] for item in complex_result["suggested"]}
        self.assertIn("statistical-traps.md", names)
        self.assertIn("measurement-traps.md", names)
        self.assertIn("study-design-traps.md", names)
        self.assertIn("false-positive-guards.md", names)
        self.assertNotIn("figure-and-table-traps.md", names)
        self.assertEqual(complex_result["recommended_path"], "full")
        self.assertGreaterEqual(complex_result["primary_module_count"], 3)
        self.assertIn("candidate routes only", complex_result["warning"])
        self.assertIn("semantic-router-card.md", complex_result["warning"])
        self.assertIn("never lowers the audit contract", complex_result["warning"])
        self.assertTrue(complex_result["semantic_router_required"])
        self.assertEqual(complex_result["merge_with"], "merge_route.py")
        self.assertEqual(complex_result["context_with"], "build_context.py")

        flash_result = suggest_modules.suggest_modules(
            "Randomized trial reporting a hazard ratio for the primary outcome."
        )
        self.assertEqual(flash_result["recommended_path"], "flash")
        self.assertLess(flash_result["primary_module_count"], 3)
        self.assertEqual(flash_result["render_with"], "render_audit.py")
        self.assertEqual(flash_result["validate_with"], "validate_audit.py")
        self.assertEqual(flash_result["complete_with"], "audit_gate.py")

    def test_renderer_turns_structured_ledger_into_valid_markdown(self):
        ledger = {
            "scope_status": "in scope",
            "evidence_viability": "auditable",
            "viability_flags": [],
            "paper_type": "computational benchmark study",
            "reader_conclusion": "The paper supports a bounded performance claim but not a broad mechanism claim.",
            "claims": [
                {
                    "content": "Method A improves benchmark accuracy on dataset X.",
                    "claim_type": "performance",
                    "conclusion_strength": "medium",
                    "support": {
                        "evidence_type": ["computational benchmark", "statistical analysis"],
                        "evidence_provenance": "paper-local",
                        "evidence_nodes": ["E1", "E2"],
                        "upstream_claims": [],
                        "evidence_dependence": "shared-source convergence",
                        "source_location": "Results; Table 2",
                        "support_level": "sufficient",
                        "reason": "The held-out benchmark comparison directly supports the bounded performance claim.",
                        "external_dependency": "none",
                    },
                },
                {
                    "content": "The gain is caused by component B.",
                    "claim_type": "mechanistic",
                    "conclusion_strength": "strong",
                    "support": {
                        "evidence_type": ["computational benchmark"],
                        "evidence_provenance": "paper-local",
                        "evidence_nodes": ["E1", "E2"],
                        "upstream_claims": [1],
                        "evidence_dependence": "shared-source convergence",
                        "source_location": "Ablation section",
                        "support_level": "partial",
                        "reason": "The ablation is compatible with the mechanism but does not uniquely establish it.",
                        "external_dependency": "none",
                    },
                },
                {
                    "content": "The method generalizes beyond dataset X.",
                    "claim_type": "generality",
                    "conclusion_strength": "strong",
                    "support": {
                        "evidence_type": ["computational benchmark"],
                        "evidence_provenance": "paper-local",
                        "evidence_nodes": ["E3"],
                        "upstream_claims": [1],
                        "evidence_dependence": "single-source",
                        "source_location": "Results; Dataset Y",
                        "support_level": "partial",
                        "reason": "One additional dataset broadens the result but does not establish universal generality.",
                        "external_dependency": "none",
                    },
                },
            ],
            "usable": {
                "results": "The benchmark estimates are usable.",
                "methods_or_design": "The held-out comparison is reusable.",
                "materials_or_documentation": "Dataset and evaluation details are documented.",
            },
            "downweight": {
                "worth_noticing": "The ablation is suggestive rather than decisive.",
                "cautious_or_ignore": "Do not convert two datasets into universal generality.",
            },
            "value_breakdown": {
                "result": "high",
                "method": "high",
                "theory_or_insight": "medium",
                "research_design": "high",
                "material_or_documentation": "high",
            },
            "uncertainty_and_follow_up": "Independent-domain replication would test generality.",
        }
        self.assertEqual(render_audit.validate_ledger(ledger), [])
        markdown = render_audit.render(ledger)
        self.assertIn("- evidence viability: auditable", markdown)
        self.assertIn("- viability flags: none", markdown)
        self.assertIn("### claim 1", markdown)
        self.assertIn("- evidence nodes: E1 + E2", markdown)
        self.assertIn("- upstream claims: C1", markdown)
        self.assertEqual(validate_audit.validate(markdown, self.allowed), [])

    def test_renderer_rejects_structural_shortcuts(self):
        ledger = dict(render_audit.TEMPLATE)
        ledger["claims"] = ledger["claims"][:2]
        errors = render_audit.validate_ledger(ledger)
        self.assertTrue(any("3 to 5 claims" in error for error in errors), errors)

    def test_output_format_is_script_owned_when_runtime_exists(self):
        for phrase in [
            "structured JSON ledger",
            "claim numbering",
            "evidence-node formatting",
            "upstream-claim formatting",
            "Rendering is mechanical. Claim–evidence–reasoning judgment is not.",
        ]:
            self.assertIn(phrase, self.ledger_format)
        self.assertIn("scripts/audit_gate.py", self.skill)
        self.assertIn("scripts/build_context.py", self.skill)
        self.assertIn("scripts/render_audit.py", self.skill)
        self.assertIn("scripts/validate_audit.py", self.skill)
        self.assertIn("Do not bypass a failed gate", self.skill)

    def test_completion_gate_recomputes_routing_from_raw_artifacts(self):
        for phrase in [
            "raw semantic-route JSON",
            "--semantic-route semantic-route.json",
            "--router-text paper.txt",
            "--context-bundle audit-context.md",
            "--module-checks module-checks.json",
            "regenerates the expected context bundle byte-for-byte",
            "requires exact per-claim routed-module execution records",
            "lexical-route JSON is only a cache",
        ]:
            self.assertIn(phrase, self.skill)
        self.assertIn("--semantic-route semantic-route.json", self.ledger_format)
        self.assertIn("--module-checks module-checks.json", self.ledger_format)
        self.assertIn("trap-module entries must confirm", self.ledger_format)
        self.assertIn("unresolved `unclear` routed check prevents `sufficient` support", self.ledger_format)
        self.assertIn("an `unclear` routed check cannot coexist with `sufficient` support", self.skill)
        self.assertIn("precise paper source location/material gap", self.skill)
        self.assertIn("at least one precise paper source location", self.ledger_format)
        self.assertIn("deterministic recomputation", self.ledger_format)

    def test_routing_precedes_inventory_execution(self):
        route_pos = self.skill.index("### Phase B — route and decide evidence handling")
        inventory_pos = self.skill.index("### Phase C — evidence inventory and ledger")
        self.assertLess(route_pos, inventory_pos)
        self.assertIn("Follow the recomputed route's evidence-inventory decision.", self.skill)
        self.assertIn("if the recomputed route requires inventory, build it now", self.skill)
        self.assertIn(
            "execute the inventory path only after semantic+lexical routing has been merged/recomputed",
            self.router,
        )

    def test_flash_path_cannot_be_used_as_a_shortcut(self):
        for phrase in [
            "does not lower the audit standard",
            "reduce the required claim count",
            "skip a routed module because it is inconvenient",
            "complete every routed module check",
            "Automatically switch to Full path",
            "three or more primary methodological modules",
            "Flash means less irrelevant context, not less work.",
        ]:
            self.assertIn(phrase, self.skill)
        self.assertIn("Escalate to Full path", self.router)
        self.assertIn("does not permit fewer claims", self.router)

    def test_domain_profiles_are_outside_skill_core(self):
        for heading in [
            "## Experimental natural science / materials / biochemistry",
            "## Machine learning / software / benchmark papers",
            "## Finance / econometrics / market microstructure",
            "## Clinical / biomedical empirical research",
            "## Quantitative social science / surveys",
            "## Empirical aesthetics / human-subject arts research",
        ]:
            self.assertIn(heading, self.domains)
        self.assertIn("references/domain-profiles.md", self.skill)

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
        self.assertGreaterEqual(len(FIXTURES), 24)
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture.name):
                errors = validate_audit.validate(fixture.read_text(encoding="utf-8"), self.allowed)
                self.assertEqual(errors, [])

    def test_cross_section_consistency_is_preserved_in_layered_refs(self):
        self.assertIn("Internal consistency", self.topology)
        self.assertIn("internal inconsistency", self.pollution)
        self.assertIn("Direct evidence wins over narrative summary", self.core)

    def test_validation_independence_is_preserved_in_layered_refs(self):
        self.assertIn("Validation independence", self.topology)
        self.assertIn("non-independent validation", self.pollution)
        self.assertIn("fitting target", self.topology)
        self.assertIn("Independent accuracy/generalization requires evidence", self.topology)

    def test_historical_topology_rules_are_explicit(self):
        for label in [
            "mechanical coupling",
            "null-result overreach",
            "proxy reification",
            "selection-conditioned evidence",
        ]:
            self.assertIn(label, self.pollution)

    def test_finance_medicine_and_empirical_arts_are_covered(self):
        self.assertIn("administrative or transactional record", self.allowed)
        self.assertIn("intervention", validate_audit.CLAIM_TYPES)
        self.assertIn("## Finance / econometrics / market microstructure", self.domains)
        self.assertIn("## Clinical / biomedical empirical research", self.domains)
        self.assertIn("## Empirical aesthetics / human-subject arts research", self.domains)
        self.assertIn("patient-specific", self.skill)

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
        self.assertIn("evidence dependence:", self.output)

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
        self.assertIn("evidence nodes:", self.output)

    def test_brain_beauty_fixture_exposes_evidence_reuse_across_claims(self):
        text = BEAUTY_FIXTURE.read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("- evidence nodes: E1 + E2"), 4)
        self.assertIn("- support level: sufficient", text)
        self.assertIn("- support level: partial", text)
        self.assertIn("- support level: insufficient", text)

    def test_claim_dependencies_and_uncertainty_propagation_are_explicit(self):
        self.assertIn("Uncertainty propagation", self.claim_dependencies_ref)
        self.assertIn("inference-chain laundering", self.claim_dependencies_ref)
        self.assertIn("upstream claims:", self.output)
        self.assertIn("inference-chain laundering", self.pollution)

    def test_validator_rejects_forward_claim_dependency(self):
        text = BEAUTY_FIXTURE.read_text(encoding="utf-8").replace(
            "- upstream claims: none", "- upstream claims: C2", 1
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("must reference earlier claims only" in error for error in errors), errors)

    def test_validator_propagates_uncertainty_without_new_evidence(self):
        text = BEAUTY_FIXTURE.read_text(encoding="utf-8").replace(
            "- support level: insufficient", "- support level: sufficient", 1
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("downstream claim cannot be sufficient" in error for error in errors), errors)

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
        self.assertIn("figure-and-table-traps.md", self.router)
        self.assertIn("visual impression overreach", self.pollution)

    def test_methodological_world_knowledge_is_modular_and_bounded(self):
        self.assertIn("Domain knowledge boundary", self.core)
        self.assertIn("Do not keep all optional references in context", self.router)
        for ref in [
            "statistical-traps.md",
            "measurement-traps.md",
            "study-design-traps.md",
        ]:
            self.assertIn(ref, self.skill)
            self.assertIn(ref, self.router)

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

    def test_measurement_reference_handles_threshold_coding_and_fit_error(self):
        self.assertIn("Thresholded or detectability outcomes", self.measurement_traps_ref)
        self.assertIn("reference category", self.measurement_traps_ref)
        self.assertIn("not independent validation", self.measurement_traps_ref)
        self.assertIn("fit error", self.measurement_traps_ref)

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
        self.assertIn("below detection", organic.lower())
        self.assertIn("benjamini-hochberg", organic.lower())
        self.assertIn("regression to the mean", before_after.lower())
        self.assertIn("concurrent control", before_after.lower())
        self.assertIn("train-test leakage", leakage.lower())
        self.assertIn("technical repeats", dic.lower())
        self.assertIn("independent fibrils", dic.lower())

    def test_false_positive_guards_are_explicit(self):
        for phrase in [
            "A trap cue is a question to investigate, not a verdict.",
            "Multiple subgroups are not automatically p-hacking",
            "Interim analyses are not automatically optional stopping",
            "Non-detects are not automatically unusable data",
            "Technical repeats are not automatically pseudo-replication",
            "Before-after is not automatically uncontrolled",
            "Silence rule",
        ]:
            self.assertIn(phrase, self.false_positive_guards_ref)
        self.assertIn("false-positive-guards.md", self.router)
        self.assertIn("Methodological risk is not a verdict", self.core)

    def test_anti_trigger_fixtures_credit_correct_mitigation(self):
        sprint = ANTI_SPRINT.read_text(encoding="utf-8")
        lod = ANTI_LOD.read_text(encoding="utf-8")
        did = ANTI_DID.read_text(encoding="utf-8")
        hierarchy = ANTI_HIERARCHY.read_text(encoding="utf-8")

        self.assertIn("Hommel-adjusted", sprint)
        self.assertIn("Lan-DeMets", sprint)
        self.assertIn("left-censored", lod)
        self.assertIn("5,000", lod)
        self.assertIn("matched comparator", did)
        self.assertIn("difference-in-differences", did.lower())
        self.assertIn("explicitly avoid the causal conclusion", did.lower())
        self.assertIn("mixed-effects", hierarchy.lower())
        self.assertIn("nested", hierarchy.lower())
        self.assertIn("Do not flag pseudo-replication", hierarchy)

    def test_validator_rejects_malformed_evidence_nodes(self):
        text = RESNET_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence nodes: E1", "- evidence nodes: Figure4", 1
        )
        errors = validate_audit.validate(text, self.allowed)
        self.assertTrue(any("invalid evidence nodes" in error for error in errors), errors)

    def test_validator_requires_two_nodes_for_convergence(self):
        text = BMD_REPLICATION_FIXTURE.read_text(encoding="utf-8").replace(
            "- evidence nodes: E1 + E2", "- evidence nodes: E1", 1
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
