import copy
import importlib.util
import json
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
AUDIT_GATE = SKILL / "scripts" / "audit_gate.py"
SABOTAGE_TEST = ROOT / "tests" / "test_fail_closed_sabotage.py"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = load_module("common_mode_gate", AUDIT_GATE)
sabotage = load_module("common_mode_sabotage", SABOTAGE_TEST)


class CommonModeOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory_fixture = json.loads(
            sabotage.INVENTORY_FIXTURE.read_text(encoding="utf-8")
        )
        cls.evidence_types = EVIDENCE_TYPES.read_text(encoding="utf-8")

    def pristine(self, kind: str) -> dict:
        original = sabotage.gate
        sabotage.gate = gate
        try:
            return sabotage.pristine_workflow(kind, self.inventory_fixture)
        finally:
            sabotage.gate = original

    def validate(self, artifacts: dict) -> list[str]:
        return gate.validate_gate(
            artifacts["audit"],
            semantic=artifacts["semantic"],
            lexical=artifacts["lexical"],
            router_text=artifacts["router_text"],
            route=artifacts["route"],
            inventory=artifacts["inventory"],
            context_bundle=artifacts["context"],
            module_checks=artifacts["module_checks"],
            evidence_types_text=self.evidence_types,
        )

    def test_required_module_survives_even_if_shared_merge_is_wrong(self):
        artifacts = self.pristine("simple")
        bad_route = copy.deepcopy(artifacts["route"])
        bad_route["modules"].remove("statistical-traps.md")
        bad_route["primary_module_count"] -= 1
        for item in bad_route["claim_module_requirements"]:
            if "statistical-traps.md" in item["modules"]:
                item["modules"].remove("statistical-traps.md")

        artifacts["route"] = None
        artifacts["context"] = gate.build_context.render_bundle(bad_route)
        artifacts["module_checks"] = sabotage.completed_module_checks(bad_route)

        with mock.patch.object(
            gate.build_context,
            "recompute_route",
            return_value=bad_route,
        ):
            errors = self.validate(artifacts)

        self.assertTrue(
            any(error.startswith("[G123]") for error in errors),
            errors,
        )
        self.assertTrue(
            any("semantic required module missing" in error for error in errors),
            errors,
        )

    def test_required_inventory_survives_even_if_shared_merge_is_wrong(self):
        artifacts = self.pristine("inventory")
        bad_route = copy.deepcopy(artifacts["route"])
        bad_route["use_evidence_inventory"] = False
        bad_route["inventory_basis"] = "mutant dropped semantic requirement"

        artifacts["route"] = None
        artifacts["inventory"] = None
        artifacts["context"] = gate.build_context.render_bundle(bad_route)
        artifacts["module_checks"] = sabotage.completed_module_checks(bad_route)

        with mock.patch.object(
            gate.build_context,
            "recompute_route",
            return_value=bad_route,
        ):
            errors = self.validate(artifacts)

        self.assertTrue(
            any(error.startswith("[G123]") for error in errors),
            errors,
        )
        self.assertTrue(
            any("semantic required evidence inventory was dropped" in error for error in errors),
            errors,
        )
        self.assertFalse(
            any(error.startswith("[G110]") for error in errors),
            errors,
        )

    def test_shared_context_renderer_bug_cannot_self_validate(self):
        artifacts = self.pristine("simple")
        bad_context = artifacts["context"].replace(
            ", statistical-traps.md",
            "",
            1,
        )
        artifacts["context"] = bad_context

        with mock.patch.object(
            gate.build_context,
            "render_bundle",
            return_value=bad_context,
        ):
            errors = self.validate(artifacts)

        self.assertFalse(
            any(error.startswith("[G109]") for error in errors),
            errors,
        )
        self.assertTrue(
            any(error.startswith("[G124]") for error in errors),
            errors,
        )

    def test_shared_context_renderer_cannot_hide_inventory_contract(self):
        artifacts = self.pristine("inventory")
        bad_context = artifacts["context"].replace(
            ", evidence-inventory-format.md",
            "",
            1,
        )
        artifacts["context"] = bad_context

        with mock.patch.object(
            gate.build_context,
            "render_bundle",
            return_value=bad_context,
        ):
            errors = self.validate(artifacts)

        self.assertFalse(
            any(error.startswith("[G109]") for error in errors),
            errors,
        )
        self.assertTrue(
            any(error.startswith("[G124]") for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
