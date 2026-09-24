# Claim Selection 12

This benchmark tests the stage before evidence support judgment: choosing which claims actually belong in the audit.

It targets four failure modes:

- missing a headline claim
- selecting discussion/speculation or method-description filler
- **silent narrowing**: replacing an author's strong causal/mechanistic/generality claim with a safer association claim before auditing it
- failing to stop claim extraction when evidence viability is non-auditable

## Design

- 12 compact source packets
- deterministically shuffled candidate claims
- private reference expectations
- script-only scoring; no semantic judge model is required

The benchmark intentionally separates **claim selection** from **support judgment**.

A claim may be required for selection even when it is ultimately unsupported. The skill must preserve what the article actually claims and then judge it, rather than quietly rewriting the claim into a version the evidence can support.

## Metrics

- required-claim recall
- forbidden-claim selection rate
- silent-narrowing rate
- evidence-viability accuracy
- claim-count contract violations

## Run

```bash
python benchmarks/claim-selection-12/generate_packets.py
# Review packets in the generated queue and save JSON responses.
python benchmarks/claim-selection-12/score.py responses/
```

Reference expectations must not be shown to the reviewer.
