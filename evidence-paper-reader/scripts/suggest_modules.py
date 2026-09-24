#!/usr/bin/env python3
"""Suggest optional Evidence Paper Reader modules from plain paper text.

This is an advisory lexical router for weaker models. It does not decide that a
methodological flaw exists. Every suggestion must be verified semantically.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MODULES = {
    "figure-and-table-traps.md": [
        r"\bfigure\b", r"\btable\b", r"heat\s*map", r"error bars?",
        r"\bsem\b", r"standard deviation", r"confidence interval",
        r"log(?:arithmic)? scale", r"normaliz", r"z[- ]?score",
        r"representative (?:image|micrograph|field)",
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

    if suggestions:
        suggestions.append({
            "module": "false-positive-guards.md",
            "cues": ["mandatory after any trap/module cue"],
        })

    return {
        "always_load": [
            "core-contract.md",
            "output-contract.md",
            "evidence-types.md",
        ],
        "suggested": suggestions,
        "warning": (
            "Lexical cues are advisory only. A cue triggers inspection, not a flaw. "
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
