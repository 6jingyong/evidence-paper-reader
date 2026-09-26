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
            self.assertEqual(
                {surface["kind"] for surface in row["test_surfaces"]},
                {"legacy-regression"},
            )

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
