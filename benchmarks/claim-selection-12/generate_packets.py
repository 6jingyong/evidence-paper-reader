#!/usr/bin/env python3
"""Generate claim-selection benchmark packets with deterministically shuffled candidates."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent


def shuffled_case(case: dict, seed: int) -> dict:
    rng = random.Random(f"{seed}:{case['case_id']}")
    candidates = list(case["candidates"])
    rng.shuffle(candidates)
    return {
        "case_id": case["case_id"],
        "domain": case["domain"],
        "source_packet": case["source_packet"],
        "candidate_claims": candidates,
    }


def render(packet: dict) -> str:
    lines = [
        f"# Claim-selection packet {packet['case_id']}",
        "",
        f"- domain: {packet['domain']}",
        "",
        "## Source packet",
    ]
    for item in packet["source_packet"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Candidate claims"])
    for item in packet["candidate_claims"]:
        lines.append(f"- {item['id']}: {item['text']}")
    lines.extend([
        "",
        "## Task",
        "- Decide evidence viability.",
        "- Select the claims that should enter a reader-side evidence audit.",
        "- Preserve author claim strength; support judgment happens later.",
        "- Use response-format.md.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("specs", nargs="?", type=Path, default=ROOT / "case_specs.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "packets")
    args = parser.parse_args()

    data = json.loads(args.specs.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    queue = []
    for case in data["cases"]:
        packet = shuffled_case(case, data["seed"])
        path = args.output_dir / f"{case['case_id']}.md"
        path.write_text(render(packet), encoding="utf-8")
        queue.append(case["case_id"])
    random.Random(data["seed"]).shuffle(queue)
    (args.output_dir / "review_queue.json").write_text(json.dumps(queue, indent=2), encoding="utf-8")
    print(f"PASS: generated {len(queue)} claim-selection packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
