#!/usr/bin/env python3
"""Validate durable isolated blind-review run records."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
RUN_ROOT = ROOT / "validation-runs" / "real-papers"
BLIND_RUNS = RUN_ROOT / "blind-runs"
BENCH = ROOT / "benchmarks" / "blind-real-paper-10"
CASE_INDEX = BENCH / "case_index.json"
RUNNER = BENCH / "run_reviewer.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


runner = load_module("durable_blind_runner_schema", RUNNER)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_backed_ids() -> set[str]:
    ids = set()
    for rd in RUN_ROOT.glob("*-round-*"):
        manifest = rd / "manifest.json"
        if manifest.is_file():
            ids.update(case["id"] for case in load(manifest)["cases"])
    return ids


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
    if data["benchmark_id"] != "blind-real-paper-10-v1":
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

    case_ids = data.get("case_ids")
    if not isinstance(case_ids, list) or not case_ids:
        errors.append("case_ids must be a non-empty list")
        case_ids = []
    if len(case_ids) != len(set(case_ids)):
        errors.append("case_ids must be unique")

    indexed = {case["case_id"] for case in load(CASE_INDEX)["cases"]}
    recorded = source_backed_ids()
    unknown = sorted(set(case_ids) - indexed)
    unrecorded = sorted(set(case_ids) - recorded)
    if unknown:
        errors.append("case_ids outside blind benchmark: " + ", ".join(unknown))
    if unrecorded:
        errors.append("case_ids without source-backed records: " + ", ".join(unrecorded))

    responses = run_dir / "responses"
    if not responses.is_dir():
        errors.append("missing responses directory")
    else:
        actual = {path.stem for path in responses.glob("*.json")}
        if actual != set(case_ids):
            errors.append("response file set must exactly match case_ids")
        for case_id in sorted(actual & set(case_ids)):
            try:
                runner.validate_response(responses / f"{case_id}.json", case_id)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{case_id}: invalid response: {exc}")

    score = run_dir / "score.json"
    if not score.is_file():
        errors.append("missing score.json")
    else:
        try:
            score_data = load(score)
            if score_data.get("benchmark_id") != data["benchmark_id"]:
                errors.append("score benchmark_id mismatch")
            if score_data.get("scored_count") != len(case_ids):
                errors.append("score.scored_count must equal case count")
            if score_data.get("missing"):
                errors.append("durable blind run cannot have missing scored cases")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid score.json: {exc}")

    return errors


def validate_all() -> list[str]:
    errors = []
    if not BLIND_RUNS.is_dir():
        return errors
    for run_dir in sorted(path for path in BLIND_RUNS.iterdir() if path.is_dir()):
        if run_dir.name.startswith("."):
            continue
        for error in validate_run(run_dir):
            errors.append(f"{run_dir.name}: {error}")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args()

    errors = validate_run(args.run_dir) if args.run_dir else validate_all()
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print("PASS: durable blind-run records satisfy isolation and evidence contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
