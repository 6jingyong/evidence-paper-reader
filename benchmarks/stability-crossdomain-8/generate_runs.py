#!/usr/bin/env python3
"""Generate a randomized 8-paper x 5-repeat stability run matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent


def packet_id(case_id: str, repeat: int, seed: int) -> str:
    raw = f"{seed}:{case_id}:{repeat}".encode("utf-8")
    return "SR-" + hashlib.sha256(raw).hexdigest()[:10].upper()


def render_case(case: dict, pid: str) -> str:
    lines = [
        f"# Stability review packet {pid}",
        "",
        f"- case id: {case['case_id']}",
        f"- domain: {case['domain']}",
        f"- source: {case['source']}",
        "",
        "## Evidence packet",
    ]
    for item in case["packet"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Candidate claims"])
    for item in case["candidates"]:
        lines.append(f"- {item['id']}: {item['text']}")
    lines.extend([
        "",
        "## Task",
        "Use the installed Evidence Paper Reader skill.",
        "Return response-format.md JSON only.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("specs", nargs="?", type=Path, default=ROOT / "case_specs.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "runs")
    args = parser.parse_args()

    data = json.loads(args.specs.read_text(encoding="utf-8"))
    packet_dir = args.output_dir / "packets"
    packet_dir.mkdir(parents=True, exist_ok=True)

    matrix = []
    for case in data["cases"]:
        for repeat in range(1, data["repeats_per_case"] + 1):
            pid = packet_id(case["case_id"], repeat, data["seed"])
            (packet_dir / f"{pid}.md").write_text(render_case(case, pid), encoding="utf-8")
            matrix.append({
                "packet_id": pid,
                "case_id": case["case_id"],
                "repeat": repeat,
                "domain": case["domain"],
            })

    random.Random(data["seed"]).shuffle(matrix)
    (args.output_dir / "run_matrix.json").write_text(
        json.dumps(matrix, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(
        f"PASS: generated {len(matrix)} isolated jobs "
        f"({len(data['cases'])} cases x {data['repeats_per_case']} repeats)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
