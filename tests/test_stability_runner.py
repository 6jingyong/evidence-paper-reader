import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "benchmarks" / "stability-crossdomain-8" / "run_reviewer.py"
GENERATOR = ROOT / "benchmarks" / "stability-crossdomain-8" / "generate_runs.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


runner = load_module("stability_runner", SCRIPT)
generate = load_module("stability_generator", GENERATOR)


class StabilityRunnerTests(unittest.TestCase):
    def test_command_substitution_is_argument_safe(self):
        job = {"packet_id":"SR-TEST", "case_id":"ST01", "repeat":3}
        command = runner.command_for(
            "python reviewer.py {packet} {output} --case {case_id} --repeat {repeat}",
            job,
            Path("/tmp/paper with spaces.md"),
            Path("/tmp/out file.json"),
        )
        self.assertEqual(
            command,
            [
                "python",
                "reviewer.py",
                "/tmp/paper with spaces.md",
                "/tmp/out file.json",
                "--case",
                "ST01",
                "--repeat",
                "3",
            ],
        )

    def test_valid_json_output_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "response.json"
            output.write_text(json.dumps({
                "case_id":"ST01",
                "evidence_viability":"auditable",
                "selected_claim_ids":["K1","K2","K5"],
                "modules":["study-design-traps.md"],
                "use_evidence_inventory":False,
                "support":[
                    {"claim_id":"K1","support_level":"sufficient"},
                    {"claim_id":"K2","support_level":"sufficient"},
                    {"claim_id":"K5","support_level":"sufficient"}
                ]
            }), encoding="utf-8")
            runner.validate_json_output(output, {"case_id":"ST01"})

    def test_wrong_case_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "response.json"
            output.write_text(json.dumps({
                "case_id":"ST02",
                "evidence_viability":"auditable",
                "selected_claim_ids":[],
                "modules":[],
                "use_evidence_inventory":False,
                "support":[]
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.validate_json_output(output, {"case_id":"ST01"})

    def test_packet_id_is_deterministic(self):
        self.assertEqual(
            generate.packet_id("ST01", 1, 20260924),
            generate.packet_id("ST01", 1, 20260924),
        )
        self.assertNotEqual(
            generate.packet_id("ST01", 1, 20260924),
            generate.packet_id("ST01", 2, 20260924),
        )

    def test_resume_requires_a_valid_response(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "response.json"
            path.write_text("not-json", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                runner.validate_json_output(path, {"case_id":"ST01"})


if __name__ == "__main__":
    unittest.main()
