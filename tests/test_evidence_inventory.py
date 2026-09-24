import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPT = SKILL / "scripts" / "evidence_inventory.py"
ROUTER_SCRIPT = SKILL / "scripts" / "suggest_modules.py"
FIXTURE = ROOT / "tests" / "inventory-fixtures" / "synthetic-duplicate-and-replication-inventory.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


inventory = load_module("evidence_inventory", SCRIPT)
router = load_module("inventory_router", ROUTER_SCRIPT)


class EvidenceInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_validates_and_compacts(self):
        self.assertEqual(inventory.validate_inventory(self.fixture), [])
        compact = inventory.compact_summary(self.fixture)
        self.assertIn("E1 <- R1 + R2 [G1; units=U1]", compact)
        self.assertIn("E2 <- R3 [G2; units=U1]", compact)
        self.assertIn("E3 <- R4 [G3; units=U2]", compact)

    def test_same_result_cannot_be_split_into_multiple_e_nodes(self):
        data = copy.deepcopy(self.fixture)
        data["promotions"].append({
            "evidence_node": "E4",
            "record_ids": ["R2"],
            "reason": "Incorrect duplicate promotion.",
        })
        data["promotions"][0]["record_ids"] = ["R1"]
        errors = inventory.validate_inventory(data)
        self.assertTrue(any("result key G1 is promoted into multiple evidence nodes" in e for e in errors), errors)

    def test_one_e_node_cannot_merge_different_results(self):
        data = copy.deepcopy(self.fixture)
        data["promotions"][0]["record_ids"] = ["R1", "R3"]
        errors = inventory.validate_inventory(data)
        self.assertTrue(any("cannot merge different result keys" in e for e in errors), errors)

    def test_same_record_cannot_be_promoted_twice(self):
        data = copy.deepcopy(self.fixture)
        data["promotions"].append({
            "evidence_node": "E4",
            "record_ids": ["R4"],
            "reason": "Incorrect duplicate record promotion.",
        })
        errors = inventory.validate_inventory(data)
        self.assertTrue(any("R4 is promoted into more than one evidence node" in e for e in errors), errors)

    def test_every_claim_must_have_promoted_evidence_or_explicit_gap(self):
        data = copy.deepcopy(self.fixture)
        data["promotions"] = [p for p in data["promotions"] if p["evidence_node"] != "E3"]
        errors = inventory.validate_inventory(data)
        self.assertTrue(any("C3: claim has neither promoted evidence nor an unresolved_claims entry" in e for e in errors), errors)

        data["unresolved_claims"] = [{
            "claim_id": "C3",
            "reason": "Replication subsection is missing from the supplied copy.",
        }]
        self.assertEqual(inventory.validate_inventory(data), [])

    def test_unresolved_claim_cannot_also_have_promoted_evidence(self):
        data = copy.deepcopy(self.fixture)
        data["unresolved_claims"] = [{
            "claim_id": "C1",
            "reason": "Incorrectly marked unresolved.",
        }]
        errors = inventory.validate_inventory(data)
        self.assertTrue(any("both promoted and unresolved" in e for e in errors), errors)

    def test_independent_convergence_cannot_share_u_key(self):
        audit = {
            "claims": [
                {
                    "support": {
                        "evidence_nodes": ["E1", "E2"],
                        "evidence_dependence": "independent convergence",
                    }
                }
            ]
        }
        errors = inventory.check_audit_alignment(self.fixture, audit)
        self.assertTrue(any("shares evidence unit(s): U1" in e for e in errors), errors)

    def test_independent_convergence_accepts_distinct_known_units(self):
        audit = {
            "claims": [
                {
                    "support": {
                        "evidence_nodes": ["E1", "E3"],
                        "evidence_dependence": "independent convergence",
                    }
                }
            ]
        }
        self.assertEqual(inventory.check_audit_alignment(self.fixture, audit), [])

    def test_router_recommends_inventory_for_complex_text_not_simple_text(self):
        simple = router.suggest_modules(
            "Randomized trial reporting a hazard ratio for one primary outcome."
        )
        self.assertFalse(simple["use_evidence_inventory"])

        complex_text = (
            ("Figure 1 Table 1 Figure 2 Table 2 Figure 3 Table 3 "
             "Figure 4 Table 4 Figure 5 Table 5 ")
            + " independent cohort replication cohort multiple datasets external validation "
            + " supplement supporting information "
            + ("results " * 6000)
        )
        complex_result = router.suggest_modules(complex_text)
        self.assertTrue(complex_result["use_evidence_inventory"])
        self.assertEqual(complex_result["inventory_with"], "evidence_inventory.py")
        self.assertTrue(complex_result["inventory_reasons"])


if __name__ == "__main__":
    unittest.main()
