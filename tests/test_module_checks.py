import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
MODULE_CHECKS = SKILL / "scripts" / "module_checks.py"
MERGE_ROUTE = SKILL / "scripts" / "merge_route.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


checks_mod = load_module("module_checks_contract", MODULE_CHECKS)
merge_mod = load_module("module_checks_merge", MERGE_ROUTE)


def route_fixture():
    routes1 = {name: "not_required" for name in merge_mod.ROUTES}
    routes1["statistical-traps.md"] = "required"
    routes1["study-design-traps.md"] = "required"

    routes2 = {name: "not_required" for name in merge_mod.ROUTES}
    routes2["evidence-dependence.md"] = "required"

    semantic = {
        "claims": [
            {
                "claim_id": "C1",
                "claim_text": "Claim one.",
                "routes": routes1,
                "inventory": "not_required",
                "reason": "C1 requires statistical and design checks.",
            },
            {
                "claim_id": "C2",
                "claim_text": "Claim two.",
                "routes": routes2,
                "inventory": "not_required",
                "reason": "C2 combines multiple evidence units.",
            },
        ]
    }
    return merge_mod.merge(
        {"suggested": [], "use_evidence_inventory": False},
        semantic,
    )


def completed(route):
    data = checks_mod.template(route)
    for claim in data["claims"]:
        for check in claim["checks"]:
            check["status"] = "clear"
            check["source_locations"] = ["Results; Methods"]
            check["reason"] = "Completed against the routed reference."
            if "mitigation_checked" in check:
                check["mitigation_checked"] = True
    return data


class ModuleChecksTests(unittest.TestCase):
    def test_template_is_exactly_claim_scoped(self):
        route = route_fixture()
        data = checks_mod.template(route)
        self.assertEqual(
            [x["claim_id"] for x in data["claims"]],
            ["C1", "C2"],
        )
        self.assertEqual(
            [x["module"] for x in data["claims"][0]["checks"]],
            ["statistical-traps.md", "study-design-traps.md"],
        )
        self.assertEqual(
            [x["module"] for x in data["claims"][1]["checks"]],
            ["evidence-dependence.md"],
        )

    def test_completed_checks_validate(self):
        route = route_fixture()
        self.assertEqual(checks_mod.validate(completed(route), route), [])

    def test_missing_or_extra_module_is_rejected(self):
        route = route_fixture()

        missing = completed(route)
        missing["claims"][0]["checks"].pop()
        errors = checks_mod.validate(missing, route)
        self.assertTrue(any("modules/order must exactly match" in x for x in errors), errors)

        extra = completed(route)
        extra["claims"][1]["checks"].append({
            "module": "follow-up-boundaries.md",
            "status": "clear",
            "source_locations": ["Results"],
            "reason": "Unrouted filler.",
        })
        errors = checks_mod.validate(extra, route)
        self.assertTrue(any("modules/order must exactly match" in x for x in errors), errors)

    def test_trap_modules_require_mitigation_review(self):
        route = route_fixture()
        data = completed(route)
        data["claims"][0]["checks"][0]["mitigation_checked"] = False
        errors = checks_mod.validate(data, route)
        self.assertTrue(any("mitigation_checked must be true" in x for x in errors), errors)

    def test_nontrap_module_does_not_require_fake_mitigation_field(self):
        route = route_fixture()
        data = completed(route)
        nontrap = data["claims"][1]["checks"][0]
        self.assertEqual(nontrap["module"], "evidence-dependence.md")
        self.assertNotIn("mitigation_checked", nontrap)
        self.assertEqual(checks_mod.validate(data, route), [])

    def test_unclear_check_blocks_sufficient_support_only(self):
        route = route_fixture()
        data = completed(route)
        data["claims"][0]["checks"][0]["status"] = "unclear"
        data["claims"][0]["checks"][0]["reason"] = "The needed detail is not available."

        audit = {
            "claims": [
                {"support": {"support_level": "sufficient"}},
                {"support": {"support_level": "sufficient"}},
            ]
        }
        errors = checks_mod.check_support_alignment(data, audit)
        self.assertTrue(
            any("sufficient support conflicts with unresolved routed module check" in x for x in errors),
            errors,
        )

        audit["claims"][0]["support"]["support_level"] = "partial"
        self.assertEqual(checks_mod.check_support_alignment(data, audit), [])

    def test_source_trace_cannot_be_skipped_or_duplicated(self):
        route = route_fixture()
        data = completed(route)
        data["claims"][0]["checks"][0]["source_locations"] = []
        errors = checks_mod.validate(data, route)
        self.assertTrue(any("source_locations must be a non-empty string list" in x for x in errors), errors)

        data = completed(route)
        data["claims"][0]["checks"][0]["source_locations"] = ["Table 2", "Table 2"]
        errors = checks_mod.validate(data, route)
        self.assertTrue(any("source_locations must not contain duplicates" in x for x in errors), errors)

    def test_reason_and_status_cannot_be_skipped(self):
        route = route_fixture()
        data = completed(route)
        data["claims"][0]["checks"][0]["reason"] = ""
        data["claims"][0]["checks"][1]["status"] = "done"
        errors = checks_mod.validate(data, route)
        self.assertTrue(any("reason must be a non-empty string" in x for x in errors), errors)
        self.assertTrue(any("status must be one of" in x for x in errors), errors)


if __name__ == "__main__":
    unittest.main()
