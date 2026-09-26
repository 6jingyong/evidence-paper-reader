# Carrier-Neutral 12

Carrier-Neutral 12 tests the claim–evidence–reasoning core without relying on research-paper conventions.

The twelve cases are **synthetic**. They represent different carrier types—vendor datasheet, laboratory report, marketing page, benchmark page, customer case study, industry survey, policy brief, incident postmortem, engineering blog, financial backtest, security whitepaper, and product experiment memo.

They do not count as real-source evidence in `EVIDENCE.md`. Their purpose is narrower: verify that the same logical objects and boundaries survive outside the paper adapter.

## Isolation

The reviewer receives only one generated packet containing:

- case ID
- carrier/source kind
- synthetic source text
- the carrier-neutral response schema

It does not receive `reference_expectations.json` or scorer output.

## What is scored

Hidden expectations score:

- evidence viability
- per-claim support level
- whether the fresh reasoning graph uses an acceptable inference type
- whether claim-local evidence direction includes an acceptable relation

The benchmark intentionally does **not** score paper-specific methodological modules, evidence inventory choice, journal metadata, or venue prestige.

## Run

Generate answer-key-free packets:

```bash
python benchmarks/carrier-neutral-12/generate_packets.py
```

Dry-run a fresh reviewer command:

```bash
python benchmarks/carrier-neutral-12/run_reviewer.py \
  --command './review_one.sh {prompt} {output}' \
  --dry-run
```

After isolated responses exist:

```bash
python benchmarks/carrier-neutral-12/score_carrier.py runs/responses --json
```

A real model result should record the reviewer/runtime/isolation method before being used as project evidence. The repository does not manufacture a score from the same context that authored the hidden expectations.
