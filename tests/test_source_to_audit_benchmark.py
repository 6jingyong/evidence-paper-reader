import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "source-to-audit-10"
RUN_ROOT = ROOT / "validation-runs" / "real-papers"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


prepare = load_module("source_prepare", BENCH / "prepare_source.py")
runner = load_module("source_runner", BENCH / "run_reviewer.py")


class SourceToAuditBenchmarkTests(unittest.TestCase):
    def test_case_index_matches_source_backed_records(self):
        index = json.loads((BENCH / "case_index.json").read_text(encoding="utf-8"))
        self.assertEqual(len(index["cases"]), 10)
        for case in index["cases"]:
            root = RUN_ROOT / case["round_id"] / case["case_id"]
            self.assertTrue((root / "source.json").is_file(), case["case_id"])
            self.assertTrue((root / "ledger.json").is_file(), case["case_id"])

    def test_source_manifest_fingerprints_exact_review_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            material = tmp / "paper.txt"
            material.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
            manifest = prepare.build_manifest(
                "attention-is-all-you-need-2017",
                material,
                acquisition_method="test fixture",
                normalization_method="identity text",
                acquired_at="2026-09-26T00:00:00+00:00",
            )
            self.assertEqual(manifest["review_material"]["bytes"], material.stat().st_size)
            self.assertEqual(
                manifest["review_material"]["sha256"],
                prepare.sha256(material),
            )
            self.assertTrue(manifest["canonical_source_url"].startswith("https://"))
            self.assertEqual(manifest["stable_id"], "arXiv:1706.03762")

    def test_runner_rejects_source_material_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case_root = root / "attention-is-all-you-need-2017"
            case_root.mkdir()
            material = case_root / "source-material.txt"
            material.write_text("original normalized source", encoding="utf-8")
            manifest = prepare.build_manifest(
                "attention-is-all-you-need-2017",
                material,
                acquisition_method="test fixture",
                normalization_method="identity text",
                acquired_at="2026-09-26T00:00:00+00:00",
            )
            (case_root / "source-input.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )
            runner.verify_prepared("attention-is-all-you-need-2017", root)

            material.write_text("tampered normalized source", encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.verify_prepared("attention-is-all-you-need-2017", root)

    def test_source_review_prompt_exposes_source_not_answer_keys(self):
        manifest = {
            "canonical_source_url": "https://example.com/paper",
            "stable_id": "doi:test",
        }
        prompt = runner.prompt_text("demo", manifest)
        self.assertIn("source-material.txt", prompt)
        self.assertIn("claim–evidence–reasoning", prompt)
        self.assertIn("reasoning_edges", prompt)
        for forbidden in [
            "real-paper-judgment-baseline",
            "regression_contract",
            "must_hold",
            "allowed_range",
            "validation-runs/",
        ]:
            self.assertNotIn(forbidden, prompt)

    def test_command_can_receive_source_path_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            command = runner.command_for(
                "reviewer {prompt} {source} {output} {case_id}",
                tmp / "prompt.md",
                tmp / "source-material.txt",
                tmp / "response.json",
                "demo",
            )
            self.assertEqual(command[0], "reviewer")
            self.assertTrue(command[1].endswith("prompt.md"))
            self.assertTrue(command[2].endswith("source-material.txt"))
            self.assertTrue(command[3].endswith("response.json"))
            self.assertEqual(command[4], "demo")


if __name__ == "__main__":
    unittest.main()
