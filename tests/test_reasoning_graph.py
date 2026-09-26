import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SKILL = ROOT / "evidence-paper-reader"
SCRIPTS = SKILL / "scripts"
REFS = SKILL / "references"
RUN_ROOT = ROOT / "validation-runs" / "real-papers"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


render = load_module("reasoning_render", SCRIPTS / "render_audit.py")
gate = load_module("reasoning_gate", SCRIPTS / "audit_gate.py")
markdown = load_module("reasoning_markdown", SCRIPTS / "validate_audit.py")
ALLOWED = markdown.evidence_labels((REFS / "evidence-types.md").read_text(encoding="utf-8"))


def v2_ledger():
    data = copy.deepcopy(render.TEMPLATE)
    data["ledger_schema_version"] = 2
    for claim in data["claims"]:
        claim["support"].pop("evidence_relations", None)
    data["paper_type"] = "controlled empirical study"
    data["reader_conclusion"] = "Three bounded claims are separated from their inferential reach."
    for index, claim in enumerate(data["claims"], start=1):
        claim["content"] = f"Bounded claim {index}."
        claim["support"]["evidence_type"] = ["direct experiment"]
        claim["support"]["source_location"] = f"Results {index}"
        claim["support"]["support_level"] = "sufficient"
        claim["support"]["reason"] = "The listed result supports this bounded claim."
    data["usable"] = {
        "results": "The bounded results are usable.",
        "methods_or_design": "The disclosed design is inspectable.",
        "materials_or_documentation": "The result locations are documented.",
    }
    data["downweight"] = {
        "worth_noticing": "Broader reach is not needed for these claims.",
        "cautious_or_ignore": "Do not extend beyond the stated setting.",
    }
    data["value_breakdown"] = {
        "result": "high",
        "method": "medium",
        "theory_or_insight": "medium",
        "research_design": "medium",
        "material_or_documentation": "high",
    }
    data["uncertainty_and_follow_up"] = "External transfer remains open."
    return data


class ReasoningGraphTests(unittest.TestCase):
    def test_reasoning_reference_is_part_of_normal_context(self):
        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        core = (REFS / "core-contract.md").read_text(encoding="utf-8")
        reasoning = (REFS / "reasoning-graph.md").read_text(encoding="utf-8")
        context = (SCRIPTS / "build_context.py").read_text(encoding="utf-8")

        self.assertIn("references/reasoning-graph.md", skill)
        self.assertIn("Reasoning edges", core)
        self.assertIn("compact audit artifact, not hidden model reasoning", reasoning)
        self.assertIn('"reasoning-graph.md"', context)

    def test_valid_v2_graph_passes_renderer_and_independent_guard(self):
        data = v2_ledger()
        self.assertEqual(render.validate_ledger(data), [])
        self.assertEqual(gate.validate_reasoning_closure(data), [])

        rendered = render.render(data)
        self.assertIn("- reasoning edges: R1", rendered)
        self.assertIn("- R1 inputs: evidence=E1; upstream=none", rendered)
        self.assertIn("- R1 reasoning status: direct", rendered)
        self.assertEqual(markdown.validate(rendered, ALLOWED), [])

    def test_v1_ledger_remains_backward_compatible(self):
        data = v2_ledger()
        data.pop("ledger_schema_version")
        data.pop("reasoning_edges")
        self.assertEqual(render.validate_ledger(data), [])
        self.assertEqual(gate.validate_reasoning_closure(data), [])

    def test_v2_cannot_omit_reasoning_graph(self):
        data = v2_ledger()
        data.pop("reasoning_edges")
        renderer_errors = render.validate_ledger(data)
        guard_errors = gate.validate_reasoning_closure(data)
        self.assertTrue(
            any("require a non-empty reasoning_edges" in error for error in renderer_errors),
            renderer_errors,
        )
        self.assertTrue(guard_errors)

    def test_reasoning_cannot_invent_evidence_input(self):
        data = v2_ledger()
        data["reasoning_edges"][0]["evidence_nodes"] = ["E999"]
        renderer_errors = render.validate_ledger(data)
        guard_errors = gate.validate_reasoning_closure(data)
        self.assertTrue(
            any("subset of target claim evidence_nodes" in error for error in renderer_errors),
            renderer_errors,
        )
        self.assertTrue(
            any("do not exactly match claim evidence_nodes" in error for error in guard_errors),
            guard_errors,
        )

    def test_reasoning_must_cover_upstream_claim_inputs(self):
        data = v2_ledger()
        data["claims"][2]["support"]["upstream_claims"] = [1]
        renderer_errors = render.validate_ledger(data)
        guard_errors = gate.validate_reasoning_closure(data)
        self.assertTrue(
            any("cover exactly the claim upstream_claims" in error for error in renderer_errors),
            renderer_errors,
        )
        self.assertTrue(
            any("upstream inputs do not exactly match" in error for error in guard_errors),
            guard_errors,
        )

    def test_partial_support_cannot_hide_all_supported_edges(self):
        data = v2_ledger()
        data["claims"][2]["support"]["support_level"] = "partial"
        data["reasoning_edges"][2]["reasoning_status"] = "supported"
        data["reasoning_edges"][2]["added_reach"] = "A bounded comparison is inferred."
        renderer_errors = render.validate_ledger(data)
        guard_errors = gate.validate_reasoning_closure(data)
        self.assertTrue(
            any("partial support requires" in error for error in renderer_errors),
            renderer_errors,
        )
        self.assertTrue(
            any("partial support lacks" in error for error in guard_errors),
            guard_errors,
        )

    def test_insufficient_support_requires_unsupported_edge(self):
        data = v2_ledger()
        data["claims"][1]["support"]["support_level"] = "insufficient"
        data["reasoning_edges"][1]["reasoning_status"] = "qualified"
        data["reasoning_edges"][1]["added_reach"] = "The evidence reaches only a narrower claim."
        renderer_errors = render.validate_ledger(data)
        guard_errors = gate.validate_reasoning_closure(data)
        self.assertTrue(
            any("insufficient support requires" in error for error in renderer_errors),
            renderer_errors,
        )
        self.assertTrue(
            any("insufficient support lacks" in error for error in guard_errors),
            guard_errors,
        )

    def test_direct_edge_cannot_claim_added_reach(self):
        data = v2_ledger()
        data["reasoning_edges"][0]["added_reach"] = "Generalizes to a new population."
        errors = render.validate_ledger(data)
        self.assertTrue(
            any("direct reasoning must use added_reach 'none'" in error for error in errors),
            errors,
        )

    def test_real_cases_preserve_distinct_multi_edge_bridges(self):
        cases = {
            "mathematical-beauty-2014": (
                RUN_ROOT
                / "2026-09-26-round-01"
                / "mathematical-beauty-2014"
                / "ledger.json"
            ),
            "gautret-hcq-2020": (
                RUN_ROOT
                / "2026-09-26-round-02"
                / "gautret-hcq-2020"
                / "ledger.json"
            ),
            "acc-dic-2021": (
                RUN_ROOT
                / "2026-09-26-round-01"
                / "acc-dic-2021"
                / "ledger.json"
            ),
        }
        ledgers = {
            name: json.loads(path.read_text(encoding="utf-8"))
            for name, path in cases.items()
        }

        beauty_c3 = [
            edge
            for edge in ledgers["mathematical-beauty-2014"]["reasoning_edges"]
            if edge["target_claim"] == 3
        ]
        self.assertEqual(
            {edge["inference_type"] for edge in beauty_c3},
            {"proxy-to-construct", "generalization"},
        )
        self.assertTrue(
            all(edge["reasoning_status"] == "unsupported" for edge in beauty_c3)
        )

        gautret_c3 = [
            edge
            for edge in ledgers["gautret-hcq-2020"]["reasoning_edges"]
            if edge["target_claim"] == 3
        ]
        self.assertEqual(len(gautret_c3), 3)
        self.assertEqual(
            [edge["inference_type"] for edge in gautret_c3].count("causal"),
            2,
        )
        self.assertIn(
            "statistical-inference",
            {edge["inference_type"] for edge in gautret_c3},
        )
        self.assertTrue(
            all(edge["reasoning_status"] == "unsupported" for edge in gautret_c3)
        )

        acc_c3 = [
            edge
            for edge in ledgers["acc-dic-2021"]["reasoning_edges"]
            if edge["target_claim"] == 3
        ]
        self.assertEqual(len(acc_c3), 2)
        self.assertTrue(
            all(edge["inference_type"] == "generalization" for edge in acc_c3)
        )
        self.assertTrue(
            all(edge["reasoning_status"] == "qualified" for edge in acc_c3)
        )

    def test_all_source_backed_ledgers_are_v3_and_reasoning_closed(self):
        ledgers = []
        for round_root in sorted(RUN_ROOT.glob("*-round-*")):
            manifest = json.loads(
                (round_root / "manifest.json").read_text(encoding="utf-8")
            )
            for case in manifest["cases"]:
                path = round_root / case["id"] / "ledger.json"
                ledgers.append((case["id"], json.loads(path.read_text(encoding="utf-8"))))

        self.assertGreaterEqual(len(ledgers), 10)
        for case_id, data in ledgers:
            with self.subTest(case_id=case_id):
                self.assertEqual(data.get("ledger_schema_version"), 4)
                self.assertEqual(render.validate_ledger(data), [])
                self.assertEqual(gate.validate_reasoning_closure(data), [])
                self.assertEqual(gate.validate_evidence_relation_closure(data), [])
                if data["evidence_viability"] == "non-auditable":
                    self.assertEqual(data.get("reasoning_edges"), [])
                else:
                    self.assertTrue(data.get("reasoning_edges"))


if __name__ == "__main__":
    unittest.main()
