import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
GATE_SCRIPT = SKILL / "scripts" / "audit_gate.py"
MATRIX = ROOT / "tests" / "sabotage-matrix.json"
INVENTORY_FIXTURE = (
    ROOT / "tests" / "inventory-fixtures" / "synthetic-duplicate-and-replication-inventory.json"
)
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = load_module("sabotage_audit_gate", GATE_SCRIPT)


def simple_audit():
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


def inventory_audit(inventory: dict):
    audit = simple_audit()
    audit["reader_conclusion"] = "The inventory exposes one main result, one secondary result, and one replication result."
    audit["claims"] = []
    for index, item in enumerate(inventory["claims"], start=1):
        audit["claims"].append({
            "content": item["content"],
            "claim_type": "observational",
            "conclusion_strength": "weak",
            "support": {
                "evidence_type": ["direct experiment"],
                "evidence_provenance": "paper-local",
                "evidence_nodes": [f"E{index}"],
                "upstream_claims": [],
                "evidence_dependence": "single-source",
                "source_location": "Results",
                "support_level": "sufficient",
                "reason": "The promoted paper-local result directly supports the bounded claim.",
                "external_dependency": "none",
            },
        })
    return audit


def semantic_for(audit: dict, *, inventory_required=False):
    claims = []
    for index, claim in enumerate(audit["claims"], start=1):
        routes = {name: "not_required" for name in gate.merge_route.ROUTES}
        routes["statistical-traps.md"] = "required"
        routes["study-design-traps.md"] = "required"
        claims.append({
            "claim_id": f"C{index}",
            "claim_text": claim["content"],
            "routes": routes,
            "inventory": "required" if inventory_required and index == 1 else "not_required",
            "reason": "The claim requires the stated design and statistical checks.",
        })
    return {"claims": claims}


def pristine_workflow(kind: str, inventory_fixture: dict) -> dict:
    inventory = None
    router_text = None
    lexical = None

    if kind == "inventory":
        inventory = copy.deepcopy(inventory_fixture)
        audit = inventory_audit(inventory)
        semantic = semantic_for(audit, inventory_required=True)
    else:
        audit = simple_audit()
        semantic = semantic_for(audit)

    if kind == "lexical":
        router_text = "A randomized trial reports a hazard ratio for the primary outcome."
        lexical = gate.build_context.suggest_modules.suggest_modules(router_text)

    route = gate.build_context.recompute_route(semantic, lexical, router_text)
    context = gate.build_context.render_bundle(route)
    return {
        "audit": audit,
        "semantic": semantic,
        "lexical": lexical,
        "router_text": router_text,
        "route": route,
        "context": context,
        "inventory": inventory,
    }


def _parent_and_key(root, path):
    current = root
    for part in path[:-1]:
        current = current[part]
    return current, path[-1]


def apply_mutation(value, mutation: dict):
    op = mutation["op"]
    if op == "append_text":
        return value + mutation["value"]
    if op == "replace_text":
        old = mutation["old"]
        if old not in value:
            raise AssertionError(f"mutation anchor missing: {old}")
        return value.replace(old, mutation["value"], 1)

    parent, key = _parent_and_key(value, mutation["path"])
    if op == "set":
        parent[key] = copy.deepcopy(mutation["value"])
    elif op == "delete":
        del parent[key]
    elif op == "toggle":
        parent[key] = not parent[key]
    elif op == "append":
        parent[key].append(copy.deepcopy(mutation["value"]))
    elif op == "remove_value":
        parent[key].remove(mutation["value"])
    elif op == "delete_index":
        del parent[key][mutation["index"]]
    else:
        raise AssertionError(f"unknown sabotage op: {op}")
    return value


class FailClosedSabotageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.inventory_fixture = json.loads(INVENTORY_FIXTURE.read_text(encoding="utf-8"))
        cls.evidence_types = EVIDENCE_TYPES.read_text(encoding="utf-8")

    def validate(self, artifacts: dict) -> list[str]:
        return gate.validate_gate(
            artifacts["audit"],
            semantic=artifacts["semantic"],
            lexical=artifacts["lexical"],
            router_text=artifacts["router_text"],
            route=artifacts["route"],
            inventory=artifacts["inventory"],
            context_bundle=artifacts["context"],
            evidence_types_text=self.evidence_types,
        )

    def test_matrix_has_required_attack_surface_coverage(self):
        cases = self.matrix["cases"]
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        covered = {case["layer"] for case in cases}
        self.assertEqual(covered, set(self.matrix["required_layers"]))
        self.assertGreaterEqual(len(cases), 12)

    def test_all_pristine_workflows_pass(self):
        for kind in ["simple", "lexical", "inventory"]:
            with self.subTest(kind=kind):
                self.assertEqual(
                    self.validate(pristine_workflow(kind, self.inventory_fixture)),
                    [],
                )

    def test_every_declared_sabotage_is_rejected_by_final_gate(self):
        for case in self.matrix["cases"]:
            with self.subTest(case=case["id"], layer=case["layer"]):
                artifacts = pristine_workflow(case["baseline"], self.inventory_fixture)
                target = case["target"]
                artifacts[target] = apply_mutation(
                    artifacts[target],
                    case,
                )
                for extra in case.get("also", []):
                    artifacts[target] = apply_mutation(
                        artifacts[target],
                        extra,
                    )

                errors = self.validate(artifacts)
                self.assertTrue(errors, f"{case['id']} escaped the final gate")
                self.assertTrue(
                    any(case["expect"] in error for error in errors),
                    f"{case['id']} failed, but not at its intended invariant: {errors}",
                )


if __name__ == "__main__":
    unittest.main()
