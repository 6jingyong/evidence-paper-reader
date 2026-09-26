import ast
import copy
import importlib.util
import json
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPTS = SKILL / "scripts"
AUDIT_GATE = SCRIPTS / "audit_gate.py"
SABOTAGE_TEST = ROOT / "tests" / "test_fail_closed_sabotage.py"
MATRIX = ROOT / "tests" / "sabotage-matrix.json"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"

DEPENDENCIES = {
    "build_context": SCRIPTS / "build_context.py",
    "merge_route": SCRIPTS / "merge_route.py",
    "evidence_inventory": SCRIPTS / "evidence_inventory.py",
    "module_checks": SCRIPTS / "module_checks.py",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


real_gate = load_module("dependency_mutation_real_gate", AUDIT_GATE)
sabotage = load_module("dependency_mutation_sabotage", SABOTAGE_TEST)


def call_path(node: ast.AST) -> str | None:
    parts = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return None


def strings_in(node: ast.AST) -> set[str]:
    return {
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }


def names_in(node: ast.AST) -> set[str]:
    return {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name)
    }


class DependencyMutator(ast.NodeTransformer):
    def __init__(self, operator: str):
        self.operator = operator
        self.mutations = 0

    def visit_Compare(self, node: ast.Compare):
        node = self.generic_visit(node)
        if len(node.ops) != 1 or len(node.comparators) != 1:
            return node

        left_name = node.left.id if isinstance(node.left, ast.Name) else None
        right = node.comparators[0]
        right_name = right.id if isinstance(right, ast.Name) else None

        if self.operator == "ignore_lexical_cache_mismatch":
            if (
                left_name == "lexical"
                and isinstance(node.ops[0], ast.NotEq)
                and right_name == "recomputed_lexical"
            ):
                self.mutations += 1
                return ast.copy_location(ast.Constant(False), node)

        if self.operator == "ignore_semantic_required_module":
            required_comparison = (
                left_name == "decision"
                and isinstance(node.ops[0], ast.Eq)
                and isinstance(right, ast.Constant)
                and right.value == "required"
            )
            aggregate_required = (
                isinstance(node.left, ast.Constant)
                and node.left.value == "required"
                and isinstance(node.ops[0], ast.In)
                and right_name == "decisions"
            )
            if required_comparison or aggregate_required:
                self.mutations += 1
                return ast.copy_location(ast.Constant(False), node)

        return node

    def visit_If(self, node: ast.If):
        node = self.generic_visit(node)
        strings = strings_in(node)
        names = names_in(node)

        if self.operator == "allow_cached_lexical_without_router_text":
            if any("cached lexical route cannot substitute for router text" in x for x in strings):
                self.mutations += 1
                node.test = ast.Constant(False)
                return node

        if self.operator == "allow_unclear_without_router_text":
            if any("semantic route contains unclear decisions" in x for x in strings):
                self.mutations += 1
                node.test = ast.Constant(False)
                return node

        if self.operator == "omit_inventory_reference":
            if "evidence-inventory-format.md" in strings:
                self.mutations += 1
                node.test = ast.Constant(False)
                return node

        if self.operator == "ignore_semantic_required_inventory":
            assigns_true = any(
                isinstance(child, ast.Assign)
                and any(
                    isinstance(target, ast.Name) and target.id == "use_inventory"
                    for target in child.targets
                )
                and isinstance(child.value, ast.Constant)
                and child.value.value is True
                for child in node.body
            )
            if assigns_true and "inventory_decisions" in names:
                self.mutations += 1
                node.test = ast.Constant(False)
                return node

        message_operators = {
            "allow_cross_result_merge": "one evidence node cannot merge different result keys",
            "allow_split_result_nodes": "is promoted into multiple evidence nodes",
            "allow_uncovered_claim": "claim has neither promoted evidence nor an unresolved_claims entry",
            "allow_shared_unit_convergence": "independent convergence shares evidence unit(s)",
            "ignore_mitigation_check": "mitigation_checked must be true after applying false-positive guards",
            "ignore_module_order": "checks modules/order must exactly match routed requirements",
            "ignore_source_locations": "source_locations must be a non-empty string list",
            "ignore_unresolved_support": "sufficient support conflicts with unresolved routed",
        }
        needle = message_operators.get(self.operator)
        if needle is not None and any(needle in x for x in strings):
            self.mutations += 1
            node.test = ast.Constant(False)
            return node

        return node

    def visit_For(self, node: ast.For):
        node = self.generic_visit(node)
        if self.operator != "omit_routed_modules":
            return node
        if not isinstance(node.target, ast.Name) or node.target.id != "module":
            return node
        if not isinstance(node.iter, ast.Call) or call_path(node.iter.func) != "route.get":
            return node
        if not node.iter.args:
            return node
        first = node.iter.args[0]
        if isinstance(first, ast.Constant) and first.value == "modules":
            self.mutations += 1
            node.body = [ast.Pass()]
        return node


def load_mutated_dependency(mutation: dict):
    path = DEPENDENCIES[mutation["module"]]
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    transformer = DependencyMutator(mutation["operator"])
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)

    expected = mutation.get("expected_sites", 1)
    if transformer.mutations != expected:
        raise AssertionError(
            f"{mutation['id']} expected {expected} mutation site(s), "
            f"got {transformer.mutations}"
        )

    module = types.ModuleType(f"dependency_mutant_{mutation['id']}")
    module.__file__ = str(path)
    exec(compile(tree, str(path), "exec"), module.__dict__)
    return module


def gate_with_dependency_mutant(mutation: dict):
    gate = load_module(f"dependency_gate_{mutation['id']}", AUDIT_GATE)
    mutant = load_mutated_dependency(mutation)

    if mutation["module"] == "build_context":
        gate.build_context = mutant
    elif mutation["module"] == "merge_route":
        gate.merge_route = mutant
        gate.build_context.merge_route = mutant
    elif mutation["module"] == "evidence_inventory":
        gate.inventory_mod = mutant
    elif mutation["module"] == "module_checks":
        gate.module_checks_mod = mutant
    else:
        raise AssertionError(f"unknown dependency module: {mutation['module']}")
    return gate


def pristine(kind: str, inventory_fixture: dict) -> dict:
    original = sabotage.gate
    sabotage.gate = real_gate
    try:
        return sabotage.pristine_workflow(kind, inventory_fixture)
    finally:
        sabotage.gate = original


def apply_case(case: dict, inventory_fixture: dict) -> dict:
    artifacts = pristine(case["baseline"], inventory_fixture)
    target = case["target"]
    artifacts[target] = sabotage.apply_mutation(artifacts[target], case)
    for extra in case.get("also", []):
        artifacts[target] = sabotage.apply_mutation(artifacts[target], extra)
    return artifacts


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


def sabotage_contract_matches(
    gate,
    case: dict,
    inventory_fixture: dict,
    evidence_types: str,
) -> bool:
    try:
        errors = validate(gate, apply_case(case, inventory_fixture), evidence_types)
    except Exception:
        return False
    if not errors:
        return False
    if not any(case["expect"] in str(error) for error in errors):
        return False
    return all(
        any(str(error).startswith(f"[{guard}]") for error in errors)
        for guard in case.get("guards", [])
    )


class DependencyMutationCanaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.inventory_fixture = json.loads(
            sabotage.INVENTORY_FIXTURE.read_text(encoding="utf-8")
        )
        cls.evidence_types = EVIDENCE_TYPES.read_text(encoding="utf-8")
        cls.cases = {case["id"]: case for case in cls.matrix["cases"]}

    def test_dependency_mutants_are_killed_by_existing_contracts(self):
        mutations = self.matrix.get("dependency_mutations", [])
        self.assertGreaterEqual(len(mutations), 15)

        seen = set()
        survivors = []
        for mutation in mutations:
            with self.subTest(mutation=mutation["id"]):
                self.assertNotIn(mutation["id"], seen)
                seen.add(mutation["id"])
                gate = gate_with_dependency_mutant(mutation)
                killed_by = []

                for kind in mutation.get("pristine", []):
                    baseline = pristine(kind, self.inventory_fixture)
                    self.assertEqual(
                        validate(real_gate, baseline, self.evidence_types),
                        [],
                        f"real baseline invalid for {mutation['id']}:{kind}",
                    )
                    if validate(gate, baseline, self.evidence_types):
                        killed_by.append(f"pristine:{kind}")

                for case_id in mutation.get("cases", []):
                    self.assertIn(case_id, self.cases)
                    case = self.cases[case_id]
                    self.assertTrue(
                        sabotage_contract_matches(
                            real_gate,
                            copy.deepcopy(case),
                            self.inventory_fixture,
                            self.evidence_types,
                        ),
                        f"real sabotage contract invalid for {mutation['id']}:{case_id}",
                    )
                    if not sabotage_contract_matches(
                        gate,
                        copy.deepcopy(case),
                        self.inventory_fixture,
                        self.evidence_types,
                    ):
                        killed_by.append(case_id)

                self.assertTrue(
                    mutation.get("pristine") or mutation.get("cases"),
                    f"{mutation['id']} has no observable contract",
                )
                if not killed_by:
                    survivors.append({
                        "id": mutation["id"],
                        "module": mutation["module"],
                        "operator": mutation["operator"],
                    })

        self.assertFalse(
            survivors,
            "dependency mutation(s) survived all designated contracts: "
            + json.dumps(survivors, sort_keys=True),
        )


if __name__ == "__main__":
    unittest.main()
