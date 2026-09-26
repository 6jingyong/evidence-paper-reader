#!/usr/bin/env python3
"""Score claim selection, silent narrowing, distractor selection, and viability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent


def load_responses(path: Path) -> dict[str, dict]:
    result = {}
    for file in path.glob("*.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        result[data["case_id"]] = data
    return result


def score(responses: dict[str, dict], expectations: dict) -> dict:
    required_total = 0
    required_hit = 0
    forbidden_total = 0
    forbidden_selected = 0
    narrowing_opportunities = 0
    silent_narrowing = 0
    viability_correct = 0
    claim_count_violations = 0
    rows = []

    for exp in expectations["cases"]:
        response = responses[exp["case_id"]]
        selected = response.get("selected_claim_ids", [])
        selected_set = set(selected)

        required_total += len(exp["required"])
        required_hit += len(selected_set & set(exp["required"]))
        forbidden_total += len(exp["forbidden"])
        forbidden_selected += len(selected_set & set(exp["forbidden"]))
        viability_correct += int(response.get("evidence_viability") == exp["viability"])

        for strong_id, narrow_id in exp["narrowing_pairs"]:
            narrowing_opportunities += 1
            if strong_id not in selected_set and narrow_id in selected_set:
                silent_narrowing += 1

        count = len(selected)
        v = response.get("evidence_viability")
        bad_count = (
            (v == "auditable" and not (3 <= count <= 5))
            or (v == "partially auditable" and not (1 <= count <= 5))
            or (v == "non-auditable" and count != 0)
        )
        claim_count_violations += int(bad_count)

        rows.append({
            "case_id": exp["case_id"],
            "viability_expected": exp["viability"],
            "viability_actual": response.get("evidence_viability"),
            "selected_claim_ids": selected,
            "missing_required": sorted(set(exp["required"]) - selected_set),
            "selected_forbidden": sorted(selected_set & set(exp["forbidden"])),
            "claim_count_violation": bad_count,
        })

    return {
        "case_count": len(expectations["cases"]),
        "required_claim_recall": required_hit / required_total if required_total else 1.0,
        "forbidden_selection_rate": forbidden_selected / forbidden_total if forbidden_total else 0.0,
        "silent_narrowing_rate": silent_narrowing / narrowing_opportunities if narrowing_opportunities else 0.0,
        "viability_accuracy": viability_correct / len(expectations["cases"]),
        "claim_count_violations": claim_count_violations,
        "cases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path)
    parser.add_argument("--expectations", type=Path, default=ROOT / "reference_expectations.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    responses = load_responses(args.responses)
    expectations = json.loads(args.expectations.read_text(encoding="utf-8"))
    missing = [x["case_id"] for x in expectations["cases"] if x["case_id"] not in responses]
    if missing:
        print("FAIL: missing responses: " + ", ".join(missing))
        return 1

    result = score(responses, expectations)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for key in [
            "required_claim_recall",
            "forbidden_selection_rate",
            "silent_narrowing_rate",
            "viability_accuracy",
            "claim_count_violations",
        ]:
            print(f"{key}: {result[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
