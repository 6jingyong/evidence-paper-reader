import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPTS = SKILL / "scripts"
RUN_ROOT = ROOT / "validation-runs" / "real-papers"
ROUND = RUN_ROOT / "2026-09-26-round-01"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = load_module("real_run_gate", SCRIPTS / "audit_gate.py")


class RealPaperRunRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (ROUND / "manifest.json").read_text(encoding="utf-8")
        )
        cls.evidence_types = EVIDENCE_TYPES.read_text(encoding="utf-8")

    def test_legacy_fixture_index_is_honest_and_complete(self):
        legacy = json.loads(
            (RUN_ROOT / "legacy-fixture-index.json").read_text(encoding="utf-8")
        )
        self.assertEqual(legacy["status"], "legacy-fixtures")
        self.assertIn("not reconstructed", legacy["provenance_note"])
        self.assertGreaterEqual(len(legacy["fixtures"]), 24)
        for rel in legacy["fixtures"]:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_round_has_cross_domain_inventory_coverage(self):
        cases = self.manifest["cases"]
        self.assertEqual(len(cases), 5)
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        self.assertGreaterEqual(len({case["domain"] for case in cases}), 5)
        self.assertTrue(any(case["inventory_expected"] for case in cases))
        self.assertTrue(any(not case["inventory_expected"] for case in cases))

    def test_every_real_paper_record_replays_through_final_gate(self):
        full_paths = 0
        inventory_paths = 0
        for case in self.manifest["cases"]:
            with self.subTest(case=case["id"]):
                root = ROUND / case["id"]
                source = json.loads((root / "source.json").read_text(encoding="utf-8"))
                ledger = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
                semantic = json.loads((root / "semantic-route.json").read_text(encoding="utf-8"))
                checks = json.loads((root / "module-checks.json").read_text(encoding="utf-8"))
                result = json.loads((root / "result.json").read_text(encoding="utf-8"))

                self.assertEqual(source["record_id"], case["id"])
                self.assertTrue(source["title"].strip())
                self.assertTrue(source["stable_id"].strip())
                self.assertTrue(source["source_url"].startswith("https://"))
                self.assertEqual(result["expected_gate"], "pass")
                self.assertEqual(result["reviewer"], self.manifest["reviewer"])

                inventory_path = root / "inventory.json"
                inventory = (
                    json.loads(inventory_path.read_text(encoding="utf-8"))
                    if inventory_path.is_file()
                    else None
                )
                self.assertEqual(inventory is not None, case["inventory_expected"])

                route = gate.build_context.recompute_route(
                    semantic,
                    lexical=None,
                    router_text=None,
                )
                if route["recommended_path"] == "full":
                    full_paths += 1
                if route["use_evidence_inventory"]:
                    inventory_paths += 1

                context = gate.build_context.render_bundle(route)
                errors = gate.validate_gate(
                    ledger,
                    semantic=semantic,
                    lexical=None,
                    router_text=None,
                    route=None,
                    inventory=inventory,
                    context_bundle=context,
                    module_checks=checks,
                    evidence_types_text=self.evidence_types,
                )
                self.assertEqual(errors, [], errors)

                expected_claims = [
                    item["claim_text"] for item in semantic["claims"]
                ]
                self.assertEqual(
                    expected_claims,
                    [claim["content"] for claim in ledger["claims"]],
                )

        self.assertGreaterEqual(full_paths, 2)
        self.assertGreaterEqual(inventory_paths, 1)


if __name__ == "__main__":
    unittest.main()
