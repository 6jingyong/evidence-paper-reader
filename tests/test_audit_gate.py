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


def base_lexical(use_inventory=False):
    return {
        "suggested": [
            {"module": "statistical-traps.md", "cues": ["regression"]},
            {"module": "study-design-traps.md", "cues": ["randomized"]},
        ],
        "use_evidence_inventory": use_inventory,
    }


def base_semantic(use_inventory=False, audit=None):
    audit = audit or base_audit()
    claims = []
    for idx, ledger_claim in enumerate(audit["claims"], start=1):
        routes = {name: "not_required" for name in gate.merge_route.ROUTES}
        routes["statistical-traps.md"] = "required"
        routes["study-design-traps.md"] = "required"
        claims.append({
            "claim_id": f"C{idx}",
            "claim_text": ledger_claim["content"],
            "routes": routes,
            "inventory": "required" if use_inventory and idx == 1 else "not_required",
            "reason": "The claim depends on the stated design and statistical comparison.",
        })
    return {"claims": claims}


def merged_route(use_inventory=False):
    return gate.merge_route.merge(
        {"suggested": [], "use_evidence_inventory": False},
        base_semantic(use_inventory=use_inventory),
    )


class AuditGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence_types = EVIDENCE_TYPES.read_text(encoding="utf-8")
        cls.inventory = json.loads(INVENTORY_FIXTURE.read_text(encoding="utf-8"))

    def validate(
        self,
        audit=None,
        *,
        semantic=None,
        lexical=None,
        router_text=None,
        route=None,
        inventory=None,
    ):
        return gate.validate_gate(
            audit or base_audit(),
            semantic=semantic,
            lexical=lexical,
            route=route,
            inventory=inventory,
            evidence_types_text=self.evidence_types,
            router_text=router_text,
        )

    def test_simple_audit_passes_with_raw_routes_and_cached_merge(self):
        errors = self.validate(
            semantic=base_semantic(),
            route=merged_route(),
        )
        self.assertEqual(errors, [])

    def test_cached_merged_route_cannot_replace_semantic_routing(self):
        errors = self.validate(
            semantic=None,
            route=merged_route(),
        )
        self.assertTrue(any("requires the raw semantic-route artifact" in x for x in errors), errors)
        self.assertTrue(any("cannot substitute for raw semantic routing" in x for x in errors), errors)

    def test_cached_merged_route_must_match_recomputation(self):
        route = merged_route()
        route["modules"] = list(route["modules"]) + ["measurement-traps.md"]
        route["primary_module_count"] += 1
        route["recommended_path"] = "full"
        errors = self.validate(
            semantic=base_semantic(),
            route=route,
        )
        self.assertTrue(any("does not match deterministic recomputation" in x for x in errors), errors)

    def test_semantic_claim_ids_must_match_final_ledger(self):
        semantic = base_semantic()
        semantic["claims"][1]["claim_id"] = "C9"
        errors = self.validate(
            semantic=semantic,
        )
        self.assertTrue(any("claim IDs must exactly match" in x for x in errors), errors)

    def test_unclear_semantic_decision_requires_lexical_artifact(self):
        semantic = base_semantic()
        semantic["claims"][0]["routes"]["measurement-traps.md"] = "unclear"
        errors = self.validate(
            semantic=semantic,
        )
        self.assertTrue(any("contain unclear but no router-text" in x for x in errors), errors)

    def test_unclear_semantic_decision_uses_recomputed_lexical_route(self):
        semantic = base_semantic()
        semantic["claims"][0]["routes"]["measurement-traps.md"] = "unclear"
        errors = self.validate(
            semantic=semantic,
            router_text="The sensor calibration was checked before analysis.",
        )
        self.assertEqual(errors, [])

    def test_cached_lexical_route_cannot_substitute_for_router_text(self):
        errors = self.validate(
            semantic=base_semantic(),
            lexical=base_lexical(),
        )
        self.assertTrue(any("cached lexical route cannot substitute" in x for x in errors), errors)

    def test_cached_lexical_route_must_match_recomputation(self):
        errors = self.validate(
            semantic=base_semantic(),
            lexical=base_lexical(),
            router_text="A randomized trial reports a hazard ratio.",
        )
        self.assertTrue(any("cached lexical route does not match" in x for x in errors), errors)

    def test_claim_change_after_routing_requires_reroute(self):
        audit = base_audit()
        semantic = base_semantic(audit=audit)
        audit["claims"][1]["content"] = "A changed claim that was not routed."
        errors = self.validate(
            audit,
            semantic=semantic,
        )
        self.assertTrue(any("claim text/order must exactly match" in x for x in errors), errors)

    def test_route_required_inventory_cannot_be_skipped(self):
        errors = self.validate(
            semantic=base_semantic(use_inventory=True),
            inventory=None,
        )
        self.assertTrue(any("requires evidence inventory" in x for x in errors), errors)

    def test_inventory_cannot_bypass_recomputed_route(self):
        errors = self.validate(
            semantic=base_semantic(),
            inventory=self.inventory,
        )
        self.assertTrue(any("conflicts with recomputed route" in x for x in errors), errors)

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

        semantic = base_semantic(use_inventory=True, audit=audit)
        errors = self.validate(
            audit,
            semantic=semantic,
            inventory=self.inventory,
        )
        self.assertTrue(any("claim contents/order drifted" in x for x in errors), errors)

    def test_final_gate_rejects_unknown_evidence_label(self):
        audit = base_audit()
        audit["claims"][0]["support"]["evidence_type"] = ["imaginary evidence"]
        errors = self.validate(
            audit,
            semantic=base_semantic(),
        )
        self.assertTrue(any("unknown evidence label" in x for x in errors), errors)


if __name__ == "__main__":
    unittest.main()
