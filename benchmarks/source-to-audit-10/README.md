# Source-to-Audit 10

This benchmark closes the gap between **artifact replay** and a true fresh audit from source material.

The existing source-backed records prove that stored semantic routes, reasoning graphs, module checks, inventories, ledgers, and final rendering remain internally consistent. They do **not** prove that a fresh reviewer starting from the source would reconstruct the same audit.

Source-to-Audit 10 tests that stronger path.

## Input boundary

The repository does not commit full copyrighted paper text merely to make the benchmark convenient.

For each run, an operator materializes a reviewable text/Markdown representation of the public source outside the repository, then the benchmark records:

- case ID
- canonical source URL and stable ID
- acquisition timestamp
- acquisition method
- normalization/extraction method
- SHA-256 and byte count of the exact review material
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

Prepare a fingerprinted input:

```bash
python benchmarks/source-to-audit-10/prepare_source.py \
  attention-is-all-you-need-2017 \
  /path/to/normalized-paper.txt \
  --acquisition-method "downloaded from canonical public URL" \
  --normalization-method "HTML-to-text preserving headings/tables" \
  --output /tmp/source-run/attention
```

The resulting directory contains a local `source-material.txt` copy plus `source-input.json`. Do not commit the source material unless its license and repository policy explicitly permit redistribution.
