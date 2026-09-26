import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / "validation-runs" / "real-papers" / "validate_blind_runs.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_module("durable_blind_run_validator", VALIDATOR)


def write_valid_run(root: Path):
    run_dir = root / "isolated-sol-smoke-01"
    responses = run_dir / "responses"
    responses.mkdir(parents=True)
    run = {
        "run_id": run_dir.name,
        "benchmark_id": "blind-real-paper-10-v1",
        "reviewer": "external-reviewer",
        "runtime": "fresh-process-test",
        "source_head": "deadbeef",
        "isolation": {
            "fresh_context_per_case": True,
            "repository_answer_keys_accessible": False,
            "method": "One independent process with only the generated prompt mounted.",
        },
        "case_ids": ["attention-is-all-you-need-2017"],
    }
    (run_dir / "run.json").write_text(json.dumps(run), encoding="utf-8")
    response = {
        "case_id": "attention-is-all-you-need-2017",
        "evidence_viability": "auditable",
        "viability_flags": [],
        "claims": [
            {
                "content": f"Independent source-facing claim {i}.",
                "claim_type": "performance",
                "conclusion_strength": "medium",
                "evidence_nodes": [f"E{i}"],
                "evidence_relations": [
                    {
                        "evidence_node": f"E{i}",
                        "relation": "supports",
                        "reason": "The evidence node bears on this bounded claim.",
                    }
                ],
                "upstream_claims": [],
                "support_level": "partial",
                "source_location": f"Results {i}",
                "reason": "The source supports this bounded statement.",
            }
            for i in range(1, 4)
        ],
        "reasoning_edges": [
            {
                "edge_id": f"R{i}",
                "target_claim": i,
                "evidence_nodes": [f"E{i}"],
                "upstream_claims": [],
                "inference_type": "generalization",
                "reasoning_status": "qualified",
                "added_reach": "The source supports only a bounded version of the claim.",
                "assumptions": [],
            }
            for i in range(1, 4)
        ],
        "modules": ["study-design-traps.md"],
        "use_evidence_inventory": False,
        "reader_conclusion": "Bounded benchmark claims are inspectable.",
    }
    (responses / "attention-is-all-you-need-2017.json").write_text(
        json.dumps(response),
        encoding="utf-8",
    )
    score = {
        "benchmark_id": "blind-real-paper-10-v1",
        "scored_count": 1,
        "missing": [],
    }
    (run_dir / "score.json").write_text(json.dumps(score), encoding="utf-8")
    return run_dir


class DurableBlindRunTests(unittest.TestCase):
    def test_valid_isolated_run_record_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            self.assertEqual(validator.validate_run(run_dir), [])

    def test_answer_key_access_must_be_explicitly_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            data["isolation"]["repository_answer_keys_accessible"] = True
            (run_dir / "run.json").write_text(json.dumps(data), encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("repository_answer_keys_accessible must be false" in e for e in errors),
                errors,
            )

    def test_fresh_context_per_case_is_hard_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            data["isolation"]["fresh_context_per_case"] = False
            (run_dir / "run.json").write_text(json.dumps(data), encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("fresh_context_per_case must be true" in e for e in errors),
                errors,
            )

    def test_unrecorded_paper_cannot_enter_durable_blind_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            data["case_ids"] = ["not-a-recorded-paper"]
            (run_dir / "run.json").write_text(json.dumps(data), encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("outside blind benchmark" in e for e in errors),
                errors,
            )
            self.assertTrue(
                any("without source-backed records" in e for e in errors),
                errors,
            )

    def test_response_set_must_exactly_match_declared_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            extra = run_dir / "responses" / "sprint-2015.json"
            extra.write_text("{}", encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("response file set must exactly match case_ids" in e for e in errors),
                errors,
            )

    def test_score_must_cover_every_committed_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            score = json.loads((run_dir / "score.json").read_text(encoding="utf-8"))
            score["scored_count"] = 0
            (run_dir / "score.json").write_text(json.dumps(score), encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("score.scored_count must equal case count" in e for e in errors),
                errors,
            )


if __name__ == "__main__":
    unittest.main()
