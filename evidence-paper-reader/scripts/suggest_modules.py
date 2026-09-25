#!/usr/bin/env python3
"""Suggest optional Evidence Paper Reader modules from plain paper text.

This is an advisory lexical router for staged Flash-path execution. It does not
decide that a methodological flaw exists. Every suggestion must be verified
semantically, and complex routes escalate to Full path rather than skipping work.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PRIMARY_METHOD_MODULES = {
    "figure-and-table-traps.md",
    "statistical-traps.md",
    "measurement-traps.md",
    "study-design-traps.md",
    "evidence-topology.md",
}

MODULES = {
    "figure-and-table-traps.md": [
        r"\bfigure\b", r"\btable\b", r"heat\s*map", r"error bars?",
        r"\bsem\b", r"standard deviation", r"log(?:arithmic)? scale",
        r"normaliz", r"z[- ]?score", r"representative (?:image|micrograph|field)",
    ],
    "statistical-traps.md": [
        r"\bp\s*[=<>]", r"confidence interval", r"credible interval",
        r"regression", r"odds ratio", r"hazard ratio", r"subgroup",
        r"interaction", r"multiple compar", r"false discovery", r"\bfdr\b",
        r"bonferroni", r"imputation", r"bayes",
    ],
    "measurement-traps.md": [
        r"assay", r"sensor", r"calibrat", r"limit of detection", r"\blod\b",
        r"limit of quantification", r"\bloq\b", r"below (?:the )?detection",
        r"biomarker", r"surrogate", r"batch effect", r"segment",
        r"intensity", r"rating scale", r"composite score",
    ],
    "study-design-traps.md": [
        r"randomi[sz]", r"controlled trial", r"before[- ]after", r"pre[- ]post",
        r"difference[- ]in[- ]differences", r"matched (?:control|comparator)",
        r"cluster", r"attrition", r"crossover", r"instrumental variable",
        r"regression discontinuity", r"train(?:ing)? set", r"validation set",
        r"test set", r"data leakage", r"train[- ]test",
    ],
    "evidence-topology.md": [
        r"complete[- ]case", r"filtered", r"valid (?:case|data|observation)",
        r"best configuration", r"optimal setting", r"proxy", r"surrogate",
        r"generaliz", r"real[- ]world", r"calibration target",
    ],
    "evidence-dependence.md": [
        r"replicat", r"technical repeat", r"technical replicat",
        r"independent cohort", r"multiple outcomes?", r"multiple datasets?",
        r"multiple sites?", r"multiple laboratories?",
    ],
    "follow-up-boundaries.md": [
        r"according to .{0,40}\bcit", r"previous(?:ly)? reported",
        r"prior (?:study|work|literature)", r"supplement", r"appendix",
        r"code (?:is )?available", r"data (?:is |are )?available",
    ],
}


def suggest_modules(text: str) -> dict:
    lower = text.lower()

    inventory_reasons = []
    figure_table_refs = len(re.findall(r"\b(?:fig(?:ure)?|table)\s*[s]?\d+", lower))
    multi_unit_cues = len(re.findall(
        r"\b(?:independent cohort|replication cohort|multiple datasets?|multiple sites?|"
        r"multiple laboratories?|external validation|validation cohort|test cohort)\b",
        lower,
    ))
    supplement_cues = len(re.findall(r"\b(?:supplement|appendix|supporting information)\b", lower))
    if len(text) >= 30000:
        inventory_reasons.append("long extracted text")
    if figure_table_refs >= 10:
        inventory_reasons.append("many figure/table references")
    if multi_unit_cues >= 2:
        inventory_reasons.append("multiple evidence-generating units")
    if supplement_cues >= 2 and figure_table_refs >= 4:
        inventory_reasons.append("decision material likely split across main and supplementary content")

    use_evidence_inventory = bool(inventory_reasons)
    suggestions = []
    for module, patterns in MODULES.items():
        hits = []
        for pattern in patterns:
            match = re.search(pattern, lower, flags=re.IGNORECASE)
            if match:
                hits.append(match.group(0))
        if hits:
            suggestions.append({
                "module": module,
                "cues": sorted(set(hits))[:8],
            })

    primary_count = sum(
        1 for item in suggestions if item["module"] in PRIMARY_METHOD_MODULES
    )

    if suggestions:
        suggestions.append({
            "module": "false-positive-guards.md",
            "cues": ["mandatory after any trap/module cue"],
        })

    recommended_path = "full" if primary_count >= 3 else "flash"
    if recommended_path == "full":
        path_reason = (
            f"{primary_count} primary methodological modules triggered; "
            "Full path required by escalation rule."
        )
    else:
        path_reason = (
            f"{primary_count} primary methodological modules triggered; "
            "Flash path remains eligible, subject to semantic escalation checks."
        )

    return {
        "always_load": [
            "core-contract.md",
            "evidence-viability.md",
            "evidence-types.md",
            "audit-ledger-format.md",
        ],
        "use_evidence_inventory": use_evidence_inventory,
        "inventory_with": "evidence_inventory.py" if use_evidence_inventory else None,
        "inventory_reasons": inventory_reasons,
        "semantic_router_required": True,
        "semantic_router_card": "semantic-router-card.md",
        "merge_with": "merge_route.py",
        "render_with": "render_audit.py",
        "validate_with": "validate_audit.py",
        "complete_with": "audit_gate.py",
        "suggested": suggestions,
        "primary_module_count": primary_count,
        "recommended_path": recommended_path,
        "path_reason": path_reason,
        "warning": (
            "Lexical cues are candidate routes only. Confirm them claim-by-claim with semantic-router-card.md. "
            "Flash path changes context loading only; it never lowers the audit contract. "
            "Verify the inference and mitigation before downweighting."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paper_text", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = suggest_modules(args.paper_text.read_text(encoding="utf-8", errors="ignore"))
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Recommended path: {result['recommended_path'].upper()}")
        print(
            "Evidence inventory: "
            + ("recommended" if result["use_evidence_inventory"] else "not required by lexical complexity check")
        )
        if result["inventory_reasons"]:
            print("Inventory reasons: " + "; ".join(result["inventory_reasons"]))
        print(result["path_reason"])
        print("Semantic route confirmation: required via semantic-router-card.md + merge_route.py")
        print("Completion gate: audit_gate.py")
        print("Always load:")
        for module in result["always_load"]:
            print(f"- {module}")
        print("Suggested optional modules:")
        if not result["suggested"]:
            print("- none")
        for item in result["suggested"]:
            print(f"- {item['module']}: {', '.join(item['cues'])}")
        print(result["warning"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
