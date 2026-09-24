#!/usr/bin/env python3
"""Summarize the 40-source prestige/attention benchmark."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

TIERS = [
    "flagship_high_attention",
    "ordinary_a",
    "ordinary_b",
    "low_attention_nontraditional",
]
SUPPORT = ["sufficient", "partial", "insufficient", "unclear"]


def validate(data: dict) -> list[str]:
    errors = []
    cases = data.get("cases", [])
    if len(cases) != 40:
        errors.append(f"expected 40 cases, found {len(cases)}")

    domains = data.get("selected_domains", [])
    if len(domains) != 10 or len(set(domains)) != 10:
        errors.append("expected exactly 10 unique selected domains")

    by_domain = defaultdict(list)
    for case in cases:
        by_domain[case.get("domain")].append(case)
        for field in [
            "id", "domain", "tier", "source_kind", "title", "year", "venue",
            "source_url", "tier_reason", "access", "modules", "scope_status",
            "narrow_claim_support", "broad_claim_support", "main_boundary",
        ]:
            if field not in case:
                errors.append(f"{case.get('id', '<unknown>')}: missing {field}")

    for domain in domains:
        xs = by_domain.get(domain, [])
        if len(xs) != 4:
            errors.append(f"{domain}: expected 4 cases, found {len(xs)}")
            continue
        found = Counter(x.get("tier") for x in xs)
        for tier in TIERS:
            if found[tier] != 1:
                errors.append(f"{domain}: expected one {tier}, found {found[tier]}")

    ids = [x.get("id") for x in cases]
    if len(ids) != len(set(ids)):
        errors.append("case ids must be unique")

    for case in cases:
        if case.get("narrow_claim_support") not in SUPPORT:
            errors.append(f"{case.get('id')}: invalid narrow support")
        if case.get("broad_claim_support") not in SUPPORT:
            errors.append(f"{case.get('id')}: invalid broad support")
        if case.get("scope_status") not in {"in scope", "partially in scope", "out of scope"}:
            errors.append(f"{case.get('id')}: invalid scope status")

    return errors


def summary(data: dict) -> dict:
    cases = data["cases"]
    tier_stats = {}
    for tier in TIERS:
        xs = [x for x in cases if x["tier"] == tier]
        tier_stats[tier] = {
            "n": len(xs),
            "scope": dict(Counter(x["scope_status"] for x in xs)),
            "narrow_support": dict(Counter(x["narrow_claim_support"] for x in xs)),
            "broad_support": dict(Counter(x["broad_claim_support"] for x in xs)),
            "source_kinds": dict(Counter(x["source_kind"] for x in xs)),
        }

    module_counts = Counter()
    for case in cases:
        module_counts.update(case["modules"])

    return {
        "benchmark_id": data["benchmark_id"],
        "selection_seed": data["selection_seed"],
        "case_count": len(cases),
        "domain_count": len(set(x["domain"] for x in cases)),
        "tier_stats": tier_stats,
        "module_counts": dict(module_counts.most_common()),
        "prestige_blind_checks": {
            "flagship_broad_not_sufficient": sum(
                x["tier"] == "flagship_high_attention"
                and x["broad_claim_support"] != "sufficient"
                for x in cases
            ),
            "low_attention_narrow_sufficient": sum(
                x["tier"] == "low_attention_nontraditional"
                and x["narrow_claim_support"] == "sufficient"
                for x in cases
            ),
            "low_attention_broad_insufficient_or_unclear": sum(
                x["tier"] == "low_attention_nontraditional"
                and x["broad_claim_support"] in {"insufficient", "unclear"}
                for x in cases
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "cases",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("cases.json"),
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.cases.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    result = summary(data)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print(f"{result['benchmark_id']}: {result['case_count']} cases / {result['domain_count']} domains")
    for tier, stats in result["tier_stats"].items():
        print(
            f"- {tier}: narrow={stats['narrow_support']}; "
            f"broad={stats['broad_support']}; scope={stats['scope']}"
        )
    checks = result["prestige_blind_checks"]
    print(
        "- checks: flagship broad not sufficient="
        f"{checks['flagship_broad_not_sufficient']}/10; "
        "low-attention narrow sufficient="
        f"{checks['low_attention_narrow_sufficient']}/10; "
        "low-attention broad insufficient/unclear="
        f"{checks['low_attention_broad_insufficient_or_unclear']}/10"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
