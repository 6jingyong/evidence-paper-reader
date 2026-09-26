import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
AUDIT_GATE = SKILL / "scripts" / "audit_gate.py"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"
MATRIX = ROOT / "tests" / "sabotage-matrix.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = load_module("sabotage_guard_gate", AUDIT_GATE)


def base_audit():
    def claim(content, node, level="sufficient"):
        return {
            "content": content,
            "claim_type": "observational",
            "conclusion_strength": "medium",
            "support": {
                "evidence_type": ["direct experiment"],
                "evidence_provenance": "paper-local",
                "evidence_nodes": [node],
                "upstream_claims": [],
                "evidence_dependence": "single-source",
                "source_location": "Results",
                "support_level": level,
                "reason": "The paper-local result directly addresses the bounded claim.",
                "external_dependency": "none",
            },
        }

    return {
        "scope_status": "in scope",
        "evidence_viability": "auditable",
        "viability_flags": [],
        "paper_type": "controlled empirical study",
        "reader_conclusion": "The bounded paper-local results are auditable.",
        "claims": [
            claim("Claim one is supported in the tested setting.", "E1"),
            claim("Claim two is supported in the tested setting.", "E2"),
            claim("Claim three is supported in the tested setting.", "E3", "partial"),
        ],
        "usable": {
            "results": "The bounded results are usable.",
            "methods_or_design": "The disclosed comparison is reusable.",
            "materials_or_documentation": "The relevant result locations are documented.",
        },
        "downweight": {
            "worth_noticing": "Some reach remains bounded to the study setting.",
            "cautious_or_ignore": "Do not extend the findings beyond the tested setting without evidence.",
        },
        "value_breakdown": {
            "result": "high",
            "method": "medium",
            "theory_or_insight": "medium",
            "research_design": "medium",
            "material_or_documentation": "high",
        },
        "uncertainty_and_follow_up": "External transfer remains uncertain.",
    }


def semantic_for(audit):
    return {
        "claims": [
            {
                "claim_id": f"C{index}",
                "claim_text": claim["content"],
                "routes": {
                    name: "not_required"
                    for name in gate.merge_route.ROUTES
                },
                "inventory": "not_required",
                "reason": "No optional methodological module is required for this compact fixture.",
            }
            for index, claim in enumerate(audit["claims"], start=1)
        ]
    }


def pristine():
    audit = base_audit()
    semantic = semantic_for(audit)
    route = gate.build_context.recompute_route(
        semantic,
        lexical=None,
        router_text=None,
    )
    context = gate.build_context.render_bundle(route)
    return audit, semantic, route, context


class SabotageGuardCanaryTests(unittest.TestCase):
    def test_ci_and_matrix_pin_the_code_level_canary(self):
        workflow = (ROOT / ".github" / "workflows" / "contract-tests.yml").read_text(
            encoding="utf-8"
        )
        matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

        self.assertIn("Run sabotage guard matrix", workflow)
        self.assertIn("test -f tests/test_sabotage_guards.py", workflow)
        self.assertIn("python tests/test_sabotage_guards.py -v", workflow)
        self.assertEqual(
            set(matrix["code_canary_guards"]),
            {"G108", "G123", "G124", "G125", "G126", "G127", "G128", "G129"},
        )
        for guard in matrix["code_canary_guards"]:
            self.assertIn(guard, gate.CRITICAL_GUARDS)

    def test_g108_reference_materialization_failure_is_fail_closed(self):
        audit, semantic, route, context = pristine()

        with mock.patch.object(
            gate.build_context,
            "render_bundle",
            side_effect=ValueError("simulated routed-reference failure"),
        ):
            errors = gate.validate_gate(
                audit,
                semantic=semantic,
                lexical=None,
                route=route,
                inventory=None,
                evidence_types_text=EVIDENCE_TYPES.read_text(encoding="utf-8"),
                context_bundle=context,
            )

        self.assertTrue(
            any(error.startswith("[G108]") for error in errors),
            errors,
        )

    def test_real_cli_wiring_accepts_valid_context_and_rejects_tampering(self):
        audit, semantic, _, context = pristine()

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            audit_path = tmp / "audit.json"
            semantic_path = tmp / "semantic.json"
            context_path = tmp / "audit-context.md"
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            semantic_path.write_text(json.dumps(semantic), encoding="utf-8")
            context_path.write_text(context, encoding="utf-8")

            command = [
                sys.executable,
                str(AUDIT_GATE),
                str(audit_path),
                "--semantic-route",
                str(semantic_path),
                "--context-bundle",
                str(context_path),
                "--check",
            ]
            clean = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(clean.returncode, 0, clean.stderr)
            self.assertIn("PASS: audit passed the execution gate", clean.stdout)

            context_path.write_text(context + "\nTAMPERED\n", encoding="utf-8")
            sabotaged = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(sabotaged.returncode, 0)
            self.assertIn("[G109]", sabotaged.stderr)
            self.assertIn(
                "does not match deterministic route materialization",
                sabotaged.stderr,
            )


if __name__ == "__main__":
    unittest.main()
