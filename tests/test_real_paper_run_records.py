import copy
import hashlib
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
JUDGMENT_BASELINE = ROOT / "tests" / "real-paper-judgment-baseline.json"
JUDGMENT_BASELINE_SHA256 = "98d6b347b01b7732395e0f74183ff8ea18d325ccb98a52a42096f4e6e35b5a8e"
VIABILITY = {"auditable", "partially auditable", "non-auditable"}
SUPPORT_LEVELS = {"sufficient", "partial", "insufficient", "unclear"}
ONLY_TOLERATED_SUPPORT_PAIR = {"partial", "insufficient"}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = load_module("real_run_gate", SCRIPTS / "audit_gate.py")


def contract_errors(contract: dict) -> list[str]:
    errors = []
    if set(contract) != {"must_hold", "allowed_range"}:
        return ["contract must contain exactly must_hold and allowed_range"]

    must = contract["must_hold"]
    allowed = contract["allowed_range"]
    if set(must) != {"viability", "required_viability_flags"}:
        errors.append("must_hold keys are not exact")
    if set(allowed) != {"viability_flags", "support_levels"}:
        errors.append("allowed_range keys are not exact")
    if errors:
        return errors

    if must["viability"] not in VIABILITY:
        errors.append("invalid hard viability")
    required_flags = must["required_viability_flags"]
    allowed_flags = allowed["viability_flags"]
    if not isinstance(required_flags, list) or len(required_flags) != len(set(required_flags)):
        errors.append("required viability flags must be a unique list")
    if not isinstance(allowed_flags, list) or len(allowed_flags) != len(set(allowed_flags)):
        errors.append("allowed viability flags must be a unique list")
    if isinstance(required_flags, list) and isinstance(allowed_flags, list):
        if not set(required_flags).issubset(set(allowed_flags)):
            errors.append("required viability flags must be inside the allowed flag set")

    support_ranges = allowed["support_levels"]
    if not isinstance(support_ranges, list):
        errors.append("support level ranges must be a list")
        return errors
    if must["viability"] == "non-auditable" and support_ranges:
        errors.append("non-auditable contracts cannot allow claim support levels")

    for index, choices in enumerate(support_ranges, start=1):
        if not isinstance(choices, list) or not choices:
            errors.append(f"claim {index}: support range must be a non-empty list")
            continue
        if len(choices) != len(set(choices)):
            errors.append(f"claim {index}: duplicate support level in range")
        if not set(choices).issubset(SUPPORT_LEVELS):
            errors.append(f"claim {index}: unknown support level")
        if len(choices) > 2:
            errors.append(f"claim {index}: support tolerance is too broad")
        if len(choices) == 2 and set(choices) != ONLY_TOLERATED_SUPPORT_PAIR:
            errors.append(
                f"claim {index}: the only permitted two-level tolerance is partial/insufficient"
            )
    return errors


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
        cls.baseline_bytes = JUDGMENT_BASELINE.read_bytes()
        cls.baseline = json.loads(cls.baseline_bytes.decode("utf-8"))

    def test_legacy_fixture_index_is_honest_and_complete(self):
        legacy = json.loads(
            (RUN_ROOT / "legacy-fixture-index.json").read_text(encoding="utf-8")
        )
        self.assertEqual(legacy["status"], "legacy-fixtures")
        self.assertIn("not reconstructed", legacy["provenance_note"])
        self.assertGreaterEqual(len(legacy["fixtures"]), 24)
        for rel in legacy["fixtures"]:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_judgment_baseline_is_pinned_and_not_silently_widened(self):
        self.assertEqual(
            hashlib.sha256(self.baseline_bytes).hexdigest(),
            JUDGMENT_BASELINE_SHA256,
        )
        self.assertEqual(self.baseline["schema_version"], 1)

        baseline_rounds = self.baseline["rounds"]
        self.assertEqual(
            set(baseline_rounds),
            {manifest["round_id"] for _, manifest in self.rounds},
        )
        for round_root, manifest in self.rounds:
            round_id = manifest["round_id"]
            cases = manifest["cases"]
            self.assertTrue(cases, round_root)
            self.assertEqual(len({case["id"] for case in cases}), len(cases))
            self.assertEqual(
                set(baseline_rounds[round_id]),
                {case["id"] for case in cases},
            )
            for case in cases:
                contract = case["regression_contract"]
                self.assertEqual(
                    contract,
                    baseline_rounds[round_id][case["id"]],
                )
                self.assertEqual(contract_errors(contract), [])

    def test_judgment_tolerance_schema_rejects_easy_escape_hatches(self):
        base = {
            "must_hold": {
                "viability": "auditable",
                "required_viability_flags": [],
            },
            "allowed_range": {
                "viability_flags": [],
                "support_levels": [["partial", "insufficient"]],
            },
        }
        self.assertEqual(contract_errors(base), [])

        too_wide = copy.deepcopy(base)
        too_wide["allowed_range"]["support_levels"][0] = [
            "sufficient",
            "partial",
            "insufficient",
        ]
        self.assertTrue(contract_errors(too_wide))

        crosses_sufficient = copy.deepcopy(base)
        crosses_sufficient["allowed_range"]["support_levels"][0] = [
            "sufficient",
            "partial",
        ]
        self.assertTrue(contract_errors(crosses_sufficient))

        missing_required_flag = copy.deepcopy(base)
        missing_required_flag["must_hold"]["required_viability_flags"] = [
            "source-integrity-failure"
        ]
        self.assertTrue(contract_errors(missing_required_flag))

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
                    contract = case["regression_contract"]
                    must_hold = contract["must_hold"]
                    allowed_range = contract["allowed_range"]
                    self.assertEqual(
                        ledger["evidence_viability"],
                        must_hold["viability"],
                    )
                    actual_flags = set(ledger.get("viability_flags", []))
                    self.assertTrue(
                        set(must_hold["required_viability_flags"]).issubset(actual_flags)
                    )
                    self.assertTrue(
                        actual_flags.issubset(set(allowed_range["viability_flags"]))
                    )

                    actual_support = [
                        claim["support"]["support_level"]
                        for claim in ledger.get("claims", [])
                    ]
                    self.assertEqual(
                        len(actual_support),
                        len(allowed_range["support_levels"]),
                    )
                    for index, (actual, choices) in enumerate(
                        zip(actual_support, allowed_range["support_levels"]),
                        start=1,
                    ):
                        self.assertIn(
                            actual,
                            choices,
                            f"claim {index} support drifted outside its allowed judgment range",
                        )

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
