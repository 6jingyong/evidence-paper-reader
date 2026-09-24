#!/usr/bin/env python3
"""Run repeated stability packets through an external isolated reviewer command."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path


PLACEHOLDERS = {
    "{packet}",
    "{output}",
    "{packet_id}",
    "{case_id}",
    "{repeat}",
}


def load_matrix(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("run matrix must be a non-empty JSON list")
    required = {"packet_id", "case_id", "repeat", "domain"}
    for row in data:
        if not required.issubset(row):
            raise ValueError(f"matrix row missing fields: {required - set(row)}")
    return data


def command_for(template: str, job: dict, packet: Path, output: Path) -> list[str]:
    tokens = shlex.split(template)
    values = {
        "{packet}": str(packet),
        "{output}": str(output),
        "{packet_id}": job["packet_id"],
        "{case_id}": job["case_id"],
        "{repeat}": str(job["repeat"]),
    }
    return [values.get(token, token) for token in tokens]


def validate_json_output(path: Path, job: dict) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("case_id") != job["case_id"]:
        raise ValueError(
            f"response case_id {data.get('case_id')!r} does not match {job['case_id']!r}"
        )
    required = {
        "evidence_viability",
        "selected_claim_ids",
        "modules",
        "use_evidence_inventory",
        "support",
    }
    missing = required - set(data)
    if missing:
        raise ValueError(f"response missing fields: {sorted(missing)}")


def run_job(
    job: dict,
    packet_dir: Path,
    response_dir: Path,
    command_template: str,
    timeout: int,
    env_extra: dict[str, str],
    dry_run: bool,
) -> dict:
    packet = packet_dir / f"{job['packet_id']}.md"
    output = response_dir / f"{job['packet_id']}.json"
    started = time.time()

    if not packet.exists():
        return {
            **job,
            "status": "failed",
            "error": f"missing packet: {packet}",
        }

    command = command_for(command_template, job, packet, output)
    result = {
        **job,
        "status": "dry_run" if dry_run else "running",
        "command": command,
        "packet": str(packet),
        "output": str(output),
    }

    if dry_run:
        return result

    env = os.environ.copy()
    env.update(env_extra)
    env.update({
        "EPR_PACKET_ID": job["packet_id"],
        "EPR_CASE_ID": job["case_id"],
        "EPR_REPEAT": str(job["repeat"]),
        "EPR_PACKET_PATH": str(packet),
        "EPR_OUTPUT_PATH": str(output),
    })

    try:
        completed = subprocess.run(
            command,
            check=False,
            timeout=timeout,
            cwd=Path.cwd(),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        result["returncode"] = completed.returncode
        result["stdout"] = completed.stdout[-4000:]
        result["stderr"] = completed.stderr[-4000:]
        if completed.returncode != 0:
            result["status"] = "failed"
            result["error"] = f"runner exited with {completed.returncode}"
            return result
        validate_json_output(output, job)
        result["status"] = "completed"
        result["elapsed_seconds"] = round(time.time() - started, 3)
        return result
    except subprocess.TimeoutExpired:
        result["status"] = "failed"
        result["error"] = f"timeout after {timeout}s"
        result["elapsed_seconds"] = round(time.time() - started, 3)
        return result
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result["status"] = "failed"
        result["error"] = str(exc)
        result["elapsed_seconds"] = round(time.time() - started, 3)
        return result


def parse_env(values: list[str]) -> dict[str, str]:
    result = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"--env must use KEY=VALUE: {item!r}")
        key, value = item.split("=", 1)
        if not key or key.startswith("EPR_"):
            raise ValueError(f"invalid runner env key: {key!r}")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, default=Path(__file__).parent / "runs" / "run_matrix.json")
    parser.add_argument("--packet-dir", type=Path, default=Path(__file__).parent / "runs" / "packets")
    parser.add_argument("--response-dir", type=Path, default=Path(__file__).parent / "runs" / "responses")
    parser.add_argument(
        "--command",
        required=True,
        help=(
            "External isolated reviewer command. Supports {packet}, {output}, "
            "{packet_id}, {case_id}, {repeat} placeholders."
        ),
    )
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status-file", type=Path)
    args = parser.parse_args()

    jobs = load_matrix(args.matrix)
    if args.limit is not None:
        jobs = jobs[: args.limit]
    args.response_dir.mkdir(parents=True, exist_ok=True)

    env_extra = parse_env(args.env)
    selected = []
    for job in jobs:
        output = args.response_dir / f"{job['packet_id']}.json"
        if args.resume and output.exists():
            try:
                validate_json_output(output, job)
                selected.append({
                    **job,
                    "status": "skipped_existing",
                    "output": str(output),
                })
                continue
            except (ValueError, json.JSONDecodeError):
                output.unlink(missing_ok=True)

        row = run_job(
            job,
            args.packet_dir,
            args.response_dir,
            args.command,
            args.timeout,
            env_extra,
            args.dry_run,
        )
        selected.append(row)
        status = row["status"]
        print(f"{job['packet_id']}: {status}", file=sys.stderr)

    if args.status_file:
        args.status_file.parent.mkdir(parents=True, exist_ok=True)
        args.status_file.write_text(
            json.dumps(selected, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    failed = [x for x in selected if x["status"] == "failed"]
    completed = sum(x["status"] in {"completed", "skipped_existing", "dry_run"} for x in selected)

    print(f"jobs: {len(selected)}; accepted: {completed}; failed: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
