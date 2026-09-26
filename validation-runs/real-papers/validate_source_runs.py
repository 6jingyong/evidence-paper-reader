#!/usr/bin/env python3
"""Validate durable source-to-audit run records."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
RUN_ROOT = ROOT / "validation-runs" / "real-papers"
SOURCE_RUNS = RUN_ROOT / "source-runs"
BENCH = ROOT / "benchmarks" / "source-to-audit-10"
CASE_INDEX = BENCH / "case_index.json"
BLIND_RUNNER = ROOT / "benchmarks" / "blind-real-paper-10" / "run_reviewer.py"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


blind = load_module("durable_source_blind_validator", BLIND_RUNNER)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def case_map() -> dict[str, dict]:
    return {
        case["case_id"]: case
        for case in load(CASE_INDEX)["cases"]
    }


def validate_source_input(case_id: str, data: dict, case: dict) -> list[str]:
    errors = []
    if data.get("case_id") != case_id:
        errors.append("source-input case_id mismatch")

    source = load(RUN_ROOT / case["round_id"] / case_id / "source.json")
    if data.get("canonical_source_url") != source.get("source_url"):
        errors.append("canonical_source_url does not match source-backed record")
    if data.get("stable_id") != source.get("stable_id"):
        errors.append("stable_id does not match source-backed record")

    for key in ["acquired_at", "acquisition_method", "normalization_method"]:
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} must be a non-empty string")

    review = data.get("review_material")
    if not isinstance(review, dict):
        errors.append("review_material must be an object")
    else:
        if not isinstance(review.get("sha256"), str) or not SHA256_RE.fullmatch(review["sha256"]):
            errors.append("review_material.sha256 must be lowercase SHA-256")
        if not isinstance(review.get("bytes"), int) or review["bytes"] <= 0:
            errors.append("review_material.bytes must be a positive integer")

    raw = data.get("raw_source")
    if raw is not None:
        if not isinstance(raw, dict):
            errors.append("raw_source must be an object when present")
        else:
            if not isinstance(raw.get("sha256"), str) or not SHA256_RE.fullmatch(raw["sha256"]):
                errors.append("raw_source.sha256 must be lowercase SHA-256")
            if not isinstance(raw.get("bytes"), int) or raw["bytes"] <= 0:
                errors.append("raw_source.bytes must be a positive integer")
    return errors


def validate_run(run_dir: Path) -> list[str]:
    errors = []
    manifest_path = run_dir / "run.json"
    if not manifest_path.is_file():
        return ["missing run.json"]
    data = load(manifest_path)

    required = {
        "run_id",
        "benchmark_id",
        "reviewer",
        "runtime",
        "source_head",
        "isolation",
        "case_ids",
    }
    missing = required - set(data)
    if missing:
        return ["run.json missing field(s): " + ", ".join(sorted(missing))]

    if data["run_id"] != run_dir.name:
        errors.append("run_id must match directory name")
    if data["benchmark_id"] != "source-to-audit-10-v1":
        errors.append("unexpected benchmark_id")
    for key in ["reviewer", "runtime", "source_head"]:
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} must be a non-empty string")

    isolation = data.get("isolation")
    if not isinstance(isolation, dict):
        errors.append("isolation must be an object")
    else:
        if isolation.get("fresh_context_per_case") is not True:
            errors.append("fresh_context_per_case must be true")
        if isolation.get("repository_answer_keys_accessible") is not False:
            errors.append("repository_answer_keys_accessible must be false")
        if not isinstance(isolation.get("method"), str) or not isolation["method"].strip():
            errors.append("isolation.method must be documented")

    cases = case_map()
    case_ids = data.get("case_ids")
    if not isinstance(case_ids, list) or not case_ids:
        errors.append("case_ids must be a non-empty list")
        case_ids = []
    if len(case_ids) != len(set(case_ids)):
        errors.append("case_ids must be unique")
    unknown = sorted(set(case_ids) - set(cases))
    if unknown:
        errors.append("case_ids outside source-to-audit benchmark: " + ", ".join(unknown))

    source_inputs = run_dir / "source-inputs"
    responses = run_dir / "responses"
    if not source_inputs.is_dir():
        errors.append("missing source-inputs directory")
    else:
        actual = {path.stem for path in source_inputs.glob("*.json")}
        if actual != set(case_ids):
            errors.append("source-input manifest set must exactly match case_ids")
        for case_id in sorted(actual & set(cases)):
            try:
                source_data = load(source_inputs / f"{case_id}.json")
                for error in validate_source_input(case_id, source_data, cases[case_id]):
                    errors.append(f"{case_id}: {error}")
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{case_id}: invalid source-input: {exc}")

    if not responses.is_dir():
        errors.append("missing responses directory")
    else:
        actual = {path.stem for path in responses.glob("*.json")}
        if actual != set(case_ids):
            errors.append("response file set must exactly match case_ids")
        for case_id in sorted(actual & set(cases)):
            try:
                blind.validate_response(responses / f"{case_id}.json", case_id)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{case_id}: invalid response: {exc}")

    score_path = run_dir / "score.json"
    if not score_path.is_file():
        errors.append("missing score.json")
    else:
        try:
            score = load(score_path)
            if score.get("benchmark_id") != data["benchmark_id"]:
                errors.append("score benchmark_id mismatch")
            if score.get("scored_count") != len(case_ids):
                errors.append("score.scored_count must equal case count")
            if score.get("missing"):
                errors.append("durable source-to-audit run cannot have missing scored cases")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid score.json: {exc}")

    forbidden_names = {
        "source-material.txt",
        "source-material.md",
        "source.pdf",
        "paper.pdf",
        "raw-source.pdf",
    }
    committed = {
        path.name
        for path in run_dir.rglob("*")
        if path.is_file()
    }
    leaked = sorted(committed & forbidden_names)
    if leaked:
        errors.append(
            "durable run contains source material that should remain external by default: "
            + ", ".join(leaked)
        )

    return errors


def validate_all() -> list[str]:
    errors = []
    if not SOURCE_RUNS.is_dir():
        return errors
    for run_dir in sorted(path for path in SOURCE_RUNS.iterdir() if path.is_dir()):
        if run_dir.name.startswith("."):
            continue
        for error in validate_run(run_dir):
            errors.append(f"{run_dir.name}: {error}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()
    errors = validate_run(args.run_dir) if args.run_dir else validate_all()
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print("PASS: durable source-to-audit records satisfy source fingerprint and isolation contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
