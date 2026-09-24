#!/usr/bin/env python3
"""Render a structured Evidence Paper Reader ledger into canonical Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCOPE_STATUSES = {"in scope", "partially in scope", "out of scope"}
CLAIM_TYPES = {"observational", "methodological", "mechanistic", "performance", "generality", "intervention"}
CONCLUSION_STRENGTHS = {"weak", "medium", "strong"}
SUPPORT_LEVELS = {"sufficient", "partial", "insufficient", "unclear"}
PROVENANCE = {"paper-local", "external citation", "mixed"}
DEPENDENCE = {
    "single-source",
    "shared-source convergence",
    "partially independent convergence",
    "independent convergence",
    "unclear",
}
VALUE_LEVELS = {"high", "medium", "low", "unclear"}

VALUE_KEYS = [
    ("result", "result value"),
    ("method", "method value"),
    ("theory_or_insight", "theory or insight value"),
    ("research_design", "research design value"),
    ("material_or_documentation", "material or documentation value"),
]

TEMPLATE = {
    "scope_status": "in scope",
    "paper_type": "",
    "reader_conclusion": "",
    "claims": [
        {
            "content": "",
            "claim_type": "observational",
            "conclusion_strength": "weak",
            "support": {
                "evidence_type": [],
                "evidence_provenance": "paper-local",
                "evidence_nodes": ["E1"],
                "upstream_claims": [],
                "evidence_dependence": "single-source",
                "source_location": "",
                "support_level": "unclear",
                "reason": "",
                "external_dependency": "none"
            }
        },
        {
            "content": "",
            "claim_type": "observational",
            "conclusion_strength": "weak",
            "support": {
                "evidence_type": [],
                "evidence_provenance": "paper-local",
                "evidence_nodes": ["E2"],
                "upstream_claims": [],
                "evidence_dependence": "single-source",
                "source_location": "",
                "support_level": "unclear",
                "reason": "",
                "external_dependency": "none"
            }
        },
        {
            "content": "",
            "claim_type": "observational",
            "conclusion_strength": "weak",
            "support": {
                "evidence_type": [],
                "evidence_provenance": "paper-local",
                "evidence_nodes": ["E3"],
                "upstream_claims": [],
                "evidence_dependence": "single-source",
                "source_location": "",
                "support_level": "unclear",
                "reason": "",
                "external_dependency": "none"
            }
        }
    ],
    "usable": {
        "results": "",
        "methods_or_design": "",
        "materials_or_documentation": ""
    },
    "downweight": {
        "worth_noticing": "",
        "cautious_or_ignore": ""
    },
    "value_breakdown": {
        "result": "unclear",
        "method": "unclear",
        "theory_or_insight": "unclear",
        "research_design": "unclear",
        "material_or_documentation": "unclear"
    },
    "uncertainty_and_follow_up": ""
}


def _text(value, field: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
        return ""
    return value.strip()


def _choice(value, allowed: set[str], field: str, errors: list[str]) -> str:
    if value not in allowed:
        errors.append(f"{field} must be one of: {', '.join(sorted(allowed))}")
        return ""
    return value


def validate_ledger(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["ledger must be a JSON object"]

    scope = _choice(data.get("scope_status"), SCOPE_STATUSES, "scope_status", errors)
    _text(data.get("paper_type"), "paper_type", errors)
    _text(data.get("reader_conclusion"), "reader_conclusion", errors)

    claims = data.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []

    if scope in {"in scope", "partially in scope"} and not (3 <= len(claims) <= 5):
        errors.append("in-scope ledgers must contain 3 to 5 claims")
    if scope == "out of scope" and claims:
        errors.append("out-of-scope ledgers must use an empty claims list")
    if scope == "out of scope":
        _text(data.get("not_applicable_reason"), "not_applicable_reason", errors)

    seen_nodes: set[str] = set()
    rendered_support = []
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            errors.append(f"claim {index} must be an object")
            continue
        _text(claim.get("content"), f"claim {index}.content", errors)
        _choice(claim.get("claim_type"), CLAIM_TYPES, f"claim {index}.claim_type", errors)
        _choice(
            claim.get("conclusion_strength"),
            CONCLUSION_STRENGTHS,
            f"claim {index}.conclusion_strength",
            errors,
        )
        support = claim.get("support")
        if not isinstance(support, dict):
            errors.append(f"claim {index}.support must be an object")
            continue

        evidence_type = support.get("evidence_type")
        if not isinstance(evidence_type, list) or not evidence_type or not all(
            isinstance(x, str) and x.strip() for x in evidence_type
        ):
            errors.append(f"claim {index}.support.evidence_type must be a non-empty string list")

        provenance = _choice(
            support.get("evidence_provenance"),
            PROVENANCE,
            f"claim {index}.support.evidence_provenance",
            errors,
        )

        nodes = support.get("evidence_nodes")
        if not isinstance(nodes, list) or not nodes:
            errors.append(f"claim {index}.support.evidence_nodes must be a non-empty list")
            nodes = []
        normalized_nodes = []
        for node in nodes:
            if not isinstance(node, str) or not node.startswith("E") or not node[1:].isdigit() or int(node[1:]) < 1:
                errors.append(f"claim {index}: invalid evidence node {node!r}")
                continue
            if node in normalized_nodes:
                errors.append(f"claim {index}: duplicate evidence node {node}")
            normalized_nodes.append(node)
            seen_nodes.add(node)

        upstream = support.get("upstream_claims", [])
        if not isinstance(upstream, list) or not all(isinstance(x, int) for x in upstream):
            errors.append(f"claim {index}.support.upstream_claims must be a list of earlier claim numbers")
            upstream = []
        if len(upstream) != len(set(upstream)):
            errors.append(f"claim {index}: duplicate upstream claim")
        if any(x < 1 or x >= index for x in upstream):
            errors.append(f"claim {index}: upstream claims must reference earlier claims only")

        dependence = _choice(
            support.get("evidence_dependence"),
            DEPENDENCE,
            f"claim {index}.support.evidence_dependence",
            errors,
        )
        if dependence in {
            "shared-source convergence",
            "partially independent convergence",
            "independent convergence",
        } and len(normalized_nodes) < 2:
            errors.append(f"claim {index}: convergence requires at least two evidence nodes")

        _text(support.get("source_location"), f"claim {index}.support.source_location", errors)
        level = _choice(
            support.get("support_level"),
            SUPPORT_LEVELS,
            f"claim {index}.support.support_level",
            errors,
        )
        _text(support.get("reason"), f"claim {index}.support.reason", errors)
        dependency = _text(
            support.get("external_dependency"),
            f"claim {index}.support.external_dependency",
            errors,
        )
        if provenance in {"external citation", "mixed"} and dependency == "none":
            errors.append(f"claim {index}: {provenance} requires a named external_dependency")

        rendered_support.append({
            "nodes": set(normalized_nodes),
            "upstream": upstream,
            "level": level,
        })

    for index, item in enumerate(rendered_support, start=1):
        if not item["upstream"] or item["level"] != "sufficient":
            continue
        upstream_nodes = set()
        upstream_levels = []
        for ref in item["upstream"]:
            if ref <= len(rendered_support):
                upstream_nodes.update(rendered_support[ref - 1]["nodes"])
                upstream_levels.append(rendered_support[ref - 1]["level"])
        if item["nodes"].issubset(upstream_nodes) and any(
            level != "sufficient" for level in upstream_levels
        ):
            errors.append(
                f"claim {index}: downstream claim cannot be sufficient without new evidence "
                "when a required upstream claim is not sufficient"
            )

    usable = data.get("usable")
    if not isinstance(usable, dict):
        errors.append("usable must be an object")
    else:
        for key in ["results", "methods_or_design", "materials_or_documentation"]:
            _text(usable.get(key), f"usable.{key}", errors)

    downweight = data.get("downweight")
    if not isinstance(downweight, dict):
        errors.append("downweight must be an object")
    else:
        for key in ["worth_noticing", "cautious_or_ignore"]:
            _text(downweight.get(key), f"downweight.{key}", errors)

    values = data.get("value_breakdown")
    if not isinstance(values, dict):
        errors.append("value_breakdown must be an object")
    else:
        for key, _ in VALUE_KEYS:
            _choice(values.get(key), VALUE_LEVELS, f"value_breakdown.{key}", errors)

    _text(data.get("uncertainty_and_follow_up"), "uncertainty_and_follow_up", errors)
    return errors


def _join_nodes(nodes: list[str]) -> str:
    return " + ".join(nodes)


def _join_upstream(upstream: list[int]) -> str:
    if not upstream:
        return "none"
    return " + ".join(f"C{i}" for i in upstream)


def render(data: dict) -> str:
    errors = validate_ledger(data)
    if errors:
        raise ValueError("\n".join(errors))

    scope = data["scope_status"]
    lines = [
        "# reader-side paper audit",
        "",
        "## 1. reader conclusion",
        f"- scope status: {scope}",
        f"- paper type: {data['paper_type'].strip()}",
        "",
        data["reader_conclusion"].strip(),
        "",
        "## 2. core claims",
        "",
    ]

    if scope == "out of scope":
        reason = data["not_applicable_reason"].strip()
        lines.extend([f"not applicable — {reason}", "", "## 3. evidence and support", "", f"not applicable — {reason}", ""])
    else:
        for index, claim in enumerate(data["claims"], start=1):
            lines.extend([
                f"### claim {index}",
                f"- content: {claim['content'].strip()}",
                f"- claim type: {claim['claim_type']}",
                f"- conclusion strength: {claim['conclusion_strength']}",
                "",
            ])
        lines.extend(["## 3. evidence and support", ""])
        for index, claim in enumerate(data["claims"], start=1):
            support = claim["support"]
            lines.extend([
                f"### claim {index}",
                f"- evidence type: {' + '.join(x.strip() for x in support['evidence_type'])}",
                f"- evidence provenance: {support['evidence_provenance']}",
                f"- evidence nodes: {_join_nodes(support['evidence_nodes'])}",
                f"- upstream claims: {_join_upstream(support.get('upstream_claims', []))}",
                f"- evidence dependence: {support['evidence_dependence']}",
                f"- source location: {support['source_location'].strip()}",
                f"- support level: {support['support_level']}",
                f"- reason: {support['reason'].strip()}",
                f"- external dependency: {support['external_dependency'].strip()}",
                "",
            ])

    lines.extend([
        "## 4. what is usable",
        "",
        "### usable results",
        data["usable"]["results"].strip(),
        "",
        "### usable methods or design",
        data["usable"]["methods_or_design"].strip(),
        "",
        "### usable materials or documentation",
        data["usable"]["materials_or_documentation"].strip(),
        "",
        "## 5. what to downweight",
        "",
        "### worth noticing but should be downweighted",
        data["downweight"]["worth_noticing"].strip(),
        "",
        "### should be treated cautiously or ignored",
        data["downweight"]["cautious_or_ignore"].strip(),
        "",
        "## 6. value breakdown",
    ])
    for key, label in VALUE_KEYS:
        lines.append(f"- {label}: {data['value_breakdown'][key]}")
    lines.extend([
        "",
        "## 7. uncertainty and follow-up",
        "",
        data["uncertainty_and_follow_up"].strip(),
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", nargs="?", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, indent=2, ensure_ascii=False))
        return 0
    if args.ledger is None:
        parser.error("ledger is required unless --template is used")

    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    errors = validate_ledger(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if args.check:
        print("PASS: ledger satisfies the renderer input contract")
        return 0

    markdown = render(data)
    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
