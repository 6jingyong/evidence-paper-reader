import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPTS = SKILL / "scripts"
RUN_ROOT = ROOT / "validation-runs" / "real-papers"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


render = load_module("relation_render", SCRIPTS / "render_audit.py")
gate = load_module("relation_gate", SCRIPTS / "audit_gate.py")


def valid_v3():
    data = copy.deepcopy(render.TEMPLATE)
    data["paper_type"] = "controlled empirical study"
    data["reader_conclusion"] = "The audit keeps evidence direction separate from inferential reach."
    for index, claim in enumerate(data["claims"], start=1):
        claim["content"] = f"Bounded claim {index}."
        claim["support"]["evidence_type"] = ["direct experiment"]
        claim["support"]["source_location"] = f"Results {index}"
        claim["support"]["support_level"] = "sufficient"
        claim["support"]["reason"] = "The bounded result supports the bounded claim."
        claim["support"]["evidence_relations"][0]["reason"] = (
            "The evidence node bears in favor of the bounded claim."
        )
    data["usable"] = {
        "results": "The bounded results are usable.",
        "methods_or_design": "The design is inspectable.",
        "materials_or_documentation": "The result locations are documented.",
    }
    data["downweight"] = {
        "worth_noticing": "Some external transfer remains open.",
        "cautious_or_ignore": "Do not add broader reach without evidence.",
    }
    data["value_breakdown"] = {
        "result": "high",
        "method": "medium",
        "theory_or_insight": "medium",
        "research_design": "medium",
        "material_or_documentation": "high",
    }
    data["uncertainty_and_follow_up"] = "External transfer remains open."
    return data


class EvidenceRelationTests(unittest.TestCase):
    def test_v3_valid_relations_pass_renderer_and_independent_guard(self):
        data = valid_v3()
        self.assertEqual(render.validate_ledger(data), [])
        self.assertEqual(gate.validate_evidence_relation_closure(data), [])
        rendered = render.render(data)
        self.assertIn("- evidence relations: E1=supports", rendered)

    def test_v2_remains_valid_without_evidence_relations(self):
        data = valid_v3()
        data["ledger_schema_version"] = 2
        for claim in data["claims"]:
            claim["support"].pop("evidence_relations")
        self.assertEqual(render.validate_ledger(data), [])
        self.assertEqual(gate.validate_evidence_relation_closure(data), [])

    def test_v3_requires_exact_relation_coverage(self):
        data = valid_v3()
        data["claims"][0]["support"]["evidence_relations"] = []
        renderer_errors = render.validate_ledger(data)
        guard_errors = gate.validate_evidence_relation_closure(data)
        self.assertTrue(
            any("must cover exactly the claim evidence_nodes" in e for e in renderer_errors),
            renderer_errors,
        )
        self.assertTrue(
            any("do not exactly cover claim evidence_nodes" in e for e in guard_errors),
            guard_errors,
        )

    def test_relation_cannot_invent_evidence_node(self):
        data = valid_v3()
        data["claims"][0]["support"]["evidence_relations"][0]["evidence_node"] = "E999"
        self.assertTrue(render.validate_ledger(data))
        self.assertTrue(gate.validate_evidence_relation_closure(data))

    def test_relation_nodes_cannot_duplicate(self):
        data = valid_v3()
        support = data["claims"][0]["support"]
        support["evidence_nodes"] = ["E1", "E2"]
        support["evidence_relations"] = [
            {
                "evidence_node": "E1",
                "relation": "supports",
                "reason": "First relation.",
            },
            {
                "evidence_node": "E1",
                "relation": "contextual",
                "reason": "Duplicate relation.",
            },
        ]
        renderer_errors = render.validate_ledger(data)
        guard_errors = gate.validate_evidence_relation_closure(data)
        self.assertTrue(any("duplicate evidence relation node" in e for e in renderer_errors))
        self.assertTrue(any("contain duplicates" in e for e in guard_errors))

    def test_relation_label_is_not_mechanical_support_level(self):
        data = valid_v3()
        relation = data["claims"][0]["support"]["evidence_relations"][0]
        relation["relation"] = "undermines"
        relation["reason"] = (
            "This node counts against one component, while the full disclosed chain can still support the bounded claim."
        )
        # Relation direction is recorded, but support remains a separate whole-chain judgment.
        self.assertEqual(render.validate_ledger(data), [])
        self.assertEqual(gate.validate_evidence_relation_closure(data), [])

    def test_real_cases_preserve_claim_local_relation_changes(self):
        gautret = json.loads(
            (
                RUN_ROOT
                / "2026-09-26-round-02"
                / "gautret-hcq-2020"
                / "ledger.json"
            ).read_text(encoding="utf-8")
        )
        c1 = {
            item["evidence_node"]: item["relation"]
            for item in gautret["claims"][0]["support"]["evidence_relations"]
        }
        c3 = {
            item["evidence_node"]: item["relation"]
            for item in gautret["claims"][2]["support"]["evidence_relations"]
        }
        self.assertEqual(c1["E3"], "contextual")
        self.assertEqual(c3["E3"], "undermines")

        echinacea = json.loads(
            (
                RUN_ROOT
                / "2026-09-26-round-01"
                / "echinacea-2010"
                / "ledger.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            {
                item["relation"]
                for item in echinacea["claims"][2]["support"]["evidence_relations"]
            },
            {"mixed"},
        )

        chocolate = json.loads(
            (
                RUN_ROOT
                / "2026-09-26-round-02"
                / "chocolate-weight-loss-2015"
                / "ledger.json"
            ).read_text(encoding="utf-8")
        )
        c3_chocolate = {
            item["evidence_node"]: item["relation"]
            for item in chocolate["claims"][2]["support"]["evidence_relations"]
        }
        self.assertEqual(c3_chocolate["E1"], "undermines")

    def test_all_source_backed_ledgers_are_v3_relation_closed(self):
        count = 0
        for round_root in sorted(RUN_ROOT.glob("*-round-*")):
            manifest = json.loads(
                (round_root / "manifest.json").read_text(encoding="utf-8")
            )
            for case in manifest["cases"]:
                data = json.loads(
                    (round_root / case["id"] / "ledger.json").read_text(encoding="utf-8")
                )
                count += 1
                with self.subTest(case=case["id"]):
                    self.assertEqual(data.get("ledger_schema_version"), 3)
                    self.assertEqual(render.validate_ledger(data), [])
                    self.assertEqual(gate.validate_evidence_relation_closure(data), [])
                    if data["evidence_viability"] == "non-auditable":
                        self.assertEqual(data.get("claims"), [])
                    else:
                        for claim in data["claims"]:
                            self.assertTrue(claim["support"].get("evidence_relations"))
        self.assertGreaterEqual(count, 10)


if __name__ == "__main__":
    unittest.main()
