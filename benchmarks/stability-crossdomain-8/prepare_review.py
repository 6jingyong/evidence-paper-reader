#!/usr/bin/env python3
"""Build one self-contained reviewer prompt from a stability packet."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).parent
REPO_ROOT = ROOT.parents[1]
SKILL = REPO_ROOT / "evidence-paper-reader" / "SKILL.md"
RESPONSE_FORMAT = ROOT / "response-format.md"


def render_prompt(
    packet_text: str,
    packet_path: str,
    *,
    include_skill: bool = False,
) -> str:
    sections = [
        "# Evidence Paper Reader — isolated stability review",
        "",
        "Run exactly this one review in a fresh model context.",
        "",
        "Use the installed Evidence Paper Reader skill. Do not use, seek, or infer any private benchmark reference expectations.",
        "Judge the candidate claims as written. Do not silently narrow a strong source claim into a safer replacement.",
        "Return JSON only and match the supplied response format exactly.",
        "",
        f"Packet path: {packet_path}",
        "",
    ]
    if include_skill:
        sections.extend([
            "## Skill snapshot",
            "",
            SKILL.read_text(encoding="utf-8").rstrip(),
            "",
        ])
    sections.extend([
        "## Response format",
        "",
        RESPONSE_FORMAT.read_text(encoding="utf-8").rstrip(),
        "",
        "## Review packet",
        "",
        packet_text.rstrip(),
        "",
        "## Final instruction",
        "",
        "Return JSON only. Do not add Markdown fences or commentary.",
        "",
    ])
    return "\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--include-skill", action="store_true")
    args = parser.parse_args()

    if not args.packet.exists():
        raise SystemExit(f"missing packet: {args.packet}")

    if args.include_skill and not SKILL.exists():
        raise SystemExit(f"missing skill file: {SKILL}")
    if not RESPONSE_FORMAT.exists():
        raise SystemExit(f"missing response format: {RESPONSE_FORMAT}")

    prompt = render_prompt(
        args.packet.read_text(encoding="utf-8"),
        str(args.packet),
        include_skill=args.include_skill,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(prompt, encoding="utf-8")
    else:
        print(prompt, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
