#!/usr/bin/env python3
"""Score blind real-paper re-audits against hidden durable judgment contracts."""

from __future__ import annotations

import argparse
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
REPO_ROOT = ROOT.parents[1]
RUN_ROOT = REPO_ROOT / "validation-runs" / "real-papers"
CASE_INDEX = ROOT / "case_index.json"

STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "by", "is", "are", "was", "were", "be", "been", "this", "that", "these",
    "those", "from", "as", "at", "it", "its", "their", "than", "among",
}


def tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in STOP
    }


def trigrams(text: str) -> set[str]:
    normalized = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", text.lower())).strip()
    if len(normalized) < 3:
        return {normalized} if normalized else set()
    return {normalized[i : i + 3] for i in range(len(normalized) - 2)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def claim_similarity(a: str, b: str) -> float:
    return 0.7 * jaccard(tokens(a), tokens(b)) + 0.3 * jaccard(trigrams(a), trigrams(b))


def best_alignment(reference_claims: list[dict], fresh_claims: list[dict]) -> list[dict]:
    if not reference_claims or not fresh_claims:
        return []
    ref_count = len(reference_claims)
    fresh_count = len(fresh_claims)
    k = min(ref_count, fresh_count)

    best_score = -1.0
    best_pairs = []
    if ref_count <= fresh_count:
        for chosen in itertools.permutations(range(fresh_count), k):
            pairs = list(enumerate(chosen))
            score = sum(
                claim_similarity(
                    reference_claims[ri]["content"],
                    fresh_claims[fi]["content"],
                )
                for ri, fi in pairs
            )
            if score > best_score:
                best_score = score
                best_pairs = pairs
    else:
        for chosen_refs in itertools.combinations(range(ref_count), k):
            for chosen_fresh in itertools.permutations(range(fresh_count), k):
                pairs = list(zip(chosen_refs, chosen_fresh))
                score = sum(
                    claim_similarity(
                        reference_claims[ri]["content"],
                        fresh_claims[fi]["content"],
                    )
                    for ri, fi in pairs
                )
                if score > best_score:
                    best_score = score
                    best_pairs = pairs

    return [
        {
            "reference_index": ri,
            "fresh_index": fi,
            "similarity": round(
                claim_similarity(
                    reference_claims[ri]["content"],
                    fresh_claims[fi]["content"],
                ),
                4,
            ),
        }
        for ri, fi in best_pairs
    ]


def load_case(case: dict) -> tuple[dict, dict]:
    root = RUN_ROOT / case["round_id"] / case["case_id"]
    ledger = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (RUN_ROOT / case["round_id"] / "manifest.json").read_text(encoding="utf-8")
    )
    manifest_case = next(item for item in manifest["cases"] if item["id"] == case["case_id"])
    return ledger, manifest_case["regression_contract"]


def score_case(case: dict, response: dict, threshold: float) -> dict:
    ledger, contract = load_case(case)
    must = contract["must_hold"]
    allowed = contract["allowed_range"]

    viability_ok = response.get("evidence_viability") == must["viability"]
    flags = set(response.get("viability_flags", []))
    required_flags = set(must["required_viability_flags"])
    allowed_flags = set(allowed["viability_flags"])
    required_flags_ok = required_flags.issubset(flags)
    flags_within_allowed = flags.issubset(allowed_flags)

    ref_claims = ledger.get("claims", [])
    fresh_claims = response.get("claims", [])
    alignment = best_alignment(ref_claims, fresh_claims)

    matched_support = []
    needs_adjudication = []
    for pair in alignment:
        ri = pair["reference_index"]
        fi = pair["fresh_index"]
        similarity = pair["similarity"]
        if similarity < threshold:
            needs_adjudication.append({
                "reference_claim": ri + 1,
                "fresh_claim": fi + 1,
                "similarity": similarity,
            })
            continue
        actual = fresh_claims[fi].get("support_level")
        choices = allowed["support_levels"][ri]
        matched_support.append({
            "reference_claim": ri + 1,
            "fresh_claim": fi + 1,
            "similarity": similarity,
            "fresh_support": actual,
            "allowed_support": choices,
            "within_tolerance": actual in choices,
        })

    confidently_matched = len(matched_support)
    support_ok = sum(item["within_tolerance"] for item in matched_support)
    reference_claim_count = len(ref_claims)
    coverage = (
        confidently_matched / reference_claim_count
        if reference_claim_count
        else 1.0
    )
    support_rate = (
        support_ok / confidently_matched
        if confidently_matched
        else (1.0 if not ref_claims else 0.0)
    )

    hard_invariants_pass = viability_ok and required_flags_ok
    return {
        "case_id": case["case_id"],
        "hard_invariants_pass": hard_invariants_pass,
        "viability": {
            "expected": must["viability"],
            "actual": response.get("evidence_viability"),
            "pass": viability_ok,
        },
        "viability_flags": {
            "required": sorted(required_flags),
            "allowed": sorted(allowed_flags),
            "actual": sorted(flags),
            "required_pass": required_flags_ok,
            "within_allowed": flags_within_allowed,
        },
        "claim_alignment": {
            "reference_count": reference_claim_count,
            "fresh_count": len(fresh_claims),
            "confident_coverage": round(coverage, 4),
            "pairs": alignment,
            "needs_adjudication": needs_adjudication,
        },
        "support": {
            "within_tolerance_rate": round(support_rate, 4),
            "matched": matched_support,
        },
    }


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
        rows.append(score_case(case, response, args.threshold))

    result = {
        "benchmark_id": index["benchmark_id"],
        "case_count": len(index["cases"]),
        "scored_count": len(rows),
        "missing": missing,
        "hard_invariant_pass_rate": (
            sum(row["hard_invariants_pass"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_claim_alignment_coverage": (
            sum(row["claim_alignment"]["confident_coverage"] for row in rows) / len(rows)
            if rows else 0.0
        ),
        "mean_support_within_tolerance": (
            sum(row["support"]["within_tolerance_rate"] for row in rows) / len(rows)
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
            f"support={result['mean_support_within_tolerance']:.3f}"
        )
        for row in rows:
            print(
                f"- {row['case_id']}: hard={row['hard_invariants_pass']}; "
                f"align={row['claim_alignment']['confident_coverage']:.3f}; "
                f"support={row['support']['within_tolerance_rate']:.3f}; "
                f"adjudicate={len(row['claim_alignment']['needs_adjudication'])}"
            )
        if missing:
            print("missing: " + ", ".join(missing))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
