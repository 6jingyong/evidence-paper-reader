#!/usr/bin/env python3
"""Validate durable judgment contracts for recorded real-paper runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VIABILITY = {"auditable", "partially auditable", "non-auditable"}
SUPPORT_LEVELS = {"sufficient", "partial", "insufficient", "unclear"}
ONLY_TOLERATED_SUPPORT_PAIR = {"partial", "insufficient"}


def contract_errors(contract: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(contract, dict):
        return ["contract must be an object"]
    if set(contract) != {"must_hold", "allowed_range"}:
        return ["contract must contain exactly must_hold and allowed_range"]

    must = contract["must_hold"]
    allowed = contract["allowed_range"]
    if not isinstance(must, dict) or set(must) != {
        "viability",
        "required_viability_flags",
    }:
        errors.append("must_hold keys are not exact")
    if not isinstance(allowed, dict) or set(allowed) != {
        "viability_flags",
        "support_levels",
    }:
        errors.append("allowed_range keys are not exact")
    if errors:
        return errors

    if must["viability"] not in VIABILITY:
        errors.append("invalid hard viability")

    required_flags = must["required_viability_flags"]
    allowed_flags = allowed["viability_flags"]
    if not isinstance(required_flags, list) or len(required_flags) != len(set(required_flags)):
        errors.append("required viability flags must be a unique list")
    if not isinstance(allowed_flags, list) or len(allowed_flags) != len(set(allowed_flags)):
        errors.append("allowed viability flags must be a unique list")
    if isinstance(required_flags, list) and isinstance(allowed_flags, list):
        if not set(required_flags).issubset(set(allowed_flags)):
            errors.append("required viability flags must be inside the allowed flag set")

    support_ranges = allowed["support_levels"]
    if not isinstance(support_ranges, list):
        errors.append("support level ranges must be a list")
        return errors
    if must["viability"] == "non-auditable" and support_ranges:
        errors.append("non-auditable contracts cannot allow claim support levels")

    for index, choices in enumerate(support_ranges, start=1):
        if not isinstance(choices, list) or not choices:
            errors.append(f"claim {index}: support range must be a non-empty list")
            continue
        if len(choices) != len(set(choices)):
            errors.append(f"claim {index}: duplicate support level in range")
        if not set(choices).issubset(SUPPORT_LEVELS):
            errors.append(f"claim {index}: unknown support level")
        if len(choices) > 2:
            errors.append(f"claim {index}: support tolerance is too broad")
        if len(choices) == 2 and set(choices) != ONLY_TOLERATED_SUPPORT_PAIR:
            errors.append(
                f"claim {index}: the only permitted two-level tolerance is partial/insufficient"
            )
    return errors


def judgment_errors(contract: dict, ledger: dict) -> list[str]:
    errors = contract_errors(contract)
    if errors:
        return errors

    must = contract["must_hold"]
    allowed = contract["allowed_range"]

    viability = ledger.get("evidence_viability")
    if viability != must["viability"]:
        errors.append(
            f"viability drift: expected {must['viability']}, got {viability}"
        )

    actual_flags = ledger.get("viability_flags", [])
    if not isinstance(actual_flags, list):
        errors.append("ledger viability_flags must be a list")
        actual_flags = []
    required_flags = set(must["required_viability_flags"])
    allowed_flags = set(allowed["viability_flags"])
    actual_flag_set = set(actual_flags)
    missing = sorted(required_flags - actual_flag_set)
    extra = sorted(actual_flag_set - allowed_flags)
    if missing:
        errors.append("missing required viability flag(s): " + ", ".join(missing))
    if extra:
        errors.append("viability flag(s) outside allowed range: " + ", ".join(extra))

    claims = ledger.get("claims", [])
    if not isinstance(claims, list):
        errors.append("ledger claims must be a list")
        claims = []
    support_ranges = allowed["support_levels"]
    if len(claims) != len(support_ranges):
        errors.append(
            f"claim-count drift: contract has {len(support_ranges)}, ledger has {len(claims)}"
        )
        return errors

    for index, (claim, choices) in enumerate(zip(claims, support_ranges), start=1):
        try:
            actual = claim["support"]["support_level"]
        except (KeyError, TypeError):
            errors.append(f"claim {index}: missing support level")
            continue
        if actual not in choices:
            errors.append(
                f"claim {index}: support {actual!r} outside allowed range {choices!r}"
            )
    return errors


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    run_root = root / "validation-runs" / "real-papers"
    baseline_path = root / "tests" / "real-paper-judgment-baseline.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_rounds = baseline.get("rounds", {})

    round_dirs = sorted(path for path in run_root.glob("*-round-*") if path.is_dir())
    manifest_rounds = {}
    for round_root in round_dirs:
        manifest = json.loads((round_root / "manifest.json").read_text(encoding="utf-8"))
        round_id = manifest["round_id"]
        manifest_rounds[round_id] = manifest
        baseline_cases = baseline_rounds.get(round_id)
        if baseline_cases is None:
            errors.append(f"{round_id}: missing from judgment baseline")
            continue

        manifest_cases = {case["id"]: case for case in manifest["cases"]}
        if set(manifest_cases) != set(baseline_cases):
            errors.append(f"{round_id}: manifest/baseline case set mismatch")
            continue

        for case_id, case in manifest_cases.items():
            contract = case.get("regression_contract")
            pinned = baseline_cases[case_id]
            if contract != pinned:
                errors.append(f"{round_id}/{case_id}: manifest contract differs from pinned baseline")
                continue
            for error in contract_errors(contract):
                errors.append(f"{round_id}/{case_id}: {error}")

            ledger_path = round_root / case_id / "ledger.json"
            if not ledger_path.is_file():
                errors.append(f"{round_id}/{case_id}: missing ledger.json")
                continue
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            for error in judgment_errors(contract, ledger):
                errors.append(f"{round_id}/{case_id}: {error}")

    if set(manifest_rounds) != set(baseline_rounds):
        errors.append("recorded round set does not exactly match judgment baseline")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).parents[2],
        help="repository root",
    )
    args = parser.parse_args()

    errors = validate_repository(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: recorded real-paper judgments satisfy hard invariants and bounded tolerance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
