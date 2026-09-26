#!/usr/bin/env python3
"""Fingerprint exact source material used for a source-to-audit run."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
REPO_ROOT = ROOT.parents[1]
RUN_ROOT = REPO_ROOT / "validation-runs" / "real-papers"
CASE_INDEX = ROOT / "case_index.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_case(case_id: str) -> tuple[dict, dict]:
    index = json.loads(CASE_INDEX.read_text(encoding="utf-8"))
    case = next((item for item in index["cases"] if item["case_id"] == case_id), None)
    if case is None:
        raise ValueError(f"unknown case_id: {case_id}")
    source_path = RUN_ROOT / case["round_id"] / case_id / "source.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    return case, source


def build_manifest(
    case_id: str,
    material: Path,
    *,
    acquisition_method: str,
    normalization_method: str,
    acquired_at: str,
    raw_source: Path | None = None,
) -> dict:
    _, source = load_case(case_id)
    if not material.is_file():
        raise ValueError(f"review material not found: {material}")
    if not acquisition_method.strip():
        raise ValueError("acquisition_method must be non-empty")
    if not normalization_method.strip():
        raise ValueError("normalization_method must be non-empty")

    manifest = {
        "case_id": case_id,
        "canonical_source_url": source["source_url"],
        "stable_id": source["stable_id"],
        "acquired_at": acquired_at,
        "acquisition_method": acquisition_method.strip(),
        "normalization_method": normalization_method.strip(),
        "review_material": {
            "sha256": sha256(material),
            "bytes": material.stat().st_size,
        },
    }
    if raw_source is not None:
        if not raw_source.is_file():
            raise ValueError(f"raw source not found: {raw_source}")
        manifest["raw_source"] = {
            "sha256": sha256(raw_source),
            "bytes": raw_source.stat().st_size,
        }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("material", type=Path)
    parser.add_argument("--raw-source", type=Path)
    parser.add_argument("--acquisition-method", required=True)
    parser.add_argument("--normalization-method", required=True)
    parser.add_argument(
        "--acquired-at",
        default=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        manifest = build_manifest(
            args.case_id,
            args.material,
            acquisition_method=args.acquisition_method,
            normalization_method=args.normalization_method,
            acquired_at=args.acquired_at,
            raw_source=args.raw_source,
        )
        args.output.mkdir(parents=True, exist_ok=True)
        target = args.output / "source-material.txt"
        shutil.copyfile(args.material, target)
        (args.output / "source-input.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    print(
        f"PASS: {args.case_id} source material fingerprinted "
        f"({manifest['review_material']['bytes']} bytes, "
        f"sha256={manifest['review_material']['sha256']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
