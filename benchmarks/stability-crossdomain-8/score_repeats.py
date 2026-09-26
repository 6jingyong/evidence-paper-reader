#!/usr/bin/env python3
"""Score repeated-run stability and reference correctness across domains."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
SUPPORT = {"sufficient", "partial", "insufficient", "unclear"}
VIABILITY = {"auditable", "partially auditable", "non-auditable"}
ALLOWED_MODULES = {
    "figure-and-table-traps.md",
    "statistical-traps.md",
    "measurement-traps.md",
    "study-design-traps.md",
    "evidence-topology.md",
    "evidence-dependence.md",
    "claim-evidence-links.md",
    "claim-dependencies.md",
    "follow-up-boundaries.md",
}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def pairwise_exact(values: list[object]) -> float:
    pairs = list(itertools.combinations(values, 2))
    if not pairs:
        return 1.0
    return sum(a == b for a, b in pairs) / len(pairs)


def pairwise_set_jaccard(values: list[set[str]]) -> float:
    pairs = list(itertools.combinations(values, 2))
    if not pairs:
        return 1.0
    return sum(jaccard(a, b) for a, b in pairs) / len(pairs)


def validate_response(data: dict, case: dict) -> list[str]:
    errors = []
    if data.get("case_id") != case["case_id"]:
        errors.append("case_id mismatch")
    if data.get("evidence_viability") not in VIABILITY:
        errors.append("invalid evidence_viability")

    candidate_ids = {x["id"] for x in case["candidates"]}
    selected = data.get("selected_claim_ids")
    if not isinstance(selected, list) or not all(x in candidate_ids for x in selected):
        errors.append("selected_claim_ids must contain known candidate IDs")
        selected = []
    if len(selected) != len(set(selected)):
        errors.append("selected_claim_ids contain duplicates")
    viability = data.get("evidence_viability")
    if viability == "auditable" and not (3 <= len(selected) <= 5):
        errors.append("auditable response must select 3 to 5 claims")
    if viability == "partially auditable" and not (1 <= len(selected) <= 5):
        errors.append("partially auditable response must select 1 to 5 claims")
    if viability == "non-auditable" and selected:
        errors.append("non-auditable response must select zero claims")

    modules = data.get("modules")
    if not isinstance(modules, list) or not all(isinstance(x, str) for x in modules):
        errors.append("modules must be a string list")
        modules = []
    if len(modules) != len(set(modules)):
        errors.append("modules contain duplicates")
    unknown_modules = [x for x in modules if x not in ALLOWED_MODULES]
    if unknown_modules:
        errors.append("unknown module(s): " + ", ".join(unknown_modules))

    if not isinstance(data.get("use_evidence_inventory"), bool):
        errors.append("use_evidence_inventory must be boolean")

    support = data.get("support")
    if not isinstance(support, list):
        errors.append("support must be a list")
        support = []
    support_ids = []
    for item in support:
        cid = item.get("claim_id")
        level = item.get("support_level")
        support_ids.append(cid)
        if cid not in candidate_ids:
            errors.append(f"unknown support claim {cid}")
        if level not in SUPPORT:
            errors.append(f"invalid support level for {cid}")
    if len(support_ids) != len(set(support_ids)):
        errors.append("duplicate support claim")
    if set(support_ids) != set(selected):
        errors.append("support claim IDs must exactly match selected_claim_ids")
    return errors


def load_runs(responses_dir: Path, matrix: list[dict], cases: dict[str, dict]) -> dict[str, list[dict]]:
    by_packet = {}
    for file in responses_dir.glob("*.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        pid = data.get("packet_id") or file.stem
        by_packet[pid] = data

    grouped = defaultdict(list)
    errors = []
    for job in matrix:
        pid = job["packet_id"]
        if pid not in by_packet:
            errors.append(f"missing response for {pid}")
            continue
        response = by_packet[pid]
        response["case_id"] = response.get("case_id", job["case_id"])
        local_errors = validate_response(response, cases[job["case_id"]])
        errors.extend(f"{pid}: {e}" for e in local_errors)
        grouped[job["case_id"]].append(response)
    if errors:
        raise ValueError("\n".join(errors))
    return grouped


def case_metrics(case: dict, runs: list[dict]) -> dict:
    ref = case["reference"]
    selected_sets = [set(r["selected_claim_ids"]) for r in runs]
    module_sets = [set(r["modules"]) for r in runs]
    viability_values = [r["evidence_viability"] for r in runs]
    inventory_values = [r["use_evidence_inventory"] for r in runs]

    required = set(ref["required_claims"])
    optional = set(ref["optional_claims"])
    forbidden = set(ref["forbidden_claims"])
    required_modules = set(ref["modules_required"])
    allowed_modules = required_modules | set(ref["modules_allowed_extra"])

    claim_required_recall = sum(len(s & required) for s in selected_sets) / (len(runs) * len(required))
    forbidden_selection_rate = (
        sum(len(s & forbidden) for s in selected_sets) / (len(runs) * len(forbidden))
        if forbidden else 0.0
    )
    route_required_recall = (
        sum(len(s & required_modules) for s in module_sets) / (len(runs) * len(required_modules))
        if required_modules else 1.0
    )
    route_unallowed_rate = (
        sum(len(s - allowed_modules) for s in module_sets)
        / max(1, sum(max(1, len(s)) for s in module_sets))
    )

    support_vectors = []
    support_accuracy_hits = 0
    support_accuracy_total = 0
    reference_support = ref["support"]
    all_support_ids = sorted(reference_support)
    for run in runs:
        support_map = {x["claim_id"]: x["support_level"] for x in run["support"]}
        vector = tuple(support_map.get(cid, "not_selected") for cid in all_support_ids)
        support_vectors.append(vector)
        scored_support_ids = set(ref["required_claims"]) | (
            set(ref["optional_claims"]) & set(run["selected_claim_ids"])
        )
        for cid in scored_support_ids:
            if cid not in reference_support:
                continue
            support_accuracy_total += 1
            support_accuracy_hits += int(
                support_map.get(cid, "not_selected") == reference_support[cid]
            )

    claim_modes = Counter(tuple(sorted(s)) for s in selected_sets)
    route_modes = Counter(tuple(sorted(s)) for s in module_sets)

    return {
        "domain": case["domain"],
        "source": case["source"],
        "run_count": len(runs),
        "stability": {
            "viability_pairwise_exact": pairwise_exact(viability_values),
            "claim_selection_pairwise_jaccard": pairwise_set_jaccard(selected_sets),
            "routing_pairwise_jaccard": pairwise_set_jaccard(module_sets),
            "inventory_pairwise_exact": pairwise_exact(inventory_values),
            "support_vector_pairwise_exact": pairwise_exact(support_vectors),
        },
        "reference": {
            "viability_accuracy": sum(v == ref["viability"] for v in viability_values) / len(runs),
            "required_claim_recall": claim_required_recall,
            "forbidden_claim_selection_rate": forbidden_selection_rate,
            "required_module_recall": route_required_recall,
            "unallowed_module_rate": route_unallowed_rate,
            "inventory_overtrigger_rate": sum(bool(v) for v in inventory_values) / len(runs),
            "support_accuracy": support_accuracy_hits / support_accuracy_total,
        },
        "modes": {
            "claim_selection": list(claim_modes.most_common(1)[0][0]),
            "routing": list(route_modes.most_common(1)[0][0]),
            "viability": Counter(viability_values).most_common(1)[0][0],
            "inventory": Counter(inventory_values).most_common(1)[0][0],
        },
    }


def aggregate(per_case: dict[str, dict]) -> dict:
    layers = [
        ("viability", "viability_pairwise_exact"),
        ("claim_selection", "claim_selection_pairwise_jaccard"),
        ("routing", "routing_pairwise_jaccard"),
        ("support", "support_vector_pairwise_exact"),
    ]
    stability = {
        label: sum(x["stability"][key] for x in per_case.values()) / len(per_case)
        for label, key in layers
    }
    weakest = min(stability, key=stability.get)
    return {
        "mean_layer_stability": stability,
        "weakest_layer": weakest,
        "case_count": len(per_case),
        "run_count": sum(x["run_count"] for x in per_case.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path)
    parser.add_argument("--specs", type=Path, default=ROOT / "case_specs.json")
    parser.add_argument("--matrix", type=Path, default=ROOT / "runs" / "run_matrix.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    specs = json.loads(args.specs.read_text(encoding="utf-8"))
    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    cases = {x["case_id"]: x for x in specs["cases"]}
    try:
        grouped = load_runs(args.responses, matrix, cases)
    except ValueError as exc:
        print(f"FAIL: {exc}")
        return 1

    expected_repeats = specs["repeats_per_case"]
    missing = [cid for cid in cases if len(grouped.get(cid, [])) != expected_repeats]
    if missing:
        print("FAIL: wrong repeat count for: " + ", ".join(missing))
        return 1

    per_case = {cid: case_metrics(cases[cid], grouped[cid]) for cid in cases}
    result = {
        "benchmark_id": specs["benchmark_id"],
        "aggregate": aggregate(per_case),
        "cases": per_case,
    }
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(
            f"{specs['benchmark_id']}: {result['aggregate']['run_count']} runs; "
            f"weakest layer={result['aggregate']['weakest_layer']}"
        )
        for layer, value in result["aggregate"]["mean_layer_stability"].items():
            print(f"- {layer}: {value:.3f}")
        for cid, row in per_case.items():
            print(
                f"- {cid} {row['domain']}: "
                f"claim={row['stability']['claim_selection_pairwise_jaccard']:.3f}; "
                f"route={row['stability']['routing_pairwise_jaccard']:.3f}; "
                f"support={row['stability']['support_vector_pairwise_exact']:.3f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
