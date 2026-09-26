import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "blind-real-paper-10"
RUN_ROOT = ROOT / "validation-runs" / "real-papers"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


generator = load_module("blind_generator", BENCH / "generate_packets.py")
prepare = load_module("blind_prepare", BENCH / "prepare_review.py")
runner = load_module("blind_runner", BENCH / "run_reviewer.py")
scorer = load_module("blind_scorer", BENCH / "score_blind.py")


class BlindRealPaperBenchmarkTests(unittest.TestCase):
    def test_generated_packets_are_answer_key_free(self):
        index = generator.load_index()
        self.assertEqual(len(index["cases"]), 10)

        with tempfile.TemporaryDirectory() as tmp:
            paths = generator.generate(Path(tmp))
            self.assertEqual(len(paths), 10)
            by_id = {path.stem: path for path in paths}

            for case in index["cases"]:
                case_id = case["case_id"]
                packet = by_id[case_id].read_text(encoding="utf-8")
                lower = packet.lower()

                for term in generator.FORBIDDEN_PACKET_TERMS:
                    self.assertNotIn(term.lower(), lower, (case_id, term))

                case_root = RUN_ROOT / case["round_id"] / case_id
                ledger = json.loads(
                    (case_root / "ledger.json").read_text(encoding="utf-8")
                )
                for claim in ledger.get("claims", []):
                    self.assertNotIn(
                        claim["content"],
                        packet,
                        f"{case_id}: stored claim leaked into blind packet",
                    )

                source = json.loads(
                    (case_root / "source.json").read_text(encoding="utf-8")
                )
                for hidden_key in [
                    "integrity_note",
                    "later_context_note",
                    "publication_status",
                ]:
                    value = source.get(hidden_key)
                    if isinstance(value, str) and value:
                        self.assertNotIn(
                            value,
                            packet,
                            f"{case_id}: interpretive source metadata leaked",
                        )

    def test_prompt_contains_packet_but_no_answer_key_paths(self):
        packet = (
            "# Blind real-paper audit packet\n\n"
            "- case_id: demo\n"
            "- primary_source_url: https://example.com/paper\n"
        )
        prompt = prepare.render_prompt(
            packet,
            "source-packet.md",
            include_skill=False,
        )
        self.assertIn("case_id: demo", prompt)
        for forbidden in [
            "real-paper-judgment-baseline",
            "ledger.json",
            "regression_contract",
            "validation-runs/",
            "must_hold",
            "allowed_range",
        ]:
            self.assertNotIn(forbidden, prompt)

    def test_response_validator_requires_a_real_fresh_audit_shape(self):
        good = {
            "case_id": "demo",
            "evidence_viability": "auditable",
            "viability_flags": [],
            "claims": [
                {
                    "content": f"Source-facing claim {index}.",
                    "claim_type": "observational",
                    "conclusion_strength": "medium",
                    "evidence_nodes": [f"E{index}"],
                    "evidence_relations": [
                        {
                            "evidence_node": f"E{index}",
                            "relation": "supports",
                            "reason": "The evidence node bears on this bounded claim.",
                        }
                    ],
                    "upstream_claims": [],
                    "support_level": "partial",
                    "source_location": f"Results section {index}",
                    "reason": "The disclosed evidence supports only this bounded statement.",
                }
                for index in range(1, 4)
            ],
            "reasoning_edges": [
                {
                    "edge_id": f"R{index}",
                    "target_claim": index,
                    "evidence_nodes": [f"E{index}"],
                    "evidence_relations": [
                        {
                            "evidence_node": f"E{index}",
                            "relation": "supports",
                            "reason": "The evidence node bears on this bounded claim.",
                        }
                    ],
                    "upstream_claims": [],
                    "inference_type": "direct-result",
                    "reasoning_status": "qualified",
                    "added_reach": "The reported result supports only a narrower version of the claim.",
                    "assumptions": [],
                }
                for index in range(1, 4)
            ],
            "modules": ["statistical-traps.md"],
            "use_evidence_inventory": False,
            "reader_conclusion": "The paper supports bounded claims only.",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.json"
            path.write_text(json.dumps(good), encoding="utf-8")
            runner.validate_response(path, "demo")

            bad = dict(good)
            bad["claims"] = []
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.validate_response(path, "demo")

    def test_response_validator_rejects_reasoning_input_drift(self):
        response = {
            "case_id": "demo",
            "evidence_viability": "auditable",
            "viability_flags": [],
            "claims": [
                {
                    "content": f"Claim {index}.",
                    "claim_type": "observational",
                    "conclusion_strength": "medium",
                    "evidence_nodes": [f"E{index}"],
                    "evidence_relations": [
                        {
                            "evidence_node": f"E{index}",
                            "relation": "supports",
                            "reason": "The evidence node bears on this bounded claim.",
                        }
                    ],
                    "upstream_claims": [],
                    "support_level": "sufficient",
                    "source_location": f"Results {index}",
                    "reason": "Direct bounded result.",
                }
                for index in range(1, 4)
            ],
            "reasoning_edges": [
                {
                    "edge_id": f"R{index}",
                    "target_claim": index,
                    "evidence_nodes": [f"E{index}"],
                    "evidence_relations": [
                        {
                            "evidence_node": f"E{index}",
                            "relation": "supports",
                            "reason": "The evidence node bears on this bounded claim.",
                        }
                    ],
                    "upstream_claims": [],
                    "inference_type": "direct-result",
                    "reasoning_status": "direct",
                    "added_reach": "none",
                    "assumptions": [],
                }
                for index in range(1, 4)
            ],
            "modules": [],
            "use_evidence_inventory": False,
            "reader_conclusion": "Bounded results only.",
        }
        response["reasoning_edges"][0]["evidence_nodes"] = ["E999"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "demo.json"
            path.write_text(json.dumps(response), encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.validate_response(path, "demo")

    def test_claim_alignment_is_advisory_and_marks_low_similarity(self):
        ref = [
            {"content": "The intervention reduced the primary cardiovascular outcome."},
            {"content": "The intervention reduced all-cause mortality."},
        ]
        fresh = [
            {"content": "Randomized intensive treatment lowered the primary cardiovascular endpoint."},
            {"content": "Bananas are yellow."},
        ]
        pairs = scorer.best_alignment(ref, fresh)
        self.assertEqual(len(pairs), 2)
        similarities = sorted(pair["similarity"] for pair in pairs)
        self.assertLess(similarities[0], similarities[1])

    def test_hidden_tolerance_accepts_only_declared_support_drift(self):
        index = json.loads((BENCH / "case_index.json").read_text(encoding="utf-8"))
        case = next(
            item
            for item in index["cases"]
            if item["case_id"] == "attention-is-all-you-need-2017"
        )
        ledger, contract = scorer.load_case(case)
        response = {
            "case_id": case["case_id"],
            "evidence_viability": ledger["evidence_viability"],
            "viability_flags": ledger["viability_flags"],
            "claims": [
                {
                    "content": claim["content"],
                    "support_level": claim["support"]["support_level"],
                }
                for claim in ledger["claims"]
            ],
        }

        baseline = scorer.score_case(case, response, threshold=0.18)
        self.assertTrue(baseline["hard_invariants_pass"])
        self.assertEqual(
            baseline["support"]["within_tolerance_rate"],
            1.0,
        )

        tolerated = json.loads(json.dumps(response))
        tolerated["claims"][2]["support_level"] = "insufficient"
        tolerated_score = scorer.score_case(case, tolerated, threshold=0.18)
        self.assertEqual(
            tolerated_score["support"]["within_tolerance_rate"],
            1.0,
        )

        forbidden = json.loads(json.dumps(response))
        forbidden["claims"][2]["support_level"] = "sufficient"
        forbidden_score = scorer.score_case(case, forbidden, threshold=0.18)
        self.assertLess(
            forbidden_score["support"]["within_tolerance_rate"],
            1.0,
        )
        self.assertEqual(
            contract["allowed_range"]["support_levels"][2],
            ["partial", "insufficient"],
        )

    def test_source_integrity_hard_invariant_survives_blind_scoring(self):
        index = json.loads((BENCH / "case_index.json").read_text(encoding="utf-8"))
        case = next(
            item
            for item in index["cases"]
            if item["case_id"] == "surgisphere-hcq-2020"
        )
        good = {
            "case_id": case["case_id"],
            "evidence_viability": "non-auditable",
            "viability_flags": ["source-integrity-failure"],
            "claims": [],
        }
        scored = scorer.score_case(case, good, threshold=0.18)
        self.assertTrue(scored["hard_invariants_pass"])

        weak = dict(good)
        weak["evidence_viability"] = "auditable"
        weak["viability_flags"] = []
        weak["claims"] = [
            {
                "content": "The registry analysis reports an association.",
                "support_level": "sufficient",
            }
        ]
        scored = scorer.score_case(case, weak, threshold=0.18)
        self.assertFalse(scored["hard_invariants_pass"])


if __name__ == "__main__":
    unittest.main()
