#!/usr/bin/env python3
"""Score lexical and semantic routing on adversarial cases."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
BENCH = Path(__file__).parent
ROUTER_SCRIPT = ROOT / "evidence-paper-reader" / "scripts" / "suggest_modules.py"
MERGER_SCRIPT = ROOT / "evidence-paper-reader" / "scripts" / "merge_route.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


lexical_router = load_module("router_bench_lexical", ROUTER_SCRIPT)
route_merger = load_module("router_bench_merger", MERGER_SCRIPT)

ROUTES = route_merger.ROUTES


def lexical_modules(case: dict) -> tuple[set[str], bool]:
    result = lexical_router.suggest_modules(case["claim"] + "\n" + case["text"])
    modules = {
        item["module"]
        for item in result["suggested"]
        if item["module"] in ROUTES
    }
    return modules, bool(result["use_evidence_inventory"])


def score_modules(cases: list[dict], route_by_case: dict[str, tuple[set[str], bool]]) -> dict:
    required_total = 0
    required_hit = 0
    forbidden_total = 0
    forbidden_hit = 0
    inventory_total = len(cases)
    inventory_correct = 0
    exact = 0
    rows = []

    for case in cases:
        modules, inventory = route_by_case[case["case_id"]]
        required = set(case["required_modules"])
        forbidden = set(case["forbidden_modules"])
        required_total += len(required)
        required_hit += len(required & modules)
        forbidden_total += len(forbidden)
        forbidden_hit += len(forbidden & modules)
        inventory_correct += int(inventory == case["inventory_required"])

        relevant_observed = modules & (required | forbidden)
        expected_observed = required
        exact_case = (
            required.issubset(modules)
            and not (forbidden & modules)
            and inventory == case["inventory_required"]
        )
        exact += int(exact_case)
        rows.append({
            "case_id": case["case_id"],
            "kind": case["kind"],
            "required": sorted(required),
            "forbidden": sorted(forbidden),
            "observed": sorted(modules),
            "missing_required": sorted(required - modules),
            "triggered_forbidden": sorted(forbidden & modules),
            "inventory_expected": case["inventory_required"],
            "inventory_observed": inventory,
            "exact": exact_case,
        })

    return {
        "case_count": len(cases),
        "required_recall": required_hit / required_total if required_total else 1.0,
        "forbidden_trigger_rate": forbidden_hit / forbidden_total if forbidden_total else 0.0,
        "inventory_accuracy": inventory_correct / inventory_total if inventory_total else 1.0,
        "exact_case_rate": exact / len(cases) if cases else 1.0,
        "cases": rows,
    }


def load_semantic_responses(path: Path) -> dict[str, dict]:
    responses = {}
    for file in path.glob("*.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        responses[file.stem] = data
    return responses


def semantic_route(data: dict) -> tuple[set[str], bool]:
    errors = route_merger.validate_semantic(data)
    if errors:
        raise ValueError("; ".join(errors))
    claim = data["claims"][0]
    modules = {
        module for module, decision in claim["routes"].items()
        if decision == "required"
    }
    inventory = claim["inventory"] == "required"
    return modules, inventory


def perfect_semantic(case: dict) -> dict:
    routes = {}
    required = set(case["required_modules"])
    for module in ROUTES:
        routes[module] = "required" if module in required else "not_required"
    return {
        "claims": [{
            "claim_id": "C1",
            "routes": routes,
            "inventory": "required" if case["inventory_required"] else "not_required",
            "reason": case["rationale"],
        }]
    }


def merged_routes(cases: list[dict], semantic_by_case: dict[str, dict]) -> dict[str, tuple[set[str], bool]]:
    out = {}
    for case in cases:
        lexical = lexical_router.suggest_modules(case["claim"] + "\n" + case["text"])
        merged = route_merger.merge(lexical, semantic_by_case[case["case_id"]])
        modules = {m for m in merged["modules"] if m in ROUTES}
        out[case["case_id"]] = (modules, merged["use_evidence_inventory"])
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--specs", type=Path, default=BENCH / "case_specs.json")
    parser.add_argument("--semantic-responses", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cases = json.loads(args.specs.read_text(encoding="utf-8"))["cases"]
    lexical = {case["case_id"]: lexical_modules(case) for case in cases}
    result = {"lexical_baseline": score_modules(cases, lexical)}

    if args.semantic_responses:
        semantic = load_semantic_responses(args.semantic_responses)
        missing = [c["case_id"] for c in cases if c["case_id"] not in semantic]
        if missing:
            raise SystemExit("missing semantic responses: " + ", ".join(missing))
        semantic_routes = {cid: semantic_route(data) for cid, data in semantic.items()}
        result["semantic"] = score_modules(cases, semantic_routes)
        result["merged"] = score_modules(cases, merged_routes(cases, semantic))
    else:
        perfect = {case["case_id"]: perfect_semantic(case) for case in cases}
        result["perfect_semantic_reference"] = score_modules(
            cases,
            {cid: semantic_route(data) for cid, data in perfect.items()},
        )
        result["perfect_merged_reference"] = score_modules(
            cases,
            merged_routes(cases, perfect),
        )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for name, section in result.items():
            print(name)
            for key in [
                "required_recall",
                "forbidden_trigger_rate",
                "inventory_accuracy",
                "exact_case_rate",
            ]:
                print(f"- {key}: {section[key]:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
