import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
BENCH = ROOT / "benchmarks" / "stability-crossdomain-8"
SCRIPT = BENCH / "run_reviewer.py"
PROMPT_SCRIPT = BENCH / "prepare_review.py"
GENERATOR = BENCH / "generate_runs.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


runner = load_module("stability_runner", SCRIPT)
generate = load_module("stability_generator", GENERATOR)
prepare = load_module("stability_prepare", PROMPT_SCRIPT)


class StabilityRunnerTests(unittest.TestCase):
    def test_command_substitution_is_argument_safe(self):
        job = {"packet_id":"SR-TEST", "case_id":"ST01", "repeat":3}
        command = runner.command_for(
            "python reviewer.py {packet} {prompt} {output} --case {case_id} --repeat {repeat}",
            job,
            Path("/tmp/paper with spaces.md"),
            Path("/tmp/prompt file.md"),
            Path("/tmp/out file.json"),
        )
        self.assertEqual(
            command,
            [
                "python",
                "reviewer.py",
                "/tmp/paper with spaces.md",
                "/tmp/prompt file.md",
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

    def test_structurally_complete_but_invalid_response_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "response.json"
            output.write_text(json.dumps({
                "case_id":"ST01",
                "evidence_viability":"auditable",
                "selected_claim_ids":["K1","K2","K9"],
                "modules":["made-up-module.md"],
                "use_evidence_inventory":False,
                "support":[
                    {"claim_id":"K1","support_level":"sufficient"},
                    {"claim_id":"K2","support_level":"sufficient"},
                    {"claim_id":"K9","support_level":"certain"}
                ]
            }), encoding="utf-8")
            job = {
                "case_id":"ST01",
                "candidate_ids":["K1","K2","K3","K4","K5"],
            }
            with self.assertRaises(ValueError):
                runner.validate_json_output(output, job)

    def test_public_response_format_is_answer_neutral(self):
        contract = (BENCH / "response-format.md").read_text(encoding="utf-8")
        self.assertNotIn('"ST01"', contract)
        self.assertNotIn('"K1"', contract)
        self.assertNotIn('"K2"', contract)
        self.assertNotIn('"K5"', contract)
        self.assertNotIn("study-design-traps.md", contract)

    def test_packet_id_is_deterministic(self):
        self.assertEqual(
            generate.packet_id("ST01", 1, 20260924),
            generate.packet_id("ST01", 1, 20260924),
        )
        self.assertNotEqual(
            generate.packet_id("ST01", 1, 20260924),
            generate.packet_id("ST01", 2, 20260924),
        )

    def test_generated_matrix_carries_candidate_ids(self):
        specs = json.loads((BENCH / "case_specs.json").read_text(encoding="utf-8"))
        case = specs["cases"][0]
        expected = [item["id"] for item in case["candidates"]]
        row = {
            "packet_id": generate.packet_id(case["case_id"], 1, specs["seed"]),
            "case_id": case["case_id"],
            "repeat": 1,
            "domain": case["domain"],
            "candidate_ids": expected,
        }
        self.assertEqual(row["candidate_ids"], expected)

    def test_resume_requires_a_valid_response(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "response.json"
            path.write_text("not-json", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                runner.validate_json_output(path, {"case_id":"ST01"})

    def test_prepare_prompt_contains_packet_and_response_contract(self):
        packet = "# packet\n\n- ST01: example evidence\n"
        prompt = prepare.render_prompt(packet, "/tmp/SR-TEST.md")
        self.assertIn("Run exactly this one review in a fresh model context.", prompt)
        self.assertIn("ST01: example evidence", prompt)
        self.assertIn('"selected_claim_ids"', prompt)
        contract = prompt.split("## Review packet", 1)[0]
        self.assertNotIn('"K1"', contract)
        self.assertNotIn('"K2"', contract)
        self.assertNotIn('"K5"', contract)
        self.assertNotIn("forbidden_claims", contract.lower())
        self.assertNotIn("required_claims", contract.lower())

    def test_run_job_executes_one_external_reviewer_and_validates_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            packet_dir = root / "packets"
            response_dir = root / "responses"
            prompt_dir = root / "prompts"
            packet_dir.mkdir()
            response_dir.mkdir()
            prompt_dir.mkdir()
            packet = packet_dir / "SR-TEST123.md"
            packet.write_text("# packet\n", encoding="utf-8")

            reviewer = root / "reviewer.py"
            reviewer.write_text(
                "import json, pathlib, sys\n"
                "prompt=pathlib.Path(sys.argv[1])\n"
                "output=pathlib.Path(sys.argv[2])\n"
                "assert prompt.exists()\n"
                "output.write_text(json.dumps({"
                "'case_id':'ST01',"
                "'evidence_viability':'auditable',"
                "'selected_claim_ids':['K1','K2','K5'],"
                "'modules':['study-design-traps.md'],"
                "'use_evidence_inventory':False,"
                "'support':["
                "{'claim_id':'K1','support_level':'sufficient'},"
                "{'claim_id':'K2','support_level':'sufficient'},"
                "{'claim_id':'K5','support_level':'sufficient'}"
                "]"
                "}), encoding='utf-8')\n",
                encoding="utf-8",
            )

            job = {
                "packet_id": "SR-TEST123",
                "case_id": "ST01",
                "repeat": 1,
                "domain": "clinical cardiology",
            }
            result = runner.run_job(
                job,
                packet_dir,
                response_dir,
                f"{os.environ.get('PYTHON', 'python3')} {reviewer} {{prompt}} {{output}}",
                30,
                {},
                False,
                prompt_dir=prompt_dir,
            )
            self.assertEqual(result["status"], "completed")
            self.assertTrue((response_dir / "SR-TEST123.json").exists())
            self.assertTrue((prompt_dir / "SR-TEST123.md").exists())
            data = json.loads((response_dir / "SR-TEST123.json").read_text(encoding="utf-8"))
            self.assertEqual(data["case_id"], "ST01")

    def test_run_job_surfaces_nonzero_reviewer_exit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            packet_dir = root / "packets"
            response_dir = root / "responses"
            packet_dir.mkdir()
            response_dir.mkdir()
            packet = packet_dir / "SR-BAD.md"
            packet.write_text("# packet\n", encoding="utf-8")
            reviewer = root / "reviewer.py"
            reviewer.write_text("raise SystemExit(7)\n", encoding="utf-8")

            result = runner.run_job(
                {"packet_id":"SR-BAD","case_id":"ST01","repeat":1},
                packet_dir,
                response_dir,
                f"python3 {reviewer} {{packet}} {{output}}",
                30,
                {},
                False,
            )
            self.assertEqual(result["status"], "failed")
            self.assertIn("runner exited with 7", result["error"])


if __name__ == "__main__":
    unittest.main()
