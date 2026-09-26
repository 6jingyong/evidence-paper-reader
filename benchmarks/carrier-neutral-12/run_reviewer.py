#!/usr/bin/env python3
"""Run Carrier-Neutral 12 through one fresh external reviewer process per case."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).parent
SPECS = ROOT / "case_specs.json"
FORMAT = ROOT / "response-format.md"

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
RELATIONS = {"supports", "undermines", "mixed", "contextual"}
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


def load_cases() -> list[dict]:
    data = json.loads(SPECS.read_text(encoding="utf-8"))
    return data["cases"]


def validate_response_data(data: dict, case_id: str) -> None:
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
    if viability == "non-auditable":
        if claims:
            raise ValueError("non-auditable response must contain zero claims")
    elif not (1 <= len(claims) <= 5):
        raise ValueError("auditable response must contain 1 to 5 claims")

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

        relations = claim.get("evidence_relations")
        if not isinstance(relations, list):
            raise ValueError(f"claim {index}: evidence_relations must be a list")
        relation_nodes = []
        for item in relations:
            if not isinstance(item, dict):
                raise ValueError(f"claim {index}: evidence relation must be an object")
            node = item.get("evidence_node")
            relation_nodes.append(node)
            if item.get("relation") not in RELATIONS:
                raise ValueError(f"claim {index}: invalid evidence relation")
            reason = item.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(f"claim {index}: evidence relation reason required")
        if len(relation_nodes) != len(set(relation_nodes)):
            raise ValueError(f"claim {index}: duplicate evidence relation nodes")
        if set(relation_nodes) != set(nodes):
            raise ValueError(
                f"claim {index}: evidence_relations must exactly cover evidence_nodes"
            )

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

    edges = data.get("reasoning_edges")
    if not isinstance(edges, list):
        raise ValueError("reasoning_edges must be a list")
    if viability == "non-auditable":
        if edges:
            raise ValueError("non-auditable response must contain zero reasoning_edges")
    elif not edges:
        raise ValueError("auditable response requires reasoning_edges")

    by_claim: dict[int, list[dict]] = {}
    for position, edge in enumerate(edges, start=1):
        if not isinstance(edge, dict):
            raise ValueError(f"reasoning edge {position} must be an object")
        edge_id = f"R{position}"
        if edge.get("edge_id") != edge_id:
            raise ValueError(f"reasoning edge {position}: edge_id must be {edge_id}")
        target = edge.get("target_claim")
        if not isinstance(target, int) or target < 1 or target > len(claims):
            raise ValueError(f"{edge_id}: invalid target_claim")
        nodes = edge.get("evidence_nodes")
        if not isinstance(nodes, list) or not all(isinstance(x, str) for x in nodes):
            raise ValueError(f"{edge_id}: evidence_nodes must be a string list")
        upstream = edge.get("upstream_claims")
        if not isinstance(upstream, list) or not all(isinstance(x, int) for x in upstream):
            raise ValueError(f"{edge_id}: upstream_claims must be an integer list")
        if any(x < 1 or x >= target for x in upstream):
            raise ValueError(f"{edge_id}: upstream_claims must reference earlier claims")
        if not nodes and not upstream:
            raise ValueError(f"{edge_id}: reasoning edge must have at least one input")
        if edge.get("inference_type") not in INFERENCE_TYPES:
            raise ValueError(f"{edge_id}: invalid inference_type")
        status = edge.get("reasoning_status")
        if status not in REASONING_STATUS:
            raise ValueError(f"{edge_id}: invalid reasoning_status")
        reach = edge.get("added_reach")
        if not isinstance(reach, str) or not reach.strip():
            raise ValueError(f"{edge_id}: added_reach must be non-empty")
        if status == "direct" and reach.strip() != "none":
            raise ValueError(f"{edge_id}: direct edge must use added_reach 'none'")
        assumptions = edge.get("assumptions")
        if not isinstance(assumptions, list) or not all(
            isinstance(x, str) and x.strip() for x in assumptions
        ):
            raise ValueError(f"{edge_id}: assumptions must be a string list")
        by_claim.setdefault(target, []).append(edge)

    if viability != "non-auditable":
        for claim_index, claim in enumerate(claims, start=1):
            claim_edges = by_claim.get(claim_index, [])
            if not claim_edges:
                raise ValueError(f"claim {claim_index}: no reasoning edge")
            graph_nodes = set().union(*(set(edge["evidence_nodes"]) for edge in claim_edges))
            graph_upstream = set().union(*(set(edge["upstream_claims"]) for edge in claim_edges))
            if graph_nodes != set(claim["evidence_nodes"]):
                raise ValueError(
                    f"claim {claim_index}: reasoning evidence inputs must exactly match evidence_nodes"
                )
            if graph_upstream != set(claim["upstream_claims"]):
                raise ValueError(
                    f"claim {claim_index}: reasoning upstream inputs must exactly match upstream_claims"
                )

            statuses = {edge["reasoning_status"] for edge in claim_edges}
            level = claim["support_level"]
            if level == "sufficient" and not statuses.issubset({"direct", "supported"}):
                raise ValueError(
                    f"claim {claim_index}: sufficient support conflicts with reasoning status"
                )
            if level == "partial" and statuses.issubset({"direct", "supported"}):
                raise ValueError(
                    f"claim {claim_index}: partial support requires a non-fully-supporting edge"
                )
            if level == "insufficient" and "unsupported" not in statuses:
                raise ValueError(
                    f"claim {claim_index}: insufficient support requires an unsupported edge"
                )
            if level == "unclear" and "unclear" not in statuses:
                raise ValueError(
                    f"claim {claim_index}: unclear support requires an unclear edge"
                )

    conclusion = data.get("reader_conclusion")
    if not isinstance(conclusion, str) or not conclusion.strip():
        raise ValueError("reader_conclusion must be non-empty")


def validate_response(path: Path, case_id: str) -> None:
    validate_response_data(json.loads(path.read_text(encoding="utf-8")), case_id)


def prompt_text(packet_text: str) -> str:
    return "\n".join([
        "# Carrier-neutral fresh audit",
        "",
        "Audit exactly this one synthetic source in a fresh context.",
        "Use only the supplied packet and carrier-neutral response schema.",
        "Do not inspect hidden expectations, scorer output, or previous responses.",
        "Return JSON only.",
        "",
        "## Response schema",
        "",
        FORMAT.read_text(encoding="utf-8").rstrip(),
        "",
        "## Source packet",
        "",
        packet_text.rstrip(),
        "",
    ])


def command_for(template: str, prompt: Path, output: Path, case_id: str) -> list[str]:
    values = {
        "{prompt}": str(prompt.resolve()),
        "{output}": str(output.resolve()),
        "{case_id}": case_id,
    }
    return [values.get(token, token) for token in shlex.split(template)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-dir", type=Path, default=ROOT / "runs" / "packets")
    parser.add_argument("--response-dir", type=Path, default=ROOT / "runs" / "responses")
    parser.add_argument("--workspace-dir", type=Path, default=ROOT / "runs" / "workspaces")
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
        packet = args.packet_dir / f"{case_id}.md"
        output = args.response_dir / f"{case_id}.json"
        workspace = args.workspace_dir / case_id
        workspace.mkdir(parents=True, exist_ok=True)

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

        source_copy = workspace / "source-packet.md"
        shutil.copyfile(packet, source_copy)
        prompt = workspace / "prompt.md"
        prompt.write_text(
            prompt_text(source_copy.read_text(encoding="utf-8")),
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
            "CER_CASE_ID": case_id,
            "CER_PROMPT_PATH": str(prompt.resolve()),
            "CER_OUTPUT_PATH": str(output.resolve()),
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
    print(f"jobs: {len(statuses)}; accepted: {len(statuses)-len(failed)}; failed: {len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
