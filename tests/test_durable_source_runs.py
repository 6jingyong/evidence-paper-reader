import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / "validation-runs" / "real-papers" / "validate_source_runs.py"
PREPARE = ROOT / "benchmarks" / "source-to-audit-10" / "prepare_source.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_module("durable_source_validator", VALIDATOR)
prepare = load_module("durable_source_prepare", PREPARE)


def write_valid_run(root: Path):
    run_dir = root / "source-sol-smoke-01"
    source_inputs = run_dir / "source-inputs"
    responses = run_dir / "responses"
    source_inputs.mkdir(parents=True)
    responses.mkdir(parents=True)

    case_id = "attention-is-all-you-need-2017"
    run = {
        "run_id": run_dir.name,
        "benchmark_id": "source-to-audit-10-v1",
        "reviewer": "external-reviewer",
        "runtime": "fresh-process-test",
        "source_head": "deadbeef",
        "isolation": {
            "fresh_context_per_case": True,
            "repository_answer_keys_accessible": False,
            "method": "One independent process with only fingerprinted source material mounted.",
        },
        "case_ids": [case_id],
    }
    (run_dir / "run.json").write_text(json.dumps(run), encoding="utf-8")

    primary = root / "attention-primary.txt"
    primary.write_text(
        "normalized source bytes used by the reviewer",
        encoding="utf-8",
    )
    bundle, components = prepare.build_bundle(
        case_id,
        {"primary": primary},
    )
    material = root / "attention-bundle.txt"
    material.write_bytes(bundle)
    source_input = prepare.build_manifest(
        case_id,
        material,
        acquisition_method="test fixture",
        normalization_method="utf8-source-bundle-v1",
        acquired_at="2026-09-26T00:00:00+00:00",
        components=components,
    )
    (source_inputs / f"{case_id}.json").write_text(
        json.dumps(source_input),
        encoding="utf-8",
    )

    claims = []
    edges = []
    for i in range(1, 4):
        claims.append({
            "content": f"Bounded source-facing claim {i}.",
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
            "reason": "The source supports only this bounded version.",
        })
        edges.append({
            "edge_id": f"R{i}",
            "target_claim": i,
            "evidence_nodes": [f"E{i}"],
            "evidence_relations": [
                {
                    "evidence_node": f"E{i}",
                    "relation": "supports",
                    "reason": "The evidence node bears on this bounded claim.",
                }
            ],
            "upstream_claims": [],
            "inference_type": "comparison",
            "reasoning_status": "qualified",
            "added_reach": "The source supports only a narrower comparative conclusion.",
            "assumptions": [],
        })
    response = {
        "case_id": case_id,
        "evidence_viability": "auditable",
        "viability_flags": [],
        "claims": claims,
        "reasoning_edges": edges,
        "modules": ["study-design-traps.md"],
        "use_evidence_inventory": False,
        "reader_conclusion": "The source supports bounded benchmark claims.",
    }
    (responses / f"{case_id}.json").write_text(
        json.dumps(response),
        encoding="utf-8",
    )

    score = {
        "benchmark_id": "source-to-audit-10-v1",
        "scored_count": 1,
        "missing": [],
    }
    (run_dir / "score.json").write_text(json.dumps(score), encoding="utf-8")
    return run_dir


class DurableSourceRunTests(unittest.TestCase):
    def test_valid_source_run_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            self.assertEqual(validator.validate_run(run_dir), [])

    def test_answer_key_access_must_be_false(self):
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

    def test_source_profile_hash_must_match_current_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            path = run_dir / "source-inputs" / "attention-is-all-you-need-2017.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["acquisition_profile"]["profile_sha256"] = "0" * 64
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("acquisition_profile does not match" in e for e in errors),
                errors,
            )

    def test_required_source_component_cannot_be_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = write_valid_run(root)
            path = run_dir / "source-inputs" / "attention-is-all-you-need-2017.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["components"] = []
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("missing required id" in e for e in errors),
                errors,
            )

    def test_source_hash_must_be_well_formed(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            path = run_dir / "source-inputs" / "attention-is-all-you-need-2017.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["review_material"]["sha256"] = "not-a-hash"
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("review_material.sha256" in e for e in errors),
                errors,
            )

    def test_source_identity_must_match_recorded_paper(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            path = run_dir / "source-inputs" / "attention-is-all-you-need-2017.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["stable_id"] = "doi:wrong"
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = validator.validate_run(run_dir)
            self.assertTrue(any("stable_id does not match" in e for e in errors), errors)

    def test_source_material_must_not_be_committed_in_durable_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            (run_dir / "source-material.txt").write_text(
                "copyrighted source body",
                encoding="utf-8",
            )
            errors = validator.validate_run(run_dir)
            self.assertTrue(
                any("contains source material" in e for e in errors),
                errors,
            )

    def test_response_set_and_score_must_cover_declared_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_valid_run(Path(tmp))
            (run_dir / "responses" / "attention-is-all-you-need-2017.json").unlink()
            errors = validator.validate_run(run_dir)
            self.assertTrue(any("response file set" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
