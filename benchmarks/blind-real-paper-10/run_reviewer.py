#!/usr/bin/env python3
"""Run blind real-paper packets through one fresh external reviewer process each."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
CASE_INDEX = ROOT / "case_index.json"
PROMPT_SCRIPT = ROOT / "prepare_review.py"

VIABILITY = {"auditable", "partially auditable", "non-auditable"}
SUPPORT = {"sufficient", "partial", "insufficient", "unclear"}
CLAIM_TYPES = {
    "observational",
    "methodological",
    "mechanistic",
    "performance",
    "generality",
    "intervention",
}
STRENGTH = {"weak", "medium", "strong"}
INFERENCE_TYPES = {
    "direct-result",
    "comparison",
    "statistical-inference",
    "causal",
    "mechanistic",
    "generalization",
    "proxy-to-construct",
    "aggregation",
    "external-import",
}
REASONING_STATUS = {"direct", "supported", "qualified", "unsupported", "unclear"}
MODULES = {
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


def load_prepare_module():
    spec = importlib.util.spec_from_file_location("blind_prepare_review", PROMPT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_cases() -> list[dict]:
    data = json.loads(CASE_INDEX.read_text(encoding="utf-8"))
    return data["cases"]


def validate_response(path: Path, case_id: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("response must be a JSON object")
    if data.get("case_id") != case_id:
        raise ValueError("response case_id mismatch")
    viability = data.get("evidence_viability")
    if viability not in VIABILITY:
        raise ValueError("invalid evidence_viability")

    flags = data.get("viability_flags")
    if not isinstance(flags, list) or not all(isinstance(x, str) for x in flags):
        raise ValueError("viability_flags must be a string list")
    if len(flags) != len(set(flags)):
        raise ValueError("viability_flags contain duplicates")

    claims = data.get("claims")
    if not isinstance(claims, list):
        raise ValueError("claims must be a list")
    if viability == "auditable" and not (3 <= len(claims) <= 5):
        raise ValueError("auditable response must contain 3 to 5 claims")
    if viability == "partially auditable" and not (1 <= len(claims) <= 5):
        raise ValueError("partially auditable response must contain 1 to 5 claims")
    if viability == "non-auditable" and claims:
        raise ValueError("non-auditable response must contain zero claims")

    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            raise ValueError(f"claim {index} must be an object")
        if not isinstance(claim.get("content"), str) or not claim["content"].strip():
            raise ValueError(f"claim {index}: content must be non-empty")
        if claim.get("claim_type") not in CLAIM_TYPES:
            raise ValueError(f"claim {index}: invalid claim_type")
        if claim.get("conclusion_strength") not in STRENGTH:
            raise ValueError(f"claim {index}: invalid conclusion_strength")
        nodes = claim.get("evidence_nodes")
        if (
            not isinstance(nodes, list)
            or not nodes
            or not all(
                isinstance(node, str)
                and node.startswith("E")
                and node[1:].isdigit()
                and int(node[1:]) >= 1
                for node in nodes
            )
        ):
            raise ValueError(f"claim {index}: evidence_nodes must be a non-empty E-node list")
        if len(nodes) != len(set(nodes)):
            raise ValueError(f"claim {index}: duplicate evidence_nodes")

        upstream = claim.get("upstream_claims")
        if not isinstance(upstream, list) or not all(isinstance(x, int) for x in upstream):
            raise ValueError(f"claim {index}: upstream_claims must be an integer list")
        if len(upstream) != len(set(upstream)):
            raise ValueError(f"claim {index}: duplicate upstream_claims")
        if any(x < 1 or x >= index for x in upstream):
            raise ValueError(f"claim {index}: upstream_claims must reference earlier claims")

        if claim.get("support_level") not in SUPPORT:
            raise ValueError(f"claim {index}: invalid support_level")
        for key in ["source_location", "reason"]:
            if not isinstance(claim.get(key), str) or not claim[key].strip():
                raise ValueError(f"claim {index}: {key} must be non-empty")

    reasoning_edges = data.get("reasoning_edges")
    if not isinstance(reasoning_edges, list):
        raise ValueError("reasoning_edges must be a list")
    if viability == "non-auditable":
        if reasoning_edges:
            raise ValueError("non-auditable response must contain zero reasoning_edges")
    elif not reasoning_edges:
        raise ValueError("auditable/partially auditable response requires reasoning_edges")

    by_claim = {}
    for position, edge in enumerate(reasoning_edges, start=1):
        if not isinstance(edge, dict):
            raise ValueError(f"reasoning edge {position} must be an object")
        expected_id = f"R{position}"
        if edge.get("edge_id") != expected_id:
            raise ValueError(f"reasoning edge {position}: edge_id must be {expected_id}")
        target = edge.get("target_claim")
        if not isinstance(target, int) or target < 1 or target > len(claims):
            raise ValueError(f"{expected_id}: invalid target_claim")

        nodes = edge.get("evidence_nodes")
        if not isinstance(nodes, list) or not all(isinstance(x, str) for x in nodes):
            raise ValueError(f"{expected_id}: evidence_nodes must be a string list")
        if len(nodes) != len(set(nodes)):
            raise ValueError(f"{expected_id}: duplicate evidence_nodes")

        upstream = edge.get("upstream_claims")
        if not isinstance(upstream, list) or not all(isinstance(x, int) for x in upstream):
            raise ValueError(f"{expected_id}: upstream_claims must be an integer list")
        if len(upstream) != len(set(upstream)):
            raise ValueError(f"{expected_id}: duplicate upstream_claims")
        if any(x < 1 or x >= target for x in upstream):
            raise ValueError(f"{expected_id}: upstream_claims must reference earlier claims")
        if not nodes and not upstream:
            raise ValueError(f"{expected_id}: reasoning edge must have at least one input")

        if edge.get("inference_type") not in INFERENCE_TYPES:
            raise ValueError(f"{expected_id}: invalid inference_type")
        status = edge.get("reasoning_status")
        if status not in REASONING_STATUS:
            raise ValueError(f"{expected_id}: invalid reasoning_status")
        reach = edge.get("added_reach")
        if not isinstance(reach, str) or not reach.strip():
            raise ValueError(f"{expected_id}: added_reach must be non-empty")
        if status == "direct" and reach.strip() != "none":
            raise ValueError(f"{expected_id}: direct edge must use added_reach 'none'")
        assumptions = edge.get("assumptions")
        if not isinstance(assumptions, list) or not all(
            isinstance(x, str) and x.strip() for x in assumptions
        ):
            raise ValueError(f"{expected_id}: assumptions must be a string list")
        if len(assumptions) != len(set(assumptions)):
            raise ValueError(f"{expected_id}: duplicate assumptions")
        by_claim.setdefault(target, []).append(edge)

    if viability != "non-auditable":
        for claim_index, claim in enumerate(claims, start=1):
            edges = by_claim.get(claim_index, [])
            if not edges:
                raise ValueError(f"claim {claim_index}: no reasoning edge")
            graph_nodes = set().union(*(set(edge["evidence_nodes"]) for edge in edges))
            graph_upstream = set().union(*(set(edge["upstream_claims"]) for edge in edges))
            if graph_nodes != set(claim["evidence_nodes"]):
                raise ValueError(
                    f"claim {claim_index}: reasoning evidence inputs must exactly match evidence_nodes"
                )
            if graph_upstream != set(claim["upstream_claims"]):
                raise ValueError(
                    f"claim {claim_index}: reasoning upstream inputs must exactly match upstream_claims"
                )

            statuses = {edge["reasoning_status"] for edge in edges}
            level = claim["support_level"]
            if level == "sufficient" and not statuses.issubset({"direct", "supported"}):
                raise ValueError(
                    f"claim {claim_index}: sufficient support conflicts with reasoning status"
                )
            if level == "partial" and statuses.issubset({"direct", "supported"}):
                raise ValueError(
                    f"claim {claim_index}: partial support requires a non-fully-supporting reasoning edge"
                )
            if level == "insufficient" and "unsupported" not in statuses:
                raise ValueError(
                    f"claim {claim_index}: insufficient support requires an unsupported edge"
                )
            if level == "unclear" and "unclear" not in statuses:
                raise ValueError(
                    f"claim {claim_index}: unclear support requires an unclear edge"
                )

    modules = data.get("modules")
    if not isinstance(modules, list) or not all(isinstance(x, str) for x in modules):
        raise ValueError("modules must be a string list")
    if len(modules) != len(set(modules)):
        raise ValueError("modules contain duplicates")
    unknown = set(modules) - MODULES
    if unknown:
        raise ValueError(f"unknown module(s): {sorted(unknown)}")

    if not isinstance(data.get("use_evidence_inventory"), bool):
        raise ValueError("use_evidence_inventory must be boolean")
    if not isinstance(data.get("reader_conclusion"), str) or not data["reader_conclusion"].strip():
        raise ValueError("reader_conclusion must be non-empty")


def command_for(template: str, prompt: Path, output: Path, case_id: str) -> list[str]:
    values = {
        "{prompt}": str(prompt.resolve()),
        "{output}": str(output.resolve()),
        "{case_id}": case_id,
    }
    return [values.get(token, token) for token in shlex.split(template)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--packet-dir",
        type=Path,
        default=ROOT / "runs" / "packets",
    )
    parser.add_argument(
        "--response-dir",
        type=Path,
        default=ROOT / "runs" / "responses",
    )
    parser.add_argument(
        "--workspace-dir",
        type=Path,
        default=ROOT / "runs" / "workspaces",
    )
    parser.add_argument(
        "--command",
        required=True,
        help="fresh reviewer command using {prompt}, {output}, and optional {case_id}",
    )
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--include-skill", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status-file", type=Path)
    args = parser.parse_args()

    prepare = load_prepare_module()
    cases = load_cases()
    if args.limit is not None:
        cases = cases[: args.limit]

    args.response_dir.mkdir(parents=True, exist_ok=True)
    args.workspace_dir.mkdir(parents=True, exist_ok=True)
    statuses = []

    for case in cases:
        case_id = case["case_id"]
        packet = args.packet_dir / f"{case_id}.md"
        output = args.response_dir / f"{case_id}.json"
        workspace = args.workspace_dir / case_id
        workspace.mkdir(parents=True, exist_ok=True)
        prompt = workspace / "prompt.md"
        source_copy = workspace / "source-packet.md"

        if not packet.is_file():
            statuses.append({"case_id": case_id, "status": "failed", "error": "missing packet"})
            continue

        if args.resume and output.is_file():
            try:
                validate_response(output, case_id)
                statuses.append({"case_id": case_id, "status": "skipped_existing"})
                continue
            except (OSError, ValueError, json.JSONDecodeError):
                output.unlink(missing_ok=True)

        packet_text = packet.read_text(encoding="utf-8")
        source_copy.write_text(packet_text, encoding="utf-8")
        prompt.write_text(
            prepare.render_prompt(
                packet_text,
                "source-packet.md",
                include_skill=args.include_skill,
            ),
            encoding="utf-8",
        )

        command = command_for(args.command, prompt, output, case_id)
        if args.dry_run:
            statuses.append({
                "case_id": case_id,
                "status": "dry_run",
                "command": command,
                "workspace": str(workspace),
            })
            continue

        started = time.time()
        env = os.environ.copy()
        env.update({
            "EPR_CASE_ID": case_id,
            "EPR_PROMPT_PATH": str(prompt.resolve()),
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
            }
            if completed.returncode != 0:
                status.update({"status": "failed", "error": "reviewer returned non-zero"})
            else:
                validate_response(output, case_id)
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
    accepted = len(statuses) - len(failed)
    print(f"jobs: {len(statuses)}; accepted: {accepted}; failed: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
