#!/usr/bin/env python3
"""Validate per-claim execution of routed methodological modules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TRAP_MODULES = {
    "figure-and-table-traps.md",
    "statistical-traps.md",
    "measurement-traps.md",
    "study-design-traps.md",
    "evidence-topology.md",
}
STATUSES = {"clear", "residual-concern", "unclear"}


def required_by_claim(route: dict) -> list[dict]:
    items = route.get("claim_module_requirements")
    if not isinstance(items, list):
        raise ValueError("route.claim_module_requirements must be a list")
    result = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"route claim requirement {index} must be an object")
        claim_id = item.get("claim_id")
        modules = item.get("modules")
        if claim_id != f"C{index}":
            raise ValueError(f"route claim requirement {index}.claim_id must be C{index}")
        if not isinstance(modules, list) or not all(isinstance(x, str) for x in modules):
            raise ValueError(f"{claim_id}.modules must be a string list")
        if len(modules) != len(set(modules)):
            raise ValueError(f"{claim_id}.modules must not contain duplicates")
        result.append({"claim_id": claim_id, "modules": modules})
    return result


def template(route: dict) -> dict:
    claims = []
    for item in required_by_claim(route):
        checks = []
        for module in item["modules"]:
            check = {
                "module": module,
                "status": "unclear",
                "source_locations": [],
                "reason": "",
            }
            if module in TRAP_MODULES:
                check["mitigation_checked"] = False
            checks.append(check)
        claims.append({
            "claim_id": item["claim_id"],
            "checks": checks,
        })
    return {"claims": claims}


def validate(data: dict, route: dict) -> list[str]:
    errors: list[str] = []
    try:
        expected = required_by_claim(route)
    except ValueError as exc:
        return [f"route: {exc}"]

    claims = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(claims, list):
        return ["module checks must contain a claims list"]

    expected_ids = [item["claim_id"] for item in expected]
    actual_ids = [
        item.get("claim_id") if isinstance(item, dict) else None
        for item in claims
    ]
    if actual_ids != expected_ids:
        errors.append(
            "module-check claim IDs/order must exactly match routed claims: "
            + ", ".join(expected_ids)
        )
        return errors

    for expected_item, item in zip(expected, claims):
        claim_id = expected_item["claim_id"]
        checks = item.get("checks") if isinstance(item, dict) else None
        if not isinstance(checks, list):
            errors.append(f"{claim_id}.checks must be a list")
            continue

        expected_modules = expected_item["modules"]
        actual_modules = [
            check.get("module") if isinstance(check, dict) else None
            for check in checks
        ]
        if actual_modules != expected_modules:
            errors.append(
                f"{claim_id}.checks modules/order must exactly match routed requirements: "
                + (", ".join(expected_modules) if expected_modules else "none")
            )
            continue

        for check in checks:
            module = check["module"]
            status = check.get("status")
            if status not in STATUSES:
                errors.append(
                    f"{claim_id} {module}: status must be one of: "
                    + ", ".join(sorted(STATUSES))
                )
            locations = check.get("source_locations")
            if (
                not isinstance(locations, list)
                or not locations
                or not all(isinstance(x, str) and x.strip() for x in locations)
            ):
                errors.append(
                    f"{claim_id} {module}: source_locations must be a non-empty string list"
                )
            elif len({x.strip() for x in locations}) != len(locations):
                errors.append(
                    f"{claim_id} {module}: source_locations must not contain duplicates"
                )

            reason = check.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{claim_id} {module}: reason must be a non-empty string")

            if module in TRAP_MODULES:
                if check.get("mitigation_checked") is not True:
                    errors.append(
                        f"{claim_id} {module}: mitigation_checked must be true after applying false-positive guards"
                    )
            elif "mitigation_checked" in check and not isinstance(
                check.get("mitigation_checked"), bool
            ):
                errors.append(
                    f"{claim_id} {module}: mitigation_checked must be boolean when present"
                )

    return errors


def check_support_alignment(data: dict, audit: dict) -> list[str]:
    """Propagate unresolved routed checks into final claim support."""
    errors: list[str] = []
    claims = data.get("claims") if isinstance(data, dict) else None
    audit_claims = audit.get("claims") if isinstance(audit, dict) else None
    if not isinstance(claims, list) or not isinstance(audit_claims, list):
        return errors
    if len(claims) != len(audit_claims):
        return errors

    for index, (item, audit_claim) in enumerate(zip(claims, audit_claims), start=1):
        if not isinstance(item, dict) or not isinstance(audit_claim, dict):
            continue
        checks = item.get("checks")
        support = audit_claim.get("support")
        if not isinstance(checks, list) or not isinstance(support, dict):
            continue

        unresolved = [
            check.get("module")
            for check in checks
            if isinstance(check, dict) and check.get("status") == "unclear"
        ]
        if unresolved and support.get("support_level") == "sufficient":
            errors.append(
                f"C{index}: sufficient support conflicts with unresolved routed "
                "module check(s): " + ", ".join(str(x) for x in unresolved)
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checks", nargs="?", type=Path)
    parser.add_argument("--route", type=Path, required=True)
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        route = json.loads(args.route.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.template:
        print(json.dumps(template(route), indent=2, ensure_ascii=False))
        return 0

    if args.checks is None:
        parser.error("checks is required unless --template is used")

    try:
        data = json.loads(args.checks.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    errors = validate(data, route)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if args.check:
        print("PASS: module checks satisfy routed obligations")
    else:
        print("PASS: module checks satisfy routed obligations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
