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

## Judgment regression contract

Each manifest case carries two different kinds of expectation:

- `must_hold`: conclusions that are part of the durable regression contract, such as auditable versus non-auditable status and decision-critical required viability flags.
- `allowed_range`: explicitly bounded judgment tolerance. Support may be exact, or may allow only the narrow `partial`/ `insufficient` boundary when the distinction is genuinely judgment-sensitive. A tolerant range never crosses into `sufficient`.

The same contracts are copied into `tests/real-paper-judgment-baseline.json`, whose exact bytes are SHA-256 pinned in the test suite. This duplication is deliberate: changing a paper answer and widening its permitted range in the same manifest is not enough to make CI pass. Updating the tolerance policy requires an explicit baseline and hash change.

This is not intended to freeze scientific judgment forever. It makes judgment drift reviewable: hard invariants fail immediately, bounded disagreements are tolerated, and any expansion of the allowed region is a visible contract change.

## Legacy fixtures

`legacy-fixture-index.json` backfills the repository's pre-record real-paper fixtures. Original conversational run metadata was not available, so they are labeled honestly as legacy fixtures rather than reconstructed run histories.
