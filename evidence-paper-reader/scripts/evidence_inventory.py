#!/usr/bin/env python3
"""Validate and compact Evidence Paper Reader evidence inventories."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

VIABILITY = {"auditable", "partially auditable", "non-auditable"}
MATERIAL_KINDS = {
    "main text", "figure", "table", "supplement", "appendix",
    "data or code", "external reference", "other",
}
MATERIAL_AVAILABILITY = {"available", "partial", "missing"}
RECORD_ROLES = {
    "direct result", "method detail", "derived result", "robustness result",
    "limitation", "author interpretation", "external evidence",
}
PROVENANCE = {"paper-local", "external citation"}
RECORD_AVAILABILITY = {"complete", "partial"}

ID_PATTERNS = {
    "claim": re.compile(r"^C[1-9]\d*$"),
    "material": re.compile(r"^M[1-9]\d*$"),
    "record": re.compile(r"^R[1-9]\d*$"),
    "result": re.compile(r"^G[1-9]\d*$"),
    "unit": re.compile(r"^U[1-9]\d*$"),
    "evidence": re.compile(r"^E[1-9]\d*$"),
}

TEMPLATE = {
    "evidence_viability": "auditable",
    "claims": [
        {"claim_id": "C1", "content": ""},
        {"claim_id": "C2", "content": ""},
        {"claim_id": "C3", "content": ""},
    ],
    "materials": [
        {
            "material_id": "M1",
            "kind": "main text",
            "availability": "available",
            "location": "",
            "notes": "",
        }
    ],
    "records": [
        {
            "record_id": "R1",
            "claim_refs": ["C1"],
            "material_id": "M1",
            "record_role": "direct result",
            "provenance": "paper-local",
            "location": "",
            "summary": "",
            "sample_or_unit": "",
            "comparison_or_baseline": "",
            "result_detail": "",
            "result_key": "G1",
            "unit_key": "U1",
            "availability": "complete",
            "selection_or_filtering": "",
        }
    ],
    "promotions": [
        {
            "evidence_node": "E1",
            "record_ids": ["R1"],
            "reason": "",
        }
    ],
    "unresolved_claims": [],
}


def _nonempty(value, field: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
        return ""
    return value.strip()


def _choice(value, allowed: set[str], field: str, errors: list[str]) -> str:
    if value not in allowed:
        errors.append(f"{field} must be one of: {', '.join(sorted(allowed))}")
        return ""
    return value


def _validate_sequential(ids: list[str], prefix: str, field: str, errors: list[str]) -> None:
    expected = [f"{prefix}{i}" for i in range(1, len(ids) + 1)]
    if ids != expected:
        errors.append(f"{field} must be sequential from {prefix}1")


def validate_inventory(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["inventory must be a JSON object"]

    viability = _choice(data.get("evidence_viability"), VIABILITY, "evidence_viability", errors)

    claims = data.get("claims")
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    claim_ids = []
    for i, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            errors.append(f"claim {i} must be an object")
            continue
        cid = claim.get("claim_id")
        if not isinstance(cid, str) or not ID_PATTERNS["claim"].fullmatch(cid):
            errors.append(f"claim {i}: invalid claim_id")
        else:
            claim_ids.append(cid)
        _nonempty(claim.get("content"), f"claim {i}.content", errors)
    if claim_ids:
        _validate_sequential(claim_ids, "C", "claim ids", errors)

    if viability == "auditable" and not (3 <= len(claims) <= 5):
        errors.append("auditable inventory must contain 3 to 5 claims")
    if viability == "partially auditable" and not (1 <= len(claims) <= 5):
        errors.append("partially auditable inventory must contain 1 to 5 claims")
    if viability == "non-auditable" and claims:
        errors.append("non-auditable inventory must not contain claims")

    materials = data.get("materials")
    if not isinstance(materials, list) or not materials:
        errors.append("materials must be a non-empty list")
        materials = []
    material_ids = []
    for i, item in enumerate(materials, start=1):
        if not isinstance(item, dict):
            errors.append(f"material {i} must be an object")
            continue
        mid = item.get("material_id")
        if not isinstance(mid, str) or not ID_PATTERNS["material"].fullmatch(mid):
            errors.append(f"material {i}: invalid material_id")
        else:
            material_ids.append(mid)
        _choice(item.get("kind"), MATERIAL_KINDS, f"material {i}.kind", errors)
        _choice(item.get("availability"), MATERIAL_AVAILABILITY, f"material {i}.availability", errors)
        _nonempty(item.get("location"), f"material {i}.location", errors)
        if not isinstance(item.get("notes", ""), str):
            errors.append(f"material {i}.notes must be a string")
    if material_ids:
        _validate_sequential(material_ids, "M", "material ids", errors)
    if len(material_ids) != len(set(material_ids)):
        errors.append("material ids must be unique")

    records = data.get("records")
    if not isinstance(records, list):
        errors.append("records must be a list")
        records = []
    if viability in {"auditable", "partially auditable"} and not records:
        errors.append(f"{viability} inventory must contain at least one evidence record")
    if viability == "non-auditable" and records:
        errors.append("non-auditable inventory must not fabricate evidence records")

    record_ids = []
    record_by_id = {}
    result_key_by_record = {}
    unit_key_by_record = {}

    for i, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"record {i} must be an object")
            continue
        rid = record.get("record_id")
        if not isinstance(rid, str) or not ID_PATTERNS["record"].fullmatch(rid):
            errors.append(f"record {i}: invalid record_id")
        else:
            record_ids.append(rid)
            record_by_id[rid] = record

        refs = record.get("claim_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"record {i}.claim_refs must be a non-empty list")
            refs = []
        if len(refs) != len(set(refs)):
            errors.append(f"record {i}: duplicate claim_refs")
        for ref in refs:
            if ref not in claim_ids:
                errors.append(f"record {i}: unknown claim ref {ref!r}")

        if record.get("material_id") not in material_ids:
            errors.append(f"record {i}: unknown material_id {record.get('material_id')!r}")

        role = _choice(record.get("record_role"), RECORD_ROLES, f"record {i}.record_role", errors)
        provenance = _choice(record.get("provenance"), PROVENANCE, f"record {i}.provenance", errors)
        _nonempty(record.get("location"), f"record {i}.location", errors)
        _nonempty(record.get("summary"), f"record {i}.summary", errors)
        _nonempty(record.get("sample_or_unit"), f"record {i}.sample_or_unit", errors)
        _nonempty(record.get("comparison_or_baseline"), f"record {i}.comparison_or_baseline", errors)
        _nonempty(record.get("result_detail"), f"record {i}.result_detail", errors)
        _choice(record.get("availability"), RECORD_AVAILABILITY, f"record {i}.availability", errors)
        _nonempty(record.get("selection_or_filtering"), f"record {i}.selection_or_filtering", errors)

        g = record.get("result_key")
        if not isinstance(g, str) or not ID_PATTERNS["result"].fullmatch(g):
            errors.append(f"record {i}: invalid result_key")
        elif rid:
            result_key_by_record[rid] = g

        u = record.get("unit_key")
        if u != "unknown" and (not isinstance(u, str) or not ID_PATTERNS["unit"].fullmatch(u)):
            errors.append(f"record {i}: invalid unit_key")
        elif rid:
            unit_key_by_record[rid] = u

        if role == "external evidence" and provenance != "external citation":
            errors.append(f"record {i}: external evidence role requires external citation provenance")

    if record_ids:
        _validate_sequential(record_ids, "R", "record ids", errors)
    if len(record_ids) != len(set(record_ids)):
        errors.append("record ids must be unique")

    promotions = data.get("promotions")
    if not isinstance(promotions, list):
        errors.append("promotions must be a list")
        promotions = []
    if viability in {"auditable", "partially auditable"} and not promotions:
        errors.append(f"{viability} inventory must contain at least one promoted evidence node")
    if viability == "non-auditable" and promotions:
        errors.append("non-auditable inventory must not contain promotions")

    evidence_ids = []
    used_records = set()
    promoted_results = {}
    evidence_units = {}

    for i, promotion in enumerate(promotions, start=1):
        if not isinstance(promotion, dict):
            errors.append(f"promotion {i} must be an object")
            continue
        eid = promotion.get("evidence_node")
        if not isinstance(eid, str) or not ID_PATTERNS["evidence"].fullmatch(eid):
            errors.append(f"promotion {i}: invalid evidence_node")
        else:
            evidence_ids.append(eid)

        rids = promotion.get("record_ids")
        if not isinstance(rids, list) or not rids:
            errors.append(f"promotion {i}.record_ids must be a non-empty list")
            rids = []
        if len(rids) != len(set(rids)):
            errors.append(f"promotion {i}: duplicate record id")
        unknown = [rid for rid in rids if rid not in record_by_id]
        if unknown:
            errors.append(f"promotion {i}: unknown record id(s): {', '.join(unknown)}")
        for rid in rids:
            if rid in used_records:
                errors.append(f"record {rid} is promoted into more than one evidence node")
            used_records.add(rid)
        known_rids = [rid for rid in rids if rid in result_key_by_record]
        result_keys = {result_key_by_record[rid] for rid in known_rids}
        if len(result_keys) > 1:
            errors.append(f"promotion {i}: one evidence node cannot merge different result keys")
        if eid and len(result_keys) == 1:
            g = next(iter(result_keys))
            if g in promoted_results and promoted_results[g] != eid:
                errors.append(f"result key {g} is promoted into multiple evidence nodes")
            promoted_results[g] = eid
            evidence_units[eid] = {unit_key_by_record.get(rid, "unknown") for rid in known_rids}

        _nonempty(promotion.get("reason"), f"promotion {i}.reason", errors)

    if evidence_ids:
        _validate_sequential(evidence_ids, "E", "evidence node ids", errors)
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("evidence node ids must be unique")

    unresolved = data.get("unresolved_claims")
    if not isinstance(unresolved, list):
        errors.append("unresolved_claims must be a list")
        unresolved = []
    unresolved_ids = []
    for i, item in enumerate(unresolved, start=1):
        if not isinstance(item, dict):
            errors.append(f"unresolved claim {i} must be an object")
            continue
        cid = item.get("claim_id")
        if cid not in claim_ids:
            errors.append(f"unresolved claim {i}: unknown claim_id {cid!r}")
        else:
            unresolved_ids.append(cid)
        _nonempty(item.get("reason"), f"unresolved claim {i}.reason", errors)
    if len(unresolved_ids) != len(set(unresolved_ids)):
        errors.append("unresolved claim ids must be unique")
    if viability == "non-auditable" and unresolved:
        errors.append("non-auditable inventory must not invent claim-specific unresolved entries")

    covered_claims = set()
    for promotion in promotions:
        for rid in promotion.get("record_ids", []):
            record = record_by_id.get(rid)
            if record:
                covered_claims.update(record.get("claim_refs", []))

    overlap = covered_claims & set(unresolved_ids)
    if overlap:
        errors.append(
            "claims cannot be both promoted and unresolved: " + ", ".join(sorted(overlap))
        )
    for cid in claim_ids:
        if cid not in covered_claims and cid not in unresolved_ids:
            errors.append(
                f"{cid}: claim has neither promoted evidence nor an unresolved_claims entry"
            )

    return errors


def compact_summary(data: dict) -> str:
    errors = validate_inventory(data)
    if errors:
        raise ValueError("\n".join(errors))

    record_by_id = {r["record_id"]: r for r in data["records"]}
    lines = [
        f"evidence viability: {data['evidence_viability']}",
        f"claims: {len(data['claims'])}; records: {len(data['records'])}; evidence nodes: {len(data['promotions'])}; unresolved: {len(data.get('unresolved_claims', []))}",
    ]

    for claim in data["claims"]:
        cid = claim["claim_id"]
        lines.append(f"\n{cid}: {claim['content']}")
        related = [
            p for p in data["promotions"]
            if any(cid in record_by_id[rid]["claim_refs"] for rid in p["record_ids"])
        ]
        if not related:
            unresolved = {
                item["claim_id"]: item["reason"]
                for item in data.get("unresolved_claims", [])
            }
            if cid in unresolved:
                lines.append(f"- unresolved retrieval gap: {unresolved[cid]}")
            else:
                lines.append("- no promoted evidence node")
            continue
        for p in related:
            rids = p["record_ids"]
            records = [record_by_id[rid] for rid in rids]
            g = records[0]["result_key"]
            units = sorted({r["unit_key"] for r in records})
            summaries = []
            seen = set()
            for r in records:
                if r["summary"] not in seen:
                    summaries.append(r["summary"])
                    seen.add(r["summary"])
            lines.append(
                f"- {p['evidence_node']} <- {' + '.join(rids)} "
                f"[{g}; units={'+'.join(units)}]: {' / '.join(summaries)}"
            )
    return "\n".join(lines) + "\n"


def check_audit_alignment(inventory: dict, audit: dict) -> list[str]:
    errors = validate_inventory(inventory)
    if errors:
        return [f"inventory: {x}" for x in errors]

    promotions = {p["evidence_node"]: p for p in inventory["promotions"]}
    record_by_id = {r["record_id"]: r for r in inventory["records"]}
    units_by_e = {}
    for eid, promotion in promotions.items():
        units_by_e[eid] = {
            record_by_id[rid]["unit_key"] for rid in promotion["record_ids"]
        }

    claims = audit.get("claims", [])
    for i, claim in enumerate(claims, start=1):
        support = claim.get("support", {})
        nodes = support.get("evidence_nodes", [])
        for node in nodes:
            if node not in promotions:
                errors.append(f"audit claim {i}: evidence node {node} is not promoted in inventory")

        dep = support.get("evidence_dependence")
        if dep == "independent convergence" and len(nodes) >= 2:
            seen_units = set()
            for node in nodes:
                units = units_by_e.get(node, {"unknown"})
                if "unknown" in units:
                    errors.append(
                        f"audit claim {i}: independent convergence cannot rely on unknown unit identity"
                    )
                    break
                overlap = seen_units & units
                if overlap:
                    errors.append(
                        f"audit claim {i}: independent convergence shares evidence unit(s): "
                        + ", ".join(sorted(overlap))
                    )
                    break
                seen_units.update(units)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inventory", nargs="?", type=Path)
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--audit-ledger", type=Path)
    args = parser.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, indent=2, ensure_ascii=False))
        return 0
    if args.inventory is None:
        parser.error("inventory is required unless --template is used")

    try:
        data = json.loads(args.inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    errors = validate_inventory(data)

    if args.audit_ledger:
        try:
            audit = json.loads(args.audit_ledger.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 1
        errors.extend(check_audit_alignment(data, audit))

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if args.compact:
        print(compact_summary(data), end="")
    else:
        print("PASS: evidence inventory satisfies the contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
