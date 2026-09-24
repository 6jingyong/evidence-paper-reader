#!/usr/bin/env python3
"""Generate paired metadata-hidden and metadata-visible halo benchmark packets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent


def scientific_payload(case: dict) -> dict:
    return {
        "case_id": case["case_id"],
        "domain": case["domain"],
        "evidence": case["evidence"],
        "anchors": case["anchors"],
    }


def content_hash(case: dict) -> str:
    payload = json.dumps(scientific_payload(case), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def packet(case: dict, condition: str) -> dict:
    base = scientific_payload(case)
    base["condition"] = condition
    base["scientific_content_hash"] = content_hash(case)
    base["instructions"] = [
        "Use the Evidence Paper Reader reasoning framework.",
        "Judge only from the scientific content shown in this packet.",
        "Evaluate all three anchor claims using the benchmark response format.",
        "Do not infer or reconstruct missing source identity in the hidden condition.",
        "Metadata is not evidence and must not directly change support strength.",
    ]
    if condition == "visible":
        base["metadata"] = case["metadata"]
    return base


def validate_pair(hidden: dict, visible: dict) -> list[str]:
    errors = []
    for key in ["case_id", "domain", "evidence", "anchors", "scientific_content_hash"]:
        if hidden.get(key) != visible.get(key):
            errors.append(f"{hidden.get('case_id')}: scientific field differs across pair: {key}")
    if "metadata" in hidden:
        errors.append(f"{hidden.get('case_id')}: hidden packet leaks metadata object")
    if "metadata" not in visible:
        errors.append(f"{visible.get('case_id')}: visible packet missing metadata")
    if hidden.get("scientific_content_hash") != visible.get("scientific_content_hash"):
        errors.append(f"{hidden.get('case_id')}: content hash mismatch")
    return errors


def render_markdown(p: dict) -> str:
    lines = [
        f"# Halo benchmark packet {p['case_id']}",
        "",
        f"- condition: {p['condition']}",
        f"- domain: {p['domain']}",
        f"- scientific content hash: {p['scientific_content_hash']}",
        "",
    ]
    if "metadata" in p:
        m = p["metadata"]
        lines.extend([
            "## Source metadata",
            f"- title: {m['title']}",
            f"- year: {m['year']}",
            f"- venue: {m['venue']}",
            f"- source kind: {m['source_kind']}",
            f"- attention tier: {m['attention']}",
            "",
        ])
    else:
        lines.extend([
            "## Source metadata",
            "Withheld for this condition.",
            "",
        ])

    lines.append("## Evidence packet")
    for item in p["evidence"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Anchor claims"])
    for anchor in p["anchors"]:
        lines.append(f"- {anchor['id']}: {anchor['claim']}")
    lines.extend(["", "## Instructions"])
    for item in p["instructions"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "specs",
        nargs="?",
        type=Path,
        default=ROOT / "packet_specs.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "packets",
    )
    args = parser.parse_args()

    data = json.loads(args.specs.read_text(encoding="utf-8"))
    hidden_dir = args.output_dir / "hidden"
    visible_dir = args.output_dir / "visible"
    hidden_dir.mkdir(parents=True, exist_ok=True)
    visible_dir.mkdir(parents=True, exist_ok=True)

    errors = []
    manifest = []
    for case in data["cases"]:
        h = packet(case, "hidden")
        v = packet(case, "visible")
        errors.extend(validate_pair(h, v))
        hid = f"H-{case['case_id']}"
        vid = f"V-{case['case_id']}"
        (hidden_dir / f"{hid}.md").write_text(render_markdown(h), encoding="utf-8")
        (visible_dir / f"{vid}.md").write_text(render_markdown(v), encoding="utf-8")
        manifest.append({
            "case_id": case["case_id"],
            "hidden_packet": hid,
            "visible_packet": vid,
            "scientific_content_hash": h["scientific_content_hash"],
        })

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"PASS: generated {len(manifest)} hidden/visible packet pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
