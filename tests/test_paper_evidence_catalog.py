import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BUILDER = ROOT / "validation-runs" / "real-papers" / "build_evidence_catalog.py"
CATALOG = ROOT / "validation-runs" / "real-papers" / "evidence-catalog.json"
EVIDENCE = ROOT / "EVIDENCE.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


builder = load_module("paper_evidence_catalog", BUILDER)


class PaperEvidenceCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.rebuilt = builder.build()

    def test_catalog_exactly_matches_discovered_evidence(self):
        self.assertEqual(self.catalog, self.rebuilt)
        self.assertEqual(builder.errors(self.catalog), [])

    def test_generated_evidence_page_is_not_hand_maintained(self):
        self.assertEqual(
            EVIDENCE.read_text(encoding="utf-8"),
            builder.render(self.rebuilt),
        )

    def test_every_recorded_round_case_is_source_backed(self):
        catalog_ids = {
            row["evidence_id"]
            for row in self.catalog["entries"]
            if row["identity_status"] == "source-backed"
        }
        discovered = set()
        run_root = ROOT / "validation-runs" / "real-papers"
        for round_root in run_root.glob("*-round-*"):
            manifest = json.loads(
                (round_root / "manifest.json").read_text(encoding="utf-8")
            )
            discovered.update(case["id"] for case in manifest["cases"])
        self.assertEqual(catalog_ids, discovered)

    def test_blind_benchmark_cannot_introduce_unrecorded_paper(self):
        blind = json.loads(
            (
                ROOT
                / "benchmarks"
                / "blind-real-paper-10"
                / "case_index.json"
            ).read_text(encoding="utf-8")
        )
        source_backed = {
            row["evidence_id"]
            for row in self.catalog["entries"]
            if row["identity_status"] == "source-backed"
        }
        self.assertTrue(
            {case["case_id"] for case in blind["cases"]}.issubset(source_backed)
        )

    def test_legacy_entries_are_explicitly_lower_provenance(self):
        legacy = [
            row
            for row in self.catalog["entries"]
            if row["identity_status"] == "legacy-fixture"
        ]
        self.assertTrue(legacy)
        for row in legacy:
            self.assertEqual(row["source_url"], "")
            self.assertEqual(row["stable_id"], "")
            kinds = {surface["kind"] for surface in row["test_surfaces"]}
            self.assertIn("legacy-regression", kinds)
            self.assertNotIn("full-replay", kinds)

    def test_tiered_sources_are_fully_mapped_without_double_counting(self):
        tiered = json.loads(
            (
                ROOT
                / "benchmarks"
                / "tiered-source-40"
                / "cases.json"
            ).read_text(encoding="utf-8")
        )["cases"]
        self.assertEqual(len(tiered), 40)
        self.assertEqual(self.catalog["counts"]["tiered_source_cases"], 40)
        self.assertEqual(self.catalog["counts"]["benchmark_only_sources"], 38)

        by_surface_case = {}
        for row in self.catalog["entries"]:
            for surface in row["test_surfaces"]:
                if surface["kind"] == "tiered-source-40":
                    by_surface_case[surface["case_id"]] = row["evidence_id"]

        self.assertEqual(
            set(by_surface_case),
            {case["id"] for case in tiered},
        )
        self.assertEqual(
            by_surface_case["cardiology-flagship"],
            "sprint-2015",
        )
        self.assertEqual(
            by_surface_case["finance-flagship"],
            "legacy:historical-order-book-2010",
        )

    def test_benchmark_only_sources_have_public_identity_but_not_full_replay(self):
        rows = [
            row
            for row in self.catalog["entries"]
            if row["identity_status"] == "benchmark-source"
        ]
        self.assertEqual(
            len(rows),
            self.catalog["counts"]["benchmark_only_sources"],
        )
        for row in rows:
            self.assertTrue(row["title"].strip())
            self.assertTrue(row["source_url"].startswith("https://"))
            kinds = {surface["kind"] for surface in row["test_surfaces"]}
            self.assertIn("tiered-source-40", kinds)
            self.assertNotIn("full-replay", kinds)

    def test_reused_benchmark_cases_attach_to_existing_evidence_identities(self):
        source_map = json.loads(
            (
                ROOT
                / "validation-runs"
                / "real-papers"
                / "benchmark-source-map.json"
            ).read_text(encoding="utf-8")
        )
        catalog_ids = {row["evidence_id"] for row in self.catalog["entries"]}

        for mapping_name in [
            "stability_crossdomain_8",
            "claim_selection_12",
        ]:
            for case_id, evidence_id in source_map[mapping_name].items():
                if evidence_id == "synthetic":
                    continue
                self.assertIn(
                    evidence_id,
                    catalog_ids,
                    f"{mapping_name}/{case_id} points outside evidence registry",
                )

        synthetic = {
            case_id
            for case_id, evidence_id in source_map["claim_selection_12"].items()
            if evidence_id == "synthetic"
        }
        self.assertEqual(synthetic, {"CS09", "CS10", "CS11"})

    def test_multiple_surfaces_do_not_inflate_paper_count(self):
        source_backed = [
            row
            for row in self.catalog["entries"]
            if row["identity_status"] == "source-backed"
        ]
        surface_count = sum(len(row["test_surfaces"]) for row in source_backed)
        self.assertGreater(surface_count, len(source_backed))
        self.assertEqual(
            self.catalog["counts"]["source_backed_papers"],
            len(source_backed),
        )
        self.assertNotEqual(
            self.catalog["counts"]["source_backed_papers"],
            surface_count,
        )


if __name__ == "__main__":
    unittest.main()
