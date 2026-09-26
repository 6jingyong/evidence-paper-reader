#!/usr/bin/env python3
"""Build and fingerprint exact source bundles for source-to-audit runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
REPO_ROOT = ROOT.parents[1]
RUN_ROOT = REPO_ROOT / "validation-runs" / "real-papers"
CASE_INDEX = ROOT / "case_index.json"
PROFILES = ROOT / "acquisition-profiles.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def load_profile_contract(case_id: str) -> dict:
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
    cases = profiles.get("cases", {})
    if case_id not in cases:
        raise ValueError(f"missing acquisition profile for case_id: {case_id}")
    return {
        "schema_version": profiles["schema_version"],
        "bundle_format": profiles["bundle_format"],
        "bundle_rules": profiles["bundle_rules"],
        "case": cases[case_id],
    }


def profile_sha256(case_id: str) -> str:
    contract = load_profile_contract(case_id)
    canonical = json.dumps(
        contract,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256_bytes(canonical)


def normalize_component_text(path: Path) -> bytes:
    if not path.is_file():
        raise ValueError(f"component source not found: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"component must be UTF-8 text before bundling: {path}"
        ) from exc
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.rstrip("\n") + "\n"
    return text.encode("utf-8")


def build_bundle(case_id: str, component_paths: dict[str, Path]) -> tuple[bytes, list[dict]]:
    contract = load_profile_contract(case_id)
    profile = contract["case"]
    declared = profile["components"]
    declared_ids = [item["component_id"] for item in declared]
    required_ids = {
        item["component_id"]
        for item in declared
        if item.get("required") is True
    }

    unknown = sorted(set(component_paths) - set(declared_ids))
    if unknown:
        raise ValueError("unknown component id(s): " + ", ".join(unknown))
    missing = sorted(required_ids - set(component_paths))
    if missing:
        raise ValueError("missing required component(s): " + ", ".join(missing))

    chunks: list[bytes] = []
    records: list[dict] = []
    for item in declared:
        component_id = item["component_id"]
        if component_id not in component_paths:
            continue
        body = normalize_component_text(component_paths[component_id])
        header = (
            f"===== BEGIN SOURCE COMPONENT: {component_id} =====\n"
            f"role: {item['role']}\n"
            f"url: {item['url']}\n"
            "\n"
        ).encode("utf-8")
        footer = (
            f"===== END SOURCE COMPONENT: {component_id} =====\n"
        ).encode("utf-8")
        chunks.extend([header, body, footer])
        records.append({
            "component_id": component_id,
            "role": item["role"],
            "url": item["url"],
            "sha256": sha256_bytes(body),
            "bytes": len(body),
        })

    bundle = b"".join(chunks)
    if not bundle:
        raise ValueError("source bundle cannot be empty")
    return bundle, records


def validate_manifest_contract(case_id: str, manifest: dict) -> list[str]:
    errors: list[str] = []
    try:
        contract = load_profile_contract(case_id)
        expected_profile_sha = profile_sha256(case_id)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"profile load failed: {exc}"]

    profile_meta = manifest.get("acquisition_profile")
    if not isinstance(profile_meta, dict):
        errors.append("acquisition_profile must be an object")
    else:
        expected = {
            "schema_version": contract["schema_version"],
            "bundle_format": contract["bundle_format"],
            "profile_sha256": expected_profile_sha,
            "representation": contract["case"]["representation"],
            "required_preservation": contract["case"]["required_preservation"],
        }
        if profile_meta != expected:
            errors.append("acquisition_profile does not match the current case profile")

    if manifest.get("normalization_method") != contract["bundle_format"]:
        errors.append(
            "normalization_method must match the acquisition profile bundle_format"
        )

    components = manifest.get("components")
    if not isinstance(components, list):
        errors.append("components must be a list")
        components = []

    declared = contract["case"]["components"]
    declared_by_id = {item["component_id"]: item for item in declared}
    required_ids = [
        item["component_id"]
        for item in declared
        if item.get("required") is True
    ]
    actual_ids = [
        item.get("component_id")
        for item in components
        if isinstance(item, dict)
    ]

    if len(actual_ids) != len(set(actual_ids)):
        errors.append("components contain duplicate component_id values")
    unknown = sorted(set(actual_ids) - set(declared_by_id))
    if unknown:
        errors.append("components contain unknown id(s): " + ", ".join(unknown))
    missing = [component_id for component_id in required_ids if component_id not in actual_ids]
    if missing:
        errors.append("components missing required id(s): " + ", ".join(missing))

    expected_order = [
        item["component_id"]
        for item in declared
        if item["component_id"] in actual_ids
    ]
    if actual_ids != expected_order:
        errors.append("components must follow acquisition-profile order")

    for item in components:
        if not isinstance(item, dict):
            errors.append("each component manifest entry must be an object")
            continue
        component_id = item.get("component_id")
        declared_item = declared_by_id.get(component_id)
        if declared_item is None:
            continue
        if item.get("role") != declared_item["role"]:
            errors.append(f"{component_id}: component role does not match profile")
        if item.get("url") != declared_item["url"]:
            errors.append(f"{component_id}: component URL does not match profile")
        digest = item.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(
            ch not in "0123456789abcdef" for ch in digest
        ):
            errors.append(f"{component_id}: component sha256 must be lowercase SHA-256")
        if not isinstance(item.get("bytes"), int) or item["bytes"] <= 0:
            errors.append(f"{component_id}: component bytes must be a positive integer")

    return errors


def build_manifest(
    case_id: str,
    material: Path,
    *,
    acquisition_method: str,
    normalization_method: str,
    acquired_at: str,
    raw_source: Path | None = None,
    components: list[dict] | None = None,
) -> dict:
    """Build a durable source-input manifest.

    The public function remains usable by tests and callers that already have
    deterministic bundle bytes. New CLI runs populate components from the
    acquisition profile and use the fixed bundle format.
    """
    _, source = load_case(case_id)
    if not material.is_file():
        raise ValueError(f"review material not found: {material}")
    if not acquisition_method.strip():
        raise ValueError("acquisition_method must be non-empty")
    if not normalization_method.strip():
        raise ValueError("normalization_method must be non-empty")

    contract = load_profile_contract(case_id)
    manifest = {
        "case_id": case_id,
        "canonical_source_url": source["source_url"],
        "stable_id": source["stable_id"],
        "acquired_at": acquired_at,
        "acquisition_method": acquisition_method.strip(),
        "normalization_method": normalization_method.strip(),
        "acquisition_profile": {
            "schema_version": contract["schema_version"],
            "bundle_format": contract["bundle_format"],
            "profile_sha256": profile_sha256(case_id),
            "representation": contract["case"]["representation"],
            "required_preservation": contract["case"]["required_preservation"],
        },
        "components": components or [],
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


def parse_component_args(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(
                f"component must use <component_id>=<path>: {value!r}"
            )
        component_id, path_text = value.split("=", 1)
        component_id = component_id.strip()
        path_text = path_text.strip()
        if not component_id or not path_text:
            raise ValueError(
                f"component must use <component_id>=<path>: {value!r}"
            )
        if component_id in result:
            raise ValueError(f"duplicate component id: {component_id}")
        result[component_id] = Path(path_text)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument(
        "material",
        nargs="?",
        type=Path,
        help="single primary text file; only valid when the profile requires one component",
    )
    parser.add_argument(
        "--component",
        action="append",
        default=[],
        metavar="ID=PATH",
        help="repeat for each source component required by the acquisition profile",
    )
    parser.add_argument("--raw-source", type=Path)
    parser.add_argument("--acquisition-method", required=True)
    parser.add_argument(
        "--acquired-at",
        default=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        components = parse_component_args(args.component)
        if args.material is not None:
            if components:
                raise ValueError(
                    "use either positional material or --component, not both"
                )
            components = {"primary": args.material}

        bundle, component_records = build_bundle(args.case_id, components)
        args.output.mkdir(parents=True, exist_ok=True)
        target = args.output / "source-material.txt"
        target.write_bytes(bundle)
        manifest = build_manifest(
            args.case_id,
            target,
            acquisition_method=args.acquisition_method,
            normalization_method="utf8-source-bundle-v1",
            acquired_at=args.acquired_at,
            raw_source=args.raw_source,
            components=component_records,
        )
        (args.output / "source-input.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    print(
        f"PASS: {args.case_id} source bundle fingerprinted "
        f"({manifest['review_material']['bytes']} bytes, "
        f"sha256={manifest['review_material']['sha256']}, "
        f"components={len(manifest['components'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
