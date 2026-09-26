import copy
import importlib.util
import json
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
AUDIT_GATE = SKILL / "scripts" / "audit_gate.py"
SABOTAGE_TEST = ROOT / "tests" / "test_fail_closed_sabotage.py"
GATE_MUTATIONS = ROOT / "tests" / "test_gate_mutation_canaries.py"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


real_gate = load_module("second_order_real_gate", AUDIT_GATE)
sabotage = load_module("second_order_sabotage", SABOTAGE_TEST)
gate_mutations = load_module("second_order_gate_mutations", GATE_MUTATIONS)


def validate(gate, artifacts: dict, evidence_types: str) -> list[str]:
    return gate.validate_gate(
        artifacts["audit"],
        semantic=artifacts["semantic"],
        lexical=artifacts["lexical"],
        router_text=artifacts["router_text"],
        route=artifacts["route"],
        inventory=artifacts["inventory"],
        context_bundle=artifacts["context"],
        module_checks=artifacts["module_checks"],
        evidence_types_text=evidence_types,
    )


class SecondOrderMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory_fixture = json.loads(
            sabotage.INVENTORY_FIXTURE.read_text(encoding="utf-8")
        )
        cls.evidence_types = EVIDENCE_TYPES.read_text(encoding="utf-8")
        cls.source = AUDIT_GATE.read_text(encoding="utf-8")
        cls.sites = gate_mutations.guard_emission_sites(cls.source)

    def pristine(self, kind: str) -> dict:
        original = sabotage.gate
        sabotage.gate = real_gate
        try:
            return sabotage.pristine_workflow(kind, self.inventory_fixture)
        finally:
            sabotage.gate = original

    def without_guard(self, guard: str):
        lines = self.sites[guard]
        self.assertEqual(len(lines), 1, guard)
        return gate_mutations.load_guard_mutant(self.source, guard, lines[0])

    def test_bad_merge_plus_g123_deletion_still_fails_closed(self):
        artifacts = self.pristine("simple")
        bad_route = copy.deepcopy(artifacts["route"])
        bad_route["modules"].remove("statistical-traps.md")
        bad_route["primary_module_count"] -= 1
        for item in bad_route["claim_module_requirements"]:
            if "statistical-traps.md" in item["modules"]:
                item["modules"].remove("statistical-traps.md")

        artifacts["route"] = None
        artifacts["context"] = real_gate.build_context.render_bundle(bad_route)
        artifacts["module_checks"] = sabotage.completed_module_checks(bad_route)

        mutant = self.without_guard("G123")
        with mock.patch.object(
            mutant.build_context,
            "recompute_route",
            return_value=bad_route,
        ):
            errors = validate(mutant, artifacts, self.evidence_types)

        self.assertTrue(
            errors,
            "second-order mutant escaped: bad merge + deleted semantic oracle",
        )
        self.assertTrue(
            any(error.startswith("[G126]") for error in errors),
            errors,
        )

    def test_bad_inventory_merge_plus_g123_deletion_still_fails_closed(self):
        artifacts = self.pristine("inventory")
        bad_route = copy.deepcopy(artifacts["route"])
        bad_route["use_evidence_inventory"] = False
        bad_route["inventory_basis"] = "mutant dropped semantic requirement"

        artifacts["route"] = None
        artifacts["inventory"] = None
        artifacts["context"] = real_gate.build_context.render_bundle(bad_route)
        artifacts["module_checks"] = sabotage.completed_module_checks(bad_route)

        mutant = self.without_guard("G123")
        with mock.patch.object(
            mutant.build_context,
            "recompute_route",
            return_value=bad_route,
        ):
            errors = validate(mutant, artifacts, self.evidence_types)

        self.assertTrue(
            any(error.startswith("[G126]") for error in errors),
            errors,
        )

    def test_shared_renderer_bug_plus_g124_deletion_still_fails_closed(self):
        artifacts = self.pristine("simple")
        begin = "## BEGIN REFERENCE: statistical-traps.md\n\n"
        end = "\n\n## END REFERENCE: statistical-traps.md"
        prefix, rest = artifacts["context"].split(begin, 1)
        _, suffix = rest.split(end, 1)
        bad_context = prefix + suffix
        bad_context = bad_context.replace(
            ", statistical-traps.md",
            "",
            1,
        )
        artifacts["context"] = bad_context

        mutant = self.without_guard("G124")
        with mock.patch.object(
            mutant.build_context,
            "render_bundle",
            return_value=bad_context,
        ):
            errors = validate(mutant, artifacts, self.evidence_types)

        self.assertTrue(
            errors,
            "second-order mutant escaped: bad renderer + deleted structure oracle",
        )
        self.assertTrue(
            any(error.startswith("[G125]") for error in errors),
            errors,
        )

    def test_corrupted_reference_body_plus_g125_deletion_is_caught_by_g109(self):
        artifacts = self.pristine("simple")
        begin = "## BEGIN REFERENCE: statistical-traps.md\n\n"
        end = "\n\n## END REFERENCE: statistical-traps.md"
        prefix, rest = artifacts["context"].split(begin, 1)
        _, suffix = rest.split(end, 1)
        artifacts["context"] = (
            prefix + begin + "CORRUPTED REFERENCE BODY" + end + suffix
        )

        mutant = self.without_guard("G125")
        errors = validate(mutant, artifacts, self.evidence_types)
        self.assertTrue(
            any(error.startswith("[G109]") for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
