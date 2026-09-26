#!/usr/bin/env python3
"""Generate answer-key-free Carrier-Neutral 12 packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent
SPECS = ROOT / "case_specs.json"

FORBIDDEN = [
    "reference_expectations",
    "expected support",
    "expected inference",
    "answer key",
]


def load_cases() -> list[dict]:
    data = json.loads(SPECS.read_text(encoding="utf-8"))
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) != 12:
        raise ValueError("carrier-neutral-12 requires exactly 12 cases")
    ids = [case.get("case_id") for case in cases]
    if len(ids) != len(set(ids)) or any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("carrier-neutral case IDs must be unique non-empty strings")
    return cases


def render_packet(case: dict) -> str:
    packet = "\n".join([
        "# Carrier-neutral audit packet",
        "",
        f"- case_id: {case['case_id']}",
        f"- source_kind: {case['source_kind']}",
        f"- carrier: {case['carrier']}",
        "",
        "## Source text",
        "",
        case["source_text"].strip(),
        "",
        "## Task",
        "",
        "Audit this source using the carrier-neutral claim–evidence–reasoning core.",
        "Judge only what the supplied source exposes. Do not use paper-specific prestige or peer-review assumptions.",
        "Do not inspect hidden expectations or scorer output.",
        "",
    ])
    lower = packet.lower()
    leaked = [term for term in FORBIDDEN if term in lower]
    if leaked:
        raise ValueError("packet leaked hidden-evaluation term(s): " + ", ".join(leaked))
    return packet


def generate(output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    written = []
    for case in load_cases():
        target = output / f"{case['case_id']}.md"
        target.write_text(render_packet(case), encoding="utf-8")
        written.append(target)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "runs" / "packets",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        paths = generate(args.output)
        if args.check:
            for path in paths:
                text = path.read_text(encoding="utf-8").lower()
                if any(term in text for term in FORBIDDEN):
                    raise ValueError(f"{path.name}: hidden expectation leakage")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    print(f"PASS: generated {len(paths)} carrier-neutral packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
