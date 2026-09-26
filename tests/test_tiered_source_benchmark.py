import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "tiered-source-40"
CASES = BENCH / "cases.json"
SUMMARY = BENCH / "summarize.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


summarize = load_module("tiered_source_summary", SUMMARY)


class TieredSourceBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CASES.read_text(encoding="utf-8"))

    def test_manifest_is_exactly_ten_domains_by_four_tiers(self):
        self.assertEqual(summarize.validate(self.data), [])
        self.assertEqual(len(self.data["cases"]), 40)
        self.assertEqual(len(set(x["domain"] for x in self.data["cases"])), 10)

    def test_tier_is_metadata_not_quality_prior(self):
        self.assertIn("never an evidence-quality prior", self.data["purpose"])
        low = [x for x in self.data["cases"] if x["tier"] == "low_attention_nontraditional"]
        self.assertEqual(len(low), 10)
        self.assertTrue(any(x["narrow_claim_support"] == "sufficient" for x in low))
        flagship = [x for x in self.data["cases"] if x["tier"] == "flagship_high_attention"]
        self.assertTrue(all(x["broad_claim_support"] != "sufficient" for x in flagship))

    def test_low_attention_tier_is_not_synonymous_with_blog(self):
        low = [x for x in self.data["cases"] if x["tier"] == "low_attention_nontraditional"]
        kinds = {x["source_kind"] for x in low}
        self.assertTrue(any("preprint" in kind for kind in kinds))
        self.assertTrue(any("blog" in kind for kind in kinds))
        self.assertTrue(any("pilot" in kind or "peer-reviewed" in kind for kind in kinds))
        self.assertIn("Matters Arising", kinds)

    def test_summary_preserves_prestige_blind_checks(self):
        result = summarize.summary(self.data)
        checks = result["prestige_blind_checks"]
        self.assertEqual(checks["flagship_broad_not_sufficient"], 10)
        self.assertEqual(checks["low_attention_narrow_sufficient"], 5)
        self.assertEqual(checks["low_attention_broad_insufficient_or_unclear"], 6)


if __name__ == "__main__":
    unittest.main()
