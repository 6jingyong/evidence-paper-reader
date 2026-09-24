import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "router-adversarial-24"
SPECS = BENCH / "case_specs.json"
SCORE_SCRIPT = BENCH / "score.py"
LEXICAL_SCRIPT = ROOT / "evidence-paper-reader" / "scripts" / "suggest_modules.py"
MERGE_SCRIPT = ROOT / "evidence-paper-reader" / "scripts" / "merge_route.py"
SEMANTIC_CARD = ROOT / "evidence-paper-reader" / "references" / "semantic-router-card.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


score_mod = load_module("router_adversarial_score", SCORE_SCRIPT)
lexical = load_module("router_adversarial_lexical", LEXICAL_SCRIPT)
merge_mod = load_module("router_adversarial_merge", MERGE_SCRIPT)


class RouterAdversarialBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(SPECS.read_text(encoding="utf-8"))["cases"]
        cls.by_id = {x["case_id"]: x for x in cls.cases}
        cls.semantic_card = SEMANTIC_CARD.read_text(encoding="utf-8")

    def test_benchmark_is_balanced_semantic_positive_and_lexical_decoy(self):
        self.assertEqual(len(self.cases), 24)
        self.assertEqual(sum(x["kind"] == "semantic_positive" for x in self.cases), 12)
        self.assertEqual(sum(x["kind"] == "lexical_decoy" for x in self.cases), 12)

    def test_benchmark_covers_all_primary_and_dependency_routes(self):
        covered = set()
        forbidden = set()
        for case in self.cases:
            covered.update(case["required_modules"])
            forbidden.update(case["forbidden_modules"])
        for module in [
            "figure-and-table-traps.md",
            "statistical-traps.md",
            "measurement-traps.md",
            "study-design-traps.md",
            "evidence-topology.md",
            "evidence-dependence.md",
            "claim-evidence-links.md",
            "follow-up-boundaries.md",
        ]:
            self.assertIn(module, covered | forbidden)

    def test_perfect_semantic_reference_scores_exactly(self):
        semantic = {
            case["case_id"]: score_mod.perfect_semantic(case)
            for case in self.cases
        }
        semantic_routes = {
            cid: score_mod.semantic_route(data)
            for cid, data in semantic.items()
        }
        semantic_score = score_mod.score_modules(self.cases, semantic_routes)
        merged_score = score_mod.score_modules(
            self.cases,
            score_mod.merged_routes(self.cases, semantic),
        )
        for result in [semantic_score, merged_score]:
            self.assertEqual(result["required_recall"], 1.0)
            self.assertEqual(result["forbidden_trigger_rate"], 0.0)
            self.assertEqual(result["inventory_accuracy"], 1.0)
            self.assertEqual(result["exact_case_rate"], 1.0)

    def test_semantic_required_can_add_a_keyword_hidden_route(self):
        case = self.by_id["RA02"]
        lexical_result = lexical.suggest_modules(case["claim"] + "\n" + case["text"])
        semantic = score_mod.perfect_semantic(case)
        merged = merge_mod.merge(lexical_result, semantic)
        self.assertIn("measurement-traps.md", merged["modules"])
        self.assertIn("measurement-traps.md", merged["semantic_modules_added"])

    def test_semantic_not_required_can_remove_an_incidental_lexical_hit(self):
        case = self.by_id["RA15"]
        lexical_result = lexical.suggest_modules(case["claim"] + "\n" + case["text"])
        lexical_names = {x["module"] for x in lexical_result["suggested"]}
        self.assertIn("evidence-topology.md", lexical_names)

        semantic = score_mod.perfect_semantic(case)
        merged = merge_mod.merge(lexical_result, semantic)
        self.assertNotIn("evidence-topology.md", merged["modules"])
        self.assertIn("evidence-topology.md", merged["lexical_only_modules_removed"])

    def test_semantic_unclear_preserves_a_lexical_hit(self):
        case = self.by_id["RA15"]
        lexical_result = lexical.suggest_modules(case["claim"] + "\n" + case["text"])
        semantic = score_mod.perfect_semantic(case)
        semantic["claims"][0]["routes"]["evidence-topology.md"] = "unclear"
        merged = merge_mod.merge(lexical_result, semantic)
        self.assertIn("evidence-topology.md", merged["modules"])
        self.assertEqual(
            merged["route_details"]["evidence-topology.md"]["basis"],
            "semantic unclear; lexical suggestion preserved",
        )

    def test_false_positive_guards_follow_retained_trap_modules(self):
        case = self.by_id["RA01"]
        lexical_result = lexical.suggest_modules(case["claim"] + "\n" + case["text"])
        merged = merge_mod.merge(lexical_result, score_mod.perfect_semantic(case))
        self.assertIn("statistical-traps.md", merged["modules"])
        self.assertIn("false-positive-guards.md", merged["modules"])

    def test_inventory_can_be_added_semantically_even_when_lexical_complexity_misses_it(self):
        case = self.by_id["RA10"]
        lexical_result = lexical.suggest_modules(case["claim"] + "\n" + case["text"])
        semantic = score_mod.perfect_semantic(case)
        merged = merge_mod.merge(lexical_result, semantic)
        self.assertTrue(merged["use_evidence_inventory"])
        self.assertEqual(merged["inventory_basis"], "semantic required")

    def test_lexical_router_exposes_semantic_confirmation_runtime(self):
        result = lexical.suggest_modules("A short descriptive result.")
        self.assertTrue(result["semantic_router_required"])
        self.assertEqual(result["semantic_router_card"], "semantic-router-card.md")
        self.assertEqual(result["merge_with"], "merge_route.py")

    def test_semantic_card_routes_relevance_not_keywords(self):
        for phrase in [
            "Do not route from keywords alone.",
            "required",
            "not_required",
            "unclear",
            "Do not require it merely because",
            "preserves a lexical hit",
        ]:
            self.assertIn(phrase, self.semantic_card)


if __name__ == "__main__":
    unittest.main()
