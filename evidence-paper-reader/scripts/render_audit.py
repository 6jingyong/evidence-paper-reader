#!/usr/bin/env python3
"""Render a structured Evidence Paper Reader ledger into canonical Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCOPE_STATUSES = {"in scope", "partially in scope", "out of scope"}
VIABILITY = {"auditable", "partially auditable", "non-auditable"}
VIABILITY_FLAGS = {
    "critical-method-omission",
    "critical-result-omission",
    "missing-comparator",
    "selective-success-only",
    "self-referential-construct",
    "circular-validation",
    "demo-only",
    "proprietary-black-box",
    "external-dependency-dominant",
    "promotional-asymmetry",
    "source-integrity-failure",
}
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
LEDGER_SCHEMA_VERSION = 4
INFERENCE_TYPES = {
    "direct-result",
    "comparison",
    "statistical-inference",
    "causal",
    "mechanistic",
    "generalization",
    "proxy-to-construct",
    "aggregation",
    "external-import",
}
REASONING_STATUSES = {"direct", "supported", "qualified", "unsupported", "unclear"}
EVIDENCE_RELATIONS = {"supports", "undermines", "mixed", "contextual"}
AUTHOR_BOUNDARY_STATUSES = {"explicit", "partial", "absent", "unclear", "not-applicable"}

VALUE_KEYS = [
    ("result", "result value"),
    ("method", "method value"),
    ("theory_or_insight", "theory or insight value"),
    ("research_design", "research design value"),
    ("material_or_documentation", "material or documentation value"),
]

TEMPLATE = {
    "ledger_schema_version": LEDGER_SCHEMA_VERSION,
    "scope_status": "in scope",
    "evidence_viability": "auditable",
    "viability_flags": [],
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
                "evidence_relations": [
                    {
                        "evidence_node": "E1",
                        "relation": "supports",
                        "reason": "The evidence node bears directly on the bounded claim."
                    }
                ],
                "upstream_claims": [],
                "evidence_dependence": "single-source",
                "source_location": "",
                "support_level": "unclear",
                "reason": "",
                "external_dependency": "none",
                "author_boundary": {
                    "status": "unclear",
                    "summary": "No author-boundary assessment recorded yet.",
                    "source_location": "none"
                }
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
                "evidence_relations": [
                    {
                        "evidence_node": "E2",
                        "relation": "supports",
                        "reason": "The evidence node bears directly on the bounded claim."
                    }
                ],
                "upstream_claims": [],
                "evidence_dependence": "single-source",
                "source_location": "",
                "support_level": "unclear",
                "reason": "",
                "external_dependency": "none",
                "author_boundary": {
                    "status": "unclear",
                    "summary": "No author-boundary assessment recorded yet.",
                    "source_location": "none"
                }
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
                "evidence_relations": [
                    {
                        "evidence_node": "E3",
                        "relation": "supports",
                        "reason": "The evidence node bears directly on the bounded claim."
                    }
                ],
                "upstream_claims": [],
                "evidence_dependence": "single-source",
                "source_location": "",
                "support_level": "unclear",
                "reason": "",
                "external_dependency": "none",
                "author_boundary": {
                    "status": "unclear",
                    "summary": "No author-boundary assessment recorded yet.",
                    "source_location": "none"
                }
            }
        }
    ],
    "reasoning_edges": [
        {
            "edge_id": "R1",
            "target_claim": 1,
            "evidence_nodes": ["E1"],
            "upstream_claims": [],
            "inference_type": "direct-result",
            "reasoning_status": "direct",
            "added_reach": "none",
            "assumptions": []
        },
        {
            "edge_id": "R2",
            "target_claim": 2,
            "evidence_nodes": ["E2"],
            "upstream_claims": [],
            "inference_type": "direct-result",
            "reasoning_status": "direct",
            "added_reach": "none",
            "assumptions": []
        },
        {
            "edge_id": "R3",
            "target_claim": 3,
            "evidence_nodes": ["E3"],
            "upstream_claims": [],
            "inference_type": "direct-result",
            "reasoning_status": "direct",
            "added_reach": "none",
            "assumptions": []
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
    viability = _choice(data.get("evidence_viability"), VIABILITY, "evidence_viability", errors)

    flags = data.get("viability_flags")
    if not isinstance(flags, list) or not all(isinstance(x, str) for x in flags):
        errors.append("viability_flags must be a string list")
        flags = []
    if len(flags) != len(set(flags)):
        errors.append("viability_flags must not contain duplicates")
    unknown_flags = [x for x in flags if x not in VIABILITY_FLAGS]
    if unknown_flags:
        errors.append(f"unknown viability flag(s): {', '.join(unknown_flags)}")
    if viability in {"partially auditable", "non-auditable"} and not flags:
        errors.append(f"{viability} requires at least one viability flag")

    _text(data.get("paper_type"), "paper_type", errors)
    _text(data.get("reader_conclusion"), "reader_conclusion", errors)

    claims = data.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []

    no_claim_audit = scope == "out of scope" or viability == "non-auditable"

    schema_version = data.get("ledger_schema_version", 1)
    if not isinstance(schema_version, int) or schema_version < 1:
        errors.append("ledger_schema_version must be a positive integer")
        schema_version = 1
    if schema_version > LEDGER_SCHEMA_VERSION:
        errors.append(
            f"ledger_schema_version {schema_version} is newer than supported version {LEDGER_SCHEMA_VERSION}"
        )

    if no_claim_audit:
        if claims:
            errors.append("out-of-scope or non-auditable ledgers must use an empty claims list")
        _text(data.get("not_applicable_reason"), "not_applicable_reason", errors)
    elif viability == "auditable":
        if not (3 <= len(claims) <= 5):
            errors.append("auditable ledgers must contain 3 to 5 claims")
    elif viability == "partially auditable":
        if not (1 <= len(claims) <= 5):
            errors.append("partially auditable ledgers must contain 1 to 5 reconstructable claims")

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
            if (
                not isinstance(node, str)
                or not node.startswith("E")
                or not node[1:].isdigit()
                or int(node[1:]) < 1
            ):
                errors.append(f"claim {index}: invalid evidence node {node!r}")
                continue
            if node in normalized_nodes:
                errors.append(f"claim {index}: duplicate evidence node {node}")
            normalized_nodes.append(node)

        if schema_version >= 3:
            relations = support.get("evidence_relations")
            if not isinstance(relations, list):
                errors.append(
                    f"claim {index}.support.evidence_relations must be a list for schema v3"
                )
                relations = []
            relation_nodes = []
            for relation_index, relation in enumerate(relations, start=1):
                if not isinstance(relation, dict):
                    errors.append(
                        f"claim {index}.support.evidence_relations[{relation_index}] must be an object"
                    )
                    continue
                node = relation.get("evidence_node")
                if not isinstance(node, str):
                    errors.append(
                        f"claim {index}.support.evidence_relations[{relation_index}].evidence_node must be a string"
                    )
                    continue
                relation_nodes.append(node)
                _choice(
                    relation.get("relation"),
                    EVIDENCE_RELATIONS,
                    f"claim {index}.support.evidence_relations[{relation_index}].relation",
                    errors,
                )
                _text(
                    relation.get("reason"),
                    f"claim {index}.support.evidence_relations[{relation_index}].reason",
                    errors,
                )
            if len(relation_nodes) != len(set(relation_nodes)):
                errors.append(f"claim {index}: duplicate evidence relation node")
            if set(relation_nodes) != set(normalized_nodes):
                errors.append(
                    f"claim {index}: evidence_relations must cover exactly the claim evidence_nodes"
                )

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

        if schema_version >= 4:
            boundary = support.get("author_boundary")
            if not isinstance(boundary, dict):
                errors.append(f"claim {index}.support.author_boundary must be an object for schema v4")
            else:
                boundary_status = _choice(
                    boundary.get("status"),
                    AUTHOR_BOUNDARY_STATUSES,
                    f"claim {index}.support.author_boundary.status",
                    errors,
                )
                boundary_summary = _text(
                    boundary.get("summary"),
                    f"claim {index}.support.author_boundary.summary",
                    errors,
                )
                boundary_location = _text(
                    boundary.get("source_location"),
                    f"claim {index}.support.author_boundary.source_location",
                    errors,
                )
                if boundary_status in {"explicit", "partial"} and boundary_location == "none":
                    errors.append(
                        f"claim {index}: {boundary_status} author boundary requires a concrete source_location"
                    )
                if level in {"partial", "insufficient", "unclear"} and boundary_status == "not-applicable":
                    errors.append(
                        f"claim {index}: non-sufficient support requires an author-boundary assessment"
                    )
                if boundary_status == "not-applicable" and (
                    boundary_summary != "none" or boundary_location != "none"
                ):
                    errors.append(
                        f"claim {index}: not-applicable author boundary must use summary/source_location 'none'"
                    )
                if boundary_status in {"absent", "unclear"} and boundary_summary == "none":
                    errors.append(
                        f"claim {index}: {boundary_status} author boundary requires a short explanatory summary"
                    )

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

    reasoning_edges = data.get("reasoning_edges")
    if schema_version >= 2 and not no_claim_audit:
        if not isinstance(reasoning_edges, list) or not reasoning_edges:
            errors.append("schema v2 claim audits require a non-empty reasoning_edges list")
            reasoning_edges = []
    elif reasoning_edges is None:
        reasoning_edges = []
    elif not isinstance(reasoning_edges, list):
        errors.append("reasoning_edges must be a list")
        reasoning_edges = []

    parsed_edges = []
    seen_edge_ids = set()
    for edge_index, edge in enumerate(reasoning_edges, start=1):
        if not isinstance(edge, dict):
            errors.append(f"reasoning edge {edge_index} must be an object")
            continue
        edge_id = edge.get("edge_id")
        if (
            not isinstance(edge_id, str)
            or not edge_id.startswith("R")
            or not edge_id[1:].isdigit()
            or int(edge_id[1:]) < 1
        ):
            errors.append(f"reasoning edge {edge_index}: invalid edge_id {edge_id!r}")
            edge_id = ""
        elif edge_id in seen_edge_ids:
            errors.append(f"duplicate reasoning edge_id: {edge_id}")
        seen_edge_ids.add(edge_id)

        target = edge.get("target_claim")
        if not isinstance(target, int) or target < 1 or target > len(claims):
            errors.append(f"{edge_id or f'reasoning edge {edge_index}'}: invalid target_claim")
            target = None

        edge_nodes = edge.get("evidence_nodes")
        if not isinstance(edge_nodes, list) or not all(isinstance(x, str) for x in edge_nodes):
            errors.append(f"{edge_id or f'reasoning edge {edge_index}'}: evidence_nodes must be a string list")
            edge_nodes = []
        if len(edge_nodes) != len(set(edge_nodes)):
            errors.append(f"{edge_id or f'reasoning edge {edge_index}'}: duplicate evidence node")

        edge_upstream = edge.get("upstream_claims")
        if not isinstance(edge_upstream, list) or not all(isinstance(x, int) for x in edge_upstream):
            errors.append(f"{edge_id or f'reasoning edge {edge_index}'}: upstream_claims must be an integer list")
            edge_upstream = []
        if len(edge_upstream) != len(set(edge_upstream)):
            errors.append(f"{edge_id or f'reasoning edge {edge_index}'}: duplicate upstream claim")

        if not edge_nodes and not edge_upstream:
            errors.append(f"{edge_id or f'reasoning edge {edge_index}'}: reasoning edge must have at least one input")

        inference_type = _choice(
            edge.get("inference_type"),
            INFERENCE_TYPES,
            f"{edge_id or f'reasoning edge {edge_index}'}.inference_type",
            errors,
        )
        reasoning_status = _choice(
            edge.get("reasoning_status"),
            REASONING_STATUSES,
            f"{edge_id or f'reasoning edge {edge_index}'}.reasoning_status",
            errors,
        )
        added_reach = _text(
            edge.get("added_reach"),
            f"{edge_id or f'reasoning edge {edge_index}'}.added_reach",
            errors,
        )
        assumptions = edge.get("assumptions")
        if not isinstance(assumptions, list) or not all(
            isinstance(x, str) and x.strip() for x in assumptions
        ):
            errors.append(f"{edge_id or f'reasoning edge {edge_index}'}: assumptions must be a string list")
            assumptions = []
        if len(assumptions) != len(set(assumptions)):
            errors.append(f"{edge_id or f'reasoning edge {edge_index}'}: duplicate assumption")
        if reasoning_status == "direct" and added_reach and added_reach != "none":
            errors.append(f"{edge_id}: direct reasoning must use added_reach 'none'")

        if target is not None and target <= len(rendered_support):
            support_item = rendered_support[target - 1]
            if not set(edge_nodes).issubset(support_item["nodes"]):
                errors.append(f"{edge_id}: reasoning evidence_nodes must be a subset of target claim evidence_nodes")
            if not set(edge_upstream).issubset(set(support_item["upstream"])):
                errors.append(f"{edge_id}: reasoning upstream_claims must be a subset of target claim upstream_claims")
            if any(ref >= target or ref < 1 for ref in edge_upstream):
                errors.append(f"{edge_id}: reasoning upstream claims must reference earlier claims only")

        parsed_edges.append({
            "edge_id": edge_id,
            "target": target,
            "nodes": set(edge_nodes),
            "upstream": set(edge_upstream),
            "status": reasoning_status,
            "inference_type": inference_type,
        })

    if schema_version >= 2 and not no_claim_audit:
        expected_ids = [f"R{i}" for i in range(1, len(parsed_edges) + 1)]
        actual_ids = [edge["edge_id"] for edge in parsed_edges]
        if actual_ids != expected_ids:
            errors.append("reasoning edge IDs must be sequential from R1 in list order")

        for claim_index, support_item in enumerate(rendered_support, start=1):
            edges = [edge for edge in parsed_edges if edge["target"] == claim_index]
            if not edges:
                errors.append(f"claim {claim_index}: schema v2 requires at least one reasoning edge")
                continue
            edge_nodes = set().union(*(edge["nodes"] for edge in edges))
            edge_upstream = set().union(*(edge["upstream"] for edge in edges))
            if edge_nodes != support_item["nodes"]:
                errors.append(
                    f"claim {claim_index}: reasoning edges must cover exactly the claim evidence_nodes"
                )
            if edge_upstream != set(support_item["upstream"]):
                errors.append(
                    f"claim {claim_index}: reasoning edges must cover exactly the claim upstream_claims"
                )

            statuses = {edge["status"] for edge in edges}
            level = support_item["level"]
            if level == "sufficient" and not statuses.issubset({"direct", "supported"}):
                errors.append(
                    f"claim {claim_index}: sufficient support cannot contain qualified/unsupported/unclear reasoning"
                )
            elif level == "partial" and statuses.issubset({"direct", "supported"}):
                errors.append(
                    f"claim {claim_index}: partial support requires at least one qualified/unsupported/unclear reasoning edge"
                )
            elif level == "insufficient" and "unsupported" not in statuses:
                errors.append(
                    f"claim {claim_index}: insufficient support requires at least one unsupported reasoning edge"
                )
            elif level == "unclear" and "unclear" not in statuses:
                errors.append(
                    f"claim {claim_index}: unclear support requires at least one unclear reasoning edge"
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


def _join_viability_flags(flags: list[str]) -> str:
    return "none" if not flags else " + ".join(flags)


def render(data: dict) -> str:
    errors = validate_ledger(data)
    if errors:
        raise ValueError("\n".join(errors))

    scope = data["scope_status"]
    viability = data["evidence_viability"]
    no_claim_audit = scope == "out of scope" or viability == "non-auditable"

    lines = [
        "# reader-side paper audit",
        "",
        "## 1. reader conclusion",
        f"- scope status: {scope}",
        f"- evidence viability: {viability}",
        f"- viability flags: {_join_viability_flags(data['viability_flags'])}",
        f"- paper type: {data['paper_type'].strip()}",
        "",
        data["reader_conclusion"].strip(),
        "",
        "## 2. core claims",
        "",
    ]

    if no_claim_audit:
        reason = data["not_applicable_reason"].strip()
        lines.extend([
            f"not applicable — {reason}",
            "",
            "## 3. evidence and support",
            "",
            f"not applicable — {reason}",
            "",
        ])
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
        edges_by_claim = {}
        for edge in data.get("reasoning_edges", []):
            if isinstance(edge, dict) and isinstance(edge.get("target_claim"), int):
                edges_by_claim.setdefault(edge["target_claim"], []).append(edge)
        for index, claim in enumerate(data["claims"], start=1):
            support = claim["support"]
            claim_edges = edges_by_claim.get(index, [])
            lines.extend([
                f"### claim {index}",
                f"- evidence type: {' + '.join(x.strip() for x in support['evidence_type'])}",
                f"- evidence provenance: {support['evidence_provenance']}",
                f"- evidence nodes: {_join_nodes(support['evidence_nodes'])}",
            ])
            if data.get("ledger_schema_version", 1) >= 3:
                relation_text = " | ".join(
                    f"{item['evidence_node']}={item['relation']} ({item['reason'].strip()})"
                    for item in support.get("evidence_relations", [])
                )
                lines.append(f"- evidence relations: {relation_text}")
            lines.extend([
                f"- upstream claims: {_join_upstream(support.get('upstream_claims', []))}",
                f"- evidence dependence: {support['evidence_dependence']}",
                f"- source location: {support['source_location'].strip()}",
                f"- support level: {support['support_level']}",
                f"- reason: {support['reason'].strip()}",
                f"- external dependency: {support['external_dependency'].strip()}",
            ])
            if data.get("ledger_schema_version", 1) >= 4:
                boundary = support["author_boundary"]
                lines.extend([
                    f"- author boundary: {boundary['status']}",
                    f"- author acknowledgment: {boundary['summary'].strip()}",
                    f"- author-boundary source: {boundary['source_location'].strip()}",
                ])
            if claim_edges:
                lines.append(
                    "- reasoning edges: " + " + ".join(edge["edge_id"] for edge in claim_edges)
                )
                for edge in claim_edges:
                    evidence_inputs = _join_nodes(edge.get("evidence_nodes", [])) or "none"
                    upstream_inputs = _join_upstream(edge.get("upstream_claims", []))
                    assumptions = "none" if not edge.get("assumptions") else " | ".join(
                        item.strip() for item in edge["assumptions"]
                    )
                    lines.extend([
                        f"- {edge['edge_id']} inputs: evidence={evidence_inputs}; upstream={upstream_inputs}",
                        f"- {edge['edge_id']} inference type: {edge['inference_type']}",
                        f"- {edge['edge_id']} reasoning status: {edge['reasoning_status']}",
                        f"- {edge['edge_id']} added reach: {edge['added_reach'].strip()}",
                        f"- {edge['edge_id']} assumptions: {assumptions}",
                    ])
            lines.append("")

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
