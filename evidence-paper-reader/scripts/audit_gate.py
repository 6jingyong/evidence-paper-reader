#!/usr/bin/env python3
"""Fail-closed execution gate for Evidence Paper Reader audits."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SKILL_ROOT = ROOT.parent
EVIDENCE_TYPES = SKILL_ROOT / "references" / "evidence-types.md"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render_audit = _load_module("epr_render_audit", ROOT / "render_audit.py")
inventory_mod = _load_module("epr_evidence_inventory", ROOT / "evidence_inventory.py")
markdown_validator = _load_module("epr_validate_audit", ROOT / "validate_audit.py")

TRAP_MODULES = {
    "figure-and-table-traps.md",
    "statistical-traps.md",
    "measurement-traps.md",
    "study-design-traps.md",
    "evidence-topology.md",
}
FINAL_MODULES = {
    *TRAP_MODULES,
    "evidence-dependence.md",
    "claim-evidence-links.md",
    "claim-dependencies.md",
    "follow-up-boundaries.md",
    "false-positive-guards.md",
}


def _load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def validate_route_result(route: dict) -> list[str]:
    errors: list[str] = []

    modules = route.get("modules")
    if not isinstance(modules, list) or not all(isinstance(x, str) for x in modules):
        errors.append("route.modules must be a string list")
        modules = []
    if len(modules) != len(set(modules)):
        errors.append("route.modules must not contain duplicates")

    unknown = [x for x in modules if x not in FINAL_MODULES]
    if unknown:
        errors.append("route contains unknown module(s): " + ", ".join(sorted(unknown)))

    if not isinstance(route.get("use_evidence_inventory"), bool):
        errors.append("route.use_evidence_inventory must be boolean")

    trap_count = sum(module in TRAP_MODULES for module in modules)
    guard_present = "false-positive-guards.md" in modules
    if trap_count and not guard_present:
        errors.append("route with trap modules must include false-positive-guards.md")
    if not trap_count and guard_present:
        errors.append("false-positive-guards.md requires at least one trap module")

    primary_count = route.get("primary_module_count")
    if not isinstance(primary_count, int) or isinstance(primary_count, bool):
        errors.append("route.primary_module_count must be an integer")
    elif primary_count != trap_count:
        errors.append(
            f"route.primary_module_count={primary_count} does not match trap-module count {trap_count}"
        )

    recommended = route.get("recommended_path")
    expected_path = "full" if trap_count >= 3 else "flash"
    if recommended not in {"flash", "full"}:
        errors.append("route.recommended_path must be flash or full")
    elif recommended != expected_path:
        errors.append(
            f"route.recommended_path={recommended} conflicts with primary-module count; expected {expected_path}"
        )

    if not isinstance(route.get("inventory_basis"), str) or not route.get("inventory_basis", "").strip():
        errors.append("route.inventory_basis must be a non-empty string")

    return errors


def _claim_contents(audit: dict) -> list[str]:
    claims = audit.get("claims", [])
    if not isinstance(claims, list):
        return []
    result = []
    for claim in claims:
        if isinstance(claim, dict) and isinstance(claim.get("content"), str):
            result.append(claim["content"].strip())
        else:
            result.append("")
    return result


def validate_gate(
    audit: dict,
    *,
    route: dict | None,
    inventory: dict | None,
    evidence_types_text: str,
) -> list[str]:
    errors = [f"ledger: {x}" for x in render_audit.validate_ledger(audit)]

    scope = audit.get("scope_status")
    viability = audit.get("evidence_viability")
    claim_audit = scope != "out of scope" and viability != "non-auditable"

    if claim_audit and route is None:
        errors.append("route: auditable/partially auditable work requires a merged route result")

    if route is not None:
        errors.extend(f"route: {x}" for x in validate_route_result(route))
        use_inventory = route.get("use_evidence_inventory")
        if use_inventory is True and inventory is None:
            errors.append("inventory: merged route requires evidence inventory but none was supplied")
        if use_inventory is False and inventory is not None:
            errors.append(
                "inventory: supplied inventory conflicts with merged route; rerun routing instead of bypassing it"
            )

    if inventory is not None:
        inventory_errors = inventory_mod.validate_inventory(inventory)
        errors.extend(f"inventory: {x}" for x in inventory_errors)

        if inventory.get("evidence_viability") != viability:
            errors.append(
                "inventory: evidence_viability does not match the final audit ledger"
            )

        inventory_claims = [
            item.get("content", "").strip()
            for item in inventory.get("claims", [])
            if isinstance(item, dict)
        ]
        audit_claims = _claim_contents(audit)
        if inventory_claims != audit_claims:
            errors.append(
                "inventory: claim contents/order drifted between evidence inventory and final audit ledger"
            )

        if not inventory_errors:
            errors.extend(
                f"inventory alignment: {x}"
                for x in inventory_mod.check_audit_alignment(inventory, audit)
            )

    # A canonical renderer output must also satisfy the public Markdown validator.
    # This catches controlled evidence-label errors that the ledger renderer alone
    # deliberately does not interpret.
    if not errors:
        markdown = render_audit.render(audit)
        allowed = markdown_validator.evidence_labels(evidence_types_text)
        errors.extend(
            f"rendered audit: {x}"
            for x in markdown_validator.validate(markdown, allowed)
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--route", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--evidence-types", type=Path, default=EVIDENCE_TYPES)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        audit = _load_json(args.ledger, "ledger")
        route = _load_json(args.route, "route") if args.route else None
        inventory = _load_json(args.inventory, "inventory") if args.inventory else None
        evidence_types_text = args.evidence_types.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    errors = validate_gate(
        audit,
        route=route,
        inventory=inventory,
        evidence_types_text=evidence_types_text,
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if args.check:
        print("PASS: audit passed the execution gate")
        return 0

    markdown = render_audit.render(audit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
