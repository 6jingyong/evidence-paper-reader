#!/usr/bin/env python3
"""Run fingerprinted source material through isolated fresh reviewers."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).parent
CASE_INDEX = ROOT / "case_index.json"
BLIND_RUNNER = ROOT.parent / "blind-real-paper-10" / "run_reviewer.py"
BLIND_FORMAT = ROOT.parent / "blind-real-paper-10" / "response-format.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


blind = load_module("source_to_audit_blind_validator", BLIND_RUNNER)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cases() -> list[dict]:
    return json.loads(CASE_INDEX.read_text(encoding="utf-8"))["cases"]


def verify_prepared(case_id: str, root: Path) -> tuple[Path, dict]:
    case_root = root / case_id
    material = case_root / "source-material.txt"
    manifest_path = case_root / "source-input.json"
    if not material.is_file() or not manifest_path.is_file():
        raise ValueError(f"{case_id}: missing source-material.txt or source-input.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("case_id") != case_id:
        raise ValueError(f"{case_id}: source-input case_id mismatch")
    expected = manifest.get("review_material", {})
    actual_hash = sha256(material)
    actual_bytes = material.stat().st_size
    if expected.get("sha256") != actual_hash:
        raise ValueError(f"{case_id}: source material SHA-256 mismatch")
    if expected.get("bytes") != actual_bytes:
        raise ValueError(f"{case_id}: source material byte count mismatch")
    return material, manifest


def prompt_text(case_id: str, manifest: dict) -> str:
    return "\n".join([
        "# Source-to-Audit fresh review",
        "",
        f"case_id: {case_id}",
        f"canonical source: {manifest.get('canonical_source_url', '')}",
        f"stable id: {manifest.get('stable_id', '')}",
        "",
        "Audit source-material.txt using the Evidence Paper Reader claim–evidence–reasoning framework.",
        "Use only the source material in this isolated workspace plus the response schema below.",
        "Do not inspect repository answer keys, stored ledgers, regression contracts, scorer output, or previous audit artifacts.",
        "Return JSON only.",
        "",
        "## Response schema",
        "",
        BLIND_FORMAT.read_text(encoding="utf-8").rstrip(),
        "",
    ])


def command_for(template: str, prompt: Path, source: Path, output: Path, case_id: str) -> list[str]:
    values = {
        "{prompt}": str(prompt.resolve()),
        "{source}": str(source.resolve()),
        "{output}": str(output.resolve()),
        "{case_id}": case_id,
    }
    return [values.get(token, token) for token in shlex.split(template)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepared-root", type=Path, required=True)
    parser.add_argument("--response-dir", type=Path, required=True)
    parser.add_argument("--workspace-dir", type=Path, required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status-file", type=Path)
    args = parser.parse_args()

    cases = load_cases()
    if args.limit is not None:
        cases = cases[: args.limit]

    args.response_dir.mkdir(parents=True, exist_ok=True)
    args.workspace_dir.mkdir(parents=True, exist_ok=True)
    statuses = []

    for case in cases:
        case_id = case["case_id"]
        output = args.response_dir / f"{case_id}.json"
        try:
            material, manifest = verify_prepared(case_id, args.prepared_root)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            statuses.append({"case_id": case_id, "status": "failed", "error": str(exc)})
            continue

        if args.resume and output.is_file():
            try:
                blind.validate_response(output, case_id)
                statuses.append({"case_id": case_id, "status": "skipped_existing"})
                continue
            except (OSError, ValueError, json.JSONDecodeError):
                output.unlink(missing_ok=True)

        workspace = args.workspace_dir / case_id
        workspace.mkdir(parents=True, exist_ok=True)
        workspace_source = workspace / "source-material.txt"
        shutil.copyfile(material, workspace_source)
        prompt = workspace / "prompt.md"
        prompt.write_text(prompt_text(case_id, manifest), encoding="utf-8")

        command = command_for(args.command, prompt, workspace_source, output, case_id)
        if args.dry_run:
            statuses.append({
                "case_id": case_id,
                "status": "dry_run",
                "command": command,
                "source_sha256": manifest["review_material"]["sha256"],
                "workspace": str(workspace),
            })
            continue

        started = time.time()
        env = os.environ.copy()
        env.update({
            "EPR_CASE_ID": case_id,
            "EPR_PROMPT_PATH": str(prompt.resolve()),
            "EPR_SOURCE_PATH": str(workspace_source.resolve()),
            "EPR_OUTPUT_PATH": str(output.resolve()),
        })
        try:
            completed = subprocess.run(
                command,
                cwd=workspace,
                env=env,
                timeout=args.timeout,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            status = {
                "case_id": case_id,
                "returncode": completed.returncode,
                "stdout": completed.stdout[-4000:],
                "stderr": completed.stderr[-4000:],
                "elapsed_seconds": round(time.time() - started, 3),
                "source_sha256": manifest["review_material"]["sha256"],
            }
            if completed.returncode != 0:
                status.update({"status": "failed", "error": "reviewer returned non-zero"})
            else:
                blind.validate_response(output, case_id)
                status["status"] = "completed"
            statuses.append(status)
        except (OSError, subprocess.TimeoutExpired, ValueError, json.JSONDecodeError) as exc:
            statuses.append({
                "case_id": case_id,
                "status": "failed",
                "error": str(exc),
                "elapsed_seconds": round(time.time() - started, 3),
            })

    if args.status_file:
        args.status_file.parent.mkdir(parents=True, exist_ok=True)
        args.status_file.write_text(
            json.dumps(statuses, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    failed = [row for row in statuses if row["status"] == "failed"]
    print(f"jobs: {len(statuses)}; accepted: {len(statuses)-len(failed)}; failed: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
