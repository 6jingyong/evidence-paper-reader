import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "stability-crossdomain-8"
SPECS = BENCH / "case_specs.json"
GENERATOR = BENCH / "generate_runs.py"
SCORER = BENCH / "score_repeats.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


generate = load_module("stability_generate", GENERATOR)
score_mod = load_module("stability_score", SCORER)


class CrossDomainStabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = json.loads(SPECS.read_text(encoding="utf-8"))
        cls.cases = cls.specs["cases"]

    def test_eight_unique_domains_and_five_repeats(self):
        self.assertEqual(len(self.cases), 8)
        self.assertEqual(len({x["domain"] for x in self.cases}), 8)
        self.assertEqual(self.specs["repeats_per_case"], 5)

    def test_run_ids_are_unique_across_40_jobs(self):
        ids = []
        for case in self.cases:
            for repeat in range(1, self.specs["repeats_per_case"] + 1):
                ids.append(generate.packet_id(case["case_id"], repeat, self.specs["seed"]))
        self.assertEqual(len(ids), 40)
        self.assertEqual(len(set(ids)), 40)

    def _perfect_runs(self, case):
        ref = case["reference"]
        runs = []
        for _ in range(self.specs["repeats_per_case"]):
            selected = list(ref["required_claims"])
            support = [
                {"claim_id": cid, "support_level": ref["support"][cid]}
                for cid in selected
            ]
            runs.append({
                "case_id": case["case_id"],
                "evidence_viability": ref["viability"],
                "selected_claim_ids": selected,
                "modules": list(ref["modules_required"]),
                "use_evidence_inventory": ref["inventory"],
                "support": support,
                "note": "Synthetic reference-consistent run.",
            })
        return runs

    def test_perfect_repeats_are_fully_stable_and_reference_correct(self):
        per_case = {}
        for case in self.cases:
            runs = self._perfect_runs(case)
            for run in runs:
                self.assertEqual(score_mod.validate_response(run, case), [])
            row = score_mod.case_metrics(case, runs)
            per_case[case["case_id"]] = row
            for value in row["stability"].values():
                self.assertEqual(value, 1.0)
            self.assertEqual(row["reference"]["viability_accuracy"], 1.0)
            self.assertEqual(row["reference"]["required_claim_recall"], 1.0)
            self.assertEqual(row["reference"]["forbidden_claim_selection_rate"], 0.0)
            self.assertEqual(row["reference"]["required_module_recall"], 1.0)
            self.assertEqual(row["reference"]["unallowed_module_rate"], 0.0)
            self.assertEqual(row["reference"]["inventory_accuracy"], 1.0)
            self.assertEqual(row["reference"]["support_accuracy"], 1.0)

        aggregate = score_mod.aggregate(per_case)
        for value in aggregate["mean_layer_stability"].values():
            self.assertEqual(value, 1.0)
        self.assertEqual(aggregate["run_count"], 40)

    def test_optional_claim_omission_does_not_reduce_support_accuracy(self):
        case = next(x for x in self.cases if x["case_id"] == "ST01")
        runs = self._perfect_runs(case)
        row = score_mod.case_metrics(case, runs)
        self.assertEqual(row["reference"]["support_accuracy"], 1.0)

    def test_one_drifting_run_is_visible_at_the_correct_layers(self):
        case = next(x for x in self.cases if x["case_id"] == "ST04")
        runs = self._perfect_runs(case)
        drift = runs[-1]
        drift["evidence_viability"] = "partially auditable"
        drift["selected_claim_ids"] = ["K1", "K2", "K5"]
        drift["modules"] = ["measurement-traps.md", "statistical-traps.md"]
        drift["use_evidence_inventory"] = True
        drift["support"] = [
            {"claim_id": "K1", "support_level": "partial"},
            {"claim_id": "K2", "support_level": "partial"},
            {"claim_id": "K5", "support_level": "unclear"},
        ]
        self.assertEqual(score_mod.validate_response(drift, case), [])

        row = score_mod.case_metrics(case, runs)
        self.assertLess(row["stability"]["viability_pairwise_exact"], 1.0)
        self.assertLess(row["stability"]["claim_selection_pairwise_jaccard"], 1.0)
        self.assertLess(row["stability"]["routing_pairwise_jaccard"], 1.0)
        self.assertLess(row["stability"]["inventory_pairwise_exact"], 1.0)
        self.assertLess(row["stability"]["support_vector_pairwise_exact"], 1.0)
        self.assertLess(row["reference"]["required_claim_recall"], 1.0)
        self.assertLess(row["reference"]["required_module_recall"], 1.0)
        self.assertLess(row["reference"]["support_accuracy"], 1.0)

    def test_required_claims_remain_source_facing(self):
        by_id = {case["case_id"]: case for case in self.cases}
        banned_fragments = {
            "ST04": ["not fully independent"],
            "ST05": ["the evidence is repeated cross-sectional"],
            "ST06": ["mechanically coupled"],
            "ST07": ["provides direct local evidence"],
        }
        for case_id, fragments in banned_fragments.items():
            case = by_id[case_id]
            candidates = {x["id"]: x["text"].lower() for x in case["candidates"]}
            required_text = "\n".join(candidates[cid] for cid in case["reference"]["required_claims"])
            for fragment in fragments:
                self.assertNotIn(fragment, required_text)

        st05 = by_id["ST05"]
        st06 = by_id["ST06"]
        st07 = by_id["ST07"]
        st04 = by_id["ST04"]
        self.assertIn("1.4 times", next(x["text"] for x in st05["candidates"] if x["id"] == "K5"))
        self.assertIn("market depth", next(x["text"] for x in st06["candidates"] if x["id"] == "K3"))
        self.assertIn("body size", next(x["text"] for x in st07["candidates"] if x["id"] == "K4"))
        self.assertIn("calibration", next(x["text"].lower() for x in st04["candidates"] if x["id"] == "K2"))

    def test_validator_rejects_unknown_modules_and_claim_count_shortcuts(self):
        case = self.cases[0]
        run = self._perfect_runs(case)[0]
        run["modules"].append("made-up-module.md")
        errors = score_mod.validate_response(run, case)
        self.assertTrue(any("unknown module" in e for e in errors), errors)

        run = self._perfect_runs(case)[0]
        run["selected_claim_ids"] = ["K1", "K2"]
        run["support"] = [
            {"claim_id": "K1", "support_level": "sufficient"},
            {"claim_id": "K2", "support_level": "sufficient"},
        ]
        errors = score_mod.validate_response(run, case)
        self.assertTrue(any("3 to 5 claims" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
