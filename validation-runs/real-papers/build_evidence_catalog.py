#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
RUN_ROOT = ROOT / "validation-runs" / "real-papers"
LEGACY = RUN_ROOT / "legacy-fixture-index.json"
BLIND = ROOT / "benchmarks" / "blind-real-paper-10" / "case_index.json"
SOURCE_TO_AUDIT = ROOT / "benchmarks" / "source-to-audit-10" / "case_index.json"
TIERED = ROOT / "benchmarks" / "tiered-source-40" / "cases.json"
METADATA = ROOT / "benchmarks" / "metadata-halo-12" / "packet_specs.json"
STABILITY = ROOT / "benchmarks" / "stability-crossdomain-8" / "case_specs.json"
CLAIM_SELECTION = ROOT / "benchmarks" / "claim-selection-12" / "case_specs.json"
BENCHMARK_MAP = RUN_ROOT / "benchmark-source-map.json"
CATALOG = RUN_ROOT / "evidence-catalog.json"
EVIDENCE_MD = ROOT / "EVIDENCE.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def add_surface(row: dict, surface: dict) -> None:
    if surface not in row["test_surfaces"]:
        row["test_surfaces"].append(surface)


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
                    "kind": "artifact-replay",
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
    rows = {}
    for rel in load(LEGACY)["fixtures"]:
        path = ROOT / rel
        if not path.is_file():
            raise ValueError(f"missing legacy fixture: {rel}")
        stem = path.stem.removesuffix("-audit")
        eid = "legacy:" + stem
        rows[eid] = {
            "evidence_id": eid,
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
        }
    return rows


def discover_tiered(entries: dict, source_map: dict):
    aliases = source_map["tiered_source_aliases"]
    tiered_to_evidence = {}
    created = set()
    for case in load(TIERED)["cases"]:
        case_id = case["case_id"] if "case_id" in case else case["id"]
        if case_id in aliases:
            eid = aliases[case_id]
            if eid not in entries:
                raise ValueError(f"tiered alias target missing: {case_id} -> {eid}")
        else:
            eid = f"benchmark:tiered-source-40:{case_id}"
            if eid in entries:
                raise ValueError(f"duplicate benchmark evidence id: {eid}")
            entries[eid] = {
                "evidence_id": eid,
                "identity_status": "benchmark-source",
                "title": case["title"],
                "authors": "",
                "year": case.get("year"),
                "stable_id": "",
                "source_url": case["source_url"],
                "domain": case["domain"],
                "round_ids": [],
                "source_kind": case.get("source_kind", ""),
                "venue": case.get("venue", ""),
                "tier": case.get("tier", ""),
                "access": case.get("access", ""),
                "test_surfaces": [],
                "current_judgment": {
                    "scope_status": case.get("scope_status"),
                    "narrow_claim_support": case.get("narrow_claim_support"),
                    "broad_claim_support": case.get("broad_claim_support"),
                    "main_boundary": case.get("main_boundary"),
                },
            }
            created.add(eid)
        tiered_to_evidence[case_id] = eid
        add_surface(entries[eid], {
            "kind": "tiered-source-40",
            "path": "benchmarks/tiered-source-40/cases.json",
            "case_id": case_id,
            "status": "benchmark-spec",
        })
    return tiered_to_evidence, created


def attach_named_benchmark_surfaces(entries: dict, tiered_to_evidence: dict, source_map: dict):
    for packet in load(METADATA)["cases"]:
        source_case_id = packet["source_case_id"]
        eid = tiered_to_evidence.get(source_case_id)
        if eid is None:
            raise ValueError(f"metadata-halo source_case_id missing from tiered map: {source_case_id}")
        add_surface(entries[eid], {
            "kind": "metadata-halo-12",
            "path": "benchmarks/metadata-halo-12/packet_specs.json",
            "case_id": packet["case_id"],
            "status": "benchmark-spec",
        })

    stability_cases = {case["case_id"] for case in load(STABILITY)["cases"]}
    stability_map = source_map["stability_crossdomain_8"]
    if set(stability_map) != stability_cases:
        raise ValueError("stability evidence map must exactly cover stability case IDs")
    for case_id, eid in sorted(stability_map.items()):
        if eid not in entries:
            raise ValueError(f"stability target missing: {case_id} -> {eid}")
        add_surface(entries[eid], {
            "kind": "stability-crossdomain-8",
            "path": "benchmarks/stability-crossdomain-8/case_specs.json",
            "case_id": case_id,
            "status": "benchmark-spec",
        })

    claim_cases = {case["case_id"] for case in load(CLAIM_SELECTION)["cases"]}
    claim_map = source_map["claim_selection_12"]
    if set(claim_map) != claim_cases:
        raise ValueError("claim-selection evidence map must exactly cover claim-selection case IDs")
    for case_id, eid in sorted(claim_map.items()):
        if eid == "synthetic":
            continue
        if eid not in entries:
            raise ValueError(f"claim-selection target missing: {case_id} -> {eid}")
        add_surface(entries[eid], {
            "kind": "claim-selection-12",
            "path": "benchmarks/claim-selection-12/case_specs.json",
            "case_id": case_id,
            "status": "benchmark-spec",
        })


def attach_blind_surfaces(entries: dict, recorded_ids: set[str]):
    blind = {x["case_id"] for x in load(BLIND)["cases"]}
    missing = sorted(blind - recorded_ids)
    if missing:
        raise ValueError(
            "blind benchmark paper lacks source-backed record: " + ", ".join(missing)
        )
    for cid in sorted(blind):
        add_surface(entries[cid], {
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
                if cid not in recorded_ids:
                    raise ValueError(f"durable blind run references unrecorded paper: {cid}")
                add_surface(entries[cid], {
                    "kind": "blind-result",
                    "path": str(run_dir.relative_to(ROOT)),
                    "status": "completed",
                    "run_id": run["run_id"],
                    "reviewer": run["reviewer"],
                    "runtime": run["runtime"],
                })
    return blind


def attach_source_to_audit_surfaces(entries: dict, recorded_ids: set[str]):
    cases = load(SOURCE_TO_AUDIT)["cases"]
    source_ids = {case["case_id"] for case in cases}
    missing = sorted(source_ids - recorded_ids)
    if missing:
        raise ValueError(
            "source-to-audit benchmark paper lacks source-backed record: "
            + ", ".join(missing)
        )

    for cid in sorted(source_ids):
        add_surface(entries[cid], {
            "kind": "source-to-audit",
            "path": "benchmarks/source-to-audit-10",
            "status": "protocol-ready",
        })

    source_runs_root = RUN_ROOT / "source-runs"
    if source_runs_root.is_dir():
        for run_dir in sorted(p for p in source_runs_root.iterdir() if p.is_dir()):
            if run_dir.name.startswith("."):
                continue
            run_file = run_dir / "run.json"
            if not run_file.is_file():
                continue
            run = load(run_file)
            for cid in run.get("case_ids", []):
                if cid not in recorded_ids:
                    raise ValueError(
                        f"durable source run references unrecorded paper: {cid}"
                    )
                add_surface(entries[cid], {
                    "kind": "source-result",
                    "path": str(run_dir.relative_to(ROOT)),
                    "status": "completed",
                    "run_id": run["run_id"],
                    "reviewer": run["reviewer"],
                    "runtime": run["runtime"],
                })
    return source_ids


def build():
    recorded = discover_recorded()
    legacy = discover_legacy()
    entries = {**recorded, **legacy}
    source_map = load(BENCHMARK_MAP)

    tiered_to_evidence, benchmark_only = discover_tiered(entries, source_map)
    attach_named_benchmark_surfaces(entries, tiered_to_evidence, source_map)
    blind = attach_blind_surfaces(entries, set(recorded))
    source_to_audit = attach_source_to_audit_surfaces(entries, set(recorded))

    ordered = sorted(
        entries.values(),
        key=lambda x: (
            {"source-backed": 0, "benchmark-source": 1, "legacy-fixture": 2}[x["identity_status"]],
            x["evidence_id"],
        ),
    )
    return {
        "schema_version": 2,
        "policy": {
            "record_first": "Future full source audits must become source-backed recorded cases; named benchmark-only sources remain explicitly lower provenance until promoted.",
            "benchmark_boundary": "A public source used only in a benchmark is preserved as benchmark-source evidence and is not described as an artifact replay.",
            "legacy_boundary": "Legacy fixtures preserve earlier regression evidence but do not claim missing historical source metadata.",
            "counting_boundary": "Multiple benchmark or replay surfaces on one source do not count as multiple independent sources.",
        },
        "counts": {
            "source_backed_papers": len(recorded),
            "benchmark_only_sources": len(benchmark_only),
            "legacy_fixtures": len(legacy),
            "evidence_entries": len(ordered),
            "tiered_source_cases": len(tiered_to_evidence),
            "blind_protocol_papers": len(blind),
            "source_to_audit_protocol_papers": len(source_to_audit),
        },
        "entries": ordered,
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
        f"- benchmark-only named sources: **{c['benchmark_only_sources']}**",
        f"- legacy regression fixtures: **{c['legacy_fixtures']}**",
        f"- total unique evidence entries: **{c['evidence_entries']}**",
        f"- tiered-source benchmark cases mapped to durable identities: **{c['tiered_source_cases']}**",
        f"- source-backed papers prepared for isolated blind re-audit: **{c['blind_protocol_papers']}**",
        f"- source-backed papers prepared for source-to-audit replay: **{c['source_to_audit_protocol_papers']}**",
        "",
        "Source-backed entries have stable source identity plus replayable audit artifacts. Benchmark-source entries have explicit public source metadata and benchmark judgments but not a artifact replay. Legacy fixtures preserve older regression work whose original source/run metadata were not reconstructed.",
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
        replay = next(x["path"] for x in row["test_surfaces"] if x["kind"] == "artifact-replay")
        title = row["title"].replace("|", "\\|")
        lines.append(
            f"| {title} ({row['year']}) | {row['domain']} | {j['evidence_viability']} | {support} | {surfaces} | {replay} |"
        )

    lines += [
        "",
        "## Benchmark-only named sources",
        "",
        "These public sources were used in benchmark cases and are preserved as evidence of tested source diversity. They are not counted as artifact replay audits until promoted into a recorded round.",
        "",
        "| Source | Domain | Tier | Narrow / broad support | Test surfaces |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in catalog["entries"]:
        if row["identity_status"] != "benchmark-source":
            continue
        j = row["current_judgment"]
        support = f"{j['narrow_claim_support']} / {j['broad_claim_support']}"
        surfaces = ", ".join(x["kind"] for x in row["test_surfaces"])
        title = row["title"].replace("|", "\|")
        lines.append(
            f"| {title} ({row['year']}) | {row['domain']} | {row.get('tier', '')} | {support} | {surfaces} |"
        )

    lines += [
        "",
        "## Legacy regression evidence",
        "",
        "These remain contract evidence, but their original source URL/model/run metadata were not reconstructed.",
        "",
        "| Evidence ID | Fixture | Test surfaces |",
        "| --- | --- | --- |",
    ]
    for row in catalog["entries"]:
        if row["identity_status"] == "legacy-fixture":
            surfaces = ", ".join(x["kind"] for x in row["test_surfaces"])
            lines.append(
                f"| {row['evidence_id']} | {row['test_surfaces'][0]['path']} | {surfaces} |"
            )

    lines += [
        "",
        "## Record-first policy",
        "",
        "A paper or public source tested only in a development conversation does not count as project evidence. Full paper audits must become source-backed validation-run records. Named benchmark sources are retained at their actual evidence grade, and additional replay, blind, model-comparison, or stability runs attach to the same identity rather than inflating coverage.",
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
        status = row.get("identity_status")
        kinds = {x["kind"] for x in row.get("test_surfaces", [])}
        if status == "source-backed":
            if not all(row.get(k) for k in ["title", "stable_id", "source_url"]):
                out.append(f"{row['evidence_id']}: incomplete source identity")
            if "artifact-replay" not in kinds:
                out.append(f"{row['evidence_id']}: missing artifact-replay surface")
        elif status == "benchmark-source":
            if not all(row.get(k) for k in ["title", "source_url", "tier"]):
                out.append(f"{row['evidence_id']}: incomplete benchmark source metadata")
            if "tiered-source-40" not in kinds:
                out.append(f"{row['evidence_id']}: benchmark source lacks tiered-source surface")
        elif status == "legacy-fixture":
            if "legacy-regression" not in kinds:
                out.append(f"{row['evidence_id']}: legacy entry lacks legacy-regression surface")
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
            f"{c['benchmark_only_sources']} benchmark-only, {c['legacy_fixtures']} legacy)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
