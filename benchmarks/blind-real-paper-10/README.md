# Blind Real-Paper 10

This benchmark tests whether a fresh reviewer can reconstruct important claim–evidence–reasoning judgments from public source material instead of merely preserving stored ledgers. It does not test whether the reviewer can discover fraud or pronounce a paper scientifically true or false.

## Isolation boundary

The reviewer side may read only:

- one generated source packet,
- the public paper/source URLs named in that packet,
- the installed Evidence Paper Reader skill,
- the public response schema.

It must not read repository `ledger.json`, `result.json`, semantic routes, module checks, manifests, `tests/real-paper-judgment-baseline.json`, or scorer output.

The scorer side is intentionally separate. Only after a response exists may it compare viability, flags, and semantically aligned claims against the durable regression contracts.

## Source packets

`generate_packets.py` discovers the ten recorded papers through `case_index.json` and reads only each case's `source.json`.

Packets whitelist neutral source fields. They omit:

- stored audit claims,
- support judgments,
- regression contracts,
- result notes,
- integrity notes,
- publication-status interpretations.

When a source record contains public integrity/provenance or later-context URLs, the packet may expose those URLs without the repository's interpretation. This is necessary for cases where source provenance is itself part of the audit question.

## Reviewer output

The reviewer creates a fresh audit judgment in the compact JSON form defined by `response-format.md`. Claim text is free-form. No stored claim IDs are exposed.

## Claim comparison

`score_blind.py` performs a conservative lexical alignment between fresh claims and stored audit claims, then checks support against the hidden `must_hold` / `allowed_range` contract.

Low-confidence claim matches are reported as `needs_adjudication`, not silently treated as wrong. Hard viability and required-integrity invariants can be scored without claim matching.

The lexical matcher is deliberately not called a semantic oracle. Its job is to automate obvious matches and route ambiguous rewrites to review.

## Run

Generate packets:

```bash
python benchmarks/blind-real-paper-10/generate_packets.py
```

Dry-run an isolated external reviewer:

```bash
python benchmarks/blind-real-paper-10/run_reviewer.py \
  --command './review_one.sh {prompt} {output}' \
  --dry-run
```

Run all ten in genuinely fresh contexts by removing `--dry-run`, then score:

```bash
python benchmarks/blind-real-paper-10/score_blind.py runs/responses --json
```

The repository does not fabricate a "blind" result from the same conversation that authored the answer key. A committed blind response should record the reviewer/model/runtime used and must come from an isolated context.
