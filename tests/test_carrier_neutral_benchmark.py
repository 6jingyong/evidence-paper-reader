import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "carrier-neutral-12"
CATALOG = ROOT / "validation-runs" / "real-papers" / "evidence-catalog.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


generator = load_module("carrier_generator", BENCH / "generate_packets.py")
runner = load_module("carrier_runner", BENCH / "run_reviewer.py")
scorer = load_module("carrier_scorer", BENCH / "score_carrier.py")


def valid_cn01():
    claims = []
    edges = []
    levels = ["sufficient", "sufficient", "insufficient"]
    inference = ["direct-result", "direct-result", "generalization"]
    statuses = ["direct", "direct", "unsupported"]
    relations = ["supports", "supports", "mixed"]
    for i in range(1, 4):
        node = f"E{i}"
        claims.append({
            "content": f"Claim {i} from the supplied datasheet.",
            "claim_type": "observational" if i < 3 else "generality",
            "conclusion_strength": "medium" if i < 3 else "strong",
            "evidence_nodes": [node],
            "evidence_relations": [{
                "evidence_node": node,
                "relation": relations[i - 1],
                "reason": "The listed source fact bears on this claim at its stated scope.",
            }],
            "upstream_claims": [],
            "support_level": levels[i - 1],
            "source_location": f"Claim {i} sentence",
            "reason": "The disclosed evidence reaches this bounded judgment.",
        })
        edges.append({
            "edge_id": f"R{i}",
            "target_claim": i,
            "evidence_nodes": [node],
            "upstream_claims": [],
            "inference_type": inference[i - 1],
            "reasoning_status": statuses[i - 1],
            "added_reach": (
                "none"
                if statuses[i - 1] == "direct"
                else "Extends two local measurements to universal deployment suitability."
            ),
            "assumptions": [],
        })
    return {
        "case_id": "CN01",
        "evidence_viability": "auditable",
        "viability_flags": [],
        "claims": claims,
        "reasoning_edges": edges,
        "reader_conclusion": "The datasheet supports two local measurements but not universal suitability.",
    }


class CarrierNeutralBenchmarkTests(unittest.TestCase):
    def test_case_and_expectation_sets_match_exactly(self):
        cases = generator.load_cases()
        expected = scorer.load_expectations()
        self.assertEqual(len(cases), 12)
        self.assertEqual(
            {case["case_id"] for case in cases},
            set(expected),
        )
        self.assertGreaterEqual(
            len({case["carrier"] for case in cases}),
            10,
        )

    def test_generated_packets_do_not_leak_hidden_expectations(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = generator.generate(Path(tmp))
            self.assertEqual(len(paths), 12)
            hidden = (BENCH / "reference_expectations.json").read_text(
                encoding="utf-8"
            )
            for path in paths:
                packet = path.read_text(encoding="utf-8")
                self.assertNotIn("reference_expectations", packet)
                self.assertNotIn("allowed_inference", packet)
                self.assertNotIn("full_reference_match", packet)
                self.assertNotEqual(packet, hidden)

    def test_valid_response_shape_and_reference_match(self):
        response = valid_cn01()
        runner.validate_response_data(response, "CN01")
        expected = scorer.load_expectations()["CN01"]
        scored = scorer.score_case("CN01", response, expected)
        self.assertTrue(scored["hard_pass"])
        self.assertTrue(scored["full_reference_match"])
        self.assertEqual(scored["support"]["pass_rate"], 1.0)
        self.assertEqual(scored["reasoning_inference"]["pass_rate"], 1.0)
        self.assertEqual(scored["evidence_direction"]["pass_rate"], 1.0)

    def test_wrong_support_is_detected_independently(self):
        response = valid_cn01()
        response["claims"][2]["support_level"] = "partial"
        response["reasoning_edges"][2]["reasoning_status"] = "qualified"
        runner.validate_response_data(response, "CN01")
        scored = scorer.score_case(
            "CN01",
            response,
            scorer.load_expectations()["CN01"],
        )
        self.assertTrue(scored["hard_pass"])
        self.assertLess(scored["support"]["pass_rate"], 1.0)
        self.assertFalse(scored["full_reference_match"])

    def test_wrong_inference_bridge_is_detected(self):
        response = valid_cn01()
        response["reasoning_edges"][2]["inference_type"] = "causal"
        runner.validate_response_data(response, "CN01")
        scored = scorer.score_case(
            "CN01",
            response,
            scorer.load_expectations()["CN01"],
        )
        self.assertLess(scored["reasoning_inference"]["pass_rate"], 1.0)
        self.assertFalse(scored["full_reference_match"])

    def test_wrong_evidence_direction_is_detected(self):
        response = valid_cn01()
        response["claims"][0]["evidence_relations"][0]["relation"] = "contextual"
        runner.validate_response_data(response, "CN01")
        scored = scorer.score_case(
            "CN01",
            response,
            scorer.load_expectations()["CN01"],
        )
        self.assertLess(scored["evidence_direction"]["pass_rate"], 1.0)
        self.assertFalse(scored["full_reference_match"])

    def test_non_auditable_marketing_case_requires_empty_graph(self):
        response = {
            "case_id": "CN03",
            "evidence_viability": "non-auditable",
            "viability_flags": ["promotional-asymmetry"],
            "claims": [],
            "reasoning_edges": [],
            "reader_conclusion": "The page exposes claims but no reconstructable evidence chain.",
        }
        runner.validate_response_data(response, "CN03")
        scored = scorer.score_case(
            "CN03",
            response,
            scorer.load_expectations()["CN03"],
        )
        self.assertTrue(scored["hard_pass"])
        self.assertTrue(scored["full_reference_match"])

    def test_synthetic_carriers_do_not_enter_real_source_registry(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        ids = {row["evidence_id"] for row in catalog["entries"]}
        for i in range(1, 13):
            self.assertNotIn(f"CN{i:02d}", ids)


if __name__ == "__main__":
    unittest.main()
