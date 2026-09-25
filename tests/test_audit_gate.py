import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPT = SKILL / "scripts" / "audit_gate.py"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"
INVENTORY_FIXTURE = ROOT / "tests" / "inventory-fixtures" / "synthetic-duplicate-and-replication-inventory.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = load_module("audit_gate", SCRIPT)


def base_audit():
    return {
        "scope_status": "in scope",
        "evidence_viability": "auditable",
        "viability_flags": [],
        "paper_type": "randomized controlled trial",
        "reader_conclusion": "The bounded primary result is supported.",
        "claims": [
            {
                "content": "Claim one is supported in the tested population.",
                "claim_type": "intervention",
                "conclusion_strength": "medium",
                "support": {
                    "evidence_type": ["direct experiment"],
                    "evidence_provenance": "paper-local",
                    "evidence_nodes": ["E1"],
                    "upstream_claims": [],
                    "evidence_dependence": "single-source",
                    "source_location": "Results; Table 1",
                    "support_level": "sufficient",
                    "reason": "The randomized comparison directly tests the bounded claim.",
                    "external_dependency": "none",
                },
            },
            {
                "content": "Claim two is supported in the tested population.",
                "claim_type": "observational",
                "conclusion_strength": "weak",
                "support": {
                    "evidence_type": ["statistical analysis"],
                    "evidence_provenance": "paper-local",
                    "evidence_nodes": ["E2"],
                    "upstream_claims": [],
                    "evidence_dependence": "single-source",
                    "source_location": "Results; Table 2",
                    "support_level": "sufficient",
                    "reason": "The reported analysis directly supports the bounded claim.",
                    "external_dependency": "none",
                },
            },
            {
                "content": "Claim three remains bounded to the study context.",
                "claim_type": "generality",
                "conclusion_strength": "medium",
                "support": {
                    "evidence_type": ["direct experiment"],
                    "evidence_provenance": "paper-local",
                    "evidence_nodes": ["E3"],
                    "upstream_claims": [1],
                    "evidence_dependence": "single-source",
                    "source_location": "Discussion",
                    "support_level": "partial",
                    "reason": "The study supports the local effect but not broad transfer.",
                    "external_dependency": "none",
                },
            },
        ],
        "usable": {
            "results": "The primary bounded comparison is usable.",
            "methods_or_design": "The randomized design is reusable.",
            "materials_or_documentation": "Key estimates and group definitions are reported.",
        },
        "downweight": {
            "worth_noticing": "Broad transfer remains uncertain.",
            "cautious_or_ignore": "Do not extend the result beyond the tested setting without evidence.",
        },
        "value_breakdown": {
            "result": "high",
            "method": "high",
            "theory_or_insight": "medium",
            "research_design": "high",
            "material_or_documentation": "high",
        },
        "uncertainty_and_follow_up": "External validity remains uncertain.",
    }


def base_route(use_inventory=False):
    return {
        "modules": [
            "statistical-traps.md",
            "study-design-traps.md",
            "false-positive-guards.md",
        ],
        "use_evidence_inventory": use_inventory,
        "inventory_basis": "semantic required" if use_inventory else "semantic not required",
        "recommended_path": "flash",
        "primary_module_count": 2,
        "route_details": {},
        "lexical_only_modules_removed": [],
        "semantic_modules_added": [],
    }


class AuditGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence_types = EVIDENCE_TYPES.read_text(encoding="utf-8")
        cls.inventory = json.loads(INVENTORY_FIXTURE.read_text(encoding="utf-8"))

    def test_simple_audit_passes_with_merged_route(self):
        errors = gate.validate_gate(
            base_audit(),
            route=base_route(),
            inventory=None,
            evidence_types_text=self.evidence_types,
        )
        self.assertEqual(errors, [])

    def test_claim_audit_requires_route(self):
        errors = gate.validate_gate(
            base_audit(),
            route=None,
            inventory=None,
            evidence_types_text=self.evidence_types,
        )
        self.assertTrue(any("requires a merged route" in x for x in errors), errors)

    def test_route_required_inventory_cannot_be_skipped(self):
        errors = gate.validate_gate(
            base_audit(),
            route=base_route(use_inventory=True),
            inventory=None,
            evidence_types_text=self.evidence_types,
        )
        self.assertTrue(any("requires evidence inventory" in x for x in errors), errors)

    def test_inventory_cannot_bypass_route_decision(self):
        errors = gate.validate_gate(
            base_audit(),
            route=base_route(use_inventory=False),
            inventory=self.inventory,
            evidence_types_text=self.evidence_types,
        )
        self.assertTrue(any("conflicts with merged route" in x for x in errors), errors)

    def test_inventory_claim_drift_is_rejected(self):
        audit = base_audit()
        audit["claims"] = []
        for idx, item in enumerate(self.inventory["claims"], start=1):
            audit["claims"].append({
                "content": item["content"],
                "claim_type": "observational",
                "conclusion_strength": "weak",
                "support": {
                    "evidence_type": ["direct experiment"],
                    "evidence_provenance": "paper-local",
                    "evidence_nodes": [f"E{idx}"],
                    "upstream_claims": [],
                    "evidence_dependence": "single-source",
                    "source_location": "Results",
                    "support_level": "sufficient",
                    "reason": "Paper-local result.",
                    "external_dependency": "none",
                },
            })
        audit["claims"][1]["content"] = "A rewritten claim that was not inventoried."

        route = base_route(use_inventory=True)
        errors = gate.validate_gate(
            audit,
            route=route,
            inventory=self.inventory,
            evidence_types_text=self.evidence_types,
        )
        self.assertTrue(any("claim contents/order drifted" in x for x in errors), errors)

    def test_route_guard_and_path_are_machine_checked(self):
        route = base_route()
        route["modules"].remove("false-positive-guards.md")
        route["recommended_path"] = "full"
        errors = gate.validate_gate(
            base_audit(),
            route=route,
            inventory=None,
            evidence_types_text=self.evidence_types,
        )
        self.assertTrue(any("must include false-positive-guards" in x for x in errors), errors)
        self.assertTrue(any("recommended_path" in x for x in errors), errors)

    def test_final_gate_rejects_unknown_evidence_label(self):
        audit = base_audit()
        audit["claims"][0]["support"]["evidence_type"] = ["imaginary evidence"]
        errors = gate.validate_gate(
            audit,
            route=base_route(),
            inventory=None,
            evidence_types_text=self.evidence_types,
        )
        self.assertTrue(any("unknown evidence label" in x for x in errors), errors)


if __name__ == "__main__":
    unittest.main()
