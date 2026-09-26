import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPTS = SKILL / "scripts"
RUN_ROOT = ROOT / "validation-runs" / "real-papers"
ROUNDS = sorted(path for path in RUN_ROOT.glob("*-round-*") if path.is_dir())
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
        cls.rounds = [
            (
                round_root,
                json.loads((round_root / "manifest.json").read_text(encoding="utf-8")),
            )
            for round_root in ROUNDS
        ]
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

    def test_round_manifests_are_nonempty_and_unique(self):
        self.assertGreaterEqual(len(self.rounds), 2)
        round_ids = [manifest["round_id"] for _, manifest in self.rounds]
        self.assertEqual(len(round_ids), len(set(round_ids)))
        for round_root, manifest in self.rounds:
            cases = manifest["cases"]
            self.assertTrue(cases, round_root)
            self.assertEqual(len({case["id"] for case in cases}), len(cases))

    def test_every_real_paper_record_replays_through_final_gate(self):
        full_paths = 0
        inventory_paths = 0
        non_auditable = 0
        for round_root, manifest in self.rounds:
            for case in manifest["cases"]:
                with self.subTest(round_id=manifest["round_id"], case=case["id"]):
                    root = round_root / case["id"]
                    source = json.loads(
                        (root / "source.json").read_text(encoding="utf-8")
                    )
                    ledger = json.loads(
                        (root / "ledger.json").read_text(encoding="utf-8")
                    )
                    result = json.loads(
                        (root / "result.json").read_text(encoding="utf-8")
                    )

                    self.assertEqual(source["record_id"], case["id"])
                    self.assertTrue(source["title"].strip())
                    self.assertTrue(source["stable_id"].strip())
                    self.assertTrue(source["source_url"].startswith("https://"))
                    self.assertEqual(result["expected_gate"], "pass")
                    self.assertEqual(result["reviewer"], manifest["reviewer"])

                    inventory_path = root / "inventory.json"
                    inventory = (
                        json.loads(inventory_path.read_text(encoding="utf-8"))
                        if inventory_path.is_file()
                        else None
                    )
                    self.assertEqual(
                        inventory is not None,
                        case["inventory_expected"],
                    )

                    no_claim_audit = (
                        ledger.get("scope_status") == "out of scope"
                        or ledger.get("evidence_viability") == "non-auditable"
                    )
                    if no_claim_audit:
                        non_auditable += 1
                        self.assertFalse((root / "semantic-route.json").exists())
                        self.assertFalse((root / "module-checks.json").exists())
                        self.assertIsNone(inventory)
                        errors = gate.validate_gate(
                            ledger,
                            semantic=None,
                            lexical=None,
                            router_text=None,
                            route=None,
                            inventory=None,
                            context_bundle=None,
                            module_checks=None,
                            evidence_types_text=self.evidence_types,
                        )
                        self.assertEqual(errors, [], errors)
                        continue

                    semantic = json.loads(
                        (root / "semantic-route.json").read_text(encoding="utf-8")
                    )
                    checks = json.loads(
                        (root / "module-checks.json").read_text(encoding="utf-8")
                    )
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

                    self.assertEqual(
                        [item["claim_text"] for item in semantic["claims"]],
                        [claim["content"] for claim in ledger["claims"]],
                    )

        self.assertGreaterEqual(full_paths, 2)
        self.assertGreaterEqual(inventory_paths, 1)
        self.assertGreaterEqual(non_auditable, 1)


if __name__ == "__main__":
    unittest.main()
