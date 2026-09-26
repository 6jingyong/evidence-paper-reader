import ast
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
AUDIT_GATE = SKILL / "scripts" / "audit_gate.py"
SABOTAGE_TEST = ROOT / "tests" / "test_fail_closed_sabotage.py"

REQUIRED_CLI_MUTATIONS = {
    "discard_validate_gate_errors",
    "ignore_nonempty_errors",
    "load_failure_returns_success",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


real_gate = load_module("cli_mutation_real_gate", AUDIT_GATE)
sabotage = load_module("cli_mutation_sabotage", SABOTAGE_TEST)


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


class CliMutator(ast.NodeTransformer):
    def __init__(self, operator: str):
        self.operator = operator
        self.in_main = False
        self.in_load_handler = False
        self.mutations = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old = self.in_main
        self.in_main = node.name == "main"
        node = self.generic_visit(node)
        self.in_main = old
        return node

    def visit_Assign(self, node: ast.Assign):
        node = self.generic_visit(node)
        if not self.in_main or self.operator != "discard_validate_gate_errors":
            return node
        targets_errors = any(
            isinstance(target, ast.Name) and target.id == "errors"
            for target in node.targets
        )
        if (
            targets_errors
            and isinstance(node.value, ast.Call)
            and call_name(node.value.func) == "validate_gate"
        ):
            self.mutations += 1
            node.value = ast.List(elts=[], ctx=ast.Load())
        return node

    def visit_If(self, node: ast.If):
        node = self.generic_visit(node)
        if not self.in_main or self.operator != "ignore_nonempty_errors":
            return node
        if isinstance(node.test, ast.Name) and node.test.id == "errors":
            self.mutations += 1
            node.test = ast.Constant(False)
        return node

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if not self.in_main:
            return self.generic_visit(node)

        old = self.in_load_handler
        names = {
            child.id
            for child in ast.walk(node.type)
            if isinstance(child, ast.Name)
        } if node.type is not None else set()
        self.in_load_handler = {"OSError", "ValueError"} <= names
        node = self.generic_visit(node)
        self.in_load_handler = old
        return node

    def visit_Return(self, node: ast.Return):
        node = self.generic_visit(node)
        if (
            self.in_main
            and self.in_load_handler
            and self.operator == "load_failure_returns_success"
            and isinstance(node.value, ast.Constant)
            and node.value.value == 1
        ):
            self.mutations += 1
            node.value = ast.Constant(0)
        return node


def load_cli_mutant(operator: str):
    source = AUDIT_GATE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    transformer = CliMutator(operator)
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    if transformer.mutations != 1:
        raise AssertionError(
            f"{operator} expected exactly one CLI mutation, got {transformer.mutations}"
        )

    module = types.ModuleType(f"audit_gate_cli_mutant_{operator}")
    module.__file__ = str(AUDIT_GATE)
    exec(compile(tree, str(AUDIT_GATE), "exec"), module.__dict__)
    return module


def run_main(module, argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with (
        mock.patch.object(module.sys, "argv", argv),
        contextlib.redirect_stdout(stdout),
        contextlib.redirect_stderr(stderr),
    ):
        code = module.main()
    return code, stdout.getvalue(), stderr.getvalue()


class CliMutationCanaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory_fixture = json.loads(
            sabotage.INVENTORY_FIXTURE.read_text(encoding="utf-8")
        )
        original = sabotage.gate
        sabotage.gate = real_gate
        try:
            cls.artifacts = sabotage.pristine_workflow(
                "simple",
                cls.inventory_fixture,
            )
        finally:
            sabotage.gate = original

    def write_workflow(self, root: Path, *, tamper_context=False) -> list[str]:
        audit = root / "audit.json"
        semantic = root / "semantic.json"
        context = root / "audit-context.md"
        checks = root / "module-checks.json"

        audit.write_text(
            json.dumps(self.artifacts["audit"]),
            encoding="utf-8",
        )
        semantic.write_text(
            json.dumps(self.artifacts["semantic"]),
            encoding="utf-8",
        )
        context_text = self.artifacts["context"]
        if tamper_context:
            context_text += "\nTAMPERED\n"
        context.write_text(context_text, encoding="utf-8")
        checks.write_text(
            json.dumps(self.artifacts["module_checks"]),
            encoding="utf-8",
        )

        return [
            "audit_gate.py",
            str(audit),
            "--semantic-route",
            str(semantic),
            "--context-bundle",
            str(context),
            "--module-checks",
            str(checks),
            "--check",
        ]

    def test_cli_mutation_surface_is_exact(self):
        observed = {
            "discard_validate_gate_errors",
            "ignore_nonempty_errors",
            "load_failure_returns_success",
        }
        self.assertEqual(observed, REQUIRED_CLI_MUTATIONS)
        for operator in sorted(REQUIRED_CLI_MUTATIONS):
            load_cli_mutant(operator)

    def test_cli_cannot_discard_or_ignore_gate_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            argv = self.write_workflow(Path(tmp), tamper_context=True)
            real_code, _, real_stderr = run_main(real_gate, argv)
            self.assertNotEqual(real_code, 0)
            self.assertIn("FAIL:", real_stderr)

            for operator in [
                "discard_validate_gate_errors",
                "ignore_nonempty_errors",
            ]:
                with self.subTest(operator=operator):
                    mutant = load_cli_mutant(operator)
                    mutant_code, _, _ = run_main(mutant, argv)
                    self.assertEqual(
                        mutant_code,
                        0,
                        f"{operator} did not weaken the CLI as intended",
                    )

    def test_cli_load_failure_cannot_be_reclassified_as_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing-ledger.json"
            argv = ["audit_gate.py", str(missing), "--check"]

            real_code, _, real_stderr = run_main(real_gate, argv)
            self.assertNotEqual(real_code, 0)
            self.assertIn("FAIL:", real_stderr)

            mutant = load_cli_mutant("load_failure_returns_success")
            mutant_code, _, mutant_stderr = run_main(mutant, argv)
            self.assertEqual(mutant_code, 0)
            self.assertIn("FAIL:", mutant_stderr)


if __name__ == "__main__":
    unittest.main()
