#!/usr/bin/env python3
"""Score paired hidden/visible metadata-halo benchmark responses."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
SUPPORT_ORDER = {"insufficient": 0, "partial": 1, "sufficient": 2}
DOWNWEIGHT_ORDER = {"none": 0, "moderate": 1, "strong": 2}
SCOPE = {"in scope", "partially in scope", "out of scope"}
SUPPORT = {"sufficient", "partial", "insufficient", "unclear"}
DOWNWEIGHT = set(DOWNWEIGHT_ORDER)


def load_responses(path: Path) -> dict[str, dict]:
    found = {}
    for file in sorted(path.glob("*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))
        found[data["packet_id"]] = data
    return found


def validate_response(data: dict) -> list[str]:
    errors = []
    packet_id = data.get("packet_id", "<unknown>")
    if not isinstance(packet_id, str) or not packet_id.startswith("P-"):
        errors.append("invalid packet_id")
    if data.get("scope_status") not in SCOPE:
        errors.append(f"{packet_id}: invalid scope status")
    anchors = data.get("anchors")
    if not isinstance(anchors, list) or len(anchors) != 3:
        errors.append(f"{packet_id}: expected exactly 3 anchors")
        return errors
    ids = [x.get("id") for x in anchors]
    if ids != ["A1", "A2", "A3"]:
        errors.append(f"{packet_id}: anchors must be A1,A2,A3 in order")
    for a in anchors:
        if a.get("support_level") not in SUPPORT:
            errors.append(f"{packet_id}/{a.get('id')}: invalid support")
        if a.get("downweight") not in DOWNWEIGHT:
            errors.append(f"{packet_id}/{a.get('id')}: invalid downweight")
        if not isinstance(a.get("follow_up_required"), bool):
            errors.append(f"{packet_id}/{a.get('id')}: follow_up_required must be boolean")
        if not isinstance(a.get("reason"), str) or not a["reason"].strip():
            errors.append(f"{packet_id}/{a.get('id')}: reason required")
    if not isinstance(data.get("requested_follow_up"), list):
        errors.append(f"{packet_id}: requested_follow_up must be a list")
    return errors


def support_direction(hidden: str, visible: str) -> str:
    if hidden == visible:
        return "same"
    if "unclear" in {hidden, visible}:
        return "unclear_transition"
    delta = SUPPORT_ORDER[visible] - SUPPORT_ORDER[hidden]
    return "visible_more_permissive" if delta > 0 else "visible_more_skeptical"


def score(responses: dict[str, dict], expectations: dict, manifest: list[dict]) -> dict:
    pair_rows = []
    direction_counts = Counter()
    scope_flips = 0
    followup_delta_total = 0
    downweight_delta_total = 0
    exact_anchor_match = 0
    total_anchors = 0
    expectation_hits = Counter()

    exp_by_case = {x["case_id"]: x for x in expectations["cases"]}
    manifest_by_case = {}
    for row in manifest:
        manifest_by_case.setdefault(row["case_id"], {})[row["condition"]] = row

    group_rows = {"flagship_high_attention": [], "low_attention_nontraditional": []}

    for case_id in sorted(exp_by_case):
        pair = manifest_by_case[case_id]
        h = responses[pair["hidden"]["packet_id"]]
        v = responses[pair["visible"]["packet_id"]]
        if h["scope_status"] != v["scope_status"]:
            scope_flips += 1

        h_anchors = {x["id"]: x for x in h["anchors"]}
        v_anchors = {x["id"]: x for x in v["anchors"]}
        anchor_rows = []
        for anchor_id in ["A1", "A2", "A3"]:
            ha = h_anchors[anchor_id]
            va = v_anchors[anchor_id]
            direction = support_direction(ha["support_level"], va["support_level"])
            direction_counts[direction] += 1
            total_anchors += 1
            if direction == "same":
                exact_anchor_match += 1
            dw_delta = DOWNWEIGHT_ORDER[va["downweight"]] - DOWNWEIGHT_ORDER[ha["downweight"]]
            fu_delta = int(va["follow_up_required"]) - int(ha["follow_up_required"])
            downweight_delta_total += dw_delta
            followup_delta_total += fu_delta

            expected = exp_by_case[case_id]["anchors"][anchor_id]
            expectation_hits[f"hidden_{h_anchors[anchor_id]['support_level'] == expected}"] += 1
            expectation_hits[f"visible_{v_anchors[anchor_id]['support_level'] == expected}"] += 1

            anchor_rows.append({
                "id": anchor_id,
                "hidden_support": ha["support_level"],
                "visible_support": va["support_level"],
                "support_direction": direction,
                "downweight_delta_visible_minus_hidden": dw_delta,
                "followup_delta_visible_minus_hidden": fu_delta,
                "reference_support": expected,
            })

        attention = pair["visible"]["attention"]
        group_key = (
            "flagship_high_attention"
            if "flagship/high-attention" in attention
            else "low_attention_nontraditional"
        )
        group_rows[group_key].append({
            "case_id": case_id,
            "anchors": anchor_rows,
        })

        pair_rows.append({
            "case_id": case_id,
            "scope_hidden": h["scope_status"],
            "scope_visible": v["scope_status"],
            "scope_flip": h["scope_status"] != v["scope_status"],
            "requested_followup_count_hidden": len(h["requested_follow_up"]),
            "requested_followup_count_visible": len(v["requested_follow_up"]),
            "anchors": anchor_rows,
        })

    group_effects = {}
    for group, rows in group_rows.items():
        directions = Counter(
            anchor["support_direction"]
            for row in rows
            for anchor in row["anchors"]
        )
        group_effects[group] = {
            "pair_count": len(rows),
            "support_directions": dict(directions),
            "visible_more_permissive": directions["visible_more_permissive"],
            "visible_more_skeptical": directions["visible_more_skeptical"],
            "net_downweight_delta_visible_minus_hidden": sum(
                anchor["downweight_delta_visible_minus_hidden"]
                for row in rows
                for anchor in row["anchors"]
            ),
            "net_followup_delta_visible_minus_hidden": sum(
                anchor["followup_delta_visible_minus_hidden"]
                for row in rows
                for anchor in row["anchors"]
            ),
        }

    return {
        "pair_count": len(pair_rows),
        "anchor_count": total_anchors,
        "exact_support_match_rate": exact_anchor_match / total_anchors if total_anchors else None,
        "support_directions": dict(direction_counts),
        "scope_flips": scope_flips,
        "net_followup_delta_visible_minus_hidden": followup_delta_total,
        "net_downweight_delta_visible_minus_hidden": downweight_delta_total,
        "group_effects": group_effects,
        "reference_accuracy": {
            "hidden": expectation_hits["hidden_True"] / total_anchors if total_anchors else None,
            "visible": expectation_hits["visible_True"] / total_anchors if total_anchors else None,
        },
        "pairs": pair_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "packets" / "manifest.json",
    )
    parser.add_argument(
        "--expectations",
        type=Path,
        default=ROOT / "reference_expectations.json",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    responses = load_responses(args.responses)
    expectations = json.loads(args.expectations.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_by_case = {}
    for row in manifest:
        manifest_by_case.setdefault(row["case_id"], {})[row["condition"]] = row

    errors = []
    for case in expectations["cases"]:
        pair = manifest_by_case.get(case["case_id"], {})
        for condition in ["hidden", "visible"]:
            row = pair.get(condition)
            if row is None:
                errors.append(f"missing manifest row: {case['case_id']}/{condition}")
                continue
            packet_id = row["packet_id"]
            if packet_id not in responses:
                errors.append(f"missing response: {packet_id}")
            else:
                errors.extend(validate_response(responses[packet_id]))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    result = score(responses, expectations, manifest)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"pairs: {result['pair_count']}; anchors: {result['anchor_count']}")
        print(f"exact hidden/visible support match: {result['exact_support_match_rate']:.3f}")
        print(f"support directions: {result['support_directions']}")
        print(f"scope flips: {result['scope_flips']}")
        print(
            "net visible-hidden follow-up delta: "
            f"{result['net_followup_delta_visible_minus_hidden']}"
        )
        print(
            "net visible-hidden downweight delta: "
            f"{result['net_downweight_delta_visible_minus_hidden']}"
        )
        print(f"group effects: {result['group_effects']}")
        print(f"reference accuracy: {result['reference_accuracy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
