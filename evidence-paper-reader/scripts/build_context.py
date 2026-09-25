#!/usr/bin/env python3
"""Build the deterministic methodological context bundle for one paper audit."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SKILL_ROOT = ROOT.parent
REFERENCES = SKILL_ROOT / "references"

BASE_REFERENCES = [
    "core-contract.md",
    "evidence-viability.md",
    "evidence-types.md",
    "audit-ledger-format.md",
]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


merge_route = _load_module("epr_context_merge_route", ROOT / "merge_route.py")
suggest_modules = _load_module("epr_context_suggest_modules", ROOT / "suggest_modules.py")


def _load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _semantic_has_unclear(semantic: dict) -> bool:
    for claim in semantic.get("claims", []):
        if not isinstance(claim, dict):
            continue
        routes = claim.get("routes", {})
        if isinstance(routes, dict) and "unclear" in routes.values():
            return True
        if claim.get("inventory") == "unclear":
            return True
    return False


def recompute_route(
    semantic: dict,
    lexical: dict | None,
    router_text: str | None = None,
) -> dict:
    semantic_errors = merge_route.validate_semantic(semantic)
    if semantic_errors:
        raise ValueError("\n".join(f"semantic route: {x}" for x in semantic_errors))

    if router_text is not None:
        recomputed_lexical = suggest_modules.suggest_modules(router_text)
        if lexical is not None and lexical != recomputed_lexical:
            raise ValueError(
                "cached lexical route does not match deterministic recomputation from router text"
            )
        lexical = recomputed_lexical
    elif lexical is not None:
        raise ValueError(
            "cached lexical route cannot substitute for router text; omit the cache or supply router text"
        )
    elif _semantic_has_unclear(semantic):
        raise ValueError(
            "semantic route contains unclear decisions; router text is required to recompute lexical routing deterministically"
        )
    else:
        lexical = {"suggested": [], "use_evidence_inventory": False}

    return merge_route.merge(lexical, semantic)


def context_files(route: dict) -> list[str]:
    names = list(BASE_REFERENCES)
    if route.get("use_evidence_inventory"):
        names.append("evidence-inventory-format.md")
    for module in route.get("modules", []):
        if module not in names:
            names.append(module)
    return names


def render_bundle(route: dict, reference_root: Path = REFERENCES) -> str:
    names = context_files(route)
    missing = [name for name in names if not (reference_root / name).is_file()]
    if missing:
        raise ValueError("missing routed reference(s): " + ", ".join(missing))

    lines = [
        "# Evidence Paper Reader — generated audit context",
        "",
        "This bundle is generated from the raw semantic route and any lexical route needed to resolve unclear decisions.",
        "Do not substitute unrelated methodology modules for the files listed here. If a claim changes or a new methodological cue appears, rerun routing and rebuild this bundle.",
        "",
        f"- recommended path: {route['recommended_path']}",
        f"- evidence inventory required: {'yes' if route['use_evidence_inventory'] else 'no'}",
        "- routed claims:",
    ]
    for item in route.get("routed_claims", []):
        lines.append(f"  - {item['claim_id']}: {item['claim_text']}")
    lines.extend([
        "- included references: " + ", ".join(names),
        "",
    ])

    for name in names:
        text = (reference_root / name).read_text(encoding="utf-8").rstrip()
        lines.extend([
            "---",
            f"## BEGIN REFERENCE: {name}",
            "",
            text,
            "",
            f"## END REFERENCE: {name}",
            "",
        ])

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--semantic-route", type=Path, required=True)
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
    parser.add_argument("--reference-root", type=Path, default=REFERENCES)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    try:
        semantic = _load_json(args.semantic_route, "semantic route")
        lexical = _load_json(args.lexical_route, "lexical route") if args.lexical_route else None
        router_text = (
            args.router_text.read_text(encoding="utf-8", errors="ignore")
            if args.router_text else None
        )
        route = recompute_route(semantic, lexical, router_text)
        bundle = render_bundle(route, args.reference_root)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.manifest:
        manifest = {
            "routed_claims": route["routed_claims"],
            "recommended_path": route["recommended_path"],
            "use_evidence_inventory": route["use_evidence_inventory"],
            "references": context_files(route),
        }
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(bundle, encoding="utf-8")
    else:
        print(bundle, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
