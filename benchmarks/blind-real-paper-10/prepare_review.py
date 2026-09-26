#!/usr/bin/env python3
"""Build one isolated blind-review prompt from a source-only packet."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).parent
REPO_ROOT = ROOT.parents[1]
SKILL = REPO_ROOT / "evidence-paper-reader" / "SKILL.md"
RESPONSE_FORMAT = ROOT / "response-format.md"


def render_prompt(packet_text: str, packet_path: str, *, include_skill: bool = False) -> str:
    parts = [
        "# Evidence Paper Reader — blind real-paper re-audit",
        "",
        "Run exactly this one audit in a fresh context.",
        "Use only the public source material named in the packet plus the installed Evidence Paper Reader skill.",
        "Do not inspect repository answer keys, prior audit artifacts, regression expectations, or scorer output.",
        "Return JSON only.",
        "",
        f"Packet path: {packet_path}",
        "",
    ]
    if include_skill:
        parts.extend([
            "## Top-level skill snapshot",
            "",
            SKILL.read_text(encoding="utf-8").rstrip(),
            "",
        ])
    parts.extend([
        "## Response format",
        "",
        RESPONSE_FORMAT.read_text(encoding="utf-8").rstrip(),
        "",
        "## Source packet",
        "",
        packet_text.rstrip(),
        "",
        "## Final instruction",
        "",
        "Audit from source material, not memory or stored repository answers. Return JSON only.",
        "",
    ])
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--include-skill", action="store_true")
    args = parser.parse_args()
    rendered = render_prompt(
        args.packet.read_text(encoding="utf-8"),
        str(args.packet),
        include_skill=args.include_skill,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
