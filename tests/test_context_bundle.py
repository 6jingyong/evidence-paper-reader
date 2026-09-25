import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPT = SKILL / "scripts" / "build_context.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


builder = load_module("build_context", SCRIPT)


def semantic(*, inventory="not_required", measurement="not_required"):
    routes = {name: "not_required" for name in builder.merge_route.ROUTES}
    routes["statistical-traps.md"] = "required"
    routes["study-design-traps.md"] = "required"
    routes["measurement-traps.md"] = measurement
    return {
        "claims": [
            {
                "claim_id": "C1",
                "claim_text": "The intervention reduced the primary outcome.",
                "routes": routes,
                "inventory": inventory,
                "reason": "The claim depends on the randomized comparison and statistical estimate.",
            }
        ]
    }


class ContextBundleTests(unittest.TestCase):
    def test_bundle_includes_base_and_only_routed_methodology(self):
        route = builder.recompute_route(semantic(), lexical=None)
        names = builder.context_files(route)
        for name in builder.BASE_REFERENCES:
            self.assertIn(name, names)
        self.assertIn("statistical-traps.md", names)
        self.assertIn("study-design-traps.md", names)
        self.assertIn("false-positive-guards.md", names)
        self.assertNotIn("measurement-traps.md", names)
        self.assertNotIn("evidence-inventory-format.md", names)

        bundle = builder.render_bundle(route)
        self.assertIn("C1: The intervention reduced the primary outcome.", bundle)
        self.assertIn("claim module requirements:", bundle)
        self.assertIn("C1: statistical-traps.md, study-design-traps.md", bundle)
        self.assertIn("BEGIN REFERENCE: statistical-traps.md", bundle)
        self.assertNotIn("BEGIN REFERENCE: measurement-traps.md", bundle)

    def test_route_generates_exact_module_check_template(self):
        route = builder.recompute_route(semantic(), lexical=None)
        template = builder.module_checks.template(route)
        self.assertEqual(
            [x["module"] for x in template["claims"][0]["checks"]],
            ["statistical-traps.md", "study-design-traps.md"],
        )
        self.assertTrue(
            all(
                check.get("mitigation_checked") is False
                for check in template["claims"][0]["checks"]
            )
        )

    def test_inventory_route_adds_inventory_contract(self):
        route = builder.recompute_route(semantic(inventory="required"), lexical=None)
        self.assertTrue(route["use_evidence_inventory"])
        self.assertIn("evidence-inventory-format.md", builder.context_files(route))

    def test_unclear_requires_lexical_route(self):
        with self.assertRaises(ValueError):
            builder.recompute_route(semantic(measurement="unclear"), lexical=None)

        route = builder.recompute_route(
            semantic(measurement="unclear"),
            lexical=None,
            router_text="The sensor calibration was checked before analysis.",
        )
        self.assertIn("measurement-traps.md", route["modules"])

    def test_cached_lexical_route_is_verification_only(self):
        with self.assertRaises(ValueError):
            builder.recompute_route(
                semantic(),
                lexical={"suggested": [], "use_evidence_inventory": False},
            )

        router_text = "A randomized trial reports a hazard ratio."
        exact_cache = builder.suggest_modules.suggest_modules(router_text)
        route = builder.recompute_route(
            semantic(),
            lexical=exact_cache,
            router_text=router_text,
        )
        self.assertIn("statistical-traps.md", route["modules"])

        bad_cache = dict(exact_cache)
        bad_cache["use_evidence_inventory"] = not exact_cache["use_evidence_inventory"]
        with self.assertRaises(ValueError):
            builder.recompute_route(
                semantic(),
                lexical=bad_cache,
                router_text=router_text,
            )

    def test_bundle_is_deterministic(self):
        route = builder.recompute_route(semantic(), lexical=None)
        self.assertEqual(builder.render_bundle(route), builder.render_bundle(route))


if __name__ == "__main__":
    unittest.main()
