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

REQUIRED_LOGIC_OPERATORS = {
    "skip_ledger_validation",
    "skip_semantic_validation",
    "skip_route_validation",
    "skip_module_check_validation",
    "skip_support_alignment",
    "skip_inventory_validation",
    "skip_inventory_alignment",
    "skip_public_validation",
    "trust_cached_recompute",
    "trust_supplied_context",
    "disable_claim_audit",
    "ignore_route_drift",
    "ignore_claim_text_drift",
    "allow_missing_inventory",
    "allow_forbidden_inventory",
    "ignore_inventory_claim_drift",
    "ignore_inventory_viability",
    "allow_missing_module_checks",
}


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


class LogicWeakeningMutator(ast.NodeTransformer):
    CALL_TO_EMPTY = {
        "skip_ledger_validation": "render_audit.validate_ledger",
        "skip_semantic_validation": "merge_route.validate_semantic",
        "skip_route_validation": "validate_route_result",
        "skip_module_check_validation": "module_checks_mod.validate",
        "skip_support_alignment": "module_checks_mod.check_support_alignment",
        "skip_inventory_validation": "inventory_mod.validate_inventory",
        "skip_inventory_alignment": "inventory_mod.check_audit_alignment",
        "skip_public_validation": "markdown_validator.validate",
    }

    def __init__(self, mutation_id: str):
        self.mutation_id = mutation_id
        self.mutations = 0

    def visit_Call(self, node: ast.Call):
        node = self.generic_visit(node)
        path = call_path(node.func)

        target = self.CALL_TO_EMPTY.get(self.mutation_id)
        if target is not None and path == target:
            self.mutations += 1
            return ast.copy_location(ast.List(elts=[], ctx=ast.Load()), node)

        if (
            self.mutation_id == "trust_cached_recompute"
            and path == "build_context.recompute_route"
        ):
            self.mutations += 1
            return ast.copy_location(ast.Name(id="route", ctx=ast.Load()), node)

        if (
            self.mutation_id == "trust_supplied_context"
            and path == "build_context.render_bundle"
        ):
            self.mutations += 1
            return ast.copy_location(ast.Name(id="context_bundle", ctx=ast.Load()), node)

        return node

    def visit_Assign(self, node: ast.Assign):
        node = self.generic_visit(node)
        if self.mutation_id == "disable_claim_audit":
            if any(
                isinstance(target, ast.Name) and target.id == "claim_audit"
                for target in node.targets
            ):
                self.mutations += 1
                node.value = ast.Constant(False)
        return node

    def visit_Compare(self, node: ast.Compare):
        node = self.generic_visit(node)
        if len(node.ops) != 1 or len(node.comparators) != 1:
            return node

        left_name = node.left.id if isinstance(node.left, ast.Name) else None
        right = node.comparators[0]
        right_name = right.id if isinstance(right, ast.Name) else None

        if self.mutation_id == "ignore_route_drift":
            if (
                left_name == "route"
                and isinstance(node.ops[0], ast.NotEq)
                and right_name == "recomputed_route"
            ):
                self.mutations += 1
                return ast.copy_location(ast.Constant(False), node)

        if self.mutation_id == "ignore_claim_text_drift":
            if left_name == "semantic_text" and right_name == "audit_text":
                if isinstance(node.ops[0], ast.NotEq):
                    self.mutations += 1
                    return ast.copy_location(ast.Constant(False), node)
                if isinstance(node.ops[0], ast.Eq):
                    self.mutations += 1
                    return ast.copy_location(ast.Constant(True), node)

        if self.mutation_id == "allow_missing_inventory":
            if (
                left_name == "use_inventory"
                and isinstance(node.ops[0], ast.Is)
                and isinstance(right, ast.Constant)
                and right.value is True
            ):
                self.mutations += 1
                return ast.copy_location(ast.Constant(False), node)

        if self.mutation_id == "allow_forbidden_inventory":
            if (
                left_name == "use_inventory"
                and isinstance(node.ops[0], ast.Is)
                and isinstance(right, ast.Constant)
                and right.value is False
            ):
                self.mutations += 1
                return ast.copy_location(ast.Constant(False), node)

        if self.mutation_id == "ignore_inventory_claim_drift":
            if (
                left_name == "inventory_claims"
                and isinstance(node.ops[0], ast.NotEq)
                and right_name == "audit_claims"
            ):
                self.mutations += 1
                return ast.copy_location(ast.Constant(False), node)

        if self.mutation_id == "ignore_inventory_viability":
            if (
                isinstance(node.left, ast.Call)
                and call_path(node.left.func) == "inventory.get"
                and node.left.args
                and isinstance(node.left.args[0], ast.Constant)
                and node.left.args[0].value == "evidence_viability"
                and isinstance(node.ops[0], ast.NotEq)
                and right_name == "viability"
            ):
                self.mutations += 1
                return ast.copy_location(ast.Constant(False), node)

        return node

    def visit_BoolOp(self, node: ast.BoolOp):
        node = self.generic_visit(node)
        if self.mutation_id != "allow_missing_module_checks":
            return node
        if not isinstance(node.op, ast.And):
            return node

        names = {
            child.id
            for child in ast.walk(node)
            if isinstance(child, ast.Name)
        }
        has_none_check = any(
            isinstance(child, ast.Compare)
            and isinstance(child.left, ast.Name)
            and child.left.id == "module_checks"
            and len(child.ops) == 1
            and isinstance(child.ops[0], ast.Is)
            and len(child.comparators) == 1
            and isinstance(child.comparators[0], ast.Constant)
            and child.comparators[0].value is None
            for child in ast.walk(node)
        )
        if "has_required_checks" in names and has_none_check:
            self.mutations += 1
            return ast.copy_location(ast.Constant(False), node)
        return node


def load_logic_mutant(source: str, mutation: dict):
    tree = ast.parse(source)
    transformer = LogicWeakeningMutator(mutation["operator"])
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    expected = mutation.get("expected_sites", 1)
    if transformer.mutations != expected:
        raise AssertionError(
            f"{mutation['id']} expected {expected} source mutation(s), "
            f"got {transformer.mutations}"
        )

    module = types.ModuleType(f"audit_gate_logic_mutant_{mutation['id']}")
    module.__file__ = str(AUDIT_GATE)
    exec(compile(tree, str(AUDIT_GATE), "exec"), module.__dict__)
    return module


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
            artifacts["route"] = None
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
        elif scenario == "semantic_required_module_dropped":
            bad_route = copy.deepcopy(artifacts["route"])
            bad_route["modules"].remove("statistical-traps.md")
            bad_route["primary_module_count"] -= 1
            for item in bad_route["claim_module_requirements"]:
                if "statistical-traps.md" in item["modules"]:
                    item["modules"].remove("statistical-traps.md")
            artifacts["route"] = None
            artifacts["context"] = gate_module.build_context.render_bundle(bad_route)
            artifacts["module_checks"] = sabotage.completed_module_checks(bad_route)
            patcher = mock.patch.object(
                gate_module.build_context,
                "recompute_route",
                return_value=bad_route,
            )
        elif scenario == "shared_context_renderer_manifest_bug":
            bad_context = artifacts["context"].replace(
                ", statistical-traps.md",
                "",
                1,
            )
            artifacts["context"] = bad_context
            patcher = mock.patch.object(
                gate_module.build_context,
                "render_bundle",
                return_value=bad_context,
            )
        elif scenario == "shared_reference_body_corruption":
            begin = "## BEGIN REFERENCE: statistical-traps.md\n\n"
            end = "\n\n## END REFERENCE: statistical-traps.md"
            prefix, rest = artifacts["context"].split(begin, 1)
            _, suffix = rest.split(end, 1)
            bad_context = prefix + begin + "CORRUPTED REFERENCE BODY" + end + suffix
            artifacts["context"] = bad_context
            patcher = mock.patch.object(
                gate_module.build_context,
                "render_bundle",
                return_value=bad_context,
            )
        elif scenario == "semantic_execution_missing":
            bad_route = copy.deepcopy(artifacts["route"])
            bad_route["modules"].remove("statistical-traps.md")
            bad_route["primary_module_count"] -= 1
            for item in bad_route["claim_module_requirements"]:
                if "statistical-traps.md" in item["modules"]:
                    item["modules"].remove("statistical-traps.md")
            artifacts["route"] = None
            artifacts["context"] = gate_module.build_context.render_bundle(bad_route)
            artifacts["module_checks"] = sabotage.completed_module_checks(bad_route)
            patcher = mock.patch.object(
                gate_module.build_context,
                "recompute_route",
                return_value=bad_route,
            )
        elif scenario == "reasoning_graph_common_mode":
            audit = artifacts["audit"]
            audit["ledger_schema_version"] = 2
            audit["reasoning_edges"] = []
            for index, claim in enumerate(audit["claims"], start=1):
                level = claim["support"]["support_level"]
                status = {
                    "sufficient": "direct",
                    "partial": "qualified",
                    "insufficient": "unsupported",
                    "unclear": "unclear",
                }[level]
                audit["reasoning_edges"].append({
                    "edge_id": f"R{index}",
                    "target_claim": index,
                    "evidence_nodes": list(claim["support"]["evidence_nodes"]),
                    "upstream_claims": list(claim["support"].get("upstream_claims", [])),
                    "inference_type": "direct-result",
                    "reasoning_status": status,
                    "added_reach": "none" if status == "direct" else "The stated claim adds reach beyond the direct result.",
                    "assumptions": [],
                })
            audit["reasoning_edges"][0]["evidence_nodes"] = ["E999"]
            patcher = mock.patch.object(
                gate_module.render_audit,
                "validate_ledger",
                return_value=[],
            )
        elif scenario == "evidence_relation_common_mode":
            audit = artifacts["audit"]
            audit["ledger_schema_version"] = 3
            audit["reasoning_edges"] = []
            for index, claim in enumerate(audit["claims"], start=1):
                level = claim["support"]["support_level"]
                status = {
                    "sufficient": "direct",
                    "partial": "qualified",
                    "insufficient": "unsupported",
                    "unclear": "unclear",
                }[level]
                claim["support"]["evidence_relations"] = [
                    {
                        "evidence_node": node,
                        "relation": "supports",
                        "reason": "The evidence node bears on the bounded claim.",
                    }
                    for node in claim["support"]["evidence_nodes"]
                ]
                audit["reasoning_edges"].append({
                    "edge_id": f"R{index}",
                    "target_claim": index,
                    "evidence_nodes": list(claim["support"]["evidence_nodes"]),
                    "upstream_claims": list(claim["support"].get("upstream_claims", [])),
                    "inference_type": "direct-result",
                    "reasoning_status": status,
                    "added_reach": "none" if status == "direct" else "The stated claim adds reach beyond the direct result.",
                    "assumptions": [],
                })
            audit["claims"][0]["support"]["evidence_relations"][0]["evidence_node"] = "E999"
            patcher = mock.patch.object(
                gate_module.render_audit,
                "validate_ledger",
                return_value=[],
            )
        elif scenario == "author_boundary_common_mode":
            audit = artifacts["audit"]
            audit["ledger_schema_version"] = 4
            audit["reasoning_edges"] = []
            for index, claim in enumerate(audit["claims"], start=1):
                level = claim["support"]["support_level"]
                status = {
                    "sufficient": "direct",
                    "partial": "qualified",
                    "insufficient": "unsupported",
                    "unclear": "unclear",
                }[level]
                claim["support"]["evidence_relations"] = [
                    {
                        "evidence_node": node,
                        "relation": "supports",
                        "reason": "The evidence node bears on the bounded claim.",
                    }
                    for node in claim["support"]["evidence_nodes"]
                ]
                claim["support"]["author_boundary"] = {
                    "status": "not-applicable",
                    "summary": "none",
                    "source_location": "none",
                }
                audit["reasoning_edges"].append({
                    "edge_id": f"R{index}",
                    "target_claim": index,
                    "evidence_nodes": list(claim["support"]["evidence_nodes"]),
                    "upstream_claims": list(claim["support"].get("upstream_claims", [])),
                    "inference_type": "direct-result",
                    "reasoning_status": status,
                    "added_reach": "none" if status == "direct" else "The stated claim adds reach beyond the direct result.",
                    "assumptions": [],
                })
            target = audit["claims"][0]["support"]
            target["author_boundary"] = {
                "status": "explicit",
                "summary": "The authors explicitly acknowledge the same boundary.",
                "source_location": "none",
            }
            patcher = mock.patch.object(
                gate_module.render_audit,
                "validate_ledger",
                return_value=[],
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

    def test_logic_weakening_mutants_are_killed_by_existing_sabotage_cases(self):
        cases = {case["id"]: case for case in self.matrix["cases"]}
        mutations = self.matrix.get("logic_weakening_mutations", [])
        self.assertEqual(len(mutations), len(REQUIRED_LOGIC_OPERATORS))
        self.assertEqual(
            {mutation["operator"] for mutation in mutations},
            REQUIRED_LOGIC_OPERATORS,
        )

        seen = set()
        survivors = []
        for mutation in mutations:
            self.assertNotIn(mutation["id"], seen)
            seen.add(mutation["id"])
            designated = mutation.get("cases", [])
            self.assertTrue(designated, mutation["id"])

            mutant = load_logic_mutant(self.source, mutation)
            killed_by = []
            for case_id in designated:
                self.assertIn(case_id, cases)
                case = cases[case_id]
                self.assertTrue(
                    case_contract_passes(
                        self.real_gate,
                        copy.deepcopy(case),
                        self.inventory_fixture,
                        self.evidence_types,
                    ),
                    f"baseline contract is invalid for {mutation['id']} via {case_id}",
                )
                if not case_contract_passes(
                    mutant,
                    copy.deepcopy(case),
                    self.inventory_fixture,
                    self.evidence_types,
                ):
                    killed_by.append(case_id)

            if not killed_by:
                survivors.append(
                    {
                        "id": mutation["id"],
                        "operator": mutation["operator"],
                        "designated_cases": designated,
                    }
                )

        self.assertFalse(
            survivors,
            "logic-weakening mutant(s) survived the fail-closed contract: "
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
