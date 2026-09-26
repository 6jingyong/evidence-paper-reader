#!/usr/bin/env python3
"""Score source-to-audit responses using the hidden real-paper contracts."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent
CASE_INDEX = ROOT / "case_index.json"
BLIND_SCORER = ROOT.parent / "blind-real-paper-10" / "score_blind.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


blind = load_module("source_to_audit_hidden_scorer", BLIND_SCORER)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path)
    parser.add_argument("--threshold", type=float, default=0.18)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    index = json.loads(CASE_INDEX.read_text(encoding="utf-8"))
    rows = []
    missing = []
    for case in index["cases"]:
        path = args.responses / f"{case['case_id']}.json"
        if not path.is_file():
            missing.append(case["case_id"])
            continue
        response = json.loads(path.read_text(encoding="utf-8"))
        rows.append(blind.score_case(case, response, args.threshold))

    result = {
        "benchmark_id": index["benchmark_id"],
        "case_count": len(index["cases"]),
        "scored_count": len(rows),
        "missing": missing,
        "hard_invariant_pass_rate": (
            sum(row["hard_invariants_pass"] for row in rows) / len(rows) if rows else 0.0
        ),
        "mean_claim_alignment_coverage": (
            sum(row["claim_alignment"]["confident_coverage"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_support_within_tolerance": (
            sum(row["support"]["within_tolerance_rate"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_reasoning_inference_type_overlap": (
            sum(row["reasoning"]["inference_type_overlap"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_reasoning_status_overlap": (
            sum(row["reasoning"]["reasoning_status_overlap"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_evidence_relation_overlap": (
            sum(row["reasoning"]["evidence_relation_overlap"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "cases": rows,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(
            f"{result['benchmark_id']}: scored={result['scored_count']}/{result['case_count']}; "
            f"hard={result['hard_invariant_pass_rate']:.3f}; "
            f"claim_alignment={result['mean_claim_alignment_coverage']:.3f}; "
            f"support={result['mean_support_within_tolerance']:.3f}; "
            f"reasoning_type={result['mean_reasoning_inference_type_overlap']:.3f}; "
            f"reasoning_status={result['mean_reasoning_status_overlap']:.3f}; "
            f"evidence_relation={result['mean_evidence_relation_overlap']:.3f}"
        )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
