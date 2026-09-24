#!/usr/bin/env python3
"""Validate the machine-checkable contract of an Evidence Paper Reader audit."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SECTION_HEADINGS = [
    "## 1. reader conclusion",
    "## 2. core claims",
    "## 3. evidence and support",
    "## 4. what is usable",
    "## 5. what to downweight",
    "## 6. value breakdown",
    "## 7. uncertainty and follow-up",
]

CLAIM_TYPES = {"observational", "methodological", "mechanistic", "performance", "generality", "intervention"}
CONCLUSION_STRENGTHS = {"weak", "medium", "strong"}
SUPPORT_LEVELS = {"sufficient", "partial", "insufficient", "unclear"}
PROVENANCE = {"paper-local", "external citation", "mixed"}
DEPENDENCE = {"single-source", "shared-source convergence", "partially independent convergence", "independent convergence", "unclear"}
VALUE_LEVELS = {"high", "medium", "low", "unclear"}
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
}
EVIDENCE_NODES_PATTERN = re.compile(r"^E[1-9]\d*(?: \+ E[1-9]\d*)*$")
UPSTREAM_CLAIMS_PATTERN = re.compile(r"^C[1-9]\d*(?: \+ C[1-9]\d*)*$")
VALUE_FIELDS = [
    "result value",
    "method value",
    "theory or insight value",
    "research design value",
    "material or documentation value",
]


def evidence_labels(reference_text: str) -> set[str]:
    return set(re.findall(r"^- \*\*(.+?)\*\*:", reference_text, flags=re.MULTILINE))


def _section(text: str, heading: str, next_heading: str | None) -> str:
    start = text.index(heading) + len(heading)
    end = text.index(next_heading, start) if next_heading else len(text)
    return text[start:end]


def _field_values(block: str, field: str) -> list[str]:
    pattern = rf"^- {re.escape(field)}:\s*(.+?)\s*$"
    return re.findall(pattern, block, flags=re.MULTILINE)


def _parse_viability_flags(value: str) -> list[str]:
    if value == "none":
        return []
    return [part.strip() for part in value.split(" + ")]


def validate(text: str, allowed_evidence: set[str]) -> list[str]:
    errors: list[str] = []

    if not text.lstrip().startswith("# reader-side paper audit"):
        errors.append("missing canonical top-level title")

    positions = []
    for heading in SECTION_HEADINGS:
        count = text.count(heading)
        if count != 1:
            errors.append(f"expected exactly one '{heading}', found {count}")
        else:
            positions.append(text.index(heading))
    if len(positions) == len(SECTION_HEADINGS) and positions != sorted(positions):
        errors.append("top-level sections are out of order")

    if errors:
        return errors

    sections = {
        heading: _section(text, heading, SECTION_HEADINGS[i + 1] if i + 1 < len(SECTION_HEADINGS) else None)
        for i, heading in enumerate(SECTION_HEADINGS)
    }

    conclusion = sections[SECTION_HEADINGS[0]]

    scope_values = _field_values(conclusion, "scope status")
    if len(scope_values) != 1 or scope_values[0] not in SCOPE_STATUSES:
        errors.append("section 1 must contain exactly one valid scope status")
    scope = scope_values[0] if len(scope_values) == 1 else None

    viability_values = _field_values(conclusion, "evidence viability")
    if len(viability_values) != 1 or viability_values[0] not in VIABILITY:
        errors.append("section 1 must contain exactly one valid evidence viability")
    viability = viability_values[0] if len(viability_values) == 1 else None

    flag_values = _field_values(conclusion, "viability flags")
    parsed_flags: list[str] = []
    if len(flag_values) != 1:
        errors.append("section 1 must contain exactly one viability flags field")
    else:
        parsed_flags = _parse_viability_flags(flag_values[0])
        if len(parsed_flags) != len(set(parsed_flags)):
            errors.append("viability flags must not contain duplicates")
        unknown_flags = [flag for flag in parsed_flags if flag not in VIABILITY_FLAGS]
        if unknown_flags:
            errors.append(f"unknown viability flag(s): {', '.join(unknown_flags)}")
        if viability in {"partially auditable", "non-auditable"} and not parsed_flags:
            errors.append(f"{viability} requires at least one viability flag")

    if len(_field_values(conclusion, "paper type")) != 1:
        errors.append("section 1 must contain exactly one paper type")

    claims = sections[SECTION_HEADINGS[1]]
    support = sections[SECTION_HEADINGS[2]]

    claim_headers = re.findall(r"^### claim (\d+)\s*$", claims, flags=re.MULTILINE)
    support_headers = re.findall(r"^### claim (\d+)\s*$", support, flags=re.MULTILINE)

    no_claim_audit = scope == "out of scope" or viability == "non-auditable"

    if no_claim_audit:
        if claim_headers or support_headers:
            errors.append("out-of-scope or non-auditable audits must not contain claim blocks")
        if "not applicable" not in claims.lower() or "not applicable" not in support.lower():
            errors.append("out-of-scope or non-auditable audits must mark sections 2 and 3 not applicable")
    elif scope in {"in scope", "partially in scope"} and viability in {"auditable", "partially auditable"}:
        expected = [str(i) for i in range(1, len(claim_headers) + 1)]
        if viability == "auditable" and not (3 <= len(claim_headers) <= 5):
            errors.append("auditable audits must contain 3 to 5 core claims")
        if viability == "partially auditable" and not (1 <= len(claim_headers) <= 5):
            errors.append("partially auditable audits must contain 1 to 5 reconstructable claims")
        if claim_headers != expected:
            errors.append("core claim numbering must be sequential from 1")
        if support_headers != claim_headers:
            errors.append("section 3 claim numbering must exactly match section 2")

        for field, allowed in [
            ("claim type", CLAIM_TYPES),
            ("conclusion strength", CONCLUSION_STRENGTHS),
        ]:
            values = _field_values(claims, field)
            if len(values) != len(claim_headers):
                errors.append(f"every core claim must contain '{field}'")
            for value in values:
                if value not in allowed:
                    errors.append(f"invalid {field}: {value}")

        support_levels = _field_values(support, "support level")
        provenances = _field_values(support, "evidence provenance")
        dependence = _field_values(support, "evidence dependence")
        evidence_nodes = _field_values(support, "evidence nodes")
        upstream_claims = _field_values(support, "upstream claims")
        locations = _field_values(support, "source location")
        dependencies = _field_values(support, "external dependency")
        evidence_values = _field_values(support, "evidence type")
        reasons = _field_values(support, "reason")

        for field, values in [
            ("evidence type", evidence_values),
            ("evidence provenance", provenances),
            ("evidence dependence", dependence),
            ("evidence nodes", evidence_nodes),
            ("upstream claims", upstream_claims),
            ("source location", locations),
            ("support level", support_levels),
            ("reason", reasons),
            ("external dependency", dependencies),
        ]:
            if len(values) != len(claim_headers):
                errors.append(f"every support block must contain '{field}'")

        for value in provenances:
            if value not in PROVENANCE:
                errors.append(f"invalid evidence provenance: {value}")

        parsed_nodes = []
        for value in evidence_nodes:
            if not EVIDENCE_NODES_PATTERN.fullmatch(value):
                errors.append(f"invalid evidence nodes: {value}")
                parsed_nodes.append([])
                continue
            nodes = value.split(" + ")
            if len(nodes) != len(set(nodes)):
                errors.append(f"duplicate evidence node within one support block: {value}")
            parsed_nodes.append(nodes)

        parsed_upstream = []
        for index, value in enumerate(upstream_claims, start=1):
            if value == "none":
                parsed_upstream.append([])
                continue
            if not UPSTREAM_CLAIMS_PATTERN.fullmatch(value):
                errors.append(f"invalid upstream claims: {value}")
                parsed_upstream.append([])
                continue
            refs = value.split(" + ")
            if len(refs) != len(set(refs)):
                errors.append(f"duplicate upstream claim within one support block: {value}")
            numbers = [int(ref[1:]) for ref in refs]
            if any(number >= index for number in numbers):
                errors.append(f"claim {index}: upstream claims must reference earlier claims only")
            parsed_upstream.append(numbers)

        for value in dependence:
            if value not in DEPENDENCE:
                errors.append(f"invalid evidence dependence: {value}")

        if len(dependence) == len(parsed_nodes) == len(claim_headers):
            for index, (dep, nodes) in enumerate(zip(dependence, parsed_nodes), start=1):
                if dep in {
                    "shared-source convergence",
                    "partially independent convergence",
                    "independent convergence",
                } and len(nodes) < 2:
                    errors.append(
                        f"claim {index}: convergence dependence requires at least two evidence nodes"
                    )

        if len(parsed_upstream) == len(parsed_nodes) == len(support_levels) == len(claim_headers):
            for index, (upstream, nodes, level) in enumerate(
                zip(parsed_upstream, parsed_nodes, support_levels), start=1
            ):
                if not upstream or level != "sufficient":
                    continue
                upstream_nodes = set()
                upstream_levels = []
                for ref in upstream:
                    upstream_nodes.update(parsed_nodes[ref - 1])
                    upstream_levels.append(support_levels[ref - 1])
                if set(nodes).issubset(upstream_nodes) and any(
                    upstream_level != "sufficient" for upstream_level in upstream_levels
                ):
                    errors.append(
                        f"claim {index}: downstream claim cannot be sufficient when it adds no new evidence and a required upstream claim is not sufficient"
                    )

        for value in support_levels:
            if value not in SUPPORT_LEVELS:
                errors.append(f"invalid support level: {value}")

        for value in locations:
            if not value.strip():
                errors.append("source location must not be empty")

        parsed_labels = []
        for value in evidence_values:
            labels = [part.strip() for part in value.split("+")]
            parsed_labels.append(labels)
            unknown = [label for label in labels if label not in allowed_evidence]
            if unknown:
                errors.append(f"unknown evidence label(s): {', '.join(unknown)}")

        if all(len(values) == len(claim_headers) for values in [provenances, dependencies, evidence_values]):
            for index, (provenance, dependency, labels) in enumerate(
                zip(provenances, dependencies, parsed_labels), start=1
            ):
                if provenance in {"external citation", "mixed"} and dependency == "none":
                    errors.append(
                        f"claim {index}: {provenance} provenance requires a named external dependency"
                    )
                if provenance == "paper-local" and "literature citation" in labels:
                    errors.append(
                        f"claim {index}: literature citation cannot be labeled paper-local"
                    )

    usable = sections[SECTION_HEADINGS[3]]
    for subheading in [
        "### usable results",
        "### usable methods or design",
        "### usable materials or documentation",
    ]:
        if usable.count(subheading) != 1:
            errors.append(f"section 4 must contain exactly one '{subheading}'")

    downweight = sections[SECTION_HEADINGS[4]]
    for subheading in [
        "### worth noticing but should be downweighted",
        "### should be treated cautiously or ignored",
    ]:
        if downweight.count(subheading) != 1:
            errors.append(f"section 5 must contain exactly one '{subheading}'")

    values = sections[SECTION_HEADINGS[5]]
    for field in VALUE_FIELDS:
        field_values = _field_values(values, field)
        if len(field_values) != 1:
            errors.append(f"section 6 must contain exactly one '{field}'")
        elif field_values[0] not in VALUE_LEVELS:
            errors.append(f"invalid {field}: {field_values[0]}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit", type=Path)
    parser.add_argument(
        "--evidence-types",
        type=Path,
        default=Path(__file__).parents[1] / "references" / "evidence-types.md",
    )
    args = parser.parse_args()
    allowed = evidence_labels(args.evidence_types.read_text(encoding="utf-8"))
    errors = validate(args.audit.read_text(encoding="utf-8"), allowed)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: audit satisfies the Evidence Paper Reader contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
