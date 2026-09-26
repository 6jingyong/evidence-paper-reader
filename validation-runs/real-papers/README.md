# Real-paper validation runs

This directory stores durable, replayable records of audits performed against identifiable real papers.

## Record contract

Each new round has a manifest and one directory per paper. A paper record stores:

- `source.json`: stable paper identity and public source used for the audit.
- `ledger.json`: structured reader-side audit judgment.
- `semantic-route.json`: raw per-claim semantic routing decisions.
- `module-checks.json`: completed routed methodological checks.
- `inventory.json`: present only when semantic routing requires the evidence-inventory path.
- `result.json`: run metadata and expected final-gate disposition.

Generated merged routes and generated audit-context bundles are intentionally not stored. CI recomputes both from the raw semantic route, then replays `audit_gate.py`. This prevents a stored cache from becoming the source of truth.

The records are evidence of a particular audit run, not immutable ground truth. A later run may disagree, but it must preserve the old record and add a new round.

## Legacy fixtures

`legacy-fixture-index.json` backfills the repository's pre-record real-paper fixtures. Original conversational run metadata was not available, so they are labeled honestly as legacy fixtures rather than reconstructed run histories.
