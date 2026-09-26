#!/usr/bin/env python3
"""Score Carrier-Neutral 12 responses against hidden expectations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent
SPECS = ROOT / "case_specs.json"
EXPECTATIONS = ROOT / "reference_expectations.json"


def load_cases() -> list[dict]:
    return json.loads(SPECS.read_text(encoding="utf-8"))["cases"]


def load_expectations() -> dict:
    return json.loads(EXPECTATIONS.read_text(encoding="utf-8"))["cases"]


def edges_for_claim(response: dict, claim_number: int) -> list[dict]:
    return [
        edge
        for edge in response.get("reasoning_edges", [])
        if isinstance(edge, dict) and edge.get("target_claim") == claim_number
    ]


def relation_labels(claim: dict) -> set[str]:
    return {
        item.get("relation")
        for item in claim.get("evidence_relations", [])
        if isinstance(item, dict) and isinstance(item.get("relation"), str)
    }


def score_case(case_id: str, response: dict, expected: dict) -> dict:
    viability_ok = response.get("evidence_viability") == expected["viability"]
    claims = response.get("claims", [])
    expected_support = expected["support"]

    count_ok = len(claims) == len(expected_support)
    support_rows = []
    inference_rows = []
    relation_rows = []

    for index, expected_level in enumerate(expected_support, start=1):
        claim = claims[index - 1] if index <= len(claims) else {}
        actual_level = claim.get("support_level")
        support_rows.append({
            "claim": index,
            "expected": expected_level,
            "actual": actual_level,
            "pass": actual_level == expected_level,
        })

        allowed_types = set(expected["inference"][index - 1])
        actual_types = {
            edge.get("inference_type")
            for edge in edges_for_claim(response, index)
            if isinstance(edge.get("inference_type"), str)
        }
        inference_rows.append({
            "claim": index,
            "allowed": sorted(allowed_types),
            "actual": sorted(actual_types),
            "pass": bool(actual_types & allowed_types),
        })

        allowed_relations = set(expected["relation_any"][index - 1])
        actual_relations = relation_labels(claim)
        relation_rows.append({
            "claim": index,
            "allowed_any": sorted(allowed_relations),
            "actual": sorted(actual_relations),
            "pass": bool(actual_relations & allowed_relations),
        })

    support_rate = (
        sum(row["pass"] for row in support_rows) / len(support_rows)
        if support_rows else 1.0
    )
    inference_rate = (
        sum(row["pass"] for row in inference_rows) / len(inference_rows)
        if inference_rows else 1.0
    )
    relation_rate = (
        sum(row["pass"] for row in relation_rows) / len(relation_rows)
        if relation_rows else 1.0
    )

    return {
        "case_id": case_id,
        "viability": {
            "expected": expected["viability"],
            "actual": response.get("evidence_viability"),
            "pass": viability_ok,
        },
        "claim_count": {
            "expected": len(expected_support),
            "actual": len(claims),
            "pass": count_ok,
        },
        "support": {
            "pass_rate": round(support_rate, 4),
            "claims": support_rows,
        },
        "reasoning_inference": {
            "pass_rate": round(inference_rate, 4),
            "claims": inference_rows,
        },
        "evidence_direction": {
            "pass_rate": round(relation_rate, 4),
            "claims": relation_rows,
        },
        "hard_pass": viability_ok and count_ok,
        "full_reference_match": (
            viability_ok
            and count_ok
            and support_rate == 1.0
            and inference_rate == 1.0
            and relation_rate == 1.0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    expectations = load_expectations()
    case_ids = [case["case_id"] for case in load_cases()]
    rows = []
    missing = []

    for case_id in case_ids:
        path = args.responses / f"{case_id}.json"
        if not path.is_file():
            missing.append(case_id)
            continue
        response = json.loads(path.read_text(encoding="utf-8"))
        rows.append(score_case(case_id, response, expectations[case_id]))

    result = {
        "benchmark_id": "carrier-neutral-12-v1",
        "case_count": len(case_ids),
        "scored_count": len(rows),
        "missing": missing,
        "hard_pass_rate": (
            sum(row["hard_pass"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "full_reference_match_rate": (
            sum(row["full_reference_match"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_support_match": (
            sum(row["support"]["pass_rate"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_inference_match": (
            sum(row["reasoning_inference"]["pass_rate"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_evidence_direction_match": (
            sum(row["evidence_direction"]["pass_rate"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "cases": rows,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(
            f"{result['benchmark_id']}: scored={result['scored_count']}/{result['case_count']}; "
            f"hard={result['hard_pass_rate']:.3f}; "
            f"full={result['full_reference_match_rate']:.3f}; "
            f"support={result['mean_support_match']:.3f}; "
            f"inference={result['mean_inference_match']:.3f}; "
            f"direction={result['mean_evidence_direction_match']:.3f}"
        )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
