import ast
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
MATRIX = ROOT / "tests" / "sabotage-matrix.json"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


sabotage = load_module("gate_mutation_sabotage", SABOTAGE_TEST)


def guard_codes(node: ast.AST) -> set[str]:
    codes = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        if not isinstance(child.func, ast.Name) or child.func.id != "_guard":
            continue
        if not child.args:
            continue
        first = child.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            codes.add(first.value)
    return codes


def guard_emission_sites(source: str) -> dict[str, list[int]]:
    tree = ast.parse(source)
    sites: dict[str, list[int]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            target_names = {
                target.id
                for target in node.targets
                if isinstance(target, ast.Name)
            }
            if "errors" not in target_names:
                continue
        elif isinstance(node, ast.Expr):
            call = node.value
            if not (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "errors"
                and call.func.attr in {"append", "extend"}
            ):
                continue
        else:
            continue

        for code in guard_codes(node):
            sites.setdefault(code, []).append(node.lineno)

    for code in sites:
        sites[code].sort()
    return sites


class DeleteGuardEmission(ast.NodeTransformer):
    def __init__(self, guard: str, lineno: int):
        self.guard = guard
        self.lineno = lineno
        self.mutations = 0

    def visit_Assign(self, node: ast.Assign):
        if node.lineno == self.lineno and self.guard in guard_codes(node):
            target_names = {
                target.id
                for target in node.targets
                if isinstance(target, ast.Name)
            }
            if "errors" in target_names:
                self.mutations += 1
                replacement = ast.Assign(
                    targets=node.targets,
                    value=ast.List(elts=[], ctx=ast.Load()),
                )
                return ast.copy_location(replacement, node)
        return self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr):
        if node.lineno == self.lineno and self.guard in guard_codes(node):
            call = node.value
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "errors"
                and call.func.attr in {"append", "extend"}
            ):
                self.mutations += 1
                return ast.copy_location(ast.Pass(), node)
        return self.generic_visit(node)


def load_guard_mutant(source: str, guard: str, lineno: int):
    tree = ast.parse(source)
    transformer = DeleteGuardEmission(guard, lineno)
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    if transformer.mutations != 1:
        raise AssertionError(
            f"expected exactly one mutation for {guard} at line {lineno}, "
            f"got {transformer.mutations}"
        )

    module = types.ModuleType(f"audit_gate_mutant_{guard}_{lineno}")
    module.__file__ = str(AUDIT_GATE)
    exec(compile(tree, str(AUDIT_GATE), "exec"), module.__dict__)
    return module


def validate_with(gate_module, artifacts: dict, evidence_types: str) -> list[str]:
    return gate_module.validate_gate(
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


def case_contract_passes(
    gate_module,
    case: dict,
    inventory_fixture: dict,
    evidence_types: str,
) -> bool:
    original_gate = sabotage.gate
    sabotage.gate = gate_module
    try:
        artifacts = sabotage.pristine_workflow(
            case["baseline"],
            inventory_fixture,
        )
        target = case["target"]
        artifacts[target] = sabotage.apply_mutation(
            artifacts[target],
            case,
        )
        for extra in case.get("also", []):
            artifacts[target] = sabotage.apply_mutation(
                artifacts[target],
                extra,
            )
        errors = validate_with(gate_module, artifacts, evidence_types)
    except Exception:
        return False
    finally:
        sabotage.gate = original_gate

    if not errors:
        return False
    if not any(case["expect"] in str(error) for error in errors):
        return False
    for guard in case.get("guards", []):
        if not any(str(error).startswith(f"[{guard}]") for error in errors):
            return False
    return True


def special_canary_passes(
    gate_module,
    scenario: str,
    expected_guard: str,
    inventory_fixture: dict,
    evidence_types: str,
) -> bool:
    original_gate = sabotage.gate
    sabotage.gate = gate_module
    try:
        artifacts = sabotage.pristine_workflow("simple", inventory_fixture)

        if scenario == "recompute_returns_none":
            patcher = mock.patch.object(
                gate_module.build_context,
                "recompute_route",
                return_value=None,
            )
        elif scenario == "render_bundle_raises":
            patcher = mock.patch.object(
                gate_module.build_context,
                "render_bundle",
                side_effect=ValueError("simulated routed-reference failure"),
            )
        else:
            raise AssertionError(f"unknown mutation canary scenario: {scenario}")

        with patcher:
            errors = validate_with(gate_module, artifacts, evidence_types)
    except Exception:
        return False
    finally:
        sabotage.gate = original_gate

    return any(str(error).startswith(f"[{expected_guard}]") for error in errors)


class GateMutationCanaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = AUDIT_GATE.read_text(encoding="utf-8")
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.inventory_fixture = json.loads(
            sabotage.INVENTORY_FIXTURE.read_text(encoding="utf-8")
        )
        cls.evidence_types = EVIDENCE_TYPES.read_text(encoding="utf-8")
        cls.real_gate = sabotage.gate
        cls.sites = guard_emission_sites(cls.source)

    def test_mutation_corpus_covers_every_critical_guard_emission_site(self):
        self.assertEqual(set(self.sites), set(self.real_gate.CRITICAL_GUARDS))

        explicit = {
            (item["guard"], item["site"]): item["scenario"]
            for item in self.matrix.get("mutation_site_canaries", [])
        }
        cases_by_guard = {
            guard: [
                case
                for case in self.matrix["cases"]
                if guard in case.get("guards", [])
            ]
            for guard in self.real_gate.CRITICAL_GUARDS
        }

        survivors = []
        for guard in sorted(self.real_gate.CRITICAL_GUARDS):
            lines = self.sites[guard]
            for site, lineno in enumerate(lines, start=1):
                mutant = load_guard_mutant(self.source, guard, lineno)

                killed = False
                for case in cases_by_guard[guard]:
                    if not case_contract_passes(
                        mutant,
                        copy.deepcopy(case),
                        self.inventory_fixture,
                        self.evidence_types,
                    ):
                        killed = True
                        break

                if not killed:
                    scenario = explicit.get((guard, site))
                    if scenario is not None:
                        self.assertTrue(
                            special_canary_passes(
                                self.real_gate,
                                scenario,
                                guard,
                                self.inventory_fixture,
                                self.evidence_types,
                            ),
                            f"invalid baseline mutation canary for {guard} site {site}",
                        )
                        killed = not special_canary_passes(
                            mutant,
                            scenario,
                            guard,
                            self.inventory_fixture,
                            self.evidence_types,
                        )

                if not killed:
                    survivors.append(
                        {
                            "guard": guard,
                            "site": site,
                            "line": lineno,
                            "artifact_cases": [
                                case["id"] for case in cases_by_guard[guard]
                            ],
                            "special_canary": explicit.get((guard, site)),
                        }
                    )

        self.assertFalse(
            survivors,
            "gate deletion mutant(s) survived the sabotage contract: "
            + json.dumps(survivors, sort_keys=True),
        )

    def test_declared_site_canaries_reference_real_sites(self):
        declared = self.matrix.get("mutation_site_canaries", [])
        self.assertGreaterEqual(len(declared), 2)
        seen = set()
        for item in declared:
            key = (item["guard"], item["site"])
            self.assertNotIn(key, seen)
            seen.add(key)
            self.assertIn(item["guard"], self.sites)
            self.assertGreaterEqual(item["site"], 1)
            self.assertLessEqual(item["site"], len(self.sites[item["guard"]]))


if __name__ == "__main__":
    unittest.main()
