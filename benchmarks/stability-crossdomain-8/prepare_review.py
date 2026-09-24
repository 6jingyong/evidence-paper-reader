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
        "Use the installed Evidence Paper Reader skill. Do not use any private answer key, reference block, or scorer output.",
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
    neutral_contract = """# Output contract

Return JSON only.

case_id must match the packet.
evidence_viability is one of: auditable, partially auditable, non-auditable.
Select 3–5 candidate claim IDs when auditable, 1–5 when partially auditable, and none when non-auditable.
modules must contain only materially required module filenames from the installed skill.
use_evidence_inventory is boolean.
support must contain exactly one object for every selected claim, using one of: sufficient, partial, insufficient, unclear.
note is optional and concise.

Schema:
{
  "case_id": "<packet case id>",
  "evidence_viability": "<controlled value>",
  "selected_claim_ids": ["<candidate id>", "..."],
  "modules": ["<module filename>", "..."],
  "use_evidence_inventory": false,
  "support": [
    {"claim_id": "<selected candidate id>", "support_level": "<controlled value>"}
  ],
  "note": "<optional concise note>"
}"""
    sections.extend([
        "## Neutral output contract",
        "",
        neutral_contract,
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
