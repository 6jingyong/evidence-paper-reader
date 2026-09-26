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
merge_route = _load_module("epr_merge_route", ROOT / "merge_route.py")
build_context = _load_module("epr_build_context", ROOT / "build_context.py")
module_checks_mod = _load_module("epr_module_checks", ROOT / "module_checks.py")

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
CONTEXT_BASE_REFERENCES = [
    "core-contract.md",
    "evidence-viability.md",
    "evidence-types.md",
    "audit-ledger-format.md",
]

CRITICAL_GUARDS = {
    "G101": "raw semantic route required",
    "G102": "semantic claim ids match ledger",
    "G103": "semantic claim text matches ledger",
    "G104": "routing recomputation succeeds from source-backed artifacts",
    "G105": "cached merged route cannot replace raw semantic routing",
    "G106": "cached merged route matches recomputation",
    "G107": "generated context bundle required",
    "G108": "generated context can be deterministically rebuilt",
    "G109": "generated context matches deterministic materialization",
    "G110": "required evidence inventory is present",
    "G111": "forbidden evidence inventory is absent",
    "G112": "inventory viability matches ledger",
    "G113": "inventory claim identity matches ledger",
    "G114": "inventory evidence topology aligns with ledger",
    "G115": "canonical rendered audit passes public validation",
    "G116": "structured ledger passes internal validation",
    "G117": "routed methodological modules have execution records",
    "G118": "module execution records match routed obligations",
    "G119": "unresolved routed checks cannot coexist with sufficient support",
    "G120": "raw semantic route satisfies its schema",
    "G121": "cached merged route satisfies its schema",
    "G122": "evidence inventory satisfies its schema",
    "G123": "recomputed route preserves raw semantic requirements independently",
    "G124": "generated context structurally matches route independently",
    "G125": "generated context embeds exact routed reference bodies independently",
    "G126": "raw semantic obligations reach execution artifacts independently",
}


def _guard(code: str, message: str) -> str:
    if code not in CRITICAL_GUARDS:
        raise ValueError(f"unknown critical guard code: {code}")
    return f"[{code}] {message}"


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

    routed_claims = route.get("routed_claims")
    if not isinstance(routed_claims, list) or not routed_claims:
        errors.append("route.routed_claims must be a non-empty list")
    else:
        for index, item in enumerate(routed_claims, start=1):
            if not isinstance(item, dict):
                errors.append(f"route.routed_claims[{index}] must be an object")
                continue
            if item.get("claim_id") != f"C{index}":
                errors.append(
                    f"route.routed_claims[{index}].claim_id must be C{index}"
                )
            if not isinstance(item.get("claim_text"), str) or not item["claim_text"].strip():
                errors.append(
                    f"route.routed_claims[{index}].claim_text must be a non-empty string"
                )

    try:
        requirements = module_checks_mod.required_by_claim(route)
    except ValueError as exc:
        errors.append(str(exc))
    else:
        if routed_claims and [x.get("claim_id") for x in routed_claims] != [
            x["claim_id"] for x in requirements
        ]:
            errors.append(
                "route.claim_module_requirements must match routed_claims IDs/order"
            )

    return errors


def validate_semantic_commitments(semantic: dict, route: dict) -> list[str]:
    """Independent minimum oracle for semantic requirements.

    This intentionally does not call merge_route.merge() or build_context helpers.
    It checks only commitments that must survive every valid merge implementation.
    """
    errors: list[str] = []
    modules = route.get("modules")
    requirements = route.get("claim_module_requirements")
    if not isinstance(modules, list) or not isinstance(requirements, list):
        return ["route lacks module structures required for independent semantic checks"]

    module_set = set(modules)
    requirements_by_claim = {
        item.get("claim_id"): set(item.get("modules", []))
        for item in requirements
        if isinstance(item, dict) and isinstance(item.get("modules"), list)
    }

    claims = semantic.get("claims", [])
    semantic_decisions_by_module: dict[str, list[str]] = {}
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        claim_id = claim.get("claim_id")
        routes = claim.get("routes")
        if not isinstance(routes, dict):
            continue
        required_for_claim = requirements_by_claim.get(claim_id, set())
        for module, decision in routes.items():
            semantic_decisions_by_module.setdefault(module, []).append(decision)
            if decision != "required":
                continue
            if module not in module_set:
                errors.append(
                    f"{claim_id}: semantic required module missing from merged route: {module}"
                )
            if module not in required_for_claim:
                errors.append(
                    f"{claim_id}: semantic required module missing from claim requirements: {module}"
                )

    for module, decisions in semantic_decisions_by_module.items():
        if decisions and set(decisions) == {"not_required"}:
            if module in module_set:
                errors.append(
                    f"merged routing retained {module} despite every semantic decision being not_required"
                )
            leaked_claims = sorted(
                claim_id
                for claim_id, modules_for_claim in requirements_by_claim.items()
                if module in modules_for_claim
            )
            if leaked_claims:
                errors.append(
                    f"{module} leaked into claim requirements despite semantic not_required: "
                    + ", ".join(leaked_claims)
                )

    inventory_decisions = [
        claim.get("inventory")
        for claim in claims
        if isinstance(claim, dict)
    ]
    if "required" in inventory_decisions and route.get("use_evidence_inventory") is not True:
        errors.append(
            "semantic required evidence inventory was dropped by merged routing"
        )
    if inventory_decisions and set(inventory_decisions) == {"not_required"}:
        if route.get("use_evidence_inventory") is not False:
            errors.append(
                "merged routing enabled evidence inventory despite every semantic decision being not_required"
            )

    return errors


def validate_context_structure(context_bundle: str, route: dict) -> list[str]:
    """Independent structural oracle for the generated context manifest."""
    errors: list[str] = []
    expected_refs = list(CONTEXT_BASE_REFERENCES)
    if route.get("use_evidence_inventory") is True:
        expected_refs.append("evidence-inventory-format.md")
    for module in route.get("modules", []):
        if module not in expected_refs:
            expected_refs.append(module)

    lines = context_bundle.splitlines()
    expected_path = f"- recommended path: {route.get('recommended_path')}"
    expected_inventory = (
        "- evidence inventory required: yes"
        if route.get("use_evidence_inventory") is True
        else "- evidence inventory required: no"
    )
    expected_included = "- included references: " + ", ".join(expected_refs)

    if lines.count(expected_path) != 1:
        errors.append("context recommended-path manifest does not match route")
    if lines.count(expected_inventory) != 1:
        errors.append("context inventory-required manifest does not match route")
    if lines.count(expected_included) != 1:
        errors.append("context included-reference manifest does not match route")

    begin_refs = [
        line.removeprefix("## BEGIN REFERENCE: ")
        for line in lines
        if line.startswith("## BEGIN REFERENCE: ")
    ]
    end_refs = [
        line.removeprefix("## END REFERENCE: ")
        for line in lines
        if line.startswith("## END REFERENCE: ")
    ]
    if begin_refs != expected_refs:
        errors.append(
            "context embedded reference order/content does not match independently expected route references"
        )
    if end_refs != expected_refs:
        errors.append(
            "context reference closing markers do not match independently expected route references"
        )

    requirement_lines = []
    for item in route.get("claim_module_requirements", []):
        if not isinstance(item, dict):
            continue
        modules = item.get("modules", [])
        rendered = ", ".join(modules) if modules else "none"
        requirement_lines.append(
            f"  - {item.get('claim_id')}: {rendered}"
        )
    for line in requirement_lines:
        if lines.count(line) != 1:
            errors.append(
                "context claim-module requirement manifest does not match route: "
                + line.strip()
            )

    return errors


def validate_semantic_execution(
    semantic: dict,
    module_checks: dict | None,
    inventory: dict | None,
    context_bundle: str | None,
) -> list[str]:
    """Check raw semantic obligations directly against execution artifacts."""
    errors: list[str] = []
    checks_by_claim: dict[str, set[str]] = {}
    if isinstance(module_checks, dict):
        claims = module_checks.get("claims")
        if isinstance(claims, list):
            for item in claims:
                if not isinstance(item, dict):
                    continue
                claim_id = item.get("claim_id")
                checks = item.get("checks")
                if not isinstance(claim_id, str) or not isinstance(checks, list):
                    continue
                checks_by_claim[claim_id] = {
                    check.get("module")
                    for check in checks
                    if isinstance(check, dict) and isinstance(check.get("module"), str)
                }

    claims = semantic.get("claims", [])
    inventory_required = False
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        claim_id = claim.get("claim_id")
        routes = claim.get("routes")
        if isinstance(routes, dict):
            required = {
                module
                for module, decision in routes.items()
                if decision == "required"
            }
            if required:
                actual = checks_by_claim.get(claim_id, set())
                missing = sorted(required - actual)
                if missing:
                    errors.append(
                        f"{claim_id}: semantic required module(s) missing from execution checks: "
                        + ", ".join(missing)
                    )
                if context_bundle is not None:
                    for module in sorted(required):
                        marker = f"## BEGIN REFERENCE: {module}"
                        if context_bundle.count(marker) != 1:
                            errors.append(
                                f"{claim_id}: semantic required module missing from execution context: {module}"
                            )
        if claim.get("inventory") == "required":
            inventory_required = True

    if inventory_required and inventory is None:
        errors.append(
            "semantic required evidence inventory is missing from execution artifacts"
        )

    return errors


def validate_context_reference_bodies(context_bundle: str, route: dict) -> list[str]:
    """Verify embedded routed reference bodies without calling the renderer."""
    errors: list[str] = []
    expected_refs = list(CONTEXT_BASE_REFERENCES)
    if route.get("use_evidence_inventory") is True:
        expected_refs.append("evidence-inventory-format.md")
    for module in route.get("modules", []):
        if module not in expected_refs:
            expected_refs.append(module)

    for name in expected_refs:
        begin = f"## BEGIN REFERENCE: {name}\n\n"
        end = f"\n\n## END REFERENCE: {name}"
        if context_bundle.count(begin) != 1 or context_bundle.count(end) != 1:
            errors.append(
                f"routed reference markers missing or duplicated: {name}"
            )
            continue
        embedded = context_bundle.split(begin, 1)[1].split(end, 1)[0]
        path = SKILL_ROOT / "references" / name
        try:
            source = path.read_text(encoding="utf-8").rstrip()
        except OSError as exc:
            errors.append(f"cannot read routed reference {name}: {exc}")
            continue
        if embedded != source:
            errors.append(
                f"embedded reference body does not exactly match source file: {name}"
            )

    return errors


def _expected_claim_ids(audit: dict) -> list[str]:
    claims = audit.get("claims", [])
    if not isinstance(claims, list):
        return []
    return [f"C{i}" for i in range(1, len(claims) + 1)]


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
    semantic: dict | None,
    lexical: dict | None,
    route: dict | None,
    inventory: dict | None,
    evidence_types_text: str,
    router_text: str | None = None,
    context_bundle: str | None = None,
    module_checks: dict | None = None,
) -> list[str]:
    errors = [
        _guard("G116", f"ledger: {x}")
        for x in render_audit.validate_ledger(audit)
    ]

    scope = audit.get("scope_status")
    viability = audit.get("evidence_viability")
    claim_audit = scope != "out of scope" and viability != "non-auditable"

    recomputed_route = None
    if claim_audit:
        if semantic is None:
            errors.append(_guard(
                "G101",
                "route: auditable/partially auditable work requires the raw semantic-route artifact",
            ))
        else:
            semantic_errors = merge_route.validate_semantic(semantic)
            errors.extend(
                _guard("G120", f"semantic route: {x}")
                for x in semantic_errors
            )

            actual_ids = [
                item.get("claim_id")
                for item in semantic.get("claims", [])
                if isinstance(item, dict)
            ]
            expected_ids = _expected_claim_ids(audit)
            if actual_ids != expected_ids:
                errors.append(_guard(
                    "G102",
                    "semantic route: claim IDs must exactly match final ledger claims in order: "
                    + ", ".join(expected_ids),
                ))

            semantic_text = [
                item.get("claim_text", "").strip()
                for item in semantic.get("claims", [])
                if isinstance(item, dict)
            ]
            audit_text = _claim_contents(audit)
            if semantic_text != audit_text:
                errors.append(_guard(
                    "G103",
                    "semantic route: claim text/order must exactly match the final ledger; rerun routing after claim changes",
                ))

            if (
                not semantic_errors
                and actual_ids == expected_ids
                and semantic_text == audit_text
            ):
                try:
                    recomputed_route = build_context.recompute_route(
                        semantic,
                        lexical,
                        router_text,
                    )
                except ValueError as exc:
                    errors.extend(
                        _guard("G104", f"route recomputation: {x}")
                        for x in str(exc).splitlines()
                    )

    if route is not None:
        errors.extend(
            _guard("G121", f"route artifact: {x}")
            for x in validate_route_result(route)
        )
        if recomputed_route is None:
            if claim_audit:
                errors.append(_guard(
                    "G105",
                    "route artifact: merged route cannot substitute for raw semantic routing",
                ))
        elif route != recomputed_route:
            errors.append(_guard(
                "G106",
                "route artifact: supplied merged route does not match deterministic recomputation",
            ))

    if claim_audit and semantic is not None and recomputed_route is not None:
        errors.extend(
            _guard("G123", f"semantic commitments: {x}")
            for x in validate_semantic_commitments(semantic, recomputed_route)
        )

    if claim_audit and semantic is not None:
        errors.extend(
            _guard("G126", f"semantic execution: {x}")
            for x in validate_semantic_execution(
                semantic,
                module_checks,
                inventory,
                context_bundle,
            )
        )

    effective_route = recomputed_route if recomputed_route is not None else route
    if claim_audit and effective_route is None and semantic is not None:
        errors.append(_guard(
            "G104",
            "route: deterministic merge did not produce a usable route",
        ))

    if claim_audit and recomputed_route is not None:
        if context_bundle is None:
            errors.append(_guard(
                "G107",
                "context: claim audit requires the generated audit-context bundle",
            ))
        else:
            try:
                expected_context = build_context.render_bundle(recomputed_route)
            except ValueError as exc:
                errors.extend(
                    _guard("G108", f"context: {x}")
                    for x in str(exc).splitlines()
                )
            else:
                if context_bundle != expected_context:
                    errors.append(_guard(
                        "G109",
                        "context: supplied audit-context bundle does not match deterministic route materialization",
                    ))

    if claim_audit and recomputed_route is not None and context_bundle is not None:
        errors.extend(
            _guard("G124", f"context structure: {x}")
            for x in validate_context_structure(context_bundle, recomputed_route)
        )
        errors.extend(
            _guard("G125", f"context reference body: {x}")
            for x in validate_context_reference_bodies(
                context_bundle,
                recomputed_route,
            )
        )

    if claim_audit and recomputed_route is not None:
        requirements = recomputed_route.get("claim_module_requirements", [])
        has_required_checks = any(item.get("modules") for item in requirements)
        if has_required_checks and module_checks is None:
            errors.append(_guard(
                "G117",
                "module checks: routed methodological modules require module-checks.json",
            ))
        elif module_checks is not None:
            module_check_errors = module_checks_mod.validate(
                module_checks,
                recomputed_route,
            )
            errors.extend(
                _guard("G118", f"module checks: {x}")
                for x in module_check_errors
            )
            if not module_check_errors:
                errors.extend(
                    _guard("G119", f"module/support alignment: {x}")
                    for x in module_checks_mod.check_support_alignment(
                        module_checks,
                        audit,
                    )
                )

    if effective_route is not None:
        use_inventory = effective_route.get("use_evidence_inventory")
        if use_inventory is True and inventory is None:
            errors.append(_guard(
                "G110",
                "inventory: recomputed route requires evidence inventory but none was supplied",
            ))
        if use_inventory is False and inventory is not None:
            errors.append(_guard(
                "G111",
                "inventory: supplied inventory conflicts with recomputed route; rerun routing instead of bypassing it",
            ))

    if inventory is not None:
        inventory_errors = inventory_mod.validate_inventory(inventory)
        errors.extend(
            _guard("G122", f"inventory: {x}")
            for x in inventory_errors
        )

        if inventory.get("evidence_viability") != viability:
            errors.append(_guard(
                "G112",
                "inventory: evidence_viability does not match the final audit ledger",
            ))

        inventory_claims = [
            item.get("content", "").strip()
            for item in inventory.get("claims", [])
            if isinstance(item, dict)
        ]
        audit_claims = _claim_contents(audit)
        if inventory_claims != audit_claims:
            errors.append(_guard(
                "G113",
                "inventory: claim contents/order drifted between evidence inventory and final audit ledger",
            ))

        if not inventory_errors:
            errors.extend(
                _guard("G114", f"inventory alignment: {x}")
                for x in inventory_mod.check_audit_alignment(inventory, audit)
            )

    if not errors:
        markdown = render_audit.render(audit)
        allowed = markdown_validator.evidence_labels(evidence_types_text)
        errors.extend(
            _guard("G115", f"rendered audit: {x}")
            for x in markdown_validator.validate(markdown, allowed)
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--semantic-route", type=Path)
    parser.add_argument(
        "--router-text",
        type=Path,
        help="Plain source text used to deterministically recompute lexical routing.",
    )
    parser.add_argument(
        "--lexical-route",
        type=Path,
        help="Optional cached lexical route; checked against --router-text and never trusted alone.",
    )
    parser.add_argument(
        "--route",
        type=Path,
        help="Optional cached merged route; checked against deterministic recomputation.",
    )
    parser.add_argument("--inventory", type=Path)
    parser.add_argument(
        "--module-checks",
        type=Path,
        help="Per-claim execution record for every routed methodological module.",
    )
    parser.add_argument(
        "--context-bundle",
        type=Path,
        help="Generated audit-context.md; verified byte-for-byte against deterministic routing.",
    )
    parser.add_argument("--evidence-types", type=Path, default=EVIDENCE_TYPES)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        audit = _load_json(args.ledger, "ledger")
        semantic = _load_json(args.semantic_route, "semantic route") if args.semantic_route else None
        lexical = _load_json(args.lexical_route, "lexical route") if args.lexical_route else None
        router_text = (
            args.router_text.read_text(encoding="utf-8", errors="ignore")
            if args.router_text else None
        )
        route = _load_json(args.route, "route") if args.route else None
        inventory = _load_json(args.inventory, "inventory") if args.inventory else None
        module_checks = (
            _load_json(args.module_checks, "module checks")
            if args.module_checks else None
        )
        context_bundle = (
            args.context_bundle.read_text(encoding="utf-8")
            if args.context_bundle else None
        )
        evidence_types_text = args.evidence_types.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    errors = validate_gate(
        audit,
        semantic=semantic,
        lexical=lexical,
        router_text=router_text,
        route=route,
        inventory=inventory,
        evidence_types_text=evidence_types_text,
        context_bundle=context_bundle,
        module_checks=module_checks,
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
