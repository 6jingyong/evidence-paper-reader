#!/usr/bin/env python3
"""Generate adversarial semantic-router packets."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent


def render(case: dict) -> str:
    return "\n".join([
        f"# Router packet {case['case_id']}",
        "",
        f"- domain: {case['domain']}",
        "",
        "## Core claim",
        f"C1: {case['claim']}",
        "",
        "## Evidence/context",
        case["text"],
        "",
        "## Task",
        "Use semantic-router-card.md and return response-format.md JSON.",
        "Decide whether each module is materially required for C1; do not route from words alone.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("specs", nargs="?", type=Path, default=ROOT / "case_specs.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "packets")
    args = parser.parse_args()

    data = json.loads(args.specs.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    queue = []
    for case in data["cases"]:
        (args.output_dir / f"{case['case_id']}.md").write_text(render(case), encoding="utf-8")
        queue.append(case["case_id"])
    random.Random(20260924).shuffle(queue)
    (args.output_dir / "review_queue.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")
    print(f"PASS: generated {len(queue)} router packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
