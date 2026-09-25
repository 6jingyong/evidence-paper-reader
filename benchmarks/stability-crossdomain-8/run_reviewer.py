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

PROMPT_SCRIPT = Path(__file__).parent / "prepare_review.py"

SUPPORT = {"sufficient", "partial", "insufficient", "unclear"}
VIABILITY = {"auditable", "partially auditable", "non-auditable"}
ALLOWED_MODULES = {
    "figure-and-table-traps.md",
    "statistical-traps.md",
    "measurement-traps.md",
    "study-design-traps.md",
    "evidence-topology.md",
    "evidence-dependence.md",
    "claim-evidence-links.md",
    "claim-dependencies.md",
    "follow-up-boundaries.md",
}

PLACEHOLDERS = {
    "{packet}",
    "{prompt}",
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


def command_for(
    template: str,
    job: dict,
    packet: Path,
    prompt: Path,
    output: Path,
) -> list[str]:
    tokens = shlex.split(template)
    values = {
        "{packet}": str(packet),
        "{prompt}": str(prompt),
        "{output}": str(output),
        "{packet_id}": job["packet_id"],
        "{case_id}": job["case_id"],
        "{repeat}": str(job["repeat"]),
    }
    return [values.get(token, token) for token in tokens]


def validate_json_output(path: Path, job: dict) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("response must be a JSON object")
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

    viability = data.get("evidence_viability")
    if viability not in VIABILITY:
        raise ValueError("invalid evidence_viability")

    selected = data.get("selected_claim_ids")
    if not isinstance(selected, list) or not all(isinstance(x, str) for x in selected):
        raise ValueError("selected_claim_ids must be a string list")
    if len(selected) != len(set(selected)):
        raise ValueError("selected_claim_ids contain duplicates")
    candidate_ids = set(job.get("candidate_ids", []))
    if candidate_ids and not set(selected) <= candidate_ids:
        raise ValueError("selected_claim_ids contain unknown candidate IDs")
    if viability == "auditable" and not (3 <= len(selected) <= 5):
        raise ValueError("auditable response must select 3 to 5 claims")
    if viability == "partially auditable" and not (1 <= len(selected) <= 5):
        raise ValueError("partially auditable response must select 1 to 5 claims")
    if viability == "non-auditable" and selected:
        raise ValueError("non-auditable response must select zero claims")

    modules = data.get("modules")
    if not isinstance(modules, list) or not all(isinstance(x, str) for x in modules):
        raise ValueError("modules must be a string list")
    if len(modules) != len(set(modules)):
        raise ValueError("modules contain duplicates")
    unknown_modules = set(modules) - ALLOWED_MODULES
    if unknown_modules:
        raise ValueError(f"unknown module(s): {sorted(unknown_modules)}")

    if not isinstance(data.get("use_evidence_inventory"), bool):
        raise ValueError("use_evidence_inventory must be boolean")

    support = data.get("support")
    if not isinstance(support, list):
        raise ValueError("support must be a list")
    support_ids = []
    for item in support:
        if not isinstance(item, dict):
            raise ValueError("support entries must be objects")
        cid = item.get("claim_id")
        level = item.get("support_level")
        if not isinstance(cid, str):
            raise ValueError("support claim_id must be a string")
        if level not in SUPPORT:
            raise ValueError(f"invalid support level for {cid}")
        if candidate_ids and cid not in candidate_ids:
            raise ValueError(f"unknown support claim {cid}")
        support_ids.append(cid)
    if len(support_ids) != len(set(support_ids)):
        raise ValueError("duplicate support claim")
    if set(support_ids) != set(selected):
        raise ValueError("support claim IDs must exactly match selected_claim_ids")


def build_prompt(
    packet: Path,
    prompt: Path,
    *,
    include_skill: bool,
) -> None:
    try:
        spec = __import__(
            "importlib.util"
        ).util.spec_from_file_location("epr_prepare_prompt", PROMPT_SCRIPT)
        module = __import__("importlib.util").util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
    except (OSError, ImportError, AttributeError) as exc:
        raise RuntimeError(f"cannot load prompt builder: {exc}") from exc

    rendered = module.render_prompt(
        packet.read_text(encoding="utf-8"),
        str(packet),
        include_skill=include_skill,
    )
    prompt.parent.mkdir(parents=True, exist_ok=True)
    prompt.write_text(rendered, encoding="utf-8")


def run_job(
    job: dict,
    packet_dir: Path,
    response_dir: Path,
    command_template: str,
    timeout: int,
    env_extra: dict[str, str],
    dry_run: bool,
    *,
    prompt_dir: Path | None = None,
    include_skill: bool = False,
) -> dict:
    packet = packet_dir / f"{job['packet_id']}.md"
    output = response_dir / f"{job['packet_id']}.json"
    prompt_root = prompt_dir or response_dir.parent / "prompts"
    prompt = prompt_root / f"{job['packet_id']}.md"
    started = time.time()

    if not packet.exists():
        return {
            **job,
            "status": "failed",
            "error": f"missing packet: {packet}",
        }

    try:
        build_prompt(packet, prompt, include_skill=include_skill)
    except (OSError, RuntimeError, UnicodeError) as exc:
        return {
            **job,
            "status": "failed",
            "error": str(exc),
        }

    command = command_for(command_template, job, packet, prompt, output)
    result = {
        **job,
        "status": "dry_run" if dry_run else "running",
        "command": command,
        "packet": str(packet),
        "prompt": str(prompt),
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
        "EPR_PROMPT_PATH": str(prompt),
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
    parser.add_argument("--prompt-dir", type=Path, default=Path(__file__).parent / "runs" / "prompts")
    parser.add_argument(
        "--command",
        required=True,
        help=(
            "External isolated reviewer command. Supports {packet}, {prompt}, {output}, "
            "{packet_id}, {case_id}, {repeat} placeholders."
        ),
    )
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("--include-skill", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status-file", type=Path)
    args = parser.parse_args()

    jobs = load_matrix(args.matrix)
    if args.limit is not None:
        jobs = jobs[: args.limit]
    args.response_dir.mkdir(parents=True, exist_ok=True)
    args.prompt_dir.mkdir(parents=True, exist_ok=True)

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
            prompt_dir=args.prompt_dir,
            include_skill=args.include_skill,
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
