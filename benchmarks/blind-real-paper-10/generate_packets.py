#!/usr/bin/env python3
"""Generate answer-key-free packets for blind re-audit of recorded real papers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parent
REPO_ROOT = ROOT.parents[1]
RUN_ROOT = REPO_ROOT / "validation-runs" / "real-papers"
CASE_INDEX = ROOT / "case_index.json"

SOURCE_FIELDS = [
    "record_id",
    "title",
    "authors",
    "year",
    "stable_id",
    "doi",
    "source_url",
    "access_format",
    "retrieved_on",
]
PUBLIC_URL_FIELDS = ["integrity_context", "later_context"]
FORBIDDEN_PACKET_TERMS = [
    "regression_contract",
    "must_hold",
    "allowed_range",
    "expected_support",
    "expected_viability",
    "ledger.json",
    "result.json",
    "real-paper-judgment-baseline",
    "integrity_note",
    "later_context_note",
]


def load_index() -> dict:
    data = json.loads(CASE_INDEX.read_text(encoding="utf-8"))
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("case_index.json must contain a non-empty cases list")
    if len(cases) != 10:
        raise ValueError(f"blind-real-paper-10 requires exactly 10 cases, got {len(cases)}")
    ids = [case.get("case_id") for case in cases]
    if any(not isinstance(x, str) or not x for x in ids) or len(ids) != len(set(ids)):
        raise ValueError("case IDs must be unique non-empty strings")
    return data


def source_path(case: dict) -> Path:
    return RUN_ROOT / case["round_id"] / case["case_id"] / "source.json"


def neutral_source(source: dict) -> dict:
    result = {key: source[key] for key in SOURCE_FIELDS if key in source}
    urls = []
    for key in PUBLIC_URL_FIELDS:
        value = source.get(key, [])
        if isinstance(value, list):
            urls.extend(item for item in value if isinstance(item, str) and item.startswith("https://"))
    if urls:
        result["supplemental_public_urls"] = list(dict.fromkeys(urls))
    return result


def render_packet(case: dict, source: dict) -> str:
    neutral = neutral_source(source)
    lines = [
        "# Blind real-paper audit packet",
        "",
        f"- case_id: {case['case_id']}",
        f"- title: {neutral.get('title', '')}",
        f"- authors: {neutral.get('authors', '')}",
        f"- year: {neutral.get('year', '')}",
        f"- stable_id: {neutral.get('stable_id', '')}",
    ]
    if neutral.get("doi"):
        lines.append(f"- doi: {neutral['doi']}")
    lines.extend([
        f"- primary_source_url: {neutral.get('source_url', '')}",
        f"- access_format: {neutral.get('access_format', '')}",
        "",
    ])
    urls = neutral.get("supplemental_public_urls", [])
    if urls:
        lines.extend(["## Supplemental public provenance/context URLs", ""])
        lines.extend(f"- {url}" for url in urls)
        lines.append("")

    lines.extend([
        "## Task",
        "",
        "Open and audit the public source material using Evidence Paper Reader.",
        "The supplemental URLs, when present, are neutral provenance/context sources; they are not answer keys.",
        "Do not inspect any repository audit ledger, result record, semantic route, module checks, manifest regression contract, judgment baseline, or scorer output.",
        "Extract the important source-facing claims yourself and judge how far the disclosed evidence supports them.",
        "",
    ])
    packet = "\n".join(lines)
    lower = packet.lower()
    leaked = [term for term in FORBIDDEN_PACKET_TERMS if term.lower() in lower]
    if leaked:
        raise ValueError("packet contains forbidden answer-key term(s): " + ", ".join(leaked))
    return packet


def generate(output: Path) -> list[Path]:
    index = load_index()
    output.mkdir(parents=True, exist_ok=True)
    written = []
    for case in index["cases"]:
        path = source_path(case)
        source = json.loads(path.read_text(encoding="utf-8"))
        if source.get("record_id") != case["case_id"]:
            raise ValueError(f"{case['case_id']}: source record_id mismatch")
        packet = render_packet(case, source)
        target = output / f"{case['case_id']}.md"
        target.write_text(packet, encoding="utf-8")
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
        written = generate(args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    if args.check:
        for path in written:
            text = path.read_text(encoding="utf-8").lower()
            leaked = [term for term in FORBIDDEN_PACKET_TERMS if term.lower() in text]
            if leaked:
                print(f"FAIL: {path.name} leaked: {', '.join(leaked)}")
                return 1
    print(f"PASS: generated {len(written)} blind source packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
