import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "metadata-halo-12"
SPECS = BENCH / "packet_specs.json"
EXPECTATIONS = BENCH / "reference_expectations.json"
GENERATOR = BENCH / "generate_packets.py"
SCORER = BENCH / "score_pairs.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


generate = load_module("metadata_halo_generate", GENERATOR)
score_pairs = load_module("metadata_halo_score", SCORER)


class MetadataHaloBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = json.loads(SPECS.read_text(encoding="utf-8"))
        cls.expectations = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))

    def test_exactly_twelve_balanced_cases(self):
        cases = self.specs["cases"]
        self.assertEqual(len(cases), 12)
        high = [c for c in cases if "flagship/high-attention" in c["metadata"]["attention"]]
        low = [c for c in cases if "flagship/high-attention" not in c["metadata"]["attention"]]
        self.assertEqual(len(high), 6)
        self.assertEqual(len(low), 6)

    def test_hidden_and_visible_packets_have_identical_scientific_payload(self):
        for case in self.specs["cases"]:
            with self.subTest(case=case["case_id"]):
                hidden = generate.packet(case, "hidden", self.specs["seed"])
                visible = generate.packet(case, "visible", self.specs["seed"])
                self.assertEqual(generate.validate_pair(hidden, visible), [])
                self.assertEqual(
                    hidden["scientific_content_hash"],
                    visible["scientific_content_hash"],
                )
                hidden_text = generate.render_markdown(hidden)
                visible_text = generate.render_markdown(visible)
                self.assertNotIn(case["metadata"]["title"], hidden_text)
                self.assertNotIn(case["metadata"]["venue"], hidden_text)
                self.assertNotIn("condition:", hidden_text.lower())
                self.assertNotIn("metadata withheld", hidden_text.lower())
                self.assertIn(case["metadata"]["title"], visible_text)
                self.assertIn(case["metadata"]["venue"], visible_text)

    def _manifest_and_responses(self):
        manifest = []
        responses = {}
        exp = {x["case_id"]: x for x in self.expectations["cases"]}
        severity = {
            "sufficient": ("none", False),
            "partial": ("moderate", True),
            "insufficient": ("strong", True),
            "unclear": ("strong", True),
        }

        for case in self.specs["cases"]:
            for condition in ["hidden", "visible"]:
                packet = generate.packet(case, condition, self.specs["seed"])
                manifest.append({
                    "packet_id": packet["packet_id"],
                    "case_id": case["case_id"],
                    "condition": condition,
                    "attention": case["metadata"]["attention"],
                    "source_kind": case["metadata"]["source_kind"],
                    "scientific_content_hash": packet["scientific_content_hash"],
                })
                anchors = []
                for anchor_id in ["A1", "A2", "A3"]:
                    support = exp[case["case_id"]]["anchors"][anchor_id]
                    downweight, follow_up = severity[support]
                    anchors.append({
                        "id": anchor_id,
                        "support_level": support,
                        "downweight": downweight,
                        "follow_up_required": follow_up,
                        "reason": "Reference-consistent synthetic response.",
                    })
                responses[packet["packet_id"]] = {
                    "packet_id": packet["packet_id"],
                    "scope_status": exp[case["case_id"]]["scope_status"],
                    "anchors": anchors,
                    "requested_follow_up": [],
                    "overall_note": "Synthetic test response.",
                }
        return manifest, responses

    def test_scorer_reports_zero_metadata_effect_for_identical_responses(self):
        manifest, responses = self._manifest_and_responses()
        result = score_pairs.score(responses, self.expectations, manifest)
        self.assertEqual(result["pair_count"], 12)
        self.assertEqual(result["anchor_count"], 36)
        self.assertEqual(result["exact_support_match_rate"], 1.0)
        self.assertEqual(result["scope_flips"], 0)
        self.assertEqual(result["support_directions"].get("same"), 36)
        self.assertEqual(result["reference_accuracy"]["hidden"], 1.0)
        self.assertEqual(result["reference_accuracy"]["visible"], 1.0)

    def test_scorer_separates_positive_and_negative_prestige_directions(self):
        manifest, responses = self._manifest_and_responses()
        by_case = {}
        for row in manifest:
            by_case.setdefault(row["case_id"], {})[row["condition"]] = row

        # High-attention visible packet becomes more permissive on A2.
        high_id = by_case["MH01"]["visible"]["packet_id"]
        responses[high_id]["anchors"][1]["support_level"] = "sufficient"
        responses[high_id]["anchors"][1]["downweight"] = "none"
        responses[high_id]["anchors"][1]["follow_up_required"] = False

        # Low-attention visible packet becomes more skeptical on A1.
        low_id = by_case["MH02"]["visible"]["packet_id"]
        responses[low_id]["anchors"][0]["support_level"] = "partial"
        responses[low_id]["anchors"][0]["downweight"] = "moderate"
        responses[low_id]["anchors"][0]["follow_up_required"] = True

        result = score_pairs.score(responses, self.expectations, manifest)
        high = result["group_effects"]["flagship_high_attention"]
        low = result["group_effects"]["low_attention_nontraditional"]
        self.assertEqual(high["visible_more_permissive"], 1)
        self.assertEqual(low["visible_more_skeptical"], 1)
        self.assertLess(high["net_downweight_delta_visible_minus_hidden"], 0)
        self.assertGreater(low["net_downweight_delta_visible_minus_hidden"], 0)

    def test_reference_expectations_never_enter_generated_packets(self):
        expectation_text = EXPECTATIONS.read_text(encoding="utf-8")
        for case in self.specs["cases"]:
            hidden = generate.render_markdown(
                generate.packet(case, "hidden", self.specs["seed"])
            )
            visible = generate.render_markdown(
                generate.packet(case, "visible", self.specs["seed"])
            )
            self.assertNotIn("reference_expectations", hidden)
            self.assertNotIn("reference_expectations", visible)
            self.assertNotEqual(hidden, expectation_text)
            self.assertNotEqual(visible, expectation_text)


if __name__ == "__main__":
    unittest.main()
