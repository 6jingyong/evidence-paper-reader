import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPTS = SKILL / "scripts"
AUDIT_GATE = SCRIPTS / "audit_gate.py"
EVIDENCE_TYPES = SKILL / "references" / "evidence-types.md"
INVENTORY_FIXTURE = (
    ROOT / "tests" / "inventory-fixtures" / "synthetic-duplicate-and-replication-inventory.json"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = load_module("sabotage_audit_gate", AUDIT_GATE)


def base_audit():
    def claim(content, node, *, level="sufficient", upstream=None):
        return {
            "content": content,
            "claim_type": "observational",
            "conclusion_strength": "medium",
            "support": {
                "evidence_type": ["direct experiment"],
                "evidence_provenance": "paper-local",
                "evidence_nodes": [node],
                "upstream_claims": upstream or [],
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
            claim("Claim three is supported in the tested setting.", "E3", level="partial"),
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


def semantic_for(audit, *, inventory_required=False):
    claims = []
    for index, claim in enumerate(audit["claims"], start=1):
        claims.append({
            "claim_id": f"C{index}",
            "claim_text": claim["content"],
            "routes": {
                name: "not_required"
                for name in gate.merge_route.ROUTES
            },
            "inventory": (
                "required"
                if inventory_required and index == 1
                else "not_required"
            ),
            "reason": "No optional methodological module is required for this compact fixture.",
        })
    return {"claims": claims}


def deterministic_artifacts(audit, *, inventory_required=False):
    semantic = semantic_for(audit, inventory_required=inventory_required)
    route = gate.build_context.recompute_route(semantic, lexical=None, router_text=None)
    context = gate.build_context.render_bundle(route)
    return semantic, route, context


def validate(audit, semantic, route, context, *, inventory=None, lexical=None, router_text=None):
    return gate.validate_gate(
        audit,
        semantic=semantic,
        lexical=lexical,
        route=route,
        inventory=inventory,
        evidence_types_text=EVIDENCE_TYPES.read_text(encoding="utf-8"),
        router_text=router_text,
        context_bundle=context,
    )


class SabotageGuardTests(unittest.TestCase):
    def test_ci_explicitly_runs_this_sabotage_suite(self):
        workflow = (ROOT / ".github" / "workflows" / "contract-tests.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("Run sabotage guard matrix", workflow)
        self.assertIn("test -f tests/test_sabotage_guards.py", workflow)
        self.assertIn("python tests/test_sabotage_guards.py -v", workflow)

    def test_clean_baseline_passes(self):
        audit = base_audit()
        semantic, route, context = deterministic_artifacts(audit)
        self.assertEqual(validate(audit, semantic, route, context), [])

    def test_artifact_sabotage_matrix_is_rejected(self):
        audit = base_audit()
        semantic, route, context = deterministic_artifacts(audit)

        cases = []

        drifted_semantic = copy.deepcopy(semantic)
        drifted_semantic["claims"][1]["claim_text"] = "A rewritten claim that was never routed."
        cases.append((
            "semantic claim drift",
            audit,
            drifted_semantic,
            route,
            context,
            "claim text/order must exactly match",
        ))

        forged_route = copy.deepcopy(route)
        forged_route["modules"].append("follow-up-boundaries.md")
        cases.append((
            "forged merged-route cache",
            audit,
            semantic,
            forged_route,
            context,
            "does not match deterministic recomputation",
        ))

        cases.append((
            "tampered generated context",
            audit,
            semantic,
            route,
            context + "\n<!-- injected shortcut -->\n",
            "does not match deterministic route materialization",
        ))

        bad_label = copy.deepcopy(audit)
        bad_label["claims"][0]["support"]["evidence_type"] = ["imaginary evidence"]
        cases.append((
            "uncontrolled evidence label",
            bad_label,
            semantic,
            route,
            context,
            "unknown evidence label",
        ))

        laundering = copy.deepcopy(audit)
        laundering["claims"][0]["support"]["support_level"] = "insufficient"
        laundering["claims"][1]["support"]["evidence_nodes"] = ["E1"]
        laundering["claims"][1]["support"]["upstream_claims"] = [1]
        laundering["claims"][1]["support"]["support_level"] = "sufficient"
        cases.append((
            "inference-chain laundering",
            laundering,
            semantic,
            route,
            context,
            "downstream claim cannot be sufficient without new evidence",
        ))

        for (
            name,
            mutated_audit,
            mutated_semantic,
            mutated_route,
            mutated_context,
            expected,
        ) in cases:
            with self.subTest(sabotage=name):
                errors = validate(
                    mutated_audit,
                    mutated_semantic,
                    mutated_route,
                    mutated_context,
                )
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_lexical_cache_sabotage_is_rejected(self):
        audit = base_audit()
        semantic = semantic_for(audit)
        semantic["claims"][0]["routes"]["measurement-traps.md"] = "unclear"
        router_text = "The sensor calibration was checked before analysis."
        exact_cache = gate.build_context.suggest_modules.suggest_modules(router_text)
        route = gate.build_context.recompute_route(
            semantic,
            exact_cache,
            router_text,
        )
        context = gate.build_context.render_bundle(route)

        forged_cache = copy.deepcopy(exact_cache)
        forged_cache["use_evidence_inventory"] = not exact_cache["use_evidence_inventory"]
        errors = validate(
            audit,
            semantic,
            route,
            context,
            lexical=forged_cache,
            router_text=router_text,
        )
        self.assertTrue(
            any("cached lexical route does not match deterministic recomputation" in x for x in errors),
            errors,
        )

    def test_inventory_cross_stage_sabotage_is_rejected(self):
        inventory = json.loads(INVENTORY_FIXTURE.read_text(encoding="utf-8"))
        audit = base_audit()
        for claim, item in zip(audit["claims"], inventory["claims"]):
            claim["content"] = item["content"]
        semantic, route, context = deterministic_artifacts(
            audit,
            inventory_required=True,
        )

        self.assertEqual(
            validate(
                audit,
                semantic,
                route,
                context,
                inventory=inventory,
            ),
            [],
        )

        unknown_node = copy.deepcopy(audit)
        unknown_node["claims"][1]["support"]["evidence_nodes"] = ["E9"]
        errors = validate(
            unknown_node,
            semantic,
            route,
            context,
            inventory=inventory,
        )
        self.assertTrue(any("evidence node E9 is not promoted" in x for x in errors), errors)

        false_independence = copy.deepcopy(audit)
        false_independence["claims"][0]["support"]["evidence_nodes"] = ["E1", "E2"]
        false_independence["claims"][0]["support"]["evidence_dependence"] = "independent convergence"
        errors = validate(
            false_independence,
            semantic,
            route,
            context,
            inventory=inventory,
        )
        self.assertTrue(
            any("independent convergence shares evidence unit(s): U1" in x for x in errors),
            errors,
        )

    def test_real_cli_wiring_accepts_valid_context_and_rejects_tampering(self):
        audit = base_audit()
        semantic, _, context = deterministic_artifacts(audit)

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
            self.assertIn(
                "does not match deterministic route materialization",
                sabotaged.stderr,
            )


if __name__ == "__main__":
    unittest.main()
