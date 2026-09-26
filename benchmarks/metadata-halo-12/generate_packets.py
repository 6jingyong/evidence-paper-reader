#!/usr/bin/env python3
"""Generate paired metadata-hidden and metadata-visible halo benchmark packets."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).parent


def scientific_payload(case: dict) -> dict:
    return {
        "domain": case["domain"],
        "evidence": case["evidence"],
        "anchors": case["anchors"],
    }


def content_hash(case: dict) -> str:
    payload = json.dumps(scientific_payload(case), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def packet_alias(case_id: str, condition: str, seed: int) -> str:
    raw = f"{seed}:{case_id}:{condition}".encode("utf-8")
    return "P-" + hashlib.sha256(raw).hexdigest()[:10].upper()


def packet(case: dict, condition: str, seed: int) -> dict:
    base = scientific_payload(case)
    base["packet_id"] = packet_alias(case["case_id"], condition, seed)
    base["scientific_content_hash"] = content_hash(case)
    base["instructions"] = [
        "Use the Evidence Paper Reader reasoning framework.",
        "Judge only from the scientific content shown in this packet.",
        "Evaluate all three anchor claims using the benchmark response format.",
        "Do not infer or reconstruct source identity when source metadata is absent.",
        "Metadata is not evidence and must not directly change support strength.",
    ]
    if condition == "visible":
        base["metadata"] = case["metadata"]
    return base


def validate_pair(hidden: dict, visible: dict) -> list[str]:
    errors = []
    for key in ["domain", "evidence", "anchors", "scientific_content_hash"]:
        if hidden.get(key) != visible.get(key):
            errors.append(f"scientific field differs across pair: {key}")
    if hidden["packet_id"] == visible["packet_id"]:
        errors.append("paired packets must have different anonymous packet IDs")
    if "metadata" in hidden:
        errors.append("hidden packet leaks metadata object")
    if "metadata" not in visible:
        errors.append("visible packet missing metadata")
    if hidden.get("scientific_content_hash") != visible.get("scientific_content_hash"):
        errors.append("content hash mismatch")
    return errors


def render_markdown(p: dict) -> str:
    lines = [
        f"# Evidence review packet {p['packet_id']}",
        "",
        f"- domain: {p['domain']}",
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
            f"- attention: {m['attention']}",
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
    packet_dir = args.output_dir
    packet_dir.mkdir(parents=True, exist_ok=True)

    errors = []
    manifest = []
    for case in data["cases"]:
        h = packet(case, "hidden", data["seed"])
        v = packet(case, "visible", data["seed"])
        errors.extend(f"{case['case_id']}: {e}" for e in validate_pair(h, v))

        for condition, p in [("hidden", h), ("visible", v)]:
            (packet_dir / f"{p['packet_id']}.md").write_text(render_markdown(p), encoding="utf-8")
            manifest.append({
                "packet_id": p["packet_id"],
                "case_id": case["case_id"],
                "condition": condition,
                "attention": case["metadata"]["attention"],
                "source_kind": case["metadata"]["source_kind"],
                "scientific_content_hash": p["scientific_content_hash"],
            })

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    queue = [row["packet_id"] for row in manifest]
    random.Random(data["seed"]).shuffle(queue)
    (args.output_dir / "review_queue.json").write_text(
        json.dumps(queue, indent=2),
        encoding="utf-8",
    )

    print(
        f"PASS: generated {len(manifest)} anonymous packets "
        f"({len(data['cases'])} pairs) and a blinded review queue"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
