#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
RUN_ROOT = ROOT / "validation-runs" / "real-papers"
LEGACY = RUN_ROOT / "legacy-fixture-index.json"
BLIND = ROOT / "benchmarks" / "blind-real-paper-10" / "case_index.json"
CATALOG = RUN_ROOT / "evidence-catalog.json"
EVIDENCE_MD = ROOT / "EVIDENCE.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def discover_recorded():
    rows = {}
    for rd in sorted(p for p in RUN_ROOT.glob("*-round-*") if p.is_dir()):
        manifest = load(rd / "manifest.json")
        for case in manifest["cases"]:
            cid = case["id"]
            root = rd / cid
            source = load(root / "source.json")
            ledger = load(root / "ledger.json")
            result = load(root / "result.json")
            if cid in rows:
                raise ValueError(f"duplicate recorded paper id: {cid}")
            rows[cid] = {
                "evidence_id": cid,
                "identity_status": "source-backed",
                "title": source["title"],
                "authors": source.get("authors", ""),
                "year": source.get("year"),
                "stable_id": source["stable_id"],
                "source_url": source["source_url"],
                "domain": case["domain"],
                "round_ids": [manifest["round_id"]],
                "test_surfaces": [{
                    "kind": "full-replay",
                    "path": str(root.relative_to(ROOT)),
                    "status": result["expected_gate"],
                }],
                "current_judgment": {
                    "evidence_viability": ledger["evidence_viability"],
                    "viability_flags": ledger.get("viability_flags", []),
                    "support_levels": [
                        c["support"]["support_level"]
                        for c in ledger.get("claims", [])
                    ],
                },
            }
    return rows


def discover_legacy():
    rows = []
    for rel in load(LEGACY)["fixtures"]:
        path = ROOT / rel
        if not path.is_file():
            raise ValueError(f"missing legacy fixture: {rel}")
        stem = path.stem.removesuffix("-audit")
        rows.append({
            "evidence_id": "legacy:" + stem,
            "identity_status": "legacy-fixture",
            "title": stem.replace("-", " "),
            "authors": "",
            "year": None,
            "stable_id": "",
            "source_url": "",
            "domain": "legacy-regression",
            "round_ids": [],
            "test_surfaces": [{
                "kind": "legacy-regression",
                "path": rel,
                "status": "contract-pass",
            }],
            "current_judgment": None,
        })
    return rows


def build():
    recorded = discover_recorded()
    blind = {x["case_id"] for x in load(BLIND)["cases"]}
    missing = sorted(blind - set(recorded))
    if missing:
        raise ValueError(
            "blind benchmark paper lacks source-backed record: " + ", ".join(missing)
        )
    for cid in sorted(blind):
        recorded[cid]["test_surfaces"].append({
            "kind": "blind-re-audit",
            "path": "benchmarks/blind-real-paper-10",
            "status": "protocol-ready",
        })

    blind_runs_root = RUN_ROOT / "blind-runs"
    if blind_runs_root.is_dir():
        for run_dir in sorted(p for p in blind_runs_root.iterdir() if p.is_dir()):
            if run_dir.name.startswith("."):
                continue
            run_file = run_dir / "run.json"
            if not run_file.is_file():
                continue
            run = load(run_file)
            for cid in run.get("case_ids", []):
                if cid not in recorded:
                    raise ValueError(
                        f"durable blind run references unrecorded paper: {cid}"
                    )
                recorded[cid]["test_surfaces"].append({
                    "kind": "blind-result",
                    "path": str(run_dir.relative_to(ROOT)),
                    "status": "completed",
                    "run_id": run["run_id"],
                    "reviewer": run["reviewer"],
                    "runtime": run["runtime"],
                })

    legacy = discover_legacy()
    entries = sorted(
        list(recorded.values()) + legacy,
        key=lambda x: (x["identity_status"] != "source-backed", x["evidence_id"]),
    )
    return {
        "schema_version": 1,
        "policy": {
            "record_first": "Every future real-paper test must resolve to a source-backed recorded case before it counts as repository evidence.",
            "legacy_boundary": "Legacy fixtures preserve earlier regression evidence but do not claim missing historical source metadata.",
            "counting_boundary": "Multiple test surfaces on one paper do not count as multiple independent papers.",
        },
        "counts": {
            "source_backed_papers": len(recorded),
            "legacy_fixtures": len(legacy),
            "evidence_entries": len(entries),
            "blind_protocol_papers": len(blind),
        },
        "entries": entries,
    }


def render(catalog):
    c = catalog["counts"]
    lines = [
        "# Evidence base",
        "",
        "This page is generated from repository artifacts. It records what the project has actually tested rather than a hand-maintained promotional count.",
        "",
        "## Current coverage",
        "",
        f"- source-backed recorded papers: **{c['source_backed_papers']}**",
        f"- legacy regression fixtures: **{c['legacy_fixtures']}**",
        f"- total evidence entries: **{c['evidence_entries']}**",
        f"- source-backed papers prepared for isolated blind re-audit: **{c['blind_protocol_papers']}**",
        "",
        "Source-backed entries have stable source identity plus replayable audit artifacts. Legacy fixtures are preserved regression evidence with incomplete historical source/run metadata and are not presented as equally reproducible.",
        "",
        "## Source-backed papers",
        "",
        "| Paper | Domain | Viability | Support vector | Test surfaces | Evidence path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in catalog["entries"]:
        if row["identity_status"] != "source-backed":
            continue
        j = row["current_judgment"]
        support = " / ".join(j["support_levels"]) or "n/a"
        surfaces = ", ".join(x["kind"] for x in row["test_surfaces"])
        replay = next(x["path"] for x in row["test_surfaces"] if x["kind"] == "full-replay")
        title = row["title"].replace("|", "\\|")
        lines.append(
            f"| {title} ({row['year']}) | {row['domain']} | {j['evidence_viability']} | {support} | {surfaces} | {replay} |"
        )
    lines += [
        "",
        "## Legacy regression evidence",
        "",
        "These remain contract evidence, but their original source URL/model/run metadata were not reconstructed.",
        "",
        "| Evidence ID | Fixture |",
        "| --- | --- |",
    ]
    for row in catalog["entries"]:
        if row["identity_status"] == "legacy-fixture":
            lines.append(f"| {row['evidence_id']} | {row['test_surfaces'][0]['path']} |")
    lines += [
        "",
        "## Record-first policy",
        "",
        "A paper mentioned or tested only in a development conversation does not count as project evidence. Future real-paper work must first create a source-backed validation-run record. Additional full replay, inventory, blind, model-comparison, or stability runs attach to the same paper identity rather than inflating the paper count.",
        "",
    ]
    return "\n".join(lines)


def errors(catalog):
    out = []
    rebuilt = build()
    if catalog != rebuilt:
        out.append("evidence-catalog.json is stale")
    ids = [x["evidence_id"] for x in catalog.get("entries", [])]
    if len(ids) != len(set(ids)):
        out.append("duplicate evidence_id")
    for row in catalog.get("entries", []):
        if row["identity_status"] == "source-backed":
            if not all(row.get(k) for k in ["title", "stable_id", "source_url"]):
                out.append(f"{row['evidence_id']}: incomplete source identity")
            kinds = {x["kind"] for x in row["test_surfaces"]}
            if "full-replay" not in kinds:
                out.append(f"{row['evidence_id']}: missing full-replay surface")
        elif row["identity_status"] == "legacy-fixture":
            if {x["kind"] for x in row["test_surfaces"]} != {"legacy-regression"}:
                out.append(f"{row['evidence_id']}: invalid legacy surface")
        else:
            out.append(f"{row.get('evidence_id')}: invalid identity_status")
    return out


def write():
    catalog = build()
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    EVIDENCE_MD.write_text(render(catalog), encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--write", action="store_true")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    if args.write:
        write()
    if args.check:
        if not CATALOG.is_file() or not EVIDENCE_MD.is_file():
            print("FAIL: missing generated evidence catalog/page")
            return 1
        catalog = load(CATALOG)
        found = errors(catalog)
        if EVIDENCE_MD.read_text(encoding="utf-8") != render(build()):
            found.append("EVIDENCE.md is stale")
        if found:
            for item in found:
                print("FAIL: " + item)
            return 1
        c = catalog["counts"]
        print(
            f"PASS: evidence catalog complete ({c['source_backed_papers']} source-backed, "
            f"{c['legacy_fixtures']} legacy)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
