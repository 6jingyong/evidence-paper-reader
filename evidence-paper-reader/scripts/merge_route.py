#!/usr/bin/env python3
"""Merge lexical and semantic routing decisions for Evidence Paper Reader."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROUTES = [
    "figure-and-table-traps.md",
    "statistical-traps.md",
    "measurement-traps.md",
    "study-design-traps.md",
    "evidence-topology.md",
    "evidence-dependence.md",
    "claim-evidence-links.md",
    "claim-dependencies.md",
    "follow-up-boundaries.md",
]
TRAP_MODULES = {
    "figure-and-table-traps.md",
    "statistical-traps.md",
    "measurement-traps.md",
    "study-design-traps.md",
    "evidence-topology.md",
}
DECISIONS = {"required", "not_required", "unclear"}


def validate_semantic(data: dict) -> list[str]:
    errors = []
    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        return ["semantic route must contain a non-empty claims list"]

    seen = set()
    for i, claim in enumerate(claims, start=1):
        cid = claim.get("claim_id")
        if not isinstance(cid, str) or not cid.startswith("C") or not cid[1:].isdigit():
            errors.append(f"claim {i}: invalid claim_id")
        elif cid in seen:
            errors.append(f"claim {i}: duplicate claim_id {cid}")
        else:
            seen.add(cid)

        routes = claim.get("routes")
        if not isinstance(routes, dict):
            errors.append(f"{cid or i}: routes must be an object")
            continue
        missing = [route for route in ROUTES if route not in routes]
        extra = [route for route in routes if route not in ROUTES]
        if missing:
            errors.append(f"{cid or i}: missing route decisions: {', '.join(missing)}")
        if extra:
            errors.append(f"{cid or i}: unknown route decisions: {', '.join(extra)}")
        for route, decision in routes.items():
            if route in ROUTES and decision not in DECISIONS:
                errors.append(f"{cid or i}: invalid decision for {route}: {decision}")

        if claim.get("inventory") not in DECISIONS:
            errors.append(f"{cid or i}: invalid inventory decision")
        if not isinstance(claim.get("reason"), str) or not claim["reason"].strip():
            errors.append(f"{cid or i}: reason required")
    return errors


def merge(lexical: dict, semantic: dict) -> dict:
    errors = validate_semantic(semantic)
    if errors:
        raise ValueError("\n".join(errors))

    lexical_modules = {
        item["module"]
        for item in lexical.get("suggested", [])
        if item.get("module") in ROUTES
    }

    aggregate = {route: [] for route in ROUTES}
    inventory_decisions = []
    for claim in semantic["claims"]:
        for route in ROUTES:
            aggregate[route].append(claim["routes"][route])
        inventory_decisions.append(claim["inventory"])

    final_modules = []
    route_details = {}
    for route in ROUTES:
        decisions = aggregate[route]
        if "required" in decisions:
            final = True
            basis = "semantic required"
        elif "unclear" in decisions and route in lexical_modules:
            final = True
            basis = "semantic unclear; lexical suggestion preserved"
        else:
            final = False
            basis = (
                "semantic not required"
                if set(decisions) == {"not_required"}
                else "no required semantic route"
            )
        route_details[route] = {
            "lexical_suggested": route in lexical_modules,
            "semantic_decisions": decisions,
            "included": final,
            "basis": basis,
        }
        if final:
            final_modules.append(route)

    lexical_inventory = bool(lexical.get("use_evidence_inventory"))
    if "required" in inventory_decisions:
        use_inventory = True
        inventory_basis = "semantic required"
    elif "unclear" in inventory_decisions and lexical_inventory:
        use_inventory = True
        inventory_basis = "semantic unclear; lexical recommendation preserved"
    else:
        use_inventory = False
        inventory_basis = (
            "semantic not required"
            if set(inventory_decisions) == {"not_required"}
            else "no required semantic inventory route"
        )

    if any(module in TRAP_MODULES for module in final_modules):
        final_modules.append("false-positive-guards.md")

    primary_count = sum(module in TRAP_MODULES for module in final_modules)
    recommended_path = "full" if primary_count >= 3 else "flash"

    return {
        "modules": final_modules,
        "use_evidence_inventory": use_inventory,
        "inventory_basis": inventory_basis,
        "recommended_path": recommended_path,
        "primary_module_count": primary_count,
        "route_details": route_details,
        "lexical_only_modules_removed": sorted(lexical_modules - set(final_modules)),
        "semantic_modules_added": sorted(set(final_modules) - lexical_modules - {"false-positive-guards.md"}),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lexical_route", type=Path)
    parser.add_argument("semantic_route", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        lexical = json.loads(args.lexical_route.read_text(encoding="utf-8"))
        semantic = json.loads(args.semantic_route.read_text(encoding="utf-8"))
        result = merge(lexical, semantic)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Recommended path: {result['recommended_path'].upper()}")
        print("Modules:")
        for module in result["modules"]:
            print(f"- {module}")
        print(
            "Evidence inventory: "
            + ("yes" if result["use_evidence_inventory"] else "no")
            + f" ({result['inventory_basis']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
