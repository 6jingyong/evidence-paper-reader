import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "claim-selection-12"
SPECS = BENCH / "case_specs.json"
EXPECTATIONS = BENCH / "reference_expectations.json"
GENERATOR = BENCH / "generate_packets.py"
SCORER = BENCH / "score.py"
RESPONSE_FORMAT = BENCH / "response-format.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


generate = load_module("claim_selection_generate", GENERATOR)
score_mod = load_module("claim_selection_score", SCORER)


class ClaimSelectionBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = json.loads(SPECS.read_text(encoding="utf-8"))
        cls.expectations = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))

    def test_exactly_twelve_cases(self):
        self.assertEqual(len(self.specs["cases"]), 12)
        self.assertEqual(
            {x["case_id"] for x in self.specs["cases"]},
            {x["case_id"] for x in self.expectations["cases"]},
        )

    def test_packets_do_not_leak_reference_roles(self):
        for case in self.specs["cases"]:
            packet = generate.shuffled_case(case, self.specs["seed"])
            rendered = generate.render(packet)
            self.assertNotIn("required", rendered.lower())
            self.assertNotIn("forbidden", rendered.lower())
            self.assertNotIn("silent_narrowing", rendered.lower())
            self.assertEqual(
                {x["id"] for x in packet["candidate_claims"]},
                {x["id"] for x in case["candidates"]},
            )

    def test_public_response_format_is_answer_neutral(self):
        contract = RESPONSE_FORMAT.read_text(encoding="utf-8")
        self.assertNotIn('"CS01"', contract)
        for candidate_id in ["K1", "K2", "K3", "K4", "K5"]:
            self.assertNotIn(f'"{candidate_id}"', contract)

    def test_cfd_case_separates_source_claims_from_auditor_diagnosis(self):
        case = next(x for x in self.specs["cases"] if x["case_id"] == "CS06")
        candidates = {x["id"]: x["text"] for x in case["candidates"]}
        expectation = next(
            x for x in self.expectations["cases"] if x["case_id"] == "CS06"
        )
        required_text = "\n".join(candidates[cid] for cid in expectation["required"])
        self.assertNotIn("used in both calibration and evaluation", required_text.lower())
        self.assertIn("CFD-derived targets", candidates["K2"])
        self.assertIn("independent real-world measurement accuracy", candidates["K4"])

    def _perfect_responses(self):
        responses = {}
        exp_by_case = {x["case_id"]: x for x in self.expectations["cases"]}
        for case in self.specs["cases"]:
            exp = exp_by_case[case["case_id"]]
            if exp["viability"] == "auditable":
                selected = list(exp["required"])
                for candidate in exp["optional"]:
                    if len(selected) >= 3:
                        break
                    selected.append(candidate)
            elif exp["viability"] == "partially auditable":
                selected = list(exp["required"])
            else:
                selected = []
            responses[case["case_id"]] = {
                "case_id": case["case_id"],
                "evidence_viability": exp["viability"],
                "selected_claim_ids": selected,
                "reason": "Synthetic reference-consistent response.",
            }
        return responses

    def test_perfect_responses_score_cleanly(self):
        result = score_mod.score(self._perfect_responses(), self.expectations)
        self.assertEqual(result["required_claim_recall"], 1.0)
        self.assertEqual(result["forbidden_selection_rate"], 0.0)
        self.assertEqual(result["silent_narrowing_rate"], 0.0)
        self.assertEqual(result["viability_accuracy"], 1.0)
        self.assertEqual(result["claim_count_violations"], 0)

    def test_silent_narrowing_is_detected_even_when_narrow_claim_is_true(self):
        responses = self._perfect_responses()
        # CS01 requires the strong headline claim K2 as well as its narrower
        # associational result K1. Dropping K2 while retaining K1 is silent
        # narrowing, not a successful evidence-aware rewrite.
        responses["CS01"]["selected_claim_ids"] = ["K1", "K5", "K3"]
        result = score_mod.score(responses, self.expectations)
        self.assertGreater(result["silent_narrowing_rate"], 0.0)
        self.assertLess(result["required_claim_recall"], 1.0)
        self.assertGreater(result["forbidden_selection_rate"], 0.0)

    def test_non_auditable_cases_require_zero_selected_claims(self):
        responses = self._perfect_responses()
        responses["CS09"]["selected_claim_ids"] = ["K3"]
        result = score_mod.score(responses, self.expectations)
        self.assertEqual(result["claim_count_violations"], 1)

    def test_partially_auditable_case_can_select_one_claim(self):
        responses = self._perfect_responses()
        self.assertEqual(responses["CS11"]["selected_claim_ids"], ["K1"])
        result = score_mod.score(responses, self.expectations)
        row = next(x for x in result["cases"] if x["case_id"] == "CS11")
        self.assertFalse(row["claim_count_violation"])


if __name__ == "__main__":
    unittest.main()
