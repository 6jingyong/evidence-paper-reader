# Source-to-Audit 10

This benchmark closes the gap between **artifact replay** and a true fresh audit from source material.

The existing source-backed records prove that stored semantic routes, reasoning graphs, module checks, inventories, ledgers, and final rendering remain internally consistent. They do **not** prove that a fresh reviewer starting from the source would reconstruct the same audit.

Source-to-Audit 10 tests that stronger path.

## Input boundary

The repository does not commit full copyrighted paper text merely to make the benchmark convenient.

For each run, an operator materializes UTF-8 text components outside the repository. The case's `acquisition-profiles.json` entry decides which components are required and in what order. The benchmark then deterministically builds one review bundle and records:

- case ID
- canonical source URL and stable ID
- acquisition timestamp and acquisition method
- acquisition-profile SHA-256
- exact component IDs, roles, URLs, byte counts, and SHA-256 values
- deterministic bundle format
- SHA-256 and byte count of the exact combined review material
- optional SHA-256 of a raw downloaded source when one was retained locally

The reviewer receives the materialized source file in an isolated workspace. It does not receive the stored ledger, semantic route, module checks, reasoning graph, regression contract, or hidden scorer.

## Why hash the source input

A URL alone is not enough. Web pages can change, PDF extraction can differ, and HTML normalization choices can alter what the reviewer actually saw.

The source-input manifest therefore fingerprints the exact normalized bytes used by the reviewer. A durable completed run can later say *which source bytes were reviewed* without redistributing those bytes in the repository.

## Reviewer output

The output schema is the same ledger-v2 compact response used by `blind-real-paper-10`: fresh claims, evidence nodes, upstream claim dependencies, support levels, and a reasoning graph.

The hidden scorer may compare the result against the durable judgment baseline only after the reviewer output exists.

## Evidence status

Merely having this protocol is **protocol-ready**, not a completed source-to-audit result.

A completed result should be persisted under `validation-runs/real-papers/source-runs/` with its source-input manifests, reviewer/runtime identity, responses, and hidden score.

## Local flow

Prepare a fingerprinted single-component input:

```bash
python benchmarks/source-to-audit-10/prepare_source.py \
  attention-is-all-you-need-2017 \
  /path/to/primary-article.txt \
  --acquisition-method "arXiv HTML converted to UTF-8 text with headings/tables preserved" \
  --output /tmp/source-run/attention
```

For a multi-component integrity/provenance case, provide every required component explicitly:

```bash
python benchmarks/source-to-audit-10/prepare_source.py \
  surgisphere-hcq-2020 \
  --component primary=/path/to/article.txt \
  --component retraction=/path/to/retraction.txt \
  --component post-publication-record=/path/to/provenance.txt \
  --acquisition-method "public HTML pages converted separately to UTF-8 text" \
  --output /tmp/source-run/surgisphere
```

The script normalizes only line endings and terminal newline, then inserts deterministic component boundaries with role and URL. It does not summarize, paraphrase, reorder, or silently drop result-bearing tables/captions. The resulting directory contains local `source-material.txt` plus `source-input.json`. Do not commit the source material unless its license and repository policy explicitly permit redistribution.
